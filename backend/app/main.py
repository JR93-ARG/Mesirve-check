import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from app.routers import perfiles, modelos, analisis, componentes
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
app.include_router(componentes.router)


@app.get("/")
async def raiz():
    return {"status": "ok"}
