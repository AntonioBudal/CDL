# Implementation Plan: F0.8.01 — Curadoria Editorial, Biblioteca Ativa e Novo Header Global

**Branch**: `065-livros-header` | **Date**: 2026-10-10 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/065-livros-header/spec.md`

---

## Summary

Refinar a arquitetura do cabeçalho global do sistema (*App Shell*) e a página de Livros (`/livros`) resolvendo a fragmentação visual, o efeito "blocos de lego" e a assimetria:
1. **Centralização Matemática da Barra de Navegação**:
   - Transição do container do cabeçalho para **CSS Grid** de 3 colunas (`1fr auto 1fr`), garantindo que o bloco central de abas fique rigorosamente centralizado na viewport, independente da assimetria entre o logotipo à esquerda e as ferramentas à direita.
2. **Despoluição e Hierarquia de Atenção das Ferramentas da Direita**:
   - **Busca**: Pílula minimalista com fundo translúcido sutil (`--color-surface-soft`), ícone de lupa e rótulo 'Buscar' — **removendo o badge textual `Ctrl K`** da interface.
   - **Sincronização**: Componente `SyncStatusBadge` simplificado para exibir **estritamente um ícone pequeno** com cor semântica e tooltip explicativo, eliminando caixas escuras, bordas retangulares pesadas e textos.
   - **Captura Rápida**: Ação primária do cabeçalho concentrada em um botão elegante arredondado contendo **apenas o `+`**, com destaque de contraste primário intencional e tooltip com atalho `Ctrl+Shift+C`.
   - **Sininho e Avatar**: Ícones limpos sobre superfície transparente, sem caixas de botão duro.
   - **Dropdown do Usuário**: Menu suspenso agrupando perfil, ajustes rápidos e a ação de Sair da conta (eliminando o botão solto `Sair`).
3. **Harmonização do Gatilho "Mais ▾"**:
   - Alinhamento estético absoluto com as abas principais (`Livros`, `Destaques`, `Revisão`, `Inbox`), com fundo transparente, mesma tipografia e diferenciando-se apenas pela seta sutil `▾`.
4. **Mesa Curatorial de Livros (Largura Total)**:
   - Extinção imediata da coluna lateral estática de cadastro (35% da tela).
   - Hero "Lendo Agora" destacando a obra mais recente no topo.
   - Estante fluida em largura total com acabamento editorial e animação suave nas capas.
   - Drawer lateral deslizante (`Drawer.vue`, 420px desktop, 100% mobile) disparado por "+ Adicionar Livro", com foco retido e fechamento via `Esc` e backdrop.

---

## Technical Context

**Language/Version**: TypeScript 5.9+ / Node.js 20+ (Frontend) e Python 3.13 (Backend)

**Primary Dependencies**:
- Frontend: Vue 3 (Composition API, `<script setup>`), Vite, Tailwind CSS / tokens nativos
- Backend: FastAPI, SQLAlchemy 2.0 (sem alterações necessárias no backend)

**Storage**: SQLite 3 local com modo WAL (sem alteração no schema)

**Testing**:
- Frontend: `node:test` e `node:assert/strict` via `npm test`
- Build: `npm run build` (`vue-tsc -b && vite build`)
- Backend: `python -m pytest`

**Target Platform**: Windows local (processo único `iniciar.py`) atendendo PC e dispositivos móveis

**Project Type**: Web application local-first (Vue 3 SPA)

**Performance Goals**:
- Centralização sem reflows via CSS Grid nativo
- Transição do Drawer em $\le 220$ms com aceleração GPU (`transform`) a 60 FPS estáveis
- Backdrop suave em $\le 200$ms (`opacity`)
- Hover nas capas de livro em $\le 150$ms
- Comportamento instantâneo (0.01ms) sob `prefers-reduced-motion: reduce`

**Constraints**:
- Imunidade cromática absoluta: consumir exclusivamente as variáveis CSS dos 10 temas existentes (`--color-surface`, `--color-page`, `--color-text`, `--color-border`, etc.)
- Ausência total de cores hexadecimais fixas nos novos estilos
- Ausência total de emojis no frontend (usar ícones SVG do `Icon.vue`)
- Alvos de toque $\ge 44 \times 44$px para resoluções móveis
- Fechamento do Drawer via `Esc`, botão fechar e clique no backdrop
- Foco automático no primeiro campo ao abrir o Drawer e retorno ao botão disparador ao fechar

---

## Constitution Check

| Princípio | Status | Justificativa / Verificação |
|---|---|---|
| **I. Proteção do Acervo e Privacidade** | APROVADO | O redesign preserva 100% dos dados dos livros e não expõe nenhum conteúdo privado de produção. |
| **II. Isolamento Estrito de Testes** | APROVADO | Testes executados exclusivamente na suíte frontend (`npm test`) com mocks e componentes isolados. Nenhuma leitura ou escrita em `caderno.db`. |
| **III. Fidelidade Arquitetural** | APROVADO | Stack oficial mantida (Vue 3, TypeScript estrito, Vite). Não adiciona dependências externas ou bibliotecas pesadas de UI. |
| **IV. Spec-Driven Development (SDD)** | APROVADO | Ciclo de especificação e planejamento formal respeitado antes da implementação. |
| **V. Resiliência e Integridade** | APROVADO | Não há alterações no banco de dados SQLite ou migrações Alembic necessárias. |

---

## Architecture & Component Breakdown

### 1. `GlobalHeader.vue`
- Layout: `.header-inner` atualizado de flexbox para `display: grid; grid-template-columns: 1fr auto 1fr;`.
  - `.header-left`: `justify-self: start;` (Marca).
  - `.header-center`: `justify-self: center;` (Abas centrais perfeitamente centradas).
  - `.header-right`: `justify-self: end;` (Ferramentas e Perfil).
- Busca:
  - Botão `.search-trigger-btn` sem o `<kbd>Ctrl K</kbd>`, exibindo apenas ícone de busca e texto `Buscar` em pílula translúcida suave.
- Captura:
  - Botão `.quick-capture-trigger-btn` contendo **apenas o `+`** (`<Icon name="plus" :size="18" :stroke-width="2.5" />`), circular/arredondado, destaque primário tátil.
- Sincronização:
  - `<SyncStatusBadge />` integrado de forma minimalista.

### 2. `SyncStatusBadge.vue`
- Removidos os spans de texto (`.badge-text-full` e `.badge-text-short`).
- Estilo atualizado para ícone circular compacto sobre fundo transparente:
  - `background: transparent; border: none; padding: 6px; width: 32px; height: 32px;`
  - Feedback cromático suave por cor do ícone (`status-syncing`, `status-offline`, `status-conflict`, etc.).
  - Tooltip informativo completo via atributos `title` e `aria-label`.

### 3. `NavigationTabs.vue`
- Abas primárias (`Livros`, `Destaques`, `Revisão`, `Inbox`) e o gatilho `Mais ▾`:
  - Fundo transparente compartilhado.
  - Mesma tipografia, espaçamento e estados de hover/ativo.
  - Dropdown do menu retrátil suspenso com cantos suaves e sombra de profundidade temática.

### 4. `UserDropdown.vue`
- Pílula de usuário com iniciais (`AN`) e nome do leitor.
- Menu suspenso com perfil, atalhos de ajustes e botão de logout encapsulado com confirmação.

### 5. `BooksView.vue` & `BookHeroCard.vue`
- Layout em largura total (removido painel lateral estático).
- Hero Card "Lendo Agora" no topo destacando a obra mais recente.
- Grade fluida de livros com animações suaves de hover.
- Botão "+ Adicionar Livro" no topo abrindo o `Drawer.vue`.

### 6. `Drawer.vue`
- Gaveta lateral acessível de 420px (100% mobile) com foco retido, `role="dialog"`, `aria-modal="true"` e fechamento por `Esc` e clique no backdrop.

---

## Tasks & Phases

- **Phase 1 (Header Refinement)**:
  - Atualizar `GlobalHeader.vue`: layout CSS Grid (`1fr auto 1fr`), remoção do badge `Ctrl K`, botão de captura contendo apenas `+`.
  - Atualizar `SyncStatusBadge.vue`: renderizar apenas o ícone pequeno discreto com tooltip, sem textos ou fundos pesados.
  - Atualizar `NavigationTabs.vue`: garantir paridade visual idêntica entre as abas e o gatilho `Mais ▾`.
- **Phase 2 (Library & Drawer)**:
  - Validar largura total de `BooksView.vue` e integração de `BookHeroCard.vue`.
  - Validar funcionamento do `Drawer.vue` para criação de livros.
- **Phase 3 (Verification & Tests)**:
  - Atualizar suíte de testes `feature-065-livros-header.test.mjs` para validar:
    - Centralização via CSS Grid em `GlobalHeader.vue`.
    - Ausência de `Ctrl K` visível no botão de busca.
    - Captura rápida exibindo apenas o `+`.
    - `SyncStatusBadge` minimalista com apenas o ícone.
  - Executar `npm test` e `npm run build`.
