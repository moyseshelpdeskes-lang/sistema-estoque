"""
Serviço de gerenciamento de produtos.

Responsabilidade: implementar as regras de negócio relacionadas
ao ciclo de vida dos produtos no estoque.

Regras aplicadas:
    RN06 — SKU globalmente único.
    RN07 — Produto exige categoria e fornecedor.
"""

import sqlite3
from typing import List

from models.product import Product
from repositories.product_repository import ProductRepository
from utils.exceptions import DuplicateSKUError, ProductNotFoundError


class ProductService:

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn
        self._product_repo = ProductRepository(conn)

    def create_product(
        self,
        sku: str,
        name: str,
        unit_price: float,
        quantity: int,
        minimum_stock: int,
        category_id: int,
        supplier_id: int,
        description: str = "",
    ) -> Product:
        """
        Cadastra um novo produto (RN06, RN07).

        Verifica unicidade de SKU antes de persistir.
        A validação de categoria e fornecedor é garantida pelas
        constraints de FK no banco de dados.

        Raises:
            DuplicateSKUError: se o SKU já estiver cadastrado.
            ValidationError: se algum invariante do domínio for violado.
        """
        existing = self._product_repo.find_by_sku(sku)
        if existing:
            raise DuplicateSKUError(
                f"SKU '{sku.strip().upper()}' já está cadastrado."
            )

        product = Product(
            sku=sku,
            name=name,
            description=description,
            unit_price=unit_price,
            quantity=quantity,
            minimum_stock=minimum_stock,
            category_id=category_id,
            supplier_id=supplier_id,
        )

        return self._product_repo.save(product)

    def get_by_sku(self, sku: str) -> Product:
        """
        Busca produto pelo SKU.

        Raises:
            ProductNotFoundError: se o SKU não for encontrado.
        """
        product = self._product_repo.find_by_sku(sku)
        if not product:
            raise ProductNotFoundError(
                f"Produto com SKU '{sku.upper()}' não encontrado."
            )
        return product

    def list_products(self, active_only: bool = True) -> List[Product]:
        """Retorna todos os produtos ordenados por nome."""
        return self._product_repo.find_all(active_only=active_only)

    def list_critical_stock(self) -> List[Product]:
        """
        Retorna produtos com saldo igual ou abaixo do estoque mínimo (RN04).
        """
        products = self._product_repo.find_all(active_only=True)
        return [p for p in products if p.is_below_minimum]

    def deactivate(self, product_id: int) -> None:
        """
        Desativa um produto (soft delete — RN05).

        Raises:
            ProductNotFoundError: se o produto não existir.
        """
        product = self._product_repo.find_by_id(product_id)
        if not product:
            raise ProductNotFoundError(
                f"Produto ID {product_id} não encontrado."
            )
        self._product_repo.deactivate(product_id)