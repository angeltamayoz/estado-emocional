# Contributing — EmoTrack

Gracias por colaborar. Este archivo explica cómo instalar, ejecutar y contribuir en el prototipo.

Entorno recomendado
-------------------
- Python 3.11 o 3.13 (se recomienda usar conda en Windows para dependencias científicas).
- Crear y activar un virtualenv o entorno conda.

Instalación mínima (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
```

Instalación opcional para análisis/plots (recomendado en Windows con conda):
```powershell
# usando conda (recomendado en Windows)
conda create -n emotrack -c conda-forge python=3.13
conda activate emotrack
pip install -r requirements.txt
pip install pandas matplotlib seaborn
```

Ejecutar la aplicación
----------------------
```powershell
python main.py
# la API estará disponible en http://localhost:8000
```

Validación rápida de sintaxis
----------------------------
```powershell
python -m py_compile app\__init__.py app\api.py app\analytics.py app\models.py app\utils.py
```

Estilo y commits
----------------
- Formato: usar `black` para formateo y `ruff` o `flake8` para lint.
- Mensajes de commit: usar mensajes descriptivos; incluir referencia a issue si aplica.
- Branches: `main` para la versión estable; crear ramas feature/* o fix/* para cambios.

Crear PRs
--------
- Abrir PR contra `main` y describir el cambio.
- Incluir pasos para reproducir los cambios y cualquier dependencia adicional.

Tests
-----
- Añade pruebas en `tests/` usando `pytest`.
- CI (ejemplo) se incluye en `.github/workflows/ci.yml` para lint/py_compile.

-- Fin del CONTRIBUTING.md --

EVIDENCE y CI (nota práctica)
------------------------------
Esta copia del repositorio no incluye la carpeta `EVIDENCE/` ni un workflow de CI por defecto. Antes de entregar, crea manualmente:

- `EVIDENCE/` con:
	- `dashboard_screenshots/` — PNGs del dashboard y gráficos.
	- `recent_commits.txt` — `git --no-pager log --oneline -n 40 > recent_commits.txt` (o una captura).
- Opcional: un workflow en `.github/workflows/ci.yml` que ejecute lint y `python -m py_compile`.

Esto asegura que la entrega contiene la evidencia y la verificación básica solicitada por el enunciado.
