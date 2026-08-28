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
from app.estimador import estimar_cpu, estimar_gpu

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
PATRON_CANTIDAD = re.compile(r"(\d+(?:[.,]\d+)?)\s*(GB|TB)\b", re.IGNORECASE)
PATRON_TIPO_DISCO = re.compile(r"\b(SSD|HDD|eMMC)\b", re.IGNORECASE)


def _ventana(lineas: list[str], desde: int, largo: int = 4) -> str:
    """Une la línea `desde` con las siguientes que tengan contenido real —
    cuenta líneas CON TEXTO, no líneas crudas, porque el OCR suele meter
    líneas en blanco entre cada bloque visual y con un conteo crudo la
    ventana se queda corta antes de alcanzar el valor real."""
    recolectadas = []
    i = desde
    while i < len(lineas) and len(recolectadas) < largo:
        if lineas[i].strip():
            recolectadas.append(lineas[i].strip())
        i += 1
    return " ".join(recolectadas)


def _extraer_ram_gb(texto: str) -> float | None:
    lineas = texto.splitlines()
    for i, linea in enumerate(lineas):
        if re.search(r"\b(ram|memoria)\b", linea, re.IGNORECASE) and not re.search(
            r"\b(ssd|hdd|almacenamiento|storage|disco|gráfic|graphics|vram)\b", linea, re.IGNORECASE
        ):
            m = PATRON_CANTIDAD.search(_ventana(lineas, i))
            if m:
                valor = float(m.group(1).replace(",", "."))
                return valor * 1024 if m.group(2).upper() == "TB" else valor
    return None


def _extraer_almacenamiento_gb(texto: str):
    lineas = texto.splitlines()
    for i, linea in enumerate(lineas):
        if re.search(r"\b(almacenamiento|storage|disco)\b", linea, re.IGNORECASE):
            bloque = _ventana(lineas, i)
            m = PATRON_CANTIDAD.search(bloque)
            if m:
                valor = float(m.group(1).replace(",", "."))
                if m.group(2).upper() == "TB":
                    valor *= 1024
                tipo_m = PATRON_TIPO_DISCO.search(bloque)
                tipo = tipo_m.group(1).lower() if tipo_m else None
                return valor, tipo
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
    lineas = texto.splitlines()
    candidatas = []
    for i, linea in enumerate(lineas):
        if any(p in linea.lower() for p in palabras_clave):
            candidatas.append(_ventana(lineas, i))
    return candidatas


async def _mejor_match(db: AsyncSession, tipo: str, lineas: list[str]):
    """El estimador por patrón (regex sobre la nomenclatura del fabricante)
    es más confiable que la similitud de texto para cualquier SKU
    estándar — no depende de "parecerse" a algo ya cargado, extrae el dato
    exacto. Por eso se prueba primero en TODAS las líneas candidatas.
    El catálogo por similitud queda como respaldo solo para nombres que el
    estimador no reconoce (ej. Pentium, Celeron, FX viejos) — y ahí sí hay
    riesgo de falsos positivos por prefijos compartidos ("Intel Core"),
    así que el umbral es más exigente que antes."""
    UMBRAL_MINIMO = 0.25

    for linea in lineas:
        descriptor = _limpiar_descriptor(linea)
        if len(descriptor) < 3:
            continue
        estimacion = estimar_cpu(descriptor) if tipo == "cpu" else estimar_gpu(descriptor)
        if estimacion:
            estimacion["exacto"] = False
            estimacion["estimado"] = True
            return estimacion

    mejor_catalogo = None
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
            if not mejor_catalogo or fila["puntaje_similitud"] > mejor_catalogo["puntaje_similitud"]:
                mejor_catalogo = dict(fila)

    if mejor_catalogo:
        mejor_catalogo["exacto"] = mejor_catalogo["puntaje_similitud"] >= 0.55
        mejor_catalogo["estimado"] = False
        return mejor_catalogo
    return None


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
    """Devuelve (cpu_texto, gpu_texto, ram_gb, almacenamiento_gb) si
    reconoce datos de nuestro one-liner (Windows o Mac), sin exigir que el
    bloque sea JSON válido/completo — la gente corta o pega mal el cierre
    todo el tiempo, así que busca cada clave por separado en vez de
    depender de que el conjunto entero parsee."""
    campos = {}
    for clave in ("procesador", "grafica", "ram_gb", "almacenamiento_gb"):
        m = re.search(rf'"{clave}"\s*:\s*"?([^",\n}}]+?)"?\s*(?:,|\n|}}|$)', texto)
        if m:
            campos[clave] = m.group(1).strip()

    if campos:
        def _num(clave):
            try:
                return float(campos[clave].replace(",", "."))
            except (KeyError, ValueError):
                return None

        return (campos.get("procesador"), campos.get("grafica"), _num("ram_gb"), _num("almacenamiento_gb"))

    # Forma de `system_profiler -json SPHardwareDataType` en Mac — esa sí
    # suele venir bien formada, se intenta como JSON de verdad.
    inicio, fin = texto.find("{"), texto.rfind("}")
    if inicio != -1 and fin != -1 and fin > inicio:
        try:
            data = json.loads(texto[inicio : fin + 1])
            if isinstance(data, dict) and "SPHardwareDataType" in data:
                hw = (data.get("SPHardwareDataType") or [{}])[0]
                chip = hw.get("chip_type") or hw.get("cpu_type")
                ram_texto = hw.get("physical_memory", "")
                ram_match = re.search(r"(\d+(?:[.,]\d+)?)", ram_texto)
                ram_gb = float(ram_match.group(1)) if ram_match else None
                return (chip, None, ram_gb, None)
        except (json.JSONDecodeError, ValueError):
            pass

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
