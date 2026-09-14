"""
IT Support Diagnostic Tool — Sistema de Gestão de Estoque
Ponto de entrada principal da aplicação.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from database.connection import get_connection, initialize_database
from cli.menus import menu_principal


def main() -> None:
    """Inicializa o banco e abre o menu principal."""
    conn = get_connection("estoque.db")
    initialize_database(conn)

    try:
        menu_principal(conn)
    finally:
        conn.close()


if __name__ == "__main__":
    main()