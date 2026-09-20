<script setup lang="ts">
import { nextTick, onMounted, onUnmounted, ref, watch } from 'vue'

const props = withDefaults(
  defineProps<{
    open: boolean
    busy?: boolean
  }>(),
  {
    busy: false,
  }
)

const emit = defineEmits<{
  confirm: []
  cancel: []
}>()

const cancelButtonRef = ref<HTMLButtonElement | null>(null)
const dialogRef = ref<HTMLDivElement | null>(null)

function handleKeyDown(event: KeyboardEvent) {
  if (!props.open) return

  if (event.key === 'Escape') {
    event.preventDefault()
    emit('cancel')
    return
  }

  // Trap de foco simples
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
      cancelButtonRef.value?.focus()
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
      @click.self="emit('cancel')"
    >
      <div
        ref="dialogRef"
        class="modal-dialog panel"
        role="dialog"
        aria-modal="true"
        aria-labelledby="confirm-reset-title"
        aria-describedby="confirm-reset-desc"
      >
        <h2 id="confirm-reset-title" class="modal-title">
          Restaurar Padrões de Aparência
        </h2>

        <p id="confirm-reset-desc">
          Esta ação redefine todas as suas escolhas visuais (tema, fontes, superclasses e layout) para os padrões originais de fábrica neste navegador.
        </p>

        <p class="muted">
          Seus livros, capítulos, estudos e anotações armazenados no banco de dados local <strong>não</strong> serão afetados.
        </p>

        <div class="modal-actions actions wrap">
          <button
            ref="cancelButtonRef"
            type="button"
            class="secondary"
            :disabled="busy"
            @click="emit('cancel')"
          >
            Cancelar
          </button>

          <button
            type="button"
            class="primary danger-action"
            :disabled="busy"
            :aria-busy="busy"
            @click="emit('confirm')"
          >
            {{ busy ? 'Restaurando…' : 'Sim, restaurar padrões' }}
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
  z-index: 1000;
  display: grid;
  place-items: center;
  padding: var(--space-unit);
  background-color: rgba(0, 0, 0, 0.55);
  backdrop-filter: blur(2px);
}

.modal-dialog {
  max-width: 32rem;
  width: 100%;
  margin: 0;
  border: var(--border-width) solid var(--color-border);
  box-shadow: var(--shadow-surface, 0 12px 32px rgba(0, 0, 0, 0.3));
}

.modal-title {
  margin-top: 0;
  font-size: var(--text-h2, 1.35rem);
}

.modal-actions {
  margin-top: calc(var(--space-unit) * 1.5);
  justify-content: flex-end;
}

.danger-action {
  background-color: #c53030;
  border-color: #9b2c2c;
  color: #fff;
}

.danger-action:hover:not(:disabled) {
  background-color: #9b2c2c;
}
</style>
