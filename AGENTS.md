# Regras para Agentes — Caderno de Leitura

Este arquivo define regras estritas para qualquer agente de IA que atue neste repositório.

## 1. Preservação de Dados e Privacidade
- **NUNCA** leia, exiba, resuma ou envie textos do acervo do usuário, notas pessoais, respostas importadas ou conteúdo do banco de dados para o chat ou para serviços externos.
- O banco ativo local (`backend/data/caderno.db`), snapshots, backups (`.db`, `.zip`) e dados pessoais são estritamente privados. Nunca os versione no Git nem os compartilhe.
- Para testes e demonstrações, use exclusivamente dados fictícios (ex.: "Livro de Teste", "Capítulo 1", amostras sintéticas).

## 2. Integridade do Banco e Operações no Ambiente
- **NÃO altere** o banco de dados ativo diretamente (`backend/data/caderno.db`) nem rode migrações sem solicitação explícita do usuário e sem um backup consistente previamente verificado.
- Todo teste automatizado ou script de validação DEVE utilizar bancos descartáveis em diretórios temporários (`tmp_path`).
- Scripts e instaladores nunca devem ser executados sem antes auditar o código e garantir o isolamento total dos dados de produção.

## 3. Estado do Roadmap e Versão 0.5
- **REGRA DE ESTADO:** Todas as dez features (F01 a F10) da versão 0.5 estão estritamente **NÃO INICIADAS**.
- A presença de patches, rascunhos, código preliminar ou arquivos de contexto NÃO altera o status de nenhuma feature.
- Nenhuma feature pode ser marcada como iniciada ou concluída sem a execução delimitada e autorizada pelo usuário através do ciclo Spec Kit.

## 4. Fluxo de Trabalho (Spec-Driven Development)
- O fluxo oficial de desenvolvimento utiliza o GitHub Spec Kit integrado ao Antigravity (`agy`).
- Siga a sequência delimitada: Especificação (`speckit.specify`) → Esclarecimento (`speckit.clarify`) → Plano Técnico (`speckit.plan`) → Tarefas (`speckit.tasks`) → Análise (`speckit.analyze`) → Implementação (`speckit.implement`).
- Não implemente funcionalidades sem planejamento e aprovação prévia de cada fatia.
## 5. Arquitetura e Restrições de Plataforma
- **Stack:** Python 3.13 (FastAPI, SQLAlchemy 2, Alembic, Uvicorn), Vue 3 (TypeScript, Vite, Tailwind/CSS), SQLite local (modo WAL).
- **Ambiente:** Windows local (PowerShell, caminhos com espaços e acentos, preservação de quebras de linha CRLF/LF).
- O servidor roda em processo único local através de `iniciar.py`, atendendo tanto PC quanto dispositivos móveis em rede privada/Tailscale.

## 6. Convenção de Versionamento Git
- **Até a versão 0.4:** O histórico consolida 1 commit por marco de Roadmap (0.1, 0.2, 0.3 e 0.4).
- **A partir da versão 0.5:** Cada feature implementada através do ciclo Spec Kit DEVE gerar seu próprio commit individual e atômico (**1 Feature = 1 Commit**).
- O commit da feature só deve ser criado após a validação completa das suítes de testes (`npm test`, `pytest`, `npm run build`).
- As mensagens de commit devem ser sempre em português, curtas, simples e descritivas (ex.: `feature — base multiusuário`).
- Para detalhes históricos e diretrizes, consulte [docs/HISTORICO-ROADMAPS.md](docs/HISTORICO-ROADMAPS.md).
