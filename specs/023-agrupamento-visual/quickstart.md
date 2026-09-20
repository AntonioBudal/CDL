# Quickstart & Validation Guide: F05 — Agrupamento Visual

**Feature Branch**: `023-agrupamento-visual`  
**Date**: 2026-09-19  
**Status**: Implemented & Fully Validated  

---

## 1. Pré-Requisitos e Ambiente de Execução

- **Python 3.13** ativo no virtualenv: `caderno-leitura-0.1/backend/.venv/Scripts/python.exe`
- **Node.js v24+** / npm no frontend: `caderno-leitura-0.1/frontend`
- **Isolamento Absoluto**: Todos os testes automatizados rodam exclusivamente contra bancos SQLite efêmeros em diretórios temporários (`tmp_path`). O banco de dados ativo (`backend/data/caderno.db`) **JAMAIS** é tocado.

---

## 2. Cenários Executáveis de Validação

### Cenário 1: Migração Alembic e Integridade de Restrições
- **Comando**:
  ```powershell
  cd caderno-leitura-0.1
  .\backend\.venv\Scripts\python.exe -m pytest backend/tests/test_study_grouping_api.py -k "test_reading_status_migration_and_constraints" -v
  ```
- **Resultado Esperado**:
  - A migração `0009_add_reading_status_and_canvas_frames` cria a coluna `reading_status` na tabela `studies` e a tabela `canvas_frames`.
  - Estudos existentes recebem o valor padrão `'rascunho'`.
  - Tentativa de atribuir valor fora de `('rascunho', 'em_estudo', 'revisado', 'concluido')` é rejeitada por `IntegrityError` / HTTP 422.
  - Tentativa de criar frame com dimensões inferiores a 100x80px é rejeitada.

### Cenário 2: Atualização Rápida de Status com Concorrência Otimista
- **Comando**:
  ```powershell
  cd caderno-leitura-0.1
  .\backend\.venv\Scripts\python.exe -m pytest backend/tests/test_study_grouping_api.py -k "test_update_study_status" -v
  ```
- **Resultado Esperado**:
  - `PATCH /api/studies/{id}/status` atualiza o status de `rascunho` para `em_estudo` e retorna `HTTP 200`.
  - Se `expected_updated_at` for anterior à última alteração, rejeita com `HTTP 409 Conflict`.

### Cenário 3: Ciclo de Vida de Molduras no Canvas 2D
- **Comando**:
  ```powershell
  cd caderno-leitura-0.1
  .\backend\.venv\Scripts\python.exe -m pytest backend/tests/test_study_grouping_api.py -k "test_canvas_frames_crud_and_cascade" -v
  ```
- **Resultado Esperado**:
  - `POST /api/books/{id}/canvas/frames` cria moldura e retorna `HTTP 201`.
  - `GET /api/books/{id}/canvas/frames` lista as molduras do livro.
  - `PATCH /api/canvas/frames/{id}` altera título, cor e dimensões.
  - `DELETE /api/canvas/frames/{id}` remove a moldura sem afetar nenhum estudo.
  - Excluir definitivamente o livro remove suas molduras em cascata (`ON DELETE CASCADE`).

### Cenário 4: Particionamento e Agrupamento Reativo no Frontend
- **Comando**:
  ```powershell
  cd caderno-leitura-0.1/frontend
  node --test tests/study-grouping.test.mjs
  ```
- **Resultado Esperado**:
  - `useStudyGrouping` agrupa por `chapter`, `status`, `category` e `date`.
  - Itens sem categoria são alocados sob "Sem Categoria".
  - Alternar entre agrupamentos preserva a integridade dos dados e o nó ativo.
  - Colapsar e expandir seções altera `isCollapsed` de forma reativa.

### Cenário 5: Contenção Espacial e Movimentação Solidária de Frames no Canvas
- **Comando**:
  ```powershell
  cd caderno-leitura-0.1/frontend
  node --test tests/canvas-frames.test.mjs
  ```
- **Resultado Esperado**:
  - Algoritmo de contenção identifica com exatidão os nós contidos no retângulo do frame.
  - Ao arrastar o frame com $(\Delta x, \Delta y)$, todos os cartões contidos recebem o mesmo deslocamento relativo.
  - Mover um cartão dentro do frame não desloca a moldura.

### Cenário 6: Acessibilidade WAI-ARIA, Sticky Headers e Alvos de Toque 44px
- **Comando**:
  ```powershell
  cd caderno-leitura-0.1/frontend
  node --test tests/study-grouping-a11y.test.mjs
  ```
- **Resultado Esperado**:
  - Seções possuem cabeçalhos semânticos e `aria-expanded`.
  - Teclas Enter e Espaço colapsam/expandem grupos.
  - Cabeçalhos móveis utilizam `position: sticky; top: 0`.
  - Todos os botões e seletores cumprem a área mínima de 44x44px.

---

## 3. Registro de Evidências da Implementação

### Validação do Backend (Python 3.13 / Pytest)
- **Comando executado**: `.\backend\.venv\Scripts\python.exe -m pytest backend/tests`
- **Resultado**:
  - **188 testes aprovados**, 1 skipped planejado (Windows symlink), **0 falhas** em 46.43s.
  - `test_study_grouping_api.py`: 6/6 testes aprovados (migração, restrições, concorrência otimista 409, CRUD de molduras e cascata).
  - `test_database.py`: 9/9 testes aprovados (verificação estrita de paridade entre modelos SQLAlchemy e migrações Alembic via `alembic.command.check`).
  - **Banco de produção preservado**: Isolamento total confirmado em `tmp_path`, nenhum dado de `backend/data/caderno.db` foi acessado ou modificado.

### Validação do Frontend (Node v24 / Vue 3 / Vite)
- **Comando executado**: `npm test` em `caderno-leitura-0.1/frontend`
- **Resultado**:
  - **178 testes unitários aprovados**, **0 falhas** em 5.19s.
  - `study-grouping.test.mjs`: 7/7 testes aprovados (particionamento por capítulo, categoria, data e status).
  - `canvas-frames.test.mjs`: 6/6 testes aprovados (algoritmo de contenção retangular, suporte a pos_x/x, arrasto solidário e projeção reversível).
  - `study-grouping-a11y.test.mjs`: 3/3 testes aprovados (cabeçalhos aderentes, atributos WAI-ARIA e alvos táteis mínimos de 44x44px).

### Compilação de Produção Vite
- **Comando executado**: `npm run build` (`vue-tsc -b && vite build`)
- **Resultado**:
  - **0 erros de tipagem estrita** em TypeScript.
  - Bundle gerado em `dist/` com sucesso em 2.75s (`dist/assets/index-DtlAIQY6.js` e `dist/assets/index--O_AJacm.css`).
