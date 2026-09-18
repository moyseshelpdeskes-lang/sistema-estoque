"""Schemas de movimentação de estoque."""

from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class MovementRequest(BaseModel):
    product_id: int = Field(gt=0)
    quantity: int = Field(gt=0, description="Quantidade a movimentar (> 0)")
    reason: str = Field(min_length=1, description="Motivo da movimentação")


class MovementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    user_id: int
    type: str
    quantity: int
    resulting_balance: int
    reason: str
    created_at: datetime


class MovementResultResponse(BaseModel):
    movement: MovementResponse
    product_name: str
    product_quantity: int
    alert: bool
    message: str