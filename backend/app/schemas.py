from pydantic import BaseModel
from typing import Optional
from uuid import UUID


class DatosEquipo(BaseModel):
    cpu_puntaje: Optional[float] = None
    gpu_puntaje: Optional[float] = None
    ram_gb: Optional[float] = None
    almacenamiento_gb: Optional[float] = None
    tipo_almacenamiento: Optional[str] = None  # ssd, hdd, emmc
    conexion_mbps: Optional[float] = None


class SolicitudAnalisis(BaseModel):
    perfil_id: int
    fuente: str  # 'navegador', 'agente', 'manual'
    datos_detectados: dict
    datos_confirmados: DatosEquipo
    modelo_equipo_id: Optional[int] = None


class ItemDesglose(BaseModel):
    componente: str
    valor_detectado: Optional[float]
    umbral_minimo: Optional[float]
    umbral_recomendado: Optional[float]
    puntaje: float
    peso: float


class RespuestaAnalisis(BaseModel):
    id: int
    token: UUID
    score: float
    veredicto: str
    desglose: list[ItemDesglose]


class PerfilUso(BaseModel):
    id: int
    nombre: str
    descripcion: Optional[str]
    icono: Optional[str]

    class Config:
        from_attributes = True


class ModeloEquipoResumen(BaseModel):
    id: int
    marca: str
    modelo: str
    tipo_dispositivo: str

    class Config:
        from_attributes = True
