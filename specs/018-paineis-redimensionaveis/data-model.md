# Data Model: F06 — Painéis Redimensionáveis

**Branch**: `018-paineis-redimensionaveis` | **Data**: 2026-09-19

Este documento especifica os tipos de dados, estruturas de persistência em cliente e contratos de estado para os painéis redimensionáveis.

---

## 1. Entidades e Tipos TypeScript

### 1.1. `PaneId` e `PanePosition`
Identificadores semânticos dos painéis:
```typescript
export type PaneId = 'left' | 'right'
export type LayoutMode = 'split' | 'drawer' | 'mobile'
```

### 1.2. `PaneConfig`
Definição estática e limites de um painel individual:
```typescript
export interface PaneConfig {
  id: PaneId
  minWidth: number      // Largura mínima em pixels (padrão: 240px)
  maxWidth: number      // Largura máxima em pixels (padrão: 600px ou 40% da tela)
  defaultWidth: number  // Largura padrão de fábrica (padrão: 300px)
  collapsible: boolean  // Se permite colapso total (padrão: true)
  defaultCollapsed: boolean // Se inicia colapsado (esquerda: false, direita: true)
}
```

### 1.3. `PaneState`
Estado reativo de um painel em execução:
```typescript
export interface PaneState {
  width: number         // Largura atual em pixels
  collapsed: boolean    // Se está colapsado (largura visual = 0)
  isDragging: boolean   // Se está sendo ativamente redimensionado pelo usuário
}
```

### 1.4. `SplitLayoutDimensions`
Objeto de persistência serializável no `localStorage`:
```typescript
export interface SplitLayoutDimensions {
  leftWidth: number
  rightWidth: number
  leftCollapsed: boolean
  rightCollapsed: boolean
  updatedAt: string     // ISO 8601 da última alteração
}
```

---

## 2. Estratégia de Armazenamento (`localStorage`)

### Chaves Utilizadas:
1. `caderno_pane_sizes_global`:
   ```json
   {
     "leftWidth": 300,
     "rightWidth": 300,
     "leftCollapsed": false,
     "rightCollapsed": true,
     "updatedAt": "2026-09-19T14:20:00.000Z"
   }
   ```
2. `caderno_pane_sizes_book_{bookId}`:
   ```json
   {
     "leftWidth": 340,
     "rightWidth": 280,
     "leftCollapsed": false,
     "rightCollapsed": false,
     "updatedAt": "2026-09-19T14:22:00.000Z"
   }
   ```

### Regras de Resolução:
1. Ao carregar a tela do livro `bookId`:
   - Se existir `caderno_pane_sizes_book_{bookId}`, carregar dimensões e estados desse registro.
   - Caso contrário, se existir `caderno_pane_sizes_global`, herdar dimensões e estados globais.
   - Caso contrário, aplicar valores padrão de fábrica:
     - `leftWidth = 300px`, `leftCollapsed = false`
     - `rightWidth = 300px`, `rightCollapsed = true` (Q1: Opção A)
2. Ao redimensionar ou colapsar/expandir:
   - Se o contexto do livro estiver ativo (`bookId`), salvar na chave específica `caderno_pane_sizes_book_{bookId}` e atualizar o registro global para refletir as novas preferências gerais do usuário.

---

## 3. Máquina de Estados do Divisor (*Gutter*)

```
       [ Idle / Estático ]
             │
   pointerdown (captura de ponteiro)
             ▼
     [ Dragging / Arrasto ] ─── Esc / pointercancel ───► [ Idle (restaura largura anterior) ]
             │
   pointermove (limita entre min/max e calcula delta)
             │
    pointerup (libera ponteiro e persiste no localStorage)
             ▼
       [ Idle / Estático ]
```

### Transição de Colapso (*Snap-to-Collapse*):
- Se o usuário arrastar a divisória para uma largura menor que 60px (ou acionar o botão de colapso), o painel transita para `collapsed = true`.
- Ao expandir novamente, restaura a largura imediatamente anterior ao colapso (ou o padrão de fábrica).
