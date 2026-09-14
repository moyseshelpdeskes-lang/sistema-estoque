"""Testes unitários do ProductService."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

import unittest

from database.connection import get_connection, initialize_database
from models.category import Category
from models.supplier import Supplier
from repositories.category_repository import CategoryRepository
from repositories.supplier_repository import SupplierRepository
from services.product_service import ProductService
from utils.exceptions import DuplicateSKUError, ProductNotFoundError


class TestProductService(unittest.TestCase):

    def setUp(self):
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

        self.service = ProductService(self.conn)

    def tearDown(self):
        self.conn.close()

    def _criar_produto(self, sku: str = "EPI-001", quantity: int = 100,
                       minimum_stock: int = 20) -> None:
        self.service.create_product(
            sku=sku, name="Capacete", unit_price=45.90,
            quantity=quantity, minimum_stock=minimum_stock,
            category_id=self.cat_id, supplier_id=self.sup_id,
        )

    def test_criar_produto_retorna_produto_com_id(self):
        produto = self.service.create_product(
            sku="EPI-001", name="Capacete", unit_price=45.90,
            quantity=100, minimum_stock=20,
            category_id=self.cat_id, supplier_id=self.sup_id,
        )
        self.assertIsNotNone(produto.id)
        self.assertEqual(produto.sku, "EPI-001")

    def test_sku_duplicado_levanta_erro(self):
        self._criar_produto(sku="EPI-001")
        with self.assertRaises(DuplicateSKUError):
            self._criar_produto(sku="EPI-001")

    def test_sku_case_insensitive_na_verificacao_de_duplicata(self):
        """'epi-001' e 'EPI-001' devem ser tratados como o mesmo SKU."""
        self._criar_produto(sku="EPI-001")
        with self.assertRaises(DuplicateSKUError):
            self._criar_produto(sku="epi-001")

    def test_get_by_sku_retorna_produto(self):
        self._criar_produto(sku="EPI-001")
        produto = self.service.get_by_sku("EPI-001")
        self.assertEqual(produto.sku, "EPI-001")

    def test_get_by_sku_inexistente_levanta_erro(self):
        with self.assertRaises(ProductNotFoundError):
            self.service.get_by_sku("NAO-EXISTE")

    def test_list_products_retorna_ativos(self):
        self._criar_produto(sku="EPI-001")
        self._criar_produto(sku="EPI-002")
        produtos = self.service.list_products()
        self.assertEqual(len(produtos), 2)

    def test_list_critical_stock_retorna_apenas_criticos(self):
        self._criar_produto(sku="EPI-001", quantity=100, minimum_stock=20)
        self._criar_produto(sku="EPI-002", quantity=10, minimum_stock=20)
        self._criar_produto(sku="EPI-003", quantity=20, minimum_stock=20)

        criticos = self.service.list_critical_stock()
        skus = [p.sku for p in criticos]

        self.assertNotIn("EPI-001", skus)
        self.assertIn("EPI-002", skus)
        self.assertIn("EPI-003", skus)

    def test_deactivate_remove_produto_da_listagem(self):
        produto = self.service.create_product(
            sku="EPI-001", name="Capacete", unit_price=45.90,
            quantity=100, minimum_stock=20,
            category_id=self.cat_id, supplier_id=self.sup_id,
        )
        assert produto.id is not None
        self.service.deactivate(produto.id)
        ativos = self.service.list_products(active_only=True)
        self.assertEqual(len(ativos), 0)

    def test_deactivate_produto_inexistente_levanta_erro(self):
        with self.assertRaises(ProductNotFoundError):
            self.service.deactivate(9999)