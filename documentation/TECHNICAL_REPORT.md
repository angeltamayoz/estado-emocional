# Technical Report - EmoTrack

Fecha: 2025-10-08
Realizado por: GitHub Copilot

## Resumen ejecutivo
EmoTrack es un prototipo de servicio web para capturar y analizar encuestas de estado emocional (mood). El objetivo principal fue construir un sistema sencillo, reproducible en local, que permita:

- Registrar usuarios y autenticarlos con JWT.
- Registrar encuestas periódicas con una puntuación de mood (1-10) y notas opcionales.
- Persistir datos en formato CSV para desarrollo local y trazabilidad fácil.
- Proveer análisis exploratorio y visualizaciones accesibles vía API.

Este informe documenta las decisiones de diseño, el proceso de análisis, los criterios de calidad aplicados y recomendaciones de mejora.

## Decisiones de diseño y motivación

1. Tecnologías principales
- FastAPI: framework ligero, alto rendimiento y documentación automática (OpenAPI/Swagger).
- passlib (pbkdf2_sha256): hashing seguro sin dependencia nativa pesada para evitar problemas en Windows.
- python-jose: gestión de JSON Web Tokens (JWT).
- pandas / matplotlib / seaborn (opcionales): para análisis y visualización. Estos paquetes pueden requerir ruedas binarias; por eso se mantienen opcionales en `requirements-analytics.txt` y la implementación es defensiva en ausencia de estas libs.

Motivación: priorizar velocidad de desarrollo, claridad del API y evitar fricciones en entornos Windows sin toolchains.

2. Persistencia: CSV
- Decisión: almacenar `users.csv` y `surveys.csv` en `data/`.
- Por qué: simplicidad, portabilidad y facilidad para revisión manual y pruebas.
- Trade-offs: no apto para concurrencia intensa ni para grandes volúmenes. Requiere migración a SQLite/Postgres en un futuro.

3. Modularidad
- Separación clara en módulos: `api.py` (routes), `auth.py` (security), `models.py` (persistence), `analytics.py` (EDA).
- Beneficio: facilita pruebas unitarias, refactor y mantenimiento.

4. Seguridad
- Hashing de contraseñas con pbkdf2_sha256 (configurable) para evitar limitaciones de bcrypt en Windows.
- JWT con expiración corta y mecanismo simple de revocación (blacklist en memoria).
- Consideración: para producción se recomienda usar HTTPS, rotación de claves y un revocation store persistente.

## Proceso de análisis implementado

- EDA básico en `analytics.py`:
  - `analytics_summary()`: recuentos, estadísticas descriptivas de `mood`, correlaciones entre promedio de mood y número de encuestas por usuario, y series temporales de promedio diario.
  - `avg_mood_by_group(group_by)`: media de mood por grupo (por defecto username).
  - `alerts_risk(threshold, window_days)`: identifica respuestas con mood <= threshold en ventana temporal reciente.
  - `evolution_time_series(days)`: series temporales de promedio por día.
  - `generate_plot_png(plot_name)`: genera histogramas, boxplots por usuario y series de tiempo como PNG (si libs instaladas).

- Consideraciones estadísticas:
  - Se usan medias (mean) y estadísticas tipo `describe()` para resumen. Estas métricas son sensibles a outliers; para robustez se puede añadir mediana y desviación intercuartílica (IQR).
  - Correlaciones calculadas con `.corr()` entre `avg_mood` y `count` por usuario; se recomienda calcular también p-values y usar Spearman si la relación no es lineal.

## Calidad de código y criterios aplicados

1. Estilo y formato
- Seguir PEP8 y usar `black` para formateo.
- Se han mantenido nombres claros y consistentes.

2. Modularidad
- Lógica de negocio separada de rutas. `models.py` encapsula acceso a CSV (create/read/update/delete) y `analytics.py` contiene la lógica EDA.

3. Validación
- Pydantic schemas (`schemas.py`) validan los payloads entrantes (tipos, formatos de email, rango de mood deberá validarse en endpoints).

4. Documentación
- README detallado, EXAMPLES con `curl` y CHANGELOG con registro de cambios.

5. Tests (recomendado)
- Añadir pruebas unitarias para:
  - `models.py`: crear, actualizar, eliminar y lectura correcta de CSV.
  - `auth.py`: hashing/verify y creación/verificación de JWT.
  - `analytics.py`: cálculos de summary, alerts y evoluciones con fixtures de datos.

## Riesgos y limitaciones

- Concurrency: CSV writes are not atomic across processes. Risk of race conditions.
- Scalability: CSV approach not suitable for large datasets or heavy read/write loads.
- Security: token blacklist is in-memory; in multi-instance deployment logout won't propagate.
- Platform-specific installs: pandas/matplotlib may require conda or build tools on Windows.

## Recomendaciones y roadmap

Short term (near next commits):
- Add file locking around CSV writes (e.g., using portalocker) to reduce corruption.
- Add basic unit tests and a GitHub Actions workflow with lint/test steps.
- Add caching for analytics endpoints (TTL-based) to reduce compute load.

Medium term:
- Migrate persistence to SQLite (as a first step) or Postgres for multi-user production.
- Move JWT secret and settings into environment/config management and add 12-factor app pattern.
- Implement RBAC for analytics (restrict to admin roles).

Long term:
- Build a frontend dashboard (React/Streamlit) that consumes analytics endpoints, with role-based UI.
- Add observability (logs, metrics, traces) and deploy to a cloud environment.

## Archivos modificados por Copilot

- `main.py`, `app/api.py`, `app/models.py`, `app/analytics.py`, `app/utils.py`, `README.md`, `EXAMPLES.md`, `CHANGELOG.md`, `project_plan.md`, `DATA_DICTIONARY.md`, `DELIVERY_CHECKLIST.md`, `CONTRIBUTING.md`.

## Entregas y artefactos para 2ª y 3ª entrega

Se agrega un mapeo explícito entre los entregables indicados en el enunciado y los archivos presentes en el repositorio. Nota: la carpeta `EVIDENCE/` y un workflow de CI **no están incluidos** por defecto en esta copia del repositorio; se recomiendan crear dichos artefactos antes de la entrega.

2ª Entrega — Fundamentos de Python y control de versiones
- Documento de planeación: `project_plan.md` (presente en la raíz).
- Estructura del repositorio: `README.md`, carpetas `app/`, `data/`, `Frontend/` (presentes). La carpeta `EVIDENCE/` no está incluida por defecto y debe crearse para recolectar evidencias de entrega.
- Scripts en Python que simulan el registro y manejo de encuestas: endpoints y utilidades en `app/api.py`, `app/models.py`, `app/utils.py`.
- Manejo de CSV: `data/users.csv` y `data/surveys.csv` (presentes en `data/`).
- Evidencia de Git: crear capturas y enlaces dentro de una carpeta `EVIDENCE/` (no incluida en esta copia del repo).
- Informe técnico con criterios de calidad: `TECHNICAL_REPORT.md` (este documento se actualizó para mapear entregables).

3ª Entrega — Gestión y análisis de datos
- Base de datos en CSV: `data/` (CSV de ejemplo incluidos).
- Scripts para limpieza y EDA: `app/analytics.py` (funciones de summary, alerts, plots).
- Visualizaciones: endpoints que generan PNGs (ver `app/api.py` y `app/analytics.py`) y frontend `Frontend/` que consume las rutas.
- Dashboard básico: `Frontend/dashboard.html` y `Frontend/js/dashboard.js` consumen endpoints para mostrar métricas y gráficos.
- Evidencia visual: cree `EVIDENCE/` y un subdirectorio `dashboard_screenshots/` para añadir PNGs del dashboard y gráficos (no incluido actualmente).

## Siguientes recomendaciones para entrega final
1. Crear y completar `EVIDENCE/` con capturas de pantalla del dashboard, logs de ejecución, y enlaces a commits y PRs.
2. Añadir 2–3 tests automatizados (pytest) para `app/models.py` y `app/analytics.py`.
3. Ejecutar el servidor local, validar los endpoints y capturar la sesión de Swagger (`/docs`).
4. Verificar dependencias en `requirements.txt` (añadir `email-validator` si fuera necesario para Pydantic/validaciones en su entorno).

*** Fin del informe ***
