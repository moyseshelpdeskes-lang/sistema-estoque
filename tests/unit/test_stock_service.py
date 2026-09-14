"""
Testes unitários do StockService.

Usa SQLite em memória para garantir isolamento.
Cada teste começa com banco limpo, categoria, fornecedor,
usuário e produto já cadastrados — prontos para movimentação.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

import unittest

from database.connection import get_connection, initialize_database
from models.category import Category
from models.supplier import Supplier
from models.user import User
from models.product import Product
from repositories.category_repository import CategoryRepository
from repositories.supplier_repository import SupplierRepository
from repositories.user_repository import UserRepository
from repositories.product_repository import ProductRepository
from services.stock_service import StockService
from utils.exceptions import InsufficientStockError, ProductNotFoundError


class TestStockService(unittest.TestCase):

    def setUp(self):
        """Prepara banco em memória com dados mínimos para os testes."""
        self.conn = get_connection(":memory:")
        initialize_database(self.conn)

        cat = CategoryRepository(self.conn).save(Category(name="EPIs"))
        assert cat.id is not None
        self.cat_id: int = cat.id

        sup = SupplierRepository(self.conn).save(
            Supplier(name="Fornecedor Teste", cnpj="12.345.678/0001-90")
        )
        assert sup.id is not None
        self.sup_id: int = sup.id

        user = UserRepository(self.conn).save(
            User(email="op@teste.com", password_hash="hash", role="employee")
        )
        assert user.id is not None
        self.user_id: int = user.id

        prod = ProductRepository(self.conn).save(Product(
            sku="EPI-001",
            name="Capacete",
            unit_price=45.90,
            quantity=100,
            minimum_stock=20,
            category_id=self.cat_id,
            supplier_id=self.sup_id,
        ))
        assert prod.id is not None
        self.product_id: int = prod.id

        self.service = StockService(self.conn)

    def tearDown(self):
        self.conn.close()

    # ── Entradas ───────────────────────────────────────────────────────

    def test_entrada_aumenta_saldo(self):
        result = self.service.register_entry(
            self.product_id, self.user_id, 50, "Reposição mensal"
        )
        self.assertEqual(result.movement.resulting_balance, 150)
        self.assertEqual(result.product.quantity, 150)

    def test_entrada_registra_tipo_correto(self):
        result = self.service.register_entry(
            self.product_id, self.user_id, 10, "NF-001"
        )
        self.assertEqual(result.movement.type, "entry")

    def test_entrada_sem_alerta_quando_acima_do_minimo(self):
        result = self.service.register_entry(
            self.product_id, self.user_id, 10, "Reposição"
        )
        self.assertFalse(result.alert)

    def test_entrada_preserva_motivo(self):
        result = self.service.register_entry(
            self.product_id, self.user_id, 5, "Devolução cliente"
        )
        self.assertEqual(result.movement.reason, "Devolução cliente")

    # ── Saídas ─────────────────────────────────────────────────────────

    def test_saida_reduz_saldo(self):
        result = self.service.register_exit(
            self.product_id, self.user_id, 30, "Entrega turno A"
        )
        self.assertEqual(result.movement.resulting_balance, 70)
        self.assertEqual(result.product.quantity, 70)

    def test_saida_registra_tipo_correto(self):
        result = self.service.register_exit(
            self.product_id, self.user_id, 10, "Uso interno"
        )
        self.assertEqual(result.movement.type, "exit")

    def test_saida_exata_do_saldo_e_permitida(self):
        """Saldo pode chegar a zero — apenas negativo é proibido (RN01)."""
        result = self.service.register_exit(
            self.product_id, self.user_id, 100, "Retirada total"
        )
        self.assertEqual(result.movement.resulting_balance, 0)

    # ── Alerta de estoque crítico (RN04) ───────────────────────────────

    def test_alerta_ativado_quando_saldo_igual_ao_minimo(self):
        """Estoque mínimo é 20. Saída que deixa saldo em 20 ativa alerta."""
        result = self.service.register_exit(
            self.product_id, self.user_id, 80, "Entrega grande"
        )
        self.assertEqual(result.product.quantity, 20)
        self.assertTrue(result.alert)

    def test_alerta_ativado_quando_saldo_abaixo_do_minimo(self):
        result = self.service.register_exit(
            self.product_id, self.user_id, 90, "Entrega urgente"
        )
        self.assertTrue(result.alert)

    def test_sem_alerta_quando_saldo_acima_do_minimo(self):
        result = self.service.register_exit(
            self.product_id, self.user_id, 10, "Uso normal"
        )
        self.assertFalse(result.alert)

    # ── InsufficientStockError (RN01) ──────────────────────────────────

    def test_saida_maior_que_saldo_levanta_erro(self):
        with self.assertRaises(InsufficientStockError):
            self.service.register_exit(
                self.product_id, self.user_id, 101, "Tentativa inválida"
            )

    def test_saldo_nao_alterado_apos_erro_de_estoque(self):
        """Após InsufficientStockError, o saldo deve permanecer intacto."""
        try:
            self.service.register_exit(
                self.product_id, self.user_id, 500, "Saída inválida"
            )
        except InsufficientStockError:
            pass

        produto = ProductRepository(self.conn).find_by_id(self.product_id)
        assert produto is not None
        self.assertEqual(produto.quantity, 100)

    def test_mensagem_de_erro_contem_quantidades(self):
        """A mensagem deve informar disponível e solicitado."""
        try:
            self.service.register_exit(
                self.product_id, self.user_id, 200, "Saída inválida"
            )
            self.fail("Deveria ter levantado InsufficientStockError")
        except InsufficientStockError as e:
            self.assertIn("100", str(e))
            self.assertIn("200", str(e))

    # ── ProductNotFoundError ───────────────────────────────────────────

    def test_entrada_produto_inexistente_levanta_erro(self):
        with self.assertRaises(ProductNotFoundError):
            self.service.register_entry(9999, self.user_id, 10, "Teste")

    def test_saida_produto_inexistente_levanta_erro(self):
        with self.assertRaises(ProductNotFoundError):
            self.service.register_exit(9999, self.user_id, 10, "Teste")

    # ── Histórico ──────────────────────────────────────────────────────

    def test_historico_registra_multiplas_movimentacoes(self):
        self.service.register_entry(self.product_id, self.user_id, 50, "Entrada 1")
        self.service.register_exit(self.product_id, self.user_id, 20, "Saída 1")
        self.service.register_entry(self.product_id, self.user_id, 10, "Entrada 2")

        historico = self.service.get_history(self.product_id)
        self.assertEqual(len(historico), 3)

    def test_historico_ordenado_do_mais_recente(self):
        self.service.register_entry(self.product_id, self.user_id, 10, "Primeira")
        self.service.register_exit(self.product_id, self.user_id, 5, "Segunda")

        historico = self.service.get_history(self.product_id)
        self.assertEqual(historico[0].reason, "Segunda")
        self.assertEqual(historico[1].reason, "Primeira")

    # ── Consistência transacional (RN03) ───────────────────────────────

    def test_saldo_do_produto_consistente_com_historico(self):
        """Saldo atual = 100 + 50 - 30 = 120."""
        self.service.register_entry(self.product_id, self.user_id, 50, "Entrada")
        self.service.register_exit(self.product_id, self.user_id, 30, "Saída")

        produto = ProductRepository(self.conn).find_by_id(self.product_id)
        assert produto is not None

        historico = self.service.get_history(self.product_id)
        entradas = sum(m.quantity for m in historico if m.type == "entry")
        saidas = sum(m.quantity for m in historico if m.type == "exit")
        saldo_calculado = 100 + entradas - saidas

        self.assertEqual(produto.quantity, saldo_calculado)