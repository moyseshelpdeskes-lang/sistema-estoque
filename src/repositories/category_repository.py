"""
Repository da entidade Categoria.

Responsabilidade única: persistir e recuperar categorias no banco.
Sem regras de negócio — apenas CRUD.
"""

import sqlite3
from datetime import datetime
from typing import List, Optional

from models.category import Category


class CategoryRepository:

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def _row_to_category(self, row: sqlite3.Row) -> Category:
        """Converte uma linha do banco em objeto Category."""
        return Category(
            id=row["id"],
            name=row["name"],
            description=row["description"],
            created_at=datetime.fromisoformat(row["created_at"]),
        )

    def save(self, category: Category) -> Category:
        """
        Persiste uma nova categoria no banco.

        Returns:
            A mesma categoria com o id gerado pelo banco preenchido.
        """
        cursor = self._conn.execute(
            "INSERT INTO categories (name, description) VALUES (?, ?)",
            (category.name, category.description),
        )
        self._conn.commit()
        return self.find_by_id(cursor.lastrowid)

    def find_by_id(self, category_id: int) -> Optional[Category]:
        """Busca categoria pelo ID. Retorna None se não encontrada."""
        row = self._conn.execute(
            "SELECT * FROM categories WHERE id = ?",
            (category_id,),
        ).fetchone()
        return self._row_to_category(row) if row else None

    def find_by_name(self, name: str) -> Optional[Category]:
        """Busca categoria pelo nome exato. Retorna None se não encontrada."""
        row = self._conn.execute(
            "SELECT * FROM categories WHERE name = ?",
            (name.strip(),),
        ).fetchone()
        return self._row_to_category(row) if row else None

    def find_all(self) -> List[Category]:
        """Retorna todas as categorias ordenadas por nome."""
        rows = self._conn.execute(
            "SELECT * FROM categories ORDER BY name"
        ).fetchall()
        return [self._row_to_category(row) for row in rows]