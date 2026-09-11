# Regras de Negócio

As regras de negócio definem **como e quando** o sistema pode executar
as operações. Diferem dos requisitos funcionais, que definem **o que**
o sistema faz.

## RN01 — Estoque nunca negativo
Verificação ocorre dentro de uma transação, antes de qualquer escrita.
Se `quantidade_disponível < quantidade_solicitada`, a operação é rejeitada
com erro descritivo.

## RN02 — Movimentação é imutável
Para corrigir um erro, cria-se uma movimentação de ajuste com motivo
descritivo — nunca se edita o registro original.

## RN03 — Saldo consistente com o histórico
`saldo_atual = quantidade_inicial + Σ(entradas) - Σ(saídas)`
Divergência entre saldo atual e histórico indica bug ou corrupção de dados.

## RN04 — Alerta automático de estoque crítico
Se `quantidade_atual <= estoque_mínimo` após qualquer movimentação,
o sistema exibe alerta imediatamente junto à confirmação da operação.

## RN05 — Permissões por perfil
Funcionário pode registrar movimentações mas não pode excluir produtos,
criar usuários ou alterar preços. Essas operações são restritas a `admin`.

## RN06 — SKU globalmente único
Duplicata resulta em erro de validação com mensagem clara antes de
qualquer escrita no banco.

## RN07 — Produto exige categoria e fornecedor
Não há produto "órfão" no sistema. Categoria e fornecedor são obrigatórios
no cadastro.

## RN08 — Usuário inativo não opera
Usuário com `is_active = False` não faz login nem registra movimentações,
mesmo que possua token JWT ainda dentro do prazo de expiração.