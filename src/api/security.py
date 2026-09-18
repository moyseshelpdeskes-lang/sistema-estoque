"""
Funções de segurança: hashing de senha e JWT.
"""

import os
from datetime import datetime, timedelta, timezone

import bcrypt
from jose import jwt

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-mude-em-producao")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 8


def hash_password(password: str) -> str:
    """Gera hash bcrypt com custo 12 (RNF01)."""
    return bcrypt.hashpw(
        password.encode(), bcrypt.gensalt(rounds=12)
    ).decode()


def verify_password(plain_password: str, password_hash: str) -> bool:
    """Verifica se a senha corresponde ao hash armazenado."""
    return bcrypt.checkpw(plain_password.encode(), password_hash.encode())


def create_access_token(data: dict) -> str:
    """Cria JWT com expiração de 8 horas (RNF02)."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    """
    Decodifica e valida JWT.

    Raises:
        JWTError: se o token for inválido ou expirado.
    """
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])