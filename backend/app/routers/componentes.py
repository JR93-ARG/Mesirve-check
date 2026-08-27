import re
import io
import json
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from PIL import Image
import pytesseract

from app.database import get_db

router = APIRouter(prefix="/api/componentes", tags=["componentes"])


@router.get("/buscar")
async def buscar_componentes(q: str, tipo: str = None, db: AsyncSession = Depends(get_db)):
    """Autocomplete manual de CPU/GPU, para cuando el usuario prefiere elegir
    en vez de pegar texto."""
    condiciones = "to_tsvector('spanish', marca || ' ' || modelo) @@ plainto_tsquery('spanish', :q) OR marca ILIKE :like_q OR modelo ILIKE :like_q"
    params = {"q": q, "like_q": f"%{q}%"}
    if tipo:
        condiciones += " AND tipo = :tipo"
        params["tipo"] = tipo
    query = text(f"SELECT id, tipo, marca, modelo, puntaje_relativo FROM componentes WHERE {condiciones} LIMIT 8")
    result = await db.execute(query, params)
    return result.mappings().all()


class TextoPegado(BaseModel):
    texto: str
    sistema_operativo: str | None = None  # "windows", "macos", "android", "ios" — pista opcional


# Patrones de RAM: "16 GB", "16.0 GB", "Memoria RAM  16,0 GB", "16384 MB"
PATRON_RAM_GB = re.compile(r"(\d+(?:[.,]\d+)?)\s*GB", re.IGNORECASE)
PATRON_RAM_MB = re.compile(r"(\d+)\s*MB", re.IGNORECASE)
PATRON_ALMACENAMIENTO_DESPUES = re.compile(
    r"(\d+(?:[.,]\d+)?)\s*(GB|TB)\b.{0,20}?\b(SSD|HDD|eMMC)\b",
    re.IGNORECASE,
)
PATRON_ALMACENAMIENTO_ANTES = re.compile(
    r"\b(almacenamiento|storage|disco)\b.{0,25}?(\d+(?:[.,]\d+)?)\s*(GB|TB)",
    re.IGNORECASE,
)


def _extraer_ram_gb(texto: str) -> float | None:
    for linea in texto.splitlines():
        if re.search(r"\b(ram|memoria)\b", linea, re.IGNORECASE) and not re.search(
            r"\b(ssd|hdd|almacenamiento|storage|disco|gráfic|graphics|vram)\b", linea, re.IGNORECASE
        ):
            m = PATRON_RAM_GB.search(linea)
            if m:
                return float(m.group(1).replace(",", "."))
    return None


def _extraer_almacenamiento_gb(texto: str):
    m = PATRON_ALMACENAMIENTO_DESPUES.search(texto)
    if m:
        valor = float(m.group(1).replace(",", "."))
        unidad = m.group(2).upper()
        tipo = m.group(3).upper()
        if unidad == "TB":
            valor *= 1024
        tipo_normalizado = "ssd" if "SSD" in tipo else "hdd" if "HDD" in tipo else "emmc"
        return valor, tipo_normalizado

    m = PATRON_ALMACENAMIENTO_ANTES.search(texto)
    if m:
        valor = float(m.group(2).replace(",", "."))
        unidad = m.group(3).upper()
        if unidad == "TB":
            valor *= 1024
        return valor, None  # etiqueta no dice si es SSD o HDD

    return None, None


def _limpiar_descriptor(linea: str) -> str:
    """De 'Procesador\tIntel(R) Core(TM) i3-10105 CPU @ 3.70GHz (3.70 GHz)'
    saca 'Intel Core i3-10105', descartando ruido que nunca va a estar en
    el catálogo (marcas registradas, velocidad de reloj, la palabra CPU)."""
    partes = re.split(r"[\t:]", linea, maxsplit=1)
    texto = partes[-1] if len(partes) > 1 else partes[0]
    texto = re.sub(r"\((?:R|TM|C)\)", "", texto, flags=re.IGNORECASE)
    texto = re.sub(r"@.*$", "", texto)
    texto = re.sub(r"\bCPU\b", "", texto, flags=re.IGNORECASE)
    texto = re.sub(r"[^\w\s.-]", " ", texto)
    return re.sub(r"\s+", " ", texto).strip()


def _lineas_candidatas(texto: str, palabras_clave: list[str]) -> list[str]:
    candidatas = []
    for linea in texto.splitlines():
        if any(p in linea.lower() for p in palabras_clave):
            candidatas.append(linea)
    return candidatas


async def _mejor_match(db: AsyncSession, tipo: str, lineas: list[str]):
    """Compara por similitud de trigramas contra el catálogo — tolera SKUs
    que no están exactos (ej. i3-10105 pegado vs i3-10100 cargado), a
    diferencia de una búsqueda de texto que exige coincidencia de palabras
    completas. UMBRAL_MINIMO evita devolver algo random cuando no hay
    ningún parecido real."""
    UMBRAL_MINIMO = 0.15
    mejor = None
    for linea in lineas:
        descriptor = _limpiar_descriptor(linea)
        if len(descriptor) < 3:
            continue
        query = text("""
            SELECT id, marca, modelo, puntaje_relativo,
                   similarity(marca || ' ' || modelo, :texto) AS puntaje_similitud
            FROM componentes
            WHERE tipo = :tipo
            ORDER BY puntaje_similitud DESC
            LIMIT 1
        """)
        fila = (await db.execute(query, {"texto": descriptor, "tipo": tipo})).mappings().first()
        if fila and fila["puntaje_similitud"] >= UMBRAL_MINIMO:
            if not mejor or fila["puntaje_similitud"] > mejor["puntaje_similitud"]:
                mejor = dict(fila)
    if mejor:
        mejor["exacto"] = mejor["puntaje_similitud"] >= 0.45
    return mejor


async def _interpretar_texto(texto: str, db: AsyncSession) -> dict:
    # Si lo que pegaron es JSON estructurado (de nuestro one-liner de
    # PowerShell o de `system_profiler -json` en Mac), lo tratamos aparte:
    # los valores de RAM/almacenamiento vienen exactos, no hay que adivinar
    # con regex. Si falla el parseo, seguimos con el camino heurístico de
    # siempre sobre texto libre.
    estructurado = _intentar_parsear_json(texto)
    if estructurado:
        cpu_texto, gpu_texto, ram_gb, almacenamiento_gb = estructurado
        cpu_match = await _mejor_match(db, "cpu", [cpu_texto] if cpu_texto else [])
        gpu_match = await _mejor_match(db, "gpu", [gpu_texto] if gpu_texto else [])
        return {
            "cpu": cpu_match,
            "gpu": gpu_match,
            "ram_gb": ram_gb,
            "almacenamiento_gb": almacenamiento_gb,
            "tipo_almacenamiento": None,
            "reconocido_algo": any([cpu_match, gpu_match, ram_gb, almacenamiento_gb]),
            "fuente_datos": "estructurado",
        }

    cpu_lineas = _lineas_candidatas(texto, ["processor", "procesador", "chip", "cpu"])
    gpu_lineas = _lineas_candidatas(texto, ["graphics", "gráfic", "grafic", "gpu", "video", "tarjeta"])

    cpu_match = await _mejor_match(db, "cpu", cpu_lineas)
    gpu_match = await _mejor_match(db, "gpu", gpu_lineas)
    ram_gb = _extraer_ram_gb(texto)
    almacenamiento_gb, tipo_almacenamiento = _extraer_almacenamiento_gb(texto)

    return {
        "cpu": cpu_match,
        "gpu": gpu_match,
        "ram_gb": ram_gb,
        "almacenamiento_gb": almacenamiento_gb,
        "tipo_almacenamiento": tipo_almacenamiento,
        "reconocido_algo": any([cpu_match, gpu_match, ram_gb, almacenamiento_gb]),
        "fuente_datos": "heuristico",
    }


def _intentar_parsear_json(texto: str):
    """Devuelve (cpu_texto, gpu_texto, ram_gb, almacenamiento_gb) si el
    texto es JSON reconocible de alguno de nuestros one-liners, o None si
    no es JSON o no tiene la forma esperada."""
    try:
        data = json.loads(texto)
    except (json.JSONDecodeError, ValueError):
        return None

    # Forma del one-liner de Windows/PowerShell que armamos nosotros.
    if isinstance(data, dict) and ("procesador" in data or "ram_gb" in data):
        return (
            data.get("procesador"),
            data.get("grafica"),
            data.get("ram_gb"),
            data.get("almacenamiento_gb"),
        )

    # Forma de `system_profiler -json SPHardwareDataType` en Mac.
    if isinstance(data, dict) and "SPHardwareDataType" in data:
        hw = (data.get("SPHardwareDataType") or [{}])[0]
        chip = hw.get("chip_type") or hw.get("cpu_type")
        ram_texto = hw.get("physical_memory", "")
        ram_match = re.search(r"(\d+(?:[.,]\d+)?)", ram_texto)
        ram_gb = float(ram_match.group(1)) if ram_match else None
        return (chip, None, ram_gb, None)

    return None


@router.post("/interpretar")
async def interpretar(payload: TextoPegado, db: AsyncSession = Depends(get_db)):
    """Recibe el texto crudo que el usuario pegó desde 'Acerca de este
    equipo' (Windows/Mac) o 'Información del teléfono' (Android/iOS), y
    devuelve lo que pudo reconocer. Es heurístico, no infalible — por eso
    cada campo devuelve también si hubo coincidencia o no, para que el
    frontend deje confirmar/corregir en vez de asumir que está bien."""
    return await _interpretar_texto(payload.texto, db)


@router.post("/interpretar-imagen")
async def interpretar_imagen(archivo: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    """Misma idea que /interpretar pero a partir de una captura de pantalla
    (ej. la pantalla de resumen de Windows 11, que muestra GPU y
    almacenamiento como tarjetas visuales que el botón 'Copiar' no incluye
    en el texto). Usa OCR — es menos confiable que el texto pegado,
    especialmente con layouts de columnas, así que el resultado siempre
    hay que dejarlo confirmar, nunca darlo por hecho."""
    contenido = await archivo.read()
    imagen = Image.open(io.BytesIO(contenido))
    try:
        texto_ocr = pytesseract.image_to_string(imagen, lang="spa+eng")
    except pytesseract.TesseractNotFoundError:
        raise HTTPException(
            503,
            "El motor de reconocimiento de imagen no está instalado en el servidor. "
            "Probá pegando el texto en su lugar.",
        )
    resultado = await _interpretar_texto(texto_ocr, db)
    resultado["texto_reconocido"] = texto_ocr.strip()
    return resultado
