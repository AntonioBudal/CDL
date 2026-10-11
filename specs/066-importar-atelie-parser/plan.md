# Implementation Plan: F0.8.05 — Ateliê de Fichamento e Parser Estruturado

**Branch**: `066-importar-atelie-parser` | **Date**: 2026-10-11 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/066-importar-atelie-parser/spec.md`

---

## Summary

O Roadmap 0.8 / Feature 05 transforma a tela `/importar` de um formulário transacional monolítico em um ambiente de ateliê de duas colunas sincronizadas (*Two-Pane Studio*):
1. **Faixa Superior Compacta**: Metadados essenciais de Livro (obrigatório), Capítulo (obrigatório), Página/Localização (opcional), Título (opcional) e botão de ação primária dispostos em uma barra horizontal unificada no topo, liberando mais de 80% da altura da viewport.
2. **Editor da Fonte Bruta (Painel Esquerdo)**: Editor de escrita com contadores de palavras e caracteres, botão manual de acionamento do parser e indicador discreto de estado desatualizado (*stale*).
3. **Prévia Estruturada Viva (Painel Direito)**: Cards dedicados às quatro seções semânticas do fichamento (*Resumo*, *Explicação*, *Conceitos-chave*, *Referências/Citações*), bloco de Conteúdo Não Classificado com botões de 1 clique para alocação rápida e pulso luminoso (`section-pulse`) ao detectar quebras de seção.
4. **Barra de Ferramentas Flutuante Contextual**: Substituição da barra fixa cinza por uma barra contextual suspensa sobre o texto selecionado (Negrito, Itálico, H3, Tabela, Código, Link), com atalhos de teclado (`Ctrl+B`, `Ctrl+I`, `Ctrl+K`) e fallback acessível no rodapé.
5. **Modos de Foco & Responsividade**: Alternância de modos (*Dividido 50/50*, *Apenas Fonte 100%*, *Apenas Prévia 100%*) com transição suave em até 180ms e conversão automática em abas segmentadas para telas menores (< 1024px).

---

## Technical Context

**Language/Version**: TypeScript 5.9+ / Node.js 20+ (Frontend) e Python 3.13 (Backend)

**Primary Dependencies**:
- Frontend: Vue 3 (Composition API, `<script setup>`), Vite, Tailwind CSS / tokens semânticos nativos, composable `useImportDraft`, `useUnsavedChanges`, utilitário `markdownFormatter.ts`
- Backend: FastAPI, SQLAlchemy 2.0 (sem alterações de backend necessárias)

**Storage**: SQLite 3 local em modo WAL (sem alteração de schema ou migrações)

**Testing**:
- Frontend: `node:test` e `node:assert/strict` via `npm test`
- Build & Tipagem: `npm run build` (`vue-tsc -b && vite build`)
- Backend: `python -m pytest`

**Target Platform**: Windows local (processo único `iniciar.py`) atendendo PC, tablets e dispositivos móveis via rede privada

**Project Type**: Web application local-first (Vue 3 SPA)

**Performance Goals**:
- Latência de digitação inferior a 50ms (debounce de 300ms no recálculo da prévia)
- Transição suave entre modos de visualização em $\le 180$ms acelerada por GPU a 60 FPS
- Suporte imediato (0.01ms) sob `prefers-reduced-motion: reduce`

**Constraints**:
- Imunidade cromática total: consumo exclusivo dos tokens semânticos dos 10 temas nativos
- Proibição estrita de emojis no frontend (utilizar catálogo vetorial SVG `Icon.vue`)
- Touch targets $\ge 44 \times 44$px para resoluções táteis
- Preservação funcional integral dos endpoints de importação (`/api/studies/preview`, `/api/studies`) e promoção do Inbox (`/api/inbox/{id}/promote`)

---

## Constitution Check

| Princípio | Status | Justificativa / Verificação |
|---|---|---|
| **I. Proteção do Acervo e Privacidade** | APROVADO | O redesenho preserva 100% dos dados dos livros, capítulos e notas; testes utilizam dados sintéticos em memória sem expor dados privados. |
| **II. Isolamento Estrito de Testes** | APROVADO | Suítes de teste utilizam mocks isolados e `tmp_path`, sem qualquer leitura ou gravação em `caderno.db`. |
| **III. Fidelidade Arquitetural** | APROVADO | Stack oficial mantida (Vue 3, TypeScript estrito, FastAPI, SQLAlchemy 2). Nenhuma biblioteca externa ou dependência pesada adicionada. |
| **IV. Spec-Driven Development (SDD)** | APROVADO | O fluxo segue a ordem canônica do Roadmap 0.8, com especificação e planejamento formais antes da implementação. |
| **V. Resiliência e Integridade** | APROVADO | Não há alterações no banco de dados SQLite ou migrações Alembic necessárias. |

---

## Architecture & Component Breakdown

### 1. `ImportView.vue` (Visualização Principal)
- **Faixa Superior Compacta (`.import-metadata-bar`)**:
  - Seletores compactos inline de Livro (`<select>`) e Capítulo (`<select>`).
  - Inputs opcionais de Localização e Título do estudo.
  - Ação primária de salvar integrada à extremidade direita da faixa.
- **Contêiner Mestre do Ateliê (`.import-studio-container`)**:
  - Modos de visualização aplicados via classe CSS dinâmica: `.studio-split`, `.studio-source-only`, `.studio-preview-only`.
  - Painel Esquerdo (`.studio-editor-pane`): textarea da fonte bruta, contador de palavras/caracteres, botão manual de análise e indicador de *stale*.
  - Painel Direito (`.studio-preview-pane`): 4 cards de seções estruturadas, card de conteúdo não classificado com botões de 1 clique, e painel de alertas da análise.
- **Abas Responsivas (< 1024px)**:
  - Navegação segmentada móvel: `[Texto da Fonte]` e `[Prévia Estruturada]`.

### 2. `FloatingMarkdownToolbar.vue` (Novo Componente)
- **Posicionamento Contextual**: Ancorada próxima à seleção ativa ou flutuante no topo do editor.
- **Ações**: Negrito (`bold`), Itálico (`italic`), Título H3 (`heading`), Tabela (`table`), Bloco de Código (`code`) e Link (`link`).
- **Comportamento**: Exibição automática na seleção (`select`/`mouseup`), desaparece com `Esc` ou desmarcação.

### 3. `StudioViewModeToggle.vue` (Novo Componente)
- Controle segmentado tátil no topo do ateliê para alternar entre:
  - `split` (50% / 50%)
  - `source` (100% Editor)
  - `preview` (100% Prévia)

### 4. `markdownFormatter.ts` (Utilitário Compartilhado)
- Expansão da função `applyMarkdownAction` para suportar a ação `table` (inserção de tabela Markdown com cabeçalho e linhas base).

### 5. `style.css` (Regras de Layout do Ateliê)
- Classes de layout `two-pane`, animação `@keyframes section-pulse` e regras de `prefers-reduced-motion`.

---

## Phases & Deliverables

- **Phase 0: Research & Setup**:
  - Consolidar decisões técnicas em `research.md`.
  - Definir modelos em `data-model.md` e contratos em `contracts/import-studio-ui.yaml`.
  - Elaborar guia de validação em `quickstart.md`.
- **Phase 1: Componentes Reutilizáveis & Utilitários**:
  - Implementar ação `table` em `markdownFormatter.ts`.
  - Criar `StudioViewModeToggle.vue` e `FloatingMarkdownToolbar.vue`.
  - Definir classes de animação e pulso em `style.css`.
- **Phase 2: Ateliê Two-Pane Studio (`ImportView.vue`)**:
  - Refatorar faixa superior para cabeçalho horizontal compacto.
  - Estruturar os dois painéis lado a lado com integração da barra flutuante.
  - Implementar cards estruturados das 4 seções com botões de atribuição de 1 clique.
  - Adicionar pulso luminoso na detecção estrutural e debounce de 300ms.
- **Phase 3: Responsividade, Promoção de Inbox e Acessibilidade**:
  - Abas segmentadas para viewports < 1024px.
  - Preservação do banner de promoção de capturas do Inbox (`promote_inbox_id`).
  - Conformidade total com os 10 temas nativos e zero emojis.
- **Phase 4: Validação & Testes**:
  - Criar e executar suíte de testes `feature-066-importar-atelie-parser.test.mjs`.
  - Executar `npm test`, `npm run build` e `python -m pytest`.
