"""
Modelo da entidade Usuário.

Responsabilidade única: representar um usuário do sistema
e garantir que ele sempre exista em estado válido.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from utils.exceptions import ValidationError

VALID_ROLES = {"admin", "employee"}


@dataclass
class User:
    """
    Representa um usuário do sistema.

    Invariantes:
        - email deve conter '@'.
        - password_hash não pode ser vazio.
        - role deve ser 'admin' ou 'employee'.
    """

    email: str
    password_hash: str
    role: str
    is_active: bool = True
    id: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        self.email = self.email.strip().lower()

        if "@" not in self.email:
            raise ValidationError(
                f"E-mail inválido: '{self.email}'."
            )

        if not self.password_hash.strip():
            raise ValidationError("Hash de senha não pode ser vazio.")

        if self.role not in VALID_ROLES:
            raise ValidationError(
                f"Perfil inválido: '{self.role}'. "
                f"Valores aceitos: {sorted(VALID_ROLES)}."
            )

    @property
    def is_admin(self) -> bool:
        """Atalho para verificar se o usuário é administrador."""
        return self.role == "admin"