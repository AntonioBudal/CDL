<script setup lang="ts">
import { ref } from 'vue'
import Icon from './ui/Icon.vue'
import { getInitials } from '../composables/useProfile.ts'

const props = withDefaults(
  defineProps<{
    username: string
    displayName: string
    avatarUrl?: string | null
    bio?: string | null
    friendsCount?: number
    pendingCount?: number
  }>(),
  {
    avatarUrl: null,
    bio: null,
    friendsCount: 0,
    pendingCount: 0,
  }
)

const emit = defineEmits<{
  (e: 'copied', handle: string): void
  (e: 'shared', url: string): void
}>()

const isStamped = ref(false)
const shareFeedback = ref<string | null>(null)
let stampTimeout: ReturnType<typeof setTimeout> | null = null
let shareTimeout: ReturnType<typeof setTimeout> | null = null

async function handleCopy() {
  if (!props.username) return
  const handleText = `@${props.username}`
  try {
    if (typeof navigator !== 'undefined' && navigator.clipboard) {
      await navigator.clipboard.writeText(handleText)
    }
  } catch {
    // Fallback silencioso de permissão
  }
  isStamped.value = true
  if (stampTimeout) clearTimeout(stampTimeout)
  stampTimeout = setTimeout(() => {
    isStamped.value = false
  }, 1200)
  emit('copied', handleText)
}

async function handleShare() {
  if (!props.username) return
  const origin = typeof window !== 'undefined' ? window.location.origin : ''
  const profileUrl = `${origin}/u/${props.username}`

  if (typeof navigator !== 'undefined' && typeof navigator.share === 'function') {
    try {
      await navigator.share({
        title: `${props.displayName || props.username} no Leitorum`,
        text: 'Acompanhe minhas leituras e cadernos de estudo no Leitorum:',
        url: profileUrl,
      })
      emit('shared', profileUrl)
      return
    } catch (err: unknown) {
      if (err instanceof Error && err.name === 'AbortError') {
        return
      }
    }
  }

  // Fallback para cópia do link do perfil
  try {
    if (typeof navigator !== 'undefined' && navigator.clipboard) {
      await navigator.clipboard.writeText(profileUrl)
    }
    shareFeedback.value = 'Link copiado!'
    if (shareTimeout) clearTimeout(shareTimeout)
    shareTimeout = setTimeout(() => {
      shareFeedback.value = null
    }, 1200)
    emit('shared', profileUrl)
  } catch {
    // Fallback silencioso
  }
}
</script>

<template>
  <header
    class="bookplate-card panel"
    role="region"
    aria-label="Ex-Líbris Digital do Leitor"
  >
    <div class="bookplate-inner">
      <!-- Avatar ou Iniciais do Leitor -->
      <div class="bookplate-avatar">
        <img
          v-if="avatarUrl"
          :src="avatarUrl"
          :alt="displayName || username"
          class="bookplate-avatar-img"
        />
        <div v-else class="bookplate-avatar-initials" aria-hidden="true">
          {{ getInitials(displayName || username) }}
        </div>
      </div>

      <!-- Informações Literárias e Identidade -->
      <div class="bookplate-info">
        <div class="bookplate-title-row">
          <h2 class="bookplate-name">{{ displayName || username }}</h2>
          <span class="bookplate-handle muted">@{{ username }}</span>
        </div>

        <p v-if="bio" class="bookplate-bio">{{ bio }}</p>

        <!-- Pílulas e Contadores de Afinidade -->
        <div class="bookplate-metrics" aria-label="Estatísticas do círculo">
          <span class="bookplate-badge">
            <Icon name="users" :size="14" />
            <span>{{ friendsCount }} {{ friendsCount === 1 ? 'conexão literária' : 'conexões literárias' }}</span>
          </span>
          <span
            v-if="pendingCount > 0"
            class="bookplate-badge alert-badge"
            aria-label="Solicitações recebidas pendentes"
          >
            <Icon name="mail" :size="14" />
            <span>{{ pendingCount }} pendente{{ pendingCount > 1 ? 's' : '' }}</span>
          </span>
        </div>
      </div>

      <!-- Ações do Ex-Líbris: Cópia e Compartilhamento -->
      <div class="bookplate-actions">
        <!-- Botão com Selo Literário de 1200ms -->
        <button
          type="button"
          class="button secondary action-btn copy-stamp-btn"
          :class="{ 'is-stamped': isStamped }"
          :aria-label="isStamped ? 'Identificador copiado' : `Copiar meu identificador @${username}`"
          @click="handleCopy"
        >
          <Icon :name="isStamped ? 'check' : 'copy'" :size="16" />
          <span>{{ isStamped ? 'Selo aplicado!' : `@${username}` }}</span>
        </button>

        <!-- Botão de Compartilhamento (Web Share / Link) -->
        <button
          type="button"
          class="button primary action-btn share-profile-btn"
          :aria-label="`Compartilhar perfil literário de @${username}`"
          @click="handleShare"
        >
          <Icon :name="shareFeedback ? 'check' : 'external-link'" :size="16" />
          <span>{{ shareFeedback || 'Compartilhar Perfil' }}</span>
        </button>
      </div>
    </div>
  </header>
</template>

<style scoped>
.bookplate-card {
  padding: 1.5rem;
  margin-bottom: 2rem;
  border-radius: var(--radius-surface, 12px);
  background-color: var(--color-surface);
  border: 1px solid var(--color-border);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.bookplate-inner {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  flex-wrap: wrap;
}

.bookplate-avatar {
  flex-shrink: 0;
  width: 64px;
  height: 64px;
}

.bookplate-avatar-img {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid var(--color-border);
}

.bookplate-avatar-initials {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background-color: var(--color-surface-soft);
  color: var(--color-text);
  border: 2px solid var(--color-border);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  font-weight: 700;
  letter-spacing: 0.02em;
}

.bookplate-info {
  flex: 1;
  min-width: 240px;
}

.bookplate-title-row {
  display: flex;
  align-items: baseline;
  gap: 0.6rem;
  flex-wrap: wrap;
  margin-bottom: 0.35rem;
}

.bookplate-name {
  margin: 0;
  font-size: 1.4rem;
  font-weight: 700;
  color: var(--color-text);
  line-height: 1.2;
}

.bookplate-handle {
  font-family: var(--font-mono, monospace);
  font-size: 0.95rem;
  color: var(--color-text-muted);
}

.bookplate-bio {
  margin: 0 0 0.6rem;
  font-size: 0.925rem;
  line-height: 1.45;
  color: var(--color-text-muted);
  max-width: 42rem;
}

.bookplate-metrics {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.bookplate-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.25rem 0.65rem;
  border-radius: 9999px;
  background-color: var(--color-surface-soft);
  color: var(--color-text);
  border: 1px solid var(--color-border);
  font-size: 0.8rem;
  font-weight: 500;
}

.bookplate-badge.alert-badge {
  background-color: var(--color-surface-soft);
  color: var(--color-accent);
  border-color: var(--color-accent);
}

.bookplate-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
  margin-left: auto;
}

.action-btn {
  min-height: 44px;
  min-width: 44px;
  padding: 0.5rem 1.15rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  font-weight: 600;
  border-radius: var(--radius-sm, 6px);
  cursor: pointer;
  white-space: nowrap;
}

.copy-stamp-btn {
  transition: transform 0.2s cubic-bezier(0.16, 1, 0.3, 1),
              background-color 0.2s ease,
              border-color 0.2s ease,
              color 0.2s ease;
  will-change: transform;
}

.copy-stamp-btn.is-stamped {
  transform: scale(1.04);
  background-color: var(--color-surface-soft);
  border-color: var(--color-primary);
  color: var(--color-primary);
}

@media (prefers-reduced-motion: reduce) {
  .copy-stamp-btn.is-stamped {
    transform: none;
  }
}

@media (max-width: 640px) {
  .bookplate-actions {
    width: 100%;
    margin-left: 0;
    margin-top: 0.5rem;
  }
  .action-btn {
    flex: 1;
  }
}
</style>
