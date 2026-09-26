<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import type { RelationPerspectiveStatus } from '../types.ts'
import { useFriends } from '../composables/useFriends.ts'
import Icon from './ui/Icon.vue'

const props = withDefaults(
  defineProps<{
    username: string
    initialStatus?: RelationPerspectiveStatus
    initialRequestId?: number | null
    compact?: boolean
    allowBlock?: boolean
  }>(),
  {
    initialStatus: undefined,
    initialRequestId: null,
    compact: false,
    allowBlock: true,
  }
)

const emit = defineEmits<{
  (e: 'status-changed', newStatus: RelationPerspectiveStatus): void
}>()

const friendsService = useFriends()

const relationStatus = ref<RelationPerspectiveStatus>(props.initialStatus || 'none')
const requestId = ref<number | null>(props.initialRequestId)
const isChecking = ref<boolean>(false)
const showBlockConfirm = ref<boolean>(false)
const showUnfriendConfirm = ref<boolean>(false)

const isBusy = computed(() => {
  return (
    isChecking.value ||
    friendsService.isActionLoading(props.username) ||
    (requestId.value != null &&
      (friendsService.isActionLoading(`accept-${requestId.value}`) ||
        friendsService.isActionLoading(`reject-${requestId.value}`) ||
        friendsService.isActionLoading(`cancel-${requestId.value}`))) ||
    friendsService.isActionLoading(`remove-${props.username}`) ||
    friendsService.isActionLoading(`block-${props.username}`) ||
    friendsService.isActionLoading(`unblock-${props.username}`)
  )
})

async function checkStatus() {
  if (props.initialStatus && props.initialStatus !== 'none') {
    relationStatus.value = props.initialStatus
    requestId.value = props.initialRequestId
    return
  }
  isChecking.value = true
  try {
    const res = await friendsService.getRelationStatus(props.username)
    relationStatus.value = res.relation_status
    requestId.value = res.request_id || null
  } finally {
    isChecking.value = false
  }
}

watch(
  () => props.username,
  () => {
    void checkStatus()
  }
)

watch(
  () => props.initialStatus,
  (newVal) => {
    if (newVal) relationStatus.value = newVal
  }
)

onMounted(() => {
  void checkStatus()
})

async function handleConnect() {
  try {
    const res = await friendsService.sendRequest(props.username)
    if (res.status === 'accepted') {
      relationStatus.value = 'friends'
    } else {
      relationStatus.value = 'pending_sent'
    }
    emit('status-changed', relationStatus.value)
  } catch {
    // Erro gerenciado no composable
  }
}

async function handleAccept() {
  if (requestId.value == null) {
    await checkStatus()
    if (requestId.value == null) return
  }
  try {
    await friendsService.acceptRequest(requestId.value)
    relationStatus.value = 'friends'
    emit('status-changed', 'friends')
  } catch {
    // Erro no composable
  }
}

async function handleReject() {
  if (requestId.value == null) {
    await checkStatus()
    if (requestId.value == null) return
  }
  try {
    await friendsService.rejectRequest(requestId.value)
    relationStatus.value = 'none'
    requestId.value = null
    emit('status-changed', 'none')
  } catch {
    // Erro no composable
  }
}

async function handleCancelRequest() {
  if (requestId.value == null) {
    await checkStatus()
    if (requestId.value == null) return
  }
  try {
    await friendsService.cancelRequest(requestId.value)
    relationStatus.value = 'none'
    requestId.value = null
    emit('status-changed', 'none')
  } catch {
    // Erro no composable
  }
}

async function handleConfirmUnfriend() {
  showUnfriendConfirm.value = false
  try {
    await friendsService.removeFriend(props.username)
    relationStatus.value = 'none'
    requestId.value = null
    emit('status-changed', 'none')
  } catch {
    // Erro no composable
  }
}

async function handleConfirmBlock() {
  showBlockConfirm.value = false
  try {
    await friendsService.blockUser(props.username)
    relationStatus.value = 'blocked_by_me'
    requestId.value = null
    emit('status-changed', 'blocked_by_me')
  } catch {
    // Erro no composable
  }
}

async function handleUnblock() {
  try {
    await friendsService.unblockUser(props.username)
    relationStatus.value = 'none'
    emit('status-changed', 'none')
  } catch {
    // Erro no composable
  }
}
</script>

<template>
  <div class="friend-action-container" :class="{ compact }">
    <!-- Estado: Sem relação -->
    <template v-if="relationStatus === 'none'">
      <button
        type="button"
        class="button primary action-btn"
        :disabled="isBusy"
        :aria-label="`Conectar com @${username}`"
        @click="handleConnect"
      >
        <Icon name="user-plus" :size="16" />
        <span>Conectar</span>
      </button>

      <button
        v-if="allowBlock && !compact"
        type="button"
        class="button secondary subtle action-btn block-btn"
        :disabled="isBusy"
        :aria-label="`Bloquear usuário @${username}`"
        @click="showBlockConfirm = true"
      >
        <Icon name="ban" :size="16" />
        <span>Bloquear</span>
      </button>
    </template>

    <!-- Estado: Solicitação Enviada -->
    <template v-else-if="relationStatus === 'pending_sent'">
      <div class="pending-pill" aria-label="Solicitação de amizade enviada">
        <Icon name="clock" :size="14" />
        <span>Solicitação enviada</span>
      </div>

      <button
        type="button"
        class="button secondary subtle action-btn"
        :disabled="isBusy"
        :aria-label="`Cancelar solicitação enviada para @${username}`"
        @click="handleCancelRequest"
      >
        <Icon name="x" :size="14" />
        <span>Cancelar</span>
      </button>
    </template>

    <!-- Estado: Solicitação Recebida -->
    <template v-else-if="relationStatus === 'pending_received'">
      <button
        type="button"
        class="button primary action-btn"
        :disabled="isBusy"
        :aria-label="`Aceitar solicitação de amizade de @${username}`"
        @click="handleAccept"
      >
        <Icon name="check" :size="16" />
        <span>Aceitar</span>
      </button>

      <button
        type="button"
        class="button secondary action-btn"
        :disabled="isBusy"
        :aria-label="`Recusar solicitação de amizade de @${username}`"
        @click="handleReject"
      >
        <Icon name="x" :size="16" />
        <span>Recusar</span>
      </button>
    </template>

    <!-- Estado: Amigos -->
    <template v-else-if="relationStatus === 'friends'">
      <div class="friends-pill" aria-label="Vocês são amigos">
        <Icon name="check-circle" :size="16" />
        <span>Amigos</span>
      </div>

      <button
        type="button"
        class="button secondary subtle action-btn danger-hover"
        :disabled="isBusy"
        :aria-label="`Desfazer amizade com @${username}`"
        @click="showUnfriendConfirm = true"
      >
        <Icon name="user-minus" :size="14" />
        <span v-if="!compact">Desfazer amizade</span>
      </button>
    </template>

    <!-- Estado: Bloqueado por mim -->
    <template v-else-if="relationStatus === 'blocked_by_me'">
      <div class="blocked-pill" aria-label="Usuário bloqueado">
        <Icon name="ban" :size="14" />
        <span>Bloqueado</span>
      </div>

      <button
        type="button"
        class="button secondary action-btn"
        :disabled="isBusy"
        :aria-label="`Desbloquear @${username}`"
        @click="handleUnblock"
      >
        <Icon name="unlock" :size="16" />
        <span>Desbloquear</span>
      </button>
    </template>

    <!-- Modal de Confirmação para Desfazer Amizade -->
    <div
      v-if="showUnfriendConfirm"
      class="dialog-overlay"
      role="dialog"
      aria-modal="true"
      aria-labelledby="unfriend-title"
    >
      <div class="dialog-card panel">
        <h3 id="unfriend-title">Desfazer amizade?</h3>
        <p class="muted">
          Você deixará de ver as anotações restritas a amigos de @{{ username }}. Esta ação pode ser revertida enviando uma nova solicitação.
        </p>
        <div class="dialog-actions">
          <button
            type="button"
            class="button secondary action-btn"
            @click="showUnfriendConfirm = false"
          >
            Cancelar
          </button>
          <button
            type="button"
            class="button danger action-btn"
            :disabled="isBusy"
            @click="handleConfirmUnfriend"
          >
            Confirmar e remover
          </button>
        </div>
      </div>
    </div>

    <!-- Modal de Confirmação para Bloquear -->
    <div
      v-if="showBlockConfirm"
      class="dialog-overlay"
      role="dialog"
      aria-modal="true"
      aria-labelledby="block-title"
    >
      <div class="dialog-card panel">
        <h3 id="block-title">Bloquear @{{ username }}?</h3>
        <p class="muted">
          Ao bloquear este leitor, qualquer vínculo de amizade será desfeito imediatamente. Ele não poderá encontrar seu perfil nem interagir com seus estudos.
        </p>
        <div class="dialog-actions">
          <button
            type="button"
            class="button secondary action-btn"
            @click="showBlockConfirm = false"
          >
            Voltar
          </button>
          <button
            type="button"
            class="button danger action-btn"
            :disabled="isBusy"
            @click="handleConfirmBlock"
          >
            Bloquear usuário
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.friend-action-container {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.action-btn {
  min-height: 44px;
  min-width: 44px;
  padding: 0.5rem 1rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
  border-radius: var(--radius-sm, 6px);
  font-size: 0.875rem;
  cursor: pointer;
  transition: background-color 0.15s ease, opacity 0.15s ease;
}

.action-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.compact .action-btn {
  min-height: 38px;
  padding: 0.35rem 0.75rem;
  font-size: 0.8125rem;
}

.pending-pill,
.friends-pill,
.blocked-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  min-height: 44px;
  padding: 0.5rem 0.875rem;
  border-radius: var(--radius-sm, 6px);
  font-size: 0.875rem;
  font-weight: 500;
}

.compact .pending-pill,
.compact .friends-pill,
.compact .blocked-pill {
  min-height: 38px;
  padding: 0.35rem 0.65rem;
  font-size: 0.8125rem;
}

.pending-pill {
  background-color: var(--color-surface-soft, rgba(0, 0, 0, 0.04));
  color: var(--color-text-muted, #666);
  border: 1px solid var(--color-border, #e5e5e5);
}

.friends-pill {
  background-color: rgba(34, 197, 94, 0.1);
  color: #16a34a;
  border: 1px solid rgba(34, 197, 94, 0.25);
}

.blocked-pill {
  background-color: rgba(239, 68, 68, 0.1);
  color: #dc2626;
  border: 1px solid rgba(239, 68, 68, 0.25);
}

.subtle {
  background: transparent;
  border-color: var(--color-border, #e5e5e5);
  color: var(--color-text-muted, #666);
}

.danger-hover:hover {
  border-color: rgba(239, 68, 68, 0.5);
  color: #dc2626;
}

.dialog-overlay {
  position: fixed;
  inset: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.dialog-card {
  max-width: 28rem;
  width: 100%;
  padding: 1.5rem;
  border-radius: var(--radius-surface, 12px);
  background-color: var(--color-surface, #fff);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
}

.dialog-card h3 {
  margin-top: 0;
  margin-bottom: 0.75rem;
  font-size: 1.125rem;
}

.dialog-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 1.25rem;
}
</style>
