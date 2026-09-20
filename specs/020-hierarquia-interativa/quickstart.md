# Quickstart & Validation Guide: F02 — Hierarquia Interativa

**Feature Branch**: `020-hierarquia-interativa`  
**Date**: 2026-09-19  
**Status**: Validated & Completed  
**Evidence**: 166 testes backend (pytest) e 135 testes frontend (node:test) 100% verdes. Build de produção Vite aprovado.  

---

## 1. Pré-Requisitos e Ambiente de Execução

- **Python 3.13** ativo no virtualenv: `.venv\Scripts\Activate.ps1`
- **Node.js 18+** / npm no frontend: `caderno-leitura-0.1/frontend`
- **Isolamento Absoluto**: Todos os testes e validações automatizadas rodam contra bancos SQLite efêmeros em diretórios temporários (`tmp_path`). O banco de dados ativo (`backend/data/caderno.db`) **JAMAIS** é tocado.

---

## 2. Cenários Executáveis de Validação

### Cenário 1: Migração e Schema Relacional
- **Comando**:
  ```powershell
  cd caderno-leitura-0.1/backend
  pytest tests/test_migrations.py -k "test_alembic_upgrade"
  ```
- **Resultado Esperado**: As colunas `parent_study_id` e `position` existem na tabela `studies`, índices `ix_studies_parent_study_id` e `ix_studies_chapter_parent_position` criados com sucesso.

### Cenário 2: Validação Algorítmica contra Ciclos (DAG) e Limite de Profundidade
- **Comando**:
  ```powershell
  cd caderno-leitura-0.1/backend
  pytest tests/test_study_hierarchy.py -v
  ```
- **Resultado Esperado**:
  - Tentativa de atribuir nó a si mesmo retorna `HTTP 422`.
  - Tentativa de atribuir nó a seu descendente (filho ou neto) retorna `HTTP 422`.
  - Tentativa de aninhar além de 5 níveis de profundidade retorna `HTTP 422`.
  - Tentativa de mover nó com concorrência desatualizada retorna `HTTP 409`.

### Cenário 3: Cascata Lógica na Lixeira (Soft Delete)
- **Comando**:
  ```powershell
  cd caderno-leitura-0.1/backend
  pytest tests/test_trash.py -k "test_study_hierarchy_cascade"
  ```
- **Resultado Esperado**:
  - Mover pai para a lixeira marca o pai e todos os seus descendentes com `deleted_at`.
  - Restaurar o pai restaura o pai e todos os descendentes conjuntamente.

### Cenário 4: Construção da Árvore e Interações no Frontend
- **Comandos**:
  ```powershell
  cd caderno-leitura-0.1/frontend
  npm test
  npm run build
  ```
- **Resultado Esperado**:
  - Testes unitários do componente `StudyTreeView` e composable `useStudyHierarchy` passam com 100% de sucesso.
  - Testes de acessibilidade (ações táteis 44x44px e atalhos WAI-ARIA) aprovados.
  - `npm run build` conclui sem erros de TypeScript (`tsc -b`) ou empacotamento Vite.
