# Implementation Plan: F0.6.2 — Seleção e Ações Contextuais

**Branch**: `041-selecao-acoes-contextuais` | **Date**: 2026-09-27 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/041-selecao-acoes-contextuais/spec.md`

---

## Summary

Evoluir a experiência de leitura de estudos no Leitorum através do conceito **`Selecionar → Escolher ação → Pronto`**.  
A solução técnica implementa:
1. **Frontend Contextual Adaptativo**:
   - Composable `useTextSelection.ts` para captura robusta de seleção de texto (Selection API + Range API) em `StudyView.vue` / `StudyTabs.vue`.
   - Componente `FloatingActionsToolbar.vue` com posicionamento inteligente no Desktop (barra flutuante sobre a seleção com detecção de bordas) e na base no Mobile (Bottom Sheet / action bar fixa com touch targets >= 44px).
   - Suporte completo às 5 ações: **Destacar** (paleta suave de 5 cores), **Anotar** (popover de nota vinculada), **Copiar Citação** (formatação com metadados da obra para clipboard), **Ocultar Trecho** (bloco de oclusão com botão de revelar) e **Transformar em Pergunta** (enunciado de estudo sobre texto ocluso).
   - Composable e utilitário `highlightRenderer.ts` para sobreposição segura de tags `<mark>` e `<span>` sobre o DOM de `MarkdownContent.vue` sem alterar nem corromper o texto Markdown original.
   - Popover de contexto `HighlightActionPopover.vue` para edição ou remoção de marcações existentes com 1 clique.
2. **Backend e Persistência Confiável**:
   - Nova entidade relacional `StudyHighlight` no SQLite mapeada via SQLAlchemy 2.0.
   - Migração Alembic `0020_add_study_highlights.py`.
   - Endpoints REST em `app/routers/study_highlights.py` com schemas Pydantic v2 para CRUD completo com isolamento por usuário e deleção em cascata com o estudo.

---

## Technical Context

**Language/Version**: Python 3.13 (64-bit) no backend, TypeScript 5.x / Vue 3 (Composition API `<script setup>`) no frontend  
**Primary Dependencies**: FastAPI, Pydantic v2, SQLAlchemy 2.0 (ORM), Alembic, Vite, Tailwind CSS / Vanilla CSS, `markdown-it`  
**Storage**: SQLite local (modo WAL), nova tabela relacional `study_highlights` vinculada a `studies` e `users`  
**Testing**: `pytest` com bancos descartáveis via `tmp_path` no backend; `vitest` / `vue-test-utils` no frontend  
**Target Platform**: Windows local (PowerShell, Uvicorn em processo único via `iniciar.py`) atendendo PC e dispositivos móveis na rede local/Tailscale  
**Project Type**: Aplicação Web local (SPA Vue 3 servida por backend FastAPI)  
**Performance Goals**: Exibição da barra flutuante em < 80ms após seleção; tempo de resposta de mutação de destaque em < 50ms  
**Constraints**: Zero perda de dados; preservação estrita do Markdown original; isolamento total de dados e privacidade (Constituição Artigo I)  
**Scale/Scope**: Operação local monousuário e multiusuário local com privacidade garantida por `user_id`  

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Princípio Constitucional | Avaliação | Status |
| :--- | :--- | :---: |
| **I. Proteção do Acervo e Privacidade** | Todas as anotações, perguntas e destaques são gravados estritamente no SQLite local do usuário (`backend/data/caderno.db` em produção; bancos efêmeros em testes); zero transmissão para APIs ou serviços externos. | ✅ APROVADO |
| **II. Isolamento Estrito de Testes** | Todas as suítes automatizadas de testes de destaques executam contra bancos SQLite efêmeros em diretórios temporários (`tmp_path`), sem tocar o banco ativo. | ✅ APROVADO |
| **III. Fidelidade Arquitetural** | Respeita rigorosamente a stack FastAPI + SQLAlchemy 2.0 + Alembic no backend e Vue 3 + TypeScript estrito + Vite no frontend. | ✅ APROVADO |
| **IV. Governança por SDD** | Segue rigorosamente o fluxo Spec Kit (`speckit-specify` → `speckit-plan` → `speckit-tasks` → `speckit-implement`). | ✅ APROVADO |
| **V. Resiliência e Migrações Seguras** | Nova tabela criada via migração Alembic padronizada com chaves estrangeiras `CASCADE` e restrições `CHECK`, sem riscos de lock ou corrupção de tabelas existentes. | ✅ APROVADO |

---

## Project Structure

### Documentation (this feature)

```text
specs/041-selecao-acoes-contextuais/
├── spec.md                  # Especificação funcional refinada e aprovada
├── checklists/
│   └── requirements.md      # Checklist de validação de qualidade (100% OK)
├── plan.md                  # Este plano de implementação técnica
├── research.md              # Pesquisa técnica e justificativas de arquitetura
├── data-model.md            # Modelo de dados e entidades de destaques
├── contracts/
│   ├── highlights-api-contract.md     # Contrato formal da API /api/studies/{study_id}/highlights
│   └── contextual-toolbar-contract.md # Contrato dos componentes de UI da barra flutuante e popover
└── quickstart.md            # Guia de validação automatizada e cenários manuais
```

### Source Code (repository layout)

```text
caderno-leitura-0.1/
├── backend/
│   ├── alembic/ / migrations/
│   │   └── versions/
│   │       └── 0020_add_study_highlights.py   # Migração para tabela study_highlights
│   ├── app/
│   │   ├── models/
│   │   │   ├── study_highlight.py             # Modelo SQLAlchemy StudyHighlight
│   │   │   └── __init__.py                    # Exportação do modelo
│   │   ├── schemas/
│   │   │   └── study_highlight.py             # DTOs Pydantic (Create, Update, Read)
│   │   ├── services/
│   │   │   └── study_highlight_service.py     # Regras de negócio, permissões e CRUD
│   │   ├── routers/
│   │   │   └── study_highlights.py            # Endpoints REST /api/studies/{study_id}/highlights
│   │   └── main.py                            # Inclusão da rota no app FastAPI
│   └── tests/
│       └── test_study_highlights.py           # Testes unitários e de integração de destaques
├── frontend/
│   └── src/
│       ├── types.ts                           # Tipos StudyHighlight, HighlightColor, HighlightKind
│       ├── services/
│       │   └── api.ts                         # Métodos api.listHighlights, create, update, delete
│       ├── composables/
│       │   ├── useTextSelection.ts            # Captura de seleção, bounding box e offsets
│       │   └── useStudyHighlights.ts          # Gerenciamento de estado reativo dos destaques do estudo
│       ├── utils/
│       │   └── highlightRenderer.ts           # Ancoragem e renderização não destrutiva no DOM
│       ├── components/
│       │   ├── FloatingActionsToolbar.vue     # Barra flutuante contextual (Desktop & Mobile)
│       │   ├── HighlightActionPopover.vue     # Popover para gerenciar destaque existente
│       │   ├── StudyTabs.vue                  # Integração da seleção com as seções do estudo
│       │   └── MarkdownContent.vue            # Renderização de texto com sobreposição de destaques
│       └── views/
│           └── StudyView.vue                  # Conexão geral com permissão canEdit e toasts
```

**Structure Decision**: Aplicação web SPA com frontend Vue 3 e backend FastAPI, mantendo isolamento por camadas e respeitando os padrões consolidados no repositório.

---

## Complexity Tracking

*Nenhuma violação aos princípios constitucionais ou padrões arquiteturais foi identificada. O design preserva a simplicidade, mantendo o Markdown original intocado e desacoplando a renderização dos trechos da lógica de armazenamento relacional.*
