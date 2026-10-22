<script setup lang="ts">
import { computed, onBeforeUnmount, ref, watch } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { api } from '../services/api'
import { useStudyResource } from '../composables/useStudyResource'
import { useStudyEdit } from '../composables/useStudyEdit'
import { useUnsavedChanges } from '../composables/useUnsavedChanges'
import { useStudyDraft } from '../composables/useStudyDraft'
import StudyEditorFields from '../components/StudyEditorFields.vue'
import ConflictResolutionModal from '../components/sync/ConflictResolutionModal.vue'
import StudyHistoryModal from '../components/StudyHistoryModal.vue'
import AppBreadcrumb from '../components/ui/AppBreadcrumb.vue'
import Icon from '../components/ui/Icon.vue'
import type { BreadcrumbItem, IconName, Study, StudyEditorDraftPayload } from '../types.ts'

const route = useRoute()
const router = useRouter()
const resource = useStudyResource(api)
const { state: resourceState } = resource
const editor = useStudyEdit(api)
const { state, dirty, hasAnalysis, canSave } = editor
const historyModalOpen = ref(false)
let disposed = false
useUnsavedChanges(() => dirty.value, () => state.saving)

const breadcrumbItems = computed<BreadcrumbItem[]>(() => {
  if (!resourceState.context) return []
  return [
    { label: 'Livros', to: '/livros' },
    {
      label: `${resourceState.context.book.title} · ${resourceState.context.chapter.name}`,
      to: {
        name: 'book',
        params: { bookId: resourceState.context.book.id },
        query: { chapter: resourceState.context.chapter.id },
      },
    },
    { label: 'Editar estudo', current: true },
  ]
})

const draft = useStudyDraft({
  studyId: () => resourceState.context?.study?.id,
  getCurrentData: () => ({
    title: state.title,
    location: state.location,
    sections: state.sections,
    notes: state.notes,
    template_id: state.template_id,
  }),
  onRestore: (savedDraft: StudyEditorDraftPayload) => {
    state.title = savedDraft.title
    state.location = savedDraft.location
    state.sections = { ...savedDraft.sections }
    state.notes = savedDraft.notes
    if (savedDraft.template_id) {
      state.template_id = savedDraft.template_id
    }
  },
})
const { isDraftRestored, saveDraft, restoreDraft, discardDraft, clearDraft } = draft

const draftStatusLabel = computed(() => {
  if (state.saving) {
    return 'Salvando…'
  }
  if (dirty.value || isDraftRestored.value) {
    return 'Rascunho salvo neste navegador'
  }
  return 'Alterações salvas'
})

const draftStatusClass = computed(() => {
  if (state.saving) {
    return 'saving'
  }
  if (dirty.value || isDraftRestored.value) {
    return 'draft-local'
  }
  return 'saved'
})

const draftStatusIcon = computed<IconName>(() => {
  if (state.saving) {
    return 'refresh-cw'
  }
  if (dirty.value || isDraftRestored.value) {
    return 'clock'
  }
  return 'check'
})

function handleStudyRestored(updatedStudy: Study) {
  editor.load(updatedStudy)
}

function handleDiscardDraft() {
  discardDraft()
  if (resourceState.context?.study) {
    editor.load(resourceState.context.study)
  }
}

const localFormData = computed(() => ({
  title: state.title,
  location: state.location,
  summary: state.sections.summary,
  explanation: state.sections.explanation,
  concepts: state.sections.concepts,
  references: state.sections.references,
  notes: state.notes,
}))

async function load() {
  editor.clear()
  const context = await resource.load(route.params.bookId, route.params.studyId)
  if (context) {
    editor.load(context.study)
    restoreDraft()
  }
}

async function save() {
  const context = resourceState.context
  if (!context) return
  const saved = await editor.save()
  if (saved && !disposed) {
    clearDraft()
    await router.push({ name: 'study', params: { bookId: context.book.id, studyId: saved.id } })
  }
}

async function handleOverwrite() {
  const context = resourceState.context
  if (!context) return
  const saved = await editor.overwrite()
  if (saved && !disposed) {
    clearDraft()
    await router.push({ name: 'study', params: { bookId: context.book.id, studyId: saved.id } })
  }
}

async function handleReload() {
  await editor.reload()
}

watch(
  [
    () => state.title,
    () => state.location,
    () => state.template_id,
    () => state.sections.summary,
    () => state.sections.explanation,
    () => state.sections.concepts,
    () => state.sections.references,
    () => state.notes,
  ],
  () => {
    if (dirty.value && resourceState.context?.study?.id) {
      saveDraft()
    }
  }
)

watch([() => route.params.bookId, () => route.params.studyId], load, { immediate: true })
onBeforeUnmount(() => { disposed = true; resource.cancel() })
</script>

<template>
  <div class="study-edit-view">
    <p v-if="resourceState.loading" class="state-panel" role="status">Carregando estudo…</p>
    <div v-else-if="resourceState.error" class="notice error" role="alert">
      <h1>Não foi possível editar o estudo.</h1>
      <p>{{ resourceState.error }}</p>
      <div class="actions wrap">
        <button type="button" class="secondary" @click="load">Tentar novamente</button>
        <RouterLink to="/livros" class="text-link">Voltar aos livros</RouterLink>
      </div>
    </div>
    <template v-else-if="resourceState.context">
      <AppBreadcrumb :items="breadcrumbItems" />
      <header class="page-header" style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 1rem;">
        <div>
          <p class="eyebrow">{{ resourceState.context.study.title }}</p>
          <div class="edit-title-row">
            <h1>Editar estudo</h1>
            <span
              class="draft-status-pill"
              :class="draftStatusClass"
              role="status"
              aria-live="polite"
            >
              <Icon :name="draftStatusIcon" :size="13" class="status-pill-icon" />
              <span>{{ draftStatusLabel }}</span>
            </span>
          </div>
          <p class="intro">Revise as seções e registre suas próprias interpretações.</p>
        </div>
        <button
          type="button"
          class="secondary"
          style="display: flex; align-items: center; gap: 0.375rem; margin-top: 0.5rem;"
          aria-label="Abrir histórico de versões do estudo"
          @click="historyModalOpen = true"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true" style="width: 16px; height: 16px;">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          Histórico de versões
        </button>
      </header>

      <!-- Banner de rascunho recuperado automaticamente da sessão -->
      <div v-if="isDraftRestored" class="draft-recovery-banner notice info" role="status" aria-live="polite">
        <div class="banner-content">
          <span>Rascunho recuperado automaticamente da sua sessão anterior.</span>
          <button type="button" class="text-link discard-btn" @click="handleDiscardDraft">
            Descartar rascunho
          </button>
        </div>
      </div>

      <form class="import-form panel import-step" @submit.prevent="save">
        <fieldset :disabled="state.saving">
          <StudyEditorFields
            id-prefix="edit"
            show-metadata
            v-model:title="state.title"
            v-model:location="state.location"
            v-model:template-id="state.template_id"
            v-model:sections="state.sections"
            v-model:notes="state.notes"
          />
          <p v-if="!hasAnalysis" class="notice warning">Preencha ao menos uma das quatro seções para salvar.</p>
          <div v-if="state.error" class="notice error" role="alert" aria-live="assertive">
            <p>{{ state.error }}</p>
          </div>
          <div class="save-bar">
            <p class="muted" role="status">
              {{ state.saving ? 'Salvando alterações…' : dirty ? 'Você tem alterações não salvas.' : 'Nenhuma alteração pendente.' }}
            </p>
            <div class="actions wrap">
              <RouterLink class="text-link" :to="{ name: 'study', params: { bookId: resourceState.context.book.id, studyId: resourceState.context.study.id } }">
                Cancelar
              </RouterLink>
              <button class="primary" :disabled="!canSave">
                {{ state.saving ? 'Salvando…' : 'Salvar alterações' }}
              </button>
            </div>
          </div>
        </fieldset>
      </form>

      <!-- Modal de Resolução de Conflitos OCC (F04) -->
      <ConflictResolutionModal
        :open="state.isConflict"
        :conflict-data="state.conflictData"
        :local-data="localFormData"
        :busy="state.saving"
        @overwrite="handleOverwrite"
        @keep-server="handleReload"
        @close="editor.dismissConflict"
      />

      <StudyHistoryModal
        :open="historyModalOpen"
        :study-id="resourceState.context.study.id"
        :can-edit="true"
        @close="historyModalOpen = false"
        @restored="handleStudyRestored"
      />
    </template>
  </div>
</template>

<style scoped>
.draft-recovery-banner {
  margin-bottom: 1rem;
}

.banner-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
}

.discard-btn {
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 0;
  text-decoration: underline;
  font-size: 0.875rem;
}

.edit-title-row {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.draft-status-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.25rem 0.625rem;
  border-radius: var(--radius-full, 9999px);
  font-size: 0.75rem;
  font-weight: 500;
  line-height: 1;
  transition: all 0.2s ease;
}

.draft-status-pill.saved {
  background-color: var(--color-surface-hover, rgba(0, 0, 0, 0.04));
  color: var(--color-muted);
  border: var(--border-width) solid var(--color-border);
}

.draft-status-pill.draft-local {
  background-color: var(--color-surface-hover, rgba(0, 0, 0, 0.05));
  color: var(--color-text);
  border: var(--border-width) solid var(--color-border);
}

.draft-status-pill.saving {
  background-color: var(--color-surface-hover, rgba(0, 0, 0, 0.05));
  color: var(--color-accent);
  border: var(--border-width) solid var(--color-accent);
}

.draft-status-pill.saving .status-pill-icon {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

@media (prefers-reduced-motion: reduce) {
  .draft-status-pill.saving .status-pill-icon {
    animation: none;
  }
}
</style>
