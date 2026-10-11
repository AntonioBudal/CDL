# Implementation Plan: F0.8.03 — Revisão: Bancada de Fixação Cognitiva

**Branch**: `068-revisao-bancada-fixacao` | **Date**: 2026-10-11 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/068-revisao-bancada-fixacao/spec.md`

---

## Summary

O Roadmap 0.8 / Feature 03 transforma a Central de Revisão (`/revisao`) de um painel de métricas dispersas em estilo SaaS administrativo em uma **Bancada de Fixação Cognitiva** imersiva, serena e ergonômica:
1. **Barra Unificada de Prontidão Intelectual (`ReviewStatsHeader.vue`)**: Fusão dos 5 blocos numéricos soltos em uma seção contínua que consolida pendências do dia, estimativa de tempo em minutos (~X min), distribuição entre perguntas e termos ocultos (*clozes*) e o botão primário proeminente "Praticar Revisão Agora".
2. **Bancada Imersiva de Active Recall (`ReviewCard.vue` e `useReviewSession.ts`)**: Prática sem distrações com foco total na reflexão, transição visual fluida na revelação da resposta, avaliação de retenção em 4 níveis cognitivos e suporte completo a atalhos de teclado (`Espaço` para virar e teclas `1-4` para classificar).
3. **Estado Vazio Pedagógico Interativo (`ReviewPedagogicalEmpty.vue`)**: Eliminação de telas estáticas vazias ou alertas genéricos; introdução de uma demonstração de termo oculto que se revela ao clique com microanimação didática e guia passo a passo para criar perguntas durante a leitura de livros.
4. **Conclusão Serena e Histórico de Sessões (`ReviewSummaryModal.vue` e `ReviewHubView.vue`)**: Resumo sereno ao zerar a fila de estudos diários e preservação elegante da aba de histórico de sessões anteriores.

---

## Technical Context

**Language/Version**: TypeScript 5.9+ / Node.js 20+ (Frontend) e Python 3.13 (Backend)

**Primary Dependencies**:
- Frontend: Vue 3 (Composition API, `<script setup>`), Vite, design tokens / temas semânticos nativos, composable `useReviewSession.ts`, catálogo vetorial `Icon.vue`
- Backend: FastAPI, SQLAlchemy 2.0 (endpoints existentes `/api/review/stats`, `/api/review/items`, `/api/review/items/{id}/record` e `/api/study-sessions/history` preservados)

**Storage**: SQLite 3 local em modo WAL (sem necessidade de novas tabelas ou migrações Alembic)

**Testing**:
- Frontend: `node:test` e `node:assert/strict` via `npm test`
- Build & Tipagem: `npm run build` (`vue-tsc -b && vite build`)
- Backend: `pytest`

**Target Platform**: Windows local (processo único `iniciar.py`) atendendo PC, tablets e celulares via rede privada

**Project Type**: Web application local-first (Vue 3 SPA)

**Performance Goals**:
- Início de sessão de revisão em $< 3$ segundos
- Transição visual de virada e avanço de cartão em $\le 250$ms a 60 FPS
- Suporte imediato ($0.01$ms) sob `prefers-reduced-motion: reduce`

**Constraints**:
- Imunidade cromática total: consumo exclusivo dos tokens semânticos dos 10 temas nativos
- Proibição estrita de emojis no frontend (utilizar catálogo vetorial SVG `Icon.vue`)
- Touch targets $\ge 44 \times 44$px para resoluções móveis e táteis
- Operação 100% por teclado na sessão ativa (`Espaço` + teclas `1-4`)

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Princípio | Status | Justificativa / Verificação |
|---|---|---|
| **I. Proteção do Acervo e Privacidade** | APROVADO | O redesign preserva 100% dos dados dos livros, capítulos, estudos e histórico de retenção; nenhum texto do usuário é exposto. |
| **II. Isolamento Estrito de Testes** | APROVADO | Suítes de teste de frontend e backend rodam em ambientes isolados e diretórios efêmeros (`tmp_path`), sem tocar em `caderno.db`. |
| **III. Fidelidade Arquitetural** | APROVADO | Stack oficial mantida (Vue 3, TypeScript estrito, FastAPI, SQLAlchemy 2). Nenhuma dependência externa adicionada. |
| **IV. Spec-Driven Development (SDD)** | APROVADO | O fluxo segue a ordem canônica do Roadmap 0.8, com artefatos de planejamento (`plan.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`). |
| **V. Resiliência e Integridade** | APROVADO | Zero alterações no banco de dados ativo; nenhuma migração Alembic necessária. |

---

## Project Structure

### Documentation (this feature)

```text
specs/068-revisao-bancada-fixacao/
├── spec.md              # Especificação de requisitos funcionais e critérios
├── plan.md              # Este arquivo (Plano de implementação técnica)
├── research.md          # Decisões arquiteturais e consolidação técnica (Phase 0)
├── data-model.md        # Entidades, contratos de dados e máquinas de estado (Phase 1)
├── quickstart.md        # Guia de execução e roteiro de validação (Phase 1)
├── contracts/           # Contratos de APIs e componentes (Phase 1)
│   └── review-hub-contract.md
├── checklists/
│   └── requirements.md
└── tasks.md             # Tarefas atômicas de implementação (Phase 2 - /speckit-tasks)
```

### Source Code Layout

```text
caderno-leitura-0.1/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   └── review/
│   │   │       ├── ReviewStatsHeader.vue      # Barra unificada de prontidão intelectual e gatilho de sessão
│   │   │       ├── ReviewCard.vue             # Cartão de Active Recall com virada e atalhos por teclado
│   │   │       ├── ReviewPedagogicalEmpty.vue # Estado vazio instrutivo com demonstração de cloze
│   │   │       └── ReviewSummaryModal.vue     # Modal comemorativo sereno ao zerar a fila
│   │   ├── composables/
│   │   │   └── useReviewSession.ts            # Gerenciamento de estado, atalhos de teclado e avanço
│   │   ├── views/
│   │   │   └── ReviewHubView.vue              # View principal da Central de Revisão
│   │   └── types/
│   │       └── index.ts (ou types.ts)         # Tipagens de métricas e estado de revisão
│   └── tests/
│       ├── review_hub_redesign.test.mjs       # Testes da barra de prontidão e estado vazio
│       └── review_card_keyboard.test.mjs      # Testes de ergonomia por teclado e transição
```

---

## Complexity Tracking

*Nenhuma violação constitucional identificada.*
