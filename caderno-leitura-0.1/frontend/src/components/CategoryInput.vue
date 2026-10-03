<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import type { Category, CategorySuggestion } from '../types'
import { categoriesApi } from '../api/categories'
import { useCategories } from '../composables/useCategories'
import CategoryBadge from './CategoryBadge.vue'

const props = withDefaults(
  defineProps<{
    modelValue: string[]
    disabled?: boolean
    placeholder?: string
  }>(),
  {
    disabled: false,
    placeholder: 'Digite para buscar ou sugerir categoria…',
  }
)

const emit = defineEmits<{
  (e: 'update:modelValue', value: string[]): void
}>()

const { categories, loadCategories, getCategoryById } = useCategories()

const query = ref('')
const isOpen = ref(false)
const activeIndex = ref(-1)
const rootRef = ref<HTMLElement | null>(null)
const inputRef = ref<HTMLInputElement | null>(null)
const suggestion = ref<CategorySuggestion | null>(null)
const isSuggesting = ref(false)

let debounceTimer: ReturnType<typeof setTimeout> | null = null

onMounted(async () => {
  await loadCategories()
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  if (debounceTimer) clearTimeout(debounceTimer)
  document.removeEventListener('click', handleClickOutside)
})

function handleClickOutside(event: MouseEvent) {
  if (rootRef.value && !rootRef.value.contains(event.target as Node)) {
    isOpen.value = false
  }
}

const selectedCategories = computed(() => {
  return props.modelValue
    .map((id) => getCategoryById(id))
    .filter((cat): cat is Category => cat !== undefined)
})

const availableSuggestions = computed(() => {
  const selectedSet = new Set(props.modelValue)
  if (suggestion.value && suggestion.value.matching_candidates.length > 0) {
    return suggestion.value.matching_candidates.filter((c) => !selectedSet.has(c.id))
  }
  const cleanQuery = query.value.trim().toLowerCase()
  if (!cleanQuery) {
    return categories.value.filter((c) => !selectedSet.has(c.id)).slice(0, 10)
  }
  return categories.value
    .filter((c) => !selectedSet.has(c.id) && (c.name.toLowerCase().includes(cleanQuery) || c.id.includes(cleanQuery)))
    .slice(0, 10)
})

watch(query, (val) => {
  if (debounceTimer) clearTimeout(debounceTimer)
  const trimmed = val.trim()
  if (!trimmed) {
    suggestion.value = null
    return
  }
  debounceTimer = setTimeout(async () => {
    isSuggesting.value = true
    try {
      const res = await categoriesApi.suggest(trimmed)
      suggestion.value = res
    } catch {
      suggestion.value = null
    } finally {
      isSuggesting.value = false
    }
  }, 150)
})

function onInput() {
  isOpen.value = true
  activeIndex.value = availableSuggestions.value.length > 0 ? 0 : -1
}

function onFocus() {
  if (!props.disabled) {
    isOpen.value = true
    activeIndex.value = availableSuggestions.value.length > 0 ? 0 : -1
  }
}

async function selectCategory(cat: Category) {
  if (props.disabled) return
  if (!props.modelValue.includes(cat.id)) {
    emit('update:modelValue', [...props.modelValue, cat.id])
  }
  query.value = ''
  suggestion.value = null
  activeIndex.value = -1
  isOpen.value = false
  inputRef.value?.focus()
}

async function handleAddTerm() {
  const term = query.value.trim()
  if (!term || props.disabled) return

  // Se houver uma sugestão canônica ou item selecionado via teclado
  if (activeIndex.value >= 0 && activeIndex.value < availableSuggestions.value.length) {
    await selectCategory(availableSuggestions.value[activeIndex.value])
    return
  }

  try {
    const createdOrExisting = await categoriesApi.create(term)
    await loadCategories(true)
    await selectCategory(createdOrExisting)
  } catch (err) {
    // Se falhar criação, apenas limpa
  }
}

function removeCategory(cat: Category) {
  if (props.disabled) return
  emit(
    'update:modelValue',
    props.modelValue.filter((id) => id !== cat.id)
  )
}

function onKeyDown(event: KeyboardEvent) {
  if (event.key === 'ArrowDown') {
    event.preventDefault()
    if (!isOpen.value) {
      isOpen.value = true
    } else if (availableSuggestions.value.length > 0) {
      activeIndex.value = (activeIndex.value + 1) % availableSuggestions.value.length
    }
  } else if (event.key === 'ArrowUp') {
    event.preventDefault()
    if (isOpen.value && availableSuggestions.value.length > 0) {
      activeIndex.value =
        (activeIndex.value - 1 + availableSuggestions.value.length) % availableSuggestions.value.length
    }
  } else if (event.key === 'Enter') {
    event.preventDefault()
    handleAddTerm()
  } else if (event.key === 'Escape') {
    isOpen.value = false
  } else if (event.key === 'Backspace' && query.value === '' && selectedCategories.value.length > 0) {
    removeCategory(selectedCategories.value[selectedCategories.value.length - 1])
  }
}
</script>

<template>
  <div ref="rootRef" class="category-input-wrapper relative" :class="{ 'opacity-60 pointer-events-none': disabled }">
    <!-- Caixa de seleção contendo badges e campo de digitação -->
    <div
      class="input-container flex flex-wrap items-center gap-1.5 p-1.5 border rounded-md bg-surface transition-all focus-within:ring-2 focus-within:ring-accent focus-within:border-accent"
      @click="inputRef?.focus()"
    >
      <CategoryBadge
        v-for="cat in selectedCategories"
        :key="cat.id"
        :category="cat"
        removable
        size="sm"
        @remove="removeCategory"
      />

      <input
        ref="inputRef"
        v-model="query"
        type="text"
        class="search-input flex-1 min-w-[140px] border-none bg-transparent outline-none text-sm px-1 py-0.5 text-main placeholder-muted"
        :placeholder="selectedCategories.length === 0 ? placeholder : ''"
        :disabled="disabled"
        @input="onInput"
        @focus="onFocus"
        @keydown="onKeyDown"
      />
    </div>

    <!-- Sugestão assistida transparente -->
    <div
      v-if="isOpen && query.trim() && suggestion && suggestion.suggested_canonical && suggestion.suggested_canonical !== query.trim()"
      class="canonical-hint text-xs px-2 py-1 mt-1 text-muted bg-surface-muted border rounded"
    >
      Sugestão canônica: <strong>{{ suggestion.suggested_canonical }}</strong>
    </div>

    <!-- Dropdown de autocomplete -->
    <div
      v-if="isOpen && availableSuggestions.length > 0"
      class="suggestions-dropdown absolute left-0 right-0 top-full mt-1 max-h-56 overflow-y-auto bg-surface border rounded-md shadow-lg z-50 py-1"
      role="listbox"
    >
      <button
        v-for="(cat, idx) in availableSuggestions"
        :key="cat.id"
        type="button"
        class="suggestion-item w-full text-left px-3 py-1.5 text-sm flex items-center justify-between hover:bg-surface-muted transition-colors cursor-pointer"
        :class="{ 'bg-surface-muted font-medium text-accent': idx === activeIndex }"
        @mousedown.prevent="selectCategory(cat)"
      >
        <span class="category-title">{{ cat.name }}</span>
        <span v-if="cat.books_count !== undefined && cat.books_count > 0" class="books-count text-xs text-muted">
          {{ cat.books_count }} {{ cat.books_count === 1 ? 'livro' : 'livros' }}
        </span>
      </button>
    </div>
  </div>
</template>

<style scoped>
.category-input-wrapper {
  width: 100%;
}
.input-container {
  border-color: var(--color-border, #cbd5e1);
  min-height: 2.5rem;
}
.suggestions-dropdown {
  background-color: var(--color-surface, #ffffff);
  border-color: var(--color-border, #cbd5e1);
}
</style>
