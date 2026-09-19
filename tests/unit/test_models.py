"""
Testes unitários dos modelos do domínio.

Verifica que os invariantes de cada entidade são respeitados:
objetos válidos são criados com sucesso e objetos inválidos
levantam ValidationError com mensagem descritiva.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

import unittest
from typing import Any, Dict

from utils.exceptions import ValidationError
from models.category import Category
from models.supplier import Supplier
from models.user import User
from models.product import Product
from models.stock_movement import StockMovement


class TestCategory(unittest.TestCase):

    def test_criacao_valida(self):
        cat = Category(name="Ferramentas")
        self.assertEqual(cat.name, "Ferramentas")
        self.assertIsNone(cat.id)

    def test_nome_vazio_levanta_erro(self):
        with self.assertRaises(ValidationError):
            Category(name="")

    def test_nome_so_espacos_levanta_erro(self):
        with self.assertRaises(ValidationError):
            Category(name="   ")

    def test_nome_com_espacos_e_normalizado(self):
        cat = Category(name="  EPIs  ")
        self.assertEqual(cat.name, "EPIs")

    def test_nome_excede_100_caracteres_levanta_erro(self):
        with self.assertRaises(ValidationError):
            Category(name="A" * 101)


class TestSupplier(unittest.TestCase):

    def test_criacao_valida_sem_cnpj(self):
        sup = Supplier(name="Distribuidora Vitória")
        self.assertEqual(sup.name, "Distribuidora Vitória")

    def test_nome_vazio_levanta_erro(self):
        with self.assertRaises(ValidationError):
            Supplier(name="")

    def test_cnpj_valido_aceito(self):
        sup = Supplier(name="Fornecedor ES", cnpj="12.345.678/0001-90")
        self.assertEqual(sup.cnpj, "12.345.678/0001-90")

    def test_cnpj_invalido_levanta_erro(self):
        with self.assertRaises(ValidationError):
            Supplier(name="Fornecedor ES", cnpj="123")


class TestUser(unittest.TestCase):

    def test_criacao_valida_admin(self):
        user = User(email="admin@empresa.com", password_hash="hash123", role="admin")
        self.assertTrue(user.is_admin)
        self.assertTrue(user.is_active)

    def test_email_sem_arroba_levanta_erro(self):
        with self.assertRaises(ValidationError):
            User(email="invalido", password_hash="hash", role="admin")

    def test_role_invalido_levanta_erro(self):
        with self.assertRaises(ValidationError):
            User(email="a@b.com", password_hash="hash", role="gerente")

    def test_password_hash_vazio_levanta_erro(self):
        with self.assertRaises(ValidationError):
            User(email="a@b.com", password_hash="", role="employee")

    def test_email_normalizado_para_minusculas(self):
        user = User(email="ADMIN@EMPRESA.COM", password_hash="hash", role="admin")
        self.assertEqual(user.email, "admin@empresa.com")

    def test_employee_nao_e_admin(self):
        user = User(email="a@b.com", password_hash="hash", role="employee")
        self.assertFalse(user.is_admin)


class TestProduct(unittest.TestCase):

    def _produto_valido(self, **kwargs: Any) -> Product:
        """Retorna produto válido com possibilidade de sobrescrever campos."""
        base: Dict[str, Any] = dict(
            sku="EPI-001",
            name="Capacete de Segurança",
            unit_price=45.90,
            quantity=100,
            minimum_stock=20,
            category_id=1,
            supplier_id=1,
        )
        base.update(kwargs)
        return Product(**base)

    def test_criacao_valida(self):
        p = self._produto_valido()
        self.assertEqual(p.sku, "EPI-001")
        self.assertFalse(p.is_below_minimum)

    def test_sku_normalizado_para_maiusculas(self):
        p = self._produto_valido(sku="epi-001")
        self.assertEqual(p.sku, "EPI-001")

    def test_quantidade_zero_e_valida(self):
        p = self._produto_valido(quantity=0)
        self.assertEqual(p.quantity, 0)

    def test_quantidade_negativa_levanta_erro(self):
        with self.assertRaises(ValidationError):
            self._produto_valido(quantity=-1)

    def test_preco_negativo_levanta_erro(self):
        with self.assertRaises(ValidationError):
            self._produto_valido(unit_price=-10.0)

    def test_preco_zero_e_valido(self):
        p = self._produto_valido(unit_price=0.0)
        self.assertEqual(p.unit_price, 0.0)

    def test_sku_vazio_levanta_erro(self):
        with self.assertRaises(ValidationError):
            self._produto_valido(sku="")

    def test_nome_vazio_levanta_erro(self):
        with self.assertRaises(ValidationError):
            self._produto_valido(name="")

    def test_estoque_minimo_negativo_levanta_erro(self):
        with self.assertRaises(ValidationError):
            self._produto_valido(minimum_stock=-1)

    def test_is_below_minimum_quando_abaixo(self):
        p = self._produto_valido(quantity=10, minimum_stock=20)
        self.assertTrue(p.is_below_minimum)

    def test_is_below_minimum_quando_igual(self):
        p = self._produto_valido(quantity=20, minimum_stock=20)
        self.assertTrue(p.is_below_minimum)

    def test_is_below_minimum_quando_acima(self):
        p = self._produto_valido(quantity=21, minimum_stock=20)
        self.assertFalse(p.is_below_minimum)


class TestStockMovement(unittest.TestCase):

    def _movimento_valido(self, **kwargs: Any) -> StockMovement:
        """Retorna movimentação válida com possibilidade de sobrescrever campos."""
        base: Dict[str, Any] = dict(
            product_id=1,
            user_id=1,
            type="entry",
            quantity=10,
            resulting_balance=110,
            reason="Recebimento de NF-001",
        )
        base.update(kwargs)
        return StockMovement(**base)

    def test_criacao_entrada_valida(self):
        mv = self._movimento_valido(type="entry")
        self.assertEqual(mv.type, "entry")

    def test_criacao_saida_valida(self):
        mv = self._movimento_valido(type="exit", resulting_balance=90)
        self.assertEqual(mv.type, "exit")

    def test_tipo_invalido_levanta_erro(self):
        with self.assertRaises(ValidationError):
            self._movimento_valido(type="ajuste")

    def test_quantidade_zero_levanta_erro(self):
        with self.assertRaises(ValidationError):
            self._movimento_valido(quantity=0)

    def test_quantidade_negativa_levanta_erro(self):
        with self.assertRaises(ValidationError):
            self._movimento_valido(quantity=-5)

    def test_saldo_negativo_levanta_erro(self):
        with self.assertRaises(ValidationError):
            self._movimento_valido(resulting_balance=-1)

    def test_saldo_zero_e_valido(self):
        mv = self._movimento_valido(resulting_balance=0)
        self.assertEqual(mv.resulting_balance, 0)

    def test_motivo_vazio_levanta_erro(self):
        with self.assertRaises(ValidationError):
            self._movimento_valido(reason="")

    def test_motivo_so_espacos_levanta_erro(self):
        with self.assertRaises(ValidationError):
            self._movimento_valido(reason="   ")


if __name__ == "__main__":
    unittest.main()