# Pesquisa e Auditoria de Responsividade — Feature 076

**Feature**: `076-estrategia-responsiva`  
**Status**: Validação e Consolidação da Auditoria Estática  
**Data Base**: 11/10/2026

---

## 1. Diagnóstico do Projeto e Arquitetura

### 1.1 Stack Técnica e Sistema de Estilos
- **Backend**: FastAPI, SQLite em modo WAL (Python 3.13), Uvicorn.
- **Frontend**: Vue 3 (Composition API com `<script setup>`), TypeScript, Vite 8.
- **CSS**: Arquitetura autoral sem Tailwind ou bibliotecas de UI de terceiros. 10 folhas de estilo globais carregadas no `index.html` complementadas por estilos `<style scoped>` por componente.
- **Dependências de Visualização**: Implementação própria e soberana para Map View, Canvas View e Tree View.

### 1.2 Mapeamento de Rotas
Foram mapeadas as 25 rotas canônicas registradas em `caderno-leitura-0.1/frontend/src/router/index.ts`:
1. `landing` (`/`)
2. `about` (`/sobre`)
3. `support` (`/apoie`, `/apoiar`)
4. `login` (`/login`)
5. `register` (`/registro`)
6. `first-access` (`/primeiro-acesso`)
7. `not-found` (`/:pathMatch(.*)*`)
8. `dashboard` (`/dashboard`)
9. `books` (`/livros`, `/books`)
10. `book` (`/livros/:id`)
11. `study` (`/livros/:bookId/estudos/:studyId`)
12. `study-edit` (`/livros/:bookId/estudos/:studyId/editar`)
13. `study-session` (`/estudo/sessao/:sessionId`)
14. `highlights-library` (`/highlights`, `/destaques`)
15. `review-hub` (`/review`, `/revisao`)
16. `inbox` (`/inbox`, `/capturas`)
17. `friends` (`/amigos`, `/conexoes`)
18. `user-profile` (`/@:username`)
19. `settings` (`/ajustes`)
20. `trash` (`/lixeira`)
21. `connection` (`/conexao`)
22. `digitize` (`/digitalizar`)
23. `import` (`/importar`)
24. `admin` (`/admin`)
25. `shared-study` (`/compartilhado/:token`)

---

## 2. Inventário de Problemas: Diagnóstico e Status de Validação (P-01 a P-19)

| ID | Gravidade | Confiança Inicial | Status de Validação | Descrição e Diagnóstico | Evidência e Rastreabilidade |
|---|---|---|---|---|---|
| **P-01** | Crítica | A (Confirmado) | **CONFIRMADO** | Barra inferior móvel órfã. Em telas `<768px`, as abas principais com rótulo acumulam-se no cabeçalho superior. `#app` reserva `padding-bottom` para uma barra que não renderiza. | `mobile-navigation.css:195` estiliza `.main-nav`, mas `NavigationTabs.vue` usa `.navigation-tabs`. Destino: **Feature 077**. |
| **P-02** | Alta | A (Confirmado) | **CONFIRMADO** | Falsa aprovação em testes de navegação móvel. Testes unitários checavam presença de regras CSS como strings isoladas sem garantir correspondência com seletores nos templates. | `tests/mobile_navigation_contrast.test.mjs`. Destino: **Feature 077**. |
| **P-03** | Alta | A (Confirmado) | **CONFIRMADO** | `ShareModal.vue` depende exclusivamente de classes de utilitário Tailwind (`fixed inset-0 z-50 flex items-center...`), inexistentes no projeto. | `components/sharing/ShareModal.vue`. Modal renderiza desestruturado em qualquer viewport. Destino: **Feature 077**. |
| **P-04** | Alta | A (Confirmado) | **CONFIRMADO** | Map View: pan e zoom exclusivos para mouse (`mousedown`, `mousemove`, `wheel`). Em viewport de 375px, nós nos anéis radiais ($R=165$ e $265$) ficam inacessíveis por toque. | `StudyMapView.vue:462`, CSS `.map-world-content` fixo em 800×560. Destino: **Feature 079**. |
| **P-05** | Média | A (Confirmado) | **CONFIRMADO** | Map View: dica textual "Duplo clique no canvas..." exibida em smartphone. Badges de aresta SVG (72×20px) são alvos difíceis para toque móvel. | `StudyMapView.vue:440, 640`. Destino: **Feature 079**. |
| **P-06** | Alta | A/M | **CONFIRMADO** | Canvas View: `touch-action: none` em palco de 680px prende a rolagem da página no celular. Ausência de manipulação de gestos de dois pontos (pinch) e alças de redimensionamento pequenas. | `StudyCanvasView.vue`, `useCanvasViewport.ts`. Destino: **Feature 079**. |
| **P-07** | Média | A (Confirmado) | **CONFIRMADO** | Canvas View: toolbar horizontal com mais de 10 botões sem indicador visual de rolagem horizontal em telas estreitas. | `CanvasToolbar.vue:184, 330`. Destino: **Feature 079**. |
| **P-08** | Média | A/H | **CONFIRMADO** | Tree View: arrasto HTML5 inoperante via toque. Ocultamento da alça apenas por `@media (max-width: 768px)` exibe alça inoperante em tablets com tela de toque grande. | `StudyTreeNodeItem.vue:110, 654`. Destino: **Feature 079**. |
| **P-09** | Média | M (Inferência) | **CONFIRMADO** | `NotificationsDropdown` com largura fixa de 360px ancorado à direita projeta-se além da borda esquerda da viewport em larguras ≤ 390px. | `NotificationsDropdown.vue:143`. Destino: **Feature 077**. |
| **P-10** | Média | A (Confirmado) | **CONFIRMADO** | Elementos fixos no rodapé (toasts, lote da lixeira, FAB de preview) ignoram a altura da barra móvel (`--mobile-nav-offset`), gerando sobreposição quando a barra estiver ativa. | Varredura de `position: fixed; bottom: ...`. Destino: **Feature 077**. |
| **P-11** | Média | A (Confirmado) | **CONFIRMADO** | Inconsistência de fronteira entre `max-width: 767px` e `max-width: 768px` gerando comportamento ambíguo em exatamente 768px. | Histograma de `@media`. Destino: **Feature 076 / 077–079**. |
| **P-12** | Média | M (Inferência) | **CONFIRMADO** | Palco dentro de `SplitPane#main` redimensionável não reflete a viewport da janela; media queries baseadas em viewport falham quando painéis laterais estão abertos. | `SplitLayout.vue`. Destino: **Features 078 e 079**. |
| **P-13** | Baixa | A (Confirmado) | **CONFIRMADO** | CSS morto no shell: `App.vue` retém estilos legados de cabeçalho que não casam com `GlobalHeader.vue`. `style.css` duplica regras de `.header-inner`. | `App.vue:150-390`, `style.css:104-110`. Destino: **Feature 077**. |
| **P-14** | Média | A (Confirmado) | **CONFIRMADO** | Tabela de usuários em `/admin` (`AdminUsersTable`) tem 8 colunas e rolagem horizontal, inviabilizando ações rápidas de moderação no celular. | `AdminUsersTable.vue:47, 230`. Destino: **Feature 078**. |
| **P-15** | Baixa | H (Hipótese) | **CONFIRMADO** | Grids com `grid-template-columns: repeat(auto-fill, minmax(280px, 1fr))` provocam estouro lateral em telas de 320px com padding lateral. | `FriendsView.vue:756`, `AdminView.vue:1270`. Destino: **Feature 078**. |
| **P-16** | Média | H (Hipótese) | **CONFIRMADO** | Modais com formulários usam `height: 85vh`, cobrindo botões de ação e campos ao abrir o teclado virtual do sistema operacional móvel. | Varredura de modais. Destino: **Feature 078**. |
| **P-17** | Média | H (Hipótese) | **CONFIRMADO** | `BookView`: estado `leftCollapsed` inicializado como `false` faz com que o primeiro acesso mobile abra cobrindo o conteúdo de estudos com a gaveta de capítulos. | `useSplitPanes.ts:116`, `BookView.vue`. Destino: **Feature 078**. |
| **P-18** | Baixa | A (Confirmado) | **CONFIRMADO** | Efeitos de transformação aplicados em `:hover` permanecem congelados após o primeiro toque do usuário em telas sensíveis ao toque. | Ausência de `@media (hover: hover)`. Destino: **Feature 078**. |
| **P-19** | Informativa | A (Confirmado) | **RATIFICADO** | Ausência de infraestrutura automatizada de testes de renderização gráfica no pipeline CI/local. | Decisão ratificada em FR-007. Destino: **Feature 076 / 080**. |

---

## 3. Confirmação Técnica da Pertinência Estudo↔Moldura no Canvas

Em `caderno-leitura-0.1/frontend/src/composables/useCanvasFrames.ts`:
- A pertinência de um estudo em relação a uma moldura (`moveFrameSolidary`) é calculada puramente por inclusão geométrica delimitadora no cliente ($x_{estudo} \ge x_{moldura}$ e $y_{estudo} \ge y_{moldura}$ dentro das dimensões da moldura).
- **Conclusão**: A alternativa móvel da visualização em Canvas (outline de estudos agrupados por moldura) pode ser computada 100% no cliente sem requisições ou alterações de schema no backend.
