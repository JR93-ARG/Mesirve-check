from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas import PerfilUso

router = APIRouter(prefix="/api/perfiles", tags=["perfiles"])


@router.get("", response_model=list[PerfilUso])
async def listar_perfiles(db: AsyncSession = Depends(get_db)):
    """Perfiles de uso disponibles, para poblar el selector de rubro."""
    query = text("SELECT id, nombre, descripcion, icono FROM perfiles_uso ORDER BY nombre")
    result = await db.execute(query)
    return result.mappings().all()


@router.get("/{perfil_id}/requisitos")
async def requisitos_de_perfil(perfil_id: int, db: AsyncSession = Depends(get_db)):
    """Desglose de qué pesa cada componente para este rubro — útil para
    mostrar en el modo avanzado por qué se pide cada dato."""
    query = text("""
        SELECT componente, peso, umbral_minimo, umbral_recomendado
        FROM requisitos_perfil
        WHERE perfil_id = :perfil_id
        ORDER BY peso DESC
    """)
    result = await db.execute(query, {"perfil_id": perfil_id})
    return result.mappings().all()


@router.get("/{perfil_id}/recomendacion")
async def recomendacion_minima(perfil_id: int, db: AsyncSession = Depends(get_db)):
    """Para cada componente del rubro, sugiere la opción MÁS ECONÓMICA de
    nuestro catálogo que ya alcanza el umbral recomendado — no la mejor
    disponible, la mínima que ya cumple sin quedar en el límite justo.
    Para RAM/almacenamiento/conexión, que no son un modelo sino una
    cantidad, devuelve directamente el número recomendado."""
    req_query = text("""
        SELECT componente, peso, umbral_minimo, umbral_recomendado
        FROM requisitos_perfil WHERE perfil_id = :perfil_id
        ORDER BY peso DESC
    """)
    requisitos = (await db.execute(req_query, {"perfil_id": perfil_id})).mappings().all()

    UNIDAD = {"ram": "GB de RAM", "almacenamiento": "GB de almacenamiento", "conexion": "Mbps de conexión"}
    sugerencias = []

    for req in requisitos:
        if req["componente"] in ("cpu", "gpu"):
            comp_query = text("""
                SELECT marca, modelo, puntaje_relativo FROM componentes
                WHERE tipo = :tipo AND puntaje_relativo >= :umbral
                ORDER BY puntaje_relativo ASC LIMIT 1
            """)
            fila = (await db.execute(comp_query, {
                "tipo": req["componente"], "umbral": req["umbral_recomendado"],
            })).mappings().first()
            sugerencias.append({
                "componente": req["componente"],
                "sugerencia": f"{fila['marca']} {fila['modelo']}" if fila else None,
                "umbral_recomendado": float(req["umbral_recomendado"]) if req["umbral_recomendado"] is not None else None,
            })
        else:
            unidad = UNIDAD.get(req["componente"], "")
            valor = req["umbral_recomendado"]
            sugerencias.append({
                "componente": req["componente"],
                "sugerencia": f"{valor:g} {unidad}" if valor is not None else None,
                "umbral_recomendado": float(valor) if valor is not None else None,
            })

    return sugerencias
