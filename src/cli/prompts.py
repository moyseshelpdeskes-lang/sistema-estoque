"""
Funções de entrada do usuário.

Responsabilidade única: solicitar, ler e converter
entradas do teclado com validação básica de formato.
"""


def input_texto(mensagem: str, obrigatorio: bool = True) -> str:
    """
    Solicita uma entrada de texto.

    Args:
        mensagem: texto exibido ao usuário.
        obrigatorio: se True, não aceita entrada vazia.

    Returns:
        Texto digitado pelo usuário, sem espaços nas bordas.
    """
    while True:
        valor = input(f"  {mensagem}: ").strip()
        if valor or not obrigatorio:
            return valor
        print("  Campo obrigatório. Tente novamente.")


def input_inteiro(mensagem: str, minimo: int = 1) -> int:
    """
    Solicita uma entrada numérica inteira.

    Args:
        mensagem: texto exibido ao usuário.
        minimo: valor mínimo aceito.

    Returns:
        Inteiro válido digitado pelo usuário.
    """
    while True:
        try:
            valor = int(input(f"  {mensagem}: ").strip())
            if valor >= minimo:
                return valor
            print(f"  Valor deve ser no mínimo {minimo}. Tente novamente.")
        except ValueError:
            print("  Digite um número inteiro válido.")


def input_float(mensagem: str, minimo: float = 0.0) -> float:
    """Solicita uma entrada numérica decimal."""
    while True:
        try:
            valor = float(input(f"  {mensagem}: ").strip().replace(",", "."))
            if valor >= minimo:
                return valor
            print(f"  Valor deve ser no mínimo {minimo}. Tente novamente.")
        except ValueError:
            print("  Digite um número válido (ex: 45.90).")


def input_opcao(mensagem: str, opcoes: list[str]) -> str:
    """
    Solicita uma escolha entre opções válidas.

    Args:
        mensagem: texto exibido ao usuário.
        opcoes: lista de valores aceitos.

    Returns:
        Opção escolhida pelo usuário.
    """
    while True:
        valor = input(f"  {mensagem}: ").strip()
        if valor in opcoes:
            return valor
        print(f"  Opção inválida. Escolha entre: {', '.join(opcoes)}")