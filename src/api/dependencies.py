"""
Dependências injetadas pelo FastAPI em cada requisição.
"""

import logging
import os
import sqlite3
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from database.connection import get_connection
from models.user import User
from repositories.user_repository import UserRepository

logger = logging.getLogger(__name__)
security = HTTPBearer()
DATABASE_PATH = os.getenv("DATABASE_PATH", "estoque.db")


def get_db():
    """Abre uma conexão SQLite por requisição e fecha ao final."""
    conn = get_connection(DATABASE_PATH)
    try:
        yield conn
    except Exception as e:
        logger.error(f"Erro na conexão: {e}")
        raise
    finally:
        conn.close()


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    conn: Annotated[sqlite3.Connection, Depends(get_db)],
) -> User:
    """Extrai e valida o usuário a partir do JWT."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais inválidas ou token expirado.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        from api.security import decode_token
        token = credentials.credentials
        payload = decode_token(token)
        raw_id = payload.get("sub")
        if raw_id is None:
            raise credentials_exception
        user_id = int(raw_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao decodificar token: {type(e).__name__}: {e}")
        raise credentials_exception

    try:
        user = UserRepository(conn).find_by_id(user_id)
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        logger.error(f"Traceback completo:\n{tb}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{type(e).__name__}: {str(e)}"
        )

    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado ou inativo.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def require_admin(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Garante que o usuário autenticado é administrador (RN05)."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito a administradores.",
        )
    return current_user