# Delivery Checklist — Proyecto Integrador (EmoTrack)

Este checklist mapea las entregas solicitadas en el enunciado con el contenido presente en el repositorio.

## 2ª Entrega: Fundamentos de Python y control de versiones
- [x] Documento de planeación: `project_plan.md` ✓
- [x] Estructura inicial del repositorio: `README.md`, carpetas organizadas, `LICENSE` ✓
- [x] Scripts en Python que simulen registro de usuarios y carga de encuestas: `app/` (parcial — revisar `app/api.py`, `app/models.py`) ~
- [x] Manejo de archivos CSV en `data/` ✓
- [x] Evidencia del uso de Git (commits, ramas, PRs) — poner capturas/links en `EVIDENCE/` ❗
- [x] Informe técnico con criterios de calidad: `TECHNICAL_REPORT.md` (actualizado) ✓

## 3ª Entrega: Gestión y análisis de datos
- [x] Base de datos estructurada en CSV en `data/` ✓
- [x] Scripts en Python para limpieza y transformación: `app/analytics.py` (parcial — agregar notebooks o scripts de ejemplo) ~
- [x] Análisis exploratorio y visualizaciones (`app/analytics.py`): parcial — generar PNGs y ejemplos reproducibles ~
- [x] Dashboard básico que muestre: estado emocional promedio por grupo, alertas, evolución temporal — Frontend/ endpoints partially cover this; verify and add screenshots.
- [x] Evidencia visual (capturas del dashboard, gráficos) — add to `EVIDENCE/`.
- [x] Informe técnico con proceso de análisis: `TECHNICAL_REPORT.md` (actualizado) ✓

## Recomendaciones previas a entregar
1. Rellenar `EVIDENCE/` con:
   - Capturas de la interfaz (dashboard) y gráficos.
   - Historial de commits y PRs (links o capturas).
2. Añadir 2–3 tests unitarios para `app/models.py` y `app/analytics.py`.
3. Ejecutar el servidor localmente y validar endpoints listados en `README.md`.