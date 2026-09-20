# Quickstart & Validation Guide: F08 — Busca Global Contextual

**Feature Branch**: `025-busca-global-contextual`  
**Date**: 2026-09-19  
**Status**: Validated & Implemented (100% dos testes passando, build Vite aprovado)  
**Specification**: [spec.md](./spec.md)  
**Contracts**: [contracts/search-api.md](./contracts/search-api.md)  
**Data Model**: [data-model.md](./data-model.md)  

---

## 1. Pré-Requisitos e Ambiente

- **Python 3.13** no virtualenv: `caderno-leitura-0.1/backend/.venv/Scripts/python.exe`
- **Node.js v20+** e npm no frontend: `caderno-leitura-0.1/frontend`
- **Isolamento Absoluto**: Todos os testes operam contra bancos SQLite descartáveis em `tmp_path`. O banco de produção `backend/data/caderno.db` **NUNCA** é acessado por testes.

---

## 2. Cenários Executáveis de Validação

### Cenário 1: Busca Transversal com Insensibilidade a Acentos e Snippets Realçados
- **Comando**:
  ```powershell
  cd caderno-leitura-0.1
  .\backend\.venv\Scripts\python.exe -m pytest backend/tests/test_search_api.py -k "test_search_accent_insensitive_and_snippets" -v
  ```
- **Resultado Esperado**:
  - Consulta por "logica" localiza estudo contendo "lógica" no título ou notas.
  - O snippet retornado contém o fragmento ao redor do match sanitizado com `<mark class="search-highlight">`.
  - `matched_field` identifica corretamente onde a correspondência ocorreu.

### Cenário 2: Combinação de Múltiplos Termos (Modo AND e Sugestão OR)
- **Comando**:
  ```powershell
  cd caderno-leitura-0.1
  .\backend\.venv\Scripts\python.exe -m pytest backend/tests/test_search_api.py -k "test_search_multi_terms_and_or_modes" -v
  ```
- **Resultado Esperado**:
  - Em modo `and`, apenas estudos contendo todas as palavras são retornados.
  - Quando a busca `and` não encontra correspondências, a flag `suggest_or` é retornada como `true` se houver matches parciais.
  - Em modo `or`, estudos com pelo menos um dos termos são retornados.

### Cenário 3: Exclusão Rigorosa de Itens na Lixeira (Soft Delete)
- **Comando**:
  ```powershell
  cd caderno-leitura-0.1
  .\backend\.venv\Scripts\python.exe -m pytest backend/tests/test_search_api.py -k "test_search_ignores_soft_deleted_items" -v
  ```
- **Resultado Esperado**:
  - Estudos com `deleted_at IS NOT NULL` não aparecem nos resultados.
  - Estudos pertencentes a livros com `deleted_at IS NOT NULL` também são omitidos integralmente.

### Cenário 4: Persistência e Limpeza do Histórico de Buscas
- **Comando**:
  ```powershell
  cd caderno-leitura-0.1
  .\backend\.venv\Scripts\python.exe -m pytest backend/tests/test_search_api.py -k "test_search_history_lifecycle" -v
  ```
- **Resultado Esperado**:
  - `GET /api/search/history` retorna os termos recentes ordenados por `updated_at DESC`.
  - `DELETE /api/search/history/{id}` remove um termo específico.
  - `DELETE /api/search/history` limpa todo o histórico.

### Cenário 5: Modal de Busca, Atalho de Teclado e Navegação em 1 Clique (Frontend)
- **Comando**:
  ```powershell
  cd caderno-leitura-0.1/frontend
  node --test tests/global-search.test.mjs
  ```
- **Resultado Esperado**:
  - O componente `GlobalSearchModal` abre ao acionar o atalho de teclado (`Ctrl+K` ou `/`) ou ao clicar no botão da barra superior.
  - A digitação com debounce dispara a requisição e exibe os resultados com `<mark>`.
  - O clique em um resultado fecha o modal e gera a rota de navegação direta `/books/{book_id}?study={study_id}`.

### Cenário 6: Ergonomia Móvel, Acessibilidade e Contenção de Overflow
- **Comando**:
  ```powershell
  cd caderno-leitura-0.1/frontend
  node --test tests/global-search-a11y.test.mjs
  ```
- **Resultado Esperado**:
  - Em viewport estreita (<768px), o modal expande em tela cheia com alvos táteis mínimos de 44x44px.
  - Contenção rigorosa contra overflow horizontal (`overflow-x: hidden`).
  - Navegação por teclado funcional com captura de foco e descarte via tecla Esc.

---

## 3. Evidências de Homologação e Conclusão

Todas as suítes de testes foram executadas e aprovadas com sucesso, sem tocar no banco de dados ativo:

1. **Backend Tests (Pytest)**:
   - **Comando**: `.\backend\.venv\Scripts\python.exe -m pytest backend/tests/`
   - **Resultado**: `199 passed, 1 skipped in 18.78s` (0 failures).
   - **Testes dedicados de busca**: `backend/tests/test_search_api.py` (6/6 aprovados).
   - **Paridade Alembic/Modelos**: `test_migration_matches_models` aprovado.

2. **Frontend Tests (Node Test Runner)**:
   - **Comando**: `npm test`
   - **Resultado**: `201 passed, 0 failed` (0 failures).
   - **Testes dedicados de busca global**: `tests/global-search.test.mjs` (6/6 aprovados).
   - **Testes de acessibilidade/teclado/móvel**: `tests/global-search-a11y.test.mjs` (5/5 aprovados).

3. **Frontend Production Build**:
   - **Comando**: `npm run build` (`vue-tsc -b && vite build`)
   - **Resultado**: Compilação TypeScript limpa (0 erros) e build de assets gerado com sucesso.

