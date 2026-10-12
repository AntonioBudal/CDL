# Briefing de Auditoria de Responsividade — Features F0.8.11 a F0.8.15

Documento de transição e diagnóstico da suite de responsividade para o Caderno de Leitura / Leitorum.
Preparado a partir da Auditoria Estática de Responsividade (11/10/2026).

---

## Parte A — Diagnóstico do Projeto

### Arquitetura
A aplicação fica em `caderno-leitura-0.1/`:
- **Backend**: FastAPI + SQLite (modo WAL, Python 3.13).
- **Frontend**: Vue 3 (`<script setup>`, TypeScript, Vite 8).
- **Estilos**: CSS autoral: 10 folhas globais conectadas em `index.html` mais `<style scoped>` por componente.
- **Dependências de runtime**: `vue`, `vue-router`, `markdown-it`, `markdown-it-mark`, `lucide-vue-next` e fonte Geist.
- Não há biblioteca externa de mapas, grafos, canvas ou árvore; as três visualizações complexas são implementação própria.

### Spec Kit
- Versão 1.0.1, integração `agy`, scripts PowerShell, numeração sequencial.
- Próxima pasta livre: `specs/076-estrategia-responsiva`.
- Cada spec segue o padrão `spec.md`, `plan.md`, `research.md`, `data-model.md`, `quickstart.md`, `tasks.md`, `contracts/`, `checklists/requirements.md`.

### Rotas
São 25 rotas em `router/index.ts`: 7 públicas, 17 autenticadas e 1 de administração. `/estudo/sessao/:id` usa `meta.cleanScreen` (sem header nem footer).

### Shell Compartilhado
- `App.vue` monta `GlobalHeader`, `main.workspace`, footer, `GlobalSearchModal`, `QuickCaptureModal` e `MobileMoreMenu`.
- `GlobalHeader` contém `NavigationTabs` (4 abas + dropdown "Mais"), `SyncStatusBadge`, busca, captura, `NotificationsDropdown`, `UserDropdown` e gatilho móvel.
- `SplitLayout` (usado em `BookView`) alterna por JS entre split (≥1024), drawer (768–1023) e mobile (<768).
- `ui/Drawer.vue` e `ui/DropdownMenu.vue` existem no catálogo base.

### Responsividade Atual
- 15 larguras de breakpoint identificadas. Dominantes: 640px e 768px (além de convívio com 767px).
- JS usa limites `<768` e `<1024`.
- Quase nenhuma container query e apenas um `@media (pointer: coarse)`.
- `viewport-fit=cover` e `env(safe-area-inset-*)` já presentes.
- 60 componentes fluidos por construção (`width: 100%` + `max-width`).

---

## Parte B — Matriz de Problemas (P-01 a P-19)

| ID | Gravidade | Confiança | Problema | Evidência |
|---|---|---|---|---|
| **P-01** | Crítica | Confirmado | Barra inferior móvel órfã. Em <768px as abas ficam comprimidas no header. `#app` ainda reserva padding-bottom para a barra inexistente. | `mobile-navigation.css:195` mira `.main-nav`; `NavigationTabs.vue` usa `.navigation-tabs`. |
| **P-02** | Alta | Confirmado | Testes de navegação móvel passam mesmo com a barra quebrada, pois verificavam apenas declarações CSS estáticas. | `tests/mobile_navigation_contrast.test.mjs` |
| **P-03** | Alta | Confirmado | `ShareModal` depende de utilitários Tailwind que não existem no projeto. | `components/sharing/ShareModal.vue` |
| **P-04** | Alta | Confirmado | Map View: pan e zoom apenas por mouse. Mundo fixo em 800×560 centrado. Em 375px nós dos anéis ficam fora de tela. | `StudyMapView.vue:462`, CSS `.map-world-content` |
| **P-05** | Média | Confirmado | Map View: dica de duplo clique exibida em celular. Badges de aresta muito pequenos para toque. | `StudyMapView.vue:440, 640` |
| **P-06** | Alta | Confirmado/Inferência | Canvas: `touch-action: none` em palco de 680px. No celular prende a rolagem e não há pinch-to-zoom de toque. | `StudyCanvasView.vue`, `useCanvasViewport.ts` |
| **P-07** | Média | Confirmado | Canvas: toolbar com cerca de 12 botões sem indicação de rolagem horizontal no mobile. | `CanvasToolbar.vue:184, 330` |
| **P-08** | Média | Confirmado/Hipótese | Tree View: arrastar-e-soltar HTML5 inoperante por toque; alça aparece em tablets com toque. | `StudyTreeNodeItem.vue:110, 654` |
| **P-09** | Média | Inferência | `NotificationsDropdown` estoura borda esquerda em telas ≤430px. | `NotificationsDropdown.vue:143` |
| **P-10** | Média | Confirmado | Elementos fixos inferiores ignoram `--mobile-nav-offset` (toasts, batch bar da lixeira, FAB de ajustes). | Varredura de `position: fixed; bottom: ...` |
| **P-11** | Média | Confirmado | Breakpoints inconsistentes (fronteira 767px vs 768px). | Histograma de `@media` |
| **P-12** | Média | Inferência | Visualizações dentro de `SplitPane#main` sofrem restrição de largura que não reflete a viewport. | `SplitLayout.vue`, `StudyMapView.vue` |
| **P-13** | Baixa | Confirmado | CSS morto ou duplicado no shell em `App.vue` e `style.css`. | `App.vue`, `style.css:104-110` |
| **P-14** | Média | Confirmado | `AdminUsersTable` tem 8 colunas com overflow horizontal e sem cards adaptativos. | `AdminUsersTable.vue:47, 230` |
| **P-15** | Baixa | Hipótese | Grids `minmax(280px, 1fr)` podem estourar telas de 320px. | `FriendsView.vue:756`, `AdminView.vue:1270` |
| **P-16** | Média | Hipótese | Modais usando `vh` em vez de `dvh` e sem blindagem para teclado virtual móvel. | Varredura de `vh` em modais |
| **P-17** | Média | Hipótese | `BookView` com gaveta de capítulos aberta por padrão no mobile cobrindo a tela. | `useSplitPanes.ts:116`, `BookView.vue` |
| **P-18** | Baixa | Confirmado | Falta de proteção `@media (hover: hover)` prendendo efeito hover após toque. | Varredura de transform em `:hover` |
| **P-19** | Informativa | Confirmado | Ausência de testes de renderização em navegador real. | `package.json` |

---

## Parte C — Estratégia por Tela e Visualização

### 1. Shell (Header + Barra Inferior)
- Restaurar a barra inferior móvel fixa (`MobileTabBar` / `.navigation-tabs` adaptada) com 4 destinos primários + gaveta "Mais" (spec 038).
- Header móvel compacto contendo apenas marca, busca, captura, notificações e perfil.
- Subir gaveta "Mais" com todos os destinos secundários (incluindo Importar e Amigos com badges).

### 2. Map View (Grafo Conceitual Radial)
- **Classificação**: Versão móvel simplificada.
- Apresentação padrão em `<768px`: Lista semântica de conexões (núcleo em destaque, estudos por anel, lista de relações e grau).
- Alternador "Lista | Grafo" para panorama tátil com pan e pinch sem bloquear rolagem da página.
- Toque assistido mantido para criar/editar relações; bottom sheet para popovers.

### 3. Canvas View (Quadro Espacial)
- **Classificação**: Desktop com alternativa móvel.
- Em `<768px`: Aba exibe aviso orientador e lista estruturada por molduras (estudos em cada moldura e avulsos), permitindo leitura e abertura direta sem manipulação espacial restrita.
- Em `768–1023px` (tablet): Canvas completo com suporte tátil (pinch-zoom, ferramenta explícita de seleção em bloco, alças de 44px em `pointer: coarse`).

### 4. Tree View (Hierarquia de Estudos)
- **Classificação**: Reorganização leve.
- Manter a árvore viva; reduzir indentação por nível com `clamp()`.
- Lixeira e "Ler" agrupados no menu de ações da linha em telas estreitas.
- Título permitindo 2 linhas sem truncar prematuramente.
- Alça de arrasto oculta em `@media (pointer: coarse)`.

### 5. Telas Tradicionais e Overlays
- **BookView**: Capítulos em gaveta fechada por padrão no mobile; ações secundárias recolhidas em menu de contexto.
- **Admin**: Tabela convertida em cards adaptativos em telas estreitas.
- **Modais**: Migração para `dvh` e proteção de formulários com foco.
- **ShareModal**: Reescrita sem classes Tailwind, utilizando os tokens canônicos do sistema.

---

## Parte D — Sequenciamento das 5 Features

1. **Feature 076 (`specs/076-estrategia-responsiva`) — F0.8.11**:
   - Validação da auditoria, ratificação das decisões, contrato de breakpoints e padrões, protocolo de validação com banco descartável, teste-guarda de inventário.
   - Zero alterações em código de produção (`frontend/src` ou `backend/app`).
2. **Feature 077 (`specs/077-shell-navegacao-movel`) — F0.8.12**:
   - Barra inferior restaurada, header móvel limpo, gaveta "Mais", offsets de elementos fixos, painel de notificações, ShareModal com tokens nativos, limpeza de CSS morto do shell.
3. **Feature 078 (`specs/078-conteudo-responsivo`) — F0.8.13**:
   - BookView (gaveta fechada e menu de ações), Admin em cards, grids em 320px, modais com `dvh`, proteções de hover e container queries.
4. **Feature 079 (`specs/079-visualizacoes-moveis`) — F0.8.14**:
   - Map híbrido (lista + panorama tátil), Canvas (outline móvel + toque em tablet), refinamentos da Tree View.
5. **Feature 080 (`specs/080-regressao-responsiva`) — F0.8.15**:
   - Bateria completa de regressão em matriz rota × viewport, documentação consolidada e encerramento do roadmap de responsividade.
