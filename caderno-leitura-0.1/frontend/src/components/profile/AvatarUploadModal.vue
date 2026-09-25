<script setup lang="ts">
import { nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import Icon from '../ui/Icon.vue'
import { useProfile } from '../../composables/useProfile.ts'

const props = withDefaults(
  defineProps<{
    open: boolean
    currentAvatarUrl?: string | null
    googleAvatarUrl?: string | null
    hasGoogleAvatar?: boolean
    initials?: string
  }>(),
  {
    currentAvatarUrl: null,
    googleAvatarUrl: null,
    hasGoogleAvatar: false,
    initials: 'CL',
  }
)

const emit = defineEmits<{
  close: []
  updated: []
}>()

const profileService = useProfile()
const fileInputRef = ref<HTMLInputElement | null>(null)
const dialogRef = ref<HTMLDivElement | null>(null)
const cancelButtonRef = ref<HTMLButtonElement | null>(null)

const selectedFile = ref<File | null>(null)
const previewUrl = ref<string | null>(null)
const errorMessage = ref<string | null>(null)
const isDragging = ref<boolean>(false)
const isProcessing = ref<boolean>(false)

const MAX_FILE_SIZE = 2 * 1024 * 1024 // 2MB
const ALLOWED_TYPES = ['image/png', 'image/jpeg', 'image/jpg', 'image/webp']

function resetState() {
  if (previewUrl.value && previewUrl.value.startsWith('blob:')) {
    URL.revokeObjectURL(previewUrl.value)
  }
  selectedFile.value = null
  previewUrl.value = null
  errorMessage.value = null
  isDragging.value = false
  isProcessing.value = false
  if (fileInputRef.value) {
    fileInputRef.value.value = ''
  }
}

function validateAndSetFile(file: File) {
  errorMessage.value = null
  if (!ALLOWED_TYPES.includes(file.type)) {
    errorMessage.value = 'Formato não suportado. Utilize arquivos PNG, JPEG ou WebP.'
    return
  }
  if (file.size > MAX_FILE_SIZE) {
    errorMessage.value = 'Tamanho excedido. A imagem deve ter no máximo 2MB.'
    return
  }

  if (previewUrl.value && previewUrl.value.startsWith('blob:')) {
    URL.revokeObjectURL(previewUrl.value)
  }
  selectedFile.value = file
  previewUrl.value = URL.createObjectURL(file)
}

function onFileInputChange(event: Event) {
  const target = event.target as HTMLInputElement
  const files = target.files
  if (files && files.length > 0) {
    validateAndSetFile(files[0])
  }
}

function triggerFileInput() {
  fileInputRef.value?.click()
}

function onDragOver(event: DragEvent) {
  event.preventDefault()
  isDragging.value = true
}

function onDragLeave(event: DragEvent) {
  event.preventDefault()
  isDragging.value = false
}

function onDrop(event: DragEvent) {
  event.preventDefault()
  isDragging.value = false
  const files = event.dataTransfer?.files
  if (files && files.length > 0) {
    validateAndSetFile(files[0])
  }
}

async function handleSaveAvatar() {
  if (!selectedFile.value) return
  isProcessing.value = true
  errorMessage.value = null
  try {
    await profileService.uploadAvatar(selectedFile.value)
    emit('updated')
    handleClose()
  } catch (err: unknown) {
    errorMessage.value = err instanceof Error ? err.message : 'Falha ao processar e salvar o avatar.'
  } finally {
    isProcessing.value = false
  }
}

async function handleUseGoogleAvatar() {
  isProcessing.value = true
  errorMessage.value = null
  try {
    await profileService.useGoogleAvatar()
    emit('updated')
    handleClose()
  } catch (err: unknown) {
    errorMessage.value = err instanceof Error ? err.message : 'Falha ao selecionar foto do Google.'
  } finally {
    isProcessing.value = false
  }
}

async function handleRemoveAvatar() {
  if (!confirm('Deseja realmente remover seu avatar personalizado?')) return
  isProcessing.value = true
  errorMessage.value = null
  try {
    await profileService.deleteAvatar()
    emit('updated')
    handleClose()
  } catch (err: unknown) {
    errorMessage.value = err instanceof Error ? err.message : 'Falha ao remover avatar.'
  } finally {
    isProcessing.value = false
  }
}

function handleClose() {
  resetState()
  emit('close')
}

function handleKeyDown(event: KeyboardEvent) {
  if (!props.open) return

  if (event.key === 'Escape') {
    event.preventDefault()
    handleClose()
    return
  }

  if (event.key === 'Tab' && dialogRef.value) {
    const focusable = dialogRef.value.querySelectorAll<HTMLElement>(
      'button:not([disabled]), [tabindex="0"], input:not([disabled])'
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
    } else {
      resetState()
    }
  }
)

onMounted(() => {
  window.addEventListener('keydown', handleKeyDown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyDown)
  if (previewUrl.value && previewUrl.value.startsWith('blob:')) {
    URL.revokeObjectURL(previewUrl.value)
  }
})
</script>

<template>
  <Teleport to="body">
    <div
      v-if="open"
      class="modal-backdrop"
      @click.self="handleClose"
    >
      <div
        ref="dialogRef"
        class="modal-dialog panel"
        role="dialog"
        aria-modal="true"
        aria-labelledby="avatar-modal-title"
        aria-describedby="avatar-modal-desc"
      >
        <header class="modal-header">
          <h2 id="avatar-modal-title" class="modal-title">
            Personalizar Avatar
          </h2>
          <button
            type="button"
            class="close-button"
            aria-label="Fechar janela"
            @click="handleClose"
          >
            <Icon name="x" :size="20" />
          </button>
        </header>

        <p id="avatar-modal-desc" class="modal-desc muted">
          Envie uma imagem do seu dispositivo (PNG, JPEG ou WebP de até 2MB) que será enquadrada em recorte quadrado de 256x256 pixels.
        </p>

        <!-- Área de Pré-visualização -->
        <div class="avatar-preview-section">
          <div class="avatar-preview-container">
            <img
              v-if="previewUrl"
              :src="previewUrl"
              alt="Pré-visualização do novo avatar"
              class="avatar-image-preview"
            />
            <img
              v-else-if="currentAvatarUrl"
              :src="currentAvatarUrl"
              alt="Avatar atual"
              class="avatar-image-preview"
            />
            <div v-else class="avatar-initials-preview" aria-hidden="true">
              {{ initials }}
            </div>
          </div>
          <span class="preview-caption muted">
            {{ previewUrl ? 'Pré-visualização do recorte' : (currentAvatarUrl ? 'Avatar em uso' : 'Iniciais padrão') }}
          </span>
        </div>

        <!-- Área de Drop e Seleção de Arquivo -->
        <div
          class="dropzone"
          :class="{ 'is-dragging': isDragging }"
          tabindex="0"
          role="button"
          aria-label="Selecionar imagem para o avatar. Clique ou arraste um arquivo até aqui."
          @click="triggerFileInput"
          @keydown.enter.prevent="triggerFileInput"
          @keydown.space.prevent="triggerFileInput"
          @dragover="onDragOver"
          @dragleave="onDragLeave"
          @drop="onDrop"
        >
          <input
            ref="fileInputRef"
            type="file"
            accept="image/png,image/jpeg,image/webp"
            class="sr-only"
            tabindex="-1"
            aria-hidden="true"
            @change="onFileInputChange"
          />
          <Icon name="upload" :size="28" class="dropzone-icon" />
          <p class="dropzone-text">
            <strong>Clique para escolher</strong> ou arraste o arquivo aqui
          </p>
          <span class="dropzone-hint muted">PNG, JPEG ou WebP (máx. 2MB)</span>
        </div>

        <!-- Mensagem de Erro -->
        <p
          v-if="errorMessage"
          class="error-notice"
          role="alert"
        >
          <Icon name="alert-triangle" :size="16" />
          <span>{{ errorMessage }}</span>
        </p>

        <!-- Opções Extras (Google / Remover) -->
        <div class="extra-options">
          <button
            v-if="hasGoogleAvatar && googleAvatarUrl"
            type="button"
            class="secondary google-avatar-btn"
            :disabled="isProcessing"
            @click="handleUseGoogleAvatar"
          >
            <img
              :src="googleAvatarUrl"
              alt=""
              class="google-thumb"
              aria-hidden="true"
            />
            <span>Usar foto da conta Google</span>
          </button>

          <button
            v-if="currentAvatarUrl"
            type="button"
            class="secondary danger-btn"
            :disabled="isProcessing"
            @click="handleRemoveAvatar"
          >
            <Icon name="trash" :size="16" />
            <span>Remover foto atual</span>
          </button>
        </div>

        <!-- Ações do Modal -->
        <div class="modal-actions actions wrap">
          <button
            ref="cancelButtonRef"
            type="button"
            class="secondary"
            :disabled="isProcessing"
            @click="handleClose"
          >
            Cancelar
          </button>

          <button
            type="button"
            class="primary"
            :disabled="!selectedFile || isProcessing"
            :aria-busy="isProcessing"
            @click="handleSaveAvatar"
          >
            {{ isProcessing ? 'Salvando…' : 'Salvar Avatar' }}
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
  max-width: 30rem;
  width: 100%;
  margin: 0;
  border: var(--border-width) solid var(--color-border);
  box-shadow: var(--shadow-surface, 0 12px 32px rgba(0, 0, 0, 0.3));
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.modal-title {
  margin: 0;
  font-size: var(--text-h2, 1.25rem);
}

.close-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 44px;
  min-height: 44px;
  padding: 0;
  border: none;
  background: transparent;
  color: var(--color-muted);
  cursor: pointer;
  border-radius: var(--radius-control, 6px);
  transition: color 0.15s ease, background-color 0.15s ease;
}

.close-button:hover {
  color: var(--color-text);
  background-color: var(--color-surface-hover);
}

.modal-desc {
  margin-top: 0;
  margin-bottom: 1.25rem;
  font-size: 0.875rem;
  line-height: 1.5;
}

.avatar-preview-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1.25rem;
}

.avatar-preview-container {
  width: 112px;
  height: 112px;
  border-radius: 50%;
  overflow: hidden;
  border: 2px solid var(--color-accent);
  background: var(--color-surface-soft, rgba(0, 0, 0, 0.04));
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.avatar-image-preview {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-initials-preview {
  font-size: 2.25rem;
  font-weight: 600;
  color: var(--color-accent);
  letter-spacing: 0.05em;
  user-select: none;
}

.preview-caption {
  font-size: 0.8125rem;
}

.dropzone {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.35rem;
  padding: 1.25rem 1rem;
  border: 2px dashed var(--color-border);
  border-radius: var(--radius-control, 8px);
  background: var(--color-surface-soft, rgba(0, 0, 0, 0.02));
  cursor: pointer;
  transition: border-color 0.15s ease, background-color 0.15s ease;
  min-height: 100px;
}

.dropzone:hover,
.dropzone:focus-visible,
.dropzone.is-dragging {
  border-color: var(--color-accent);
  background: var(--color-surface-hover);
  outline: none;
}

.dropzone-icon {
  color: var(--color-accent);
}

.dropzone-text {
  margin: 0;
  font-size: 0.875rem;
  color: var(--color-text);
  text-align: center;
}

.dropzone-hint {
  font-size: 0.75rem;
}

.sr-only {
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

.error-notice {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 0.875rem;
  margin-top: 0.75rem;
  margin-bottom: 0;
  border-radius: var(--radius-control, 6px);
  background-color: #fef2f2;
  border: 1px solid #fecaca;
  color: #b91c1c;
  font-size: 0.8125rem;
}

.extra-options {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-top: 1rem;
}

.google-avatar-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  min-height: 44px;
}

.google-thumb {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  object-fit: cover;
}

.danger-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  min-height: 44px;
  color: #b91c1c;
  border-color: #fecaca;
}

.danger-btn:hover:not(:disabled) {
  background-color: #fef2f2;
  border-color: #b91c1c;
}

.modal-actions {
  margin-top: 1.25rem;
  justify-content: flex-end;
  gap: 0.5rem;
}
</style>
