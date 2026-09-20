# Implementation Plan: F05 — Agrupamento Visual

**Branch**: `023-agrupamento-visual` | **Date**: 2026-09-19 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `specs/023-agrupamento-visual/spec.md`  

---

## Summary

Implementar um sistema unificado e não-destrutivo de **Agrupamento Visual** que permite ao leitor projetar e reparticionar os estudos sob múltiplos critérios (por Capítulo, por Status de Leitura, por Categoria e por Data) nas visualizações de Grade e Lista, além de disponibilizar **Molduras Manuais Delimitadoras (*Canvas Frames*)** no Canvas 2D com movimentação solidária em bloco, apoiado pela adição do campo `reading_status` (ciclo editorial de 4 estados) e pela tabela `canvas_frames` com persistência relacional atômica.

---

## Technical Context

**Language/Version**: Python 3.13 de 64 bits (backend) / TypeScript 5.8 e Node.js v24+ (frontend)  
**Primary Dependencies**: FastAPI 0.115+, SQLAlchemy 2.0+, Alembic, Uvicorn, Vue 3.5+ (Composition API, `<script setup>`), Vite 6+, Lucide Vue Next  
**Storage**: SQLite local em modo Write-Ahead Logging (`backend/data/caderno.db`), com isolamento absoluto e bancos descartáveis em `tmp_path` durante testes  
**Testing**: `pytest` com fixtures temporárias no backend (`pytest backend/tests`), `node --test` com asserções estritas no frontend (`npm test`)  
**Target Platform**: Windows 11 local (PowerShell, caminhos com espaços e acentos, preservação de quebras CRLF/LF) com responsividade integral para telas móveis e tablets  
**Project Type**: Aplicação web local orquestrada em processo único (`iniciar.py`)  
**Performance Goals**: Reparticionamento reativo de mais de 100 estudos em memória em <100ms; atualização de status com confirmação em <200ms; arrasto de molduras manuais no Canvas 2D a 60fps estáveis  
**Constraints**: Zero chamadas para nuvem ou APIs externas pagas; preservação absoluta de dados privados do usuário; alvos de toque mínimos de 44x44px; projeção reversível no Canvas (restauração de coordenadas originais ao sair de agrupamentos automáticos)  
**Scale/Scope**: Obras com dezenas de capítulos e centenas de estudos catalogados  

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Princípio Constitucional | Requisito / Critério de Auditoria | Status | Justificativa / Mecanismo de Garantia |
|---|---|:---:|---|
| **I. Privacidade de Dados** | Nenhum dado pessoal do acervo exposto em prompts, logs ou serviços externos | **PASS** | Toda a operação é local no SQLite. Testes utilizam amostras sintéticas ("Estudo Alfa", "Livro de Teste"). |
| **II. Isolamento de Testes** | Banco ativo `backend/data/caderno.db` nunca é acessado por testes | **PASS** | Todas as suítes de teste de agrupamento e molduras usam fixtures `tmp_path` do pytest e mocks no frontend. |
| **III. Arquitetura e Stack** | Python 3.13, FastAPI, SQLAlchemy 2, Alembic, Vue 3, Vite, SQLite | **PASS** | Tecnologias canônicas do projeto rigorosamente preservadas sem novas dependências externas. |
| **IV. Governança SDD** | Execução por fatias verificáveis (`specify` → `clarify` → `plan` → `tasks` → `implement`) | **PASS** | Ciclo SDD estritamente respeitado com esclarecimentos prévios consolidados (Q1: A, Q2: A, Q3: A). |
| **V. Resiliência e Migrações** | Migração segura sem quebra de chaves primárias e com cascata limpa | **PASS** | Migração Alembic `0009` adiciona coluna com valor padrão `'rascunho'` e nova tabela `canvas_frames` com `ON DELETE CASCADE`. |

---

## Project Structure

### Documentation (this feature)

```text
specs/023-agrupamento-visual/
├── spec.md              # Especificação de requisitos e cenários de aceite
├── plan.md              # Este plano de implementação técnica
├── research.md          # Decisões de pesquisa técnica consolidadas
├── data-model.md        # Modelagem relacional, schemas Pydantic e tipos TypeScript
├── quickstart.md        # Cenários executáveis de validação ponta a ponta
├── contracts/           # Contratos OpenAPI para rotas de agrupamento e frames
│   └── study-grouping-api.yaml
└── checklists/          # Checklist de qualidade de requisitos
    └── requirements.md
```

### Source Code (repository root)

```text
caderno-leitura-0.1/
├── backend/
│   ├── app/
│   │   ├── models/
│   │   │   ├── study.py            # [MODIFY] Adicionar campo reading_status
│   │   │   ├── canvas_frame.py     # [NEW] Modelo CanvasFrame
│   │   │   └── __init__.py         # [MODIFY] Exportar CanvasFrame
│   │   ├── schemas/
│   │   │   └── study_grouping.py   # [NEW] Schemas Pydantic para status e frames
│   │   ├── services/
│   │   │   ├── study_service.py    # [MODIFY] Método update_study_status com concorrência
│   │   │   └── canvas_service.py   # [MODIFY] Métodos CRUD de canvas_frames
│   │   ├── routers/
│   │   │   ├── studies.py          # [MODIFY] Endpoint PATCH /api/studies/{id}/status
│   │   │   └── canvas.py           # [MODIFY] Endpoints /api/books/{id}/canvas/frames e /canvas/frames/{id}
│   │   └── migrations/versions/
│   │       └── 0009_add_reading_status_and_canvas_frames.py # [NEW] Migração Alembic
│   └── tests/
│       └── test_study_grouping_api.py # [NEW] Testes de integração backend
│
└── frontend/
    ├── src/
    │   ├── types.ts                # [MODIFY] Tipos ReadingStatus, CanvasFrameItem, StudyGroup
    │   ├── services/
    │   │   └── api.ts              # [MODIFY] Métodos updateStudyStatus, getCanvasFrames, etc.
    │   ├── composables/
    │   │   ├── useStudyGrouping.ts # [NEW] Particionamento reativo por capítulo, status, categoria e data
    │   │   └── useCanvasFrames.ts  # [NEW] Gestão espacial de molduras e movimentação solidária
    │   └── components/
    │       ├── views/
    │       │   ├── GroupBySelector.vue      # [NEW] Seletor visual de agrupamento na barra de ferramentas
    │       │   ├── GroupSection.vue         # [NEW] Contêiner de seção colapsável com sticky header
    │       │   ├── StudyGridView.vue        # [MODIFY] Integração com GroupSection
    │       │   ├── StudyListView.vue        # [MODIFY] Integração com GroupSection
    │       │   ├── StudyCanvasView.vue      # [MODIFY] Integração com CanvasFrames e projeção reversível
    │       │   └── canvas/
    │       │       └── CanvasFrameNode.vue  # [NEW] Componente visual da moldura no Canvas 2D
    └── tests/
        ├── study-grouping.test.mjs          # [NEW] Testes unitários do composable de agrupamento
        ├── canvas-frames.test.mjs           # [NEW] Testes unitários de contenção e movimentação solidária
        └── study-grouping-a11y.test.mjs     # [NEW] Testes de acessibilidade, sticky headers e 44px
```

---

## Complexity Tracking

*Nenhuma violação ou desvio da Constituição detectado. Todas as mudanças seguem os padrões estabelecidos do projeto.*
