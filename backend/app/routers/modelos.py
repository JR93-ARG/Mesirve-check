from fastapi import APIRouter, Depends, Query
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas import ModeloEquipoResumen

router = APIRouter(prefix="/api/modelos", tags=["modelos"])


@router.get("/buscar", response_model=list[ModeloEquipoResumen])
async def buscar_modelos(
    q: str = Query(..., min_length=2, description="Texto pegado o tipeado por el usuario"),
    db: AsyncSession = Depends(get_db),
):
    """Autocomplete contra el catálogo propio. Usa full-text search de Postgres
    (ver índice gin en la migración) para tolerar texto pegado desde
    'Acerca de este equipo' con ruido alrededor del modelo real."""
    query = text("""
        SELECT id, marca, modelo, tipo_dispositivo
        FROM modelos_equipo
        WHERE to_tsvector('spanish', marca || ' ' || modelo) @@ plainto_tsquery('spanish', :q)
           OR marca ILIKE :like_q OR modelo ILIKE :like_q
        LIMIT 10
    """)
    result = await db.execute(query, {"q": q, "like_q": f"%{q}%"})
    return result.mappings().all()


@router.get("/{modelo_id}")
async def detalle_modelo(modelo_id: int, db: AsyncSession = Depends(get_db)):
    """Devuelve las specs completas de fábrica de un modelo del catálogo,
    con el puntaje de sus componentes ya resuelto — esto es lo que
    autocompleta el formulario de confirmación cuando el usuario elige
    una sugerencia."""
    query = text("""
        SELECT
            me.id, me.marca, me.modelo, me.tipo_dispositivo,
            me.ram_gb_default, me.almacenamiento_gb_default, me.tipo_almacenamiento,
            cpu.modelo AS cpu_modelo, cpu.puntaje_relativo AS cpu_puntaje,
            gpu.modelo AS gpu_modelo, gpu.puntaje_relativo AS gpu_puntaje
        FROM modelos_equipo me
        LEFT JOIN componentes cpu ON cpu.id = me.cpu_id
        LEFT JOIN componentes gpu ON gpu.id = me.gpu_id
        WHERE me.id = :modelo_id
    """)
    result = await db.execute(query, {"modelo_id": modelo_id})
    return result.mappings().first()
