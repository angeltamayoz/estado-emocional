# Ejemplos de uso de la API

## 1. Registrar un nuevo usuario

```bash
curl -X POST "http://localhost:8000/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "usuario1",
    "email": "usuario1@ejemplo.com",
    "password": "mipassword123"
  }'
```

Respuesta esperada:
```json
{
  "id": 1,
  "username": "usuario1",
  "email": "usuario1@ejemplo.com",
  "created_at": "2025-09-30T10:30:00.123456"
}
```

## 2. Iniciar sesión

```bash
curl -X POST "http://localhost:8000/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "usuario1",
    "password": "mipassword123"
  }'
```

Respuesta esperada:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

## 3. Cerrar sesión

```bash
curl -X POST "http://localhost:8000/logout" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

Respuesta esperada:
```json
{
  "message": "User usuario1 logged out successfully"
}
```

## 4. Crear encuesta de estado emocional

```bash
curl -X POST "http://localhost:8000/surveys" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <TOKEN>" \
  -d '{
    "mood": 7,
    "notes": "Me siento bien hoy"
  }'
```

Respuesta esperada:
```json
{
  "id": 1,
  "user_id": 1,
  "username": "usuario1",
  "mood": 7,
  "notes": "Me siento bien hoy",
  "created_at": "2025-09-30T10:45:00.123456"
}
```

## Notas importantes

- Los tokens tienen una duración de 30 minutos
- Una vez que se hace logout, el token queda invalidado
- La base de datos es en memoria, por lo que se reinicia al parar la aplicación
- Para probar la API de forma interactiva, visita: http://localhost:8000/docs