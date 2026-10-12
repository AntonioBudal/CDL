# Modelo de Dados e Estados de Interface: Feature 080

**Feature**: `080-visualizacoes-e-destaques-moveis`  
**Data**: 2026-10-12  
**Status**: Concluído  

---

## 1. Estados Reativos da Biblioteca de Destaques

```typescript
// Interface de estado da barra de filtros e listagem de destaques
export interface HighlightsLibraryResponsiveState {
  searchQuery: string
  selectedBookId: number | null
  selectedKind: HighlightKind | null
  selectedColor: HighlightColor | null
  viewMode: 'recent' | 'by_book'
  page: number
  perPage: number
  totalPages: number
  totalItems: number
  mobileFiltersOpen: boolean
}
```

### Regras de Validação e Transição de Estado
- `viewMode`: Persistido em `localStorage['caderno_highlights_view_mode']` e sincronizado na URL como `?view_mode=recent` ou `?view_mode=by_book`.
- Em telas $\le 767\text{px}$, `mobileFiltersOpen` controla a visibilidade da linha secundária de filtros sem causar recálculo de largura externa.

---

## 2. Estados de Gestos Táteis no Mapa de Estudos (`StudyMapView`)

```typescript
// Estado de rastreamento de gestos multitoque (pan e pinch)
export interface MapTouchGestureState {
  touchCount: number
  startDistance: number
  initialZoom: number
  lastTouchX: number
  lastTouchY: number
  isPinching: boolean
  isPanning: boolean
}

// Modo de apresentação em telas móveis
export type MapDisplayMode = 'graph' | 'relations_list'
```

### Regras de Transição e Delimitação
- **Pan (1 dedo)**:
  - $\Delta x = \text{touch.clientX} - \text{lastTouchX}$
  - $\Delta y = \text{touch.clientY} - \text{lastTouchY}$
  - Limites de deslocamento delimitados para impedir que o grafo fuja da viewport.
- **Pinch Zoom (2 dedos)**:
  - Distância atual $d = \sqrt{(x_1 - x_2)^2 + (y_1 - y_2)^2}$
  - Fator de escala $s = d / \text{startDistance}$
  - $\text{novoZoom} = \max(0.5, \min(2.5, \text{initialZoom} \times s))$
- **Alternador de Apresentação**: Em viewports $\le 767\text{px}$, o usuário pode comutar entre `'graph'` e `'relations_list'`.

---

## 3. Estados de Controle do Canvas de Estudos (`StudyCanvasView`)

```typescript
// Modo de toque e rolagem da viewport espacial
export interface CanvasTouchState {
  touchMode: 'pan_page' | 'pan_canvas'
  toolbarCompactMenuOpen: boolean
}
```

### Regras de Toque
- `touchMode === 'pan_page'`: `.canvas-viewport` aplica `touch-action: pan-y;`, permitindo que o leitor role a página normalmente para cima e para baixo.
- `touchMode === 'pan_canvas'`: Acionado quando a ferramenta 'pan' está ativa, aplicando `touch-action: none;` para navegação espacial precisa.

---

## 4. Ações Contextuais da Árvore de Estudos (`StudyTreeView`)

```typescript
// Ação contextual disparada pelo menu tátil de nó
export interface TreeNodeMoveActionPayload {
  studyId: number
  direction: 'up' | 'down' | 'indent' | 'outdent'
  currentParentId: number | null
}
```

### Regras de Reordenação Tátil
- `direction: 'up'`: Troca de posição com o irmão imediatamente anterior na lista.
- `direction: 'down'`: Troca de posição com o irmão imediatamente posterior na lista.
- Todas as operações emitem eventos consumidos por `useStudyHierarchy.ts` e persistem a ordenação.
