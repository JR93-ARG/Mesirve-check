import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from pathlib import Path

from app.routers import perfiles, modelos, analisis
from app.migraciones import aplicar_migraciones_pendientes

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Chequeador de dispositivos API")


@app.on_event("startup")
async def migrar_al_arrancar():
    # Corre sola cada vez que Railway levanta un nuevo deploy. Si no hay
    # migraciones nuevas en la carpeta migrations/, no hace nada.
    await aplicar_migraciones_pendientes()

origenes = os.environ.get("CORS_ORIGINS", "http://localhost:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origenes,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(perfiles.router)
app.include_router(modelos.router)
app.include_router(analisis.router)


@app.get("/api/health")
async def salud():
    return {"status": "ok"}


# El frontend ya compilado (npm run build) se copia acá adentro por el
# Dockerfile, como carpeta "static". Se monta al final para que las rutas
# /api/* de arriba tengan prioridad — Starlette evalúa en orden y el mount
# en "/" matchea cualquier cosa que no haya matcheado antes.
directorio_estatico = Path(__file__).resolve().parent.parent / "static"
if directorio_estatico.exists():
    app.mount("/", StaticFiles(directory=directorio_estatico, html=True), name="frontend")
else:
    @app.get("/")
    async def raiz():
        return {"status": "ok", "aviso": "build del frontend no encontrado en /static"}
