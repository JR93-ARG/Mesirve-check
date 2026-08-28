import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.routers import perfiles, modelos, analisis, componentes
from app.migraciones import aplicar_migraciones_pendientes

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Chequeador de dispositivos API")

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

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


@app.middleware("http")
async def agregar_cabeceras_seguridad(request: Request, call_next):
    respuesta = await call_next(request)
    respuesta.headers["X-Content-Type-Options"] = "nosniff"
    respuesta.headers["X-Frame-Options"] = "DENY"
    respuesta.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    respuesta.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains"
    return respuesta


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
