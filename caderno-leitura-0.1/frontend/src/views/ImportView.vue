<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { api, errorMessage } from '../services/api'
import { useImportDraft } from '../composables/useImportDraft'
import { useUnsavedChanges } from '../composables/useUnsavedChanges'
import StudyEditorFields from '../components/StudyEditorFields.vue'
import StudioViewModeToggle, { type StudioViewMode } from '../components/studies/StudioViewModeToggle.vue'
import FloatingMarkdownToolbar from '../components/studies/FloatingMarkdownToolbar.vue'
import { applyFormatToTextarea, type MarkdownFormatAction } from '../utils/markdownFormatter'
import { useInboxCount } from '../composables/useInboxCount'
import { positiveId, SECTION_LABELS, type Book, type Chapter, type InboxCapture } from '../types'

const route = useRoute()
const draft = useImportDraft(api)
const { state, stale, hasManualChanges, hasAnalysis, canSave, assignUnassignedToSection } = draft
useUnsavedChanges(() => draft.dirty.value, () => state.preparing || state.saving)
const { refreshCount: refreshInboxCount } = useInboxCount()

const promotingInboxId = computed(() => {
  const param = route.query.promote_inbox_id
  return param ? positiveId(param) : null
})
const promotingCapture = ref<InboxCapture | null>(null)
const loadingPromotionCapture = ref(false)

const books = ref<Book[]>([])
const chapters = ref<Chapter[]>([])
const booksLoading = ref(true)
const chaptersLoading = ref(false)
const booksError = ref('')
const chaptersError = ref('')

const reviewHeading = ref<HTMLElement | null>(null)
const sourceInput = ref<HTMLTextAreaElement | null>(null)
const successHeading = ref<HTMLElement | null>(null)

// Studio View & Toolbar States
const viewMode = ref<StudioViewMode>('split')
const activeMobileTab = ref<'source' | 'preview'>('source')
const showFloatingToolbar = ref(false)
const floatingToolbarCoords = ref<{ x: number; y: number } | null>(null)
const sectionPulse = ref(false)

const selectedBook = computed(() => books.value.find(item => item.id === positiveId(state.bookId)))
const selectedChapter = computed(() => chapters.value.find(item => item.id === positiveId(state.chapterId) && item.book_id === positiveId(state.bookId)))

const wordCount = computed(() => {
  const text = state.sourceResponse.trim()
  return text ? text.split(/\s+/).length : 0
})

const charCount = computed(() => state.sourceResponse.length)

let bookRequest: AbortController | null = null
let chapterRequest: AbortController | null = null
let preferredChapter = positiveId(route.query.chapter)
let pulseTimer: ReturnType<typeof setTimeout> | null = null
state.bookId = positiveId(route.query.book)?.toString() ?? ''

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
    const preferred = result.find(item => item.id === preferredChapter)
    state.chapterId = preferred?.id.toString() ?? (result.length === 1 ? String(result[0]!.id) : '')
    preferredChapter = null
  } catch (error) {
    if (!controller.signal.aborted) chaptersError.value = errorMessage(error)
  } finally {
    if (!controller.signal.aborted) chaptersLoading.value = false
  }
}

function triggerSectionPulse() {
  if (pulseTimer) clearTimeout(pulseTimer)
  sectionPulse.value = true
  pulseTimer = setTimeout(() => {
    sectionPulse.value = false
  }, 480)
}

async function prepare() {
  if (hasManualChanges.value && !window.confirm('Preparar novamente substituirá as correções das quatro seções. Suas anotações serão mantidas. Continuar?')) return
  if (await draft.prepare()) {
    triggerSectionPulse()
    activeMobileTab.value = 'preview'
    await nextTick()
    reviewHeading.value?.focus()
  }
}

async function onPaste(event: ClipboardEvent) {
  const text = event.clipboardData?.getData('text')
  if (text && text.trim()) {
    state.sourceResponse = text
    await nextTick()
    if (await draft.prepare()) {
      triggerSectionPulse()
      activeMobileTab.value = 'preview'
      await nextTick()
      reviewHeading.value?.focus()
    }
  }
}

function updateSelection() {
  const textarea = sourceInput.value
  if (!textarea) return

  const start = textarea.selectionStart
  const end = textarea.selectionEnd

  if (start !== end && textarea.value.slice(start, end).trim().length > 0) {
    // Calcula posição próxima à borda superior do editor
    floatingToolbarCoords.value = { x: 16, y: 12 }
    showFloatingToolbar.value = true
  } else {
    showFloatingToolbar.value = false
  }
}

function onTextareaBlur() {
  // Atraso sutil para permitir clique nos botões da barra flutuante
  setTimeout(() => {
    showFloatingToolbar.value = false
  }, 180)
}

function handleFooterFormat(action: MarkdownFormatAction) {
  if (sourceInput.value) {
    applyFormatToTextarea(sourceInput.value, action)
  }
}

async function loadPromotionCapture() {
  if (!promotingInboxId.value) return
  loadingPromotionCapture.value = true
  try {
    const capture = await api.getInboxCapture(promotingInboxId.value)
    promotingCapture.value = capture
    if (capture.content) {
      state.sourceResponse = capture.content
      state.sections.summary = capture.content
      state.sections.references = capture.source_hint || ''
      state.preview = {
        source_response: capture.content,
        summary: capture.content,
        explanation: '',
        concepts: '',
        references: capture.source_hint || '',
        warnings: [],
        unassigned_text: '',
      }
    }
    if (capture.book_id && !state.bookId) {
      state.bookId = String(capture.book_id)
    }
  } catch {
    // Silencioso se não encontrar captura
  } finally {
    loadingPromotionCapture.value = false
  }
}

async function save() {
  if (!selectedBook.value || !selectedChapter.value || chaptersLoading.value) {
    state.saveError = 'Selecione um livro e um capítulo disponíveis.'
    return
  }
  const saved = await draft.save()
  if (saved) {
    if (promotingInboxId.value) {
      try {
        await api.promoteInboxCapture(promotingInboxId.value, { study_id: saved.id })
        await refreshInboxCount()
      } catch {
        // Falha não-fatal no vínculo da promoção
      }
    }
    await nextTick()
    successHeading.value?.focus()
  }
}

async function startAnother() {
  draft.reset()
  activeMobileTab.value = 'source'
  await nextTick()
  sourceInput.value?.focus()
}

watch(() => state.bookId, loadChapters, { immediate: true })
onMounted(async () => {
  await loadBooks()
  if (promotingInboxId.value) {
    await loadPromotionCapture()
  }
})

onBeforeUnmount(() => {
  bookRequest?.abort()
  chapterRequest?.abort()
  if (pulseTimer) clearTimeout(pulseTimer)
})
</script>

<template>
  <div class="import-view">
    <div class="import-studio-view">
      <header class="page-header">
      <p class="eyebrow">Ateliê de Fichamento</p>
      <h1>Importar Fichamento</h1>
    </header>

    <!-- Banner de Promoção de Captura do Inbox -->
    <div v-if="promotingCapture" class="notice info promotion-banner" role="status">
      <p>
        <strong>Promovendo Captura do Inbox:</strong>
        "{{ promotingCapture.content.length > 120 ? promotingCapture.content.slice(0, 120) + '...' : promotingCapture.content }}"
      </p>
      <RouterLink to="/inbox" class="text-link">Cancelar promoção e voltar ao Inbox</RouterLink>
    </div>

    <!-- Tela de Salvamento Concluído -->
    <section v-if="state.saved" class="panel saved-panel" aria-labelledby="saved-heading">
      <p class="success-label" role="status">Salvamento concluído</p>
      <h2 id="saved-heading" ref="successHeading" tabindex="-1">{{ state.saved.title }}</h2>
      <p>{{ selectedBook?.title }} · {{ selectedChapter?.name }}</p>
      <p class="muted">{{ state.saved.location || 'Localização não informada' }}</p>
      <div class="actions wrap">
        <RouterLink class="button primary" :to="{ name: 'study', params: { bookId: state.bookId, studyId: state.saved.id } }">Ler estudo</RouterLink>
        <RouterLink class="text-link" :to="{ name: 'book', params: { bookId: state.bookId }, query: { chapter: state.saved.chapter_id } }">Ver estudos do capítulo</RouterLink>
        <button class="secondary" type="button" @click="startAnother">Importar outro estudo</button>
      </div>
    </section>

    <!-- Formulário do Ateliê Two-Pane Studio -->
    <form v-else class="import-form import-studio-form" @submit.prevent="save">
      <fieldset :disabled="state.preparing || state.saving">
        <!-- Faixa Superior Compacta de Metadados -->
        <header class="import-top-bar" aria-label="Metadados do Estudo">
          <div class="import-meta-fields">
            <div class="meta-field-compact">
              <label for="import-book">Livro</label>
              <select id="import-book" v-model="state.bookId" required :disabled="booksLoading || books.length === 0">
                <option value="">{{ booksLoading ? 'Carregando livros…' : 'Selecione um livro' }}</option>
                <option v-for="book in books" :key="book.id" :value="String(book.id)">{{ book.title }}</option>
              </select>
            </div>

            <div class="meta-field-compact">
              <label for="import-chapter">Capítulo</label>
              <select id="import-chapter" v-model="state.chapterId" required :disabled="chaptersLoading || !state.bookId || chapters.length === 0">
                <option value="">{{ chaptersLoading ? 'Carregando capítulos…' : 'Selecione um capítulo' }}</option>
                <option v-for="chapter in chapters" :key="chapter.id" :value="String(chapter.id)">{{ chapter.name }}</option>
              </select>
            </div>

            <div class="meta-field-compact">
              <label for="import-location">Localização <span class="optional">opcional</span></label>
              <input id="import-location" v-model="state.location" placeholder="Ex.: p. 32–34" />
            </div>

            <div class="meta-field-compact">
              <label for="import-title">Título <span class="optional">opcional</span></label>
              <input id="import-title" v-model="state.title" placeholder="Título do estudo" />
            </div>
          </div>

          <div class="import-top-actions">
            <StudioViewModeToggle v-model="viewMode" />
            <button
              class="primary save-button"
              type="submit"
              :disabled="!canSave || !selectedBook || !selectedChapter || chaptersLoading"
            >
              {{ state.saving ? 'Salvando…' : 'Salvar estudo' }}
            </button>
          </div>
        </header>

        <!-- Avisos e Estados de Carga dos Metadados -->
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
        <p v-if="state.saveError" class="notice error" role="alert">{{ state.saveError }}</p>

        <!-- Abas responsivas para telas intermediárias (< 1024px) -->
        <div class="mobile-studio-tabs" role="tablist" aria-label="Abas do Ateliê">
          <button
            type="button"
            role="tab"
            class="mobile-studio-tab-btn"
            :class="{ 'is-active': activeMobileTab === 'source' }"
            :aria-selected="activeMobileTab === 'source'"
            @click="activeMobileTab = 'source'"
          >
            Texto da Fonte
          </button>
          <button
            type="button"
            role="tab"
            class="mobile-studio-tab-btn"
            :class="{ 'is-active': activeMobileTab === 'preview' }"
            :aria-selected="activeMobileTab === 'preview'"
            @click="activeMobileTab = 'preview'"
          >
            Prévia Estruturada
          </button>
        </div>

        <!-- Área de Trabalho Two-Pane Studio -->
        <main
          class="import-studio-workspace"
          :class="{
            'is-source-only': viewMode === 'source',
            'is-preview-only': viewMode === 'preview',
            'mobile-hide-source': activeMobileTab === 'preview',
            'mobile-hide-preview': activeMobileTab === 'source',
          }"
        >
          <!-- Painel Esquerdo: Editor da Fonte Bruta -->
          <section class="source-pane" aria-labelledby="source-pane-heading">
            <header class="source-pane-header">
              <h2 id="source-pane-heading" class="source-pane-title">Fichamento da Fonte</h2>
              <span class="muted text-xs">Cole o texto integral com seções</span>
            </header>

            <div class="source-editor-wrapper">
              <FloatingMarkdownToolbar
                target-id="source-response"
                :visible="showFloatingToolbar"
                :coords="floatingToolbarCoords"
                @close="showFloatingToolbar = false"
              />

              <textarea
                id="source-response"
                ref="sourceInput"
                v-model="state.sourceResponse"
                class="source-studio-textarea"
                rows="14"
                placeholder="Cole o texto-base do fichamento aqui (ex.: artigos, transcrições, notas)..."
                spellcheck="false"
                @paste="onPaste"
                @select="updateSelection"
                @keyup="updateSelection"
                @mouseup="updateSelection"
                @blur="onTextareaBlur"
              ></textarea>
            </div>

            <!-- Rodapé do Editor com Contadores, Atalhos e Ações Rápidas -->
            <footer class="source-pane-footer">
              <div class="source-stats">
                <span>{{ wordCount }} palavras</span>
                <span>{{ charCount }} caracteres</span>
                <span v-if="stale" class="warning-badge">Texto alterado após análise</span>
              </div>

              <div class="source-footer-actions">
                <!-- Atalhos rápidos acessíveis de formatação no rodapé -->
                <button
                  type="button"
                  class="secondary text-xs"
                  title="Negrito (**texto**)"
                  @click="handleFooterFormat('bold')"
                >
                  B
                </button>
                <button
                  type="button"
                  class="secondary text-xs"
                  title="Itálico (*texto*)"
                  @click="handleFooterFormat('italic')"
                >
                  I
                </button>
                <button
                  type="button"
                  class="secondary text-xs"
                  title="Título H3 (### Título)"
                  @click="handleFooterFormat('heading')"
                >
                  H3
                </button>
                <button
                  type="button"
                  class="secondary text-xs"
                  title="Inserir Tabela"
                  @click="handleFooterFormat('table')"
                >
                  Tabela
                </button>

                <!-- Botão de Análise Manual -->
                <button
                  type="button"
                  class="primary"
                  :disabled="!state.sourceResponse.trim() || state.preparing"
                  @click="prepare"
                >
                  {{ state.preparing ? 'Analisando…' : stale ? 'Atualizar prévia' : state.preview ? 'Reanalisar texto' : 'Analisar texto' }}
                </button>
              </div>
            </footer>
          </section>

          <!-- Painel Direito: Prévia Estruturada Viva -->
          <section class="preview-pane" aria-labelledby="preview-pane-heading">
            <header class="preview-pane-header">
              <h2 id="preview-pane-heading" ref="reviewHeading" tabindex="-1" class="preview-pane-title">Prévia Estruturada</h2>
              <span class="muted text-xs">{{ state.preview ? '4 Seções Cognitivas' : 'Aguardando texto da fonte' }}</span>
            </header>

            <p v-if="state.previewError" class="notice error" role="alert">{{ state.previewError }}</p>
            <p v-if="state.preview && !hasAnalysis" class="notice warning">Preencha ao menos uma das quatro seções para salvar.</p>

            <!-- Avisos da Análise -->
            <div v-if="state.preview && state.preview.warnings.length" class="notice warning" role="status">
              <h3>Avisos da análise</h3>
              <ul>
                <li v-for="(warning, index) in state.preview.warnings" :key="index">
                  {{ warning.message }}<span v-if="warning.line !== null" class="warning-line"> Linha {{ warning.line }}.</span>
                </li>
              </ul>
            </div>

            <!-- Conteúdo Não Classificado com botões de 1 clique -->
            <div
              v-if="state.preview && state.preview.unassigned_text.trim()"
              class="unassigned-card notice warning"
              role="region"
              aria-label="Conteúdo Não Classificado"
            >
              <div class="unassigned-header">
                <h3>Conteúdo Não Classificado</h3>
                <p class="field-hint">O trecho abaixo não foi identificado como título de seção. Atribua-o com 1 clique a uma das seções ou salve direto (será anexado à Explicação):</p>
              </div>
              <pre class="unassigned-preview">{{ state.preview.unassigned_text }}</pre>
              <div class="unassigned-actions">
                <span class="action-label">Mover para:</span>
                <button type="button" class="button secondary small" @click="assignUnassignedToSection('summary')">Resumo</button>
                <button type="button" class="button secondary small" @click="assignUnassignedToSection('explanation')">Explicação</button>
                <button type="button" class="button secondary small" @click="assignUnassignedToSection('concepts')">Conceitos</button>
                <button type="button" class="button secondary small" @click="assignUnassignedToSection('references')">Referências</button>
              </div>
            </div>

            <!-- Cartões Estruturados das Quatro Seções -->
            <div class="preview-cards-stack" role="region" aria-label="Seções Estruturadas">
              <article
                v-for="sec in SECTION_LABELS"
                :key="sec.key"
                class="preview-section-card"
                :class="{
                  'is-empty': !state.sections[sec.key].trim(),
                  'pulse-active': sectionPulse && !!state.sections[sec.key].trim(),
                }"
              >
                <header class="section-card-header">
                  <h3 class="section-card-title">{{ sec.label }}</h3>
                  <span v-if="!state.sections[sec.key].trim()" class="empty-badge">Vazia</span>
                </header>
                <div class="section-card-content">
                  <p v-if="state.sections[sec.key].trim()" class="section-text">{{ state.sections[sec.key] }}</p>
                  <p v-else class="section-card-empty-msg">Nenhum conteúdo identificado para esta seção.</p>
                </div>
              </article>
            </div>

            <!-- Ajuste manual detalhado (Accordion opcional) -->
            <details v-if="state.preview" class="manual-adjustment-panel">
              <summary class="manual-adjustment-summary">
                <span>Ajuste manual detalhado e anotações pessoais (opcional)</span>
              </summary>
              <div class="manual-adjustment-body">
                <StudyEditorFields
                  id-prefix="import"
                  v-model:title="state.title"
                  v-model:location="state.location"
                  v-model:template-id="state.template_id"
                  v-model:sections="state.sections"
                  v-model:notes="state.notes"
                />
              </div>
            </details>
          </section>
        </main>
      </fieldset>
    </form>
    </div>
  </div>
</template>

<style scoped>
.preview-cards-stack {
  display: flex;
  flex-direction: column;
  gap: calc(var(--space-unit) * 1);
}

.warning-badge {
  font-size: 0.75rem;
  padding: 2px 6px;
  background-color: var(--color-page);
  border: 1px solid var(--color-border);
  border-radius: 4px;
  color: var(--color-text-muted);
}

.unassigned-card {
  margin: 0;
  padding: calc(var(--space-unit) * 1.25);
  border-radius: var(--radius-card, 8px);
}

.unassigned-header h3 {
  margin: 0 0 0.5rem 0;
}

.unassigned-preview {
  background: var(--color-page);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm, 6px);
  padding: 0.75rem;
  white-space: pre-wrap;
  font-family: inherit;
  font-size: 0.875rem;
  max-height: 160px;
  overflow-y: auto;
  margin: 0.75rem 0;
}

.unassigned-actions {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.action-label {
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--color-text-muted);
}

.unassigned-actions .button.small {
  padding: 0.35rem 0.75rem;
  font-size: 0.8125rem;
}

.section-text {
  white-space: pre-wrap;
  font-size: 0.9375rem;
  line-height: 1.6;
  margin: 0;
  color: var(--color-text);
}

.manual-adjustment-panel {
  margin-top: 0.5rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-card, 8px);
  background: var(--color-surface);
}

.manual-adjustment-summary {
  padding: 0.875rem 1.25rem;
  cursor: pointer;
  font-weight: 600;
  font-size: 0.875rem;
  color: var(--color-text);
  user-select: none;
  outline: none;
}

.manual-adjustment-summary:focus-visible {
  outline: 2px solid var(--color-accent);
}

.manual-adjustment-body {
  padding: 0 1.25rem 1.25rem 1.25rem;
  border-top: 1px solid var(--color-border);
  background: var(--color-surface);
  color: var(--color-text);
}
</style>
