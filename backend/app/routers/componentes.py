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


def _lineas_candidatas(texto: str, palabras_clave: list[str]) -> list[str]:
    candidatas = []
    for linea in texto.splitlines():
        if any(p in linea.lower() for p in palabras_clave):
            candidatas.append(linea)
    return candidatas or texto.splitlines()


async def _mejor_match(db: AsyncSession, tipo: str, lineas: list[str]):
    for linea in lineas:
        limpia = re.sub(r"[^\w\sáéíóúñ.-]", " ", linea, flags=re.IGNORECASE).strip()
        if len(limpia) < 3:
            continue
        query = text("""
            SELECT id, marca, modelo, puntaje_relativo,
                   ts_rank(to_tsvector('spanish', marca || ' ' || modelo), plainto_tsquery('spanish', :texto)) AS rango
            FROM componentes
            WHERE tipo = :tipo
              AND to_tsvector('spanish', marca || ' ' || modelo) @@ plainto_tsquery('spanish', :texto)
            ORDER BY rango DESC
            LIMIT 1
        """)
        fila = (await db.execute(query, {"texto": limpia, "tipo": tipo})).mappings().first()
        if fila:
            return dict(fila)
    return None


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
