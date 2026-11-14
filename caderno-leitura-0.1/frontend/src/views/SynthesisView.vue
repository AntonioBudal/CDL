<script setup lang="ts">
/** F0.11.11 (spec 113): um caderno de síntese — ler (com trechos resolvidos) e editar (Markdown + "Inserir trecho"). */
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { ApiError, api, errorMessage } from '../services/api'
import MarkdownContent from '../components/MarkdownContent.vue'
import EmbedBlock from '../components/synthesis/EmbedBlock.vue'
import InsertEmbedDialog from '../components/synthesis/InsertEmbedDialog.vue'
import { useUnsavedChanges } from '../composables/useUnsavedChanges'
import type { EmbedResolved, SynthesisRead } from '../types'
import { insertOnOwnLine, splitBody } from '../utils/synthesisEmbeds'

const route = useRoute()
const router = useRouter()
const synthesis = ref<SynthesisRead | null>(null)
const embeds = ref<Record<string, EmbedResolved>>({})
const loading = ref(true)
const error = ref('')
const message = ref('')
const editing = ref(false)
const saving = ref(false)
const draftTitle = ref('')
const draftBody = ref('')
const dialogOpen = ref(false)
const textarea = ref<HTMLTextAreaElement | null>(null)

const id = computed(() => Number(route.params.id))
const dirty = computed(() => editing.value && !!synthesis.value
  && (draftTitle.value !== synthesis.value.title || draftBody.value !== synthesis.value.body))
const segments = computed(() => splitBody(synthesis.value?.body ?? ''))
const hasInvalid = computed(() => splitBody(draftBody.value).some((s) => s.type === 'invalid'))

useUnsavedChanges(() => dirty.value, () => saving.value)

async function load() {
  loading.value = true
  error.value = ''
  try {
    const data = await api.getResolvedSynthesis(id.value)
    synthesis.value = data.synthesis
    embeds.value = data.embeds
    if (route.query.editar === '1' && !editing.value) startEdit()
  } catch (e) {
    error.value = errorMessage(e)
  } finally {
    loading.value = false
  }
}

function startEdit() {
  if (!synthesis.value) return
  draftTitle.value = synthesis.value.title
  draftBody.value = synthesis.value.body
  editing.value = true
  message.value = ''
}

function cancelEdit() {
  if (dirty.value && !window.confirm('Descartar as alterações deste caderno?')) return
  editing.value = false
  if (route.query.editar) void router.replace({ query: {} })
}

async function save() {
  if (!synthesis.value) return
  saving.value = true
  error.value = ''
  try {
    await api.updateSynthesis(synthesis.value.id, {
      title: draftTitle.value.trim() || synthesis.value.title,
      body: draftBody.value,
      version: synthesis.value.version,
    })
    editing.value = false
    if (route.query.editar) void router.replace({ query: {} })
    await load()
    message.value = 'Caderno salvo.'
  } catch (e) {
    error.value = e instanceof ApiError && e.status === 409
      ? 'Este caderno foi alterado em outro aparelho. Copie o seu texto, recarregue a página e junte as mudanças.'
      : errorMessage(e)
  } finally {
    saving.value = false
  }
}

function insert(token: string) {
  const area = textarea.value
  const position = area ? area.selectionStart : draftBody.value.length
  const result = insertOnOwnLine(draftBody.value, position, token)
  draftBody.value = result.body
  void nextTick(() => {
    area?.focus()
    area?.setSelectionRange(result.cursor, result.cursor)
  })
}

async function remove() {
  if (!synthesis.value) return
  if (!window.confirm(`Mandar "${synthesis.value.title}" para Excluídos? Dá para restaurar por 30 dias.`)) return
  try {
    await api.trashSynthesis(synthesis.value.id)
    await router.push({ name: 'syntheses' })
  } catch (e) {
    error.value = errorMessage(e)
  }
}

async function exportMarkdown() {
  if (!synthesis.value) return
  try {
    await api.exportSynthesis(synthesis.value.id)
    message.value = 'Arquivo Markdown gerado.'
  } catch (e) {
    error.value = errorMessage(e)
  }
}

watch(id, () => { editing.value = false; void load() })
onMounted(load)
</script>

<template>
  <section class="synthesis-view wrap" aria-labelledby="synthesis-heading">
    <RouterLink :to="{ name: 'syntheses' }" class="synthesis-back">← Sínteses</RouterLink>
    <p v-if="error" class="notice error" role="alert">{{ error }}</p>
    <p v-if="loading" class="synthesis-muted" role="status">Carregando o caderno…</p>

    <template v-else-if="synthesis">
      <header class="page-header">
        <p class="eyebrow">Caderno de síntese</p>
        <h1 id="synthesis-heading">{{ editing ? 'Editar caderno' : synthesis.title }}</h1>
      </header>
      <p class="synthesis-muted" role="status" aria-live="polite">{{ message }}</p>

      <!-- Ler -->
      <template v-if="!editing">
        <div class="synthesis-actions">
          <button type="button" class="primary synthesis-button" @click="startEdit">Editar</button>
          <button type="button" class="quiet synthesis-button" @click="exportMarkdown">Exportar Markdown</button>
          <button type="button" class="quiet synthesis-button" @click="remove">Excluir</button>
        </div>
        <article class="synthesis-body">
          <p v-if="!synthesis.body.trim()" class="synthesis-muted">Caderno vazio. Use "Editar" para escrever e inserir trechos.</p>
          <template v-for="(segment, index) in segments" :key="index">
            <MarkdownContent v-if="segment.type === 'text' && segment.text.trim()" :content="segment.text" />
            <EmbedBlock v-else-if="segment.type === 'embed'" :item="embeds[segment.embed.key] ?? null" />
            <p v-else-if="segment.type === 'invalid'" class="synthesis-invalid">
              <code>{{ segment.text.trim() }}</code>
              <span>Marca de trecho não reconhecida (ela precisa ficar sozinha na linha).</span>
            </p>
          </template>
        </article>
      </template>

      <!-- Editar -->
      <form v-else class="synthesis-form" @submit.prevent="save">
        <label class="synthesis-field">
          <span>Título</span>
          <input v-model="draftTitle" type="text" maxlength="300" required />
        </label>
        <div class="synthesis-actions">
          <button type="button" class="quiet synthesis-button" @click="dialogOpen = true">Inserir trecho</button>
        </div>
        <label class="synthesis-field">
          <span>Texto (Markdown)</span>
          <textarea ref="textarea" v-model="draftBody" rows="18" class="synthesis-textarea" />
        </label>
        <p class="synthesis-muted">
          Marcas de trecho, cada uma sozinha na linha: <code>![[Título|id]]</code> (estudo),
          <code>![[Título|id#resumo]]</code> (seção) e <code>![[destaque:id]]</code> (destaque).
        </p>
        <p v-if="hasInvalid" class="synthesis-invalid" role="status">
          Há marcas que não serão reconhecidas: confira se cada uma está sozinha na linha.
        </p>
        <div class="synthesis-actions">
          <button type="submit" class="primary synthesis-button" :disabled="saving">{{ saving ? 'Salvando…' : 'Salvar' }}</button>
          <button type="button" class="quiet synthesis-button" :disabled="saving" @click="cancelEdit">Cancelar</button>
        </div>
      </form>
      <InsertEmbedDialog :open="dialogOpen" @insert="insert" @close="dialogOpen = false" />
    </template>
  </section>
</template>

<style scoped>
.synthesis-view {
  max-width: 52rem;
  margin: 0 auto;
  padding-block: 1.5rem 3rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  min-width: 0;
}
.synthesis-back {
  color: var(--color-link);
  display: inline-flex;
  align-items: center;
  min-height: 44px;
  align-self: flex-start;
}
.synthesis-muted {
  color: var(--color-muted);
  font-size: 0.9rem;
  margin: 0;
}
.synthesis-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.synthesis-button {
  min-height: 44px;
}
.synthesis-body {
  min-width: 0;
  overflow-wrap: anywhere;
}
.synthesis-form {
  display: grid;
  gap: 10px;
}
.synthesis-field {
  display: grid;
  gap: 4px;
  min-width: 0;
}
.synthesis-field input {
  min-height: 44px;
}
.synthesis-textarea {
  width: 100%;
  min-height: 20rem;
  font-family: var(--font-mono, ui-monospace, monospace);
  resize: vertical;
}
.synthesis-invalid {
  display: flex;
  flex-wrap: wrap;
  gap: 4px 8px;
  color: var(--color-warning-text);
  background: var(--color-warning-bg);
  border: 1px solid var(--color-warning-border);
  border-radius: 6px;
  padding: 6px 10px;
  margin: 8px 0;
  overflow-wrap: anywhere;
}
</style>
