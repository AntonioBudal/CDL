# Implementation Plan: F0.12.05 — Exportar o livro em JSON Canvas

**Spec**: [spec.md](spec.md) | **Date**: 2026-11-15 | **Status**: Concluída

## Technical Context

FastAPI + SQLAlchemy 2, Vue 3. **Sem migração** (lê as tabelas do quadro que já existem). JSON com `json`. Testes em
`tmp_path` e `node:test`.

## Constitution Check

| Regra | Situação |
|---|---|
| Dados do usuário nunca lidos | OK: só código e dados fictícios |
| Banco ativo | Não é tocado |
| Privacidade | Arquivo baixado pelo próprio dono; só título e resumo (sem notas nem fichamento) |
| Decisão da 0.9 | Mantida: nada de quadro na tela |
| Lote | 5ª feature do 0.12 (fecha o lote com as suítes completas) |

## Arquivos e mudanças

| Arquivo | Mudança |
|---|---|
| `backend/app/services/json_canvas_export.py` (novo) | montagem do JSON Canvas, layout automático, cores, alturas |
| `backend/app/routers/canvas.py` | `GET /books/{id}/canvas/export` |
| `frontend/src/components/ExportModal.vue`, `services/api.ts` | formato "JSON Canvas (Obsidian)" no escopo livro |
| `VERSION`, `package.json`, `package-lock.json`, `data/versionHistory.ts` | `0.12.0-alpha.5` |
| testes | `test_json_canvas_export.py`, `feature-118-json-canvas.test.mjs` |
| docs | `ROADMAP-0.12.md` (item redefinido), `RETOMADA.md`, `HANDOFF.md` |

## Decisões

1. **Só exportação** (usuário, 2026-11-15): entrega o formato aberto sem reabrir a decisão da 0.9.
2. **Nó de texto, não de arquivo**: um `.canvas` só, que abre em qualquer leitor do formato, sem montar cofre.
3. **Posições antigas primeiro**: quem arrumou o quadro antes não perde o arranjo; o resto entra por capítulo.
4. **Ids estáveis por tipo**: exportar de novo gera os mesmos ids (o Obsidian mantém referências).

## Riscos

| Risco | Mitigação |
|---|---|
| Sobreposição no layout automático | Colunas com largura fixa e alturas somadas; teste de não sobreposição |
| Aresta para nó inexistente | Só relações com os dois estudos no livro e fora da lixeira; teste |
