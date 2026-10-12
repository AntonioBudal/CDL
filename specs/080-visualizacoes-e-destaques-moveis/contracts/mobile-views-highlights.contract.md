# Contrato Técnico: Padrões de Visualizações Móveis e Responsividade de Destaques

**Feature**: `080-visualizacoes-e-destaques-moveis`  
**Escopo**: Definição normativa das regras de layout, gestos táteis e integridade da barra inferior móvel.

---

## 1. Contrato da Biblioteca de Destaques (`/destaques`)

### 1.1 Prevenção de Transbordamento Horizontal
Em viewports $\le 767\text{px}$:
- O container `.highlights-library-view` e `.library-container` devem declarar:
  ```css
  max-width: 100%;
  box-sizing: border-box;
  overflow-x: hidden;
  ```
- A linha primária da barra de ferramentas (`.toolbar-primary-row`) deve declarar:
  ```css
  flex-wrap: wrap;
  gap: 0.75rem;
  ```
- O campo de busca (`.search-input-wrapper`) deve expandir para largura total:
  ```css
  width: 100%;
  min-width: 0;
  flex: 1 1 100%;
  ```
- O alternador de modo (`.view-mode-toggle`) e o botão móvel de filtros (`.btn-mobile-filter-toggle`) devem dividir a segunda linha harmoniosamente, com alvos táteis mínimos de **$44 \times 44\text{ px}$**.

### 1.2 Integridade e Espaçamento da Barra Inferior (`MobileTabBar`)
- Em viewports $\le 767\text{px}$, a tela de destaques deve reservar espaço inferior utilizando o token canônico:
  ```css
  padding-bottom: calc(var(--mobile-nav-offset, 56px) + 1.5rem);
  ```
- A barra de paginação (`.pagination-nav`) deve permitir quebra de linha (`flex-wrap: wrap`) e centralização, garantindo que botões de página anterior/próxima e números de página tenham no mínimo **$44 \times 44\text{ px}$** e nunca colidam com a `MobileTabBar`.
- O micro-toast de confirmação de cópia (`.study-micro-toast`) deve flutuar acima da barra inferior utilizando:
  ```css
  bottom: calc(var(--mobile-nav-offset, 56px) + 1rem);
  ```

---

## 2. Contrato do Mapa de Estudos (`StudyMapView`)

### 2.1 Gestos Multitoque
- O palco interativo SVG deve responder a eventos de toque:
  - **1 toque (Arrasto/Pan)**: Translação contínua do grafo acompanhando o deslocamento do dedo.
  - **2 toques (Pinça/Pinch Zoom)**: Escala contínua do zoom baseada na variação da distância euclidiana, restrita ao intervalo canônico $[0.5, 2.5]$.

### 2.2 Lista Semântica Alternativa no Celular
- Em telas $\le 767\text{px}$, a interface deve oferecer alternância entre a representação gráfica radial e a lista estruturada de nós e relações semânticas.
- Todas as ações da lista (editar relação, inverter sentido, desvincular, abrir estudo) devem oferecer botões com alvos táteis mínimos de **$44 \times 44\text{ px}$**.

---

## 3. Contrato do Canvas de Estudos (`StudyCanvasView`)

### 3.1 Desbloqueio de Rolagem Vertical
- Em telas móveis ($\le 767\text{px}$), o contêiner `.canvas-viewport` não pode capturar irreversivelmente gestos de rolagem vertical.
- Aplica-se:
  ```css
  @media (max-width: 767px) {
    .canvas-viewport:not(.is-panning) {
      touch-action: pan-y;
    }
  }
  ```
- Quando o usuário acionar expressamente a ferramenta de pan ou interagir com cartões arrastáveis, `touch-action: none` é ativado temporariamente.

### 3.2 Compactação de Toolbar em Telas $< 1024\text{px}$
- Ferramentas de criação de moldura, alinhamento e reset de zoom agrupam-se em menu contextual móvel, evitando transbordamento da barra de topo.

---

## 4. Contrato da Árvore de Estudos (`StudyTreeView`)

### 4.1 Acessibilidade Tátil sem Dependência de Mouse
- Sob `@media (pointer: coarse)` ou `@media (max-width: 767px)`:
  - Alça `.tree-drag-handle` é ocultada (`display: none;`).
  - Menu contextual de cada nó (`.mobile-menu-toggle-btn`) torna-se o canal primário para "Mover para cima", "Mover para baixo", "Aninhar" e "Excluir".
  - Todos os itens de menu e botões de chevron possuem alvos mínimos de **$44 \times 44\text{ px}$**.
