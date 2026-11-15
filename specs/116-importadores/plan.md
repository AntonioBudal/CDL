# Implementation Plan: F0.12.03 — Importadores

**Spec**: [spec.md](spec.md) | **Date**: 2026-11-15 | **Status**: Executado em 2026-11-15

## Technical Context

FastAPI + SQLAlchemy 2, Vue 3 + TS. **Sem migração** (usa campos de livro e capturas que já existem). Leitura de CSV
com o módulo `csv` da biblioteca padrão; ZIP com `zipfile` em memória. Testes em `tmp_path` e `node:test`.

## Constitution Check

| Regra | Situação |
|---|---|
| Dados do usuário nunca lidos | OK: arquivos de teste fictícios, montados nos próprios testes |
| Banco ativo | Não é tocado; sem migração |
| Segurança | Prévia sem gravar; arquivo não fica no servidor; ZIP só na memória, com limites contra arquivo malicioso |
| Lote | 3ª feature do 0.12 |

## Arquivos e mudanças

| Arquivo | Mudança |
|---|---|
| `backend/app/services/library_import/__init__.py` (leitores puros dos 3 serviços) e `service.py` (novos) | detecção, leitores, prévia, importação |
| `backend/app/schemas/library_import.py`, `routers/library_import.py` (novos; registrado antes do roteador de livros) | API de prévia e importação |
| `backend/app/services/ereader_import/{readwise_csv,omnivore}.py` (novos), `__init__.py`, `service.py`, `schemas/ereader_import.py` | destaques do Readwise e do Omnivore |
| `frontend/src/views/LibraryImportView.vue` (novo), `router/index.ts`, `views/BooksView.vue` | tela e entrada |
| `frontend/src/views/EreaderImportView.vue` | textos e `accept` com `.csv` e `.zip` |
| `frontend/src/services/api.ts`, `types.ts` | chamadas e tipos |
| `specs/076-…`, `specs/081-…` | rota `library-import` |
| `VERSION`, `package.json`, `package-lock.json`, `data/versionHistory.ts` | `0.12.0-alpha.3` |
| testes | `test_library_import.py`, `test_ereader_readwise_omnivore.py`, `feature-116-importadores.test.mjs` |
| docs | `RETOMADA.md`, `HANDOFF.md`, `ROADMAP-0.12.md` |

## Decisões

1. **Dois caminhos, uma feature:** biblioteca vira livros; destaques viram capturas pela tela existente (reuso da
   prévia, escolha de livro e deduplicação da F0.11.03).
2. **Detecção pelo cabeçalho**, não pelo nome do arquivo: os serviços mudam o nome; as colunas são estáveis.
3. **Leitores tolerantes:** nomes de coluna sem diferença de maiúsculas, colunas extras ignoradas, BOM, `;` e CRLF.
4. **Sem estrelas:** o Leitorum não tem nota; criar o campo seria outra feature.
5. **Readwise sem confirmação:** leitor por nome de coluna + teste do usuário com um arquivo real depois da entrega.

## Riscos

| Risco | Mitigação |
|---|---|
| Formato real diferente do pesquisado | Prévia mostra o que foi lido antes de gravar; mensagem clara se faltar coluna obrigatória |
| ZIP malicioso | Limites de tamanho, de arquivos e de descompactado; leitura só de nomes esperados, nada no disco |
| Duplicar livros já existentes | Casamento por ISBN e por título/autor; padrão "pular" para os já existentes |
