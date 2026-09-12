"""Repository da entidade Usuário."""

import sqlite3
from datetime import datetime
from typing import List, Optional

from models.user import User


class UserRepository:

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def _row_to_user(self, row: sqlite3.Row) -> User:
        return User(
            id=row["id"],
            email=row["email"],
            password_hash=row["password_hash"],
            role=row["role"],
            is_active=bool(row["is_active"]),
            created_at=datetime.fromisoformat(row["created_at"]),
        )

    def save(self, user: User) -> User:
        cursor = self._conn.execute(
            """INSERT INTO users (email, password_hash, role, is_active)
               VALUES (?, ?, ?, ?)""",
            (user.email, user.password_hash, user.role, int(user.is_active)),
        )
        self._conn.commit()
        return self.find_by_id(cursor.lastrowid)

    def find_by_id(self, user_id: int) -> Optional[User]:
        row = self._conn.execute(
            "SELECT * FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()
        return self._row_to_user(row) if row else None

    def find_by_email(self, email: str) -> Optional[User]:
        row = self._conn.execute(
            "SELECT * FROM users WHERE email = ?",
            (email.strip().lower(),),
        ).fetchone()
        return self._row_to_user(row) if row else None

    def update_status(self, user_id: int, is_active: bool) -> None:
        """Ativa ou desativa um usuário."""
        self._conn.execute(
            "UPDATE users SET is_active = ? WHERE id = ?",
            (int(is_active), user_id),
        )
        self._conn.commit()

    def find_all(self) -> List[User]:
        rows = self._conn.execute(
            "SELECT * FROM users ORDER BY email"
        ).fetchall()
        return [self._row_to_user(row) for row in rows]