# Pesquisa Técnica: Visualizações Móveis e Responsividade de Destaques

**Feature**: `080-visualizacoes-e-destaques-moveis`  
**Data**: 2026-10-12  
**Status**: Concluído  

---

## 1. Responsividade da Biblioteca de Destaques (`HighlightsLibraryView.vue`)

### Problema 1: Transbordamento Horizontal da Página (`scrollWidth > clientWidth`)
- **Causa Raiz**: O componente `HighlightFilterToolbar.vue` declara `.toolbar-primary-row { display: flex; align-items: center; gap: 1rem; width: 100%; }` sem `flex-wrap: wrap`. Em viewports $\le 767\text{px}$, a soma do campo de busca (`min-width: 220px`), do alternador de modo (`view-mode-toggle`, ~140px) e do botão de filtros (`btn-mobile-filter-toggle`, ~90px) mais os gaps excede 480px, estourando as larguras de tela de 320px a 430px.
- **Decisão**:
  1. Em `@media (max-width: 767px)`, aplicar `.toolbar-primary-row { flex-wrap: wrap; gap: 0.75rem; }`.
  2. O `.search-input-wrapper` passa a ter `width: 100%; min-width: 0; flex: 1 1 100%;`, ocupando a primeira linha integralmente.
  3. A segunda linha agrupa o alternador de modo (`.view-mode-toggle { flex: 1 1 auto; min-width: 0; }`) e o gatilho de filtros móvel (`.btn-mobile-filter-toggle { flex: 0 0 auto; min-height: 44px; }`).
  4. Garantir `max-width: 100%; box-sizing: border-box; overflow-x: hidden;` no container `.highlights-library-view`.
- **Alternativas Rejeitadas**:
  - Esconder o alternador de modo no mobile: Rejeitado porque a distinção entre "Recentes" e "Por Obra" é uma funcionalidade-chave de consulta de destaques.
  - Reduzir tamanho de fontes e ícones abaixo de 13px: Rejeitado por violação de ergonomia e acessibilidade.

### Problema 2: Desconfiguração e Sobreposição da Barra Inferior Móvel (`MobileTabBar`)
- **Causa Raiz**:
  1. O transbordamento horizontal da página provocava deslocamento e descolamento da barra inferior fixa (`position: fixed; inset: auto 0 0; width: 100%;`).
  2. O padding inferior de `.highlights-library-view` em telas $< 640\text{px}$ era fixado em míseros `2.5rem` (40px), inferior à altura física da `MobileTabBar` (56px + safe-area), cobrindo a paginação e o último card.
- **Decisão**:
  1. Fixar o espaçamento inferior no container com o token canônico: `padding-bottom: calc(var(--mobile-nav-offset, 56px) + 1.5rem);`.
  2. Ajustar a paginação (`.pagination-nav`) para `flex-wrap: wrap; justify-content: center; gap: 0.75rem;` com alvos mínimos de botão $\ge 44 \times 44\text{ px}$.
  3. Ajustar o micro-toast flutuante (`.study-micro-toast`) para usar `bottom: calc(var(--mobile-nav-offset, 56px) + 1rem);`.

---

## 2. Adaptação do Mapa de Estudos (`StudyMapView.vue`)

### Gestos Táteis de Pan e Pinch Zoom
- **Contexto**: O grafo radial implementa pan e zoom via eventos de mouse (`wheel`, `mousedown`, `mousemove`, `mouseup`).
- **Decisão**:
  1. Adicionar listeners para `touchstart`, `touchmove`, `touchend`, `touchcancel` na superfície SVG do mapa.
  2. Um toque (`touches.length === 1`): calcula deslocamento relativo delta ($dx, dy$) para arrasto (pan) com amortecimento suave.
  3. Dois toques (`touches.length === 2`): calcula distância euclidiana entre os dois pontos ($\sqrt{\Delta x^2 + \Delta y^2}$) e atualiza proporcionalmente o zoom entre 0.5x e 2.5x.
  4. Manter `touch-action: none` especificamente na viewport do mapa durante gestos de pinça, mas fornecer barra de controle explícita.
  5. Alternativa de exibição: em telas $\le 767\text{px}$, fornecer alternador "Grafo / Lista de Relações", permitindo que o usuário visualize e edite as conexões semânticas em uma lista tátil com botões $\ge 44 \times 44\text{ px}$.

---

## 3. Desbloqueio e Ergonomia do Canvas (`StudyCanvasView.vue`)

### Remoção do Bloqueio de Rolagem Vertical
- **Contexto**: A viewport do canvas de 680px utiliza `touch-action: none;`, capturando todos os gestos táteis e impedindo que o leitor no celular role a página para cima ou para baixo.
- **Decisão**:
  1. Em viewports móveis ($\le 767\text{px}$), ajustar `.canvas-viewport` para `touch-action: pan-y;` quando a ferramenta ativa for de seleção/leitura, permitindo rolagem vertical natural da página.
  2. Quando a ferramenta "Pan" for explicitamente acionada ou durante gestos com dois dedos, ativar pan bidimensional delimitado.
  3. Compactar a barra de ferramentas `CanvasToolbar.vue`: em $< 1024\text{px}$, agrupar ferramentas secundárias (molduras, alinhamento, reset) em menu suspenso ou gaveta colapsável.

---

## 4. Árvore de Estudos Móvel (`StudyTreeView.vue` e `StudyTreeNodeItem.vue`)

### Ações Táteis e Hierarquia Acessível
- **Contexto**: A árvore utiliza drag-and-drop de mouse para ordenar e aninhar nós, com alça de arrasto diminuta (`.tree-drag-handle`).
- **Decisão**:
  1. Sob `@media (pointer: coarse)`, ocultar a alça de arrasto `.tree-drag-handle`.
  2. Exibir de forma proeminente o menu contextual de ações de cada nó (`.mobile-menu-toggle-btn` com alvo $\ge 44 \times 44\text{ px}$).
  3. Assegurar que o dropdown inclua ações táteis inequívocas: "Mover para cima", "Mover para baixo", "Adicionar filho", "Excluir".
  4. Em telas compactas, aplicar compressão de indentação (máximo de 16px por nível a partir do 3º nível) para impedir que o conteúdo do card seja esmagado contra a margem direita.
