# Data Model & Storage Contracts: F01 — Sistema de Visualizações e Dashboard Responsivo

**Branch**: `019-sistema-visualizacoes` | **Data**: 2026-09-19

---

## 1. Tipos e Entidades TypeScript

### 1.1. Modo de Visualização (`StudyViewMode`)

```typescript
export type StudyViewMode = 'grid' | 'list' | 'tree' | 'map' | 'canvas'

export interface StudyViewOption {
  id: StudyViewMode
  label: string
  icon: IconName
  description: string
}
```

### 1.2. Definição Canônica dos 5 Modos

```typescript
export const STUDY_VIEW_OPTIONS: StudyViewOption[] = [
  {
    id: 'grid',
    label: 'Grade',
    icon: 'grid',
    description: 'Cartões visuais com ênfase em capas, localização e resumos'
  },
  {
    id: 'list',
    label: 'Lista',
    icon: 'list',
    description: 'Apresentação compacta em alta densidade de leitura'
  },
  {
    id: 'tree',
    label: 'Árvore',
    icon: 'folder',
    description: 'Hierarquia visual com nós expansíveis e ramos de estudo'
  },
  {
    id: 'map',
    label: 'Mapa',
    icon: 'network',
    description: 'Rede bidimensional de conceitos e conexões'
  },
  {
    id: 'canvas',
    label: 'Canvas',
    icon: 'canvas',
    description: 'Espaço 2D livre com exploração espacial flexível'
  }
]
```

### 1.3. Preferência de Visualização (`ViewPreferenceState`)

```typescript
export interface ViewPreferenceState {
  bookId?: number | string | null
  mode: StudyViewMode
  updatedAt: string
}
```

---

## 2. Estrutura de Armazenamento Local (`localStorage`)

| Chave | Tipo | Descrição | Exemplo de Valor |
| :--- | :--- | :--- | :--- |
| `caderno_default_view` | String | Preferência global de visualização do leitor | `"grid"`, `"list"` ou `"tree"` |
| `caderno_preferred_view_{bookId}` | String | Preferência customizada para uma obra específica | `"tree"`, `"map"`, `"canvas"` |

### Regra de Precedência
1. `localStorage.getItem('caderno_preferred_view_' + bookId)`
2. `localStorage.getItem('caderno_default_view')`
3. Fallback de fábrica: `'grid'`

---

## 3. Impacto no Banco de Dados SQLite
**Zero impacto.** O schema do banco de dados SQLite (`backend/data/caderno.db`) permanece 100% inalterado. Toda a parametrização de visualização e layout responsivo opera exclusivamente no cliente frontend.
