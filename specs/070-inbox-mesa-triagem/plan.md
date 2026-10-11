# Implementation Plan: F0.8.04 — Inbox: Mesa de Triagem e Despejo Intelectual

**Branch**: `070-inbox-mesa-triagem` | **Date**: 2026-10-11 | **Spec**: [spec.md](file:///c:/Users/User/caderno/specs/070-inbox-mesa-triagem/spec.md)

**Input**: Feature specification from `specs/070-inbox-mesa-triagem/spec.md`

---

## Summary

Transformar a tela `/inbox` do Leitorum em uma **Mesa de Triagem e Despejo Intelectual**, eliminando diálogos modais bloqueantes para capturar pensamentos efêmeros (*fleeting notes*).
A solução técnica implementa:
1. Um componente permanente no topo da página (`QuickThoughtDrop.vue`) que expande suavemente com `:focus-within` e persiste imediatamente via `Ctrl+Enter` (e `Cmd+Enter`).
2. Uma barra segmentada de triagem moderna com contadores dinâmicos nos 5 estados (`Pendentes`, `Promovidos`, `Vinculados`, `Arquivados` e `Todos`) e acessibilidade WAI-ARIA completa.
3. Redesenho de `CaptureItemCard.vue` com ferramentas diretas de triagem (Promover, Vincular, Arquivar, Desarquivar, Excluir) e transições cinéticas aceleradas por GPU (`transform: translateX(30px)`, `opacity: 0`, $\le 200$ms).
4. Navegação e triagem rápida por teclado (`J`/`K` para percorrer notas, `E` para arquivar, `Ctrl+Shift+C` para focar a captura) com guarda defensiva estrita contra digitação.
5. Estado vazio acolhedor ("Mesa Limpa"), tratamento editorial de erros (banimento de mensagens cruas de "Not Found") e 100% de conformidade com os 10 temas visuais do Leitorum (imunidade cromática, zero emojis).

---

## Technical Context

**Language/Version**: TypeScript 5.6+ (Strict mode), Vue 3.5 (Composition API, `<script setup>`), Vite. Backend: Python 3.13 (FastAPI, SQLAlchemy 2.0, Alembic, SQLite WAL).

**Primary Dependencies**: Vue 3, Vue Router, `@vue/test-utils` / `node:test`. Backend inalterado. Zero novas dependências de runtime.

**Storage**: SQLite local (`backend/data/caderno.db` em produção; efêmero/isolado em testes). Tabela existente `inbox_captures`. Nenhuma alteração de schema ou migração de banco é necessária.

**Testing**: Suíte de testes do frontend com `node:test` (`frontend/tests/inbox.test.mjs`, `frontend/tests/feature-070-inbox-mesa-triagem.test.mjs`), build de produção com verificação de tipos (`npm run build`), e suíte de backend (`pytest backend/tests`).

**Target Platform**: Aplicação web local responsiva para desktop e dispositivos móveis (Windows local, Tailscale, PWA).

**Project Type**: Web application (Frontend SPA em Vue 3 + Backend API FastAPI local em processo único).

**Performance Goals**: Animações de triagem e saída $\le 200$ms a 60 FPS consistentes; salvamento e inserção no topo da lista < 500ms; resposta de filtros da barra < 100ms.

**Constraints**: Imunidade Cromática (consumo estrito dos tokens CSS dos 10 temas, banimento de hexadecimais fixos); Zero emojis; Acessibilidade WAI-ARIA com alvos táteis móveis $\ge 44 \times 44$px; Sem alteração no backend; Preservação absoluta da privacidade do acervo.

**Scale/Scope**: 1 tela principal refatorada (`InboxView.vue`), 1 novo componente (`QuickThoughtDrop.vue`), 1 componente redesenhado (`CaptureItemCard.vue`), novo teste de contrato (`feature-070-inbox-mesa-triagem.test.mjs`).

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Artigo da Constituição | Descrição do Princípio | Status | Justificativa / Validação |
|---|---|---|---|
| **I. Proteção Absoluta do Acervo** | Proibição de exposição do acervo real do usuário e preservação de dados. | **PASS** | Nenhuma nota real é lida ou exposta; todas as validações usam dados sintéticos. |
| **II. Isolamento Estrito de Testes** | Zero impacto no banco ativo; bancos efêmeros e descartáveis. | **PASS** | Testes de unidade operam em memória e mocks; testes de backend usam `tmp_path`. |
| **III. Fidelidade Arquitetural** | FastAPI, Vue 3 (`<script setup>`, TS estrito), SQLite WAL, processo único. | **PASS** | Tecnologias respeitadas rigorosamente; zero dependências externas adicionadas. |
| **IV. Governança por SDD** | Fatias delimitadas e ciclo formal Spec Kit. | **PASS** | Etapa formal `speckit.plan` em execução, sem avançar para tarefas ou código prematuramente. |
| **V. Resiliência Operacional** | Backups pré-migração e segurança de dados. | **PASS** | Nenhuma alteração de schema, DDL ou migração é realizada nesta feature. |

*Re-avaliação pós-Fase 1: Todos os artigos da Constituição permanecem 100% atendidos.*

---

## Project Structure

### Documentation (this feature)

```text
specs/070-inbox-mesa-triagem/
├── plan.md              # Este plano técnico consolidado
├── research.md          # Decisões técnicas da Fase 0 (expansão suave, GPU transitions, atalhos J/K/E)
├── data-model.md        # Modelos de dados e estados reativos da Fase 1
├── quickstart.md        # Roteiro de testes automatizados e validação manual
└── contracts/
    └── inbox-contract.md # Contratos de UI, componentes, WAI-ARIA e imunidade cromática
```

### Source Code (repository root)

```text
caderno-leitura-0.1/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   └── inbox/
│   │   │       ├── QuickThoughtDrop.vue       # [NOVO] Campo permanente superior com expansão suave e Ctrl+Enter
│   │   │       ├── CaptureItemCard.vue        # [REFATORADO] Cartão com ferramentas de triagem, animação de saída e tokens semânticos
│   │   │       ├── QuickCaptureModal.vue      # [PRESERVADO] Modal global para uso fora da tela /inbox
│   │   │       └── LinkToStudyModal.vue       # [PRESERVADO] Modal de vinculação a estudo existente
│   │   ├── composables/
│   │   │   ├── useInboxCount.ts               # [PRESERVADO] Contagem reativa de pendências do Inbox
│   │   │   └── useQuickCapture.ts             # [PRESERVADO] Estado global de captura rápida
│   │   ├── views/
│   │   │   └── InboxView.vue                  # [REFATORADO] Mesa de Triagem com barra segmentada, atalhos J/K/E e mesa limpa
│   │   └── types.ts                           # [PRESERVADO/ESTENDIDO] Tipos de triagem e captura
│   └── tests/
│       ├── inbox.test.mjs                     # [PRESERVADO] Testes existentes de tipos e métodos de API
│       └── feature-070-inbox-mesa-triagem.test.mjs # [NOVO] Teste de contrato e integridade da Mesa de Triagem
└── backend/
    ├── app/
    │   └── routers/
    │       └── inbox.py                       # [PRESERVADO] Endpoints REST inalterados (/api/inbox/captures)
    └── tests/                                 # [PRESERVADO] Suíte de testes do backend
```

**Structure Decision**: A implementação é restrita ao frontend (`caderno-leitura-0.1/frontend/`), estendendo componentes em `src/components/inbox/`, atualizando a visualização mestre `src/views/InboxView.vue` e adicionando uma suíte dedicada em `tests/`, mantendo o backend 100% inalterado e preservado.

---

## Complexity Tracking

> **Nenhuma violação constitucional.** Todos os princípios e diretrizes foram atendidos sem necessidade de exceções técnicas.
