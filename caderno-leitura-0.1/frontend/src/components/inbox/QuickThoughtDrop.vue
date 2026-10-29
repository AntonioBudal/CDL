<script setup lang="ts">
import { computed, nextTick, ref } from 'vue'
import { api } from '../../services/api.ts'
import { useInboxCount } from '../../composables/useInboxCount.ts'
import Icon from '../ui/Icon.vue'
import type { InboxCapture } from '../../types.ts'

const props = withDefaults(
  defineProps<{
    placeholder?: string
    autoFocus?: boolean
  }>(),
  {
    placeholder: 'O que está passando pela sua mente? Despeje uma ideia, citação ou reflexão...',
    autoFocus: false,
  }
)

const emit = defineEmits<{
  (e: 'created', capture: InboxCapture): void
}>()

const { increment } = useInboxCount()

const textareaRef = ref<HTMLTextAreaElement | null>(null)
const content = ref('')
const sourceHint = ref('')
const isFocused = ref(false)
const isSubmitting = ref(false)
const submitError = ref<string | null>(null)

const isExpanded = computed(() => isFocused.value || content.value.trim().length > 0)
const canSubmit = computed(() => content.value.trim().length > 0 && !isSubmitting.value)

function onFocus() {
  isFocused.value = true
}

function onBlur(event: FocusEvent) {
  // Se o foco foi para outro elemento dentro do mesmo container, mantém expandido
  const currentTarget = event.currentTarget as HTMLElement | null
  const relatedTarget = event.relatedTarget as HTMLElement | null
  if (currentTarget && relatedTarget && currentTarget.contains(relatedTarget)) {
    return
  }
  if (!content.value.trim()) {
    isFocused.value = false
  }
}

function onKeydown(e: KeyboardEvent) {
  if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
    e.preventDefault()
    handleSubmit()
  }
}

async function handleSubmit() {
  const text = content.value.trim()
  if (!text || isSubmitting.value) return

  isSubmitting.value = true
  submitError.value = null

  try {
    const created = await api.createInboxCapture({
      content: text,
      source_hint: sourceHint.value.trim() || null,
    })
    increment()
    content.value = ''
    sourceHint.value = ''
    isFocused.value = false
    emit('created', created)
    await nextTick()
    if (textareaRef.value) {
      textareaRef.value.blur()
    }
  } catch (err: unknown) {
    submitError.value = err instanceof Error ? err.message : 'Falha ao salvar a captura no Inbox.'
  } finally {
    isSubmitting.value = false
  }
}

function focus() {
  if (textareaRef.value) {
    textareaRef.value.focus()
    isFocused.value = true
  }
}

defineExpose({
  focus,
})
</script>

<template>
  <div
    class="quick-thought-drop"
    :class="{ 'is-expanded': isExpanded }"
    role="region"
    aria-label="Campo de descarrego mental rápido para o Inbox"
    @focusin="onFocus"
    @focusout="onBlur"
  >
    <div class="input-container">
      <textarea
        ref="textareaRef"
        v-model="content"
        class="quick-drop-input"
        :rows="isExpanded ? 4 : 1"
        :placeholder="props.placeholder"
        :disabled="isSubmitting"
        aria-label="Conteúdo do pensamento ou citação"
        aria-keyshortcuts="Control+Enter"
        @keydown="onKeydown"
      ></textarea>
    </div>

    <!-- Barra de Ações e Fonte Opcional (visível quando expandido) -->
    <transition name="fade-slide">
      <div v-if="isExpanded" class="quick-drop-actions">
        <div class="source-field-wrapper">
          <input
            v-model="sourceHint"
            type="text"
            class="quick-drop-source"
            placeholder="Fonte, livro ou autor (opcional)"
            :disabled="isSubmitting"
            aria-label="Origem ou fonte do pensamento"
            @keydown="onKeydown"
          />
        </div>

        <div class="action-buttons-wrapper">
          <kbd class="shortcut-hint" title="Atalho de teclado">
            Ctrl+Enter para despejar
          </kbd>

          <button
            type="button"
            class="button primary quick-drop-submit"
            :disabled="!canSubmit"
            @click="handleSubmit"
          >
            <Icon name="plus" size="xs" />
            <span>{{ isSubmitting ? 'Salvando...' : 'Despejar Pensamento' }}</span>
          </button>
        </div>
      </div>
    </transition>

    <!-- Notificação Editorial de Erro -->
    <div v-if="submitError" class="quick-drop-error" role="alert">
      <span>{{ submitError }}</span>
      <button type="button" class="dismiss-error-btn" aria-label="Fechar erro" @click="submitError = null">
        <Icon name="x" size="xs" />
      </button>
    </div>
  </div>
</template>

<style scoped>
.quick-thought-drop {
  background-color: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg, 12px);
  padding: 12px 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  transition: border-color 180ms ease, box-shadow 180ms ease;
}

.quick-thought-drop:focus-within,
.quick-thought-drop.is-expanded {
  border-color: var(--color-accent);
  box-shadow: 0 4px 12px -2px rgba(0, 0, 0, 0.08);
}

.input-container {
  width: 100%;
}

.quick-drop-input {
  width: 100%;
  border: none;
  background: transparent;
  color: var(--color-text);
  font-family: inherit;
  font-size: 1rem;
  line-height: 1.5;
  resize: vertical;
  padding: 0;
  outline: none;
  transition: min-height 180ms cubic-bezier(0.2, 0, 0, 1);
  min-height: 28px;
}

.quick-thought-drop.is-expanded .quick-drop-input {
  min-height: 96px;
}

.quick-drop-input::placeholder {
  color: var(--color-text-muted);
}

.quick-drop-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid var(--color-border-subtle);
  flex-wrap: wrap;
}

.source-field-wrapper {
  flex: 1 1 240px;
}

.quick-drop-source {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-md, 6px);
  background-color: var(--color-bg);
  color: var(--color-text);
  font-size: 0.875rem;
  outline: none;
  transition: border-color 150ms ease;
}

.quick-drop-source:focus {
  border-color: var(--color-accent);
}

.action-buttons-wrapper {
  display: flex;
  align-items: center;
  gap: 12px;
}

.shortcut-hint {
  font-size: 0.75rem;
  color: var(--color-text-muted);
  background: var(--color-bg);
  border: 1px solid var(--color-border-subtle);
  border-radius: 4px;
  padding: 4px 8px;
  display: none;
}

@media (min-width: 640px) {
  .shortcut-hint {
    display: inline-block;
  }
}

.quick-drop-submit {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-weight: 600;
  min-height: 40px;
  padding: 8px 16px;
  border-radius: var(--radius-md, 6px);
  background-color: var(--color-primary);
  color: var(--color-on-accent);
  border: none;
  cursor: pointer;
  transition: opacity 150ms ease, background-color 150ms ease;
}

.quick-drop-submit:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.quick-drop-error {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 10px;
  padding: 8px 12px;
  background-color: var(--color-surface-hover);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md, 6px);
  color: var(--color-text);
  font-size: 0.85rem;
}

.dismiss-error-btn {
  background: transparent;
  border: none;
  color: var(--color-text-muted);
  cursor: pointer;
  padding: 4px;
}

/* Transições suaves */
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: opacity 180ms ease, transform 180ms ease;
}

.fade-slide-enter-from,
.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}
</style>
