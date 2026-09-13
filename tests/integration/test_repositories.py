"""
Testes de integração dos repositories.

Usa SQLite em memória (':memory:') para isolar os testes
do banco de dados real. Cada teste começa com um banco limpo.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

import unittest
from typing import Any, Dict

from database.connection import get_connection, initialize_database
from models.category import Category
from models.supplier import Supplier
from models.product import Product
from repositories.category_repository import CategoryRepository
from repositories.product_repository import ProductRepository
from repositories.supplier_repository import SupplierRepository


class TestCategoryRepository(unittest.TestCase):

    def setUp(self):
        """Banco em memória limpo para cada teste."""
        self.conn = get_connection(":memory:")
        initialize_database(self.conn)
        self.repo = CategoryRepository(self.conn)

    def tearDown(self):
        self.conn.close()

    def test_save_retorna_categoria_com_id(self):
        cat = self.repo.save(Category(name="EPIs"))
        self.assertIsNotNone(cat.id)
        self.assertIsInstance(cat.id, int)

    def test_find_by_id_retorna_categoria_correta(self):
        salva = self.repo.save(Category(name="Ferramentas"))
        assert salva.id is not None
        encontrada = self.repo.find_by_id(salva.id)
        assert encontrada is not None
        self.assertEqual(encontrada.name, "Ferramentas")

    def test_find_by_id_inexistente_retorna_none(self):
        resultado = self.repo.find_by_id(999)
        self.assertIsNone(resultado)

    def test_find_by_name_retorna_categoria_correta(self):
        self.repo.save(Category(name="Lubrificantes"))
        encontrada = self.repo.find_by_name("Lubrificantes")
        self.assertIsNotNone(encontrada)

    def test_find_all_retorna_todas_em_ordem(self):
        self.repo.save(Category(name="Fixadores"))
        self.repo.save(Category(name="EPIs"))
        self.repo.save(Category(name="Ferramentas"))
        cats = self.repo.find_all()
        nomes = [c.name for c in cats]
        self.assertEqual(nomes, sorted(nomes))

    def test_nome_duplicado_levanta_erro(self):
        self.repo.save(Category(name="EPIs"))
        with self.assertRaises(Exception):
            self.repo.save(Category(name="EPIs"))


class TestProductRepository(unittest.TestCase):

    def setUp(self):
        self.conn = get_connection(":memory:")
        initialize_database(self.conn)

        cat_repo = CategoryRepository(self.conn)
        sup_repo = SupplierRepository(self.conn)

        cat = cat_repo.save(Category(name="EPIs"))
        assert cat.id is not None
        self.cat_id: int = cat.id

        sup = sup_repo.save(
            Supplier(name="Fornecedor Teste", cnpj="12.345.678/0001-90")
        )
        assert sup.id is not None
        self.sup_id: int = sup.id

        self.repo = ProductRepository(self.conn)

    def tearDown(self):
        self.conn.close()

    def _produto(self, **kwargs: Any) -> Product:
        base: Dict[str, Any] = dict(
            sku="EPI-001",
            name="Capacete",
            unit_price=45.90,
            quantity=100,
            minimum_stock=20,
            category_id=self.cat_id,
            supplier_id=self.sup_id,
        )
        base.update(kwargs)
        return Product(**base)

    def test_save_retorna_produto_com_id(self):
        prod = self.repo.save(self._produto())
        self.assertIsNotNone(prod.id)

    def test_find_by_sku_retorna_produto_correto(self):
        self.repo.save(self._produto(sku="EPI-001"))
        encontrado = self.repo.find_by_sku("EPI-001")
        assert encontrado is not None
        self.assertEqual(encontrado.name, "Capacete")

    def test_sku_busca_case_insensitive(self):
        self.repo.save(self._produto(sku="EPI-001"))
        encontrado = self.repo.find_by_sku("epi-001")
        self.assertIsNotNone(encontrado)

    def test_find_by_sku_inexistente_retorna_none(self):
        resultado = self.repo.find_by_sku("NAO-EXISTE")
        self.assertIsNone(resultado)

    def test_update_quantity_altera_saldo(self):
        prod = self.repo.save(self._produto(quantity=100))
        assert prod.id is not None
        self.repo.update_quantity(prod.id, 75)
        self.conn.commit()
        atualizado = self.repo.find_by_id(prod.id)
        assert atualizado is not None
        self.assertEqual(atualizado.quantity, 75)

    def test_find_all_retorna_apenas_ativos_por_padrao(self):
        p1 = self.repo.save(self._produto(sku="EPI-001"))
        assert p1.id is not None
        self.repo.save(self._produto(sku="EPI-002", name="Luva"))
        self.repo.deactivate(p1.id)
        ativos = self.repo.find_all(active_only=True)
        self.assertEqual(len(ativos), 1)
        self.assertEqual(ativos[0].sku, "EPI-002")

    def test_sku_duplicado_levanta_erro(self):
        self.repo.save(self._produto(sku="EPI-001"))
        with self.assertRaises(Exception):
            self.repo.save(self._produto(sku="EPI-001", name="Outro"))


if __name__ == "__main__":
    unittest.main()