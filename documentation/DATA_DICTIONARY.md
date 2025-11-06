# Data Dictionary — EmoTrack

Este documento describe las tablas CSV usadas por el prototipo y las columnas esperadas.

## data/users.csv
Descripción: usuarios registrados en el sistema.
Columnas:
- id: integer — identificador único (autoincremental simple).
- username: string — nombre de usuario (único en la práctica).
- email: string — email del usuario (opcionalmente validado por Pydantic).
- hashed_password: string — contraseña hasheada con passlib.
- created_at: ISO-8601 datetime string — fecha de creación.

Ejemplo de fila:
```
1,ana,ana@example.com,$pbkdf2-sha256$...,2025-10-10T12:34:56
```

## data/surveys.csv
Descripción: respuestas de encuestas de estado emocional.
Columnas:
- id: integer — id único de la encuesta.
- user_id: integer — id del usuario que respondió.
- username: string — copia del username (comodidad para consultas rápidas).
- mood: integer (1-10) — puntuación de bienestar/emoción.
- notes: text (opcional) — notas abiertas.
- created_at: ISO-8601 datetime string — fecha y hora de la respuesta.

Ejemplo de fila:
```
1,1,ana,4,"Me siento triste hoy",2025-10-10T18:00:00
```

## data/alerts.csv
Descripción: (opcional) alertas generadas por el sistema cuando se detectan puntuaciones de riesgo.
Columnas sugeridas:
- id, user_id, username, mood, reason, generated_at

## data/recommendations.csv
Descripción: recomendaciones predefinidas según nivel de riesgo.
Columnas:
- id, risk_level, title, description, url (opcional)

Notas generales
----------------
- Todos los datetime deben ser ISO-8601 para interoperabilidad.
- En entorno de producción migrar estas tablas a una base de datos relacional y normalizar (users, surveys, alerts).
- Las IDs en CSV se generan por lectura del último id y +1; esto no es seguro en concurrencia alta.