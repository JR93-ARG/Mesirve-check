from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from app.routers import perfiles, modelos, analisis

app = FastAPI(title="Chequeador de dispositivos API")

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


@app.get("/")
async def raiz():
    return {"status": "ok"}
