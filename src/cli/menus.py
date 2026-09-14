"""
Menus da interface de linha de comando.

Responsabilidade única: orquestrar a navegação entre telas,
capturar inputs e delegar operações aos services.
"""

import sqlite3

from cli.formatters import (
    cabecalho,
    exibir_historico,
    exibir_lista_produtos,
    exibir_produto_detalhe,
    exibir_resultado_movimentacao,
    separador,
)
from cli.prompts import input_float, input_inteiro, input_opcao, input_texto
from services.product_service import ProductService
from services.stock_service import StockService
from utils.exceptions import (
    DuplicateSKUError,
    InsufficientStockError,
    ProductNotFoundError,
    ValidationError,
)

# ID fixo do usuário operador enquanto auth não está implementada (Fase 6)
OPERADOR_ID = 1


def _menu_produtos(product_service: ProductService) -> None:
    """Submenu de gerenciamento de produtos."""
    while True:
        cabecalho("PRODUTOS")
        print("  1. Listar todos os produtos")
        print("  2. Cadastrar novo produto")
        print("  3. Buscar por SKU")
        print("  4. Ver estoque crítico")
        print("  0. Voltar")
        separador()

        opcao = input_opcao("Opção", ["0", "1", "2", "3", "4"])

        if opcao == "0":
            break

        elif opcao == "1":
            cabecalho("LISTA DE PRODUTOS")
            produtos = product_service.list_products()
            exibir_lista_produtos(produtos)

        elif opcao == "2":
            cabecalho("CADASTRAR PRODUTO")
            try:
                sku = input_texto("SKU (ex: EPI-001)")
                name = input_texto("Nome")
                description = input_texto("Descrição (opcional)", obrigatorio=False)
                unit_price = input_float("Preço unitário (ex: 45.90)", minimo=0.0)
                quantity = input_inteiro("Quantidade inicial", minimo=0)
                minimum_stock = input_inteiro("Estoque mínimo", minimo=0)
                category_id = input_inteiro("ID da categoria")
                supplier_id = input_inteiro("ID do fornecedor")

                produto = product_service.create_product(
                    sku=sku,
                    name=name,
                    description=description,
                    unit_price=unit_price,
                    quantity=quantity,
                    minimum_stock=minimum_stock,
                    category_id=category_id,
                    supplier_id=supplier_id,
                )
                print(f"\n  ✓ Produto '{produto.name}' cadastrado com sucesso.")
                print(f"    ID: {produto.id}  SKU: {produto.sku}")

            except (DuplicateSKUError, ValidationError) as e:
                print(f"\n  ✗ Erro: {e}")

        elif opcao == "3":
            cabecalho("BUSCAR PRODUTO")
            sku = input_texto("SKU")
            try:
                produto = product_service.get_by_sku(sku)
                exibir_produto_detalhe(produto)
            except ProductNotFoundError as e:
                print(f"\n  ✗ {e}")

        elif opcao == "4":
            cabecalho("ESTOQUE CRÍTICO")
            criticos = product_service.list_critical_stock()
            if not criticos:
                print("\n  ✓ Nenhum produto abaixo do estoque mínimo.")
            else:
                print(f"\n  ⚠  {len(criticos)} produto(s) em nível crítico:\n")
                exibir_lista_produtos(criticos)

        input("\n  [Enter para continuar]")


def _menu_movimentacoes(
    stock_service: StockService,
    product_service: ProductService,
) -> None:
    """Submenu de movimentações de estoque."""
    while True:
        cabecalho("MOVIMENTAÇÕES")
        print("  1. Registrar entrada")
        print("  2. Registrar saída")
        print("  3. Histórico de produto")
        print("  0. Voltar")
        separador()

        opcao = input_opcao("Opção", ["0", "1", "2", "3"])

        if opcao == "0":
            break

        elif opcao == "1":
            cabecalho("REGISTRAR ENTRADA")
            try:
                sku = input_texto("SKU do produto")
                produto = product_service.get_by_sku(sku)
                exibir_produto_detalhe(produto)

                assert produto.id is not None
                quantidade = input_inteiro("Quantidade a receber", minimo=1)
                motivo = input_texto("Motivo / Nota fiscal")

                result = stock_service.register_entry(
                    product_id=produto.id,
                    user_id=OPERADOR_ID,
                    quantity=quantidade,
                    reason=motivo,
                )
                exibir_resultado_movimentacao(result)

            except (ProductNotFoundError, ValidationError) as e:
                print(f"\n  ✗ {e}")

        elif opcao == "2":
            cabecalho("REGISTRAR SAÍDA")
            try:
                sku = input_texto("SKU do produto")
                produto = product_service.get_by_sku(sku)
                exibir_produto_detalhe(produto)

                assert produto.id is not None
                quantidade = input_inteiro("Quantidade a retirar", minimo=1)
                motivo = input_texto("Motivo")

                result = stock_service.register_exit(
                    product_id=produto.id,
                    user_id=OPERADOR_ID,
                    quantity=quantidade,
                    reason=motivo,
                )
                exibir_resultado_movimentacao(result)

            except (ProductNotFoundError, InsufficientStockError, ValidationError) as e:
                print(f"\n  ✗ {e}")

        elif opcao == "3":
            cabecalho("HISTÓRICO DE PRODUTO")
            try:
                sku = input_texto("SKU do produto")
                produto = product_service.get_by_sku(sku)
                assert produto.id is not None
                historico = stock_service.get_history(produto.id)
                exibir_historico(historico, produto.name)

            except ProductNotFoundError as e:
                print(f"\n  ✗ {e}")

        input("\n  [Enter para continuar]")


def menu_principal(conn: sqlite3.Connection) -> None:
    """Menu principal do sistema."""
    product_service = ProductService(conn)
    stock_service = StockService(conn)

    while True:
        cabecalho("SISTEMA DE GESTÃO DE ESTOQUE")
        print("  1. Produtos")
        print("  2. Movimentações")
        print("  0. Sair")
        separador()

        opcao = input_opcao("Opção", ["0", "1", "2"])

        if opcao == "0":
            print("\n  Até logo.\n")
            break
        elif opcao == "1":
            _menu_produtos(product_service)
        elif opcao == "2":
            _menu_movimentacoes(stock_service, product_service)