# Implementation Plan: F0.11.03 — Importar Destaques do Kindle e do Kobo

**Spec**: [spec.md](spec.md) | **Date**: 2026-11-09 | **Status**: Executado em 2026-11-09

## Technical Context

FastAPI (multipart já usado nas capas e na digitalização) + SQLAlchemy 2, Vue 3. **Sem migração**, sem dependência
nova (o `sqlite3` da biblioteca padrão lê o banco do Kobo). Testes com arquivos sintéticos gerados no próprio teste.

## Constitution Check

| Regra | Situação |
|---|---|
| Dados do usuário nunca lidos | OK: os testes geram `My Clippings.txt` e `KoboReader.sqlite` fictícios; nenhum arquivo real é lido nesta conversa |
| Banco ativo | Não é tocado; sem migração |
| Arquivo enviado | Lido em memória (Kindle) ou cópia temporária somente leitura (Kobo), apagada no `finally` |
| Lote | 3ª feature do lote 1 do 0.11 |

## Arquivos e mudanças

| Arquivo | Mudança |
|---|---|
| `backend/app/services/ereader_import/__init__.py`, `kindle.py`, `kobo.py` (novos) | parsers puros e detecção de formato |
| `backend/app/services/ereader_import/service.py` (novo) | prévia (agrupar, sugerir livro com `normalize_title_key`, contar duplicatas) e importação em lote |
| `backend/app/schemas/ereader_import.py` (novo) | prévia, escolhas e resultado |
| `backend/app/routers/inbox.py` | `POST /ereader/preview` e `POST /ereader/import` |
| `frontend/src/types.ts`, `services/api.ts` | tipos e chamadas multipart |
| `frontend/src/views/EreaderImportView.vue` (novo), `router/index.ts` | tela `/inbox/importar-leitor` |
| `frontend/src/views/InboxView.vue` | botão "Importar do Kindle ou Kobo" |
| testes | `backend/tests/test_ereader_import.py`, `frontend/tests/feature-105-importar-kindle-kobo.test.mjs` |
| docs | `RETOMADA.md`, `HANDOFF.md` |

## Decisões

1. **Destino = Mesa de Triagem**: destaque de leitor digital é matéria-prima; a bandeja do capítulo (F0.11.02) é onde
   ele vira estudo.
2. **Duas chamadas sem estado no servidor**: a prévia não grava nada nem guarda o arquivo; a importação recebe o arquivo
   de novo com as escolhas. Mais simples e sem arquivos esquecidos no disco.
3. **Duplicata por conteúdo + localização** em vez de coluna nova: evita migração; o custo é uma consulta por livro.
4. **Casar livros com as funções da F0.10.07**: mesma regra de título e sobrenome usada em "Em comum".
5. **Kobo pelo SQLite do aparelho**: é o único lugar onde o Kobo guarda destaques sem exportação oficial; abrir em modo
   somente leitura (`mode=ro`) a partir de cópia temporária.

## Riscos

| Risco | Mitigação |
|---|---|
| Variações do cabeçalho do Kindle por idioma e firmware | Regex tolerante (inglês e português), testes com várias formas; entrada não reconhecida é contada e relatada, não derruba o arquivo |
| SQLite do Kobo malicioso ou corrompido | Somente leitura, `quick_check` antes, só `SELECT` nas tabelas esperadas, limite de tamanho e de linhas |
| Arquivo grande demorando | Agregação por livro, inserção em lote numa transação |
