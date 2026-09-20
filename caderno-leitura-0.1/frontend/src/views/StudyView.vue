<script setup lang="ts">
import { onBeforeUnmount, ref, watch } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { api, errorMessage } from '../services/api'
import { useStudyResource } from '../composables/useStudyResource'
import StudyTabs from '../components/StudyTabs.vue'
import ReaderTools from '../components/ReaderTools.vue'
import ExportModal from '../components/ExportModal.vue'
import TrashConfirmModal from '../components/TrashConfirmModal.vue'
import StudyRelationsList from '../components/relations/StudyRelationsList.vue'
import CreateRelationModal from '../components/relations/CreateRelationModal.vue'
import StudyStatusBadge from '../components/StudyStatusBadge.vue'

const route = useRoute()
const router = useRouter()
const resource = useStudyResource(api)
const { state } = resource

const exportModalOpen = ref(false)
const confirmTrashOpen = ref(false)
const createRelationModalOpen = ref(false)
const relationsListRef = ref<InstanceType<typeof StudyRelationsList> | null>(null)
const trashing = ref(false)
const trashError = ref('')

function handleRelationCreated() {
  createRelationModalOpen.value = false
  relationsListRef.value?.loadRelations()
}

async function handleTrash() {
  if (!state.context || trashing.value) return
  trashing.value = true
  trashError.value = ''
  try {
    await api.trashStudy(state.context.study.id)
    confirmTrashOpen.value = false
    await router.push({
      name: 'book',
      params: { bookId: state.context.book.id },
      query: { chapter: state.context.chapter.id }
    })
  } catch (error) {
    trashError.value = errorMessage(error)
  } finally {
    trashing.value = false
  }
}

async function load() { await resource.load(route.params.bookId, route.params.studyId) }
watch([() => route.params.bookId, () => route.params.studyId], load, { immediate: true })
onBeforeUnmount(resource.cancel)
</script>

<template>
  <div class="study-view">
    <p v-if="state.loading" class="state-panel" role="status">Carregando estudo…</p>
  <div v-else-if="state.error" class="notice error" role="alert">
    <h1>Não foi possível abrir o estudo.</h1><p>{{ state.error }}</p>
    <div class="actions wrap"><button type="button" class="secondary" @click="load">Tentar novamente</button><RouterLink to="/" class="text-link">Voltar aos livros</RouterLink></div>
  </div>
  <template v-else-if="state.context">
    <nav class="breadcrumb" aria-label="Caminho">
      <RouterLink to="/">Meus livros</RouterLink><span aria-hidden="true">/</span>
      <RouterLink :to="{ name: 'book', params: { bookId: state.context.book.id } }">{{ state.context.book.title }}</RouterLink><span aria-hidden="true">/</span>
      <RouterLink :to="{ name: 'book', params: { bookId: state.context.book.id }, query: { chapter: state.context.chapter.id } }">{{ state.context.chapter.name }}</RouterLink>
    </nav>
    <header class="page-header reader-heading">
      <div>
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 6px;">
          <p class="eyebrow" style="margin: 0;">Estudo</p>
          <StudyStatusBadge
            :status="state.context.study.reading_status || 'rascunho'"
            :study-id="state.context.study.id"
            :interactive="true"
            @change="(newSt) => { if (state.context) state.context.study.reading_status = newSt }"
          />
        </div>
        <h1>{{ state.context.study.title }}</h1>
        <p class="intro">{{ state.context.study.location || 'Localização não informada' }}</p>
      </div>
      <div class="header-actions">
        <button type="button" class="secondary" @click="exportModalOpen = true">Exportar estudo</button>
        <RouterLink class="button secondary" :to="{ name: 'study-edit', params: { bookId: state.context.book.id, studyId: state.context.study.id } }">Editar estudo</RouterLink>
        <button type="button" class="secondary danger-action" @click="confirmTrashOpen = true">Mover para a lixeira</button>
      </div>
    </header>
    <ReaderTools :key="state.context.study.id" />

    <div class="reader-layout reader-static-surface">
      <StudyTabs :key="state.context.study.id" :id-prefix="`study-${state.context.study.id}`" :sections="state.context.study" />
      <aside class="panel reader-notes" aria-labelledby="notes-heading">
        <h2 id="notes-heading">Minhas anotações</h2>
        <p v-if="state.context.study.notes.trim()" class="notes-content">{{ state.context.study.notes }}</p>
        <p v-else class="muted">Nenhuma anotação ainda. Registre suas interpretações em “Editar estudo”.</p>
      </aside>
    </div>
    <details class="original-response"><summary>Consultar Fichamento da Fonte</summary><pre>{{ state.context.study.source_response }}</pre></details>

    <StudyRelationsList
      ref="relationsListRef"
      :study-id="state.context.study.id"
      :book-id="state.context.book.id"
      @open-create-modal="createRelationModalOpen = true"
    />

    <CreateRelationModal
      :open="createRelationModalOpen"
      :source-study-id="state.context.study.id"
      :source-study-title="state.context.study.title"
      @close="createRelationModalOpen = false"
      @relation-created="handleRelationCreated"
    />

    <TrashConfirmModal
      :open="confirmTrashOpen"
      title="Mover estudo para a lixeira?"
      :message="`Deseja enviar o estudo “${state.context.study.title}” para a lixeira? Ele poderá ser restaurado nos próximos 30 dias.`"
      confirm-label="Mover para a lixeira"
      :loading="trashing"
      @close="confirmTrashOpen = false"
      @confirm="handleTrash"
    />

    <ExportModal
      :open="exportModalOpen"
      :title="state.context.study.title"
      scope="study"
      :book-id="state.context.book.id"
      :study-id="state.context.study.id"
      @close="exportModalOpen = false"
    />
  </template>
  </div>
</template>

<style scoped>
.header-actions {
  display: flex;
  align-items: center;
  gap: calc(var(--space-unit) * 0.75);
}

.danger-action {
  color: var(--color-danger, #b91c1c);
}

.danger-action:hover {
  background: var(--color-surface-hover);
  border-color: var(--color-danger, #b91c1c);
}
</style>
