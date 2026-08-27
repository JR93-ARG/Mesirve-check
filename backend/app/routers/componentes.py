import re
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

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
PATRON_ALMACENAMIENTO = re.compile(
    r"(\d+(?:[.,]\d+)?)\s*(GB|TB)\b.{0,20}?\b(SSD|HDD|eMMC|almacenamiento|storage|disco)",
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
    m = PATRON_ALMACENAMIENTO.search(texto)
    if not m:
        return None, None
    valor = float(m.group(1).replace(",", "."))
    unidad = m.group(2).upper()
    tipo = m.group(3).upper()
    if unidad == "TB":
        valor *= 1024
    tipo_normalizado = "ssd" if "SSD" in tipo else "hdd" if "HDD" in tipo else "emmc" if "EMMC" in tipo.upper() else None
    return valor, tipo_normalizado


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


@router.post("/interpretar")
async def interpretar(payload: TextoPegado, db: AsyncSession = Depends(get_db)):
    """Recibe el texto crudo que el usuario pegó desde 'Acerca de este
    equipo' (Windows/Mac) o 'Información del teléfono' (Android/iOS), y
    devuelve lo que pudo reconocer. Es heurístico, no infalible — por eso
    cada campo devuelve también si hubo coincidencia o no, para que el
    frontend deje confirmar/corregir en vez de asumir que está bien."""
    texto = payload.texto

    cpu_lineas = _lineas_candidatas(texto, ["processor", "procesador", "chip", "cpu"])
    gpu_lineas = _lineas_candidatas(texto, ["graphics", "gráfic", "gpu", "video", "tarjeta"])

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
    }
