# Project Plan — EmoTrack

Versión: 1.0
Fecha: 2025-11-05
Autores: Equipo de práctica (estudiantes) — repositorio: angeltamayoz/estado-emocional

Resumen ejecutivo
-----------------
Diseñar y desarrollar una plataforma web para monitorear el estado emocional y mental de jóvenes en contextos vulnerables, integrando herramientas de análisis de datos en Python para identificar patrones de riesgo, generar alertas tempranas y ofrecer recursos de apoyo.

Objetivo (por entrega)
----------------------
- 2ª Entrega (Fundamentos de Python y control de versiones):
  - Sentar la base del proyecto con código modular y versionado.
  - Entregables: documento de planeación, estructura del repositorio, scripts de simulación (registro/carga encuestas), persistencia en CSV y evidencia de Git (commits/branches/PRs).

- 3ª Entrega (Gestión y análisis de datos):
  - Integrar fuentes de datos, limpiarlas, analizarlas y generar visualizaciones.
  - Entregables: CSVs estructurados, scripts de limpieza/EDA, visualizaciones (PNG/JS), dashboard básico y informe técnico del análisis.

Alcance inicial
----------------
- Usuarios: jóvenes de contextos vulnerables (registro y perfil emocional básico).
- Funcionalidades iniciales:
  - Registro de usuarios y autenticación (JWT).
  - Encuestas periódicas con puntuación mood (1-10) y notas opcionales.
  - Endpoints para estadísticas agregadas y generación de gráficos PNG.
  - Mecanismo simple de alertas por puntuaciones bajas.

Restricciones y supuestos
-------------------------
- Persistencia local en CSV (desarrollos en entorno local / prototipo).
- No se requiere escalado o concurrencia para la entrega; en producción migrar a una BD transaccional.
- Librerías para visualización (pandas/matplotlib/seaborn) pueden instalarse opcionalmente.

Plan de trabajo y timeline (sugerido)
--------------------------------------
- Semana 1: Definición de alcance y estructura del repo, crear README y project_plan.md (2ª Entrega).
- Semana 2: Implementación básica de endpoints (registro/login/surveys), CSV persistence, ejemplos y EXAMPLES.md.
- Semana 3: EDA inicial, endpoints de analytics y generación de plots; preparar DATA_DICTIONARY.md y TECHNICAL_REPORT.md.
- Semana 4: Recolección de evidencias, tests mínimos, CI básico y empaquetado para entrega.

Criterios de aceptación (por entrega)
-------------------------------------
- 2ª Entrega:
  - Documentación: project_plan.md, README.md y evidencia mínima de commits/branches.
  - Código: scripts que simulan registro y escritura en CSV.
  - Calidad: PEP8 y modularidad mínimas.

- 3ª Entrega:
  - CSV con datos de ejemplo en `data/` y DATA_DICTIONARY.md.
  - Scripts de limpieza/EDA en `app/analytics.py` con ejemplos de uso.
  - Visualizaciones accesibles (endpoints que devuelven PNG o JSON para plots).
  - Informe técnico describiendo las decisiones y resultados (TECHNICAL_REPORT.md).

Riesgos y mitigaciones
-----------------------
- Riesgo: problemas en instalación de libs científicas en Windows. Mitigación: documentar uso de conda y mantener la funcionalidad defensiva si libs faltan.
- Riesgo: corrupción de CSV por concurrencia. Mitigación: advertir en docs y proponer migración a SQLite.

Contacto y repositorio
----------------------
Repositorio: https://github.com/angeltamayoz/estado-emocional

-- Fin del project_plan.md --
