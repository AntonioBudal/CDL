---
trigger: always_on
description: Regras e âncora de contexto para o Caderno de Leitura
---

# Caderno de Leitura — Regras do Workspace

Você está atuando no projeto **Caderno de Leitura**, um sistema pessoal de caderno de leitura e estudos construído em FastAPI (Python 3.13), Vue 3 (TypeScript/Vite) e SQLite local.

## Referências Principais
- A raiz real da aplicação é `caderno-leitura-0.1/`.
- Leia [AGENTS.md](caderno-leitura-0.1/AGENTS.md) para os limites de conduta e segurança.
- Documentos de contexto do projeto estão em `docs/contexto/` (e `caderno-leitura-0.1/docs/contexto/`):
  - `PROJETO.md`: Arquitetura, fluxo de produto e decisões técnicas.
  - `ROADMAP-0.5.md`: Requisitos, arquitetura e critérios de aceite das features F01–F10.
  - `AMBIENTE-E-VALIDACAO.md`: Instruções de execução, build e testes no Windows.
  - `FLUXO-SPECKIT.md`: Guia de trabalho com Spec Kit e Antigravity.
  - `CONVENCAO-GIT.md`: Guia de versionamento Git (1 Feature = 1 Commit a partir da 0.5).
  - `RETOMADA.md`: Histórico de sessões anteriores e próximos passos imediatos.
  - `AUDITORIA-INICIAL.md`: Relatório de transição e diagnóstico da versão 0.3.

## Regras Invioláveis
1. **Privacidade Absoluta:** Jamais leia, registre, resuma ou envie textos do acervo do usuário, anotações ou dados de `backend/data/caderno.db` para o chat.
2. **Estado das Features:** Todas as features F01 a F10 da versão 0.5 estão estritamente **NÃO INICIADAS**. Nenhum código experimental ou rascunho anterior altera o status de qualquer entrega.
3. **Isolamento de Testes:** Testes nunca tocam o banco de dados de produção. Use sempre `tmp_path` e portas efêmeras.
4. **Governança:** Alterações estruturais no código só ocorrem após ciclo de especificação e planejamento delimitado via Spec Kit (`agy`).
5. **Cuidado com o Banco:** Backups consistentes (via SQLite Backup API) são obrigatórios antes de qualquer migração ou alteração no schema.
