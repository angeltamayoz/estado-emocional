from datetime import datetime, timedelta
from typing import Optional, Set
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status

# Configuración de seguridad
SECRET_KEY = "tu-clave-secreta-super-segura-cambiala-en-produccion"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Contexto para hash de passwords
# Usamos pbkdf2_sha256 para evitar dependencias nativas (bcrypt) en Windows
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

# Set para tokens invalidados (logout)
blacklisted_tokens: Set[str] = set()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verificar password"""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except ValueError:
        # Problemas con el backend de hashing (p.ej. longitudes inválidas)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password verification failed due to invalid format or length"
        )


def get_password_hash(password: str) -> str:
    """Generar hash de password"""
    try:
        return pwd_context.hash(password)
    except ValueError as e:
        # Evitar devolver detalles internos del backend de hashing
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password hashing failed"
        )


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Crear token JWT"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[str]:
    """Verificar token JWT y retornar username"""
    try:
        # Verificar si el token está en blacklist
        if token in blacklisted_tokens:
            return None
            
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        return username
    except JWTError:
        return None


def blacklist_token(token: str):
    """Añadir token a blacklist (logout)"""
    blacklisted_tokens.add(token)