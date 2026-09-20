# Quickstart & Validation Guide: F03 — Canvas de Estudos

**Feature Branch**: `021-canvas-estudos`  
**Date**: 2026-09-19  
**Status**: Ready for Planning / Implementation  

---

## 1. Pré-Requisitos e Ambiente de Execução

- **Python 3.13** ativo no virtualenv: `caderno-leitura-0.1/.venv/Scripts/Activate.ps1`
- **Node.js 18+** / npm no frontend: `caderno-leitura-0.1/frontend`
- **Isolamento Absoluto**: Todos os testes automatizados rodam exclusivamente contra bancos SQLite efêmeros em diretórios temporários (`tmp_path`). O banco de dados ativo (`backend/data/caderno.db`) **JAMAIS** é tocado.

---

## 2. Cenários Executáveis de Validação

### Cenário 1: Migração Alembic e Schema da Tabela `study_canvas_nodes`
- **Comando**:
  ```powershell
  cd caderno-leitura-0.1/backend
  pytest tests/test_migrations.py -k "test_alembic_upgrade"
  ```
- **Resultado Esperado**:
  - A tabela `study_canvas_nodes` é criada via migração `0007_add_study_canvas_nodes.py`.
  - Colunas `id`, `study_id`, `book_id`, `pos_x`, `pos_y`, `width`, `height`, `z_index`, `color_tag` e `updated_at` presentes com tipos e restrições corretas.
  - Chaves estrangeiras com `ON DELETE CASCADE` e restrição única `(study_id, book_id)` ativas.

### Cenário 2: API de Persistência e Batch Update de Coordenadas
- **Comando**:
  ```powershell
  cd caderno-leitura-0.1/backend
  pytest tests/test_canvas_api.py -v
  ```
- **Resultado Esperado**:
  - `GET /api/books/{id}/canvas`: Retorna lista vazia ou nós previamente salvos.
  - `PUT /api/books/{id}/canvas`: Sincroniza posições de múltiplos estudos em batch atômico.
  - `PATCH /api/studies/{id}/canvas`: Atualiza nó individual (posição ou tag de cor).
  - Tentativa de associar estudo de outro livro é rejeitada com `HTTP 400`.
  - Coordenadas não-numéricas (`NaN`/`Infinity`) são rejeitadas com `HTTP 422`.

### Cenário 3: Auto-Grid Inicial para Estudos sem Coordenadas (Q1: Opção A)
- **Comando**:
  ```powershell
  cd caderno-leitura-0.1/frontend
  npm test tests/canvas-auto-grid.test.mjs
  ```
- **Resultado Esperado**:
  - Estudos sem registro no banco são dispostos automaticamente em colunas por capítulo com espaçamento de 24px a partir de (0, 0).
  - Nenhum card é renderizado sobreposto a outro.

### Cenário 4: Viewport 2D, Pan, Zoom e Bounding Box (Fit to View)
- **Comando**:
  ```powershell
  cd caderno-leitura-0.1/frontend
  npm test tests/canvas-viewport.test.mjs
  ```
- **Resultado Esperado**:
  - Conversões entre coordenadas do mundo (*world coordinates*) e coordenadas de tela (*screen coordinates*) são exatas.
  - Zoom respeita limites rígidos entre 0.25x (25%) e 2.0x (200%).
  - Cálculo de Bounding Box e "Ajustar à Tela" calcula escala e pan centrando todos os nós com margem de segurança.
  - Viewport é restaurado com sucesso a partir de `localStorage`.

### Cenário 5: Seleção Simples, Marquee e Movimentação em Bloco
- **Comando**:
  ```powershell
  cd caderno-leitura-0.1/frontend
  npm test tests/canvas-selection.test.mjs
  ```
- **Resultado Esperado**:
  - Marquee selection detecta interseção exata de cards com a caixa delimitadora retangular.
  - Arraste de múltiplos cards selecionados aplica o mesmo delta $(\Delta x, \Delta y)$ preservando distâncias relativas.
  - O card manipulado tem seu `z_index` incrementado para o topo visual.

### Cenário 6: Validação de Build e Tipagem Estrita TypeScript
- **Comando**:
  ```powershell
  cd caderno-leitura-0.1/frontend
  npm run build
  ```
- **Resultado Esperado**:
  - `tsc -b` conclui com 0 erros de tipagem.
  - O bundle Vite compila com sucesso os novos componentes de canvas (`StudyCanvasView.vue`, `CanvasNode.vue`, `CanvasMinimap.vue`, `CanvasToolbar.vue`).

---

## 3. Evidências de Execução e Homologação (2026-09-19)

### Backend (FastAPI + SQLAlchemy + Pytest)
- **Comando**: `.venv\Scripts\pytest.exe -q`
- **Resultado**: `173 passed, 1 skipped, 2 warnings in 44.15s` (100% verde).
- **Testes dedicados do Canvas**: `backend/tests/test_canvas_api.py` (7/7 passed).

### Frontend (Node.js Test Runner + Vue 3)
- **Comando**: `node --test tests/canvas-viewport.test.mjs tests/canvas-nodes.test.mjs tests/canvas-minimap.test.mjs tests/canvas-a11y.test.mjs`
- **Resultado**: `18 passed, 0 failed, 0 skipped` (100% verde).
- **Suíte geral de regressão**: `npm test` -> `153 passed, 0 failed` (100% verde).

### Compilação de Produção
- **Comando**: `npm run build` (`vue-tsc -b && vite build`)
- **Resultado**: `✓ 1973 modules transformed. ✓ built in 2.90s` (0 erros TypeScript).

