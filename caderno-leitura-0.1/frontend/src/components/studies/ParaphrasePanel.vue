<script setup lang="ts">
/**
 * F0.11.07 (spec 109): validador de paráfrase. Compara Resumo, Explicação e Conceitos com o texto da fonte, no
 * navegador, e avisa as frases perto demais. Só avisa: nunca bloqueia o salvamento.
 */
import { computed, nextTick, onBeforeUnmount, ref, shallowRef, watch } from 'vue'
import { api } from '../../services/api'
import Icon from '../ui/Icon.vue'
import type { AnalysisSections, ParaphraseSource } from '../../types'
import {
  PARAPHRASE_SECTIONS,
  abntQuoteCall,
  buildSourceIndex,
  checkParaphrase,
  markAsQuote,
  type DeclaredQuote,
  type ParaphraseFlag,
  type ParaphraseResult,
  type ParaphraseSourceInput,
} from '../../utils/paraphraseCheck'

const props = defineProps<{
  idPrefix: string
  studyId?: number | null
  chapterId?: number | null
  author?: string | null
  year?: number | null
  bookTitle?: string | null
}>()
const sections = defineModel<AnalysisSections>('sections', { required: true })

const DEBOUNCE_MS = 400
const open = ref(false)
const loading = ref(false)
const error = ref('')
const notice = ref('')
const remote = ref<ParaphraseSource[]>([])
const declared = ref<DeclaredQuote[]>([])
const result = shallowRef<ParaphraseResult | null>(null)
let controller: AbortController | null = null
let timer: ReturnType<typeof setTimeout> | null = null

const sources = computed<ParaphraseSourceInput[]>(() => {
  return remote.value.map((s) => ({ label: s.label, text: s.text }))
})
const index = computed(() => buildSourceIndex(sources.value))
const hasSources = computed(() => sources.value.length > 0)

const sourceSummary = computed(() => {
  const parts: string[] = []
  const quotes = remote.value.filter((s) => s.kind === 'quote').length
  const captures = remote.value.filter((s) => s.kind === 'capture').length
  if (quotes) parts.push(`${quotes} ${quotes === 1 ? 'citação literal de outro estudo' : 'citações literais de outros estudos'}`)
  if (captures) parts.push(`${captures} ${captures === 1 ? 'captura do livro' : 'capturas do livro'}`)
  return parts.join(' · ')
})

const summaryText = computed(() => {
  const r = result.value
  if (!r) return ''
  if (r.flagged.length === 0) return 'Nenhuma frase muito próxima da fonte.'
  const n = r.flagged.length
  const base = `${n} ${n === 1 ? 'frase para revisar' : 'frases para revisar'} em ${r.total}`
  return r.copies ? `${base}; ${r.copies} ${r.copies === 1 ? 'cópia' : 'cópias'}.` : `${base}.`
})

const sectionLabel = (key: string) => PARAPHRASE_SECTIONS.find((s) => s.key === key)?.label ?? key
const percent = (score: number) => `${Math.round(score * 100)}%`

async function loadSources() {
  controller?.abort()
  const studyId = props.studyId ?? null
  const chapterId = props.chapterId ?? null
  if (!studyId && !chapterId) { remote.value = []; declared.value = []; return }
  const current = new AbortController()
  controller = current
  loading.value = true
  error.value = ''
  try {
    const data = studyId
      ? await api.getStudyParaphraseSources(studyId, current.signal)
      : await api.getChapterParaphraseSources(chapterId!, current.signal)
    if (!current.signal.aborted) {
      remote.value = data.sources
      declared.value = data.declared_quotes ?? []
    }
  } catch (e) {
    if (!current.signal.aborted) {
      remote.value = []
      declared.value = []
      error.value = e instanceof Error ? e.message : 'Não foi possível carregar o texto da fonte.'
    }
  } finally {
    if (!current.signal.aborted) loading.value = false
  }
}

function run() {
  result.value = hasSources.value ? checkParaphrase(sections.value, index.value, declared.value) : null
}

function schedule() {
  if (timer) clearTimeout(timer)
  timer = setTimeout(() => { timer = null; if (open.value) run() }, DEBOUNCE_MS)
}

async function toggle() {
  open.value = !open.value
  notice.value = ''
  if (open.value) {
    await loadSources()
    run()
  }
}

function markQuote(flag: ParaphraseFlag) {
  const call = abntQuoteCall(props.author, props.year, props.bookTitle)
  const current = sections.value[flag.section]
  const next = markAsQuote(current, flag.sentence, call)
  if (next === null) {
    notice.value = 'A frase mudou no editor; não encontrei o trecho para marcar.'
    return
  }
  sections.value = { ...sections.value, [flag.section]: next }
  notice.value = 'Frase marcada como citação. Complete o número da página na chamada.'
  void nextTick(run)
}

watch(() => [props.studyId, props.chapterId], () => { if (open.value) void loadSources().then(run) })
watch(sections, schedule, { deep: true })
onBeforeUnmount(() => { controller?.abort(); if (timer) clearTimeout(timer) })
</script>

<template>
  <section class="paraphrase-panel" :aria-labelledby="`${idPrefix}-paraphrase-title`">
    <div class="paraphrase-head">
      <h3 :id="`${idPrefix}-paraphrase-title`" class="paraphrase-title">Paráfrase</h3>
      <button
        type="button"
        class="quiet paraphrase-toggle"
        :aria-expanded="open"
        :aria-controls="`${idPrefix}-paraphrase-body`"
        @click="toggle"
      >
        {{ open ? 'Fechar verificação' : 'Verificar paráfrase' }}
      </button>
    </div>
    <div v-if="open" :id="`${idPrefix}-paraphrase-body`" class="paraphrase-body">
      <p class="paraphrase-note">
        Compara o Resumo, a Explicação e os Conceitos com o texto do livro que você guardou (capturas e citações
        literais de outros estudos), palavra por palavra: não reconhece sinônimos. Trechos entre aspas, em citação
        (<code>&gt;</code>) ou marcados como citação literal ficam de fora.
      </p>
      <p v-if="loading" class="paraphrase-muted" role="status">Carregando o texto da fonte…</p>
      <p v-else-if="error" class="paraphrase-error" role="alert">{{ error }}</p>
      <p v-else-if="!hasSources" class="paraphrase-muted">
        Ainda não há texto deste livro para comparar. Capture trechos na Mesa ou importe os destaques do Kindle ou
        do Kobo.
      </p>
      <template v-else>
        <p class="paraphrase-muted">Fontes: {{ sourceSummary }}</p>
        <p class="paraphrase-summary" aria-live="polite">{{ summaryText }}</p>
        <p v-if="notice" class="paraphrase-muted" role="status">{{ notice }}</p>
        <ol v-if="result && result.flagged.length" class="paraphrase-list">
          <li
            v-for="(flag, i) in result.flagged"
            :key="`${flag.section}-${i}-${flag.sentence}`"
            class="paraphrase-item"
            :class="`is-${flag.level}`"
          >
            <p class="paraphrase-level">
              <Icon :name="flag.level === 'copy' ? 'alert-triangle' : 'eye'" :size="16" aria-hidden="true" />
              <strong>{{ flag.level === 'copy' ? 'Cópia' : 'Muito próxima' }}</strong>
              <span class="paraphrase-muted">· {{ sectionLabel(flag.section) }} · {{ percent(flag.score) }} de semelhança<template v-if="flag.run >= 6"> · {{ flag.run }} palavras seguidas iguais</template></span>
            </p>
            <p class="paraphrase-advice">
              {{ flag.level === 'copy'
                ? 'Está igual ao texto do livro. Use aspas e cite a página, ou reescreva com suas palavras.'
                : 'Ainda segue a fonte de perto. Tente mudar a estrutura, não só trocar palavras.' }}
            </p>
            <p class="paraphrase-text">
              <span class="paraphrase-caption">Seu texto:</span>
              <template v-for="(part, j) in flag.sentenceParts" :key="j"><mark v-if="part.shared">{{ part.text }}</mark><template v-else>{{ part.text }}</template></template>
            </p>
            <p class="paraphrase-text">
              <span class="paraphrase-caption">{{ flag.sourceLabel }}:</span>
              <template v-for="(part, j) in flag.sourceParts" :key="j"><mark v-if="part.shared">{{ part.text }}</mark><template v-else>{{ part.text }}</template></template>
            </p>
            <button type="button" class="quiet paraphrase-action" @click="markQuote(flag)">Marcar como citação</button>
          </li>
        </ol>
      </template>
    </div>
  </section>
</template>

<style scoped>
.paraphrase-panel {
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: 12px 16px;
  margin-top: 16px;
  background: var(--color-surface);
  color: var(--color-text);
}
.paraphrase-head {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}
.paraphrase-title {
  margin: 0;
  font-size: 1rem;
}
.paraphrase-toggle,
.paraphrase-action {
  min-height: 44px;
}
.paraphrase-body {
  margin-top: 8px;
}
.paraphrase-note,
.paraphrase-muted {
  color: var(--color-muted);
  font-size: 0.9rem;
  margin: 6px 0;
}
.paraphrase-error {
  color: var(--color-danger-text);
}
.paraphrase-summary {
  font-weight: 600;
  margin: 8px 0;
}
.paraphrase-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  gap: 12px;
}
.paraphrase-item {
  border: 1px solid var(--color-border);
  border-left-width: 4px;
  border-radius: 6px;
  padding: 10px 12px;
  min-width: 0;
}
.paraphrase-item.is-copy {
  border-left-color: var(--color-danger-text);
}
.paraphrase-item.is-close {
  border-left-color: var(--color-warning-text);
}
.paraphrase-level {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px;
  margin: 0 0 4px;
}
.is-copy .paraphrase-level strong {
  color: var(--color-danger-text);
}
.is-close .paraphrase-level strong {
  color: var(--color-warning-text);
}
.paraphrase-advice {
  margin: 0 0 6px;
}
.paraphrase-text {
  margin: 6px 0;
  overflow-wrap: anywhere;
}
.paraphrase-caption {
  display: block;
  font-size: 0.85rem;
  color: var(--color-muted);
}
.paraphrase-text mark {
  background: var(--color-warning-bg);
  color: var(--color-warning-text);
  border-bottom: 1px solid var(--color-warning-border);
  padding: 0 1px;
}
</style>
