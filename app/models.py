"""
models.py - simple dataclasses / schemas for the project.
"""
from dataclasses import dataclass
from typing import Optional

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
