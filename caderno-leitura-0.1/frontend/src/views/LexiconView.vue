<script setup lang="ts">
/**
 * F0.11.06 (spec 108): léxico de conceitos do acervo, derivado das seções Conceitos e das menções [[conceito:…]].
 */
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { RouterLink } from 'vue-router'
import { api, errorMessage } from '../services/api'
import type { ConceptSummary } from '../types'

const PER_PAGE = 100
const query = ref('')
const items = ref<ConceptSummary[]>([])
const total = ref(0)
const page = ref(1)
const loading = ref(true)
const error = ref('')
let request: AbortController | null = null
let debounce: ReturnType<typeof setTimeout> | null = null

const pages = computed(() => Math.max(1, Math.ceil(total.value / PER_PAGE)))

async function load() {
  request?.abort()
  const controller = new AbortController()
  request = controller
  loading.value = true
  error.value = ''
  try {
    const data = await api.listConcepts({ q: query.value, page: page.value, per_page: PER_PAGE }, controller.signal)
    if (controller.signal.aborted) return
    items.value = data.items
    total.value = data.total
  } catch (err) {
    if (!controller.signal.aborted) error.value = errorMessage(err)
  } finally {
    if (!controller.signal.aborted) loading.value = false
  }
}

watch(query, () => {
  if (debounce) clearTimeout(debounce)
  debounce = setTimeout(() => {
    page.value = 1
    void load()
  }, 250)
})

function goTo(next: number) {
  page.value = Math.min(Math.max(1, next), pages.value)
  void load()
}

onMounted(load)
onBeforeUnmount(() => {
  request?.abort()
  if (debounce) clearTimeout(debounce)
})
</script>

<template>
  <section class="lexicon-view wrap" aria-labelledby="lexicon-heading">
    <header class="page-header">
      <p class="eyebrow">Conceitos do acervo</p>
      <h1 id="lexicon-heading">Léxico</h1>
      <p class="lexicon-lead">
        Montado a partir da seção Conceitos dos seus estudos (linhas como <code>**Termo**: definição</code> ou
        <code>Termo: definição</code>) e das menções <code>[[conceito:Termo]]</code>. Editar um estudo atualiza o léxico.
      </p>
    </header>

    <label class="lexicon-search">
      <span>Buscar conceito</span>
      <input v-model="query" type="search" placeholder="Ex.: mímese" autocomplete="off" />
    </label>

    <p class="lexicon-status" role="status" aria-live="polite">
      <template v-if="loading">Carregando o léxico…</template>
      <template v-else-if="!error">{{ total === 1 ? '1 conceito' : `${total} conceitos` }}</template>
    </p>
    <p v-if="error" class="notice error" role="alert">{{ error }}</p>

    <p v-else-if="!loading && total === 0" class="lexicon-empty">
      <template v-if="query">Nenhum conceito com “{{ query }}”.</template>
      <template v-else>
        Ainda não há conceitos. Escreva na seção Conceitos de um estudo uma linha como
        <code>**Termo**: definição</code>, ou mencione <code>[[conceito:Termo]]</code> em qualquer seção.
      </template>
    </p>

    <ul v-else class="lexicon-list">
      <li v-for="item in items" :key="item.key" class="lexicon-item">
        <RouterLink :to="`/conceitos/${item.key}`" class="lexicon-term">{{ item.term }}</RouterLink>
        <span v-if="item.fragile" class="fragile-tag">Frágil</span>
        <span class="lexicon-meta">
          {{ item.definitions === 1 ? '1 definição' : `${item.definitions} definições` }}
          · {{ item.books === 1 ? '1 livro' : `${item.books} livros` }}<template v-if="item.mentions">
          · {{ item.mentions === 1 ? '1 menção' : `${item.mentions} menções` }}</template>
        </span>
      </li>
    </ul>

    <nav v-if="pages > 1" class="lexicon-pages" aria-label="Páginas do léxico">
      <button type="button" class="quiet lexicon-page" :disabled="page <= 1" @click="goTo(page - 1)">Anterior</button>
      <span class="lexicon-meta">Página {{ page }} de {{ pages }}</span>
      <button type="button" class="quiet lexicon-page" :disabled="page >= pages" @click="goTo(page + 1)">Próxima</button>
    </nav>
  </section>
</template>

<style scoped>
.fragile-tag {
  font-size: 0.8rem;
  font-weight: 600;
  padding: 1px 8px;
  border-radius: 999px;
  border: 1px solid var(--color-warning-border);
  background: var(--color-warning-bg);
  color: var(--color-warning-text);
}
.lexicon-view {
  max-width: 52rem;
  margin: 0 auto;
  padding-block: 1.5rem 3rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.lexicon-lead,
.lexicon-meta,
.lexicon-status,
.lexicon-empty {
  color: var(--color-muted);
}

.lexicon-lead {
  margin: 0.5rem 0 0;
  line-height: 1.55;
}

.lexicon-lead code,
.lexicon-empty code {
  overflow-wrap: anywhere;
}

.lexicon-search {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-muted);
}

.lexicon-search input {
  min-height: 44px;
  max-width: 24rem;
  color: var(--color-text);
}

.lexicon-status,
.lexicon-empty {
  margin: 0;
  font-size: 0.9rem;
}

.lexicon-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
}

.lexicon-item {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: 0.25rem 0.75rem;
  padding: 0.35rem 0;
  border-bottom: 1px solid var(--color-border);
  min-width: 0;
}

.lexicon-term {
  display: inline-flex;
  align-items: center;
  min-height: 44px;
  font-weight: 600;
  color: var(--color-link);
  text-decoration: underline;
  text-underline-offset: 3px;
  overflow-wrap: anywhere;
}

.lexicon-meta {
  font-size: 0.85rem;
}

.lexicon-pages {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.75rem;
}

.lexicon-page {
  --quiet-border: var(--color-border-strong, var(--color-border));
  min-height: 44px;
}
</style>
