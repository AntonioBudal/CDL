# Implementation Plan: F04 — Relações entre Estudos

**Branch**: `022-relacoes-estudos` | **Date**: 2026-09-19 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/022-relacoes-estudos/spec.md`

---

## Summary

Implementar a malha semântica de conexões explícitas entre estudos (F04 do Roadmap 0.4), viabilizando a criação e consulta bidirecional de vínculos tipados (`relacionado_com`, `complementa`, `contradiz`, `depende_de`, `mesmo_tema`, `desdobramento_de`) de forma transversal a todo o acervo pessoal. A solução abrange a persistência estrita com chave estrangeira dupla e constraints de integridade no SQLite (`study_relations`), consulta unificada de backlinks sem N+1, resolução latente sob lixeira (soft delete), busca incremental de estudos candidatos com exclusão do próprio estudo e projeção gráfica vetorial de arestas Bézier dinâmicas com badges e setas direcionais a 60fps no Canvas 2D e modo Mapa.

---

## Technical Context

**Language/Version**: Python 3.13 (Backend de 64 bits no Windows) | TypeScript 5.x / JavaScript ES2022 (Frontend Vue 3).  
**Primary Dependencies**: FastAPI, SQLAlchemy 2.0, Alembic, Pydantic v2, Uvicorn | Vue 3 (Composition API, `<script setup>`), Vite, Lucide Vue Next.  
**Storage**: SQLite local em modo WAL com integridade referencial ativa (`PRAGMA foreign_keys = ON`). Tabela `study_relations`.  
**Testing**: Pytest (backend com SQLite efêmero em `tmp_path`) | Node.js Test Runner (`node --test`) e Vite build estrito no frontend.  
**Target Platform**: Windows local (PowerShell, processo único via `iniciar.py`), acessível em desktop e smartphones via rede local/Tailscale.  
**Project Type**: Aplicação Web local completa (Backend REST FastAPI + Frontend SPA Vue 3).  
**Performance Goals**: Renderização e atualização de arestas Bézier no Canvas a 60fps; busca de candidatos e carregamento de backlinks < 50ms; 0 queries N+1.  
**Constraints**: Área mínima de toque de 44x44px em telas táteis móveis; acessibilidade WAI-ARIA com navegação por teclado; isolamento absoluto do acervo real (`backend/data/caderno.db`).  
**Scale/Scope**: Centenas a milhares de estudos e conexões semânticas com filtros indexados e carregamento otimizado.

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [X] **Artigo I — Proteção Absoluta do Acervo e Privacidade de Dados**: Nenhum dado real é lido ou manipulado nos testes. Todos os testes utilizam dados fictícios sintéticos e bancos temporários.
- [X] **Artigo II — Isolamento Estrito de Testes e Operações Locais**: Testes de API e banco rodam exclusivamente em `tmp_path`. O banco ativo de produção `caderno.db` permanece 100% intocado e protegido.
- [X] **Artigo III — Fidelidade Arquitetural e Tecnológica**: Python 3.13, FastAPI, SQLAlchemy 2.0 declarativo, Alembic, Vue 3 com TypeScript estrito, sem dependência de serviços em nuvem ou APIs pagas de terceiros.
- [X] **Artigo IV — Governança por Especificação Delimitada (SDD)**: Ciclo formal rigoroso via Spec Kit (`specify` → `clarify` → `plan` → `tasks` → `analyze` → `implement`).
- [X] **Artigo V — Resiliência Operacional, Transações e Migrações Seguras**: Migração Alembic incremental e segura (`0008_add_study_relations.py`) com constraints de unicidade e integridade no banco.

---

## Project Structure

### Documentation (this feature)

```text
specs/022-relacoes-estudos/
├── spec.md                  # Especificação funcional com decisões de esclarecimento incorporadas
├── plan.md                  # Este plano técnico de implementação
├── research.md              # Decisões arquiteturais e rationales (Phase 0)
├── data-model.md            # Esquema relacional, SQLAlchemy, Pydantic e TypeScript (Phase 1)
├── contracts/
│   └── study-relations-api.yaml # Contrato OpenAPI 3.0 dos endpoints da funcionalidade
├── quickstart.md            # Guia de validação executável ponta a ponta
└── checklists/
    └── requirements.md      # Checklist de validação de qualidade da especificação (100% aprovado)
```

### Source Code (repository root)

```text
caderno-leitura-0.1/
├── backend/
│   ├── app/
│   │   ├── models/
│   │   │   ├── __init__.py           # Exportação do modelo StudyRelation
│   │   │   └── study_relation.py     # Modelo SQLAlchemy StudyRelation com constraints
│   │   ├── schemas/
│   │   │   └── study_relation.py     # Schemas Pydantic v2 (Input, Output, Backlink, Enum)
│   │   ├── services/
│   │   │   └── study_relation_service.py # Lógica de integridade, busca unificada de backlinks e busca de candidatos
│   │   ├── routers/
│   │   │   └── study_relations.py    # Endpoints REST (/api/studies/{id}/relations, /api/relations/{id}, etc.)
│   │   └── main.py                   # Inclusão do router de relações
│   ├── migrations/versions/
│   │   └── 0008_add_study_relations.py # Migração Alembic para tabela study_relations
│   └── tests/
│       ├── test_study_relations_api.py   # Testes de integração da API de relações
│       ├── test_study_relations_search.py # Testes da busca transversal de candidatos
│       └── test_study_relations_trash.py  # Testes de preservação latente sob lixeira
└── frontend/
    ├── src/
    │   ├── types.ts                  # Tipos TypeScript para StudyRelation, tipos semânticos e payloads
    │   ├── services/
    │   │   └── api.ts                # Métodos de API (getStudyRelations, createStudyRelation, deleteStudyRelation, etc.)
    │   ├── composables/
    │   │   ├── useStudyRelations.ts  # Composable reativo para gestão de relações e backlinks
    │   │   └── useCanvasConnections.ts # Cálculo geométrico de arestas Bézier e badges para o Canvas
    │   └── components/
    │       ├── relations/
    │       │   ├── StudyRelationsList.vue   # Seção de relações e backlinks no painel/tela do estudo
    │       │   └── CreateRelationModal.vue  # Modal/gaveta de criação de relação com busca rápida
    │       └── views/
    │           ├── canvas/
    │           │   └── CanvasConnectionsLayer.vue # Camada SVG de arestas Bézier sobre o Canvas
    │           └── StudyCanvasView.vue      # Integração da camada de conexões sobre o palco 2D
    └── tests/
        ├── study-relations.test.mjs  # Testes de consulta e gerenciamento de relações
        └── canvas-relations.test.mjs # Testes de cálculo de arcos Bézier e badges
```

**Structure Decision**: Adoção estrita da estrutura de aplicação web desacoplada (`backend/` FastAPI + `frontend/` Vue 3), reaproveitando os contratos existentes de isolamento e governança.

---

## Complexity Tracking

> **Nenhuma violação à Constituição.** A arquitetura utiliza recursos nativos de SQLite, SVG do navegador e CSS Transforms acelerados por GPU, sem novas dependências externas pesadas.

| Módulo / Decisão | Justificativa | Alternativa Rejeitada |
| :--- | :--- | :--- |
| Tabela `study_relations` dedicada | Integridade referencial estrita, consultas indexadas de backlinks e prevenção de anomalias | Coluna JSON em `studies`: Rejeitada por violar 1FN e impedir constraints nativas |
| Arestas vetoriais em SVG reativo | Integração natural com o ciclo de vida do Vue 3, eventos de clique e acessibilidade | Canvas 2D nativo (context2d): Rejeitado por exigir repintura imperativa complexa e dificultar interatividade declarativa |
| Busca transversal com paginação leve | Permite cruzar teses entre quaisquer obras da biblioteca com desambiguação clara | Busca global sem limite: Rejeitada para evitar overhead de memória |
