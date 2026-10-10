# Data Model: 066-importar-atelie-parser

## 1. Estruturas de Estado do Ateliê

```typescript
export type StudioViewMode = 'split' | 'source' | 'preview'

export interface StudioToolbarState {
  visible: boolean
  x: number
  y: number
  selectionStart: number
  selectionEnd: number
}

export interface SectionCardMeta {
  key: 'summary' | 'explanation' | 'concepts' | 'references'
  label: string
  detected: boolean
  wordCount: number
  characterCount: number
  pulsing: boolean
}

export interface ImportStudioDraftState {
  bookId: string
  chapterId: string
  location: string
  title: string
  sourceResponse: string
  sections: {
    summary: string
    explanation: string
    concepts: string
    references: string
  }
  preview: ImportPreviewResponse | null
  previewError: string
  saveError: string
  preparing: boolean
  saving: boolean
  saved: StudyDetail | null
  viewMode: StudioViewMode
  activeMobileTab: 'source' | 'preview'
}
```

## 2. Contratos de Ações do Markdown

```typescript
export type MarkdownFormatAction =
  | 'bold'
  | 'italic'
  | 'heading'
  | 'bullet_list'
  | 'quote'
  | 'code'
  | 'link'
  | 'table'
```

## 3. Preservação de Entidades de Banco de Dados

Nenhuma alteração de schema no banco de dados SQLite é necessária. As chamadas de backend utilizam os endpoints REST existentes:
- `POST /api/studies/preview`
- `POST /api/studies`
- `GET /api/books`
- `GET /api/books/{book_id}/chapters`
- `GET /api/inbox/{id}`
- `POST /api/inbox/{id}/promote`
