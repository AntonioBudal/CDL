# UI Component Contracts: F01 — Sistema de Visualizações e Dashboard Responsivo

**Branch**: `019-sistema-visualizacoes` | **Data**: 2026-09-19

---

## 1. Composable `useViewPreference.ts`

```typescript
export interface UseViewPreferenceOptions {
  bookId?: string | number | null
  initialMode?: StudyViewMode
  onModeChange?: (mode: StudyViewMode) => void
}

export function useViewPreference(options?: UseViewPreferenceOptions): {
  currentMode: Ref<StudyViewMode>
  activeStudyId: Ref<number | null>
  availableModes: StudyViewOption[]
  
  // Ações
  setMode: (mode: StudyViewMode) => void
  setActiveStudy: (id: number | null) => void
  resetToDefault: () => void
}
```

---

## 2. Componente `ViewSwitcher.vue` (Barra Seletora de Modos)

### Propriedades (`props`)
```typescript
interface Props {
  modelValue: StudyViewMode
  options?: StudyViewOption[]
  disabled?: boolean
  compact?: boolean
}
```

### Eventos (`emits`)
```typescript
interface Emits {
  (e: 'update:modelValue', mode: StudyViewMode): void
}
```

### Acessibilidade WAI-ARIA
- Contêiner: `role="tablist"` com `aria-label="Modo de visualização dos estudos"`.
- Botões de modo: `role="tab"`, `:aria-selected="modelValue === mode.id"`, `tabindex="0"` (para o ativo) ou `"-1"` (para os inativos).
- Suporte a teclado: Teclas `ArrowRight` e `ArrowDown` movem o foco e ativam a aba seguinte; `ArrowLeft` e `ArrowUp` ativam a aba anterior; `Home` e `End` saltam para a primeira e última aba.

---

## 3. Contrato Unificado dos Renderers de Visualização

Todos os 5 renderers implementam a mesma interface padrão de propriedades e eventos:

### Propriedades Comuns
```typescript
interface StudyRendererProps {
  studies: StudySummary[]
  bookId: number
  chapterId?: number | null
  activeStudyId?: number | null
  loading?: boolean
}
```

### Eventos Comuns
```typescript
interface StudyRendererEmits {
  (e: 'select-study', studyId: number): void
  (e: 'trash-study', study: StudySummary): void
}
```

### Renderers Implementados
1. **`StudyGridView.vue`**: Grade responsiva de cartões com títulos, datas e meta de localização.
2. **`StudyListView.vue`**: Lista linear compacta de alta densidade informativa.
3. **`StudyTreeView.vue`**: Estrutura em árvore expansível com hierarquia visual dos estudos.
4. **`StudyMapView.vue`**: Grafo de nós em rede bidimensional com distribuição radial.
5. **`StudyCanvasView.vue`**: Espaço bidimensional 2D com pan, zoom e cartões espaciais.

---

## 4. Contratos de Adaptação Mobile do Dashboard

### `DashboardView.vue`
- Grade de métricas em telas < 768px:
  - `grid-template-columns: repeat(2, 1fr)`
  - `.streak-card`: `grid-column: span 2`
  - Gap: `0.75rem`
- Botões de ação da linha do tempo:
  - Dimensão tátil mínima garantida: 44x44px.

### `HeatmapCalendar.vue`
- No evento de montagem (`onMounted`) sob resoluções móveis (< 768px):
  - Executa `scrollLeft = scrollWidth - clientWidth` no elemento `.heatmap-scroll-area` com comportamento suave (`behavior: 'smooth'`), garantindo que as semanas recentes e a data de hoje estejam imediatamente no campo visual do leitor.
