"""Repository da entidade Produto."""

import sqlite3
from datetime import datetime
from typing import List, Optional

from models.product import Product


class ProductRepository:

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def _row_to_product(self, row: sqlite3.Row) -> Product:
        return Product(
            id=int(row["id"]),
            sku=row["sku"],
            name=row["name"],
            description=row["description"],
            unit_price=float(row["unit_price"]),
            quantity=int(row["quantity"]),
            minimum_stock=int(row["minimum_stock"]),
            category_id=int(row["category_id"]),
            supplier_id=int(row["supplier_id"]),
            is_active=bool(row["is_active"]),
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )

    def save(self, product: Product) -> Product:
        """Persiste um novo produto. Retorna o produto com id preenchido."""
        cursor = self._conn.execute(
            """INSERT INTO products
               (sku, name, description, unit_price, quantity,
                minimum_stock, category_id, supplier_id, is_active)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                product.sku,
                product.name,
                product.description,
                product.unit_price,
                product.quantity,
                product.minimum_stock,
                product.category_id,
                product.supplier_id,
                int(product.is_active),
            ),
        )
        self._conn.commit()
        result = self.find_by_id(cursor.lastrowid)
        assert result is not None
        return result

    def find_by_id(self, product_id: int) -> Optional[Product]:
        row = self._conn.execute(
            "SELECT * FROM products WHERE id = ?",
            (product_id,),
        ).fetchone()
        return self._row_to_product(row) if row else None

    def find_by_sku(self, sku: str) -> Optional[Product]:
        row = self._conn.execute(
            "SELECT * FROM products WHERE sku = ?",
            (sku.strip().upper(),),
        ).fetchone()
        return self._row_to_product(row) if row else None

    def find_all(self, active_only: bool = True) -> List[Product]:
        """Retorna produtos ordenados por nome."""
        if active_only:
            rows = self._conn.execute(
                "SELECT * FROM products WHERE is_active = 1 ORDER BY name"
            ).fetchall()
        else:
            rows = self._conn.execute(
                "SELECT * FROM products ORDER BY name"
            ).fetchall()
        return [self._row_to_product(row) for row in rows]

    def update_quantity(self, product_id: int, new_quantity: int) -> None:
        """
        Atualiza apenas a quantidade do produto.

        Não faz commit — a transação é gerenciada pelo Service.
        """
        self._conn.execute(
            """UPDATE products
               SET quantity = ?, updated_at = datetime('now', 'localtime')
               WHERE id = ?""",
            (new_quantity, product_id),
        )

    def deactivate(self, product_id: int) -> None:
        """Soft delete: marca o produto como inativo."""
        self._conn.execute(
            """UPDATE products
               SET is_active = 0, updated_at = datetime('now', 'localtime')
               WHERE id = ?""",
            (product_id,),
        )
        self._conn.commit()