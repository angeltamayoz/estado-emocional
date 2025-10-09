from fastapi import FastAPI, HTTPException, status, Depends, Header, Response
from fastapi.security import HTTPBearer
from typing import Optional
from datetime import timedelta

from .models import user_db
from .models import user_db, survey_db
from .schemas import UserCreate, UserLogin, UserResponse, Token, LogoutResponse
from .schemas import SurveyCreate, SurveyResponse
from .auth import (
    verify_password, 
    get_password_hash, 
    create_access_token, 
    verify_token, 
    blacklist_token,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from .analytics import analytics_summary, generate_plot_png

app = FastAPI(
    title="EmoTrack",
    description="EmoTrack - API para seguimiento del estado emocional y encuestas",
    version="1.0.0"
)

security = HTTPBearer()


def get_current_user_from_token(authorization: str = Header(...)):
    """Extraer y validar usuario desde el token JWT"""
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication scheme"
        )
    
    token = authorization.split(" ")[1]
    username = verify_token(token)
    
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    user = user_db.get_user_by_username(username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user, token


@app.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate):
    """Registrar un nuevo usuario"""
    
    # Verificar si el usuario ya existe
    if user_db.user_exists(user_data.username, user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered"
        )
    
    # Hash del password
    try:
        hashed_password = get_password_hash(user_data.password)
    except HTTPException:
        # Ya está formateado como HTTPException en auth.get_password_hash
        raise
    except Exception:
        # Retornar error de cliente en vez de 500 para problemas de hashing
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password hashing failed"
        )
    
    # Crear usuario
    user = user_db.create_user(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password
    )
    
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        created_at=user.created_at
    )


@app.post("/login", response_model=Token)
async def login(user_data: UserLogin):
    """Iniciar sesión y obtener token JWT"""
    
    # Buscar usuario
    user = user_db.get_user_by_username(user_data.username)
    
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    # Crear token JWT
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, 
        expires_delta=access_token_expires
    )
    
    return Token(access_token=access_token, token_type="bearer")


@app.get("/users/{username}", response_model=UserResponse)
async def get_user(username: str, user_and_token = Depends(get_current_user_from_token)):
    """Obtener usuario por username"""
    _user, _ = user_and_token
    u = user_db.get_user_by_username(username)
    if u is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return UserResponse(id=u.id, username=u.username, email=u.email, created_at=u.created_at)


@app.put("/users/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, payload: UserCreate, user_and_token = Depends(get_current_user_from_token)):
    """Actualizar usuario (username/email/password) - password opcional"""
    current_user, _ = user_and_token
    # Solo permitir si es el mismo usuario (por simplicidad)
    if current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    hashed = None
    if payload.password:
        hashed = get_password_hash(payload.password)

    updated = user_db.update_user(user_id=user_id, username=payload.username, email=payload.email, hashed_password=hashed)
    if updated is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Update failed")
    return UserResponse(id=updated.id, username=updated.username, email=updated.email, created_at=updated.created_at)


@app.delete("/users/{user_id}")
async def delete_user(user_id: int, user_and_token = Depends(get_current_user_from_token)):
    current_user, _ = user_and_token
    if current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    ok = user_db.delete_user(user_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Delete failed")
    return {"message": "User deleted"}


@app.post("/logout", response_model=LogoutResponse)
async def logout(user_and_token = Depends(get_current_user_from_token)):
    """Cerrar sesión (invalidar token)"""
    
    user, token = user_and_token
    
    # Añadir token a blacklist
    blacklist_token(token)
    
    return LogoutResponse(message=f"User {user.username} logged out successfully")


@app.get("/")
async def root():
    """Endpoint raíz con información básica"""
    return {
        "message": "EmoTrack - seguimiento de estado emocional",
        "endpoints": [
            "POST /register - Registrar nuevo usuario",
            "POST /login - Iniciar sesión",
            "POST /logout - Cerrar sesión"
        ],
        "docs": "/docs"
    }


@app.post("/surveys", response_model=SurveyResponse, status_code=status.HTTP_201_CREATED)
async def create_survey(survey: SurveyCreate, user_and_token = Depends(get_current_user_from_token)):
    """Crear una encuesta de estado emocional para el usuario autenticado"""
    user, _ = user_and_token
    # Validaciones simples
    if not (1 <= survey.mood <= 10):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="mood must be between 1 and 10")

    s = survey_db.create_survey(user_id=user.id, username=user.username, mood=survey.mood, notes=survey.notes)
    return SurveyResponse(
        id=s.id,
        user_id=s.user_id,
        username=s.username,
        mood=s.mood,
        notes=s.notes,
        created_at=s.created_at
    )


@app.get("/surveys", response_model=list[SurveyResponse])
async def list_surveys(user_and_token = Depends(get_current_user_from_token)):
    """Listar todas las encuestas (limitado a desarrollo)"""
    _user, _ = user_and_token
    items = []
    for s in survey_db.list_surveys():
        items.append(SurveyResponse(id=s.id, user_id=s.user_id, username=s.username, mood=s.mood, notes=s.notes, created_at=s.created_at))
    return items


@app.get("/surveys/{survey_id}", response_model=SurveyResponse)
async def get_survey(survey_id: int, user_and_token = Depends(get_current_user_from_token)):
    """Obtener una encuesta por ID"""
    _user, _ = user_and_token
    s = survey_db.get_survey(survey_id)
    if s is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Survey not found")
    return SurveyResponse(id=s.id, user_id=s.user_id, username=s.username, mood=s.mood, notes=s.notes, created_at=s.created_at)


@app.put("/surveys/{survey_id}", response_model=SurveyResponse)
async def update_survey(survey_id: int, payload: SurveyCreate, user_and_token = Depends(get_current_user_from_token)):
    _user, _ = user_and_token
    updated = survey_db.update_survey(survey_id=survey_id, mood=payload.mood, notes=payload.notes)
    if updated is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Update failed or survey not found")
    return SurveyResponse(id=updated.id, user_id=updated.user_id, username=updated.username, mood=updated.mood, notes=updated.notes, created_at=updated.created_at)


@app.delete("/surveys/{survey_id}")
async def delete_survey(survey_id: int, user_and_token = Depends(get_current_user_from_token)):
    _user, _ = user_and_token
    ok = survey_db.delete_survey(survey_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Delete failed or survey not found")
    return {"message": "Survey deleted"}


@app.get("/analytics/summary")
async def analytics_summary_endpoint(user_and_token = Depends(get_current_user_from_token)):
    """Return exploratory statistics and correlations for users and surveys (JSON)."""
    _user, _ = user_and_token
    summary = analytics_summary()
    return summary


@app.get("/analytics/plot/{plot_name}")
async def analytics_plot_endpoint(plot_name: str, user_and_token = Depends(get_current_user_from_token)):
    """Return a PNG image (binary) for a named plot. plot_name options: 'mood_hist', 'mood_by_user'"""
    _user, _ = user_and_token
    png_bytes = generate_plot_png(plot_name)
    if png_bytes is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plot not found")
    return Response(content=png_bytes, media_type="image/png")


@app.get("/analytics/group-average")
async def analytics_group_average(group_by: str = 'username', user_and_token = Depends(get_current_user_from_token)):
    """Average mood by group (query param: group_by)."""
    _user, _ = user_and_token
    result = analytics_summary if False else None
    # call analytics helper
    from .analytics import avg_mood_by_group
    return avg_mood_by_group(group_by=group_by)


@app.get("/analytics/alerts")
async def analytics_alerts(threshold: float = 3.0, window_days: int = 30, user_and_token = Depends(get_current_user_from_token)):
    """Return alerts for surveys with mood <= threshold in last window_days."""
    _user, _ = user_and_token
    from .analytics import alerts_risk
    return alerts_risk(threshold=threshold, window_days=window_days)


@app.get("/analytics/evolution")
async def analytics_evolution(days: int = 90, user_and_token = Depends(get_current_user_from_token)):
    """Return evolution time series of average mood for last `days` days."""
    _user, _ = user_and_token
    from .analytics import evolution_time_series
    return evolution_time_series(days=days)