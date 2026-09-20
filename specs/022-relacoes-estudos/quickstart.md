# Quickstart & Validation Guide: F04 — Relações entre Estudos

**Feature Branch**: `022-relacoes-estudos`  
**Date**: 2026-09-19  
**Status**: Homologado e 100% Validado  

---

## 1. Pré-Requisitos e Ambiente de Execução

- **Python 3.13** ativo no virtualenv: `caderno-leitura-0.1/backend/.venv/Scripts/python.exe`
- **Node.js v24+** / npm no frontend: `caderno-leitura-0.1/frontend`
- **Isolamento Absoluto**: Todos os testes automatizados rodam exclusivamente contra bancos SQLite efêmeros em diretórios temporários (`tmp_path`). O banco de dados ativo (`backend/data/caderno.db`) **JAMAIS** é tocado.

---

## 2. Cenários Executáveis de Validação & Evidências Reais

### Cenário 1: Migração Alembic e Integridade de Restrições
- **Comando**:
  ```powershell
  cd caderno-leitura-0.1
  .\backend\.venv\Scripts\python.exe -m pytest backend/tests/test_study_relations_api.py -v
  ```
- **Evidência Registrada**:
  - Migração `0008_add_study_relations` aplicada com sucesso.
  - Constraints `ck_study_relations_no_self`, `ck_study_relations_type` e `uq_study_relations_src_tgt_type` ativas e validadas.
  - Índices de performance `ix_study_relations_source` e `ix_study_relations_target` criados.
  - Testes unitários de rejeição de auto-relacionamento (`test_reject_self_relation`), duplicata (`test_reject_duplicate_relation`) e tipo inválido (`test_reject_invalid_relation_type`) aprovados.

### Cenário 2: API de Vínculos Semânticos e Resolução de Backlinks
- **Comando**:
  ```powershell
  cd caderno-leitura-0.1
  .\backend\.venv\Scripts\python.exe -m pytest backend/tests/test_study_relations_api.py -k "test_create_and_get_study_relations_bidirectional" -v
  ```
- **Evidência Registrada**:
  - `POST /api/studies/{id}/relations`: Cria relação direcional com código `HTTP 201`.
  - `GET /api/studies/{id}/relations`: Retorna relações de saída (*outbound*) no estudo de origem e backlinks (*inbound*) com metadados completos de livro e capítulo no estudo de destino.
  - `PATCH /api/relations/{id}` e `DELETE /api/relations/{id}`: Atualização e remoção segura validadas em `test_update_and_delete_relation`.

### Cenário 3: Busca Rápida de Estudos Candidatos (Transversal ao Acervo)
- **Comando**:
  ```powershell
  cd caderno-leitura-0.1
  .\backend\.venv\Scripts\python.exe -m pytest backend/tests/test_study_relations_api.py -k "test_search_candidate_studies" -v
  ```
- **Evidência Registrada**:
  - `GET /api/studies/search-candidates?query=...&exclude_study_id=...`: Busca incremental transversal rápida em todo o acervo ativo.
  - Estudo de origem informado em `exclude_study_id` e estudos na lixeira são rigorosamente filtrados.

### Cenário 4: Preservação Latente sob Soft Delete (Lixeira) & Cascata Definitiva
- **Comando**:
  ```powershell
  cd caderno-leitura-0.1
  .\backend\.venv\Scripts\python.exe -m pytest backend/tests/test_study_relations_trash.py -v
  ```
- **Evidência Registrada**:
  - `test_latent_relations_under_soft_delete_and_restore`: Ao mover estudo para a lixeira, os vínculos são ocultados das listagens ativas e do Canvas; ao restaurar o estudo, todas as conexões reaparecem intactas.
  - `test_permanent_deletion_cascades_relations`: No expurgo definitivo (`DELETE /api/studies/{id}/permanent`), relações vinculadas são removidas automaticamente em cascata (`ON DELETE CASCADE` com `passive_deletes=True`).

### Cenário 5: Cálculo Geométrico de Arestas Bézier, Badges e Acessibilidade no Frontend
- **Comando**:
  ```powershell
  cd caderno-leitura-0.1/frontend
  npm test
  ```
- **Evidência Registrada**:
  - `canvas-relations.test.mjs`: Testes de ancoragem analítica retangular (`getRectIntersection`), cálculo de curvatura Bézier cúbica e posicionamento paramétrico de badges aprovados.
  - `study-relations.test.mjs`: Dicionário `RELATION_TYPE_LABELS`, contagem unificada e normalização bidirecional aprovados.
  - `study-relations-a11y.test.mjs`: Contrato WAI-ARIA (`role="dialog"`, `role="listbox"`, `role="radiogroup"`), atalho Escape e alvos de toque mínimos de 44x44px aprovados.
  - Resultado: **162/162 testes unitários do frontend aprovados (100% verde)**.

### Cenário 6: Validação de Build e Tipagem Estrita TypeScript
- **Comando**:
  ```powershell
  cd caderno-leitura-0.1/frontend
  npm run build
  ```
- **Evidência Registrada**:
  - `vue-tsc -b`: 0 erros de tipagem estrita TypeScript.
  - `vite build`: Pacote de produção compilado com sucesso em `frontend/dist/`.

### Cenário 7: Suíte Completa de Regressão do Backend
- **Comando**:
  ```powershell
  cd caderno-leitura-0.1
  .\backend\.venv\Scripts\python.exe -m pytest backend/tests
  ```
- **Evidência Registrada**:
  - **182 testes executados e aprovados** (1 pulado por não-aplicabilidade de symlink no Windows local).
  - 0 falhas, 0 erros.
