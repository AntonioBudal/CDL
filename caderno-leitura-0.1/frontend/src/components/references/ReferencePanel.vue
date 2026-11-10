<script setup lang="ts">
/**
 * F0.11.05 (spec 107): referência da obra (e do trecho, na página do estudo) em ABNT, APA, BibTeX e CSL-JSON,
 * com copiar e baixar; as obras citadas do estudo saem como o leitor escreveu (só texto).
 */
import { computed, ref } from 'vue'
import Drawer from '../ui/Drawer.vue'
import { copyRich } from '../../utils/clipboard'
import { referenceLines } from '../../utils/referenceScopes'
import {
  REFERENCE_FORMATS,
  abntInTextCall,
  apaInTextCall,
  bibtexKey,
  formatReference,
  missingReferenceFields,
  type ReferenceBook,
  type ReferenceFormat,
  type ReferencePassage,
} from '../../utils/referenceFormats'

const props = defineProps<{
  open: boolean
  book: ReferenceBook
  /** Trecho (página do estudo): capítulo e localização. */
  passage?: ReferencePassage | null
  /** Seção Referências do estudo (obras citadas, como escritas). */
  citedText?: string | null
}>()

const emit = defineEmits<{ (e: 'close'): void; (e: 'edit-book'): void }>()

const format = ref<ReferenceFormat>('abnt')
const liveMessage = ref('')

const output = computed(() => formatReference(props.book, format.value, props.passage ?? undefined))
const missing = computed(() => missingReferenceFields(props.book))
const formatInfo = computed(() => REFERENCE_FORMATS.find((f) => f.value === format.value)!)
const inTextCall = computed(() => {
  if (!props.passage) return ''
  if (format.value === 'abnt') return abntInTextCall(props.book, props.passage)
  if (format.value === 'apa') return apaInTextCall(props.book, props.passage)
  return ''
})
const cited = computed(() => referenceLines(props.citedText))
const isStructured = computed(() => format.value === 'bibtex' || format.value === 'csl')

function announce(message: string) {
  liveMessage.value = ''
  setTimeout(() => {
    liveMessage.value = message
  }, 30)
}

async function copyReference() {
  const html = isStructured.value ? undefined : output.value.html
  const ok = await copyRich(output.value.text, html)
  announce(ok ? `Referência ${formatInfo.value.label} copiada.` : 'Não foi possível copiar automaticamente.')
}

async function copyCall() {
  const ok = await copyRich(inTextCall.value)
  announce(ok ? 'Chamada no texto copiada.' : 'Não foi possível copiar automaticamente.')
}

async function copyCited() {
  const ok = await copyRich(cited.value.join('\n'))
  announce(ok ? 'Lista de obras citadas copiada.' : 'Não foi possível copiar automaticamente.')
}

function download(content: string, filename: string, mime: string) {
  const blob = new Blob([content], { type: `${mime};charset=utf-8` })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  link.remove()
  setTimeout(() => URL.revokeObjectURL(url), 1000)
}

function downloadReference() {
  const info = formatInfo.value
  download(`${output.value.text}\n`, `${bibtexKey(props.book)}-${info.value}.${info.extension}`, info.mime)
  announce(`Arquivo ${info.label} baixado.`)
}

function downloadCited() {
  download(`${cited.value.join('\n')}\n`, `${bibtexKey(props.book)}-obras-citadas.txt`, 'text/plain')
  announce('Lista de obras citadas baixada.')
}

function onTabKeydown(event: KeyboardEvent, index: number) {
  if (event.key !== 'ArrowRight' && event.key !== 'ArrowLeft') return
  event.preventDefault()
  const step = event.key === 'ArrowRight' ? 1 : -1
  const next = REFERENCE_FORMATS[(index + step + REFERENCE_FORMATS.length) % REFERENCE_FORMATS.length]!
  format.value = next.value
  const tabs = (event.currentTarget as HTMLElement).parentElement?.querySelectorAll<HTMLButtonElement>('[role="tab"]')
  tabs?.[(index + step + REFERENCE_FORMATS.length) % REFERENCE_FORMATS.length]?.focus()
}
</script>

<template>
  <Drawer
    :open="open"
    title="Referência"
    :description="passage ? 'Da obra e deste trecho, em quatro formatos.' : 'Da obra, em quatro formatos.'"
    @close="emit('close')"
  >
    <div class="reference-panel">
      <div class="reference-tabs" role="tablist" aria-label="Formato da referência">
        <button
          v-for="(item, index) in REFERENCE_FORMATS"
          :key="item.value"
          type="button"
          role="tab"
          class="reference-tab"
          :class="{ 'is-active': item.value === format }"
          :aria-selected="item.value === format"
          :tabindex="item.value === format ? 0 : -1"
          @click="format = item.value"
          @keydown="onTabKeydown($event, index)"
        >
          {{ item.label }}
        </button>
      </div>

      <section class="reference-block" aria-label="Referência da obra">
        <h3 class="reference-heading">Obra</h3>
        <pre class="reference-text" tabindex="0">{{ output.text }}</pre>
        <div class="reference-actions">
          <button type="button" class="primary reference-action" @click="copyReference">Copiar</button>
          <button type="button" class="quiet reference-action" @click="downloadReference">
            Baixar .{{ formatInfo.extension }}
          </button>
        </div>
        <p v-if="missing.length" class="reference-missing">
          Sem {{ missing.join(', ') }}: a referência sai sem esses dados.
          <button type="button" class="quiet reference-link" @click="emit('edit-book')">Completar em Editar livro</button>
        </p>
      </section>

      <section v-if="passage && inTextCall" class="reference-block" aria-label="Chamada no texto">
        <h3 class="reference-heading">Chamada no texto (este trecho)</h3>
        <pre class="reference-text" tabindex="0">{{ inTextCall }}</pre>
        <div class="reference-actions">
          <button type="button" class="quiet reference-action" @click="copyCall">Copiar chamada</button>
        </div>
      </section>
      <p v-else-if="passage && isStructured" class="reference-muted">
        No {{ formatInfo.label }}, o capítulo e a localização do estudo já entram na própria referência.
      </p>

      <section v-if="citedText !== undefined" class="reference-block" aria-label="Obras citadas neste estudo">
        <h3 class="reference-heading">Obras citadas neste estudo</h3>
        <p v-if="cited.length === 0" class="reference-muted">A seção Referências deste estudo está vazia.</p>
        <template v-else>
          <p class="reference-muted">
            Como você escreveu, sem estruturar<template v-if="isStructured">; por isso não entram no {{ formatInfo.label }}</template>.
          </p>
          <ul class="reference-cited">
            <li v-for="(line, index) in cited" :key="index">{{ line }}</li>
          </ul>
          <div class="reference-actions">
            <button type="button" class="quiet reference-action" @click="copyCited">Copiar lista</button>
            <button type="button" class="quiet reference-action" @click="downloadCited">Baixar .txt</button>
          </div>
        </template>
      </section>

      <span class="visually-hidden" role="status" aria-live="polite">{{ liveMessage }}</span>
    </div>
  </Drawer>
</template>

<style scoped>
.reference-panel {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  min-width: 0;
}

.reference-tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
}

/* A regra global de botões exclui role="tab": as abas têm estilo próprio. */
.reference-tab {
  min-height: 44px;
  padding: 0 0.9rem;
  border-radius: 999px;
  border: 1px solid var(--color-border-strong, var(--color-border));
  background: transparent;
  color: var(--color-text);
  font: inherit;
  font-size: 0.9rem;
  cursor: pointer;
}

.reference-tab:hover {
  background: var(--color-surface-hover, var(--color-surface-soft));
}

.reference-tab.is-active {
  background: var(--color-selected-bg);
  color: var(--color-selected-text);
  border-color: var(--color-selected-bg);
  font-weight: 600;
}

.reference-tab:focus-visible {
  outline: 2px solid var(--ring-focus);
  outline-offset: 2px;
}

.reference-block {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  min-width: 0;
}

.reference-heading {
  margin: 0;
  font-size: 0.95rem;
  color: var(--color-text);
}

.reference-text {
  margin: 0;
  padding: 0.75rem;
  max-height: 18rem;
  overflow: auto;
  white-space: pre-wrap;
  overflow-wrap: anywhere;
  font-family: var(--font-mono, ui-monospace, monospace);
  font-size: 0.85rem;
  line-height: 1.5;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  background: var(--color-page);
  color: var(--color-text);
}

.reference-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.reference-action {
  min-height: 44px;
}

.reference-action.quiet {
  --quiet-border: var(--color-border-strong, var(--color-border));
}

.reference-missing,
.reference-muted {
  margin: 0;
  font-size: 0.875rem;
  color: var(--color-muted);
}

.reference-link {
  --quiet-fg: var(--color-link, var(--color-text));
  padding: 0 0.25rem;
  min-height: 44px;
  text-decoration: underline;
  text-underline-offset: 3px;
  cursor: pointer;
  font: inherit;
}

.reference-cited {
  margin: 0;
  padding-left: 1.2rem;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  color: var(--color-text);
  overflow-wrap: anywhere;
}

.visually-hidden {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}
</style>
