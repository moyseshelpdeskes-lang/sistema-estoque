"""Schemas de produto."""

from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class ProductCreate(BaseModel):
    sku: str
    name: str
    description: str = ""
    unit_price: float = Field(ge=0, description="Preço unitário (≥ 0)")
    quantity: int = Field(ge=0, description="Quantidade inicial (≥ 0)")
    minimum_stock: int = Field(ge=0, description="Estoque mínimo (≥ 0)")
    category_id: int = Field(gt=0)
    supplier_id: int = Field(gt=0)


class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    sku: str
    name: str
    description: str
    unit_price: float
    quantity: int
    minimum_stock: int
    category_id: int
    supplier_id: int
    is_active: bool
    is_below_minimum: bool
    created_at: datetime
    updated_at: datetime