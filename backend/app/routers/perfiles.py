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
