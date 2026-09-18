"""Endpoints de autenticação."""

import sqlite3
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from api.dependencies import get_db
from api.schemas.auth import LoginRequest, TokenResponse
from api.security import create_access_token, verify_password
from repositories.user_repository import UserRepository

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post("/login", response_model=TokenResponse)
def login(
    credentials: LoginRequest,
    conn: Annotated[sqlite3.Connection, Depends(get_db)],
) -> TokenResponse:
    """
    Autentica o usuário e retorna um JWT.
    RN08: usuário inativo não opera.
    """
    user = UserRepository(conn).find_by_email(credentials.email)

    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorretos.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo. Contate o administrador.",
        )

    assert user.id is not None
    token = create_access_token({"sub": str(user.id), "role": user.role})
    return TokenResponse(access_token=token)