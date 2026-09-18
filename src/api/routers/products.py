"""Endpoints de produtos."""

import sqlite3
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from api.dependencies import get_current_user, get_db, require_admin
from api.schemas.product import ProductCreate, ProductResponse
from models.user import User
from services.product_service import ProductService
from utils.exceptions import DuplicateSKUError, ProductNotFoundError, ValidationError

router = APIRouter(prefix="/products", tags=["Produtos"])


@router.get("", response_model=list[ProductResponse])
def list_products(
    conn: Annotated[sqlite3.Connection, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
    active_only: bool = True,
) -> list[ProductResponse]:
    """Lista produtos. Por padrão, retorna apenas ativos."""
    products = ProductService(conn).list_products(active_only=active_only)
    return [ProductResponse.model_validate(p) for p in products]


@router.get("/critical", response_model=list[ProductResponse])
def list_critical(
    conn: Annotated[sqlite3.Connection, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
) -> list[ProductResponse]:
    """Lista produtos com estoque igual ou abaixo do mínimo (RN04)."""
    products = ProductService(conn).list_critical_stock()
    return [ProductResponse.model_validate(p) for p in products]


@router.get("/{sku}", response_model=ProductResponse)
def get_by_sku(
    sku: str,
    conn: Annotated[sqlite3.Connection, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
) -> ProductResponse:
    """Busca produto pelo SKU."""
    try:
        product = ProductService(conn).get_by_sku(sku)
        return ProductResponse.model_validate(product)
    except ProductNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    payload: ProductCreate,
    conn: Annotated[sqlite3.Connection, Depends(get_db)],
    _: Annotated[User, Depends(require_admin)],
) -> ProductResponse:
    """Cadastra novo produto. Restrito a administradores (RN05)."""
    try:
        product = ProductService(conn).create_product(**payload.model_dump())
        return ProductResponse.model_validate(product)
    except DuplicateSKUError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao cadastrar produto: {str(e)}"
        )


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def deactivate_product(
    product_id: int,
    conn: Annotated[sqlite3.Connection, Depends(get_db)],
    _: Annotated[User, Depends(require_admin)],
) -> None:
    """Desativa produto — soft delete. Restrito a administradores (RN05)."""
    try:
        ProductService(conn).deactivate(product_id)
    except ProductNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))