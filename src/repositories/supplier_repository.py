"""Repository da entidade Fornecedor."""

import sqlite3
from datetime import datetime
from typing import List, Optional

from models.supplier import Supplier


class SupplierRepository:

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def _row_to_supplier(self, row: sqlite3.Row) -> Supplier:
        return Supplier(
            id=row["id"],
            name=row["name"],
            contact=row["contact"],
            cnpj=row["cnpj"],
            created_at=datetime.fromisoformat(row["created_at"]),
        )

    def save(self, supplier: Supplier) -> Supplier:
        cursor = self._conn.execute(
            "INSERT INTO suppliers (name, contact, cnpj) VALUES (?, ?, ?)",
            (supplier.name, supplier.contact, supplier.cnpj),
        )
        self._conn.commit()
        return self.find_by_id(cursor.lastrowid)

    def find_by_id(self, supplier_id: int) -> Optional[Supplier]:
        row = self._conn.execute(
            "SELECT * FROM suppliers WHERE id = ?",
            (supplier_id,),
        ).fetchone()
        return self._row_to_supplier(row) if row else None

    def find_all(self) -> List[Supplier]:
        rows = self._conn.execute(
            "SELECT * FROM suppliers ORDER BY name"
        ).fetchall()
        return [self._row_to_supplier(row) for row in rows]