<script setup lang="ts">
import { computed, onBeforeUnmount, watch } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { api } from '../services/api'
import { useStudyResource } from '../composables/useStudyResource'
import { useStudyEdit } from '../composables/useStudyEdit'
import { useUnsavedChanges } from '../composables/useUnsavedChanges'
import StudyEditorFields from '../components/StudyEditorFields.vue'
import ConflictResolutionModal from '../components/sync/ConflictResolutionModal.vue'

const route = useRoute()
const router = useRouter()
const resource = useStudyResource(api)
const { state: resourceState } = resource
const editor = useStudyEdit(api)
const { state, dirty, hasAnalysis, canSave } = editor
let disposed = false
useUnsavedChanges(() => dirty.value, () => state.saving)

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
  if (context) editor.load(context.study)
}

async function save() {
  const context = resourceState.context
  if (!context) return
  const saved = await editor.save()
  if (saved && !disposed) {
    await router.push({ name: 'study', params: { bookId: context.book.id, studyId: saved.id } })
  }
}

async function handleOverwrite() {
  const context = resourceState.context
  if (!context) return
  const saved = await editor.overwrite()
  if (saved && !disposed) {
    await router.push({ name: 'study', params: { bookId: context.book.id, studyId: saved.id } })
  }
}

async function handleReload() {
  await editor.reload()
}

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
        <RouterLink to="/" class="text-link">Voltar aos livros</RouterLink>
      </div>
    </div>
    <template v-else-if="resourceState.context">
      <nav class="breadcrumb" aria-label="Caminho">
        <RouterLink to="/">Meus livros</RouterLink><span aria-hidden="true">/</span>
        <RouterLink :to="{ name: 'book', params: { bookId: resourceState.context.book.id }, query: { chapter: resourceState.context.chapter.id } }">
          {{ resourceState.context.book.title }} · {{ resourceState.context.chapter.name }}
        </RouterLink>
      </nav>
      <header class="page-header">
        <p class="eyebrow">{{ resourceState.context.study.title }}</p>
        <h1>Editar estudo</h1>
        <p class="intro">Revise as seções e registre suas próprias interpretações.</p>
      </header>
      <form class="import-form panel import-step" @submit.prevent="save">
        <fieldset :disabled="state.saving">
          <StudyEditorFields
            id-prefix="edit"
            show-metadata
            v-model:title="state.title"
            v-model:location="state.location"
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
    </template>
  </div>
</template>
