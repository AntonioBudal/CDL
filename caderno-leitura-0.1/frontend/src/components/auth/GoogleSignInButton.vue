<script setup lang="ts">
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import { Loader2 } from 'lucide-vue-next'
import { useAuthStore } from '../../stores/auth.ts'
import { useGoogleIdentity } from '../../composables/useGoogleIdentity.ts'

const props = withDefaults(
  defineProps<{
    text?: 'signin_with' | 'signup_with' | 'continue_with'
    shape?: 'rectangular' | 'pill' | 'circle' | 'square'
    width?: number
  }>(),
  {
    text: 'signin_with',
    shape: 'rectangular',
  },
)

const emit = defineEmits<{
  (e: 'success', credential: string): void
  (e: 'error', message: string): void
}>()

const authStore = useAuthStore()
const { isGsiLoading, gsiLoadError, loadGsiScript, initializeAndRenderButton } = useGoogleIdentity()

const buttonContainer = ref<HTMLElement | null>(null)
const isRendering = ref<boolean>(false)

const hasGsiClient = computed(() => authStore.googleAuthEnabled.value && !!authStore.googleClientId.value)

const buttonLabel = computed(() => {
  if (props.text === 'signup_with') return 'Cadastrar com o Google'
  if (props.text === 'continue_with') return 'Continuar com o Google'
  return 'Entrar com o Google'
})

async function renderButton() {
  if (!buttonContainer.value || !hasGsiClient.value) return
  isRendering.value = true

  const success = await loadGsiScript()
  if (success && buttonContainer.value) {
    await nextTick()
    const options: Partial<google.accounts.id.GsiButtonConfiguration> = {
      text: props.text,
      shape: props.shape,
      theme: 'outline',
      size: 'large',
    }
    if (props.width) {
      options.width = props.width
    }
    initializeAndRenderButton(
      buttonContainer.value,
      (credential: string) => emit('success', credential),
      options,
    )
  }
  isRendering.value = false
}

onMounted(() => {
  if (hasGsiClient.value) {
    renderButton()
  }
})

watch(
  () => hasGsiClient.value,
  (enabled) => {
    if (enabled) {
      renderButton()
    }
  },
)
</script>

<template>
  <div class="google-signin-wrapper">
    <div v-show="hasGsiClient && !gsiLoadError" ref="buttonContainer" class="google-button-slot" />

    <div v-if="hasGsiClient && (isGsiLoading || isRendering)" class="google-loading-state">
      <Loader2 class="loading-icon animate-spin" :size="18" />
      <span>Carregando Google...</span>
    </div>

    <div v-else-if="!hasGsiClient || gsiLoadError" class="google-fallback-wrap">
      <a href="/api/auth/google/login" class="google-redirect-btn" :title="buttonLabel">
        <svg class="google-icon" viewBox="0 0 24 24" width="18" height="18" aria-hidden="true">
          <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
          <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
          <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z" />
          <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z" />
        </svg>
        <span>{{ buttonLabel }}</span>
      </a>
    </div>
  </div>
</template>

<style scoped>
.google-signin-wrapper {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  margin: 0.5rem 0;
  min-height: 44px;
}

.google-button-slot {
  width: 100%;
  display: flex;
  justify-content: center;
}

.google-loading-state,
.google-error-state {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  font-size: 0.85rem;
  padding: 0.5rem;
  width: 100%;
  border-radius: 6px;
}

.google-loading-state {
  color: var(--color-text-muted, #666);
}

.google-error-state {
  color: var(--color-accent-danger, #b91c1c);
  background-color: var(--color-bg-subtle, #fef2f2);
  border: 1px solid var(--color-border-subtle, #fee2e2);
}

.loading-icon {
  animation: spin 1s linear infinite;
}

.google-fallback-wrap {
  width: 100%;
  display: flex;
  justify-content: center;
}

.google-redirect-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  width: 100%;
  min-height: 44px;
  padding: 0.65rem 1rem;
  border-radius: 6px;
  background-color: var(--color-bg-surface, #ffffff);
  border: 1px solid var(--color-border-subtle, #dadce0);
  color: var(--color-text-primary, #3c4043);
  font-size: 0.9rem;
  font-weight: 500;
  text-decoration: none;
  cursor: pointer;
  transition: background-color 0.2s, box-shadow 0.2s;
}

.google-redirect-btn:hover {
  background-color: var(--color-bg-hover, #f8f9fa);
  box-shadow: 0 1px 3px rgba(60, 64, 67, 0.15);
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
