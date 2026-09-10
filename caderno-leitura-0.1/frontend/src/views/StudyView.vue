<script setup lang="ts">
import { onBeforeUnmount, watch } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { api } from '../services/api'
import { useStudyResource } from '../composables/useStudyResource'
import StudyTabs from '../components/StudyTabs.vue'

const route = useRoute()
const resource = useStudyResource(api)
const { state } = resource
async function load() { await resource.load(route.params.bookId, route.params.studyId) }
watch([() => route.params.bookId, () => route.params.studyId], load, { immediate: true })
onBeforeUnmount(resource.cancel)
</script>

<template>
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
      <div><p class="eyebrow">Estudo</p><h1>{{ state.context.study.title }}</h1><p class="intro">{{ state.context.study.location || 'Localização não informada' }}</p></div>
      <RouterLink class="button secondary" :to="{ name: 'study-edit', params: { bookId: state.context.book.id, studyId: state.context.study.id } }">Editar estudo</RouterLink>
    </header>
    <div class="reader-layout">
      <StudyTabs :key="state.context.study.id" :id-prefix="`study-${state.context.study.id}`" :sections="state.context.study" />
      <aside class="panel reader-notes" aria-labelledby="notes-heading">
        <h2 id="notes-heading">Minhas anotações</h2>
        <p v-if="state.context.study.notes.trim()" class="notes-content">{{ state.context.study.notes }}</p>
        <p v-else class="muted">Nenhuma anotação ainda. Registre suas interpretações em “Editar estudo”.</p>
      </aside>
    </div>
    <details class="original-response"><summary>Consultar resposta original</summary><pre>{{ state.context.study.source_response }}</pre></details>
  </template>
</template>
