<script setup lang="ts">
/**
 * F0.12.03 (spec 116): importar a biblioteca de outro serviço (Goodreads, StoryGraph, BookWyrm) pelo CSV exportado.
 * Passos: arquivo → prévia (nada gravado) → escolher o que fazer com cada livro → importar.
 */
import { computed, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { api, errorMessage } from '../services/api'
import type { LibraryAction, LibraryImportResponse, LibraryPreviewResponse } from '../types'

const file = ref<File | null>(null)
const preview = ref<LibraryPreviewResponse | null>(null)
const actions = ref<Record<string, LibraryAction>>({})
const withReviews = ref(false)
const stateFilter = ref('')
const busy = ref(false)
const error = ref('')
const result = ref<LibraryImportResponse | null>(null)
const liveMessage = ref('')

const step = computed(() => (result.value ? 'done' : preview.value ? 'preview' : 'pick'))
const rows = computed(() => (preview.value?.rows ?? []).filter((r) => !stateFilter.value || (r.state ?? '') === stateFilter.value))
const counts = computed(() => {
  const all = Object.values(actions.value)
  return { create: all.filter((a) => a === 'create').length, update: all.filter((a) => a === 'update').length }
})
const reviewsAvailable = computed(() => (preview.value?.rows ?? []).some((r) => r.has_review))

function onFileChange(event: Event) {
  file.value = (event.target as HTMLInputElement).files?.[0] ?? null
  error.value = ''
}

function formatDate(value: string | null | undefined): string {
  if (!value) return ''
  const [y, m, d] = value.split('-')
  return `${d}/${m}/${y}`
}

async function sendPreview() {
  if (!file.value) return
  busy.value = true
  error.value = ''
  try {
    const data = await api.previewLibraryImport(file.value)
    preview.value = data
    actions.value = Object.fromEntries(data.rows.map((r) => [r.key, r.suggested_action]))
    liveMessage.value = `Encontrei ${data.rows.length} ${data.rows.length === 1 ? 'livro' : 'livros'} no arquivo do ${data.service_label}.`
  } catch (e) {
    error.value = errorMessage(e)
  } finally {
    busy.value = false
  }
}

function setAll(action: LibraryAction) {
  for (const row of preview.value?.rows ?? []) {
    if (action === 'update' && !row.existing_book_id) continue
    if (action === 'create' && row.existing_book_id) continue
    actions.value[row.key] = action
  }
}

async function runImport() {
  if (!file.value || !preview.value) return
  busy.value = true
  error.value = ''
  try {
    const choices = Object.entries(actions.value).map(([key, action]) => ({ key, action }))
    result.value = await api.importLibrary(file.value, choices, withReviews.value)
    liveMessage.value = 'Importação concluída.'
  } catch (e) {
    error.value = errorMessage(e)
  } finally {
    busy.value = false
  }
}

function restart() {
  file.value = null
  preview.value = null
  result.value = null
  actions.value = {}
  withReviews.value = false
  stateFilter.value = ''
}
</script>

<template>
  <section class="library-import wrap" aria-labelledby="library-import-heading">
    <RouterLink to="/livros" class="library-import-back">← Livros</RouterLink>
    <header class="page-header">
      <p class="eyebrow">Importar</p>
      <h1 id="library-import-heading">Importar biblioteca</h1>
      <p class="library-import-muted">
        Traga sua lista de livros de outro serviço, com o estado de leitura e as datas. Destaques do Kindle, Kobo,
        KOReader, Readwise e Omnivore entram por <RouterLink to="/inbox/importar-leitor">Importar de leitor digital</RouterLink>.
      </p>
    </header>

    <p class="visually-hidden" role="status" aria-live="polite">{{ liveMessage }}</p>
    <p v-if="error" class="notice error" role="alert">{{ error }}</p>

    <section v-if="step === 'pick'" class="panel library-import-panel" aria-labelledby="library-pick-heading">
      <h2 id="library-pick-heading">1. Escolha o arquivo</h2>
      <ul class="library-import-help">
        <li><strong>Goodreads:</strong> My Books → Import and export → Export Library (arquivo <code>.csv</code>).</li>
        <li><strong>The StoryGraph:</strong> Manage Account → Export StoryGraph Library (<code>.csv</code>).</li>
        <li><strong>BookWyrm:</strong> Configurações → Exportar CSV.</li>
      </ul>
      <label class="library-import-file">
        <span>Arquivo CSV</span>
        <input type="file" accept=".csv,text/csv" @change="onFileChange" />
      </label>
      <p class="library-import-muted">Nada é gravado nesta etapa, e o arquivo não fica guardado no servidor.</p>
      <button type="button" class="primary library-import-button" :disabled="!file || busy" @click="sendPreview">
        {{ busy ? 'Lendo…' : 'Ver o que tem no arquivo' }}
      </button>
    </section>

    <section v-else-if="step === 'preview' && preview" class="panel library-import-panel" aria-labelledby="library-preview-heading">
      <h2 id="library-preview-heading">2. Escolha o que fazer com cada livro</h2>
      <p class="library-import-muted">
        Arquivo do {{ preview.service_label }}: {{ preview.rows.length }} livros<template v-if="preview.skipped">,
        {{ preview.skipped }} linhas puladas (sem título ou repetidas)</template>. As notas em estrelas não são importadas:
        o Leitorum não tem esse campo.
      </p>
      <div class="library-import-tools">
        <label class="library-import-filter">
          <span>Mostrar</span>
          <select v-model="stateFilter">
            <option value="">Todos</option>
            <option value="quero_ler">Quero ler</option>
            <option value="lendo">Lendo</option>
            <option value="lido">Lido</option>
            <option value="abandonado">Abandonado</option>
          </select>
        </label>
        <button type="button" class="quiet library-import-button" @click="setAll('create')">Criar todos os novos</button>
        <button type="button" class="quiet library-import-button" @click="setAll('update')">Atualizar todos os existentes</button>
        <button type="button" class="quiet library-import-button" @click="setAll('skip')">Pular todos</button>
      </div>
      <ul class="library-import-list">
        <li v-for="row in rows" :key="row.key" class="library-import-row">
          <div class="library-import-info">
            <strong>{{ row.title }}</strong>
            <span class="library-import-muted">
              {{ row.author || 'Autor não informado' }}<template v-if="row.isbn"> · ISBN {{ row.isbn }}</template>
            </span>
            <span class="library-import-muted">
              {{ row.state_label }}<template v-if="row.started_on"> · início {{ formatDate(row.started_on) }}</template><template v-if="row.finished_on"> · fim {{ formatDate(row.finished_on) }}</template>
              · <span :class="row.existing_book_id ? 'library-import-existing' : ''">{{ row.existing_book_id ? `já no acervo (${row.existing_book_title})` : 'novo' }}</span>
            </span>
          </div>
          <label class="library-import-action">
            <span class="visually-hidden">Ação para {{ row.title }}</span>
            <select v-model="actions[row.key]">
              <option v-if="!row.existing_book_id" value="create">Criar</option>
              <option v-if="row.existing_book_id" value="update">Atualizar estado e datas</option>
              <option value="skip">Pular</option>
            </select>
          </label>
        </li>
      </ul>
      <label v-if="reviewsAvailable" class="library-import-check">
        <input v-model="withReviews" type="checkbox" />
        <span>Trazer as resenhas como capturas na Caixa de entrada</span>
      </label>
      <div class="library-import-tools">
        <button type="button" class="primary library-import-button" :disabled="busy || (counts.create + counts.update) === 0" @click="runImport">
          {{ busy ? 'Importando…' : `Importar (${counts.create} novos, ${counts.update} atualizações)` }}
        </button>
        <button type="button" class="quiet library-import-button" :disabled="busy" @click="restart">Escolher outro arquivo</button>
      </div>
    </section>

    <section v-else-if="result" class="panel library-import-panel" aria-labelledby="library-done-heading">
      <h2 id="library-done-heading">Pronto</h2>
      <p>
        {{ result.created }} {{ result.created === 1 ? 'livro criado' : 'livros criados' }},
        {{ result.updated }} {{ result.updated === 1 ? 'atualizado' : 'atualizados' }},
        {{ result.skipped }} {{ result.skipped === 1 ? 'pulado' : 'pulados' }}<template v-if="result.reviews">,
        {{ result.reviews }} {{ result.reviews === 1 ? 'resenha na Caixa de entrada' : 'resenhas na Caixa de entrada' }}</template>.
      </p>
      <div class="library-import-tools">
        <RouterLink to="/livros" class="button primary library-import-button">Ver Livros</RouterLink>
        <button type="button" class="quiet library-import-button" @click="restart">Importar outro arquivo</button>
      </div>
    </section>
  </section>
</template>

<style scoped>
.library-import {
  max-width: 52rem;
  margin: 0 auto;
  padding-block: 1.5rem 3rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  min-width: 0;
}
.library-import-back {
  color: var(--color-link);
  display: inline-flex;
  align-items: center;
  min-height: 44px;
  align-self: flex-start;
}
.library-import-muted {
  color: var(--color-muted);
  font-size: 0.9rem;
  margin: 4px 0;
}
.library-import-help {
  margin: 8px 0;
  padding-left: 1.2rem;
}
.library-import-file,
.library-import-filter,
.library-import-action {
  display: grid;
  gap: 4px;
}
.library-import-file input,
.library-import-filter select,
.library-import-action select {
  min-height: 44px;
  max-width: 100%;
}
.library-import-tools {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  gap: 8px;
  margin: 10px 0;
}
.library-import-button {
  min-height: 44px;
  white-space: normal;
}
.library-import-list {
  list-style: none;
  margin: 8px 0;
  padding: 0;
  display: grid;
  gap: 6px;
}
.library-import-row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 6px 12px;
  padding: 8px 0;
  border-bottom: 1px solid var(--color-border);
  min-width: 0;
}
.library-import-info {
  display: grid;
  gap: 2px;
  min-width: 0;
  flex: 1 1 18rem;
  overflow-wrap: anywhere;
}
.library-import-existing {
  font-weight: 600;
  color: var(--color-text);
}
.library-import-check {
  display: flex;
  align-items: center;
  gap: 8px;
  min-height: 44px;
}
</style>
