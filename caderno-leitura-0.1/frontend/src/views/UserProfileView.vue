<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import type { UserProfilePublic } from '../types.ts'
import { useProfile } from '../composables/useProfile.ts'
import { useAuthStore } from '../stores/auth.ts'
import UserProfileCard from '../components/profile/UserProfileCard.vue'
import Icon from '../components/ui/Icon.vue'

const route = useRoute()
const auth = useAuthStore()
const profileService = useProfile()

const username = computed(() => {
  const param = route.params.username
  if (Array.isArray(param)) return param[0] || ''
  return String(param || '')
})

const publicProfile = ref<UserProfilePublic | null>(null)
const isLoading = ref<boolean>(true)
const errorMessage = ref<string | null>(null)

const isOwner = computed(() => {
  if (!auth.user.value || !publicProfile.value) return false
  return auth.user.value.username.toLowerCase() === publicProfile.value.username.toLowerCase()
})

async function loadProfile() {
  if (!username.value) {
    errorMessage.value = 'Nome de usuário inválido.'
    isLoading.value = false
    return
  }

  isLoading.value = true
  errorMessage.value = null

  try {
    const data = await profileService.fetchPublicProfile(username.value)
    publicProfile.value = data
  } catch (err: unknown) {
    if (err instanceof Error && err.message.includes('404')) {
      errorMessage.value = 'Leitor não encontrado. O perfil solicitado não existe no sistema.'
    } else {
      errorMessage.value = err instanceof Error ? err.message : 'Falha ao carregar perfil do leitor.'
    }
    publicProfile.value = null
  } finally {
    isLoading.value = false
  }
}

watch(
  () => route.params.username,
  () => {
    void loadProfile()
  }
)

onMounted(() => {
  void loadProfile()
})
</script>

<template>
  <section class="user-profile-view wrap">
    <div class="profile-view-content">
      <!-- Estado de Carregamento -->
      <div v-if="isLoading" class="loading-state panel" role="status" aria-live="polite">
        <Icon name="search" :size="24" class="spinning-icon" />
        <p>Carregando perfil do leitor…</p>
      </div>

      <!-- Estado de Erro / Não Encontrado -->
      <div v-else-if="errorMessage || !publicProfile" class="error-state panel" role="alert">
        <Icon name="alert-triangle" :size="32" class="error-icon" />
        <h2>Perfil indisponível</h2>
        <p class="muted">{{ errorMessage || 'Não foi possível encontrar as informações deste usuário.' }}</p>
        <div class="actions">
          <RouterLink to="/" class="button primary">
            Voltar ao Início
          </RouterLink>
        </div>
      </div>

      <!-- Perfil Carregado com Sucesso -->
      <div v-else class="loaded-profile">
        <nav class="breadcrumb-nav" aria-label="Navegação de retorno">
          <RouterLink to="/" class="back-link">
            <Icon name="arrow-right" :size="14" class="back-icon" />
            <span>Voltar ao acervo</span>
          </RouterLink>
        </nav>

        <UserProfileCard
          :profile="publicProfile"
          :is-owner="isOwner"
          :show-edit-button="true"
        />
      </div>
    </div>
  </section>
</template>

<style scoped>
.user-profile-view {
  padding-top: calc(var(--space-unit) * 1.5);
  padding-bottom: calc(var(--space-unit) * 3);
}

.profile-view-content {
  max-width: 48rem;
  margin: 0 auto;
}

.breadcrumb-nav {
  margin-bottom: 1rem;
}

.back-link {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.875rem;
  color: var(--color-muted);
  text-decoration: none;
  transition: color 0.15s ease;
  min-height: 44px;
}

.back-link:hover {
  color: var(--color-accent);
}

.back-icon {
  transform: rotate(180deg);
}

.loading-state,
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: calc(var(--space-unit) * 3);
  margin-top: 2rem;
  border-radius: var(--radius-surface, 12px);
  border: var(--border-width) solid var(--color-border);
}

.error-icon {
  color: var(--color-accent);
  margin-bottom: 0.75rem;
}

.error-state h2 {
  margin-top: 0;
  margin-bottom: 0.5rem;
}

.error-state .actions {
  margin-top: 1.5rem;
}

.spinning-icon {
  animation: spin 1.2s linear infinite;
  color: var(--color-accent);
  margin-bottom: 0.5rem;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>
