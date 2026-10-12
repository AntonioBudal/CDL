<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { sharingApi } from '../../api/sharing.ts'
import type {
  ResourcePermissionsRead,
  ResourcePermissionItem,
  ResourceVisibility,
} from '../../types.ts'
import Icon from '../ui/Icon.vue'

interface Props {
  modelValue: boolean
  studyId: number
  bookId?: number | null
  initialVisibility?: ResourceVisibility
}

const props = withDefaults(defineProps<Props>(), {
  bookId: null,
  initialVisibility: 'inherit',
})

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void
  (e: 'visibility-changed', payload: { visibility: ResourceVisibility; effectiveVisibility: ResourceVisibility }): void
}>()

const loading = ref(false)
const saving = ref(false)
const granting = ref(false)
const revokingUserId = ref<string | null>(null)
const error = ref<string | null>(null)
const successMsg = ref<string | null>(null)
const copyFeedback = ref(false)

const currentVisibility = ref<ResourceVisibility>(props.initialVisibility)
const effectiveVisibility = ref<ResourceVisibility>('private')
const permissions = ref<ResourcePermissionItem[]>([])
const newReaderUsername = ref('')

const studyLink = computed(() => {
  if (typeof window === 'undefined') return ''
  return `${window.location.origin}/estudo/${props.studyId}`
})

const visibilityOptions: { value: ResourceVisibility; label: string; desc: string }[] = [
  {
    value: 'inherit',
    label: 'Herança do Livro',
    desc: 'Adota a visibilidade do livro associado ao capítulo',
  },
  {
    value: 'private',
    label: 'Privado',
    desc: 'Apenas você pode visualizar este estudo',
  },
  {
    value: 'friends',
    label: 'Amigos',
    desc: 'Visível para suas amizades confirmadas no Leitorum',
  },
  {
    value: 'custom',
    label: 'Personalizado',
    desc: 'Apenas leitores convidados nominalmente na lista abaixo',
  },
  {
    value: 'public',
    label: 'Público',
    desc: 'Acessível para qualquer leitor autenticado que tenha o link',
  },
]

async function loadPermissions() {
  if (!props.studyId) return
  loading.value = true
  error.value = null
  try {
    const data: ResourcePermissionsRead = await sharingApi.getStudyPermissions(props.studyId)
    currentVisibility.value = data.visibility
    effectiveVisibility.value = data.effective_visibility
    permissions.value = data.permissions || []
  } catch (err: unknown) {
    error.value = err instanceof Error ? err.message : 'Falha ao carregar permissões.'
  } finally {
    loading.value = false
  }
}

async function onVisibilityChange(newVal: ResourceVisibility) {
  if (newVal === currentVisibility.value) return
  saving.value = true
  error.value = null
  successMsg.value = null
  try {
    const data = await sharingApi.updateStudyVisibility(props.studyId, newVal)
    currentVisibility.value = data.visibility
    effectiveVisibility.value = data.effective_visibility
    emit('visibility-changed', {
      visibility: data.visibility,
      effectiveVisibility: data.effective_visibility,
    })
    successMsg.value = 'Visibilidade atualizada.'
    setTimeout(() => {
      if (successMsg.value === 'Visibilidade atualizada.') successMsg.value = null
    }, 3000)
  } catch (err: unknown) {
    error.value = err instanceof Error ? err.message : 'Falha ao alterar visibilidade.'
  } finally {
    saving.value = false
  }
}

async function handleGrantPermission() {
  const username = newReaderUsername.value.trim().replace(/^@/, '')
  if (!username) return
  granting.value = true
  error.value = null
  successMsg.value = null
  try {
    const newItem = await sharingApi.grantStudyPermission(props.studyId, username)
    permissions.value = [newItem, ...permissions.value.filter((p) => p.user_id !== newItem.user_id)]
    newReaderUsername.value = ''
    successMsg.value = `Permissão concedida para @${newItem.username}.`
    setTimeout(() => {
      if (successMsg.value?.includes(newItem.username)) successMsg.value = null
    }, 4000)
  } catch (err: unknown) {
    error.value = err instanceof Error ? err.message : 'Erro ao conceder permissão.'
  } finally {
    granting.value = false
  }
}

async function handleRevokePermission(userId: string, username: string) {
  revokingUserId.value = userId
  error.value = null
  try {
    await sharingApi.revokeStudyPermission(props.studyId, userId)
    permissions.value = permissions.value.filter((p) => p.user_id !== userId)
    successMsg.value = `Permissão de @${username} revogada.`
    setTimeout(() => {
      if (successMsg.value?.includes(username)) successMsg.value = null
    }, 3000)
  } catch (err: unknown) {
    error.value = err instanceof Error ? err.message : 'Erro ao revogar permissão.'
  } finally {
    revokingUserId.value = null
  }
}

async function copyLink() {
  try {
    await navigator.clipboard.writeText(studyLink.value)
    copyFeedback.value = true
    setTimeout(() => {
      copyFeedback.value = false
    }, 2500)
  } catch {
    // Fallback se clipboard falhar
    const input = document.createElement('input')
    input.value = studyLink.value
    document.body.appendChild(input)
    input.select()
    document.execCommand('copy')
    document.body.removeChild(input)
    copyFeedback.value = true
    setTimeout(() => {
      copyFeedback.value = false
    }, 2500)
  }
}

function close() {
  emit('update:modelValue', false)
}

function handleKeydown(e: KeyboardEvent) {
  if (e.key === 'Escape' && props.modelValue) {
    close()
  }
}

watch(
  () => props.modelValue,
  (val) => {
    if (val) {
      loadPermissions()
    }
  },
)

onMounted(() => {
  window.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
})
</script>

<template>
  <div
    v-if="modelValue"
    class="share-modal-backdrop"
    role="dialog"
    aria-modal="true"
    aria-labelledby="share-modal-title"
    @click.self="close"
  >
    <div class="share-modal-card">
      <!-- Modal Header -->
      <header class="share-modal-header">
        <div class="share-modal-title-group">
          <Icon name="network" :size="20" class="share-modal-icon" />
          <h2 id="share-modal-title" class="share-modal-title">
            Compartilhar Estudo
          </h2>
        </div>
        <button
          type="button"
          class="share-modal-close-btn"
          aria-label="Fechar janela de compartilhamento"
          @click="close"
        >
          <Icon name="x" :size="20" />
        </button>
      </header>

      <!-- Modal Body (Scrollable) -->
      <div class="share-modal-body">
        <!-- Notificações de feedback -->
        <div
          v-if="error"
          class="share-feedback-alert error"
          role="alert"
        >
          <Icon name="alert-triangle" :size="16" class="feedback-icon" />
          <span>{{ error }}</span>
        </div>

        <div
          v-if="successMsg"
          class="share-feedback-alert success"
          role="status"
        >
          <Icon name="check" :size="16" class="feedback-icon" />
          <span>{{ successMsg }}</span>
        </div>

        <!-- Copiar Link do Estudo -->
        <div class="share-field-group">
          <label class="share-field-label">
            Link direto para o estudo
          </label>
          <div class="share-input-row">
            <input
              type="text"
              readonly
              :value="studyLink"
              class="share-link-input"
              aria-label="Link do estudo"
            />
            <button
              type="button"
              class="share-copy-btn"
              :class="{ copied: copyFeedback }"
              aria-label="Copiar link do estudo"
              @click="copyLink"
            >
              <Icon :name="copyFeedback ? 'check' : 'copy'" :size="16" />
              <span>{{ copyFeedback ? 'Copiado!' : 'Copiar' }}</span>
            </button>
          </div>
        </div>

        <!-- Seção de Visibilidade -->
        <div class="share-field-group">
          <div class="share-visibility-header">
            <label class="share-field-label">
              Nível de Visibilidade
            </label>
            <span
              v-if="effectiveVisibility"
              class="share-effective-tag"
            >
              Efetivo: {{ effectiveVisibility }}
            </span>
          </div>

          <div class="share-visibility-options" role="radiogroup" aria-label="Nível de visibilidade do estudo">
            <label
              v-for="opt in visibilityOptions"
              :key="opt.value"
              class="share-visibility-option"
              :class="{
                selected: currentVisibility === opt.value,
                disabled: saving,
              }"
            >
              <input
                type="radio"
                name="study-visibility"
                :value="opt.value"
                :checked="currentVisibility === opt.value"
                class="share-radio-input"
                @change="onVisibilityChange(opt.value)"
              />
              <div class="share-option-text">
                <span class="share-option-label">{{ opt.label }}</span>
                <p class="share-option-desc">{{ opt.desc }}</p>
              </div>
            </label>
          </div>
        </div>

        <!-- Seção ACL Granular (Apenas no modo 'custom') -->
        <div v-if="currentVisibility === 'custom'" class="share-acl-section">
          <label class="share-field-label">
            Conceder Acesso Nominal
          </label>

          <!-- Input para adicionar amigo por username -->
          <form class="share-input-row" @submit.prevent="handleGrantPermission">
            <div class="share-username-wrap">
              <span class="share-at-prefix">@</span>
              <input
                v-model="newReaderUsername"
                type="text"
                placeholder="nome_do_leitor"
                maxlength="50"
                class="share-username-input"
                aria-label="Handle do leitor para conceder acesso"
              />
            </div>
            <button
              type="submit"
              :disabled="!newReaderUsername.trim() || granting"
              class="share-grant-btn"
            >
              <span>{{ granting ? 'Concedendo...' : 'Conceder' }}</span>
            </button>
          </form>

          <!-- Lista de Leitores Autorizados -->
          <div class="share-readers-group">
            <h4 class="share-readers-title">
              Leitores autorizados ({{ permissions.length }})
            </h4>

            <div v-if="permissions.length === 0" class="share-empty-readers">
              Nenhum leitor convidado ainda. Digite o @username acima para autorizar.
            </div>

            <ul v-else class="share-readers-list">
              <li
                v-for="user in permissions"
                :key="user.user_id"
                class="share-reader-item"
              >
                <div class="share-reader-info">
                  <div class="share-reader-avatar">
                    <img
                      v-if="user.avatar_url"
                      :src="user.avatar_url"
                      :alt="user.display_name"
                      class="share-avatar-img"
                    />
                    <span v-else class="share-avatar-initial">{{ user.display_name.charAt(0).toUpperCase() }}</span>
                  </div>
                  <div class="share-reader-details">
                    <p class="share-reader-name">{{ user.display_name }}</p>
                    <p class="share-reader-handle">@{{ user.username }}</p>
                  </div>
                </div>

                <button
                  type="button"
                  class="share-revoke-btn"
                  :aria-label="`Revogar acesso de @${user.username}`"
                  :disabled="revokingUserId === user.user_id"
                  @click="handleRevokePermission(user.user_id, user.username)"
                >
                  <Icon name="trash" :size="16" />
                </button>
              </li>
            </ul>
          </div>
        </div>
      </div>

      <!-- Modal Footer -->
      <footer class="share-modal-footer">
        <button
          type="button"
          class="share-done-btn"
          @click="close"
        >
          Concluir
        </button>
      </footer>
    </div>
  </div>
</template>

<style scoped>
.share-modal-backdrop {
  position: fixed;
  inset: 0;
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  background-color: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(2px);
}

.share-modal-card {
  width: 100%;
  max-width: 32rem;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background-color: var(--color-surface);
  border: var(--border-width, 1px) solid var(--color-border);
  border-radius: var(--radius-card, 1rem);
  box-shadow: var(--shadow-modal, 0 20px 25px -5px rgba(0, 0, 0, 0.3));
}

.share-modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.5rem;
  border-bottom: var(--border-width, 1px) solid var(--color-border);
}

.share-modal-title-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.share-modal-icon {
  color: var(--color-accent);
}

.share-modal-title {
  margin: 0;
  font-size: 1.125rem;
  font-weight: 650;
  color: var(--color-text);
}

.share-modal-close-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  background: transparent;
  border: none;
  border-radius: var(--radius-control, 0.375rem);
  color: var(--color-muted);
  cursor: pointer;
  transition: color 0.15s ease, background-color 0.15s ease;
}

.share-modal-close-btn:hover {
  background-color: var(--color-surface-hover);
  color: var(--color-text);
}

.share-modal-body {
  padding: 1.5rem;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  flex: 1;
}

.share-feedback-alert {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  font-size: 0.875rem;
  border-radius: var(--radius-control, 0.5rem);
}

.share-feedback-alert.error {
  background-color: var(--color-error-bg, rgba(239, 68, 68, 0.1));
  color: var(--color-error-text, #b91c1c);
  border: 1px solid var(--color-error-border, rgba(239, 68, 68, 0.2));
}

.share-feedback-alert.success {
  background-color: var(--color-success-bg, rgba(34, 197, 94, 0.1));
  color: var(--color-success-text, #15803d);
  border: 1px solid var(--color-success-border, rgba(34, 197, 94, 0.2));
}

.share-field-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.share-field-label {
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--color-muted);
}

.share-input-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  width: 100%;
  box-sizing: border-box;
}

.share-link-input {
  flex: 1 1 auto;
  min-width: 0;
  width: 100%;
  padding: 0.625rem 0.75rem;
  font-size: 0.875rem;
  font-family: monospace;
  background-color: var(--color-surface-soft, rgba(0, 0, 0, 0.03));
  border: var(--border-width, 1px) solid var(--color-border);
  border-radius: var(--radius-control, 0.5rem);
  color: var(--color-text);
  user-select: all;
  box-sizing: border-box;
}

.share-copy-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.375rem;
  min-height: 44px;
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
  font-weight: 600;
  border-radius: var(--radius-control, 0.5rem);
  border: none;
  background-color: var(--color-accent);
  color: var(--color-on-accent, #fff);
  cursor: pointer;
  flex-shrink: 0;
  white-space: nowrap;
  transition: background-color 0.15s ease;
}

.share-copy-btn:hover {
  background-color: var(--color-accent-hover, var(--color-accent));
}

.share-copy-btn.copied {
  background-color: var(--color-success-marker, #16a34a);
}

.share-visibility-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.share-effective-tag {
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.15rem 0.5rem;
  border-radius: 9999px;
  background-color: var(--color-surface-soft, rgba(0, 0, 0, 0.05));
  color: var(--color-muted);
}

.share-visibility-options {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  width: 100%;
  min-width: 0;
  box-sizing: border-box;
}

.share-visibility-option {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 0.75rem;
  width: 100%;
  min-width: 0;
  box-sizing: border-box;
  border-radius: var(--radius-control, 0.5rem);
  border: var(--border-width, 1px) solid var(--color-border);
  background-color: var(--color-surface);
  cursor: pointer;
  transition: all 0.15s ease;
}

.share-visibility-option:hover {
  background-color: var(--color-surface-hover);
}

.share-visibility-option.selected {
  border-color: var(--color-accent);
  background-color: var(--color-surface-hover);
  box-shadow: 0 0 0 1px var(--color-accent);
}

.share-visibility-option.disabled {
  opacity: 0.6;
  pointer-events: none;
}

.share-radio-input {
  margin-top: 0.2rem;
  flex-shrink: 0;
  width: 1.125rem;
  height: 1.125rem;
  cursor: pointer;
  accent-color: var(--color-accent);
}

.share-option-text {
  flex: 1 1 auto;
  min-width: 0;
  display: flex;
  flex-direction: column;
}

.share-option-label {
  display: block;
  font-size: 0.875rem;
  font-weight: 600;
  line-height: 1.35;
  color: var(--color-text);
  word-break: normal;
  overflow-wrap: break-word;
}

.share-option-desc {
  margin: 0.2rem 0 0;
  font-size: 0.75rem;
  color: var(--color-muted);
  line-height: 1.4;
  word-break: normal;
  overflow-wrap: break-word;
}

.share-acl-section {
  padding-top: 0.75rem;
  border-top: var(--border-width, 1px) solid var(--color-border);
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.share-username-wrap {
  position: relative;
  flex: 1;
}

.share-at-prefix {
  position: absolute;
  left: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  color: var(--color-muted);
  font-family: monospace;
}

.share-username-input {
  width: 100%;
  padding: 0.625rem 0.75rem 0.625rem 1.75rem;
  font-size: 0.875rem;
  background-color: var(--color-surface-soft, rgba(0, 0, 0, 0.03));
  border: var(--border-width, 1px) solid var(--color-border);
  border-radius: var(--radius-control, 0.5rem);
  color: var(--color-text);
  box-sizing: border-box;
}

.share-grant-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 44px;
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
  font-weight: 600;
  border-radius: var(--radius-control, 0.5rem);
  border: none;
  background-color: var(--color-accent);
  color: var(--color-on-accent, #fff);
  cursor: pointer;
  transition: opacity 0.15s ease;
}

.share-grant-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.share-readers-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.share-readers-title {
  margin: 0;
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--color-muted);
}

.share-empty-readers {
  padding: 1rem;
  text-align: center;
  font-size: 0.75rem;
  color: var(--color-muted);
  border: 1px dashed var(--color-border);
  border-radius: var(--radius-control, 0.5rem);
}

.share-readers-list {
  list-style: none;
  padding: 0;
  margin: 0;
  max-height: 12rem;
  overflow-y: auto;
  border: var(--border-width, 1px) solid var(--color-border);
  border-radius: var(--radius-control, 0.5rem);
}

.share-reader-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.625rem 0.75rem;
  gap: 0.75rem;
  border-bottom: var(--border-width, 1px) solid var(--color-border);
}

.share-reader-item:last-child {
  border-bottom: none;
}

.share-reader-info {
  display: flex;
  align-items: center;
  gap: 0.625rem;
  min-width: 0;
}

.share-reader-avatar {
  width: 32px;
  height: 32px;
  border-radius: 9999px;
  background-color: var(--color-surface-soft, rgba(0, 0, 0, 0.08));
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--color-accent);
  overflow: hidden;
  flex-shrink: 0;
}

.share-avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.share-reader-details {
  min-width: 0;
}

.share-reader-name {
  margin: 0;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.share-reader-handle {
  margin: 0;
  font-size: 0.75rem;
  font-family: monospace;
  color: var(--color-muted);
}

.share-revoke-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 44px;
  min-height: 44px;
  border: none;
  background: transparent;
  color: var(--color-muted);
  cursor: pointer;
  border-radius: var(--radius-control, 0.375rem);
  transition: color 0.15s ease, background-color 0.15s ease;
}

.share-revoke-btn:hover {
  color: var(--color-error-text, #ef4444);
  background-color: var(--color-error-bg, rgba(239, 68, 68, 0.1));
}

.share-modal-footer {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding: 0.75rem 1.5rem;
  border-top: var(--border-width, 1px) solid var(--color-border);
  background-color: var(--color-surface-soft, rgba(0, 0, 0, 0.02));
}

.share-done-btn {
  min-height: 44px;
  padding: 0.5rem 1.25rem;
  font-size: 0.875rem;
  font-weight: 600;
  border-radius: var(--radius-control, 0.5rem);
  border: var(--border-width, 1px) solid var(--color-border);
  background-color: var(--color-surface);
  color: var(--color-text);
  cursor: pointer;
  transition: background-color 0.15s ease;
}

.share-done-btn:hover {
  background-color: var(--color-surface-hover);
}

@media (max-width: 640px) {
  .share-modal-backdrop {
    padding: 0.5rem;
  }

  .share-modal-card {
    max-height: calc(100dvh - 1rem);
    border-radius: var(--radius-card, 0.75rem);
  }

  .share-modal-header {
    padding: 0.875rem 1rem;
  }

  .share-modal-body {
    padding: 1rem;
    gap: 1rem;
  }

  .share-modal-footer {
    padding: 0.75rem 1rem;
  }
}
</style>
