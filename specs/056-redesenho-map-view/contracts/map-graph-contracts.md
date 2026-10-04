# Contracts: F 0.7.7 — Redesenho da Map View (Criação e Edição de Grafo Semântico)

**Feature**: F 0.7.7 — Redesenho da Map View  
**Created**: 2026-10-04  
**Status**: Completed  

---

## 1. Contratos de Componentes Vue

### `StudyMapView.vue`
Componente principal da visualização de grafo semântico.

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

### `MapRelationPopover.vue`
Mini-popover ancorado para seleção e edição de relações semânticas no grafo.

```typescript
// Props
interface Props {
  isOpen: boolean
  sourceStudy: StudySummary | null
  targetStudy: StudySummary | null
  existingRelation?: StudyRelationItem | null
  position: { x: number; y: number }
}

// Emits
interface Emits {
  (e: 'close'): void
  (e: 'save', payload: {
    sourceId: number
    targetId: number
    relationType: StudyRelationType
    description?: string
  }): void
  (e: 'delete', relationId: number): void
}
```

---

### `MapQuickCreateCard.vue`
Mini-card inline para criação rápida in-place de estudos no mapa.

```typescript
// Props
interface Props {
  isOpen: boolean
  position: { x: number; y: number }
  chapterId: number
  bookId: number
  connectedSourceId?: number | null
}

// Emits
interface Emits {
  (e: 'close'): void
  (e: 'created', payload: {
    study: StudySummary
    initialRelation?: {
      sourceId: number
      targetId: number
      relationType: StudyRelationType
    }
  }): void
}
```

---

## 2. Contratos de Composables

### `useMapLayout.ts`
Lógica pura de posicionamento radial concêntrico e repulsão suave.

```typescript
export interface MapLayoutOptions {
  width: number
  height: number
  coreRadius: number
  primaryRadius: number
  secondaryRadius: number
  minAngularSeparation: number
}

export function computeRadialLayout(
  studies: StudySummary[],
  relations: StudyRelationItem[],
  activeStudyId: number | null,
  options?: Partial<MapLayoutOptions>
): {
  coreNode: MapNodeItem | null
  nodes: MapNodeItem[]
  edges: MapConnectionEdge[]
}
```

---

## 3. Contratos de API REST

### `POST /api/studies/{study_id}/relations`
Cria uma relação semântica entre estudos (já existente e reutilizado).

```json
// Request Body
{
  "target_study_id": 42,
  "relation_type": "fundamenta",
  "description": "Justificativa da premissa."
}

// Response: 201 Created
{
  "id": 105,
  "source_study_id": 10,
  "target_study_id": 42,
  "relation_type": "fundamenta",
  "description": "Justificativa da premissa.",
  "created_at": "2026-10-04T17:00:00Z",
  "connected_study": {
    "id": 42,
    "title": "Estudo Alvo",
    "book_id": 1,
    "book_title": "Obra Principal",
    "chapter_id": 5,
    "chapter_title": "Capítulo 5"
  }
}
```

---

### `DELETE /api/studies/relations/{relation_id}`
Remove uma relação semântica existente (já existente e reutilizado).

```json
// Response: 204 No Content
```

---

### `POST /api/studies`
Criação de estudo direto (com suporte a seção analítica inicial).

```json
// Request Body
{
  "chapter_id": 5,
  "title": "Síntese Emergente",
  "summary": "Ideia central articulada no mapa.",
  "location": "Grafo Semântico"
}

// Response: 201 Created
{
  "id": 45,
  "chapter_id": 5,
  "title": "Síntese Emergente",
  "summary": "Ideia central articulada no mapa.",
  "location": "Grafo Semântico",
  "reading_status": "rascunho",
  "created_at": "2026-10-04T17:01:00Z",
  "updated_at": "2026-10-04T17:01:00Z"
}
```
