"""
Gerenciamento de conexão com o banco de dados SQLite.

Responsabilidade única: abrir conexões configuradas corretamente
e inicializar o schema do banco a partir das migrações SQL.
"""

import sqlite3
from pathlib import Path


def get_connection(db_path: str = "estoque.db") -> sqlite3.Connection:
    """
    Cria e retorna uma conexão SQLite configurada.

    Configurações aplicadas:
        - row_factory = sqlite3.Row: acesso às colunas por nome.
        - PRAGMA foreign_keys = ON: ativa validação de FK.

    Args:
        db_path: caminho do arquivo .db. Use ':memory:' para testes.

    Returns:
        Conexão SQLite pronta para uso.
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def initialize_database(conn: sqlite3.Connection) -> None:
    """
    Executa as migrações SQL e cria as tabelas se não existirem.

    Lê o arquivo 001_create_tables.sql e executa com executescript(),
    que suporta múltiplos comandos SQL separados por ponto-e-vírgula.

    Args:
        conn: conexão ativa com o banco de dados.
    """
    migrations_dir = Path(__file__).parent / "migrations"
    migration_file = migrations_dir / "001_create_tables.sql"

    sql = migration_file.read_text(encoding="utf-8")
    conn.executescript(sql)