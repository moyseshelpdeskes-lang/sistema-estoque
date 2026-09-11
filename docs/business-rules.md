# RN01 — Estoque nunca negativo. Verificação ocorre dentro de uma transação, antes de qualquer escrita.

# RN02 — Movimentação é imutável. Para corrigir um erro, cria-se uma movimentação de ajuste com motivo descritivo — nunca se edita o registro original.

# RN03 — Saldo consistente com o histórico. saldo_atual = quantidade_inicial + Σ(entradas) - Σ(saídas). Divergência indica bug ou corrupção.

# RN04 — Alerta automático. Se quantidade_atual <= estoque_mínimo após qualquer movimentação, o sistema exibe alerta imediatamente na resposta.

# RN05 — Permissões por perfil. Funcionário pode registrar movimentações mas não pode excluir produtos, criar usuários ou alterar preços.

# RN06 — SKU globalmente único. Duplicata resulta em erro de validação com mensagem clara.

# RN07 — Produto exige categoria e fornecedor. Não há produto "órfão" no sistema.

# RN08 — Usuário inativo não opera. Nem faz login, nem registra movimentações, mesmo com token ainda no prazo.