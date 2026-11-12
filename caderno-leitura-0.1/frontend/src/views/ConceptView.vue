<script setup lang="ts">
/** F0.11.06 (spec 108): definições e menções de um conceito do léxico. */
import { computed, onBeforeUnmount, ref, watch } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { api, errorMessage } from '../services/api'
import type { ConceptDetail } from '../types'

const route = useRoute()
const key = computed(() => String(route.params.key || ''))
const concept = ref<ConceptDetail | null>(null)
const loading = ref(true)
const error = ref('')
let request: AbortController | null = null

async function load() {
  request?.abort()
  const controller = new AbortController()
  request = controller
  loading.value = true
  error.value = ''
  concept.value = null
  try {
    const data = await api.getConcept(key.value, controller.signal)
    if (!controller.signal.aborted) concept.value = data
  } catch (err) {
    if (!controller.signal.aborted) error.value = errorMessage(err)
  } finally {
    if (!controller.signal.aborted) loading.value = false
  }
}

watch(key, () => void load(), { immediate: true })
onBeforeUnmount(() => request?.abort())

function studyLink(studyId: number, bookId: number) {
  return { name: 'study', params: { bookId, studyId } }
}
</script>

<template>
  <section class="concept-view wrap" aria-labelledby="concept-heading">
    <RouterLink to="/conceitos" class="concept-back">← Léxico</RouterLink>

    <p v-if="loading" class="concept-muted" role="status">Carregando o conceito…</p>
    <div v-else-if="error" class="notice error" role="alert">
      <p>{{ error }}</p>
    </div>

    <template v-else-if="concept">
      <header class="page-header">
        <p class="eyebrow">Conceito</p>
        <h1 id="concept-heading">{{ concept.term }}</h1>
        <p v-if="concept.fragile" class="fragile-note">
          <span class="fragile-tag">Frágil</span> Este conceito anda difícil na revisão. Pratique em
          <RouterLink to="/revisao">Revisão</RouterLink>, filtro "Conceitos".
        </p>
      </header>

      <section class="concept-block" aria-labelledby="concept-definitions-heading">
        <h2 id="concept-definitions-heading">
          Definições <span class="concept-count">({{ concept.definitions.length }})</span>
        </h2>
        <p v-if="concept.definitions.length === 0" class="concept-muted">
          Ainda sem definição nos seus estudos. Escreva <code>**{{ concept.term }}**: definição</code> na seção
          Conceitos de um estudo.
        </p>
        <ul v-else class="concept-list">
          <li v-for="(item, index) in concept.definitions" :key="`d-${index}`" class="concept-item">
            <p class="concept-text">{{ item.text }}</p>
            <p class="concept-source">
              <RouterLink :to="studyLink(item.study_id, item.book_id)" class="concept-link">{{ item.study_title }}</RouterLink>
              · {{ item.book_title }}<template v-if="item.chapter_name"> · {{ item.chapter_name }}</template>
            </p>
          </li>
        </ul>
      </section>

      <section class="concept-block" aria-labelledby="concept-mentions-heading">
        <h2 id="concept-mentions-heading">
          Mencionado em <span class="concept-count">({{ concept.mentions.length }})</span>
        </h2>
        <p v-if="concept.mentions.length === 0" class="concept-muted">
          Nenhum estudo menciona <code>[[conceito:{{ concept.term }}]]</code> ainda.
        </p>
        <ul v-else class="concept-list">
          <li v-for="(item, index) in concept.mentions" :key="`m-${index}`" class="concept-item">
            <p class="concept-text concept-snippet">{{ item.text }}</p>
            <p class="concept-source">
              <RouterLink :to="studyLink(item.study_id, item.book_id)" class="concept-link">{{ item.study_title }}</RouterLink>
              · {{ item.book_title }}<template v-if="item.chapter_name"> · {{ item.chapter_name }}</template>
            </p>
          </li>
        </ul>
      </section>
    </template>
  </section>
</template>

<style scoped>
.fragile-note {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px;
  color: var(--color-muted);
  margin: 4px 0 0;
}
.fragile-tag {
  font-size: 0.8rem;
  font-weight: 600;
  padding: 1px 8px;
  border-radius: 999px;
  border: 1px solid var(--color-warning-border);
  background: var(--color-warning-bg);
  color: var(--color-warning-text);
}
.concept-view {
  max-width: 52rem;
  margin: 0 auto;
  padding-block: 1.5rem 3rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.concept-back,
.concept-link {
  display: inline-flex;
  align-items: center;
  min-height: 44px;
  color: var(--color-link);
  text-decoration: underline;
  text-underline-offset: 3px;
  overflow-wrap: anywhere;
}

.concept-block h2 {
  margin: 0 0 0.5rem;
  font-size: 1.1rem;
}

.concept-count,
.concept-muted,
.concept-source {
  color: var(--color-muted);
}

.concept-muted {
  margin: 0;
}

.concept-muted code {
  overflow-wrap: anywhere;
}

.concept-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.concept-item {
  padding: 0.75rem 1rem;
  border: 1px solid var(--color-border);
  border-radius: 10px;
  background: var(--color-surface);
  min-width: 0;
}

.concept-text {
  margin: 0;
  line-height: 1.55;
  color: var(--color-text);
  white-space: pre-wrap;
  overflow-wrap: anywhere;
}

.concept-snippet {
  font-size: 0.9rem;
}

.concept-source {
  margin: 0.35rem 0 0;
  font-size: 0.85rem;
}
</style>
