# Contracts: API e Componente da Grid View

**Feature**: F 0.7.4 — Redesenho da Grid View  
**Status**: Completed  
**Artifact**: `contracts/study-grid-api.md`

---

## 1. Contrato da API REST

### 1.1 Endpoint de Listagem por Capítulo

`GET /api/chapters/{chapter_id}/studies`

#### Resposta HTTP 200 (OK)
```json
[
  {
    "id": 12,
    "chapter_id": 4,
    "book_id": 2,
    "title": "A dialética da natureza",
    "location": "Páginas 45-48",
    "reading_status": "em_andamento",
    "parent_study_id": null,
    "position": 0,
    "version": 3,
    "created_at": "2026-10-01T14:20:00Z",
    "updated_at": "2026-10-02T19:30:00Z",
    "deleted_at": null,
    "visibility": "inherit",
    "effective_visibility": "private",
    "can_edit": true,
    "summary_preview": "Análise da concepção ontológica do movimento na física clássica confrontada com os princípios dialéticos.",
    "highlights_count": 5,
    "relations_count": 2
  }
]
```

---

## 2. Contrato do Componente `StudyGridView.vue`

### 2.1 Props

```typescript
interface StudyGridViewProps {
  studies: StudySummary[]
  bookId: number
  chapterId?: number | null
  chapters?: { id: number; name: string }[]
  activeStudyId?: number | null
  loading?: boolean
}
```

### 2.2 Eventos Emitidos (Emits)

```typescript
interface StudyGridViewEmits {
  (e: 'select-study', studyId: number): void
  (e: 'trash-study', study: StudySummary): void
}
```

### 2.3 Semântica WAI-ARIA e Acessibilidade do Cartão

- O cartão principal é um elemento semântico `<article class="study-card">`.
- Possui `tabindex="0"` e `@keydown.enter="emit('select-study', study.id)"`.
- O badge interativo de status possui seu próprio foco e não dispara a navegação geral do cartão (`@click.stop`).
- O botão de exclusão da lixeira possui `aria-label="Mover estudo para a lixeira"` e suprime a propagação de clique (`@click.stop`).
- Quando `loading === true`, são exibidos 6 blocos `<div class="study-card skeleton-card" aria-hidden="true">` com animação de pulso.
