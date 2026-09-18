# Sistema de Gestão de Estoque

Sistema para controle de estoque desenvolvido para uma empresa de
logística e distribuição industrial na Grande Vitória, ES.

> ⚠️ Projeto em desenvolvimento ativo.

## O problema

Controle de estoque em planilhas gera perdas, pedidos duplicados e
falta de rastreabilidade. Este sistema substitui as planilhas por
uma plataforma com controle em tempo real, auditoria completa e
alertas automáticos de estoque crítico.

## Status das fases

| Fase | Descrição | Status |
|------|-----------|--------|
| 0 | Planejamento e setup | 🔲 Em andamento |
| 1 | Modelos do domínio | 🔲 Não iniciado |
| 2 | Banco de dados e repositórios | 🔲 Não iniciado |
| 3 | Serviços e regras de negócio | 🔲 Não iniciado |
| 4 | Interface CLI | 🔲 Não iniciado |
| 5 | Testes completos com pytest | 🔲 Não iniciado |
| 6 | API REST com FastAPI | 🔲 Não iniciado |
| 7 | Migração para PostgreSQL | 🔲 Não iniciado |
| 8 | Docker | 🔲 Não iniciado |
| 9 | CI/CD | 🔲 Não iniciado |
| 10 | Deploy e observabilidade | 🔲 Não iniciado |

## Documentação

- [Requisitos](docs/requirements.md)
- [Regras de negócio](docs/business-rules.md)
- [Modelo de dados](docs/database.md)
- [Decisões de arquitetura](docs/decisions/)

## Utilização

### API REST
```bash
python run_api.py
# Acesse http://localhost:8000/docs
```

### CLI (linha de comando)
```bash
python src/main.py
```

> **Limitação conhecida da CLI:** o ID do operador está fixo em `OPERADOR_ID = 1`.
> A CLI não possui tela de login — assume que o usuário com ID 1 está operando.
> A autenticação completa está disponível apenas via API REST (Fase 6).