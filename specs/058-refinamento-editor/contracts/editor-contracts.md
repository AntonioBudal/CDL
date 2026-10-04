# Contratos de Interface: F 0.7.9 — Refinamento do Editor de Estudos e Correção de Ícones de Categorias

**Feature**: F 0.7.9 — Refinamento do Editor de Estudos  
**Branch**: `058-refinamento-editor`  
**Date**: 2026-10-04  

---

## 1. Contrato do Componente: `StudyEditorFields.vue`

### Props & Models (v-model bidirecional)

```typescript
interface StudyEditorFieldsProps {
  idPrefix: string
  showMetadata?: boolean
}

// Model bindings
const title = defineModel<string>('title', { required: true })
const location = defineModel<string>('location', { required: true })
const notes = defineModel<string>('notes', { required: true })
const sections = defineModel<AnalysisSections>('sections', { required: true })
```

### Estado Interno e Comportamento

- `activeTab`: `'summary' | 'explanation' | 'concepts' | 'references' | 'notes'` (padrão: `'summary'`).
- `viewMode`: `'focused' | 'all'` (padrão: `'focused'`).
- `isPreviewing`: `Record<string, boolean>` (mapeia se cada seção está exibindo a prévia Markdown renderizada ou a textarea).
- Pílulas com `role="tablist"` e `role="tab"`, com `:aria-selected="activeTab === section.key"`.
- Botão "Editar / Prévia" em cada seção com `title="Alternar prévia de Markdown"` e `aria-label="Alternar pré-visualização"`.

---

## 2. Contrato do Componente: `MarkdownToolbar.vue`

### Props

```typescript
interface MarkdownToolbarProps {
  targetId: string
}
```

### Eventos e Comportamento Tátil

- Botões dispostos em container com `overflow-x: auto`, `scrollbar-width: none` e `touch-action: manipulation`.
- Alvos táteis no mobile: `min-width: 44px; min-height: 44px;`.
- Todas as ações disparam com `@mousedown.prevent="handleFormat(action)"` para manter o foco ativo e a seleção do cursor na textarea.
- Ações suportadas: `'bold'`, `'italic'`, `'heading'`, `'bullet_list'`, `'quote'`, `'code'`, `'link'`.
- Atalhos de teclado escutados diretamente na textarea vinculada: `Ctrl+B` (negrito), `Ctrl+I` (itálico), `Ctrl+K` (link).

---

## 3. Contrato do Composable: `useStudyDraft.ts`

### Interface de Parâmetros e Retorno

```typescript
export interface StudyEditorDraftPayload {
  studyId: number
  title: string
  location: string
  sections: AnalysisSections
  notes: string
  savedAt: number
}

export interface UseStudyDraftOptions {
  studyId: MaybeRefOrGetter<number | undefined>
  getCurrentData: () => {
    title: string
    location: string
    sections: AnalysisSections
    notes: string
  }
  onRestore: (draft: StudyEditorDraftPayload) => void
}

export function useStudyDraft(options: UseStudyDraftOptions): {
  hasDraft: Ref<boolean>
  isDraftRestored: Ref<boolean>
  saveDraft: () => void
  restoreDraft: () => boolean
  discardDraft: () => void
  clearDraft: () => void
}
```

### Regras de Operação

- `saveDraft`: Salva no `sessionStorage` sob a chave `caderno_draft_study_<id>` via debounce de 500ms.
- `restoreDraft`: Se houver snapshot recente diferente do estado inicial, invoca `onRestore` e ativa `isDraftRestored.value = true`.
- `discardDraft`: Limpa `sessionStorage` e sinaliza descarte, permitindo reverter para o estado original do servidor.
- `clearDraft`: Invocado após salvamento bem-sucedido na API REST.

---

## 4. Contrato dos Componentes de Categoria: `CategoryBadge.vue` e `CategoryInput.vue`

### `CategoryBadge.vue`

```typescript
interface CategoryBadgeProps {
  category: Category
  removable?: boolean
  clickable?: boolean
  size?: 'sm' | 'md'
}

const emit = defineEmits<{
  (e: 'remove', category: Category): void
  (e: 'click', category: Category): void
}>()
```

- Botão de remoção: Renderiza `<Icon name="x" :size="12" />`.
- Alinhamento vertical: `inline-flex items-center justify-center`.
- Acessibilidade: `:aria-label="'Remover categoria ' + category.name"` e foco visível via `:focus-visible`.

### `CategoryInput.vue`

```typescript
interface CategoryInputProps {
  modelValue: string[]
  disabled?: boolean
  placeholder?: string
}

const emit = defineEmits<{
  (e: 'update:modelValue', value: string[]): void
}>()
```

- Badges internos padronizados com `<CategoryBadge size="sm" removable />`.
- Ícone de busca/sugestão integrado sem SVG cru inline.
- Suporte a teclado completo: `ArrowDown`, `ArrowUp`, `Enter`, `Escape`, `Backspace`.
