<script setup lang="ts">
/**
 * F0.11.03 (spec 105): importar destaques do Kindle (My Clippings.txt) e do Kobo (KoboReader.sqlite) para a
 * Mesa de Triagem. Passos: enviar o arquivo (prévia, nada gravado) → escolher o livro de cada grupo → importar.
 */
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { api, errorMessage } from '../services/api'
import type { Book, EreaderChoice, EreaderImportResponse, EreaderPreviewResponse } from '../types'

type Step = 'pick' | 'review' | 'done'

const step = ref<Step>('pick')
const file = ref<File | null>(null)
const busy = ref(false)
const error = ref('')
const liveMessage = ref('')
const preview = ref<EreaderPreviewResponse | null>(null)
const result = ref<EreaderImportResponse | null>(null)
const myBooks = ref<Book[]>([])
/** Por livro do arquivo: 'create', 'skip' ou o id do livro do acervo (texto, por causa do <select>). */
const destinations = ref<Record<string, string>>({})

const sourceLabel = computed(() => (preview.value?.source === 'kobo' ? 'Kobo' : 'Kindle'))
const totalNew = computed(() =>
  (preview.value?.books ?? [])
    .filter((book) => destinations.value[book.key] !== 'skip')
    .reduce((sum, book) => sum + book.new_count, 0),
)

onMounted(async () => {
  try {
    myBooks.value = (await api.listBooks()).filter((book) => !book.deleted_at)
  } catch {
    myBooks.value = []
  }
})

function onFileChange(event: Event) {
  const input = event.target as HTMLInputElement
  file.value = input.files?.[0] ?? null
  error.value = ''
}

async function sendPreview() {
  if (!file.value || busy.value) return
  busy.value = true
  error.value = ''
  liveMessage.value = 'Lendo o arquivo…'
  try {
    const data = await api.previewEreaderImport(file.value)
    preview.value = data
    destinations.value = Object.fromEntries(
      data.books.map((book) => [
        book.key,
        book.suggested_action === 'existing' && book.suggested_book_id ? String(book.suggested_book_id) : 'create',
      ]),
    )
    step.value = 'review'
    liveMessage.value = `Encontrei ${data.books.length} ${data.books.length === 1 ? 'livro' : 'livros'} no arquivo do ${data.source === 'kobo' ? 'Kobo' : 'Kindle'}.`
  } catch (err) {
    error.value = errorMessage(err)
    liveMessage.value = ''
  } finally {
    busy.value = false
  }
}

function choicesPayload(): EreaderChoice[] {
  return (preview.value?.books ?? []).map((book) => {
    const value = destinations.value[book.key] ?? 'create'
    if (value === 'skip' || value === 'create') return { key: book.key, action: value }
    return { key: book.key, action: 'existing', book_id: Number(value) }
  })
}

async function runImport() {
  if (!file.value || busy.value) return
  busy.value = true
  error.value = ''
  liveMessage.value = 'Importando…'
  try {
    result.value = await api.importEreaderHighlights(file.value, choicesPayload())
    step.value = 'done'
    liveMessage.value = `${result.value.created} ${result.value.created === 1 ? 'captura criada' : 'capturas criadas'}.`
  } catch (err) {
    error.value = errorMessage(err)
    liveMessage.value = ''
  } finally {
    busy.value = false
  }
}

function restart() {
  step.value = 'pick'
  file.value = null
  preview.value = null
  result.value = null
  error.value = ''
  liveMessage.value = ''
}
</script>

<template>
  <section class="ereader-view wrap" aria-labelledby="ereader-heading">
    <header class="page-header">
      <p class="eyebrow">Mesa de Triagem</p>
      <h1 id="ereader-heading">Importar do Kindle ou Kobo</h1>
      <p class="ereader-lead">
        Os destaques entram na Mesa de Triagem como capturas do livro. Depois, na página do livro, a bandeja ajuda a
        levá-los para os capítulos e transformá-los em estudos.
      </p>
    </header>

    <p class="visually-hidden" role="status" aria-live="polite">{{ liveMessage }}</p>
    <p v-if="error" class="notice error" role="alert">{{ error }}</p>

    <!-- 1. Arquivo -->
    <section v-if="step === 'pick'" class="panel ereader-panel" aria-labelledby="ereader-pick-heading">
      <h2 id="ereader-pick-heading">1. Escolha o arquivo</h2>
      <ul class="ereader-help">
        <li><strong>Kindle:</strong> conecte pelo cabo USB e abra <code>documents/My Clippings.txt</code>.</li>
        <li><strong>Kobo:</strong> conecte pelo cabo USB e abra <code>.kobo/KoboReader.sqlite</code> (pasta oculta).</li>
      </ul>
      <label class="ereader-file">
        <span>Arquivo do leitor digital</span>
        <input type="file" accept=".txt,.sqlite,text/plain,application/octet-stream" @change="onFileChange" />
      </label>
      <p class="ereader-muted">Nada é gravado nesta etapa, e o arquivo não fica guardado no servidor.</p>
      <div class="ereader-actions">
        <button type="button" class="primary" :disabled="!file || busy" @click="sendPreview">
          {{ busy ? 'Lendo…' : 'Ver o que tem no arquivo' }}
        </button>
        <RouterLink to="/inbox" class="ereader-link">Voltar à Mesa de Triagem</RouterLink>
      </div>
    </section>

    <!-- 2. Prévia e destino -->
    <section v-else-if="step === 'review' && preview" class="panel ereader-panel" aria-labelledby="ereader-review-heading">
      <h2 id="ereader-review-heading">2. Escolha onde cada livro entra</h2>
      <p class="ereader-muted">
        Arquivo do {{ sourceLabel }}: {{ preview.total_entries }} {{ preview.total_entries === 1 ? 'destaque' : 'destaques' }}
        em {{ preview.books.length }} {{ preview.books.length === 1 ? 'livro' : 'livros' }}<template v-if="preview.skipped">
        ({{ preview.skipped }} {{ preview.skipped === 1 ? 'marcador ignorado' : 'marcadores ignorados' }})</template>.
      </p>
      <ul class="ereader-books">
        <li v-for="book in preview.books" :key="book.key" class="ereader-book">
          <div class="ereader-book-info">
            <strong class="ereader-book-title">{{ book.title }}</strong>
            <span v-if="book.author" class="ereader-muted">{{ book.author }}</span>
            <span class="ereader-muted">
              {{ book.new_count }} {{ book.new_count === 1 ? 'novo' : 'novos' }}<template v-if="book.duplicate_count">
              · {{ book.duplicate_count }} já na Mesa</template><template v-if="book.notes">
              · {{ book.notes }} com nota</template>
            </span>
          </div>
          <label class="ereader-destination">
            <span>Destino</span>
            <select v-model="destinations[book.key]">
              <option value="create">Criar o livro "{{ book.title }}"</option>
              <option v-for="own in myBooks" :key="own.id" :value="String(own.id)">{{ own.title }}</option>
              <option value="skip">Não importar este livro</option>
            </select>
          </label>
        </li>
      </ul>
      <div class="ereader-actions">
        <button type="button" class="primary" :disabled="busy || totalNew === 0" @click="runImport">
          {{ busy ? 'Importando…' : `Importar ${totalNew} ${totalNew === 1 ? 'destaque' : 'destaques'}` }}
        </button>
        <button type="button" class="quiet ereader-secondary" :disabled="busy" @click="restart">Escolher outro arquivo</button>
      </div>
    </section>

    <!-- 3. Resultado -->
    <section v-else-if="step === 'done' && result" class="panel ereader-panel" aria-labelledby="ereader-done-heading">
      <h2 id="ereader-done-heading">Pronto</h2>
      <p>
        {{ result.created }} {{ result.created === 1 ? 'captura criada' : 'capturas criadas' }}<template v-if="result.duplicates">;
        {{ result.duplicates }} {{ result.duplicates === 1 ? 'já estava' : 'já estavam' }} na Mesa e {{ result.duplicates === 1 ? 'foi pulada' : 'foram puladas' }}</template>.
      </p>
      <ul class="ereader-books">
        <li v-for="book in result.books" :key="book.key" class="ereader-book">
          <div class="ereader-book-info">
            <strong class="ereader-book-title">{{ book.book_title }}</strong>
            <span class="ereader-muted">
              {{ book.created }} {{ book.created === 1 ? 'nova' : 'novas' }}<template v-if="book.book_created"> · livro criado</template>
            </span>
          </div>
          <div class="ereader-actions">
            <RouterLink :to="{ name: 'book', params: { bookId: book.book_id } }" class="ereader-link">Abrir o livro</RouterLink>
            <RouterLink :to="{ path: '/inbox', query: { livro: String(book.book_id) } }" class="ereader-link">Ver na Mesa</RouterLink>
          </div>
        </li>
      </ul>
      <div class="ereader-actions">
        <button type="button" class="quiet ereader-secondary" @click="restart">Importar outro arquivo</button>
      </div>
    </section>
  </section>
</template>

<style scoped>
.ereader-view {
  max-width: 52rem;
  margin: 0 auto;
  padding-block: 1.5rem 3rem;
}

.ereader-lead,
.ereader-muted {
  color: var(--color-muted);
}

.ereader-lead {
  margin: 0.5rem 0 0;
  line-height: 1.55;
}

.ereader-muted {
  margin: 0;
  font-size: 0.875rem;
}

.ereader-panel {
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
  margin-top: 1.25rem;
  min-width: 0;
}

.ereader-panel h2 {
  margin: 0;
  font-size: 1.15rem;
}

.ereader-help {
  margin: 0;
  padding-left: 1.2rem;
  line-height: 1.6;
  color: var(--color-text);
}

.ereader-help code {
  overflow-wrap: anywhere;
}

.ereader-file,
.ereader-destination {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-muted);
  min-width: 0;
}

.ereader-file input,
.ereader-destination select {
  min-height: 44px;
  max-width: 100%;
  color: var(--color-text);
}

.ereader-actions {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.5rem 1rem;
}

.ereader-secondary {
  --quiet-border: var(--color-border-strong, var(--color-border));
  min-height: 44px;
}

.ereader-link {
  display: inline-flex;
  align-items: center;
  min-height: 44px;
  color: var(--color-link);
  text-decoration: underline;
  text-underline-offset: 3px;
}

.ereader-books {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.ereader-book {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  justify-content: space-between;
  gap: 0.5rem 1rem;
  padding: 0.75rem 0;
  border-bottom: 1px solid var(--color-border);
  min-width: 0;
}

.ereader-book-info {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
  min-width: 0;
  flex: 1 1 16rem;
}

.ereader-book-title {
  overflow-wrap: anywhere;
  color: var(--color-text);
}

.ereader-destination {
  flex: 1 1 14rem;
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
