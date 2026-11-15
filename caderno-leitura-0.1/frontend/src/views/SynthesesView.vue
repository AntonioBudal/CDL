<script setup lang="ts">
/** F0.11.11 (spec 113): lista dos cadernos de síntese e os excluídos (30 dias). */
import { onMounted, ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { api, errorMessage } from '../services/api'
import type { SynthesisSummary } from '../types'

const router = useRouter()
const items = ref<SynthesisSummary[]>([])
const trashed = ref<SynthesisSummary[]>([])
const loading = ref(true)
const busy = ref(false)
const error = ref('')
const message = ref('')
const newTitle = ref('')

function when(value: string): string {
  return new Date(value).toLocaleString('pt-BR', { dateStyle: 'short', timeStyle: 'short' })
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    const [active, removed] = await Promise.all([api.listSyntheses(), api.listTrashedSyntheses()])
    items.value = active
    trashed.value = removed
  } catch (e) {
    error.value = errorMessage(e)
  } finally {
    loading.value = false
  }
}

async function create() {
  const title = newTitle.value.trim() || 'Nova síntese'
  busy.value = true
  error.value = ''
  try {
    const created = await api.createSynthesis(title)
    await router.push({ name: 'synthesis', params: { id: created.id }, query: { editar: '1' } })
  } catch (e) {
    error.value = errorMessage(e)
  } finally {
    busy.value = false
  }
}

async function restore(item: SynthesisSummary) {
  busy.value = true
  try {
    await api.restoreSynthesis(item.id)
    message.value = `"${item.title}" restaurado.`
    await load()
  } catch (e) {
    error.value = errorMessage(e)
  } finally {
    busy.value = false
  }
}

async function removeForever(item: SynthesisSummary) {
  if (!window.confirm(`Excluir de vez "${item.title}"? O texto do caderno não poderá ser recuperado (os estudos transcluídos continuam intactos).`)) return
  busy.value = true
  try {
    await api.deleteSynthesisPermanently(item.id)
    message.value = `"${item.title}" excluído de vez.`
    await load()
  } catch (e) {
    error.value = errorMessage(e)
  } finally {
    busy.value = false
  }
}

onMounted(load)
</script>

<template>
  <section class="syntheses-view wrap" aria-labelledby="syntheses-heading">
    <header class="page-header">
      <p class="eyebrow">Seus textos</p>
      <h1 id="syntheses-heading">Sínteses</h1>
      <p class="syntheses-lead">
        Textos seus que atravessam livros e estudos. Trechos transcluídos mostram sempre o conteúdo atual do estudo,
        da seção ou do destaque de origem: nada é copiado.
      </p>
    </header>

    <form class="syntheses-new" @submit.prevent="create">
      <label class="syntheses-field">
        <span>Título do novo caderno</span>
        <input v-model="newTitle" type="text" maxlength="300" placeholder="Ex.: Tragédia e catarse" />
      </label>
      <button type="submit" class="primary syntheses-button" :disabled="busy">Novo caderno</button>
    </form>

    <p v-if="error" class="notice error" role="alert">{{ error }}</p>
    <p class="syntheses-muted" role="status" aria-live="polite">
      <template v-if="loading">Carregando…</template>
      <template v-else>{{ message || (items.length === 1 ? '1 caderno' : `${items.length} cadernos`) }}</template>
    </p>

    <p v-if="!loading && !items.length" class="syntheses-muted">
      Nenhum caderno ainda. Crie um e use "Inserir trecho" para trazer estudos, seções e destaques.
    </p>
    <ul v-else class="syntheses-list">
      <li v-for="item in items" :key="item.id" class="syntheses-item">
        <RouterLink :to="{ name: 'synthesis', params: { id: item.id } }" class="syntheses-title">{{ item.title }}</RouterLink>
        <span class="syntheses-muted">
          atualizado em {{ when(item.updated_at) }} ·
          {{ item.embeds === 1 ? '1 trecho' : `${item.embeds} trechos` }}
        </span>
      </li>
    </ul>

    <section v-if="trashed.length" class="syntheses-trash" aria-labelledby="syntheses-trash-heading">
      <h2 id="syntheses-trash-heading" class="syntheses-subtitle">Excluídos</h2>
      <p class="syntheses-muted">Ficam aqui por 30 dias e depois somem de vez.</p>
      <ul class="syntheses-list">
        <li v-for="item in trashed" :key="item.id" class="syntheses-item">
          <span class="syntheses-trashed-title">{{ item.title }}</span>
          <span class="syntheses-actions">
            <button type="button" class="quiet syntheses-button" :disabled="busy" @click="restore(item)">Restaurar</button>
            <button type="button" class="quiet syntheses-button" :disabled="busy" @click="removeForever(item)">Excluir de vez</button>
          </span>
        </li>
      </ul>
    </section>
  </section>
</template>

<style scoped>
.syntheses-view {
  max-width: 52rem;
  margin: 0 auto;
  padding-block: 1.5rem 3rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.syntheses-lead,
.syntheses-muted {
  color: var(--color-muted);
}
.syntheses-muted {
  font-size: 0.9rem;
  margin: 0;
}
.syntheses-new {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  gap: 8px;
}
.syntheses-field {
  display: grid;
  gap: 4px;
  flex: 1 1 16rem;
  min-width: 0;
}
.syntheses-field input {
  min-height: 44px;
}
.syntheses-button {
  min-height: 44px;
}
.syntheses-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: 4px;
}
.syntheses-item {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 4px 12px;
  padding: 6px 0;
  border-bottom: 1px solid var(--color-border);
  min-width: 0;
}
.syntheses-title {
  color: var(--color-link);
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  min-height: 44px;
  overflow-wrap: anywhere;
}
.syntheses-trashed-title {
  flex: 1 1 12rem;
  overflow-wrap: anywhere;
}
.syntheses-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.syntheses-subtitle {
  font-size: 1.1rem;
  margin: 0;
}
</style>
