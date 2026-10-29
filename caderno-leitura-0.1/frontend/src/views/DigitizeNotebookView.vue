<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { RouterLink } from 'vue-router'
import { api, errorMessage } from '../services/api'
import { useDigitizeDraft, type UncertainLine } from '../composables/useDigitizeDraft'
import { useUnsavedChanges } from '../composables/useUnsavedChanges'
import EmptyState from '../components/ui/EmptyState.vue'
import LoadingSkeleton from '../components/ui/LoadingSkeleton.vue'
import Icon from '../components/ui/Icon.vue'
import OrganizedSectionsEditor from '../components/OrganizedSectionsEditor.vue'
import { positiveId, type Book, type Chapter } from '../types'
import { DIGITIZE_ACCEPT, DIGITIZE_EXIT_SHORTCUTS, DIGITIZE_SECTIONS } from '../types/digitize'
import { ORGANIZE_SECTIONS, type OrganizeSection } from '../types/organize'
import type { OrganizeReviewItem } from '../composables/useSectionOrganizer'
import type { MediaUsage } from '../types/media'
import { VAULT_STATE_TEXT, shortDate, usageText } from '../utils/mediaFormat'

const draft = useDigitizeDraft({
  status: api.getDigitizeStatus,
  preview: api.previewDigitize,
  createStudy: api.createStudy,
  organize: api.organizeText,
  storePhoto: api.storeStudyPhoto,
  sendFeedback: api.sendOrganizerFeedback,
})
const { state, canSave, uncertainLines } = draft
const organizer = draft.organizer
// Organizar nas 4 seções (feature 089): disponível só se o artefato do organizador estiver íntegro.
const organizeAvailable = ref<boolean | null>(null)
const organizedEditor = ref<InstanceType<typeof OrganizedSectionsEditor> | null>(null)
// A leitura em andamento pode ser abandonada (é cancelada ao sair); só o salvamento segura a navegação.
useUnsavedChanges(() => draft.dirty.value, () => state.phase === 'saving')

const cameraInput = ref<HTMLInputElement | null>(null)
const fileInput = ref<HTMLInputElement | null>(null)
const editor = ref<HTMLTextAreaElement | null>(null)
const reviewHeading = ref<HTMLElement | null>(null)
const resultHeading = ref<HTMLElement | null>(null)

const books = ref<Book[]>([])
const chapters = ref<Chapter[]>([])
const booksLoading = ref(true)
const chaptersLoading = ref(false)
const booksError = ref('')
const chaptersError = ref('')
let bookRequest: AbortController | null = null
let chapterRequest: AbortController | null = null
const statusRequest = new AbortController()

// Foto de conferência (feature 090-C): a caixa some quando não há espaço ou o cofre está trancado.
const mediaUsage = ref<MediaUsage | null>(null)
const photoBlocked = computed(() => {
  const usage = mediaUsage.value
  if (!usage) return ''
  const vault = usage.vault?.state ?? 'ready'
  if (vault !== 'ready') return VAULT_STATE_TEXT[vault]
  if (usage.user.level === 'full') return 'Seu espaço de imagens está cheio; libere espaço para guardar fotos.'
  if (usage.server.level === 'full') return 'O servidor está sem espaço para novas imagens.'
  return ''
})
watch(photoBlocked, (blocked) => { if (blocked) state.keepPhoto = false })

async function loadMediaUsage() {
  try {
    mediaUsage.value = await api.getMediaUsage()
  } catch {
    mediaUsage.value = null // sem o uso, a caixa continua; o servidor recusa com o motivo se faltar espaço
  }
}

const selectedBook = computed(() => books.value.find(item => item.id === positiveId(state.bookId)))
const unavailableDescription = computed(() => state.unavailableReason === 'integrity_failed'
  ? 'Os arquivos do motor de leitura não passaram na verificação de integridade. Reinstale o motor com instalar.py --motor.'
  : 'O motor de leitura não está instalado neste computador. Para ativá-lo, rode instalar.py --motor. Enquanto isso, os outros caminhos continuam disponíveis.')
const noText = computed(() => state.preview?.warnings.some(warning => warning.code === 'no_text') ?? false)
const manyUncertain = computed(() => state.preview?.warnings.find(warning => warning.code === 'many_uncertain'))

async function loadBooks() {
  bookRequest?.abort()
  const controller = new AbortController()
  bookRequest = controller
  booksLoading.value = true
  booksError.value = ''
  try {
    const result = await api.listBooks(controller.signal)
    if (controller.signal.aborted) return
    books.value = result
    if (state.bookId && !selectedBook.value) state.bookId = ''
  } catch (error) {
    if (!controller.signal.aborted) booksError.value = errorMessage(error)
  } finally {
    if (!controller.signal.aborted) booksLoading.value = false
  }
}

async function loadChapters() {
  chapterRequest?.abort()
  const controller = new AbortController()
  chapterRequest = controller
  const preferred = positiveId(state.chapterId)
  state.chapterId = ''
  chapters.value = []
  chaptersError.value = ''
  const id = positiveId(state.bookId)
  chaptersLoading.value = id !== null
  if (id === null) return
  try {
    const result = await api.listChapters(id, controller.signal)
    if (controller.signal.aborted) return
    chapters.value = result
    const kept = result.find(item => item.id === preferred)
    state.chapterId = kept?.id.toString() ?? (result.length === 1 ? String(result[0]!.id) : '')
  } catch (error) {
    if (!controller.signal.aborted) chaptersError.value = errorMessage(error)
  } finally {
    if (!controller.signal.aborted) chaptersLoading.value = false
  }
}

function openPicker(input: HTMLInputElement | null) {
  if (!input) return
  input.value = ''
  input.click()
}

async function onFileChosen(event: Event) {
  const file = (event.target as HTMLInputElement).files?.[0]
  if (!file) return
  const ok = await draft.choose(file)
  await nextTick()
  if (ok) reviewHeading.value?.focus()
  else if (state.phase === 'error') resultHeading.value?.focus()
}

function selectLine(line: UncertainLine) {
  const textarea = editor.value
  if (!textarea || line.revised) return
  const start = state.text.indexOf(line.text)
  if (start < 0) return
  textarea.focus()
  textarea.setSelectionRange(start, start + line.text.length)
  const lineHeight = parseFloat(getComputedStyle(textarea).lineHeight) || 24
  const before = state.text.slice(0, start).split('\n').length - 1
  textarea.scrollTop = Math.max(0, (before - 2) * lineHeight)
}

async function loadOrganizeStatus() {
  try {
    organizeAvailable.value = (await api.getOrganizeStatus(statusRequest.signal)).available
  } catch {
    if (!statusRequest.signal.aborted) organizeAvailable.value = false
  }
}

async function organizeText() {
  if (await draft.organize()) {
    await nextTick()
    const first = await organizedEditor.value?.reveal('summary')
    first?.focus()
  }
}

async function backToSingleText() {
  if (organizer.edited.value && !window.confirm('Voltar para o texto único descarta as alterações feitas nas 4 seções. Continuar?')) return
  draft.unorganize()
  await nextTick()
  editor.value?.focus()
}

async function moveItem(item: OrganizeReviewItem, event: Event) {
  const select = event.target as HTMLSelectElement
  const target = select.value as OrganizeSection
  select.value = ''
  if (target && organizer.move(item.index, target)) {
    const textarea = await organizedEditor.value?.reveal(target)
    textarea?.focus()
  }
}

function sectionLabel(key: OrganizeSection) {
  return ORGANIZE_SECTIONS.find(item => item.key === key)?.label ?? key
}

const extraWarnings = computed(() => organizer.state.warnings.filter(warning => warning.code !== 'suggestion'))

async function save() {
  if (await draft.save()) {
    await nextTick()
    resultHeading.value?.focus()
  }
}

async function startAnother() {
  if (draft.dirty.value && !window.confirm('Descartar o texto desta página e enviar outra foto?')) return
  draft.reset()
  await nextTick()
  resultHeading.value?.focus()
}

watch(() => state.bookId, loadChapters)
onMounted(() => {
  void draft.checkStatus(statusRequest.signal)
  void loadOrganizeStatus()
  void loadBooks()
  void loadMediaUsage()
})
onBeforeUnmount(() => {
  statusRequest.abort()
  bookRequest?.abort()
  chapterRequest?.abort()
  draft.dispose()
})
</script>

<template>
  <main class="digitize-view" role="main" aria-labelledby="digitize-main-title">
    <header class="page-header digitize-header">
      <p class="eyebrow">Ateliê de Fichamento</p>
      <h1 id="digitize-main-title">Digitalizar Caderno</h1>
      <p class="digitize-lead">
        Fotografe uma página do seu caderno. O Leitorum lê o texto manuscrito, você revisa e salva como estudo.
      </p>
    </header>

    <!-- Verificando o motor -->
    <section v-if="state.phase === 'checking'" class="panel" aria-label="Verificando a digitalização">
      <LoadingSkeleton shape="text" :lines="3" height="1.1rem" />
    </section>

    <!-- Motor indisponível: o resto do Leitorum segue funcionando -->
    <section v-else-if="state.phase === 'unavailable'" aria-labelledby="unavailable-heading">
      <EmptyState icon="camera" title="Digitalização indisponível nesta instalação" :description="unavailableDescription">
        <RouterLink class="button primary" to="/importar">Importar texto</RouterLink>
        <RouterLink class="button secondary" to="/inbox">Anotar na Caixa de Entrada</RouterLink>
      </EmptyState>
      <h2 id="unavailable-heading" class="sr-only">Caminhos disponíveis</h2>
      <div class="exit-grid">
        <article v-for="shortcut in DIGITIZE_EXIT_SHORTCUTS" :key="shortcut.routePath" class="panel exit-card">
          <h3>{{ shortcut.title }}</h3>
          <p class="muted-text">{{ shortcut.description }}</p>
          <RouterLink class="text-link" :to="shortcut.routePath">{{ shortcut.actionLabel }}</RouterLink>
        </article>
      </div>
    </section>

    <!-- Escolher a foto -->
    <section v-else-if="state.phase === 'idle'" class="panel capture-panel" aria-labelledby="capture-heading">
      <div class="capture-icon" aria-hidden="true"><Icon name="camera" :size="28" /></div>
      <h2 id="capture-heading" ref="resultHeading" tabindex="-1">Enviar uma página</h2>
      <p class="muted-text">
        Uma foto por estudo. Fotografe a folha inteira, de frente, com boa luz e sem sombra. JPEG, PNG ou WebP, até 20 MB.
      </p>
      <div class="actions">
        <button type="button" class="primary" @click="openPicker(cameraInput)">
          <Icon name="camera" :size="18" aria-hidden="true" /> Tirar foto
        </button>
        <button type="button" class="secondary" @click="openPicker(fileInput)">
          <Icon name="image" :size="18" aria-hidden="true" /> Escolher imagem
        </button>
      </div>
      <input ref="cameraInput" class="file-picker" type="file" :accept="DIGITIZE_ACCEPT" capture="environment" hidden tabindex="-1" @change="onFileChosen" />
      <input ref="fileInput" class="file-picker" type="file" :accept="DIGITIZE_ACCEPT" hidden tabindex="-1" @change="onFileChosen" />
    </section>

    <!-- Lendo -->
    <section v-else-if="state.phase === 'reading'" class="panel reading-panel" aria-labelledby="reading-heading" aria-busy="true">
      <h2 id="reading-heading">Lendo a página</h2>
      <p class="muted-text" role="status">A leitura acontece neste computador e costuma levar de 10 a 20 segundos.</p>
      <div class="review-grid">
        <div class="photo-frame">
          <img v-if="state.previewUrl" :src="state.previewUrl" alt="Foto enviada" class="photo" />
        </div>
        <LoadingSkeleton shape="text" :lines="8" height="1rem" gap="0.75rem" />
      </div>
      <div class="actions">
        <button type="button" class="secondary" @click="draft.cancel()">
          <Icon name="x" :size="18" aria-hidden="true" /> Cancelar
        </button>
      </div>
    </section>

    <!-- Erro -->
    <section v-else-if="state.phase === 'error'" class="panel" aria-labelledby="error-heading">
      <h2 id="error-heading" ref="resultHeading" tabindex="-1">Não foi possível ler esta foto</h2>
      <p class="notice error" role="alert">{{ state.error?.message }}</p>
      <div class="actions">
        <button type="button" class="primary" @click="startAnother">Tentar outra foto</button>
        <RouterLink class="text-link" to="/importar">Importar texto digitado</RouterLink>
      </div>
    </section>

    <!-- Salvo -->
    <section v-else-if="state.phase === 'saved' && state.saved" class="panel" aria-labelledby="saved-heading">
      <p class="success-label" role="status">
        <Icon name="check-circle" :size="18" aria-hidden="true" /> Estudo salvo como rascunho
      </p>
      <h2 id="saved-heading" ref="resultHeading" tabindex="-1">{{ state.saved.title }}</h2>
      <p v-if="state.photoExpiresAt" class="muted-text">
        Foto guardada cifrada até {{ shortDate(state.photoExpiresAt) }}, para conferir na folha original do estudo.
      </p>
      <p v-else-if="state.photoWarning" class="notice error" role="alert">
        A foto não foi guardada: {{ state.photoWarning }}
        <RouterLink to="/minhas-imagens">Abrir Minhas Imagens e Espaço</RouterLink>
      </p>
      <div class="actions">
        <RouterLink class="button primary" :to="{ name: 'study', params: { bookId: state.bookId, studyId: state.saved.id } }">Abrir estudo</RouterLink>
        <button type="button" class="secondary" @click="startAnother">Digitalizar outra página</button>
      </div>
    </section>

    <!-- Revisão -->
    <form v-else class="review-form" @submit.prevent="save">
      <fieldset :disabled="state.phase === 'saving'">
        <h2 id="review-heading" ref="reviewHeading" tabindex="-1">Revisar o texto</h2>
        <div class="notice warning draft-notice" role="note">
          <Icon name="alert-triangle" :size="18" aria-hidden="true" />
          <p>
            <strong>Rascunho lido automaticamente.</strong> O texto pode ter erros de leitura: confira com a foto e corrija
            antes de salvar.
          </p>
        </div>
        <p v-if="manyUncertain" class="notice warning" role="status">{{ manyUncertain.message }}</p>
        <div v-if="noText" class="notice" role="status">
          <p>Nenhuma linha de texto foi encontrada nesta foto. Fotografe a folha inteira, com boa luz e sem sombra.</p>
          <button type="button" class="secondary" @click="startAnother">Tentar outra foto</button>
        </div>

        <div class="review-grid">
          <figure class="photo-frame">
            <img v-if="state.previewUrl" :src="state.previewUrl" alt="Foto da página enviada" class="photo" />
            <figcaption class="muted-text">{{ state.fileName }}</figcaption>
          </figure>

          <div v-if="organizer.state.loading" class="editor-column" aria-busy="true">
            <p class="muted-text" role="status">Organizando o texto nas 4 seções…</p>
            <LoadingSkeleton shape="rect" :lines="4" height="5rem" gap="1rem" />
          </div>

          <div v-else-if="organizer.state.active" class="editor-column organized-column">
            <div class="notice warning draft-notice" role="note">
              <Icon name="alert-triangle" :size="18" aria-hidden="true" />
              <p>
                <strong>Distribuição automática.</strong> A sugestão pode colocar trechos na seção errada: confira cada seção
                antes de salvar. Nenhuma palavra foi alterada.
              </p>
            </div>
            <p v-for="warning in extraWarnings" :key="warning.code" class="notice" role="status">{{ warning.message }}</p>

            <section v-if="organizer.reviewItems.value.length" class="uncertain" aria-labelledby="review-sections-heading">
              <h3 id="review-sections-heading">Seções para conferir ({{ organizer.reviewItems.value.length }})</h3>
              <p class="muted-text">Atribuição incerta. Mova o trecho se a seção sugerida não for a certa.</p>
              <ul class="uncertain-list">
                <li v-for="item in organizer.reviewItems.value" :key="item.index" class="review-item">
                  <span class="review-text">
                    <Icon :name="item.movable ? 'eye' : 'check'" :size="16" aria-hidden="true" />
                    <span class="uncertain-number">{{ sectionLabel(item.section) }}</span>
                    <span class="uncertain-text">{{ item.movable ? item.text : 'já editado' }}</span>
                  </span>
                  <label class="sr-only" :for="`move-${item.index}`">Mover o trecho para outra seção</label>
                  <select :id="`move-${item.index}`" class="move-select" :disabled="!item.movable" @change="moveItem(item, $event)">
                    <option value="">Mover para…</option>
                    <option v-for="option in ORGANIZE_SECTIONS.filter(o => o.key !== item.section)" :key="option.key" :value="option.key">
                      {{ option.label }}
                    </option>
                  </select>
                </li>
              </ul>
            </section>

            <OrganizedSectionsEditor
              ref="organizedEditor"
              v-model:sections="organizer.state.sections"
              id-prefix="digitize-organized"
              :review-counts="organizer.reviewCounts.value"
            />
            <div class="actions">
              <button type="button" class="secondary" @click="backToSingleText">
                <Icon name="rotate-ccw" :size="18" aria-hidden="true" /> Voltar para texto único
              </button>
            </div>
          </div>

          <div v-else class="editor-column">
            <section v-if="uncertainLines.length" class="uncertain" aria-labelledby="uncertain-heading">
              <h3 id="uncertain-heading">Linhas para conferir ({{ uncertainLines.length }})</h3>
              <p class="muted-text">Leitura incerta. Toque numa linha para selecioná-la no texto.</p>
              <ul class="uncertain-list">
                <li v-for="line in uncertainLines" :key="line.index">
                  <button
                    type="button"
                    class="uncertain-item"
                    :disabled="line.revised"
                    :aria-label="line.revised ? `Linha ${line.number}, já revisada` : `Selecionar a linha ${line.number} no texto`"
                    @click="selectLine(line)"
                  >
                    <Icon :name="line.revised ? 'check' : 'eye'" :size="16" aria-hidden="true" />
                    <span class="uncertain-number">Linha {{ line.number }}</span>
                    <span class="uncertain-text">{{ line.revised ? 'já revisada' : line.text }}</span>
                  </button>
                </li>
              </ul>
            </section>

            <div class="field">
              <label for="digitize-text">Texto da página</label>
              <textarea id="digitize-text" ref="editor" v-model="state.text" rows="16" spellcheck="true" />
            </div>
          </div>
        </div>

        <section class="destination" aria-labelledby="destination-heading">
          <h3 id="destination-heading">Salvar como estudo</h3>
          <div v-if="booksError" class="notice error" role="alert">
            <p>{{ booksError }}</p>
            <button type="button" class="secondary" @click="loadBooks">Tentar novamente</button>
          </div>
          <div v-else-if="!booksLoading && books.length === 0" class="notice">
            <p>Cadastre um livro e um capítulo para escolher onde salvar.</p>
            <RouterLink class="text-link" to="/livros">Cadastrar livro</RouterLink>
          </div>
          <div v-if="chaptersError" class="notice error" role="alert">
            <p>{{ chaptersError }}</p>
            <button type="button" class="secondary" @click="loadChapters">Tentar novamente</button>
          </div>
          <p v-else-if="selectedBook && !chaptersLoading && chapters.length === 0" class="notice">
            Este livro ainda não tem capítulos.
            <RouterLink class="text-link" :to="{ name: 'book', params: { bookId: selectedBook.id } }">Adicionar capítulo</RouterLink>
          </p>

          <div class="destination-grid">
            <div class="field">
              <label for="digitize-book">Livro</label>
              <select id="digitize-book" v-model="state.bookId" required :disabled="booksLoading || books.length === 0">
                <option value="">{{ booksLoading ? 'Carregando livros…' : 'Selecione um livro' }}</option>
                <option v-for="book in books" :key="book.id" :value="String(book.id)">{{ book.title }}</option>
              </select>
            </div>
            <div class="field">
              <label for="digitize-chapter">Capítulo</label>
              <select id="digitize-chapter" v-model="state.chapterId" required :disabled="chaptersLoading || !state.bookId || chapters.length === 0">
                <option value="">{{ chaptersLoading ? 'Carregando capítulos…' : 'Selecione um capítulo' }}</option>
                <option v-for="chapter in chapters" :key="chapter.id" :value="String(chapter.id)">{{ chapter.name }}</option>
              </select>
            </div>
            <div class="field title-field">
              <label for="digitize-title">Título</label>
              <input id="digitize-title" v-model="state.title" required maxlength="200" />
            </div>
          </div>

          <fieldset v-if="!organizer.state.active" class="section-choice">
            <legend>Seção do estudo que recebe o texto</legend>
            <div class="section-options">
              <label v-for="option in DIGITIZE_SECTIONS" :key="option.key" class="section-option">
                <input v-model="state.section" type="radio" name="digitize-section" :value="option.key" />
                <span>{{ option.label }}</span>
              </label>
            </div>
            <div class="organize-row">
              <button
                type="button"
                class="secondary"
                :disabled="organizeAvailable !== true || organizer.state.loading || !state.text.trim()"
                @click="organizeText"
              >
                <Icon name="grid" :size="18" aria-hidden="true" /> Organizar nas 4 seções
              </button>
              <p v-if="organizeAvailable === false" class="muted-text small">
                Organização automática indisponível nesta instalação.
              </p>
              <p v-else-if="manyUncertain" class="muted-text small">
                Muitas linhas tiveram leitura incerta: corrija o texto antes de organizar para uma sugestão melhor.
              </p>
              <p v-else class="muted-text small">
                Sugere a divisão do texto entre Resumo, Explicação, Conceitos e Referências, para você conferir.
              </p>
            </div>
            <p v-if="organizer.state.error" class="notice error" role="alert">{{ organizer.state.error.message }}</p>
          </fieldset>

          <div class="keep-photo">
            <label class="keep-photo-option">
              <input
                v-model="state.keepPhoto"
                type="checkbox"
                :disabled="Boolean(photoBlocked)"
                aria-describedby="keep-photo-help"
              >
              <span>Guardar a foto com o estudo para conferência (apagada automaticamente em 30 dias)</span>
            </label>
            <p id="keep-photo-help" class="muted-text small">
              <template v-if="photoBlocked">
                {{ photoBlocked }} <RouterLink to="/minhas-imagens">Minhas Imagens e Espaço</RouterLink>
              </template>
              <template v-else-if="mediaUsage">
                Seu espaço: {{ usageText(mediaUsage.user.used_bytes, mediaUsage.user.quota_bytes) }}. A foto fica
                cifrada e só você a vê; no celular, ela é enviada de novo ao salvar.
              </template>
              <template v-else>A foto fica cifrada e só você a vê.</template>
            </p>
          </div>

          <p v-if="state.error" class="notice error" role="alert">{{ state.error.message }}</p>
          <div class="actions">
            <button type="submit" class="primary" :disabled="!canSave">
              {{ state.phase === 'saving' ? 'Salvando…' : 'Salvar como estudo' }}
            </button>
            <button type="button" class="secondary" @click="startAnother">Descartar e enviar outra</button>
          </div>
          <p class="muted-text small">O texto lido automaticamente, sem as suas correções, fica guardado no estudo como registro de origem.</p>
        </section>
      </fieldset>
    </form>

    <!-- Transparência (US3) -->
    <section class="panel transparency" aria-labelledby="transparency-heading">
      <div class="transparency-icon" aria-hidden="true"><Icon name="lock" :size="22" /></div>
      <div>
        <h2 id="transparency-heading">Onde a leitura acontece</h2>
        <p class="muted-text">
          A foto é processada no computador onde o Leitorum está instalado, inclusive quando você a envia pelo celular na
          rede local. Nada é enviado para a internet.
          <template v-if="state.keepPhoto">
            A leitura apaga a foto ao terminar; como você marcou para guardá-la, ela é enviada de novo ao salvar e fica
            guardada cifrada no seu espaço por 30 dias, salvo se você a mantiver.
          </template>
          <template v-else>
            A foto é apagada assim que a leitura termina; só o texto que você salvar fica no acervo.
          </template>
        </p>
        <p class="muted-text">
          O texto é um rascunho do leitor de licença livre (PP-OCRv6) e erra com frequência em letra cursiva. Revise sempre.
        </p>
      </div>
    </section>
  </main>
</template>

<style scoped>
.digitize-view {
  max-width: 1120px;
  margin: 0 auto;
  padding: calc(var(--space-unit) * 2) calc(var(--space-unit) * 1.25) calc(var(--space-unit) * 4);
  display: flex;
  flex-direction: column;
  gap: calc(var(--space-unit) * 1.5);
  color: var(--color-text);
}

.digitize-header h1 {
  margin: 0;
}

.digitize-lead {
  margin: calc(var(--space-unit) * 0.5) 0 0;
  color: var(--color-muted);
  max-width: 62ch;
}

.panel {
  background: var(--color-surface);
  border: var(--border-width) solid var(--color-border);
  border-radius: var(--radius-card);
  padding: calc(var(--space-unit) * 1.5);
}

h2,
h3 {
  margin: 0 0 calc(var(--space-unit) * 0.5);
}

h2:focus-visible,
h3:focus-visible {
  outline: var(--focus-width, 2px) solid var(--color-accent);
  outline-offset: var(--focus-offset, 2px);
}

h2[tabindex='-1']:focus:not(:focus-visible) {
  outline: none;
}

.muted-text {
  color: var(--color-muted);
  margin: 0 0 calc(var(--space-unit) * 0.75);
}

.small {
  font-size: 0.875rem;
}

.sr-only {
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

.actions {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: calc(var(--space-unit) * 0.75);
  margin-top: calc(var(--space-unit) * 0.75);
}

.actions .button,
.actions button {
  min-height: 44px;
  min-width: 44px;
}

.actions :is(a, button):focus-visible,
.uncertain-item:focus-visible,
.section-option input:focus-visible {
  outline: var(--focus-width, 2px) solid var(--color-accent);
  outline-offset: var(--focus-offset, 2px);
}

.capture-panel {
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.capture-panel .actions {
  justify-content: center;
}

/* A regra global `input { display: block }` do style.css vence o `[hidden]` do navegador:
   sem isto, os dois seletores nativos aparecem abaixo dos botões. Abertos só por openPicker(). */
.file-picker,
.file-picker[hidden] {
  display: none;
}

.capture-icon,
.transparency-icon {
  width: 52px;
  height: 52px;
  border-radius: var(--radius-button);
  display: grid;
  place-items: center;
  background: var(--color-surface-soft);
  color: var(--color-accent);
  margin-bottom: calc(var(--space-unit) * 0.75);
  flex-shrink: 0;
}

.review-grid {
  display: grid;
  grid-template-columns: minmax(0, 2fr) minmax(0, 3fr);
  gap: calc(var(--space-unit) * 1.25);
  align-items: start;
  margin-top: calc(var(--space-unit) * 1);
}

.photo-frame {
  margin: 0;
  position: sticky;
  top: calc(var(--space-unit) * 1);
}

.photo {
  display: block;
  width: 100%;
  max-height: 72vh;
  object-fit: contain;
  border: var(--border-width) solid var(--color-border);
  border-radius: var(--radius-control);
  background: var(--color-surface-soft);
}

.review-form fieldset {
  border: 0;
  margin: 0;
  padding: 0;
  min-width: 0;
}

.review-form > fieldset {
  background: var(--color-surface);
  border: var(--border-width) solid var(--color-border);
  border-radius: var(--radius-card);
  padding: calc(var(--space-unit) * 1.5);
}

.draft-notice {
  display: flex;
  gap: calc(var(--space-unit) * 0.6);
  align-items: flex-start;
}

.draft-notice p {
  margin: 0;
}

.editor-column {
  min-width: 0;
}

.editor-column textarea {
  min-height: 22rem;
  resize: vertical;
  line-height: 1.6;
}

.uncertain {
  border: var(--border-width) solid var(--color-warning-border);
  background: var(--color-warning-bg);
  color: var(--color-warning-text);
  border-radius: var(--radius-control);
  padding: calc(var(--space-unit) * 0.9);
  margin-bottom: calc(var(--space-unit) * 1);
}

.uncertain .muted-text {
  color: inherit;
}

.uncertain-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: calc(var(--space-unit) * 0.4);
  max-height: 14rem;
  overflow-y: auto;
}

.uncertain-item {
  width: 100%;
  min-height: 44px;
  justify-content: flex-start;
  text-align: left;
  white-space: normal;
  background: var(--color-surface);
  color: var(--color-text);
  border: var(--border-width) solid var(--color-border);
}

.uncertain-item:hover:not(:disabled) {
  background: var(--color-surface-hover);
  color: var(--color-text);
}

.uncertain-number {
  font-weight: 700;
  flex-shrink: 0;
}

.uncertain-text {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  min-width: 0;
  font-weight: 400;
}

.destination {
  margin-top: calc(var(--space-unit) * 1.5);
  padding-top: calc(var(--space-unit) * 1.25);
  border-top: var(--border-width) solid var(--color-border);
}

.destination-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: calc(var(--space-unit) * 1);
}

.section-choice legend {
  font-weight: 650;
  margin-bottom: calc(var(--space-unit) * 0.5);
}

.section-options {
  display: flex;
  flex-wrap: wrap;
  gap: calc(var(--space-unit) * 0.5);
}

.section-option {
  display: inline-flex;
  align-items: center;
  gap: calc(var(--space-unit) * 0.5);
  min-height: 44px;
  padding: 0 calc(var(--space-unit) * 0.9);
  border: var(--border-width) solid var(--color-border-strong);
  border-radius: var(--radius-button);
  background: var(--color-surface);
  cursor: pointer;
}

.section-option:has(input:checked) {
  border-color: var(--color-accent);
  background: var(--color-selected-bg);
  color: var(--color-selected-text);
  font-weight: 650;
}

.organize-row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: calc(var(--space-unit) * 0.75);
  margin-top: calc(var(--space-unit) * 0.9);
}

.organize-row button {
  min-height: 44px;
}

.organize-row p {
  margin: 0;
}

.organized-column {
  display: flex;
  flex-direction: column;
  gap: calc(var(--space-unit) * 0.75);
}

.review-item {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: calc(var(--space-unit) * 0.5);
  background: var(--color-surface);
  color: var(--color-text);
  border: var(--border-width) solid var(--color-border);
  border-radius: var(--radius-control);
  padding: calc(var(--space-unit) * 0.4) calc(var(--space-unit) * 0.6);
}

.review-text {
  display: inline-flex;
  align-items: center;
  gap: calc(var(--space-unit) * 0.4);
  flex: 1 1 12rem;
  min-width: 0;
}

.move-select {
  width: auto;
  min-height: 44px;
  flex: 0 0 auto;
}

.move-select:focus-visible {
  outline: var(--focus-width, 2px) solid var(--color-accent);
  outline-offset: var(--focus-offset, 2px);
}

.section-option input {
  width: auto;
  min-height: 0;
  margin: 0;
  accent-color: var(--color-accent);
}

.exit-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: calc(var(--space-unit) * 1);
  margin-top: calc(var(--space-unit) * 1);
}

.exit-card .text-link,
.actions .text-link {
  display: inline-flex;
  align-items: center;
  min-height: 44px;
}

.success-label {
  display: inline-flex;
  align-items: center;
  gap: calc(var(--space-unit) * 0.4);
}

.keep-photo {
  display: grid;
  gap: 0.35rem;
  margin: 1rem 0;
}

.keep-photo-option {
  display: flex;
  align-items: flex-start;
  gap: 0.6rem;
  min-height: 44px;
  font-weight: 600;
  cursor: pointer;
}

.keep-photo-option input {
  width: 22px;
  height: 22px;
  margin: 0.1rem 0 0;
  flex-shrink: 0;
  accent-color: var(--color-accent);
}

.keep-photo-option input:focus-visible {
  outline: 2px solid var(--color-accent);
  outline-offset: 2px;
}

.keep-photo-option:has(input:disabled) {
  cursor: not-allowed;
  color: var(--color-text-secondary);
}

.transparency {
  display: flex;
  gap: calc(var(--space-unit) * 1);
  align-items: flex-start;
}

.transparency .muted-text:last-child {
  margin-bottom: 0;
}

@media (max-width: 768px) {
  .digitize-view {
    padding: calc(var(--space-unit) * 1.25) calc(var(--space-unit) * 0.75) calc(var(--space-unit) * 3);
  }

  .review-grid,
  .destination-grid,
  .exit-grid {
    grid-template-columns: minmax(0, 1fr);
  }

  .photo-frame {
    position: static;
  }

  .photo {
    max-height: 40vh;
  }

  .panel,
  .review-form > fieldset {
    padding: calc(var(--space-unit) * 1);
  }

  .transparency {
    flex-direction: column;
  }

  .actions .button,
  .actions button {
    flex: 1 1 100%;
  }
}

@media (prefers-reduced-motion: reduce) {
  .digitize-view * {
    transition: none !important;
    animation: none !important;
  }
}
</style>
