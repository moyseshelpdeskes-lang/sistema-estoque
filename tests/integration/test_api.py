"""
Testes de integração dos endpoints da API.

Usa FastAPI TestClient para simular requisições HTTP sem servidor real.
Substitui get_db por banco SQLite em memória via dependency_overrides.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

import pytest
from fastapi.testclient import TestClient

from api.app import app
from api.dependencies import get_db
from api.security import hash_password
from database.connection import get_connection, initialize_database
from models.category import Category
from models.supplier import Supplier
from models.user import User
from models.product import Product
from repositories.category_repository import CategoryRepository
from repositories.supplier_repository import SupplierRepository
from repositories.user_repository import UserRepository
from repositories.product_repository import ProductRepository


# ──────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────

@pytest.fixture
def test_db():
    """
    Banco SQLite em memória com dados mínimos para os testes da API.

    Cria: 1 categoria, 1 fornecedor, 1 admin, 1 funcionário, 1 produto.
    """
    conn = get_connection(":memory:")
    initialize_database(conn)

    cat = CategoryRepository(conn).save(Category(name="EPIs"))
    assert cat.id is not None

    sup = SupplierRepository(conn).save(
        Supplier(name="Fornecedor Teste", cnpj="12.345.678/0001-90")
    )
    assert sup.id is not None

    user_repo = UserRepository(conn)
    user_repo.save(User(
        email="admin@teste.com",
        password_hash=hash_password("Admin@123"),
        role="admin",
    ))
    user_repo.save(User(
        email="func@teste.com",
        password_hash=hash_password("Func@123"),
        role="employee",
    ))

    ProductRepository(conn).save(Product(
        sku="EPI-001",
        name="Capacete",
        unit_price=45.90,
        quantity=100,
        minimum_stock=20,
        category_id=cat.id,
        supplier_id=sup.id,
    ))

    yield conn
    conn.close()


@pytest.fixture
def client(test_db):
    """
    TestClient com banco de teste injetado via dependency_overrides.

    Qualquer endpoint que declare Depends(get_db) receberá
    o banco em memória de test_db, sem afetar o banco real.
    """
    def override_get_db():
        try:
            yield test_db
        finally:
            pass  # fechamento gerenciado pelo fixture test_db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def token_admin(client):
    """Token JWT de administrador gerado via login."""
    response = client.post("/auth/login", json={
        "email": "admin@teste.com",
        "password": "Admin@123",
    })
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture
def token_employee(client):
    """Token JWT de funcionário gerado via login."""
    response = client.post("/auth/login", json={
        "email": "func@teste.com",
        "password": "Func@123",
    })
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture
def auth_admin(token_admin):
    """Header Authorization pronto para requisições de admin."""
    return {"Authorization": f"Bearer {token_admin}"}


@pytest.fixture
def auth_employee(token_employee):
    """Header Authorization pronto para requisições de funcionário."""
    return {"Authorization": f"Bearer {token_employee}"}


# ──────────────────────────────────────────────
# Testes de autenticação
# ──────────────────────────────────────────────

class TestAuth:

    def test_login_valido_retorna_token(self, client):
        response = client.post("/auth/login", json={
            "email": "admin@teste.com",
            "password": "Admin@123",
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_senha_errada_retorna_401(self, client):
        response = client.post("/auth/login", json={
            "email": "admin@teste.com",
            "password": "senha_errada",
        })
        assert response.status_code == 401

    def test_login_email_inexistente_retorna_401(self, client):
        response = client.post("/auth/login", json={
            "email": "naoexiste@teste.com",
            "password": "qualquer",
        })
        assert response.status_code == 401

    def test_login_payload_invalido_retorna_422(self, client):
        """Pydantic valida automaticamente — campo obrigatório ausente."""
        response = client.post("/auth/login", json={"email": "admin@teste.com"})
        assert response.status_code == 422


# ──────────────────────────────────────────────
# Testes de produtos — autenticação
# ──────────────────────────────────────────────

class TestProductsAuth:

    def test_get_products_sem_token_retorna_401(self, client):
        response = client.get("/products")
        assert response.status_code == 401

    def test_get_products_com_token_retorna_200(self, client, auth_admin):
        response = client.get("/products", headers=auth_admin)
        assert response.status_code == 200

    def test_get_products_retorna_lista(self, client, auth_admin):
        response = client.get("/products", headers=auth_admin)
        assert isinstance(response.json(), list)
        assert len(response.json()) == 1

    def test_get_product_por_sku_existente(self, client, auth_admin):
        response = client.get("/products/EPI-001", headers=auth_admin)
        assert response.status_code == 200
        assert response.json()["name"] == "Capacete"

    def test_get_product_por_sku_inexistente_retorna_404(self, client, auth_admin):
        response = client.get("/products/NAO-EXISTE", headers=auth_admin)
        assert response.status_code == 404


# ──────────────────────────────────────────────
# Testes de produtos — permissões (RN05)
# ──────────────────────────────────────────────

class TestProductsPermissoes:

    def _payload_produto(self, sku: str = "NOVO-001") -> dict:
        return {
            "sku": sku,
            "name": "Produto Teste",
            "unit_price": 10.0,
            "quantity": 50,
            "minimum_stock": 5,
            "category_id": 1,
            "supplier_id": 1,
        }

    def test_criar_produto_como_admin_retorna_201(self, client, auth_admin):
        response = client.post(
            "/products", headers=auth_admin, json=self._payload_produto()
        )
        assert response.status_code == 201
        assert response.json()["sku"] == "NOVO-001"

    def test_criar_produto_como_employee_retorna_403(self, client, auth_employee):
        """RN05: funcionário não pode cadastrar produtos."""
        response = client.post(
            "/products", headers=auth_employee, json=self._payload_produto("NOVO-002")
        )
        assert response.status_code == 403

    def test_criar_produto_sku_duplicado_retorna_409(self, client, auth_admin):
        """RN06: SKU globalmente único."""
        response = client.post(
            "/products", headers=auth_admin, json=self._payload_produto("EPI-001")
        )
        assert response.status_code == 409

    def test_deletar_produto_como_employee_retorna_403(self, client, auth_employee):
        response = client.delete("/products/1", headers=auth_employee)
        assert response.status_code == 403

    def test_deletar_produto_como_admin_retorna_204(self, client, auth_admin):
        response = client.delete("/products/1", headers=auth_admin)
        assert response.status_code == 204


# ──────────────────────────────────────────────
# Testes de estoque crítico (RN04)
# ──────────────────────────────────────────────

class TestEstoqueCritico:

    def test_endpoint_critical_retorna_lista(self, client, auth_admin):
        response = client.get("/products/critical", headers=auth_admin)
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_produto_com_saldo_abaixo_do_minimo_aparece_como_critico(
        self, client, auth_admin
    ):
        """EPI-001: quantidade=100, mínimo=20 — não deve ser crítico."""
        response = client.get("/products/critical", headers=auth_admin)
        skus_criticos = [p["sku"] for p in response.json()]
        assert "EPI-001" not in skus_criticos


# ──────────────────────────────────────────────
# Testes de movimentações
# ──────────────────────────────────────────────

class TestMovimentos:

    def test_entrada_valida_retorna_201(self, client, auth_admin):
        response = client.post("/movements/entry", headers=auth_admin, json={
            "product_id": 1,
            "quantity": 50,
            "reason": "Reposição NF-001",
        })
        assert response.status_code == 201
        data = response.json()
        assert data["movement"]["type"] == "entry"
        assert data["product_quantity"] == 150

    def test_saida_valida_reduz_saldo(self, client, auth_admin):
        response = client.post("/movements/exit", headers=auth_admin, json={
            "product_id": 1,
            "quantity": 30,
            "reason": "Entrega turno A",
        })
        assert response.status_code == 201
        assert response.json()["product_quantity"] == 70

    def test_saida_com_saldo_insuficiente_retorna_409(self, client, auth_admin):
        """RN01: estoque nunca negativo."""
        response = client.post("/movements/exit", headers=auth_admin, json={
            "product_id": 1,
            "quantity": 99999,
            "reason": "Tentativa inválida",
        })
        assert response.status_code == 409

    def test_movimento_sem_token_retorna_401(self, client):
        response = client.post("/movements/entry", json={
            "product_id": 1,
            "quantity": 10,
            "reason": "Teste",
        })
        assert response.status_code == 401

    def test_historico_produto_existente_retorna_200(self, client, auth_admin):
        client.post("/movements/entry", headers=auth_admin, json={
            "product_id": 1,
            "quantity": 10,
            "reason": "Entrada para histórico",
        })
        response = client.get("/movements/1/history", headers=auth_admin)
        assert response.status_code == 200
        assert len(response.json()) >= 1

    def test_alerta_ativado_quando_saldo_atinge_minimo(self, client, auth_admin):
        """RN04: saldo 100, saída 80, resultado 20 = mínimo → alerta."""
        response = client.post("/movements/exit", headers=auth_admin, json={
            "product_id": 1,
            "quantity": 80,
            "reason": "Entrega grande",
        })
        assert response.status_code == 201
        assert response.json()["alert"] is True


# ──────────────────────────────────────────────
# Testes do sistema
# ──────────────────────────────────────────────

class TestSistema:

    def test_health_check_retorna_ok(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

    def test_health_nao_requer_autenticacao(self, client):
        """Endpoint de saúde deve ser acessível sem token."""
        response = client.get("/health")
        assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])