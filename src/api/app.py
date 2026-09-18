"""
Aplicação FastAPI — Sistema de Gestão de Estoque.
"""

import os
import sys
from contextlib import asynccontextmanager

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from fastapi import FastAPI

from api.routers import auth, movements, products
from database.connection import get_connection, initialize_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Inicializa o banco na subida e fecha na descida."""
    db_path = os.getenv("DATABASE_PATH", "estoque.db")
    conn = get_connection(db_path)
    initialize_database(conn)
    conn.close()
    yield


app = FastAPI(
    title="Sistema de Gestão de Estoque",
    description=(
        "API REST para controle de estoque de logística industrial "
        "na Grande Vitória, ES."
    ),
    version="0.2.0",
    lifespan=lifespan,
)

app.include_router(auth.router)
app.include_router(products.router)
app.include_router(movements.router)


@app.get("/health", tags=["Sistema"])
def health_check() -> dict:
    """Verifica se a API está no ar."""
    return {"status": "ok", "version": "0.2.0"}

