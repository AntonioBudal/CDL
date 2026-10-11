# Implementation Plan: F0.8.02 — Destaques: Códice e Margens Vivas

**Branch**: `067-destaques-codice-margens` | **Date**: 2026-10-11 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/067-destaques-codice-margens/spec.md`

---

## Summary

O Roadmap 0.8 / Feature 02 transforma a página `/destaques` de uma listagem transacional com filtros faceta genéricos em uma experiência imersiva de *commonplace book* (fichas literárias e caderno de citações vivo):
1. **Fichas Literárias (*HighlightCard.vue*)**: Apresentação tipográfica destacada para o trecho da obra em fonte serifada (`--font-serif`) com aspas editoriais, separação visual nítida em relação a anotações pessoais do leitor e rodapé bibliográfico com livro, capítulo, localização e data.
2. **Categorias Semânticas de Grifo (*HighlightFilterToolbar.vue*)**: Conversão dos seletores de cor em intenções intelectuais de estudo (Ideia Central, Citação-chave, Dúvida, Refutação, Síntese) com contagem dinâmica e `aria-label` acessível.
3. **Cópia Contextual Multiformato (`citationFormatter.ts`)**: Cópia rápida de citações em formatos acadêmico (ABNT) e Markdown com microfeedback tátil no botão e notificação flutuante de 1500ms via `useFloatingToast.ts`.
4. **Expansão Suave de Contexto**: Truncamento inteligente para passagens com mais de 260 caracteres com animação fluida ($\le 180$ms) acelerada por GPU e suporte a `prefers-reduced-motion`.
5. **Estado de Erro Acolhedor e Resiliente (*HighlightsLibraryView.vue*)**: Substituição de alertas vermelhos estáticos por estado de erro integrado aos 10 temas visuais com suporte a reintento (*retry*).

---

## Technical Context

**Language/Version**: TypeScript 5.9+ / Node.js 20+ (Frontend) e Python 3.13 (Backend)

**Primary Dependencies**:
- Frontend: Vue 3 (Composition API, `<script setup>`), Vite, design tokens / temas semânticos nativos, composable `useFloatingToast.ts`, catálogo vetorial `Icon.vue`
- Backend: FastAPI, SQLAlchemy 2.0 (sem alterações de backend ou migrações necessárias)

**Storage**: SQLite 3 local em modo WAL (sem alteração de schema ou migrações)

**Testing**:
- Frontend: `node:test` e `node:assert/strict` via `npm test`
- Build & Tipagem: `npm run build` (`vue-tsc -b && vite build`)
- Backend: `python -m pytest`

**Target Platform**: Windows local (processo único `iniciar.py`) atendendo PC, tablets e celulares via rede privada

**Project Type**: Web application local-first (Vue 3 SPA)

**Performance Goals**:
- Latência de filtragem reativa $< 50$ms
- Transição de expansão de contexto em $\le 180$ms a 60 FPS acelerada por GPU
- Duração exata do microfeedback de cópia em 1500ms
- Suporte imediato (0.01ms) sob `prefers-reduced-motion: reduce`

**Constraints**:
- Imunidade cromática total: consumo exclusivo dos tokens semânticos dos 10 temas nativos
- Proibição estrita de emojis no frontend (utilizar catálogo vetorial SVG `Icon.vue`)
- Touch targets $\ge 44 \times 44$px para resoluções móveis e táteis
- Preservação funcional integral dos endpoints (`/api/highlights/library` e `/api/studies/{id}/highlights/{id}`)

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Princípio | Status | Justificativa / Verificação |
|---|---|---|
| **I. Proteção do Acervo e Privacidade** | APROVADO | O redesign preserva 100% dos dados dos livros, capítulos e notas; testes utilizam dados sintéticos em memória sem expor dados privados. |
| **II. Isolamento Estrito de Testes** | APROVADO | Suítes de teste utilizam mocks isolados e `tmp_path`, sem qualquer leitura ou gravação no banco ativo `backend/data/caderno.db`. |
| **III. Fidelidade Arquitetural** | APROVADO | Stack oficial mantida (Vue 3, TypeScript estrito, FastAPI, SQLAlchemy 2). Nenhuma biblioteca externa ou dependência pesada adicionada. |
| **IV. Spec-Driven Development (SDD)** | APROVADO | O fluxo segue a ordem canônica do Roadmap 0.8, com especificação e planejamento formais antes da implementação. |
| **V. Resiliência e Integridade** | APROVADO | Não há alterações no banco de dados SQLite ou migrações Alembic necessárias. |

---

## Project Structure

### Documentation (this feature)

```text
specs/067-destaques-codice-margens/
├── spec.md              # Especificação de requisitos funcionais e critérios
├── plan.md              # Este arquivo (Plano de implementação técnica)
├── research.md          # Decisões arquiteturais e consolidação técnica (Phase 0)
├── data-model.md        # Entidades, contratos de dados e máquinas de estado (Phase 1)
├── quickstart.md        # Guia de execução e roteiro de validação (Phase 1)
├── contracts/           # Contratos de APIs e componentes (Phase 1)
│   └── highlights-library-contract.md
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
│   │   │   └── highlights/
│   │   │       ├── HighlightCard.vue          # Ficha literária com tipografia editorial e cópia
│   │   │       └── HighlightFilterToolbar.vue # Filtros semânticos com categorias de estudo
│   │   ├── utils/
│   │   │   └── citationFormatter.ts           # Utilitário de formatação de citações (ABNT/Markdown)
│   │   ├── views/
│   │   │   └── HighlightsLibraryView.vue      # View da biblioteca com estado de erro temático
│   │   └── types/
│   │       └── highlights.ts (ou index.ts)    # Tipagem de categorias e formatos de citação
│   └── tests/
│       ├── highlight_card_editorial.test.mjs  # Testes da ficha literária e formatação
│       ├── highlight_filter_semantic.test.mjs # Testes das categorias semânticas e acessibilidade
│       ├── highlight_citation_copy.test.mjs   # Testes de cópia de citação e microfeedback
│       └── highlights_error_retry.test.mjs    # Testes do estado de erro e recuperação
└── backend/
    └── tests/                                 # Suíte de regressão do backend (sem alterações)
```

**Structure Decision**: Aplicação Web local com Frontend em Vue 3 (Composition API / TypeScript) e Backend FastAPI. O escopo da Feature 02 é 100% contido no cliente frontend, consumindo os endpoints já existentes e testados.

---

## Architecture & Component Breakdown

### 1. `HighlightCard.vue` (Ficha Literária)
- **Tipografia Editorial**:
  - Trecho citado com classe `.editorial-quote` (`font-family: var(--font-serif)`, tamanho `1.05rem`, aspas clássicas).
  - Indicador de tonalidade através de borda esquerda semitransparente na cor semântica do tema.
- **Bloco da Voz do Leitor**:
  - Subordinado visualmente com fundo suave (`--bg-subtle`), ícone `edit-3` e tipografia `--font-sans`.
- **Ações Rápidas de Ficha**:
  - Botão de cópia rápida no cabeçalho com transição suave de ícone (`copy` -> `check`) e disparo de toast flutuante (1500ms).
  - Truncamento defensivo em 260 caracteres com transição suave ($\le 180$ms) e botão "Expandir contexto".
  - Edição in-card e confirmação integrada de exclusão.

### 2. `HighlightFilterToolbar.vue` (Filtros Semânticos)
- **Categorias Intelectuais de Estudo**:
  - Pílulas para Ideia Central (Amarelo), Citação-chave (Verde), Dúvida (Azul), Refutação (Rosa) e Síntese (Roxo).
  - Rótulos visíveis, contadores dinâmicos de itens e atributos acessíveis `aria-label`.
- **Eliminação de Cores Hexadecimais**:
  - Remoção dos valores hexadecimais estáticos (`#eab308`, `#22c55e`, etc.) em favor de variáveis semânticas do tema.
- **Integração com Busca Textual e Modos**:
  - Campo de busca integrado com debounce de 250ms e seletor Recentes vs Por Obra.

### 3. `HighlightsLibraryView.vue` (Visualização Principal)
- **Estado de Erro Acolhedor**:
  - Remoção definitiva da classe `.notice-error` com cores `#fef2f2` e `#991b1b`.
  - Bloco de erro integrado aos tokens de tema (`--bg-surface`, `--border-subtle`, `--text-primary`) com botão "Tentar novamente" (`.btn-secondary`).
- **Estados Vazios Contextualizados**:
  - Diferenciação clara entre "Sem resultados para os filtros" e "Biblioteca sem destaques".

### 4. `citationFormatter.ts` (Novo Utilitário)
- Funções puras e testáveis:
  - `formatCitationABNT(item: HighlightLibraryItem): string`
  - `formatCitationMarkdown(item: HighlightLibraryItem): string`

---

## Complexity Tracking

| Violação | Por que é necessária | Alternativa mais simples rejeitada porque |
|---|---|---|
| Nenhuma | N/A | N/A |

---

## Phases & Deliverables

- **Phase 0: Research & Setup**:
  - Diagnóstico e decisões arquiteturais consolidados em `research.md`.
- **Phase 1: Design & Contracts**:
  - Modelos de dados e máquinas de estado em `data-model.md`.
  - Contratos de componentes e API em `contracts/highlights-library-contract.md`.
  - Roteiro de validação em `quickstart.md`.
- **Phase 2: Tasks Decomposing**:
  - Decomposição em tarefas atômicas via `/speckit-tasks`.
