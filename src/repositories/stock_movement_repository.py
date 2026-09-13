"""Repository da entidade Movimentação de Estoque."""

import sqlite3
from datetime import datetime
from typing import List, Optional

from models.stock_movement import StockMovement


class StockMovementRepository:

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def _row_to_movement(self, row: sqlite3.Row) -> StockMovement:
        return StockMovement(
            id=int(row["id"]),
            product_id=int(row["product_id"]),
            user_id=int(row["user_id"]),
            type=row["type"],
            quantity=int(row["quantity"]),
            resulting_balance=int(row["resulting_balance"]),
            reason=row["reason"],
            created_at=datetime.fromisoformat(row["created_at"]),
        )

    def save(self, movement: StockMovement) -> StockMovement:
        """
        Persiste uma movimentação.

        Não faz commit — a transação é gerenciada pelo StockService,
        que precisa fazer INSERT aqui e UPDATE em products atomicamente.
        """
        cursor = self._conn.execute(
            """INSERT INTO stock_movements
               (product_id, user_id, type, quantity, resulting_balance, reason)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (
                movement.product_id,
                movement.user_id,
                movement.type,
                movement.quantity,
                movement.resulting_balance,
                movement.reason,
            ),
        )
        result = self.find_by_id(cursor.lastrowid)
        assert result is not None
        return result

    def find_by_id(self, movement_id: int) -> Optional[StockMovement]:
        row = self._conn.execute(
            "SELECT * FROM stock_movements WHERE id = ?",
            (movement_id,),
        ).fetchone()
        return self._row_to_movement(row) if row else None

    def find_by_product_id(self, product_id: int) -> List[StockMovement]:
        """Retorna o histórico de um produto, do mais recente ao mais antigo."""
        rows = self._conn.execute(
            """SELECT * FROM stock_movements
               WHERE product_id = ?
               ORDER BY created_at DESC""",
            (product_id,),
        ).fetchall()
        return [self._row_to_movement(row) for row in rows]

    def find_all(self) -> List[StockMovement]:
        rows = self._conn.execute(
            "SELECT * FROM stock_movements ORDER BY created_at DESC"
        ).fetchall()
        return [self._row_to_movement(row) for row in rows]