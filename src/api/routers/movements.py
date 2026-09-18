"""Endpoints de movimentações de estoque."""

import sqlite3
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from api.dependencies import get_current_user, get_db
from api.schemas.movement import (
    MovementRequest,
    MovementResponse,
    MovementResultResponse,
)
from models.user import User
from services.stock_service import StockService
from utils.exceptions import InsufficientStockError, ProductNotFoundError, ValidationError

router = APIRouter(prefix="/movements", tags=["Movimentações"])


@router.post("/entry", response_model=MovementResultResponse,
             status_code=status.HTTP_201_CREATED)
def register_entry(
    payload: MovementRequest,
    conn: Annotated[sqlite3.Connection, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> MovementResultResponse:
    """Registra entrada de estoque (RF06, RN02, RN03)."""
    assert current_user.id is not None
    try:
        result = StockService(conn).register_entry(
            product_id=payload.product_id,
            user_id=current_user.id,
            quantity=payload.quantity,
            reason=payload.reason,
        )
        return MovementResultResponse(
            movement=MovementResponse.model_validate(result.movement),
            product_name=result.product.name,
            product_quantity=result.product.quantity,
            alert=result.alert,
            message=f"Entrada registrada. Saldo atual: {result.product.quantity}.",
        )
    except ProductNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)
        )


@router.post("/exit", response_model=MovementResultResponse,
             status_code=status.HTTP_201_CREATED)
def register_exit(
    payload: MovementRequest,
    conn: Annotated[sqlite3.Connection, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> MovementResultResponse:
    """Registra saída de estoque (RF07, RN01, RN02, RN03)."""
    assert current_user.id is not None
    try:
        result = StockService(conn).register_exit(
            product_id=payload.product_id,
            user_id=current_user.id,
            quantity=payload.quantity,
            reason=payload.reason,
        )
        sufixo = " ⚠ Estoque crítico!" if result.alert else ""
        return MovementResultResponse(
            movement=MovementResponse.model_validate(result.movement),
            product_name=result.product.name,
            product_quantity=result.product.quantity,
            alert=result.alert,
            message=f"Saída registrada. Saldo atual: {result.product.quantity}.{sufixo}",
        )
    except ProductNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except InsufficientStockError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)
        )


@router.get("/{product_id}/history", response_model=list[MovementResponse])
def get_history(
    product_id: int,
    conn: Annotated[sqlite3.Connection, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
) -> list[MovementResponse]:
    """Retorna histórico de movimentações de um produto (RF11)."""
    try:
        movements = StockService(conn).get_history(product_id)
        return [MovementResponse.model_validate(m) for m in movements]
    except ProductNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))