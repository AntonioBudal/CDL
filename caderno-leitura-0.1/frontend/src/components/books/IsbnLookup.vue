<script setup lang="ts">
/**
 * F0.11.04 (spec 106): campo ISBN com "Buscar dados" (BrasilAPI → Open Library, consultadas pelo servidor).
 * O resultado é só uma sugestão: "Usar estes dados" preenche os campos vazios (ou todos, se marcado).
 */
import { computed, ref } from 'vue'
import { api, errorMessage } from '../../services/api'
import type { IsbnLookupResponse } from '../../types'

export interface IsbnBookFields {
  title: string
  subtitle: string
  author: string
  year: string
  publisher: string
  place: string
}

const props = defineProps<{
  idPrefix: string
  current: IsbnBookFields
  disabled?: boolean
}>()

const isbn = defineModel<string>('isbn', { required: true })
const emit = defineEmits<{ (e: 'apply', fields: Partial<IsbnBookFields>): void }>()

const searching = ref(false)
const error = ref('')
const suggestion = ref<IsbnLookupResponse | null>(null)
const overwrite = ref(false)
const liveMessage = ref('')

const SOURCE_LABELS: Record<string, string> = { brasilapi: 'BrasilAPI', openlibrary: 'Open Library' }

/** Mesma regra do servidor (dígito verificador), para não ir à rede com ISBN errado. */
function isbnLooksValid(raw: string): boolean {
  const digits = raw.replace(/[\s.-]/g, '').toUpperCase()
  if (/^\d{9}[\dX]$/.test(digits)) {
    const total = [...digits].reduce((sum, c, i) => sum + (10 - i) * (c === 'X' ? 10 : Number(c)), 0)
    return total % 11 === 0
  }
  if (/^97[89]\d{10}$/.test(digits)) {
    const total = [...digits.slice(0, 12)].reduce((sum, c, i) => sum + Number(c) * (i % 2 === 0 ? 1 : 3), 0)
    return (10 - (total % 10)) % 10 === Number(digits[12])
  }
  return false
}

const suggestedFields = computed<IsbnBookFields | null>(() => {
  const s = suggestion.value
  if (!s) return null
  return {
    title: s.title,
    subtitle: s.subtitle,
    author: s.author,
    year: s.year ? String(s.year) : '',
    publisher: s.publisher,
    place: s.place,
  }
})

async function search() {
  error.value = ''
  suggestion.value = null
  if (!isbnLooksValid(isbn.value)) {
    error.value = 'ISBN inválido: confira os 10 ou 13 dígitos.'
    return
  }
  searching.value = true
  liveMessage.value = 'Buscando…'
  try {
    suggestion.value = await api.lookupIsbn(isbn.value)
    liveMessage.value = `Encontrado na ${SOURCE_LABELS[suggestion.value.source] ?? suggestion.value.source}.`
  } catch (err) {
    error.value = errorMessage(err)
    liveMessage.value = ''
  } finally {
    searching.value = false
  }
}

function apply() {
  const fields = suggestedFields.value
  if (!fields) return
  const chosen: Partial<IsbnBookFields> = {}
  for (const key of Object.keys(fields) as (keyof IsbnBookFields)[]) {
    const value = fields[key]
    if (!value) continue
    if (overwrite.value || !props.current[key]?.trim()) chosen[key] = value
  }
  emit('apply', chosen)
  if (suggestion.value) isbn.value = suggestion.value.isbn
  suggestion.value = null
  liveMessage.value = 'Dados aplicados ao formulário. Salve para gravar.'
}
</script>

<template>
  <div class="isbn-lookup">
    <label :for="`${idPrefix}-isbn`" class="isbn-label">ISBN <span class="optional">(opcional)</span></label>
    <div class="isbn-row">
      <input
        :id="`${idPrefix}-isbn`"
        v-model="isbn"
        inputmode="numeric"
        autocomplete="off"
        placeholder="Ex.: 978-85-359-0846-6"
        :disabled="disabled || searching"
        :aria-invalid="!!error"
        @keydown.enter.prevent="search"
      />
      <button type="button" class="quiet isbn-search" :disabled="disabled || searching || !isbn.trim()" @click="search">
        {{ searching ? 'Buscando…' : 'Buscar dados' }}
      </button>
    </div>
    <p class="isbn-hint">Consulta a BrasilAPI e a Open Library pelo servidor do Leitorum, só quando você clica.</p>
    <p v-if="error" class="isbn-error" role="alert">{{ error }}</p>

    <div v-if="suggestion && suggestedFields" class="isbn-suggestion" role="region" :aria-label="`Dados encontrados para o ISBN ${suggestion.isbn}`">
      <p class="isbn-source">Dados da {{ SOURCE_LABELS[suggestion.source] ?? suggestion.source }}</p>
      <dl class="isbn-fields">
        <template v-if="suggestedFields.title"><dt>Título</dt><dd>{{ suggestedFields.title }}</dd></template>
        <template v-if="suggestedFields.subtitle"><dt>Subtítulo</dt><dd>{{ suggestedFields.subtitle }}</dd></template>
        <template v-if="suggestedFields.author"><dt>Autor</dt><dd>{{ suggestedFields.author }}</dd></template>
        <template v-if="suggestedFields.year"><dt>Ano</dt><dd>{{ suggestedFields.year }}</dd></template>
        <template v-if="suggestedFields.publisher"><dt>Editora</dt><dd>{{ suggestedFields.publisher }}</dd></template>
        <template v-if="suggestedFields.place"><dt>Local</dt><dd>{{ suggestedFields.place }}</dd></template>
      </dl>
      <p v-if="suggestion.existing_book" class="isbn-warning">
        Você já tem este ISBN em “{{ suggestion.existing_book.title }}”.
      </p>
      <label class="isbn-overwrite">
        <input v-model="overwrite" type="checkbox" />
        Substituir o que já está preenchido
      </label>
      <div class="isbn-actions">
        <button type="button" class="primary isbn-apply" @click="apply">Usar estes dados</button>
        <button type="button" class="quiet isbn-discard" @click="suggestion = null">Descartar</button>
      </div>
    </div>
    <span class="visually-hidden" role="status" aria-live="polite">{{ liveMessage }}</span>
  </div>
</template>

<style scoped>
.isbn-lookup {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  min-width: 0;
}

.isbn-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.isbn-row input {
  flex: 1 1 12rem;
  min-height: 44px;
  min-width: 0;
}

.isbn-search,
.isbn-discard {
  --quiet-border: var(--color-border-strong, var(--color-border));
  min-height: 44px;
}

.isbn-hint {
  margin: 0;
  font-size: 0.8125rem;
  color: var(--color-muted);
}

.isbn-error,
.isbn-warning {
  margin: 0;
  font-size: 0.875rem;
  color: var(--color-danger-text, var(--color-error-text, var(--color-text)));
}

.isbn-warning {
  color: var(--color-text);
  font-weight: 600;
}

.isbn-suggestion {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  padding: 0.75rem;
  border: 1px solid var(--color-border-strong, var(--color-border));
  border-radius: 8px;
  background: var(--color-surface);
}

.isbn-source {
  margin: 0;
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--color-muted);
}

.isbn-fields {
  display: grid;
  grid-template-columns: max-content 1fr;
  gap: 0.2rem 0.75rem;
  margin: 0;
  font-size: 0.9rem;
  color: var(--color-text);
}

.isbn-fields dt {
  color: var(--color-muted);
}

.isbn-fields dd {
  margin: 0;
  overflow-wrap: anywhere;
}

.isbn-overwrite {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  min-height: 44px;
  font-size: 0.875rem;
  color: var(--color-text);
}

.isbn-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.isbn-apply {
  min-height: 44px;
}

.visually-hidden {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}
</style>
