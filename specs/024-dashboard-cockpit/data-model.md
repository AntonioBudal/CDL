# Data Model & Contracts: F07 — Dashboard 2.0 (Cockpit de Estudos e Hub de Navegação)

**Feature Branch**: `024-dashboard-cockpit`  
**Date**: 2026-09-19  
**Spec**: [spec.md](./spec.md)  
**Research**: [research.md](./research.md)  

---

## 1. Modelos Relacionais e Persistência de Dados

Esta funcionalidade opera estritamente sobre as tabelas existentes do banco de dados relacional SQLite (`studies`, `books`, `chapters`, `categories`, `study_relations`), sem necessidade de novas migrações estruturais DDL. As agregações, contagens e filtros de isolamento operam exclusivamente em queries SQL otimizadas com respeito ao `deleted_at IS NULL` (soft delete).

---

## 2. Schemas Pydantic v2 (Backend)

Localização: `backend/app/schemas/dashboard.py`

### 2.1 `RecentStudyActivityItem` (Estudos para Retoma Imediata)
```python
class RecentStudyActivityItem(OutputModel):
    study_id: int
    title: str
    book_id: int
    book_title: str
    chapter_id: int | None = None
    chapter_title: str | None = None
    reading_status: str = "rascunho"  # 'rascunho' | 'em_estudo' | 'revisado' | 'concluido'
    updated_at: datetime
```

### 2.2 `UnlinkedStudyItem` (Estudos Órfãos para Enriquecimento)
```python
class UnlinkedStudyItem(OutputModel):
    study_id: int
    title: str
    book_id: int
    book_title: str
    chapter_id: int | None = None
    chapter_title: str | None = None
    reading_status: str = "rascunho"
    created_at: datetime
```

### 2.3 `RecentRelationItem` (Últimas Conexões Semânticas Criadas)
```python
class RecentRelationItem(OutputModel):
    relation_id: int
    relation_type: str  # 'relacionado_com' | 'complementa' | 'contradiz' | 'depende_de' | 'mesmo_tema' | 'desdobramento_de'
    description: str | None = None
    source_study_id: int
    source_study_title: str
    source_book_id: int
    source_book_title: str
    target_study_id: int
    target_study_title: str
    target_book_id: int
    target_book_title: str
    created_at: datetime
```

### 2.4 `DashboardSummary` (Métricas Agregadas Consolidadas)
```python
class DashboardSummary(OutputModel):
    total_books: int = 0
    total_studies: int = 0
    total_reading_days: int = 0
    current_streak: int = 0
    avg_studies_per_book: float = 0.0
    total_relations: int = 0
    total_categories: int = 0
    unlinked_studies_count: int = 0
```

### 2.5 `DashboardResponse` (Payload Unificado do Endpoint)
```python
class DashboardResponse(OutputModel):
    summary: DashboardSummary
    heatmap: list[HeatmapPoint]
    timeline: list[TimelineItem]
    recent_studies: list[RecentStudyActivityItem] = []
    unlinked_studies: list[UnlinkedStudyItem] = []
    latest_relations: list[RecentRelationItem] = []
```

---

## 3. Tipagem TypeScript (Frontend)

Localização: `frontend/src/types.ts`

```typescript
export interface RecentStudyActivityItem {
  study_id: number
  title: string
  book_id: number
  book_title: string
  chapter_id: number | null
  chapter_title: string | null
  reading_status: ReadingStatus | string
  updated_at: string
}

export interface UnlinkedStudyItem {
  study_id: number
  title: string
  book_id: number
  book_title: string
  chapter_id: number | null
  chapter_title: string | null
  reading_status: ReadingStatus | string
  created_at: string
}

export interface RecentRelationItem {
  relation_id: number
  relation_type: StudyRelationType | string
  description: string | null
  source_study_id: number
  source_study_title: string
  source_book_id: number
  source_book_title: string
  target_study_id: number
  target_study_title: string
  target_book_id: number
  target_book_title: string
  created_at: string
}

export interface DashboardSummary {
  total_books: number
  total_studies: number
  total_reading_days: number
  current_streak: number
  avg_studies_per_book: number
  total_relations: number
  total_categories: number
  unlinked_studies_count: number
}

export interface DashboardResponse {
  summary: DashboardSummary
  heatmap: HeatmapPoint[]
  timeline: TimelineItem[]
  recent_studies: RecentStudyActivityItem[]
  unlinked_studies: UnlinkedStudyItem[]
  latest_relations: RecentRelationItem[]
}

export type HomeViewPreference = 'dashboard' | 'books'

export interface DashboardBlockVisibility {
  resumeStudies: boolean
  unlinkedStudies: boolean
  recentRelations: boolean
  timelineHeatmap: boolean
}
```

---

## 4. Persistência de Estado no Navegador (`localStorage`)

| Chave de Armazenamento | Tipo | Valor Padrão | Descrição e Finalidade |
| :--- | :--- | :--- | :--- |
| `caderno_home_view` | `string` | `'dashboard'` | Determina a tela de entrada ao acessar a raiz `/` (`'dashboard'` ou `'books'`). |
| `caderno_dashboard_blocks_visibility` | `string` (JSON) | `{"resumeStudies":true,"unlinkedStudies":true,"recentRelations":true,"timelineHeatmap":true}` | Persiste o estado colapsado ou visível de cada um dos quatro blocos modulares do Dashboard. |
| `caderno_dashboard_mobile_tab` | `string` | `'unlinked'` | Armazena a aba selecionada no container combinado móvel (`'unlinked'` ou `'relations'`). |
