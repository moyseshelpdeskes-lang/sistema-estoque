# Requisitos do Sistema

## Requisitos Funcionais

### RF01 — Cadastro de produto
Cadastrar produto com: nome, SKU único, descrição, preço unitário, quantidade inicial, estoque mínimo, categoria e fornecedor.

### RF02 — Listagem de produtos
Listar produtos com quantidade atual e sinalização visual para itens abaixo do estoque mínimo.

### RF03 — Busca de produtos
Buscar produto por nome, SKU, categoria ou fornecedor.

### RF04 — Atualização de produto
Atualizar atributos cadastrais de um produto. Histórico de movimentações é sempre imutável.

### RF05 — Desativação de produto
Desativar produto (soft delete). Produto com movimentações não pode ser excluído fisicamente.

### RF06 — Registro de entrada
Registrar entrada de estoque: produto, quantidade, motivo e responsável.

### RF07 — Registro de saída
Registrar saída de estoque: produto, quantidade, motivo e responsável.

### RF08 — Prevenção de estoque negativo
Saída só processada se `quantidade_disponível >= quantidade_solicitada`.

### RF09 — Imutabilidade de movimentações
Registrar cada movimentação de forma imutável: produto, tipo, quantidade, saldo resultante, data/hora, usuário e motivo.

### RF10 — Alertas automáticos
Listar produtos com `quantidade_atual <= estoque_mínimo` após cada movimentação.

### RF11 — Relatório de movimentações
Filtrável por produto, período e tipo. Exportável como JSON inicialmente.

### RF12 — Gerenciamento de usuários
Criar, editar e desativar usuários com perfis `admin` e `employee`.

---

## Requisitos Não Funcionais

| ID | Categoria | Critério |
|---|---|---|
| RNF01 | Segurança | Senhas com `bcrypt`, custo ≥ 12. Nunca plain text. |
| RNF02 | Segurança | JWT com expiração ≤ 8h |
| RNF03 | Desempenho | Listagem de 1.000 produtos em < 500ms |
| RNF04 | Rastreabilidade | Toda movimentação registra usuário + data/hora + motivo |
| RNF05 | Manutenibilidade | Cada módulo com propósito claramente definido |
| RNF06 | Testabilidade | ≥ 80% de cobertura nos métodos da camada Service |
| RNF07 | Portabilidade | `docker compose up` sobe tudo em qualquer OS |
| RNF08 | Integridade | Sem `UPDATE` ou `DELETE` em `stock_movements` |
| RNF09 | Observabilidade | Logs estruturados com níveis INFO/WARNING/ERROR |
| RNF10 | Disponibilidade | CLI sempre funcional sem dependência de rede externa |