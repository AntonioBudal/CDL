# UI Component Contracts: F06 — Painéis Redimensionáveis

**Branch**: `018-paineis-redimensionaveis` | **Data**: 2026-09-19

Este documento formaliza as interfaces, propriedades (`props`), eventos (`emits`), slots e contratos de acessibilidade dos componentes de layout redimensionável.

---

## 1. `useSplitPanes.ts` (Composable Central)

### Assinatura
```typescript
export interface UseSplitPanesOptions {
  bookId?: string | number | null
  initialLeftWidth?: number
  initialRightWidth?: number
  minWidth?: number
  maxWidth?: number
  onResizeEnd?: (dimensions: SplitLayoutDimensions) => void
}

export function useSplitPanes(options?: UseSplitPanesOptions): {
  leftWidth: Ref<number>
  rightWidth: Ref<number>
  leftCollapsed: Ref<boolean>
  rightCollapsed: Ref<boolean>
  isDragging: Ref<boolean>
  layoutMode: ComputedRef<'split' | 'drawer' | 'mobile'>
  
  // Ações
  startDrag: (pane: 'left' | 'right', event: PointerEvent) => void
  toggleCollapse: (pane: 'left' | 'right') => void
  resetToDefault: (pane: 'left' | 'right') => void
  stepResize: (pane: 'left' | 'right', deltaPixels: number) => void
}
```

---

## 2. `SplitLayout.vue` (Contêiner Principal)

### Propriedades (`props`)
```typescript
interface SplitLayoutProps {
  bookId?: string | number | null
  leftCollapsible?: boolean   // default: true
  rightCollapsible?: boolean  // default: true
  minPaneWidth?: number       // default: 240
  maxPaneWidth?: number       // default: 600
  defaultPaneWidth?: number   // default: 300
}
```

### Slots
- `#left`: Conteúdo da barra lateral de navegação (capítulos, árvore, filtros).
- `#default`: Conteúdo do palco principal (leitor de estudo, detalhes do livro, canvas).
- `#right`: Conteúdo do painel lateral de contexto/inspetor (metadados, notas complementares, relações).
- `#left-toggle` / `#right-toggle` (opcionais): Customização dos botões de alternância rápida de colapso.

### Eventos (`emits`)
```typescript
interface SplitLayoutEmits {
  (e: 'resize', dimensions: SplitLayoutDimensions): void
  (e: 'toggle', pane: 'left' | 'right', collapsed: boolean): void
}
```

---

## 3. `SplitGutter.vue` (Divisor Interativo)

### Propriedades (`props`)
```typescript
interface SplitGutterProps {
  pane: 'left' | 'right'
  currentWidth: number
  minWidth: number
  maxWidth: number
  collapsed: boolean
  ariaLabel?: string
}
```

### Eventos (`emits`)
```typescript
interface SplitGutterEmits {
  (e: 'start-drag', event: PointerEvent): void
  (e: 'toggle'): void
  (e: 'reset'): void
  (e: 'step', delta: number): void
}
```

### Acessibilidade WAI-ARIA
- `role="separator"`
- `tabindex="0"`
- `aria-orientation="vertical"`
- `:aria-valuenow="collapsed ? 0 : currentWidth"`
- `:aria-valuemin="minWidth"`
- `:aria-valuemax="maxWidth"`
- `:aria-label="ariaLabel || (pane === 'left' ? 'Separador do navegador de capítulos' : 'Separador do painel de contexto')"`

---

## 4. `SplitPane.vue` (Painel Envelope)

### Propriedades (`props`)
```typescript
interface SplitPaneProps {
  id: 'left' | 'right' | 'main'
  width?: number
  collapsed?: boolean
  minWidth?: number
  maxWidth?: number
}
```

### Classes CSS Reativas
- `.split-pane-left`, `.split-pane-right`, `.split-pane-main`
- `.is-collapsed`: aplicado quando `collapsed === true`
- `.is-resizing`: aplicado durante o arrasto ativo
