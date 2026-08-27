# Chequeador de dispositivos

Sitio que lee las specs disponibles del dispositivo del usuario, pide
confirmar lo que el navegador no puede exponer, y da un veredicto de
aptitud según el rubro de uso elegido (oficina, diseño gráfico, CAD,
POS, desarrollo, estudio).

## Estructura

Un repo, dos servicios en Railway (mismo patrón que el resto de tus
proyectos):

```
backend/    FastAPI + SQLAlchemy async + Postgres — Root Directory: backend
frontend/   React + Vite + Tailwind v4 — Root Directory: frontend
```

## Deploy en Railway

**Proyecto con 3 servicios:** Postgres (ya lo tenés) + backend + frontend.

### Backend

1. Si todavía no existe como servicio propio: **New Service → Deploy from
   GitHub repo** (mismo repo), y en Settings → **Root Directory** poné
   `backend`.
2. Variables:
   - `DATABASE_URL=${{Postgres.DATABASE_URL}}`
   - `CORS_ORIGINS=https://<dominio-del-frontend>`
3. Generar dominio público (Settings → Networking → Generate Domain).
4. Al arrancar, la app aplica sola las migraciones pendientes de
   `backend/migrations/` — no hace falta correr SQL a mano. Cualquier
   `.sql` nuevo que agregues ahí (con número más alto) se aplica solo en
   el próximo deploy.

### Frontend

1. Otro servicio del mismo repo, Root Directory `frontend`.
2. Variable: `VITE_API_URL=https://<dominio-del-backend>` — **con
   `https://` incluido**, sin barra al final. Se usa en tiempo de build,
   así que si la cambiás hace falta un redeploy (no alcanza con reiniciar).
3. Generar dominio público.
4. `package.json` ya trae `serve` y el script `start` para que Railway
   levante el build de producción solo.

## Desarrollo local

Backend:
```
cd backend
pip install -r requirements.txt --break-system-packages
uvicorn app.main:app --reload
```

Frontend (con `frontend/.env` copiado de `.env.example`, apuntando a
`http://localhost:8000`):
```
cd frontend
npm install
npm run dev
```

## Estado actual

- [x] Esquema de base de datos y motor de scoring
- [x] Catálogo de CPUs/GPUs de referencia (54 CPU / 33 GPU, generaciones antiguas a actuales)
- [x] Migraciones automáticas al arrancar
- [x] Pantalla de detección + confirmación + resultado, diseño propio (panel de escaneo en vivo, medidor de barras)
- [ ] Cargar `modelos_equipo` de forma orgánica a partir de lo que la gente confirma manualmente
- [ ] Guía visual por sistema operativo para encontrar las specs manualmente
- [ ] Modo avanzado: agente descargable (Go) para lectura real vía WMI / system_profiler
- [ ] OCR de etiqueta del equipo como fallback de identificación
