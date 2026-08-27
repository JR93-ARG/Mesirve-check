# Chequeador de dispositivos

Sitio que lee las specs disponibles del dispositivo del usuario, pide
confirmar lo que el navegador no puede exponer, y da un veredicto de
aptitud según el rubro de uso elegido (oficina, diseño gráfico, CAD,
POS, desarrollo, estudio).

## Estructura

```
backend/    FastAPI + SQLAlchemy async + Postgres
frontend/   React + Vite + Tailwind v4
```

## Backend — subir a Railway

1. Crear un servicio Postgres en Railway (o usar uno existente).
2. Correr la migración una vez, apuntando a esa base:
   ```
   psql $DATABASE_URL -f backend/migrations/001_schema.sql
   ```
3. Crear el servicio del backend apuntando a la carpeta `backend/`.
   Railway detecta el `Procfile` automáticamente.
4. Variables de entorno en Railway:
   - `DATABASE_URL` (Railway la inyecta solo si el Postgres está en el mismo proyecto)
   - `CORS_ORIGINS` → la URL del frontend en producción

Local:
```
cd backend
pip install -r requirements.txt --break-system-packages
uvicorn app.main:app --reload
```

## Frontend — subir a Railway o Vercel

```
cd frontend
npm install
npm run dev
```

Variable de entorno: `VITE_API_URL` apuntando a la URL del backend en Railway.

Para build de producción: `npm run build`, se sirve la carpeta `dist/`.

## Estado actual

- [x] Esquema de base de datos (componentes, modelos de equipo, perfiles de uso, requisitos, análisis)
- [x] Endpoint de scoring (`POST /api/analisis`)
- [x] Endpoint de perfiles y requisitos
- [x] Autocomplete de modelos (`GET /api/modelos/buscar`)
- [x] Pantalla de detección + confirmación + resultado
- [ ] Cargar catálogo real de `componentes` y `modelos_equipo` (los datos de ejemplo de la migración son solo para probar)
- [ ] Guía visual por sistema operativo para encontrar las specs manualmente
- [ ] Modo avanzado: agente descargable (Go) para lectura real vía WMI / system_profiler
- [ ] OCR de etiqueta del equipo como fallback de identificación
