"""
Serviço de movimentações de estoque.

Responsabilidade: implementar as regras de negócio relacionadas
a entradas e saídas de estoque, garantindo consistência transacional.

Regras aplicadas:
    RN01 — Estoque nunca negativo.
    RN02 — Movimentação imutável (inserção apenas, nunca edição).
    RN03 — Saldo consistente com o histórico (transação atômica).
    RN04 — Alerta automático quando saldo <= mínimo.
"""

import sqlite3
from dataclasses import dataclass

from models.product import Product
from models.stock_movement import StockMovement
from repositories.product_repository import ProductRepository
from repositories.stock_movement_repository import StockMovementRepository
from utils.exceptions import InsufficientStockError, ProductNotFoundError


@dataclass
class MovementResult:
    """
    Resultado de uma movimentação de estoque.

    Attributes:
        movement: movimentação registrada no histórico.
        product: produto com o saldo atualizado após a movimentação.
        alert: True se o saldo atual atingiu ou ficou abaixo do mínimo.
    """

    movement: StockMovement
    product: Product
    alert: bool


class StockService:

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn
        self._product_repo = ProductRepository(conn)
        self._movement_repo = StockMovementRepository(conn)

    def _get_active_product(self, product_id: int) -> Product:
        """
        Busca produto ativo pelo ID.

        Raises:
            ProductNotFoundError: se o produto não existir ou estiver inativo.
        """
        product = self._product_repo.find_by_id(product_id)
        if not product or not product.is_active:
            raise ProductNotFoundError(
                f"Produto ID {product_id} não encontrado ou inativo."
            )
        return product

    def register_entry(
        self,
        product_id: int,
        user_id: int,
        quantity: int,
        reason: str,
    ) -> MovementResult:
        """
        Registra uma entrada de estoque (RN02, RN03, RN04).

        A operação é atômica: INSERT em stock_movements e UPDATE em
        products.quantity são confirmados juntos ou desfeitos juntos.

        Args:
            product_id: ID do produto que recebe a entrada.
            user_id: ID do usuário que registra a movimentação.
            quantity: quantidade a adicionar (deve ser > 0).
            reason: motivo da entrada.

        Returns:
            MovementResult com a movimentação, produto atualizado e alerta.

        Raises:
            ProductNotFoundError: se o produto não existir ou estiver inativo.
            ValidationError: se quantity <= 0 ou reason vazio.
        """
        product = self._get_active_product(product_id)
        new_quantity = product.quantity + quantity

        movement = StockMovement(
            product_id=product_id,
            user_id=user_id,
            type="entry",
            quantity=quantity,
            resulting_balance=new_quantity,
            reason=reason,
        )

        try:
            saved_movement = self._movement_repo.save(movement)
            self._product_repo.update_quantity(product_id, new_quantity)
            self._conn.commit()
        except Exception:
            self._conn.rollback()
            raise

        updated_product = self._product_repo.find_by_id(product_id)
        assert updated_product is not None

        return MovementResult(
            movement=saved_movement,
            product=updated_product,
            alert=updated_product.is_below_minimum,
        )

    def register_exit(
        self,
        product_id: int,
        user_id: int,
        quantity: int,
        reason: str,
    ) -> MovementResult:
        """
        Registra uma saída de estoque (RN01, RN02, RN03, RN04).

        Verifica se há saldo suficiente antes de qualquer escrita no banco.
        Se o saldo for insuficiente, nenhum dado é alterado.

        Args:
            product_id: ID do produto que sofre a saída.
            user_id: ID do usuário que registra a movimentação.
            quantity: quantidade a retirar (deve ser > 0).
            reason: motivo da saída.

        Returns:
            MovementResult com a movimentação, produto atualizado e alerta.

        Raises:
            ProductNotFoundError: se o produto não existir ou estiver inativo.
            InsufficientStockError: se o saldo for menor que a quantidade.
            ValidationError: se quantity <= 0 ou reason vazio.
        """
        product = self._get_active_product(product_id)

        if product.quantity < quantity:
            raise InsufficientStockError(
                f"Saldo insuficiente para '{product.name}': "
                f"disponível {product.quantity}, solicitado {quantity}."
            )

        new_quantity = product.quantity - quantity

        movement = StockMovement(
            product_id=product_id,
            user_id=user_id,
            type="exit",
            quantity=quantity,
            resulting_balance=new_quantity,
            reason=reason,
        )

        try:
            saved_movement = self._movement_repo.save(movement)
            self._product_repo.update_quantity(product_id, new_quantity)
            self._conn.commit()
        except Exception:
            self._conn.rollback()
            raise

        updated_product = self._product_repo.find_by_id(product_id)
        assert updated_product is not None

        return MovementResult(
            movement=saved_movement,
            product=updated_product,
            alert=updated_product.is_below_minimum,
        )

    def get_history(self, product_id: int) -> list[StockMovement]:
        """
        Retorna o histórico de movimentações de um produto.

        Args:
            product_id: ID do produto.

        Returns:
            Lista de movimentações ordenadas da mais recente à mais antiga.
        """
        self._get_active_product(product_id)
        return self._movement_repo.find_by_product_id(product_id)