from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional

from app.database import get_db
from app.admin_auth import verificar_admin

router = APIRouter(prefix="/api/admin", tags=["admin"], dependencies=[Depends(verificar_admin)])


class NuevoComponente(BaseModel):
    tipo: str  # 'cpu' | 'gpu'
    marca: str
    modelo: str
    puntaje_relativo: int
    nucleos: Optional[int] = None
    vram_gb: Optional[int] = None
    generacion: Optional[str] = None


@router.post("/componentes")
async def agregar_componente(datos: NuevoComponente, db: AsyncSession = Depends(get_db)):
    query = text("""
        INSERT INTO componentes (tipo, marca, modelo, puntaje_relativo, nucleos, vram_gb, generacion)
        VALUES (:tipo, :marca, :modelo, :puntaje_relativo, :nucleos, :vram_gb, :generacion)
        ON CONFLICT (marca, modelo) DO UPDATE SET puntaje_relativo = EXCLUDED.puntaje_relativo
        RETURNING id
    """)
    fila = (await db.execute(query, datos.model_dump())).mappings().first()
    await db.commit()
    return {"id": fila["id"]}


class RequisitoPrograma(BaseModel):
    componente: str
    umbral_minimo: Optional[float] = None
    umbral_recomendado: Optional[float] = None


class NuevoPrograma(BaseModel):
    perfil_id: int
    nombre: str
    requisitos: list[RequisitoPrograma] = []


@router.post("/programas")
async def agregar_programa(datos: NuevoPrograma, db: AsyncSession = Depends(get_db)):
    query = text("INSERT INTO programas (perfil_id, nombre) VALUES (:perfil_id, :nombre) RETURNING id")
    fila = (await db.execute(query, {"perfil_id": datos.perfil_id, "nombre": datos.nombre})).mappings().first()
    programa_id = fila["id"]

    for req in datos.requisitos:
        await db.execute(text("""
            INSERT INTO requisitos_programa (programa_id, componente, umbral_minimo, umbral_recomendado)
            VALUES (:programa_id, :componente, :umbral_minimo, :umbral_recomendado)
        """), {"programa_id": programa_id, **req.model_dump()})

    await db.commit()
    return {"id": programa_id}


class NuevoSistemaOperativo(BaseModel):
    nombre: str
    tipo: str  # windows | linux | macos
    liviano: bool = False
    ram_minima: Optional[float] = None
    ram_recomendada: Optional[float] = None
    almacenamiento_minimo: Optional[float] = None
    requiere_cpu_moderno: bool = False
    pros: list[str] = []
    contras: list[str] = []
    notas: Optional[str] = None
    url_referencia: Optional[str] = None


@router.post("/sistemas-operativos")
async def agregar_sistema_operativo(datos: NuevoSistemaOperativo, db: AsyncSession = Depends(get_db)):
    query = text("""
        INSERT INTO sistemas_operativos
            (nombre, tipo, liviano, ram_minima, ram_recomendada, almacenamiento_minimo,
             requiere_cpu_moderno, pros, contras, notas, url_referencia)
        VALUES
            (:nombre, :tipo, :liviano, :ram_minima, :ram_recomendada, :almacenamiento_minimo,
             :requiere_cpu_moderno, :pros, :contras, :notas, :url_referencia)
        RETURNING id
    """)
    fila = (await db.execute(query, datos.model_dump())).mappings().first()
    await db.commit()
    return {"id": fila["id"]}
