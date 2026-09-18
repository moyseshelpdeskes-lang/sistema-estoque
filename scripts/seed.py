"""
Popula o banco com dados de exemplo do cenário capixaba.

Execute: python scripts/seed.py
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from database.connection import get_connection, initialize_database
from api.security import hash_password
from models.category import Category
from models.supplier import Supplier
from models.user import User
from models.product import Product
from repositories.category_repository import CategoryRepository
from repositories.supplier_repository import SupplierRepository
from repositories.user_repository import UserRepository
from repositories.product_repository import ProductRepository


def seed():
    conn = get_connection("estoque.db")
    initialize_database(conn) 

    cat_repo = CategoryRepository(conn)
    sup_repo = SupplierRepository(conn)
    user_repo = UserRepository(conn)
    prod_repo = ProductRepository(conn)

    print("Populando categorias...")
    epis = cat_repo.save(Category(name="EPIs", description="Equipamentos de Proteção Individual"))
    assert epis.id is not None

    ferramentas = cat_repo.save(Category(name="Ferramentas", description="Ferramentas manuais e elétricas"))
    assert ferramentas.id is not None

    eletricos = cat_repo.save(Category(name="Materiais Elétricos", description="Cabos, disjuntores e conexões"))
    assert eletricos.id is not None

    fixadores = cat_repo.save(Category(name="Fixadores", description="Parafusos, porcas e arruelas"))
    assert fixadores.id is not None

    lubrif = cat_repo.save(Category(name="Lubrificantes", description="Óleos e graxas industriais"))
    assert lubrif.id is not None

    print("Populando fornecedores...")
    segurança_es = sup_repo.save(Supplier(
        name="Segurança Total ES",
        contact="(27) 3322-4455",
        cnpj="12.345.678/0001-90",
    ))
    assert segurança_es.id is not None

    ferragem_cariacica = sup_repo.save(Supplier(
        name="Ferragem Cariacica Ltda",
        contact="(27) 3336-7788",
        cnpj="98.765.432/0001-11",
    ))
    assert ferragem_cariacica.id is not None

    eletro_vitoria = sup_repo.save(Supplier(
        name="Eletro Vitória Distribuidora",
        contact="(27) 3301-2233",
        cnpj="11.222.333/0001-44",
    ))
    assert eletro_vitoria.id is not None

    print("Populando usuários...")
    user_repo.save(User(
        email="admin@logistica-es.com",
        password_hash=hash_password("Admin@2026"),
        role="admin",
    ))
    user_repo.save(User(
        email="almoxarife@logistica-es.com",
        password_hash=hash_password("Funcionario@2026"),
        role="employee",
    ))

    print("Populando produtos...")
    produtos = [
        Product(sku="EPI-001", name="Capacete de Segurança Classe B",
                unit_price=45.90, quantity=80, minimum_stock=20,
                category_id=epis.id, supplier_id=segurança_es.id),
        Product(sku="EPI-002", name="Luva de Raspa Cano Curto",
                unit_price=12.50, quantity=150, minimum_stock=50,
                category_id=epis.id, supplier_id=segurança_es.id),
        Product(sku="EPI-003", name="Botina de Segurança Bico de Aço",
                unit_price=189.90, quantity=15, minimum_stock=10,
                category_id=epis.id, supplier_id=segurança_es.id),
        Product(sku="FERR-001", name='Chave de Fenda Phillips 1/4"',
                unit_price=18.90, quantity=5, minimum_stock=10,
                category_id=ferramentas.id, supplier_id=ferragem_cariacica.id),
        Product(sku="FERR-002", name='Alicate Universal 8"',
                unit_price=34.50, quantity=22, minimum_stock=8,
                category_id=ferramentas.id, supplier_id=ferragem_cariacica.id),
        Product(sku="ELET-001", name="Cabo Flexível 2,5mm² (metro)",
                unit_price=4.20, quantity=300, minimum_stock=100,
                category_id=eletricos.id, supplier_id=eletro_vitoria.id),
        Product(sku="FIX-001", name="Parafuso M8 Sextavado Zincado (cx100)",
                unit_price=28.00, quantity=12, minimum_stock=5,
                category_id=fixadores.id, supplier_id=ferragem_cariacica.id),
        Product(sku="LUB-001", name="Graxa Multiuso Tubarão 500g",
                unit_price=22.90, quantity=8, minimum_stock=10,
                category_id=lubrif.id, supplier_id=ferragem_cariacica.id),
    ]

    for produto in produtos:
        prod_repo.save(produto)

    print("\nSeed concluído.")
    print(f"  {len(produtos)} produtos cadastrados.")

    todos = prod_repo.find_all()
    criticos = [p for p in todos if p.is_below_minimum]
    if criticos:
        print(f"\n  [ALERTA] {len(criticos)} produto(s) abaixo do estoque mínimo:")
        for p in criticos:
            print(f"    - {p.sku}: {p.name} (atual: {p.quantity}, mínimo: {p.minimum_stock})")

    conn.close()


if __name__ == "__main__":
    seed()