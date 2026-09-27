<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import type { NotificationItem } from '../../types/notifications.ts'
import Icon from '../ui/Icon.vue'
import { useNotifications } from '../../composables/useNotifications.ts'

const props = defineProps<{
  item: NotificationItem
}>()

const emit = defineEmits<{
  (e: 'close-dropdown'): void
}>()

const router = useRouter()
const { markAsRead, respondFriendRequest } = useNotifications()

const inlineActionStatus = ref<string | null>(null)
const inlineActionMessage = ref<string | null>(null)
const isSubmitting = ref(false)

const isUnread = computed(() => !props.item.read_at)

const eventIcon = computed(() => {
  switch (props.item.event_type) {
    case 'friend_request':
      return 'user-plus'
    case 'friend_accepted':
      return 'user-check'
    case 'study_shared':
      return 'book-open'
    case 'system_alert':
      return 'shield'
    default:
      return 'bell'
  }
})

const actorInitials = computed(() => {
  if (props.item.actor?.display_name) {
    const parts = props.item.actor.display_name.trim().split(/\s+/)
    if (parts.length >= 2) {
      return (parts[0][0] + parts[1][0]).toUpperCase()
    }
    return parts[0].slice(0, 2).toUpperCase()
  }
  if (props.item.actor?.username) {
    return props.item.actor.username.slice(0, 2).toUpperCase()
  }
  return 'LT'
})

const formattedTime = computed(() => {
  try {
    const d = new Date(props.item.created_at)
    const now = new Date()
    const diffSec = Math.floor((now.getTime() - d.getTime()) / 1000)
    if (diffSec < 60) return 'agora'
    const diffMin = Math.floor(diffSec / 60)
    if (diffMin < 60) return `há ${diffMin} min`
    const diffHours = Math.floor(diffMin / 60)
    if (diffHours < 24) return `há ${diffHours} h`
    const diffDays = Math.floor(diffHours / 24)
    if (diffDays === 1) return 'ontem'
    if (diffDays < 7) return `há ${diffDays} dias`
    return d.toLocaleDateString('pt-BR', { day: '2-digit', month: 'short' })
  } catch {
    return ''
  }
})

async function handleItemClick() {
  if (isUnread.value) {
    void markAsRead(props.item.id)
  }

  // Navegação contextual baseada no payload
  if (props.item.payload?.link) {
    emit('close-dropdown')
    await router.push(props.item.payload.link)
  } else if (props.item.event_type === 'study_shared' && props.item.payload?.study_id) {
    emit('close-dropdown')
    await router.push(`/estudos/${props.item.payload.study_id}`)
  } else if (
    (props.item.event_type === 'friend_accepted' || props.item.event_type === 'friend_request') &&
    props.item.actor?.username
  ) {
    emit('close-dropdown')
    await router.push(`/@${props.item.actor.username}`)
  }
}

async function handleAcceptFriend() {
  if (isSubmitting.value) return
  const friendshipId = props.item.payload?.friendship_id
  if (!friendshipId) return

  isSubmitting.value = true
  const res = await respondFriendRequest(props.item.id, friendshipId, 'accept')
  isSubmitting.value = false
  if (res.ok) {
    inlineActionStatus.value = 'accepted'
    inlineActionMessage.value = 'Amizade aceita'
  } else {
    inlineActionMessage.value = res.message
  }
}

async function handleRejectFriend() {
  if (isSubmitting.value) return
  const friendshipId = props.item.payload?.friendship_id
  if (!friendshipId) return

  isSubmitting.value = true
  const res = await respondFriendRequest(props.item.id, friendshipId, 'reject')
  isSubmitting.value = false
  if (res.ok) {
    inlineActionStatus.value = 'rejected'
    inlineActionMessage.value = 'Solicitação recusada'
  } else {
    inlineActionMessage.value = res.message
  }
}

async function handleMarkRead(event: Event) {
  event.stopPropagation()
  await markAsRead(props.item.id)
}
</script>

<template>
  <div
    class="notification-item"
    :class="{
      'is-unread': isUnread,
      'is-system-alert': item.event_type === 'system_alert',
      'is-severity-warning': item.payload?.severity === 'warning',
      'is-severity-critical': item.payload?.severity === 'critical',
      'is-clickable': Boolean(item.payload?.link || item.payload?.study_id || item.actor?.username),
    }"
    role="article"
    @click="handleItemClick"
  >
    <!-- Avatar ou Ícone do Evento -->
    <div class="notification-avatar-area">
      <div v-if="item.actor?.avatar_url" class="notification-avatar">
        <img :src="item.actor.avatar_url" :alt="item.actor.display_name" class="avatar-img" />
      </div>
      <div v-else-if="item.actor" class="notification-avatar-initials">
        {{ actorInitials }}
      </div>
      <div v-else class="notification-icon-badge" :class="item.event_type">
        <Icon :name="eventIcon" :size="18" />
      </div>
    </div>

    <!-- Conteúdo Textual da Notificação -->
    <div class="notification-content">
      <div class="notification-header-row">
        <span v-if="item.event_type === 'system_alert'" class="notification-title system-title">
          {{ item.payload?.title || 'Aviso da Plataforma' }}
        </span>
        <span v-else-if="item.actor" class="notification-actor-name">
          {{ item.actor.display_name }}
        </span>
        <span class="notification-time">{{ formattedTime }}</span>
      </div>

      <p class="notification-message">
        {{ item.payload?.message || item.payload?.resource_title || 'Nova notificação no Leitorum' }}
      </p>

      <!-- Ações Rápidas de Amizade (FR-005) -->
      <div
        v-if="item.event_type === 'friend_request' && !inlineActionStatus"
        class="friend-actions-row"
        @click.stop
      >
        <button
          type="button"
          class="btn-friend-accept"
          :disabled="isSubmitting"
          aria-label="Aceitar solicitação de amizade"
          @click="handleAcceptFriend"
        >
          <Icon name="check" :size="14" />
          <span>Aceitar</span>
        </button>
        <button
          type="button"
          class="btn-friend-reject"
          :disabled="isSubmitting"
          aria-label="Recusar solicitação de amizade"
          @click="handleRejectFriend"
        >
          <Icon name="x" :size="14" />
          <span>Recusar</span>
        </button>
      </div>

      <!-- Feedback Inline de Confirmação -->
      <div v-else-if="inlineActionMessage" class="inline-feedback-msg" :class="inlineActionStatus">
        {{ inlineActionMessage }}
      </div>
    </div>

    <!-- Indicador de Não Lido / Ação de Marcar Lido -->
    <div class="notification-status-area">
      <button
        v-if="isUnread"
        type="button"
        class="btn-mark-read"
        title="Marcar como lida"
        aria-label="Marcar como lida"
        @click="handleMarkRead"
      >
        <span class="unread-dot" aria-hidden="true" />
      </button>
    </div>
  </div>
</template>

<style scoped>
.notification-item {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 0.85rem 1rem;
  border-bottom: 1px solid var(--color-border, #e5e7eb);
  background-color: var(--color-surface, #ffffff);
  transition: background-color 0.15s ease;
  position: relative;
}

.notification-item:hover {
  background-color: var(--color-surface-hover, #f9fafb);
}

.notification-item.is-clickable {
  cursor: pointer;
}

.notification-item.is-unread {
  background-color: var(--color-surface-selected, rgba(59, 130, 246, 0.05));
}

.notification-item.is-system-alert {
  border-left: 3px solid var(--color-accent, #3b82f6);
}

.notification-item.is-system-alert.is-severity-warning {
  border-left-color: #d97706;
}

.notification-item.is-system-alert.is-severity-critical {
  border-left-color: #dc2626;
}

.notification-avatar-area {
  flex-shrink: 0;
  margin-top: 0.15rem;
}

.notification-avatar,
.notification-avatar-initials,
.notification-icon-badge {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar-img {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
}

.notification-avatar-initials {
  background: var(--color-primary-light, #e0e7ff);
  color: var(--color-primary, #4338ca);
  font-weight: 600;
  font-size: 0.85rem;
}

.notification-icon-badge {
  background: var(--color-surface-muted, #f3f4f6);
  color: var(--color-text-muted, #6b7280);
}

.notification-icon-badge.system_alert {
  background: rgba(59, 130, 246, 0.12);
  color: #2563eb;
}

.notification-icon-badge.friend_request,
.notification-icon-badge.friend_accepted {
  background: rgba(16, 185, 129, 0.12);
  color: #059669;
}

.notification-icon-badge.study_shared {
  background: rgba(245, 158, 11, 0.12);
  color: #d97706;
}

.notification-content {
  flex: 1;
  min-width: 0;
}

.notification-header-row {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 0.5rem;
  margin-bottom: 0.2rem;
}

.notification-actor-name {
  font-weight: 600;
  font-size: 0.88rem;
  color: var(--color-text, #111827);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.notification-title.system-title {
  font-weight: 600;
  font-size: 0.88rem;
  color: var(--color-text, #111827);
}

.notification-time {
  font-size: 0.75rem;
  color: var(--color-text-muted, #9ca3af);
  white-space: nowrap;
  flex-shrink: 0;
}

.notification-message {
  font-size: 0.83rem;
  line-height: 1.35;
  color: var(--color-text-muted, #4b5563);
  margin: 0;
  word-break: break-word;
}

.friend-actions-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.btn-friend-accept {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  padding: 0.25rem 0.65rem;
  font-size: 0.78rem;
  font-weight: 500;
  border-radius: 4px;
  background-color: var(--color-primary, #2563eb);
  color: #ffffff;
  border: none;
  cursor: pointer;
  transition: opacity 0.15s ease;
}

.btn-friend-accept:hover:not(:disabled) {
  opacity: 0.9;
}

.btn-friend-reject {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  padding: 0.25rem 0.65rem;
  font-size: 0.78rem;
  font-weight: 500;
  border-radius: 4px;
  background-color: var(--color-surface-muted, #f3f4f6);
  color: var(--color-text, #374151);
  border: 1px solid var(--color-border, #d1d5db);
  cursor: pointer;
  transition: background-color 0.15s ease;
}

.btn-friend-reject:hover:not(:disabled) {
  background-color: var(--color-surface-hover, #e5e7eb);
}

.inline-feedback-msg {
  margin-top: 0.4rem;
  font-size: 0.78rem;
  font-weight: 500;
  color: var(--color-text-muted, #6b7280);
}

.inline-feedback-msg.accepted {
  color: #059669;
}

.inline-feedback-msg.rejected {
  color: #dc2626;
}

.notification-status-area {
  flex-shrink: 0;
  display: flex;
  align-items: center;
}

.btn-mark-read {
  background: transparent;
  border: none;
  padding: 0.25rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.unread-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: var(--color-accent, #3b82f6);
  display: block;
}
</style>
