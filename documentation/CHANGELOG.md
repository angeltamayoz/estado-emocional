# Changelog - EmoTrack

Registro de todos los cambios realizados en el proyecto.

---

## Cambios - 2025-09-30
**Realizado por:** GitHub Copilot

**Descripción:** Creación inicial del proyecto EmoTrack con arquitectura completa de autenticación JWT.

**Archivos creados:**
- `requirements.txt` - Dependencias del proyecto (FastAPI, uvicorn, python-jose, passlib, python-multipart)
- `README.md` - Documentación principal del proyecto con instrucciones de instalación y uso
- `EXAMPLES.md` - Ejemplos de uso de los endpoints con comandos curl
- `app/__init__.py` - Package marker para convertir app en módulo Python
- `app/schemas.py` - Esquemas Pydantic para validación de datos (UserCreate, UserLogin, UserResponse, Token, LogoutResponse)
- `app/models.py` - Modelo de usuario y base de datos en memoria (User dataclass, UserDatabase class)
- `app/auth.py` - Sistema de autenticación con JWT tokens, hashing de passwords y blacklist
- `app/api.py` - Endpoints principales de la API (register, login, logout) con FastAPI
- `main.py` - Punto de entrada para ejecutar la aplicación con uvicorn

**Impacto:** Creación de una API funcional de autenticación con 3 endpoints, manejo de datos en memoria, seguridad básica con JWT y bcrypt, sin capa de testing como se solicitó.

---

## Cambios - 2025-09-30
**Realizado por:** GitHub Copilot

**Descripción:** Migración del archivo copilot-instructions.md de Java a Python y reubicación a carpeta .github siguiendo convenciones de GitHub.

**Archivos modificados:**
- `copilot-instructions.md` - Convertido de lineamientos Java a Python (frameworks, estructura, herramientas)
- Movido de raíz del proyecto a `.github/copilot-instructions.md`

**Impacto:** Establecimiento de lineamientos claros para desarrollo Python con FastAPI, siguiendo la ubicación estándar de GitHub para archivos de configuración del repositorio.

---

## Cambios - 2025-09-30
**Realizado por:** GitHub Copilot

**Descripción:** Corrección del warning de uvicorn al iniciar la aplicación. Cambio de objeto app a string de importación para habilitar correctamente el modo reload.

**Archivos modificados:**
- `main.py` - Cambio de `app` object a `"app.api:app"` string en uvicorn.run()

**Impacto:** La aplicación ahora inicia correctamente sin warnings y con hot-reload habilitado para desarrollo.

---

## Cambios - 2025-09-30
**Realizado por:** GitHub Copilot

**Descripción:** Agregada nueva sección obligatoria en copilot-instructions.md para registro automático de cambios realizados por Copilot.

**Archivos modificados:**
- `.github/copilot-instructions.md` - Nueva sección "10. Registro de Cambios por Copilot"
- `CHANGELOG.md` - Archivo creado para mantener trazabilidad de cambios

**Impacto:** Implementación de trazabilidad completa de cambios automatizados, mejorando la documentación y transparencia del proyecto.

---

## Cambios - 2025-10-03
**Realizado por:** GitHub Copilot

**Descripción:** Añadidos endpoints y modelos en memoria para encuestas de estado emocional.

**Archivos modificados/creados:**
- `app/schemas.py` - Nuevos esquemas `SurveyCreate` y `SurveyResponse`
- `app/models.py` - `Survey` y `SurveyDatabase` en memoria
- `app/api.py` - Endpoints `POST /surveys`, `GET /surveys`, `GET /surveys/{id}` (autenticados)
- `EXAMPLES.md` - Ejemplo de uso de `POST /surveys`
- `README.md` - Referencia a los nuevos endpoints

**Impacto:** Permite a usuarios autenticados crear y consultar encuestas de estado emocional en memoria (no persistente).

---

## Cambios - 2025-10-06
**Realizado por:** GitHub Copilot

**Descripción:** Implementada persistencia local básica mediante archivos CSV (`data/users.csv`, `data/surveys.csv`).

**Archivos modificados:**
- `app/models.py` - Carga/escritura de `users.csv` y `surveys.csv` para persistencia local
- `README.md` - Documentación de la persistencia CSV

**Impacto:** Ahora los usuarios y encuestas se conservan entre reinicios del servicio mediante CSV; sigue siendo una solución simple para desarrollo/local.

---

## Cambios - 2025-10-08
**Realizado por:** GitHub Copilot

**Descripción:** Añadidos análisis exploratorio (estadísticas, correlaciones, series de tiempo) y visualizaciones (histograma, boxplot por usuario, serie de tiempo) accesibles vía API.

**Archivos modificados/creados:**
- `app/analytics.py` - Nuevo módulo para carga de CSV, EDA y generación de gráficos en PNG
- `app/api.py` - Nuevos endpoints `/analytics/summary` y `/analytics/plot/{plot_name}` que devuelven JSON y PNG respectivamente
- `requirements.txt` - Agregadas dependencias `pandas`, `matplotlib`, `seaborn`

**Impacto:** Ahora es posible consultar por HTTP un resumen de métricas y descargar visualizaciones de las encuestas para uso en frontend o reportes.