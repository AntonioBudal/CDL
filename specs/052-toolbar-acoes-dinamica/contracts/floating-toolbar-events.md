# Contracts: Componentes e Eventos da Floating Actions Toolbar

**Feature**: F 0.7.3 — Refatoração Dinâmica da Floating Actions Toolbar  
**Status**: Completed  
**Artifact**: `contracts/floating-toolbar-events.md`

---

## 1. Contrato de `FloatingActionsToolbar.vue`

Componente principal da régua de ações em 1 clique.

### 1.1 Props
```typescript
interface FloatingActionsToolbarProps {
  visible: boolean
  selection: TextSelectionContext | null
  studyTitle?: string
  bookTitle?: string
  chapterName?: string
  canEdit?: boolean
}
```

### 1.2 Eventos Emitidos
```typescript
interface FloatingActionsToolbarEmits {
  (e: 'highlight', payload: { color: HighlightColor; selection?: TextSelectionContext }): void
  (e: 'occlude', payload?: { selection?: TextSelectionContext }): void
  (e: 'copy-quote', payload?: { selection?: TextSelectionContext }): void
  (e: 'annotate', payload: { note: string; color: HighlightColor; selection?: TextSelectionContext }): void
  (e: 'ask-question', payload: { question: string; selection?: TextSelectionContext }): void
  (e: 'tool-selected', payload: { tool: string; label: string; colorDot?: string }): void
  (e: 'close'): void
}
```

---

## 2. Contrato de `NoteQuestionPopover.vue`

Componente desacoplado para a camada de detalhe ancorada (popover contextual no desktop / bottom-sheet no mobile).

### 2.1 Props
```typescript
interface NoteQuestionPopoverProps {
  visible: boolean
  kind: 'note' | 'question'
  selection: TextSelectionContext | null
  activeColor: HighlightColor
  anchorRect: DOMRect | null
}
```

### 2.2 Eventos Emitidos
```typescript
interface NoteQuestionPopoverEmits {
  (e: 'save', payload: {
    text: string
    color: HighlightColor
    kind: 'note' | 'question'
    selection: TextSelectionContext
  }): void
  (e: 'cancel'): void
}
```

### 2.3 Comportamento de Foco e Acessibilidade
- **Ao abrir (`visible: true`):** Executa `nextTick()` e focaliza automaticamente o elemento `<textarea>`.
- **Atalhos no campo de texto:**
  - `Enter` (sem `Shift`): Dispara `@save` e fecha.
  - `Shift+Enter`: Insere nova linha no texto.
  - `Escape`: Dispara `@cancel` e fecha.
- **WAI-ARIA:** O popover possui `role="dialog"`, `aria-label="Adicionar anotação"` (ou "Criar pergunta reflexiva") e `aria-modal="true"`.

---

## 3. Contrato de `useHighlightColorPreference.ts`

Composable para persistência da última cor de marca-texto.

```typescript
export interface HighlightColorPreferenceReturn {
  activeColor: Ref<HighlightColor>
  colorHex: ComputedRef<string>
  colorLabel: ComputedRef<string>
  setColor: (color: HighlightColor) => void
  resetToDefault: () => void
}
```

- **Chave de armazenamento:** `caderno_last_highlight_color`
- **Valor padrão:** `'yellow'`
- **Comportamento:** Carrega síncronamente ao inicializar e sincroniza no `localStorage` a cada mutação de cor.
