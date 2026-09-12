"""
Exceções customizadas do domínio.

Cada exceção representa um erro com significado de negócio específico,
não apenas um erro técnico. Isso torna o tratamento de erros mais preciso
e as mensagens mais úteis para quem usa o sistema.
"""


class ValidationError(Exception):
    """Levantada quando um objeto viola um invariante de domínio."""
    pass


class InsufficientStockError(Exception):
    """Levantada quando a quantidade solicitada excede o saldo disponível."""
    pass


class DuplicateSKUError(Exception):
    """Levantada quando se tenta cadastrar um SKU já existente."""
    pass


class DuplicateEmailError(Exception):
    """Levantada quando se tenta cadastrar um e-mail já existente."""
    pass


class ProductNotFoundError(Exception):
    """Levantada quando o produto solicitado não existe."""
    pass


class InactiveUserError(Exception):
    """Levantada quando um usuário inativo tenta realizar uma operação."""
    pass