"""
Funções de formatação de saída para o terminal.

Responsabilidade única: transformar objetos do domínio
em texto legível para exibição no terminal.
"""

from models.product import Product
from models.stock_movement import StockMovement
from services.stock_service import MovementResult

SEPARADOR = "─" * 56
SEPARADOR_DUPLO = "═" * 56


def cabecalho(titulo: str) -> None:
    """Exibe um cabeçalho formatado."""
    print(f"\n{SEPARADOR_DUPLO}")
    print(f"  {titulo}")
    print(SEPARADOR_DUPLO)


def separador() -> None:
    print(SEPARADOR)


def produto_linha(produto: Product) -> str:
    """Formata um produto em uma linha resumida."""
    alerta = " ⚠ CRÍTICO" if produto.is_below_minimum else ""
    return (
        f"  {produto.sku:<12} {produto.name:<30} "
        f"Qtd: {produto.quantity:>5}  "
        f"Mín: {produto.minimum_stock:>4}{alerta}"
    )


def exibir_produto_detalhe(produto: Product) -> None:
    """Exibe os detalhes completos de um produto."""
    separador()
    print(f"  SKU:            {produto.sku}")
    print(f"  Nome:           {produto.name}")
    print(f"  Descrição:      {produto.description or '—'}")
    print(f"  Preço unitário: R$ {produto.unit_price:.2f}")
    print(f"  Quantidade:     {produto.quantity}")
    print(f"  Estoque mínimo: {produto.minimum_stock}")
    status = "✓ Ativo" if produto.is_active else "✗ Inativo"
    print(f"  Status:         {status}")
    if produto.is_below_minimum:
        print(f"\n  ⚠  ALERTA: estoque abaixo do mínimo!")
    separador()


def exibir_lista_produtos(produtos: list[Product]) -> None:
    """Exibe uma lista de produtos formatada."""
    if not produtos:
        print("\n  Nenhum produto encontrado.")
        return

    separador()
    print(f"  {'SKU':<12} {'Nome':<30} {'Qtd':>8}  {'Mín':>7}")
    separador()
    for produto in produtos:
        print(produto_linha(produto))
    separador()
    print(f"  Total: {len(produtos)} produto(s)")


def exibir_resultado_movimentacao(result: MovementResult) -> None:
    """Exibe o resultado de uma movimentação de estoque."""
    tipo = "ENTRADA" if result.movement.type == "entry" else "SAÍDA"
    separador()
    print(f"  ✓ {tipo} registrada com sucesso")
    print(f"  Produto:        {result.product.name}")
    print(f"  Quantidade:     {result.movement.quantity}")
    print(f"  Saldo anterior: {result.product.quantity}")
    print(f"  Saldo atual:    {result.movement.resulting_balance}")
    print(f"  Motivo:         {result.movement.reason}")
    if result.alert:
        print(f"\n  ⚠  ALERTA: estoque crítico!")
        print(f"  Atual: {result.movement.resulting_balance}  "
              f"Mínimo: {result.product.minimum_stock}")
    separador()


def exibir_historico(movimentacoes: list[StockMovement], nome_produto: str) -> None:
    """Exibe o histórico de movimentações de um produto."""
    if not movimentacoes:
        print("\n  Nenhuma movimentação registrada.")
        return

    separador()
    print(f"  Histórico: {nome_produto}")
    separador()
    for mov in movimentacoes:
        tipo = "ENT" if mov.type == "entry" else "SAI"
        data = mov.created_at.strftime("%d/%m/%Y %H:%M")
        print(
            f"  [{tipo}] {data}  "
            f"Qtd: {mov.quantity:>5}  "
            f"Saldo: {mov.resulting_balance:>6}  "
            f"{mov.reason}"
        )
    separador()
    print(f"  Total: {len(movimentacoes)} movimentação(ões)")