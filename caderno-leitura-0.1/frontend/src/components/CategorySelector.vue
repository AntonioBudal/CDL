<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import type { Category } from '../types'
import { useCategories } from '../composables/useCategories'
import CategoryBadge from './CategoryBadge.vue'

const props = withDefaults(
  defineProps<{
    modelValue: string[]
    disabled?: boolean
  }>(),
  {
    disabled: false,
  }
)

const emit = defineEmits<{
  (e: 'update:modelValue', value: string[]): void
}>()

const { loadCategories, searchCategories, getCategoryById } = useCategories()

const query = ref('')
const isOpen = ref(false)
const activeIndex = ref(-1)
const rootRef = ref<HTMLElement | null>(null)
const inputRef = ref<HTMLInputElement | null>(null)

onMounted(async () => {
  await loadCategories()
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
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
  return searchCategories(query.value, 15).filter((cat) => !selectedSet.has(cat.id))
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

function selectCategory(category: Category) {
  if (props.disabled) return
  if (!props.modelValue.includes(category.id)) {
    emit('update:modelValue', [...props.modelValue, category.id])
  }
  query.value = ''
  activeIndex.value = -1
  isOpen.value = false
  inputRef.value?.focus()
}

function removeCategory(category: Category) {
  if (props.disabled) return
  emit(
    'update:modelValue',
    props.modelValue.filter((id) => id !== category.id)
  )
}

function onKeyDown(event: KeyboardEvent) {
  if (!isOpen.value) {
    if (event.key === 'ArrowDown' || event.key === 'ArrowUp') {
      isOpen.value = true
      event.preventDefault()
      return
    }
  }

  if (event.key === 'ArrowDown') {
    event.preventDefault()
    if (availableSuggestions.value.length > 0) {
      activeIndex.value = (activeIndex.value + 1) % availableSuggestions.value.length
    }
  } else if (event.key === 'ArrowUp') {
    event.preventDefault()
    if (availableSuggestions.value.length > 0) {
      activeIndex.value =
        (activeIndex.value - 1 + availableSuggestions.value.length) % availableSuggestions.value.length
    }
  } else if (event.key === 'Enter') {
    if (isOpen.value && activeIndex.value >= 0 && activeIndex.value < availableSuggestions.value.length) {
      event.preventDefault()
      selectCategory(availableSuggestions.value[activeIndex.value])
    }
  } else if (event.key === 'Escape') {
    isOpen.value = false
    activeIndex.value = -1
  }
}
</script>

<template>
  <div ref="rootRef" class="category-selector relative flex flex-col gap-2 font-sans">
    <!-- Etiquetas Selecionadas -->
    <div v-if="selectedCategories.length > 0" class="flex flex-wrap gap-1.5 min-h-[32px] items-center">
      <CategoryBadge
        v-for="cat in selectedCategories"
        :key="cat.id"
        :category="cat"
        :removable="!disabled"
        size="md"
        @remove="removeCategory"
      />
    </div>

    <!-- Campo de Busca e Autocomplete -->
    <div class="relative">
      <input
        ref="inputRef"
        v-model="query"
        type="text"
        :disabled="disabled"
        class="w-full rounded-md border border-theme px-3 py-2 text-sm bg-theme text-theme placeholder:text-muted focus:outline-none focus:ring-2 focus:ring-accent focus:border-transparent transition-all"
        placeholder="Digitar categoria (ex: Filosofia, Literatura, Brasil)..."
        autocomplete="off"
        @input="onInput"
        @focus="onFocus"
        @keydown="onKeyDown"
      />

      <!-- Dropdown de Sugestões -->
      <div
        v-if="isOpen && availableSuggestions.length > 0"
        class="category-dropdown absolute z-50 left-0 right-0 mt-1 max-h-60 overflow-y-auto rounded-md border shadow-lg py-1 bg-surface border-theme"
      >
        <div
          v-for="(cat, index) in availableSuggestions"
          :key="cat.id"
          class="category-option px-3 py-2 cursor-pointer text-sm transition-colors flex flex-col"
          :class="[index === activeIndex ? 'bg-accent/15 font-medium' : 'hover:bg-accent/10']"
          @mousedown.prevent="selectCategory(cat)"
          @mouseenter="activeIndex = index"
        >
          <span class="category-name text-theme">{{ cat.name }}</span>
          <span v-if="cat.path !== cat.name" class="category-path text-xs text-muted truncate">
            {{ cat.path }}
          </span>
        </div>
      </div>

      <!-- Nenhum resultado -->
      <div
        v-else-if="isOpen && query.trim().length > 0"
        class="category-dropdown absolute z-50 left-0 right-0 mt-1 rounded-md border shadow-lg p-3 bg-surface border-theme text-xs text-muted text-center"
      >
        Nenhuma categoria encontrada para "{{ query }}".
      </div>
    </div>
  </div>
</template>

<style scoped>
.bg-surface {
  background-color: var(--color-surface, #ffffff);
}

.category-option:hover {
  background-color: var(--color-surface-hover, rgba(0, 0, 0, 0.05));
}
</style>
