"""
Modelo da entidade Movimentação de Estoque.

Responsabilidade única: representar uma movimentação imutável
no histórico do estoque.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from utils.exceptions import ValidationError

VALID_TYPES = {"entry", "exit"}


@dataclass
class StockMovement:
    """
    Representa uma movimentação de estoque (entrada ou saída).

    Este objeto é imutável por design: representa um fato histórico
    que nunca deve ser alterado. Correções são feitas através de
    novas movimentações de ajuste.

    Invariantes:
        - type deve ser 'entry' ou 'exit'.
        - quantity deve ser maior que zero.
        - resulting_balance não pode ser negativo.
        - reason não pode ser vazio.
    """

    product_id: int
    user_id: int
    type: str
    quantity: int
    resulting_balance: int
    reason: str
    id: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        if self.type not in VALID_TYPES:
            raise ValidationError(
                f"Tipo de movimentação inválido: '{self.type}'. "
                f"Valores aceitos: {sorted(VALID_TYPES)}."
            )

        if self.quantity <= 0:
            raise ValidationError(
                f"Quantidade deve ser maior que zero: {self.quantity}."
            )

        if self.resulting_balance < 0:
            raise ValidationError(
                f"Saldo resultante não pode ser negativo: {self.resulting_balance}."
            )

        self.reason = self.reason.strip()
        if not self.reason:
            raise ValidationError("Motivo da movimentação não pode ser vazio.")