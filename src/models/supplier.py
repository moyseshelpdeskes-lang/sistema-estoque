"""
Modelo da entidade Fornecedor.

Responsabilidade única: representar um fornecedor de produtos
e garantir que ele sempre exista em estado válido.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from utils.exceptions import ValidationError


@dataclass
class Supplier:
    """
    Representa um fornecedor de produtos.

    Invariantes:
        - name não pode ser vazio.
        - cnpj, quando informado, deve ter 14 dígitos numéricos.
    """

    name: str
    contact: str = ""
    cnpj: str = ""
    id: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        self.name = self.name.strip()

        if not self.name:
            raise ValidationError("Nome do fornecedor não pode ser vazio.")

        if self.cnpj:
            digits = "".join(filter(str.isdigit, self.cnpj))
            if len(digits) != 14:
                raise ValidationError(
                    f"CNPJ deve ter 14 dígitos numéricos. Recebido: '{self.cnpj}'."
                )