# Phase 1: Data Model — Exportação de Anotações em TXT e Markdown

**Feature Branch**: `015-exportacao-anotacoes`  
**Date**: 2026-09-19  
**Status**: Completed  

---

## 1. Modelos do Backend (Python / Pydantic)

### `ExportFormat` (Enum)
```python
from enum import Enum

class ExportFormat(str, Enum):
    MARKDOWN = "markdown"
    TEXT = "text"
```

### `ExportOptions` (Schema de Parâmetros)
```python
from pydantic import BaseModel, Field

class ExportOptions(BaseModel):
    format: ExportFormat = Field(
        default=ExportFormat.MARKDOWN,
        description="Formato de saída: 'markdown' (.md) ou 'text' (.txt)"
    )
    include_notes: bool = Field(
        default=True,
        description="Incluir anotações pessoais do leitor (sempre ativado)"
    )
    include_sections: bool = Field(
        default=True,
        description="Incluir seções de análise (resumo, explicação, conceitos, referências)"
    )
    include_source: bool = Field(
        default=False,
        description="Incluir a resposta textual original da importação"
    )
    include_metadata: bool = Field(
        default=True,
        description="Incluir cabeçalho com autor, ano e categorias"
    )
```

---

## 2. Modelos do Frontend (TypeScript)

### `ExportConfig`
```typescript
export type ExportFormat = 'markdown' | 'text'

export interface ExportConfig {
  format: ExportFormat
  includeNotes: boolean
  includeSections: boolean
  includeSource: boolean
  includeMetadata: boolean
}

export interface ExportModalProps {
  open: boolean
  title: string
  scope: 'book' | 'study'
  bookId: number
  studyId?: number | null
}
```

---

## 3. Estrutura do Documento Gerado

### Estrutura Hierárquica em Memória
```text
BookExportDocument
├── Metadata: title, author, subtitle, year, categories, date_exported
├── Chapters[] (ordenados por position, id; apenas deleted_at IS NULL)
│   └── Studies[] (ordenados por id; apenas deleted_at IS NULL)
│       ├── Title, Location
│       ├── Notes (se include_notes)
│       ├── Sections: summary, explanation, concepts, references (se include_sections)
│       └── SourceResponse (se include_source)
```
