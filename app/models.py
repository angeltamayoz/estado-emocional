"""
models.py - simple dataclasses / schemas for the project.
"""
from dataclasses import dataclass
from typing import Optional
from pydantic import BaseModel

@dataclass
class UserModel:
    id: int
    username: str
    email: str
    created_at: str

@dataclass
class SurveyModel:
    id: int
    user_id: int
    username: str
    mood: int
    mood_score: int
    sleep_hours: float
    appetite: int
    concentration: int
    notes: Optional[str]
    created_at: str


# Pydantic schemas moved here for reuse across the app (requests/validation)
class Register(BaseModel):
    username: str
    email: str
    password: str
    role: Optional[str] = None


class Login(BaseModel):
    username: str
    password: str


class SurveyCreate(BaseModel):
    mood: int
    mood_score: Optional[int] = None
    sleep_hours: Optional[float] = None
    appetite: Optional[int] = None
    concentration: Optional[int] = None
    notes: Optional[str] = None
