# Chequeador de dispositivos

Sitio que lee las specs disponibles del dispositivo del usuario, pide
confirmar lo que el navegador no puede exponer, y da un veredicto de
aptitud según el rubro de uso elegido (oficina, diseño gráfico, CAD,
POS, desarrollo, estudio).

## Estructura

```
Dockerfile   Compila el frontend y lo empaqueta dentro del backend
backend/     FastAPI + SQLAlchemy async + Postgres, sirve también el frontend
frontend/    React + Vite + Tailwind v4
```

Un solo servicio: el Dockerfile compila el frontend (`npm run build`) y
copia el resultado adentro del backend, que lo sirve como archivos
estáticos en `/`. Las rutas de API quedan bajo `/api/*`. No hace falta
CORS ni configurar una URL de API — el frontend le pide todo a su propio
dominio.

## Deploy en Railway (servicio único)

1. Un solo servicio en Railway, apuntando a la raíz del repo (Root
   Directory vacío o `/`). Railway detecta el `Dockerfile` solo.
2. Variables de entorno del servicio:
   - `DATABASE_URL=${{Postgres.DATABASE_URL}}` (referencia al servicio de Postgres del mismo proyecto)
3. Generar el dominio público en Settings → Networking → Generate Domain.
4. Al arrancar, la app aplica sola las migraciones pendientes de
   `backend/migrations/` (ver `backend/app/migraciones.py`) — no hace
   falta correr SQL a mano.

Cualquier archivo `.sql` nuevo que se agregue a `backend/migrations/` (con
un número más alto que el anterior) se aplica solo en el próximo deploy.

## Desarrollo local

Backend:
```
cd backend
pip install -r requirements.txt --break-system-packages
uvicorn app.main:app --reload
```

Frontend (proceso separado en local, con `VITE_API_URL` en `frontend/.env`
apuntando a `http://localhost:8000`):
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
- [x] Deploy como servicio único (Dockerfile), sin CORS entre frontend y backend
- [ ] Cargar `modelos_equipo` de forma orgánica a partir de lo que la gente confirma manualmente
- [ ] Guía visual por sistema operativo para encontrar las specs manualmente
- [ ] Modo avanzado: agente descargable (Go) para lectura real vía WMI / system_profiler
- [ ] OCR de etiqueta del equipo como fallback de identificación
