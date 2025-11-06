<!-- README for EmoTrack -->
# EmoTrack — Seguimiento de estado emocional

EmoTrack es una API ligera desarrollada en Python/ FastAPI para registrar usuarios y capturar encuestas de estado emocional (mood). Está pensada como un prototipo local que persiste datos en CSV para facilitar pruebas y despliegue sencillo.

Contenido de este README:
- Resumen y objetivos
- Estructura del proyecto
- Requisitos e instalación
- Cómo ejecutar
- Endpoints (contrato HTTP)
- Formato de datos (CSV)
- Seguridad y autenticación
- Desarrollo: estilo, pruebas y calidad
- Limitaciones y siguientes pasos
- Referencias y archivos importantes

Resumen y objetivos
-------------------
Objetivo: proporcionar un prototipo que permita:
- Registro, inicio/cierre de sesión y gestión básica de usuarios.
- Registrar encuestas periódicas de estado emocional (puntuación mood 1-10 + notas opcionales).
- Exponer análisis exploratorio y ayudas para visualización vía endpoints (estadísticas, alertas, evolución temporal).

Estructura del proyecto
----------------------
Raíz del servicio: `simple-auth-api/` (package de ejecución)

Principales archivos y carpetas:
- `main.py` — punto de entrada (uvicorn import string `app.api:app`).
- `requirements.txt` — dependencias mínimas para ejecutar la API.
- `requirements-analytics.txt` — (opcional) dependencias para análisis/plots (pandas, matplotlib, seaborn).
- `app/` — código fuente:
	- `api.py` — definición de endpoints HTTP (FastAPI)
	- `auth.py` — utilidades de hashing y JWT
	- `models.py` — persistencia CSV (create/read/update/delete)
	- `schemas.py` — Pydantic schemas
	- `analytics.py` — funciones EDA y generación de gráficos (si libs instaladas)
- `data/` — CSV de persistencia (`users.csv`, `surveys.csv`)
- `CHANGELOG.md`, `EXAMPLES.md` — documentación histórica y ejemplos

Requisitos e instalación
-----------------------
- Python 3.11+ recomendado (3.13 soportado, pero algunas ruedas binarias pueden faltar; usar conda si es necesario).

Instalación mínima (sin analytics pesados):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

Instalación opcional para analytics y visualizaciones (puede requerir conda en Windows):

```powershell
# Option A: pip (may fail on Windows if no wheels available)
pip install -r requirements-analytics.txt

# Option B (recommended on Windows): conda
conda create -n emotrack -c conda-forge python=3.13 fastapi uvicorn pandas matplotlib seaborn
conda activate emotrack
pip install python-jose passlib python-multipart
```

Cómo ejecutar
-------------
Arrancar el servicio en modo desarrollo con recarga automática:

```powershell
python main.py
```

La API está en: http://localhost:8000
Interfaz interactiva (Swagger): http://localhost:8000/docs

Contratos HTTP (endpoints)
-------------------------
Autenticación: JWT en header `Authorization: Bearer <token>`

User endpoints
- POST /register — body: {username, email, password}. Retorna metadata del usuario (sin contraseña).
- POST /login — body: {username, password}. Retorna {access_token, token_type}.
- POST /logout — invalidación del token.
- GET /users/{username} — obtener usuario autenticado.
- PUT /users/{user_id} — actualizar (solo el propio usuario).
- DELETE /users/{user_id} — eliminar (solo el propio usuario).

Survey endpoints
- POST /surveys — crear encuesta (mood 1-10, notes opcional).
- GET /surveys — listar encuestas (autenticado).
- GET /surveys/{id} — obtener encuesta por ID.
- PUT /surveys/{id} — actualizar encuesta.
- DELETE /surveys/{id} — eliminar encuesta.

Analytics / Dashboard endpoints
- GET /analytics/summary — estadísticas básicas, correlaciones y time series (JSON).
- GET /analytics/group-average?group_by=username — devuelve avg mood por grupo.
- GET /analytics/alerts?threshold=3.0&window_days=30 — listas de encuestas con mood <= threshold en ventana.
- GET /analytics/evolution?days=90 — evolución temporal (avg mood por día).
- GET /analytics/plot/{plot_name} — PNG image for plots (mood_hist, mood_by_user, mood_ts) — requires plotting libs.

Formato de datos (CSV)
---------------------
Local persistence is CSV-based (under `data/`). This is simple and human-readable.

- `data/users.csv` columns: `id,username,email,hashed_password,created_at`
- `data/surveys.csv` columns: `id,user_id,username,mood,notes,created_at`

Notes:
- IDs are integers assigned by scanning the CSV to pick the next id.
- Dates are ISO-8601 strings.

Seguridad y autenticación
-------------------------
- Password hashing: `passlib` with `pbkdf2_sha256` (no native bcrypt dependency to avoid Windows build issues).
- Tokens: JWT signed with a secret (see `auth.py`) and short expiry (configurable constant).
- Token invalidation: simple in-memory blacklist (suitable for dev; consider persistent revocation store in prod).

Desarrollo, estilo y calidad
---------------------------
Se aplicaron los siguientes criterios de calidad y prácticas recomendadas:

- PEP8 / formatting: follow PEP8 conventions; use `black` and `ruff`/`flake8` in CI (recommended).
- Type hints: Pydantic schemas provide runtime validation; functions include type hints where helpful.
- Modularity: separation between `api.py` (routes), `auth.py` (security), `models.py` (persistence) and `analytics.py` (EDA & plotting).
- Documentation: `README.md` (esta guía), `EXAMPLES.md` (curl examples), `CHANGELOG.md` (registro de cambios por Copilot).
- Tests: not included by spec, but recommended: unit tests for `models.py`, `auth.py` and analytics functions with `pytest`.

Limitaciones y siguientes pasos
------------------------------
- CSV persistence is simple but not safe for concurrent writes. For production, migrate to SQLite/Postgres.
- Analytics use pandas/matplotlib — on Windows prefer conda for reliable installs.
- Token blacklist is in-memory: logging out doesn't revoke tokens across multiple process instances.

Suggested next improvements:
- Add file-locking or transactional layer for CSV writes.
- Add caching for analytics endpoints to reduce recompute cost.
- Add CI pipeline with linting (black, ruff), type checks (mypy) and tests (pytest).
- Add role-based access for analytics (admin-only).

Archivos importantes
--------------------
- `main.py` — start script
- `app/api.py` — routes and endpoint definitions
- `app/models.py` — CSV persistence
- `app/auth.py` — security and hashing
- `app/analytics.py` — EDA and plotting helpers
- `data/` — CSV storage

Ejemplos y pruebas
------------------
Ver `EXAMPLES.md` para ejemplos `curl` de registro, login, logout y creación de encuestas.

Soporte y contacto
-------------------
Este proyecto fue generado y mantenido con asistencia automatizada (GitHub Copilot). Para cambios en el diseño o migraciones sugeridas, abre un issue con los requerimientos y prioridad.

Entregas y estado (nota de estado real)
------------------------------------
Este repositorio contiene la mayor parte de la documentación y el código del proyecto; sin embargo, algunos artefactos sugeridos en la documentación (p. ej. la carpeta `EVIDENCE/` o un workflow de CI en `.github/workflows/`) no están presentes por defecto en esta copia del repositorio.

Estado y recomendaciones principales:

2ª Entrega — Fundamentos de Python y control de versiones (estado):
- Documento de planeación: `project_plan.md` (presente en la raíz).
- Estructura del repositorio: `README.md`, `CONTRIBUTING.md`, `project_plan.md` y carpetas `app/`, `data/`, `Frontend/` (presentes).
- Scripts que simulan registro y manejo de encuestas: implementados en `app/` (revisar `app/api.py` y `app/models.py`).
- Manejo de CSV en `data/` (presente).
- Evidencia de Git: actualmente NO hay carpeta `EVIDENCE/` en el repositorio; crea `EVIDENCE/` y añade capturas de commits/PRs antes de la entrega.
- Informe técnico con criterios de calidad: `TECHNICAL_REPORT.md` (presente).

3ª Entrega — Gestión y análisis de datos (estado):
- Base de datos en CSV en `data/` (presente).
- Scripts en Python para limpieza y transformación: funciones principales en `app/analytics.py` (parcial — añade scripts de ejemplo o notebooks si es necesario).
- Análisis exploratorio y visualizaciones: endpoints en `app/api.py` y utilidades en `app/analytics.py` (parcial — verifica generación de PNGs en tu entorno local).
- Dashboard básico: `Frontend/dashboard.html` y `Frontend/js/dashboard.js` (presentes; verifica cobertura de métricas).
- Evidencia visual: create `EVIDENCE/dashboard_screenshots/` and add screenshots prior to delivery.

Archivos sugeridos (si no existen, crear antes de la entrega):
- `EVIDENCE/` — Carpeta para capturas, logs y evidencia de commits/PRs (no incluida por defecto).
- `.github/workflows/ci.yml` — plantilla de CI para lint/tests (recomendada; no incluida por defecto).

Pasos recomendados antes de entregar
1. Crear la carpeta `EVIDENCE/` y añadir:
	- Capturas del dashboard y `/docs` (Swagger).
	- Un listado de commits/PRs (`git log --oneline` o capturas).
2. Añadir al menos 2 tests automatizados (pytest) para `app/models.py` y `app/analytics.py`.
3. Validar localmente la ejecución del servidor y la generación de gráficos (puede requerir instalación de dependencias extra; ver `CONTRIBUTING.md`).
4. Actualizar `DELIVERY_CHECKLIST.md` con las evidencias recopiladas.