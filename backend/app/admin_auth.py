import os
from fastapi import Header, HTTPException

ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN")


async def verificar_admin(x_admin_token: str = Header(default=None)):
    """Protección simple por clave compartida — no hay sistema de cuentas
    de usuario en este proyecto, así que esto alcanza para que no
    cualquiera en internet pueda escribir en el catálogo. Si no se
    configuró ADMIN_TOKEN en el servidor, estas rutas quedan bloqueadas
    por completo (fail-safe, no fail-open)."""
    if not ADMIN_TOKEN:
        raise HTTPException(503, "Administración no configurada en el servidor.")
    if x_admin_token != ADMIN_TOKEN:
        raise HTTPException(401, "Clave de administrador inválida.")
