<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { sharingApi } from '../../api/sharing.ts'
import type {
  ResourcePermissionsRead,
  ResourcePermissionItem,
  ResourceVisibility,
} from '../../types.ts'

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
    class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm"
    role="dialog"
    aria-modal="true"
    aria-labelledby="share-modal-title"
    @click.self="close"
  >
    <div
      class="w-full max-w-lg overflow-hidden bg-white dark:bg-zinc-900 rounded-2xl shadow-2xl border border-zinc-200 dark:border-zinc-800 transition-all flex flex-col max-h-[90vh]"
    >
      <!-- Modal Header -->
      <header class="flex items-center justify-between px-6 py-4 border-b border-zinc-100 dark:border-zinc-800/80">
        <div class="flex items-center gap-2">
          <svg class="w-5 h-5 text-amber-600 dark:text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
          </svg>
          <h2 id="share-modal-title" class="text-lg font-semibold text-zinc-900 dark:text-zinc-100">
            Compartilhar Estudo
          </h2>
        </div>
        <button
          type="button"
          class="flex items-center justify-center w-11 h-11 text-zinc-400 hover:text-zinc-600 dark:hover:text-zinc-200 rounded-lg hover:bg-zinc-100 dark:hover:bg-zinc-800 transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-amber-500"
          aria-label="Fechar janela de compartilhamento"
          @click="close"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </header>

      <!-- Modal Body (Scrollable) -->
      <div class="p-6 overflow-y-auto space-y-6 flex-1">
        <!-- Notificações de feedback -->
        <div
          v-if="error"
          class="p-3 text-sm rounded-xl bg-red-50 dark:bg-red-950/40 text-red-700 dark:text-red-300 border border-red-200 dark:border-red-900/50 flex items-center gap-2"
          role="alert"
        >
          <svg class="w-4 h-4 text-red-600 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <span>{{ error }}</span>
        </div>

        <div
          v-if="successMsg"
          class="p-3 text-sm rounded-xl bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-900/50 flex items-center gap-2"
          role="status"
        >
          <svg class="w-4 h-4 text-emerald-600 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
          </svg>
          <span>{{ successMsg }}</span>
        </div>

        <!-- Copiar Link do Estudo -->
        <div class="space-y-2">
          <label class="block text-xs font-semibold uppercase tracking-wider text-zinc-500 dark:text-zinc-400">
            Link direto para o estudo
          </label>
          <div class="flex items-center gap-2">
            <input
              type="text"
              readonly
              :value="studyLink"
              class="flex-1 px-3 py-2.5 text-sm rounded-xl bg-zinc-50 dark:bg-zinc-800/60 border border-zinc-200 dark:border-zinc-700 text-zinc-700 dark:text-zinc-300 select-all font-mono focus:outline-none"
              aria-label="Link do estudo"
            />
            <button
              type="button"
              class="inline-flex items-center justify-center min-h-[44px] px-4 py-2 text-sm font-medium rounded-xl transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-amber-500"
              :class="
                copyFeedback
                  ? 'bg-emerald-600 text-white'
                  : 'bg-amber-600 hover:bg-amber-500 text-white shadow-sm hover:shadow'
              "
              aria-label="Copiar link do estudo"
              @click="copyLink"
            >
              <span v-if="copyFeedback" class="flex items-center gap-1.5">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                </svg>
                Copiado!
              </span>
              <span v-else class="flex items-center gap-1.5">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m0 0h2a2 2 0 012 2v3m2 4H10m0 0l3-3m-3 3l3 3" />
                </svg>
                Copiar
              </span>
            </button>
          </div>
        </div>

        <!-- Seção de Visibilidade -->
        <div class="space-y-3">
          <div class="flex items-center justify-between">
            <label class="block text-xs font-semibold uppercase tracking-wider text-zinc-500 dark:text-zinc-400">
              Nível de Visibilidade
            </label>
            <span
              v-if="effectiveVisibility"
              class="text-xs px-2 py-0.5 rounded-full font-medium bg-zinc-100 dark:bg-zinc-800 text-zinc-600 dark:text-zinc-400"
            >
              Efetivo: {{ effectiveVisibility }}
            </span>
          </div>

          <div class="grid grid-cols-1 gap-2" role="radiogroup" aria-label="Nível de visibilidade do estudo">
            <label
              v-for="opt in visibilityOptions"
              :key="opt.value"
              class="flex items-start gap-3 p-3 rounded-xl border transition-all cursor-pointer select-none"
              :class="[
                currentVisibility === opt.value
                  ? 'border-amber-500 bg-amber-50/50 dark:bg-amber-950/20 ring-1 ring-amber-500/50'
                  : 'border-zinc-200 dark:border-zinc-800 hover:bg-zinc-50 dark:hover:bg-zinc-800/40',
                saving ? 'opacity-60 pointer-events-none' : '',
              ]"
            >
              <input
                type="radio"
                name="study-visibility"
                :value="opt.value"
                :checked="currentVisibility === opt.value"
                class="mt-1 w-4 h-4 text-amber-600 border-zinc-300 dark:border-zinc-700 focus:ring-amber-500 focus:ring-offset-0"
                @change="onVisibilityChange(opt.value)"
              />
              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-1.5 text-sm font-medium text-zinc-900 dark:text-zinc-100">
                  <span>{{ opt.label }}</span>
                </div>
                <p class="text-xs text-zinc-500 dark:text-zinc-400 mt-0.5 leading-relaxed">
                  {{ opt.desc }}
                </p>
              </div>
            </label>
          </div>
        </div>

        <!-- Seção ACL Granular (Apenas no modo 'custom') -->
        <div v-if="currentVisibility === 'custom'" class="pt-2 border-t border-zinc-100 dark:border-zinc-800 space-y-4">
          <label class="block text-xs font-semibold uppercase tracking-wider text-zinc-500 dark:text-zinc-400">
            Conceder Acesso Nominal
          </label>

          <!-- Input para adicionar amigo por username -->
          <form class="flex items-center gap-2" @submit.prevent="handleGrantPermission">
            <div class="relative flex-1">
              <span class="absolute left-3 top-1/2 -translate-y-1/2 text-zinc-400 text-sm font-mono">@</span>
              <input
                v-model="newReaderUsername"
                type="text"
                placeholder="nome_do_leitor"
                maxlength="50"
                class="w-full pl-8 pr-3 py-2.5 text-sm rounded-xl bg-zinc-50 dark:bg-zinc-800/60 border border-zinc-200 dark:border-zinc-700 text-zinc-900 dark:text-zinc-100 placeholder-zinc-400 focus:outline-none focus:ring-2 focus:ring-amber-500/50 focus:border-amber-500"
                aria-label="Handle do leitor para conceder acesso"
              />
            </div>
            <button
              type="submit"
              :disabled="!newReaderUsername.trim() || granting"
              class="inline-flex items-center justify-center min-h-[44px] px-4 py-2 text-sm font-medium rounded-xl bg-amber-600 hover:bg-amber-500 disabled:opacity-50 text-white shadow-sm transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-amber-500"
            >
              <span v-if="granting">Concedendo...</span>
              <span v-else>Conceder</span>
            </button>
          </form>

          <!-- Lista de Leitores Autorizados -->
          <div class="space-y-2">
            <h4 class="text-xs font-medium text-zinc-600 dark:text-zinc-400">
              Leitores autorizados ({{ permissions.length }})
            </h4>

            <div v-if="permissions.length === 0" class="p-4 text-center text-xs text-zinc-400 dark:text-zinc-500 border border-dashed border-zinc-200 dark:border-zinc-800 rounded-xl">
              Nenhum leitor convidado ainda. Digite o @username acima para autorizar.
            </div>

            <ul v-else class="divide-y divide-zinc-100 dark:divide-zinc-800/80 rounded-xl border border-zinc-200 dark:border-zinc-800 max-h-48 overflow-y-auto">
              <li
                v-for="user in permissions"
                :key="user.user_id"
                class="flex items-center justify-between p-3 gap-3 hover:bg-zinc-50 dark:hover:bg-zinc-800/40 transition-colors"
              >
                <div class="flex items-center gap-2.5 min-w-0">
                  <div
                    class="w-8 h-8 rounded-full bg-amber-100 dark:bg-amber-950/60 text-amber-800 dark:text-amber-300 flex items-center justify-center text-xs font-semibold overflow-hidden shrink-0"
                  >
                    <img
                      v-if="user.avatar_url"
                      :src="user.avatar_url"
                      :alt="user.display_name"
                      class="w-full h-full object-cover"
                    />
                    <span v-else>{{ user.display_name.charAt(0).toUpperCase() }}</span>
                  </div>
                  <div class="min-w-0">
                    <p class="text-sm font-medium text-zinc-900 dark:text-zinc-100 truncate">
                      {{ user.display_name }}
                    </p>
                    <p class="text-xs text-zinc-400 dark:text-zinc-500 font-mono truncate">
                      @{{ user.username }}
                    </p>
                  </div>
                </div>

                <button
                  type="button"
                  class="flex items-center justify-center min-w-[44px] min-h-[44px] text-zinc-400 hover:text-red-600 dark:hover:text-red-400 rounded-lg hover:bg-red-50 dark:hover:bg-red-950/40 transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-red-500"
                  :aria-label="`Revogar acesso de @${user.username}`"
                  :disabled="revokingUserId === user.user_id"
                  @click="handleRevokePermission(user.user_id, user.username)"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>
              </li>
            </ul>
          </div>
        </div>
      </div>

      <!-- Modal Footer -->
      <footer class="flex items-center justify-end px-6 py-3.5 border-t border-zinc-100 dark:border-zinc-800/80 bg-zinc-50 dark:bg-zinc-900/50">
        <button
          type="button"
          class="min-h-[44px] px-5 py-2 text-sm font-medium text-zinc-700 dark:text-zinc-300 hover:text-zinc-900 dark:hover:text-zinc-100 rounded-xl hover:bg-zinc-100 dark:hover:bg-zinc-800 transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-amber-500"
          @click="close"
        >
          Concluir
        </button>
      </footer>
    </div>
  </div>
</template>
