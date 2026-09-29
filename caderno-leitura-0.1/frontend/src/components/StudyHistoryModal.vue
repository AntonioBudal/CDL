<script setup lang="ts">
import { computed, nextTick, ref, watch } from 'vue'
import { api, errorMessage } from '../services/api'
import Icon from './ui/Icon.vue'
import MarkdownContent from './MarkdownContent.vue'
import StudyDiffViewer from './StudyDiffViewer.vue'
import type { Study, StudyDiffResult, StudyVersionDetail, StudyVersionSummary } from '../types.ts'

const props = defineProps<{
  open: boolean
  studyId: number
  canEdit: boolean
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'restored', study: Study): void
}>()

const loadingVersions = ref(false)
const versions = ref<StudyVersionSummary[]>([])
const selectedVersionId = ref<number | null>(null)

const loadingDetail = ref(false)
const versionDetail = ref<StudyVersionDetail | null>(null)

const activeTab = ref<'inspection' | 'diff'>('diff')
const loadingDiff = ref(false)
const diffResult = ref<StudyDiffResult | null>(null)

const confirmModalOpen = ref(false)
const restoring = ref(false)
const actionError = ref('')
const closeButtonRef = ref<HTMLButtonElement | null>(null)

const selectedVersion = computed(() => {
  return versions.value.find((v) => v.id === selectedVersionId.value) || null
})

const isCurrentSelected = computed(() => {
  return selectedVersion.value?.is_current === true
})

function formatDate(isoString: string): string {
  if (!isoString) return ''
  try {
    const d = new Date(isoString)
    return new Intl.DateTimeFormat('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    }).format(d)
  } catch {
    return isoString
  }
}

async function loadVersions() {
  loadingVersions.value = true
  actionError.value = ''
  try {
    const data = await api.listStudyVersions(props.studyId)
    versions.value = data
    if (data.length > 0) {
      // Por padrão, se houver mais de uma versão, seleciona a penúltima para ver o diff contra a atual
      const defaultId = data.length > 1 ? data[1].id : data[0].id
      await selectVersion(defaultId)
    } else {
      selectedVersionId.value = null
      versionDetail.value = null
      diffResult.value = null
    }
  } catch (err) {
    actionError.value = errorMessage(err)
  } finally {
    loadingVersions.value = false
  }
}

async function selectVersion(id: number) {
  selectedVersionId.value = id
  await Promise.all([loadDetail(id), loadDiff(id)])
}

async function loadDetail(id: number) {
  loadingDetail.value = true
  try {
    versionDetail.value = await api.getStudyVersionDetail(props.studyId, id)
  } catch (err) {
    actionError.value = errorMessage(err)
  } finally {
    loadingDetail.value = false
  }
}

async function loadDiff(id: number) {
  loadingDiff.value = true
  try {
    diffResult.value = await api.getStudyVersionDiff(props.studyId, id)
  } catch (err) {
    actionError.value = errorMessage(err)
  } finally {
    loadingDiff.value = false
  }
}

async function executeRestore() {
  if (!selectedVersionId.value) return
  restoring.value = true
  actionError.value = ''
  try {
    const updated = await api.restoreStudyVersion(props.studyId, selectedVersionId.value)
    confirmModalOpen.value = false
    emit('restored', updated)
    emit('close')
  } catch (err) {
    actionError.value = errorMessage(err)
  } finally {
    restoring.value = false
  }
}

function onKeydown(e: KeyboardEvent) {
  if (!props.open) return
  if (e.key === 'Escape') {
    if (confirmModalOpen.value) {
      confirmModalOpen.value = false
    } else {
      emit('close')
    }
  }
}

watch(
  () => props.open,
  (isOpen) => {
    if (isOpen) {
      loadVersions()
      nextTick(() => {
        closeButtonRef.value?.focus()
      })
    } else {
      confirmModalOpen.value = false
      actionError.value = ''
    }
  },
  { immediate: true },
)
</script>

<template>
  <div
    v-if="open"
    class="modal-backdrop"
    role="presentation"
    @click.self="emit('close')"
    @keydown="onKeydown"
  >
    <div
      class="modal-container history-modal"
      role="dialog"
      aria-modal="true"
      aria-labelledby="history-modal-title"
    >
      <header class="modal-header">
        <div class="header-info">
          <h2 id="history-modal-title">Histórico de Versões</h2>
          <p class="header-desc">Consulte a evolução do estudo, compare diferenças ou recupere versões passadas.</p>
        </div>
        <button
          ref="closeButtonRef"
          type="button"
          class="close-button"
          aria-label="Fechar histórico"
          @click="emit('close')"
        >
          <Icon name="x" :size="20" />
        </button>
      </header>

      <div v-if="actionError" class="notice error" role="alert">
        <p>{{ actionError }}</p>
      </div>

      <div v-if="loadingVersions" class="state-loading">
        <p>Carregando histórico de versões…</p>
      </div>

      <div v-else-if="versions.length === 0" class="empty-state">
        <p>Nenhuma versão anterior registrada para este estudo.</p>
        <p class="muted-text">
          O sistema arquiva automaticamente um snapshot imutável a cada salvamento com alterações de conteúdo.
        </p>
      </div>

      <div v-else class="history-layout">
        <!-- Coluna da Esquerda: Linha do Tempo de Versões -->
        <aside class="timeline-sidebar" aria-label="Linha do tempo de versões">
          <ul class="version-list" role="list">
            <li
              v-for="v in versions"
              :key="v.id"
              class="version-card"
              :class="{
                selected: v.id === selectedVersionId,
                'is-current': v.is_current,
              }"
              role="button"
              tabindex="0"
              :aria-selected="v.id === selectedVersionId"
              @click="selectVersion(v.id)"
              @keydown.enter="selectVersion(v.id)"
              @keydown.space.prevent="selectVersion(v.id)"
            >
              <div class="version-card-top">
                <span class="version-number-tag">v{{ v.version_number }}</span>
                <span v-if="v.is_current" class="current-badge">Atual</span>
                <span v-else class="summary-badge">{{ v.change_summary }}</span>
              </div>
              <p class="version-date">{{ formatDate(v.updated_at || v.created_at) }}</p>
              <div class="version-meta">
                <span class="author-name">{{ v.author_name || 'Autor' }}</span>
                <span class="meta-dot">·</span>
                <span>{{ v.char_count }} caracteres</span>
                <template v-if="v.highlights_count > 0">
                  <span class="meta-dot">·</span>
                  <span>{{ v.highlights_count }} marcações</span>
                </template>
              </div>
            </li>
          </ul>
        </aside>

        <!-- Coluna da Direita: Inspeção e Diff -->
        <main class="version-viewport" aria-label="Detalhes da versão selecionada">
          <header v-if="selectedVersion" class="viewport-header">
            <div class="viewport-meta">
              <h3>
                Versão {{ selectedVersion.version_number }}
                <span v-if="selectedVersion.is_current" class="current-tag">(Estado Atual)</span>
              </h3>
              <p class="viewport-sub">
                Registrada em {{ formatDate(selectedVersion.created_at) }} por
                <strong>{{ selectedVersion.author_name || 'Autor' }}</strong>
              </p>
            </div>

            <div class="viewport-controls">
              <div class="tab-toggle" role="tablist" aria-label="Modo de visualização">
                <button
                  type="button"
                  role="tab"
                  :aria-selected="activeTab === 'diff'"
                  :class="{ active: activeTab === 'diff' }"
                  @click="activeTab = 'diff'"
                >
                  Comparar Alterações
                </button>
                <button
                  type="button"
                  role="tab"
                  :aria-selected="activeTab === 'inspection'"
                  :class="{ active: activeTab === 'inspection' }"
                  @click="activeTab = 'inspection'"
                >
                  Inspeção Completa
                </button>
              </div>

              <button
                v-if="canEdit && !isCurrentSelected"
                type="button"
                class="primary restore-button"
                aria-label="Restaurar esta versão no estudo ativo"
                @click="confirmModalOpen = true"
              >
                <Icon name="rotate-ccw" :size="16" />
                Restaurar versão
              </button>
            </div>
          </header>

          <div class="viewport-body">
            <!-- Aba Diff -->
            <div v-if="activeTab === 'diff'" class="diff-container">
              <div v-if="loadingDiff" class="state-loading">
                <p>Calculando diferenças entre versões…</p>
              </div>
              <div v-else-if="diffResult">
                <StudyDiffViewer :diff="diffResult" />
              </div>
            </div>

            <!-- Aba Inspeção -->
            <div v-else-if="activeTab === 'inspection'" class="inspection-container">
              <div v-if="loadingDetail" class="state-loading">
                <p>Carregando conteúdo da versão…</p>
              </div>
              <article v-else-if="versionDetail" class="version-article">
                <h2 class="version-study-title">{{ versionDetail.title }}</h2>

                <section class="section-block">
                  <h4 class="section-heading">Resumo</h4>
                  <MarkdownContent
                    v-if="versionDetail.summary.trim()"
                    :content="versionDetail.summary"
                    :highlights="versionDetail.highlights.filter((h) => h.section === 'summary')"
                  />
                  <p v-else class="empty-field">Seção vazia nesta versão.</p>
                </section>

                <section class="section-block">
                  <h4 class="section-heading">Argumentos</h4>
                  <MarkdownContent
                    v-if="versionDetail.explanation.trim()"
                    :content="versionDetail.explanation"
                    :highlights="versionDetail.highlights.filter((h) => h.section === 'explanation')"
                  />
                  <p v-else class="empty-field">Seção vazia nesta versão.</p>
                </section>

                <section class="section-block">
                  <h4 class="section-heading">Conceitos</h4>
                  <MarkdownContent
                    v-if="versionDetail.concepts.trim()"
                    :content="versionDetail.concepts"
                    :highlights="versionDetail.highlights.filter((h) => h.section === 'concepts')"
                  />
                  <p v-else class="empty-field">Seção vazia nesta versão.</p>
                </section>

                <section class="section-block">
                  <h4 class="section-heading">Citações e Referências</h4>
                  <MarkdownContent
                    v-if="versionDetail.references.trim()"
                    :content="versionDetail.references"
                    :highlights="versionDetail.highlights.filter((h) => h.section === 'references')"
                  />
                  <p v-else class="empty-field">Seção vazia nesta versão.</p>
                </section>

                <section v-if="versionDetail.notes.trim()" class="section-block">
                  <h4 class="section-heading">Anotações</h4>
                  <p class="notes-text">{{ versionDetail.notes }}</p>
                </section>
              </article>
            </div>
          </div>
        </main>
      </div>

      <!-- Diálogo Modal de Confirmação de Restauração -->
      <div
        v-if="confirmModalOpen"
        class="confirm-overlay"
        role="presentation"
        @click.self="confirmModalOpen = false"
      >
        <div
          class="confirm-card"
          role="alertdialog"
          aria-modal="true"
          aria-labelledby="confirm-title"
          aria-describedby="confirm-desc"
        >
          <h3 id="confirm-title">Confirmar restauração de versão</h3>
          <p id="confirm-desc">
            Tem certeza de que deseja restaurar a <strong>Versão {{ selectedVersion?.version_number }}</strong>?
            O estado presente do seu estudo será automaticamente salvo no histórico antes da substituição, garantindo que nenhum trabalho seja perdido.
          </p>
          <div class="confirm-actions">
            <button
              type="button"
              class="secondary"
              :disabled="restoring"
              @click="confirmModalOpen = false"
            >
              Cancelar
            </button>
            <button
              type="button"
              class="primary danger-confirm"
              :disabled="restoring"
              @click="executeRestore"
            >
              <span v-if="restoring">Restaurando…</span>
              <span v-else>Confirmar restauração</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.modal-backdrop {
  position: fixed;
  inset: 0;
  background-color: rgba(0, 0, 0, 0.55);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1.5rem;
  backdrop-filter: blur(2px);
}

.history-modal {
  width: 100%;
  max-width: 1080px;
  height: 85vh;
  max-height: 860px;
  background: var(--color-surface, #fff);
  border-radius: 12px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  position: relative;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 1.25rem 1.75rem;
  border-bottom: 1px solid var(--color-border-subtle, rgba(0, 0, 0, 0.08));
  background-color: var(--color-surface-subtle, rgba(0, 0, 0, 0.02));
}

.modal-header h2 {
  margin: 0 0 0.25rem;
  font-size: 1.25rem;
  font-weight: 600;
}

.header-desc {
  margin: 0;
  font-size: 0.875rem;
  color: var(--color-text-muted, #666);
}

.close-button {
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 0.375rem;
  border-radius: 6px;
  color: var(--color-text-muted, #666);
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-button:hover {
  background-color: var(--color-surface-hover, rgba(0, 0, 0, 0.05));
  color: var(--color-text, #111);
}

.history-layout {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.timeline-sidebar {
  width: 320px;
  border-right: 1px solid var(--color-border-subtle, rgba(0, 0, 0, 0.08));
  background-color: var(--color-surface-subtle, rgba(0, 0, 0, 0.015));
  overflow-y: auto;
  padding: 1rem;
  display: flex;
  flex-direction: column;
}

.version-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.625rem;
}

.version-card {
  padding: 0.875rem;
  border-radius: 8px;
  border: 1px solid var(--color-border, rgba(0, 0, 0, 0.1));
  background: var(--color-surface, #fff);
  cursor: pointer;
  transition: all 0.15s ease;
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}

.version-card:hover {
  border-color: var(--color-primary, #2563eb);
  background-color: var(--color-surface-hover, rgba(37, 99, 235, 0.02));
}

.version-card.selected {
  border-color: var(--color-primary, #2563eb);
  box-shadow: 0 0 0 1px var(--color-primary, #2563eb);
  background-color: var(--color-primary-subtle, rgba(37, 99, 235, 0.05));
}

.version-card-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.version-number-tag {
  font-weight: 700;
  font-size: 0.9375rem;
  color: var(--color-text, inherit);
}

.current-badge {
  font-size: 0.6875rem;
  font-weight: 600;
  text-transform: uppercase;
  background-color: #d1fae5;
  color: #065f46;
  padding: 0.125rem 0.5rem;
  border-radius: 4px;
}

.summary-badge {
  font-size: 0.75rem;
  color: var(--color-text-muted, #666);
  background-color: var(--color-surface-subtle, rgba(0, 0, 0, 0.05));
  padding: 0.125rem 0.375rem;
  border-radius: 4px;
}

.version-date {
  margin: 0;
  font-size: 0.8125rem;
  color: var(--color-text-muted, #555);
}

.version-meta {
  font-size: 0.75rem;
  color: var(--color-text-subtle, #888);
  display: flex;
  align-items: center;
  gap: 0.25rem;
  flex-wrap: wrap;
}

.version-viewport {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: var(--color-surface, #fff);
}

.viewport-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.75rem;
  border-bottom: 1px solid var(--color-border-subtle, rgba(0, 0, 0, 0.08));
  gap: 1rem;
  flex-wrap: wrap;
}

.viewport-meta h3 {
  margin: 0 0 0.25rem;
  font-size: 1.125rem;
  font-weight: 600;
}

.current-tag {
  font-size: 0.875rem;
  font-weight: 500;
  color: #059669;
  margin-left: 0.375rem;
}

.viewport-sub {
  margin: 0;
  font-size: 0.8125rem;
  color: var(--color-text-muted, #666);
}

.viewport-controls {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.tab-toggle {
  display: flex;
  background-color: var(--color-surface-subtle, rgba(0, 0, 0, 0.06));
  padding: 3px;
  border-radius: 6px;
}

.tab-toggle button {
  background: transparent;
  border: none;
  padding: 0.375rem 0.75rem;
  font-size: 0.8125rem;
  font-weight: 500;
  border-radius: 4px;
  cursor: pointer;
  color: var(--color-text-muted, #555);
  transition: all 0.15s ease;
}

.tab-toggle button.active {
  background: var(--color-surface, #fff);
  color: var(--color-text, #111);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.restore-button {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  font-size: 0.8125rem;
  padding: 0.4375rem 0.875rem;
}

.viewport-body {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem 1.75rem;
}

.version-article {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.version-study-title {
  margin: 0 0 1rem;
  font-size: 1.375rem;
  font-weight: 600;
  border-bottom: 1px solid var(--color-border-subtle, rgba(0, 0, 0, 0.08));
  padding-bottom: 0.5rem;
}

.section-block {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.section-heading {
  margin: 0;
  font-size: 0.9375rem;
  font-weight: 600;
  color: var(--color-text-muted, #444);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.empty-field {
  margin: 0;
  font-size: 0.875rem;
  font-style: italic;
  color: var(--color-text-subtle, #888);
}

.notes-text {
  margin: 0;
  font-size: 0.9375rem;
  line-height: 1.6;
  white-space: pre-wrap;
}

.state-loading,
.empty-state {
  padding: 3rem;
  text-align: center;
  color: var(--color-text-muted, #666);
}

.confirm-overlay {
  position: absolute;
  inset: 0;
  background-color: rgba(0, 0, 0, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
  backdrop-filter: blur(2px);
}

.confirm-card {
  width: 90%;
  max-width: 440px;
  background: var(--color-surface, #fff);
  border-radius: 10px;
  padding: 1.5rem;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.25);
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.confirm-card h3 {
  margin: 0;
  font-size: 1.125rem;
}

.confirm-card p {
  margin: 0;
  font-size: 0.875rem;
  line-height: 1.5;
  color: var(--color-text-muted, #555);
}

.confirm-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 0.5rem;
}

.danger-confirm {
  background-color: #2563eb;
  color: #fff;
}

@media (max-width: 768px) {
  .history-layout {
    flex-direction: column;
  }
  .timeline-sidebar {
    width: 100%;
    max-height: 200px;
    border-right: none;
    border-bottom: 1px solid var(--color-border-subtle, rgba(0, 0, 0, 0.08));
  }
}
</style>
