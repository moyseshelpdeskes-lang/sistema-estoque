"""
Modelo da entidade Produto.

Responsabilidade única: representar um produto do estoque
e garantir que ele sempre exista em estado válido.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from utils.exceptions import ValidationError


@dataclass
class Product:
    """
    Representa um produto do estoque.

    Invariantes:
        - sku não pode ser vazio.
        - name não pode ser vazio.
        - unit_price >= 0.
        - quantity >= 0.
        - minimum_stock >= 0.
        - category_id e supplier_id devem ser inteiros positivos.
    """

    sku: str
    name: str
    unit_price: float
    quantity: int
    minimum_stock: int
    category_id: int
    supplier_id: int
    description: str = ""
    is_active: bool = True
    id: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        self.sku = self.sku.strip().upper()
        self.name = self.name.strip()

        if not self.sku:
            raise ValidationError("SKU não pode ser vazio.")

        if not self.name:
            raise ValidationError("Nome do produto não pode ser vazio.")

        if self.unit_price < 0:
            raise ValidationError(
                f"Preço unitário não pode ser negativo: {self.unit_price}."
            )

        if self.quantity < 0:
            raise ValidationError(
                f"Quantidade não pode ser negativa: {self.quantity}."
            )

        if self.minimum_stock < 0:
            raise ValidationError(
                f"Estoque mínimo não pode ser negativo: {self.minimum_stock}."
            )

        if self.category_id <= 0:
            raise ValidationError(
                f"category_id deve ser um inteiro positivo: {self.category_id}."
            )

        if self.supplier_id <= 0:
            raise ValidationError(
                f"supplier_id deve ser um inteiro positivo: {self.supplier_id}."
            )

    @property
    def is_below_minimum(self) -> bool:
        """Retorna True se o estoque atual está no nível de alerta."""
        return self.quantity <= self.minimum_stock