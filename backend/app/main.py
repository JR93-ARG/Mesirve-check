import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os

from app.routers import perfiles, modelos, analisis, componentes
from app.migraciones import aplicar_migraciones_pendientes

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Chequeador de dispositivos API")

origenes = os.environ.get("CORS_ORIGINS", "http://localhost:5173").split(",")


@app.exception_handler(Exception)
async def manejar_error_no_capturado(request: Request, exc: Exception):
    # Sin esto, un error 500 en cualquier endpoint sale SIN headers de CORS
    # (por cómo se apilan los middlewares en Starlette) y el navegador lo
    # reporta como "bloqueado por CORS", ocultando el error real. Este
    # handler asegura que cualquier crash devuelva una respuesta prolija
    # que sí pasa por CORS normalmente.
    logging.exception("Error no manejado en %s", request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Error interno del servidor"})


@app.on_event("startup")
async def migrar_al_arrancar():
    # Corre sola cada vez que Railway levanta un nuevo deploy. Si no hay
    # migraciones nuevas en la carpeta migrations/, no hace nada.
    await aplicar_migraciones_pendientes()

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
