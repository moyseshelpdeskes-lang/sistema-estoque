"""
Modelo da entidade Categoria.

Responsabilidade única: representar uma categoria de produtos
e garantir que ela sempre exista em estado válido.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from utils.exceptions import ValidationError


@dataclass
class Category:
    """
    Representa uma categoria de produtos.

    Invariantes:
        - name não pode ser vazio ou conter apenas espaços.
        - name não pode exceder 100 caracteres.
    """

    name: str
    description: str = ""
    id: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        self.name = self.name.strip()

        if not self.name:
            raise ValidationError("Nome da categoria não pode ser vazio.")

        if len(self.name) > 100:
            raise ValidationError(
                f"Nome da categoria excede 100 caracteres: {len(self.name)}."
            )