<script setup lang="ts">
import { nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import { restoreBackupPackage } from '../services/api.ts'
import Icon from './ui/Icon.vue'
import type { RestoreResult } from '../types.ts'

const props = defineProps<{
  open: boolean
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'restored', result: RestoreResult): void
}>()

const fileInputRef = ref<HTMLInputElement | null>(null)
const cancelButtonRef = ref<HTMLButtonElement | null>(null)
const dialogRef = ref<HTMLDivElement | null>(null)

const selectedFile = ref<File | null>(null)
const busy = ref(false)
const statusMessage = ref('')
const errorMessage = ref('')
const successResult = ref<RestoreResult | null>(null)

function resetState() {
  selectedFile.value = null
  busy.value = false
  statusMessage.value = ''
  errorMessage.value = ''
  successResult.value = null
  if (fileInputRef.value) {
    fileInputRef.value.value = ''
  }
}

function handleFileChange(event: Event) {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (file) {
    selectedFile.value = file
    errorMessage.value = ''
  }
}

async function handleRestore() {
  if (!selectedFile.value || busy.value) return

  busy.value = true
  errorMessage.value = ''
  statusMessage.value = 'Enviando e validando integridade do pacote na sandbox…'

  try {
    const result = await restoreBackupPackage(selectedFile.value)
    successResult.value = result
    statusMessage.value = ''
    emit('restored', result)
  } catch (err) {
    errorMessage.value = err instanceof Error ? err.message : 'Falha ao restaurar acervo.'
    statusMessage.value = ''
  } finally {
    busy.value = false
  }
}

function handleClose() {
  if (busy.value) return
  emit('close')
}

function reloadPage() {
  window.location.reload()
}

function handleKeyDown(event: KeyboardEvent) {
  if (!props.open) return

  if (event.key === 'Escape' && !busy.value) {
    event.preventDefault()
    handleClose()
    return
  }

  if (event.key === 'Tab' && dialogRef.value) {
    const focusable = dialogRef.value.querySelectorAll<HTMLElement>(
      'button:not([disabled]), input:not([disabled]), [tabindex="0"]'
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
      resetState()
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
      role="presentation"
      @click="handleClose"
    >
      <div
        ref="dialogRef"
        class="modal-dialog"
        role="dialog"
        aria-modal="true"
        aria-labelledby="restore-modal-title"
        aria-describedby="restore-modal-description"
        @click.stop
      >
        <h2 id="restore-modal-title">Restaurar Acervo de Backup</h2>

        <template v-if="!successResult">
          <p id="restore-modal-description" class="modal-intro">
            Selecione um arquivo de backup completo (<code>.zip</code> com capas e manifesto) ou banco avulso (<code>.db</code>).
          </p>

          <div class="warning-box" role="alert">
            <p><strong>Atenção:</strong> Os livros, estudos e capas atuais serão substituídos pelo conteúdo do backup.</p>
            <p class="muted">Um snapshot de salvaguarda do acervo ativo será criado automaticamente antes de qualquer troca.</p>
          </div>

          <div class="field" style="margin-top: 1rem;">
            <label for="restore-file-input" class="label">Arquivo de Backup:</label>
            <input
              id="restore-file-input"
              ref="fileInputRef"
              type="file"
              accept=".zip,.db,application/zip,application/x-sqlite3"
              :disabled="busy"
              @change="handleFileChange"
            />
          </div>

          <p v-if="statusMessage" class="status-msg muted" role="status" aria-live="polite">
            ◌ {{ statusMessage }}
          </p>

          <p v-if="errorMessage" class="notice error" role="alert">
            {{ errorMessage }}
          </p>

          <div class="modal-actions">
            <button
              ref="cancelButtonRef"
              type="button"
              class="secondary"
              :disabled="busy"
              @click="handleClose"
            >
              Cancelar
            </button>

            <button
              type="button"
              class="primary"
              :disabled="!selectedFile || busy"
              :aria-busy="busy"
              @click="handleRestore"
            >
              {{ busy ? 'Restaurando…' : 'Confirmar e Restaurar' }}
            </button>
          </div>
        </template>

        <template v-else>
          <div class="success-box" role="status">
            <h3><Icon name="check-circle" :size="20" class="inline-icon" /> Acervo Restaurado com Êxito</h3>
            <p>{{ successResult.message }}</p>
            <ul class="stats-list">
              <li><strong>Livros restaurados:</strong> {{ successResult.counts['books'] ?? 0 }}</li>
              <li><strong>Capítulos restaurados:</strong> {{ successResult.counts['chapters'] ?? 0 }}</li>
              <li><strong>Estudos restaurados:</strong> {{ successResult.counts['studies'] ?? 0 }}</li>
              <li><strong>Capas restauradas:</strong> {{ successResult.covers_restored }}</li>
              <li class="muted"><strong>Snapshot de salvaguarda:</strong> {{ successResult.pre_restore_snapshot }}</li>
            </ul>
          </div>

          <div class="modal-actions">
            <button
              type="button"
              class="primary"
              @click="reloadPage"
            >
              Recarregar Aplicação
            </button>
          </div>
        </template>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.modal-backdrop {
  position: fixed;
  inset: 0;
  background-color: rgba(0, 0, 0, 0.6);
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
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
}

.modal-intro {
  margin-top: 0.5rem;
  margin-bottom: 1rem;
  line-height: 1.5;
}

.warning-box {
  background-color: var(--color-bg-warning, #fffbeb);
  border: 1px solid var(--color-border-warning, #fef3c7);
  padding: 0.75rem 1rem;
  border-radius: 6px;
  font-size: 0.9rem;
}

.warning-box p {
  margin: 0;
}

.warning-box p + p {
  margin-top: 0.25rem;
}

.success-box {
  background-color: var(--color-bg-success, #ecfdf5);
  border: 1px solid var(--color-border-success, #d1fae5);
  padding: 1rem;
  border-radius: 6px;
  margin-top: 1rem;
}

.stats-list {
  margin-top: 0.5rem;
  padding-left: 1.25rem;
  font-size: 0.9rem;
  line-height: 1.6;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.label {
  font-weight: 600;
  font-size: 0.9rem;
}

.status-msg {
  margin-top: 0.75rem;
  font-size: 0.9rem;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 1.5rem;
}
</style>
