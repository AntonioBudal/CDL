<script setup lang="ts">
/**
 * F0.11.01 (spec 103): estado de leitura do livro (Quero ler, Lendo, Lido, Abandonado ou sem estado) e datas.
 * Grava pelo PATCH do livro com expected_version; o servidor preenche início/fim quando vazios.
 */
import { computed, ref, watch } from 'vue'
import { api, errorMessage } from '../../services/api'
import { BOOK_READING_STATE_OPTIONS, type Book, type BookPatch, type BookReadingState } from '../../types'

const props = defineProps<{ book: Book }>()
const emit = defineEmits<{ (e: 'saved', book: Book): void }>()

const saving = ref(false)
const error = ref('')
const started = ref(props.book.reading_started_on || '')
const finished = ref(props.book.reading_finished_on || '')
const optionRefs = ref<HTMLButtonElement[]>([])

watch(
  () => [props.book.id, props.book.reading_started_on, props.book.reading_finished_on],
  () => {
    started.value = props.book.reading_started_on || ''
    finished.value = props.book.reading_finished_on || ''
  },
)

const current = computed<BookReadingState | null>(() => props.book.reading_state ?? null)
const options = computed(() => [
  { value: null as BookReadingState | null, label: 'Sem estado' },
  ...BOOK_READING_STATE_OPTIONS,
])

async function save(payload: BookPatch) {
  if (saving.value) return
  saving.value = true
  error.value = ''
  try {
    const body: BookPatch = { ...payload }
    if (typeof props.book.version === 'number') body.expected_version = props.book.version
    const updated = await api.updateBook(props.book.id, body)
    emit('saved', updated)
  } catch (err) {
    error.value = errorMessage(err)
    started.value = props.book.reading_started_on || ''
    finished.value = props.book.reading_finished_on || ''
  } finally {
    saving.value = false
  }
}

function choose(value: BookReadingState | null) {
  if (value === current.value) return
  void save({ reading_state: value })
}

function onKeydown(event: KeyboardEvent, index: number) {
  const keys = ['ArrowRight', 'ArrowDown', 'ArrowLeft', 'ArrowUp']
  if (!keys.includes(event.key)) return
  event.preventDefault()
  const step = event.key === 'ArrowRight' || event.key === 'ArrowDown' ? 1 : -1
  const next = (index + step + options.value.length) % options.value.length
  optionRefs.value[next]?.focus()
  choose(options.value[next]!.value)
}

function saveDate(field: 'reading_started_on' | 'reading_finished_on', value: string) {
  const previous = props.book[field] || ''
  if (value === previous) return
  void save({ [field]: value || null })
}
</script>

<template>
  <section class="reading-state" aria-labelledby="reading-state-label">
    <span id="reading-state-label" class="reading-state-label">Leitura</span>
    <div class="reading-state-options" role="radiogroup" aria-labelledby="reading-state-label" :aria-busy="saving">
      <button
        v-for="(option, index) in options"
        :key="option.label"
        :ref="(el) => { if (el) optionRefs[index] = el as HTMLButtonElement }"
        type="button"
        role="radio"
        class="reading-state-option"
        :class="{ quiet: option.value !== current, 'is-selected': option.value === current }"
        :aria-checked="option.value === current"
        :tabindex="option.value === current ? 0 : -1"
        @click="choose(option.value)"
        @keydown="onKeydown($event, index)"
      >
        {{ option.label }}
      </button>
    </div>

    <div class="reading-state-dates">
      <label class="reading-state-date">
        <span>Início</span>
        <input
          v-model="started"
          type="date"
          :readonly="saving"
          @change="saveDate('reading_started_on', started)"
        />
      </label>
      <label class="reading-state-date">
        <span>Fim</span>
        <input
          v-model="finished"
          type="date"
          :min="started || undefined"
          :readonly="saving"
          @change="saveDate('reading_finished_on', finished)"
        />
      </label>
    </div>

    <p v-if="error" class="reading-state-error" role="alert">{{ error }}</p>
  </section>
</template>

<style scoped>
.reading-state {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin: 0.75rem 0 0;
  min-width: 0;
}

.reading-state-label {
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--color-muted);
}

.reading-state-options {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
}

.reading-state-option {
  min-height: 44px;
  padding: 0 0.85rem;
  font-size: 0.875rem;
  border-radius: 999px;
}

.reading-state-option.quiet {
  --quiet-border: var(--color-border-strong, var(--color-border));
}

.reading-state-dates {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem 1rem;
}

.reading-state-date {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
  font-size: 0.8125rem;
  color: var(--color-muted);
  min-width: 0;
}

.reading-state-date input {
  min-height: 44px;
  color: var(--color-text);
}

.reading-state-error {
  margin: 0;
  font-size: 0.875rem;
  color: var(--color-danger-text, var(--color-error-text, var(--color-text)));
}
</style>
