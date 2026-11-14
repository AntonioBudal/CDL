<script setup lang="ts">
/**
 * F0.11.11 (spec 113): "Inserir trecho" — busca um estudo e oferece o estudo inteiro, as seções preenchidas e os
 * destaques dele. Emite a marca pronta (`![[…]]`).
 */
import { computed, nextTick, onBeforeUnmount, ref, watch } from 'vue'
import { api, errorMessage } from '../../services/api'
import type { Study, StudyCandidateOption, StudyHighlight } from '../../types'
import { SECTION_SLUGS, embedToken, type SectionSlug } from '../../utils/synthesisEmbeds'

const props = defineProps<{ open: boolean }>()
const emit = defineEmits<{ (e: 'insert', token: string): void; (e: 'close'): void }>()

const dialog = ref<HTMLDialogElement | null>(null)
const searchInput = ref<HTMLInputElement | null>(null)
const query = ref('')
const candidates = ref<StudyCandidateOption[]>([])
const chosen = ref<StudyCandidateOption | null>(null)
const study = ref<Study | null>(null)
const highlights = ref<StudyHighlight[]>([])
const loading = ref(false)
const error = ref('')
let timer: ReturnType<typeof setTimeout> | null = null
let controller: AbortController | null = null

const filledSections = computed(() =>
  (Object.keys(SECTION_SLUGS) as SectionSlug[]).filter((slug) => {
    const key = SECTION_SLUGS[slug].key
    return Boolean(study.value && String(study.value[key] ?? '').trim())
  }),
)
const visibleHighlights = computed(() => highlights.value.filter((h) => h.kind !== 'hidden'))

async function search() {
  controller?.abort()
  const current = new AbortController()
  controller = current
  loading.value = true
  error.value = ''
  try {
    const found = await api.searchStudyCandidates(query.value, 12, current.signal)
    if (!current.signal.aborted) candidates.value = found
  } catch (e) {
    if (!current.signal.aborted) error.value = errorMessage(e)
  } finally {
    if (!current.signal.aborted) loading.value = false
  }
}

async function choose(item: StudyCandidateOption) {
  chosen.value = item
  loading.value = true
  error.value = ''
  try {
    const [full, marks] = await Promise.all([api.getStudy(item.id), api.listStudyHighlights(item.id)])
    study.value = full
    highlights.value = marks
  } catch (e) {
    error.value = errorMessage(e)
  } finally {
    loading.value = false
  }
}

function pick(token: string) {
  emit('insert', token)
  close()
}

function back() {
  chosen.value = null
  study.value = null
  highlights.value = []
  void nextTick(() => searchInput.value?.focus())
}

function close() {
  if (dialog.value?.open) dialog.value.close()
  // Avisa o pai na hora (não depende do evento nativo "close", que alguns navegadores atrasam).
  emit('close')
}

function reset() {
  query.value = ''
  back()
}

watch(() => props.open, (open) => {
  if (open) {
    reset()
    dialog.value?.showModal()
    void search()
    void nextTick(() => searchInput.value?.focus())
  } else if (dialog.value?.open) {
    dialog.value.close()
  }
})

watch(query, () => {
  if (timer) clearTimeout(timer)
  timer = setTimeout(search, 250)
})

onBeforeUnmount(() => {
  controller?.abort()
  if (timer) clearTimeout(timer)
})
</script>

<template>
  <dialog ref="dialog" class="embed-dialog" aria-labelledby="embed-dialog-title" @close="emit('close')" @cancel.prevent="close">
    <h2 id="embed-dialog-title" class="embed-dialog-title">Inserir trecho</h2>
    <p v-if="error" class="embed-dialog-error" role="alert">{{ error }}</p>

    <template v-if="!chosen">
      <label class="embed-dialog-field">
        <span>Buscar estudo</span>
        <input ref="searchInput" v-model="query" type="search" autocomplete="off" placeholder="Título do estudo" />
      </label>
      <p class="embed-dialog-muted" role="status">{{ loading ? 'Buscando…' : `${candidates.length} estudos` }}</p>
      <ul class="embed-dialog-list">
        <li v-for="item in candidates" :key="item.id">
          <button type="button" class="quiet embed-dialog-option" @click="choose(item)">
            <strong>{{ item.title }}</strong>
            <span class="embed-dialog-muted">{{ item.book_title }} · {{ item.chapter_name }}</span>
          </button>
        </li>
      </ul>
    </template>

    <template v-else>
      <p class="embed-dialog-muted">{{ chosen.book_title }} · {{ chosen.chapter_name }}</p>
      <h3 class="embed-dialog-study">{{ chosen.title }}</h3>
      <p v-if="loading" class="embed-dialog-muted" role="status">Carregando…</p>
      <ul v-else class="embed-dialog-list">
        <li>
          <button type="button" class="quiet embed-dialog-option" @click="pick(embedToken('study', chosen.id, chosen.title))">
            <strong>Estudo inteiro</strong>
          </button>
        </li>
        <li v-for="slug in filledSections" :key="slug">
          <button
            type="button"
            class="quiet embed-dialog-option"
            @click="pick(embedToken('section', chosen.id, chosen.title, slug))"
          >
            <strong>Seção {{ SECTION_SLUGS[slug].label }}</strong>
          </button>
        </li>
        <li v-for="mark in visibleHighlights" :key="mark.id">
          <button type="button" class="quiet embed-dialog-option" @click="pick(embedToken('highlight', mark.id))">
            <strong>Destaque</strong>
            <span class="embed-dialog-excerpt">{{ mark.selected_text }}</span>
          </button>
        </li>
      </ul>
      <button type="button" class="quiet embed-dialog-action" @click="back">Escolher outro estudo</button>
    </template>

    <div class="embed-dialog-footer">
      <button type="button" class="quiet embed-dialog-action" @click="close">Cancelar</button>
    </div>
  </dialog>
</template>

<style scoped>
.embed-dialog {
  width: min(36rem, calc(100vw - 32px));
  max-height: min(80vh, 44rem);
  border: 1px solid var(--color-border);
  border-radius: 10px;
  padding: 16px;
  background: var(--color-surface);
  color: var(--color-text);
}
.embed-dialog::backdrop {
  background: rgb(0 0 0 / 0.5);
}
.embed-dialog-title {
  margin: 0 0 8px;
  font-size: 1.15rem;
}
.embed-dialog-study {
  margin: 0 0 8px;
  font-size: 1rem;
}
.embed-dialog-field {
  display: grid;
  gap: 4px;
}
.embed-dialog-field input {
  min-height: 44px;
}
.embed-dialog-muted {
  color: var(--color-muted);
  font-size: 0.88rem;
  margin: 4px 0;
}
.embed-dialog-error {
  color: var(--color-danger-text);
}
.embed-dialog-list {
  list-style: none;
  margin: 8px 0;
  padding: 0;
  display: grid;
  gap: 6px;
}
.embed-dialog-option {
  width: 100%;
  min-height: 44px;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 2px;
  text-align: left;
  white-space: normal;
}
.embed-dialog-excerpt {
  font-size: 0.88rem;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}
.embed-dialog-action {
  min-height: 44px;
}
.embed-dialog-footer {
  display: flex;
  justify-content: flex-end;
  margin-top: 8px;
}
</style>
