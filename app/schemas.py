from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    """Schema para crear un nuevo usuario"""
    username: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    """Schema para login de usuario"""
    username: str
    password: str


class UserResponse(BaseModel):
    """Schema para respuesta de usuario (sin password)"""
    id: int
    username: str
    email: str
    created_at: datetime


class Token(BaseModel):
    """Schema para respuesta de token"""
    access_token: str
    token_type: str


class LogoutResponse(BaseModel):
    """Schema para respuesta de logout"""
    message: str


class SurveyCreate(BaseModel):
    """Schema para crear una encuesta de estado emocional"""
    mood: int  # 1-10, por ejemplo
    notes: Optional[str] = None


class SurveyResponse(BaseModel):
    """Schema para respuesta de encuesta"""
    id: int
    user_id: int
    username: str
    mood: int
    notes: Optional[str] = None
    created_at: datetime