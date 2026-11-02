# Implementation Plan: F0.10.02.5 — Correções Visuais e Gerenciamento de Capítulos

**Spec**: [spec.md](spec.md) | **Date**: 2026-11-02

## Arquivos e mudanças

| Arquivo | Mudança |
|---|---|
| `backend/app/routers/chapters.py` | `DELETE /{chapter_id}`: dono do livro; conta estudos do capítulo (com `deleted_at` ou não) e responde 409 se houver; senão apaga, renumera as posições (0..n-1) e devolve a lista |
| `frontend/src/services/api.ts` | `deleteChapter(bookId, chapterId)` → `Chapter[]` |
| `frontend/src/appearance-advanced.css` | `.quiet`: `--button-fg: var(--quiet-fg, var(--color-text))`; no `:disabled`, `color: var(--quiet-fg-disabled, var(--color-muted))` |
| `frontend/src/views/BookView.vue` | (1) regra móvel da capa em `.book-cover-container`; (2) `.chapter-pill.selected .pill-tool-btn` define `--quiet-fg`, `--quiet-fg-disabled` e `--quiet-border`; (3) botão "Excluir capítulo" nas ferramentas; (4) menu "Gerenciar capítulo" ao lado do seletor móvel e campo de renomear abaixo dele; (5) estado e funções `requestDeleteChapter`, `confirmDeleteChapter`, com o `TrashConfirmModal` já importado |
| `backend/tests/test_chapter_delete.py` (novo) | os 5 casos do SC-001 |
| `frontend/tests/feature-094-capa-capitulos.test.mjs` (novo) | SC-002 |
| `frontend/tests/feature-092-header-leve.test.mjs` | a asserção de `--button-fg` passa a aceitar o gancho `--quiet-fg` |
| `caderno-leitura-0.1/docs/contexto/RETOMADA.md` | registro |

## Decisões

1. **Excluir capítulo com estudos é recusado**, não cascateado. A chave estrangeira `studies.chapter_id` já é
   `ondelete="RESTRICT"`, e estudos na lixeira guardam o capítulo para poderem ser restaurados. A interface avisa
   antes de abrir a confirmação quando o capítulo selecionado tem estudos ativos; a API cobre o resto (lixeira) com
   409.
2. **Cor das ferramentas por gancho**, não por regra nova de especificidade: a pílula selecionada já define
   `--color-selected-text` para o próprio texto, e as ferramentas passam a herdá-la pela variante.
3. **Celular reaproveita as funções do desktop** (`moveChapter`, `startEditChapter`, `saveChapter`, exclusão);
   muda só a apresentação: `DropdownMenu` (componente já usado em "Ações do livro") e um campo de renomear abaixo
   do seletor.
4. **Escopo travado**: nenhuma mudança na faixa de pílulas além do botão novo e das cores; nenhuma reorganização
   do cabeçalho do livro.
