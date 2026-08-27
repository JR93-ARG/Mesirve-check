import os
import logging
from pathlib import Path

import asyncpg

logger = logging.getLogger("migraciones")

MIGRATIONS_DIR = Path(__file__).resolve().parent.parent / "migrations"


def _dsn_asyncpg(database_url: str) -> str:
    # asyncpg.connect necesita el DSN plano "postgresql://", no la variante
    # "+asyncpg" que usa el engine de SQLAlchemy en database.py.
    if database_url.startswith("postgresql+asyncpg://"):
        return database_url.replace("postgresql+asyncpg://", "postgresql://", 1)
    return database_url


async def aplicar_migraciones_pendientes():
    """Se ejecuta una vez al arrancar la app (ver evento startup en main.py).
    Lee todos los .sql de /migrations en orden alfabético, y aplica solo
    los que todavía no están registrados en _migraciones_aplicadas.
    Idempotente: correrlo de nuevo sobre una base ya migrada no hace nada."""
    database_url = _dsn_asyncpg(os.environ.get("DATABASE_URL", ""))
    if not database_url:
        logger.warning("DATABASE_URL no configurada, se omite la migración automática")
        return

    conn = await asyncpg.connect(database_url)
    try:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS _migraciones_aplicadas (
                nombre TEXT PRIMARY KEY,
                aplicada_en TIMESTAMPTZ DEFAULT now()
            )
        """)

        aplicadas = {r["nombre"] for r in await conn.fetch("SELECT nombre FROM _migraciones_aplicadas")}

        archivos = sorted(MIGRATIONS_DIR.glob("*.sql"))
        pendientes = [f for f in archivos if f.name not in aplicadas]

        if not pendientes:
            logger.info("Sin migraciones pendientes (%d ya aplicadas)", len(aplicadas))
            return

        for archivo in pendientes:
            sql = archivo.read_text(encoding="utf-8")
            logger.info("Aplicando migración: %s", archivo.name)
            async with conn.transaction():
                await conn.execute(sql)
                await conn.execute(
                    "INSERT INTO _migraciones_aplicadas (nombre) VALUES ($1)", archivo.name
                )
            logger.info("OK: %s", archivo.name)
    finally:
        await conn.close()
