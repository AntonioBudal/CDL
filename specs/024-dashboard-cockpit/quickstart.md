# Quickstart & Validation Guide: F07 — Dashboard 2.0 (Cockpit de Estudos e Hub de Navegação)

**Feature Branch**: `024-dashboard-cockpit`  
**Date**: 2026-09-19  
**Status**: Validated & Implemented (100% PASS)  

---

## 1. Pré-Requisitos e Ambiente de Execução

- **Python 3.13** no virtualenv: `caderno-leitura-0.1/backend/.venv/Scripts/python.exe`
- **Node.js v24+** / npm no frontend: `caderno-leitura-0.1/frontend`
- **Isolamento Absoluto**: Todos os testes automatizados operam exclusivamente contra bancos SQLite descartáveis em diretórios temporários (`tmp_path`). O banco de dados ativo de produção (`backend/data/caderno.db`) **NUNCA** é tocado.

---

## 2. Cenários Executáveis de Validação

### Cenário 1: Retorno Consolidado de Indicadores e Atividades Recentes
- **Comando**:
  ```powershell
  cd caderno-leitura-0.1
  .\backend\.venv\Scripts\python.exe -m pytest backend/tests/test_dashboard_v2.py -k "test_dashboard_summary_recent_studies" -v
  ```
- **Resultado Esperado**:
  - `GET /api/dashboard/summary` retorna payload com `stats`, `recent_studies`, `unlinked_studies` e `latest_relations`.
  - `recent_studies` lista até 10 estudos ordenados por `updated_at DESC`.
  - Cada item possui `study_id`, `title`, `book_title`, `reading_status` e data de modificação.

### Cenário 2: Identificação de Estudos Sem Vínculos (Órfãos) e Relações Recentes
- **Comando**:
  ```powershell
  cd caderno-leitura-0.1
  .\backend\.venv\Scripts\python.exe -m pytest backend/tests/test_dashboard_v2.py -k "test_unlinked_studies_and_recent_relations" -v
  ```
- **Resultado Esperado**:
  - Estudos que possuem relações em `study_relations` (como origem ou destino) não aparecem em `unlinked_studies`.
  - Estudos sem nenhuma conexão ativa constam em `unlinked_studies` e são contabilizados em `unlinked_studies_count`.
  - As últimas relações semânticas criadas são listadas em `latest_relations` com nomes dos livros e tipos canônicos.

### Cenário 3: Exclusão Rigorosa de Soft Delete (Lixeira)
- **Comando**:
  ```powershell
  cd caderno-leitura-0.1
  .\backend\.venv\Scripts\python.exe -m pytest backend/tests/test_dashboard_v2.py -k "test_soft_deleted_items_excluded_from_dashboard" -v
  ```
- **Resultado Esperado**:
  - Estudos ou livros com `deleted_at IS NOT NULL` são omitidos de `recent_studies`, `unlinked_studies`, `latest_relations` e de todas as contagens métricas.

### Cenário 4: Retoma Rápida e Roteamento Inicial Configurável
- **Comando**:
  ```powershell
  cd caderno-leitura-0.1/frontend
  node --test tests/dashboard-cockpit.test.mjs
  ```
- **Resultado Esperado**:
  - Com `caderno_home_view = 'dashboard'`, rota `/` abre o Dashboard.
  - Com `caderno_home_view = 'books'`, rota `/` redireciona para `/books`.
  - O card de retoma rápida gera URL direta `/books/{bookId}?study={studyId}`.
  - O botão "Ver mais" expande a exibição de 5 para 10 estudos.

### Cenário 5: Calibração de Contraste e Opacidade no Calendário de 12 Meses
- **Comando**:
  ```powershell
  cd caderno-leitura-0.1/frontend
  node --test tests/dashboard-theme-contrast.test.mjs
  ```
- **Resultado Esperado**:
  - Células sem atividade (`.level-0`) possuem tokens com opacidade atenuada em todos os temas (`dark`, `sepia`, `solarized`, `e-ink`).
  - Células com atividade (`.level-1` a `.level-3`) possuem contraste nítido e opacidade plena (`1.0`), garantindo discernimento visual imediato.

### Cenário 6: Hierarquia Móvel, Abas e Prevenção de Overflow
- **Comando**:
  ```powershell
  cd caderno-leitura-0.1/frontend
  node --test tests/dashboard-mobile-a11y.test.mjs
  ```
- **Resultado Esperado**:
  - Em larguras <768px, as métricas adotam grade compacta 2x2.
  - As seções secundárias adotam seletor de abas (*tabs*) ou acordeão para reduzir rolagem.
  - Contêiner raiz possui `overflow-x: hidden` para blindagem contra rolagem lateral no smartphone.
  - Todos os elementos clicáveis respeitam a área mínima tátil de 44x44px.

---

## 3. Evidências Finais de Validação (Homologação)

### 3.1 Backend (Pytest)
- **Comando**: `pytest backend/tests/`
- **Resultado**: `193 passed, 1 skipped, 0 failures` (tempo de execução: 70.14s)
- **Isolamento**: 100% dos testes executados em bancos efêmeros descartáveis em `tmp_path`, sem nenhum acesso a `backend/data/caderno.db`.

### 3.2 Frontend (Node Test Runner)
- **Comando**: `npm test` (`node --test tests/*.test.mjs`)
- **Resultado**: `190 passed, 0 failures` (tempo de execução: 4.5s)
- **Cobertura**: Retoma de estudos, expansão para 10 itens, identificação de órfãos, conexões semânticas, tokens de contraste do heatmap em todos os temas e ergonomia móvel (alvos 44px e contenção de overflow).

### 3.3 Compilação de Produção (Vite + TypeScript)
- **Comando**: `npm run build` (`vue-tsc -b && vite build`)
- **Resultado**: Sucesso em 23.27s (dist gerado com 0 erros de tipagem estrita).
