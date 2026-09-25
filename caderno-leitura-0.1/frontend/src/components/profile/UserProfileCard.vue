<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink } from 'vue-router'
import type { UserProfilePublic } from '../../types.ts'
import Icon from '../ui/Icon.vue'
import { getInitials } from '../../composables/useProfile.ts'

const props = withDefaults(
  defineProps<{
    profile: UserProfilePublic
    isOwner?: boolean
    showEditButton?: boolean
  }>(),
  {
    isOwner: false,
    showEditButton: false,
  }
)

const initials = computed(() =>
  getInitials(props.profile.display_name || props.profile.username)
)

const formattedDate = computed(() => {
  if (!props.profile.created_at) return ''
  try {
    const d = new Date(props.profile.created_at)
    return d.toLocaleDateString('pt-BR', { month: 'long', year: 'numeric' })
  } catch {
    return ''
  }
})

const restrictionNotice = computed(() => {
  if (props.profile.profile_visibility === 'friends') {
    return 'Visível apenas para amigos'
  }
  return 'Este perfil é privado'
})
</script>

<template>
  <article class="profile-card panel">
    <div class="profile-header">
      <!-- Avatar com recorte quadrado/circular ou Iniciais -->
      <div class="profile-avatar-container">
        <img
          v-if="profile.avatar_url"
          :src="profile.avatar_url"
          :alt="`Avatar de ${profile.display_name || profile.username}`"
          class="profile-avatar-img"
        />
        <div v-else class="profile-avatar-initials" aria-hidden="true">
          {{ initials }}
        </div>
      </div>

      <!-- Informações de Identidade -->
      <div class="profile-identity">
        <div class="profile-title-row">
          <h1 class="profile-name">
            {{ profile.display_name || profile.username }}
          </h1>
          <RouterLink
            v-if="isOwner && showEditButton"
            to="/ajustes"
            class="button secondary edit-profile-btn"
            title="Editar perfil nos ajustes"
          >
            <Icon name="pencil" :size="16" />
            <span>Editar perfil</span>
          </RouterLink>
        </div>
        <p class="profile-handle muted">@{{ profile.username }}</p>

        <div v-if="formattedDate" class="profile-meta-row muted">
          <Icon name="calendar" :size="14" />
          <span>Membro desde {{ formattedDate }}</span>
        </div>
      </div>
    </div>

    <!-- Estado Restrito / Cartão Discreto para Perfis Privados -->
    <div v-if="profile.is_private" class="restricted-card" role="note">
      <div class="restricted-badge">
        <Icon name="lock" :size="18" />
        <strong>{{ restrictionNotice }}</strong>
      </div>
      <p class="restricted-desc muted">
        As anotações, biografia e estatísticas deste leitor estão protegidas pelas configurações de privacidade.
      </p>
    </div>

    <!-- Conteúdo Público (quando o perfil não é privado) -->
    <template v-else>
      <!-- Biografia do Leitor -->
      <div v-if="profile.bio" class="profile-bio">
        <p>{{ profile.bio }}</p>
      </div>

      <!-- Estatísticas Quantitativas de Leitura (se autorizadas) -->
      <div
        v-if="profile.reading_stats"
        class="profile-stats-grid"
        aria-label="Estatísticas de leitura"
      >
        <div class="stat-card">
          <span class="stat-icon-wrap">
            <Icon name="book-open" :size="20" />
          </span>
          <div class="stat-content">
            <span class="stat-value">{{ profile.reading_stats.total_books }}</span>
            <span class="stat-label muted">Obras no acervo</span>
          </div>
        </div>

        <div class="stat-card">
          <span class="stat-icon-wrap">
            <Icon name="layout-dashboard" :size="20" />
          </span>
          <div class="stat-content">
            <span class="stat-value">{{ profile.reading_stats.total_studies }}</span>
            <span class="stat-label muted">Estudos realizados</span>
          </div>
        </div>

        <div class="stat-card">
          <span class="stat-icon-wrap flame-icon">
            <Icon name="flame" :size="20" />
          </span>
          <div class="stat-content">
            <span class="stat-value">{{ profile.reading_stats.current_streak_days }}</span>
            <span class="stat-label muted">Dias consecutivos</span>
          </div>
        </div>
      </div>
    </template>
  </article>
</template>

<style scoped>
.profile-card {
  max-width: 44rem;
  margin: 0 auto;
  padding: calc(var(--space-unit) * 1.5);
  border: var(--border-width) solid var(--color-border);
  background-color: var(--color-surface);
  border-radius: var(--radius-surface, 12px);
  box-shadow: var(--shadow-surface, 0 4px 16px rgba(0, 0, 0, 0.05));
}

.profile-header {
  display: flex;
  align-items: center;
  gap: 1.25rem;
  margin-bottom: 1.25rem;
}

.profile-avatar-container {
  width: 88px;
  height: 88px;
  border-radius: 50%;
  overflow: hidden;
  border: 3px solid var(--color-accent);
  background: var(--color-surface-soft, rgba(0, 0, 0, 0.04));
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.profile-avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.profile-avatar-initials {
  font-size: 2rem;
  font-weight: 700;
  color: var(--color-accent);
  letter-spacing: 0.04em;
  user-select: none;
}

.profile-identity {
  flex: 1;
  min-width: 0;
}

.profile-title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.profile-name {
  margin: 0;
  font-size: var(--text-h2, 1.5rem);
  line-height: 1.25;
  color: var(--color-text);
  word-break: break-word;
}

.edit-profile-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  min-height: 44px;
  padding: 0.4rem 0.85rem;
  font-size: 0.875rem;
  text-decoration: none;
}

.profile-handle {
  margin: 0.2rem 0 0.4rem;
  font-size: 1rem;
  font-weight: 500;
}

.profile-meta-row {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.8125rem;
}

.restricted-card {
  margin-top: 1rem;
  padding: 1.25rem;
  border-radius: var(--radius-control, 8px);
  background-color: var(--color-surface-soft, rgba(0, 0, 0, 0.03));
  border: 1px dashed var(--color-border);
  text-align: center;
}

.restricted-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--color-accent);
  font-size: 1rem;
  margin-bottom: 0.5rem;
}

.restricted-desc {
  margin: 0;
  font-size: 0.875rem;
  line-height: 1.5;
}

.profile-bio {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid var(--color-border);
  font-size: 0.9375rem;
  line-height: 1.6;
  color: var(--color-text);
  word-break: break-word;
  white-space: pre-wrap;
}

.profile-stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
  gap: 0.75rem;
  margin-top: 1.25rem;
  padding-top: 1.25rem;
  border-top: 1px solid var(--color-border);
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  border-radius: var(--radius-control, 8px);
  background-color: var(--color-surface-soft, rgba(0, 0, 0, 0.03));
  border: 1px solid var(--color-border);
}

.stat-icon-wrap {
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-accent);
}

.flame-icon {
  color: #ea580c;
}

.stat-content {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 1.25rem;
  font-weight: 700;
  line-height: 1.2;
  color: var(--color-text);
}

.stat-label {
  font-size: 0.75rem;
  line-height: 1.2;
}

@media (max-width: 600px) {
  .profile-header {
    flex-direction: column;
    text-align: center;
  }
  .profile-title-row {
    justify-content: center;
  }
  .profile-meta-row {
    justify-content: center;
  }
}
</style>
