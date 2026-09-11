# ADR-001: Escolha do banco de dados inicial

**Data:** 2026-09-08
**Status:** Aceito

**Contexto:**
Sistema novo, escopo educacional, ambiente Windows sem Docker ainda,
estudante com experiência em Python mas sem experiência prévia com SQL.

**Opções avaliadas:**
- SQLite: embutido, arquivo único, zero configuração
- PostgreSQL: produção real, requer servidor separado
- MySQL: popular mas sem vantagem sobre PostgreSQL neste contexto

**Decisão:** SQLite nas Fases 0–6.

**Consequências positivas:**
- Foco no aprendizado de SQL sem overhead operacional
- Arquivo .db inspecionável com DB Browser for SQLite
- Sem dependência de servidor externo

**Consequências negativas:**
- Sem suporte real a concorrência
- Não representa ambiente de produção
- Migração para PostgreSQL na Fase 7 custará refatoração do Repository