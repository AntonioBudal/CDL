<script setup lang="ts">
import { nextTick, onMounted, onUnmounted, ref, watch } from 'vue'

const props = withDefaults(
  defineProps<{
    open: boolean
    message?: string
    busy?: boolean
  }>(),
  {
    message: 'Este estudo foi modificado em outro dispositivo enquanto você editava.',
    busy: false,
  }
)

const emit = defineEmits<{
  (e: 'overwrite'): void
  (e: 'reload'): void
  (e: 'close'): void
}>()

const dialogRef = ref<HTMLDivElement | null>(null)
const defaultButtonRef = ref<HTMLButtonElement | null>(null)

function handleKeyDown(event: KeyboardEvent) {
  if (!props.open || props.busy) return

  if (event.key === 'Escape') {
    event.preventDefault()
    emit('close')
    return
  }

  if (event.key === 'Tab' && dialogRef.value) {
    const focusable = dialogRef.value.querySelectorAll<HTMLElement>(
      'button:not([disabled]), [tabindex="0"]'
    )
    if (focusable.length > 0) {
      const first = focusable[0]
      const last = focusable[focusable.length - 1]

      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault()
        last.focus()
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault()
        first.focus()
      }
    }
  }
}

watch(
  () => props.open,
  async (isOpen) => {
    if (isOpen) {
      await nextTick()
      defaultButtonRef.value?.focus()
    }
  }
)

onMounted(() => {
  window.addEventListener('keydown', handleKeyDown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyDown)
})
</script>

<template>
  <Teleport to="body">
    <div
      v-if="open"
      class="modal-backdrop"
      role="presentation"
      @click="!busy && emit('close')"
    >
      <div
        ref="dialogRef"
        class="modal-dialog"
        role="dialog"
        aria-modal="true"
        aria-labelledby="concurrency-title"
        aria-describedby="concurrency-description"
        @click.stop
      >
        <h2 id="concurrency-title">Conflito de Concorrência Detectado</h2>

        <div class="warning-box" role="alert">
          <p id="concurrency-description">
            {{ message }}
          </p>
          <p class="muted" style="margin-top: 0.5rem;">
            <strong>Seus dados não foram perdidos:</strong> todo o texto digitado permanece preservado no formulário.
          </p>
        </div>

        <p class="explanation">
          Escolha como deseja prosseguir:
        </p>

        <div class="conflict-options">
          <button
            ref="defaultButtonRef"
            type="button"
            class="primary overwrite-btn"
            :disabled="busy"
            @click="emit('overwrite')"
          >
            Sobrescrever com minhas alterações
            <span class="btn-subtext">Grava o conteúdo atual do formulário na base</span>
          </button>

          <button
            type="button"
            class="secondary reload-btn"
            :disabled="busy"
            @click="emit('reload')"
          >
            Recarregar versão externa
            <span class="btn-subtext">Descarta as edições locais e busca os dados mais recentes</span>
          </button>
        </div>

        <div class="modal-footer">
          <button
            type="button"
            class="text-link"
            :disabled="busy"
            @click="emit('close')"
          >
            Permanecer no formulário e revisar
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.modal-backdrop {
  position: fixed;
  inset: 0;
  background-color: rgba(0, 0, 0, 0.65);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.modal-dialog {
  background-color: var(--color-bg, #ffffff);
  color: var(--color-text, #111827);
  border: var(--border-width, 1px) solid var(--color-border, #e5e7eb);
  border-radius: var(--border-radius, 8px);
  padding: 1.5rem;
  max-width: 32rem;
  width: 100%;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.25);
}

.warning-box {
  background-color: var(--color-bg-warning, #fffbeb);
  border: 1px solid var(--color-border-warning, #fef3c7);
  padding: 0.85rem 1rem;
  border-radius: 6px;
  margin-top: 0.75rem;
  font-size: 0.95rem;
  line-height: 1.5;
}

.explanation {
  margin-top: 1rem;
  margin-bottom: 0.5rem;
  font-weight: 600;
  font-size: 0.9rem;
}

.conflict-options {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-top: 0.5rem;
}

.conflict-options button {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  text-align: left;
  padding: 0.75rem 1rem;
  min-height: 3.5rem;
  border-radius: 6px;
}

.btn-subtext {
  font-size: 0.8rem;
  font-weight: 400;
  opacity: 0.85;
  margin-top: 0.2rem;
}

.modal-footer {
  display: flex;
  justify-content: center;
  margin-top: 1.25rem;
}
</style>
