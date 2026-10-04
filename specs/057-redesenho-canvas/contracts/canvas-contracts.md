# Contracts: F 0.7.8 — Redesenho do Canvas: Espaço Livre de Pensamento e Criação Espacial

**Feature**: F 0.7.8 — Redesenho do Canvas  
**Date**: 2026-10-04  
**Status**: Completed  

---

## 1. Contratos de Componentes Vue

### `StudyCanvasView.vue`
Componente principal da mesa espacial de pensamento livre.

```typescript
// Props
interface Props {
  studies: StudySummary[]
  bookId: number
  chapterId?: number | null
  activeStudyId?: number | null
  loading?: boolean
}

// Emits
interface Emits {
  (e: 'select-study', studyId: number): void
  (e: 'trash-study', study: StudySummary): void
  (e: 'studies-updated', updatedStudies?: StudySummary[]): void
}
```

---

### `CanvasToolbar.vue`
Barra de ferramentas de navegação e modos operacionais.

```typescript
// Props
interface Props {
  zoomLevel: number
  activeTool: 'select' | 'pan' | 'frame' | 'connect'
  hasSelection?: boolean
  selectedCount?: number
  hasNodes?: boolean
}

// Emits
interface Emits {
  (e: 'select-tool', tool: 'select' | 'pan' | 'frame' | 'connect'): void
  (e: 'zoom-in'): void
  (e: 'zoom-out'): void
  (e: 'reset-zoom'): void
  (e: 'fit-to-view'): void
  (e: 'clear-selection'): void
  (e: 'add-frame'): void
  (e: 'quick-create'): void
}
```

---

### `CanvasFrameNode.vue`
Componente de renderização de molduras delimitadoras coloridas.

```typescript
// Props
interface Props {
  frame: CanvasFrameItem
  isSelected?: boolean
  isDragging?: boolean
  isResizing?: boolean
}

// Emits
interface Emits {
  (e: 'select', frameId: number): void
  (e: 'update-title', payload: { frameId: number; title: string }): void
  (e: 'update-color', payload: { frameId: number; colorTag: string }): void
  (e: 'delete', frameId: number): void
  (e: 'start-drag', event: MouseEvent): void
  (e: 'start-resize', event: MouseEvent, handle: string): void
}
```

---

### `CanvasNode.vue`
Componente de renderização do cartão espacial de estudo.

```typescript
// Props
interface Props {
  node: CanvasPositionedCard
  study: StudySummary
  isSelected?: boolean
  isFocused?: boolean
  isConnecting?: boolean
}

// Emits
interface Emits {
  (e: 'select', studyId: number): void
  (e: 'trash', study: StudySummary): void
  (e: 'start-drag', event: MouseEvent): void
  (e: 'start-connect', event: MouseEvent): void
  (e: 'connect-target', studyId: number): void
}
```

---

## 2. Contratos de Composables

### `useSmartSnapping.ts`
Lógica geométrica de alinhamento magnético inteligente (Smart Guides).

```typescript
export interface SnappingTarget {
  x: number
  y: number
  width: number
  height: number
}

export interface SnappedPosition {
  x: number
  y: number
  guides: Array<{
    type: 'horizontal' | 'vertical'
    coordinate: number
    start: number
    end: number
  }>
}

export function computeSmartSnapping(
  draggingRect: SnappingTarget,
  otherRects: SnappingTarget[],
  threshold?: number // default: 10px
): SnappedPosition
```

---

### `useCanvasFrames.ts`
Gestão de molduras, redimensionamento e movimento solidário de cartões internos.

```typescript
export function useCanvasFrames(bookId: Ref<number>) {
  const frames: Ref<CanvasFrameItem[]>
  const loading: Ref<boolean>
  const error: Ref<string | null>

  function loadFrames(bookId: number): Promise<void>
  function createFrame(payload: CreateCanvasFramePayload): Promise<CanvasFrameItem>
  function updateFrame(frameId: number, payload: UpdateCanvasFramePayload): Promise<CanvasFrameItem>
  function deleteFrame(frameId: number): Promise<void>

  /**
   * Identifica os cartões contidos dentro da moldura especificada
   */
  function getContainedNodes(
    frame: CanvasFrameItem,
    nodesMap: Map<number, CanvasPositionedCard>
  ): CanvasPositionedCard[]

  return {
    frames,
    loading,
    error,
    loadFrames,
    createFrame,
    updateFrame,
    deleteFrame,
    getContainedNodes,
  }
}
```

---

## 3. Contratos de API REST

### `POST /api/canvas/batch`
Persistência em lote de coordenadas cartesianas de nós de estudo (debounce de 500ms).

```json
// Request Body
{
  "nodes": [
    {
      "study_id": 10,
      "pos_x": 340.5,
      "pos_y": 210.0,
      "width": 280,
      "height": 200,
      "z_index": 2,
      "color_tag": "blue"
    }
  ]
}

// Response: 200 OK
{
  "ok": true,
  "updated_count": 1
}
```

---

### `POST /api/books/{book_id}/canvas/frames`
Criação de nova moldura retangular temática.

```json
// Request Body
{
  "title": "Argumentos Centrais",
  "pos_x": 100.0,
  "pos_y": 150.0,
  "width": 640.0,
  "height": 420.0,
  "color_tag": "purple"
}

// Response: 201 Created
{
  "id": 12,
  "book_id": 1,
  "title": "Argumentos Centrais",
  "pos_x": 100.0,
  "pos_y": 150.0,
  "width": 640.0,
  "height": 420.0,
  "color_tag": "purple",
  "created_at": "2026-10-04T18:00:00Z"
}
```

---

### `PATCH /api/canvas/frames/{frame_id}`
Atualização de posição, dimensões, título ou cor de moldura.

```json
// Request Body
{
  "pos_x": 120.0,
  "pos_y": 160.0,
  "width": 700.0,
  "height": 450.0,
  "title": "Argumentos Revisados"
}

// Response: 200 OK
{
  "id": 12,
  "title": "Argumentos Revisados",
  "pos_x": 120.0,
  "pos_y": 160.0,
  "width": 700.0,
  "height": 450.0,
  "color_tag": "purple"
}
```

---
