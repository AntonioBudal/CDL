<script setup lang="ts">
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import { AlertCircle, Loader2 } from 'lucide-vue-next'
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

const isEnabled = computed(() => authStore.googleAuthEnabled.value && !!authStore.googleClientId.value)

async function renderButton() {
  if (!buttonContainer.value || !isEnabled.value) return
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
  if (isEnabled.value) {
    renderButton()
  }
})

watch(
  () => isEnabled.value,
  (enabled) => {
    if (enabled) {
      renderButton()
    }
  },
)
</script>

<template>
  <div v-if="isEnabled" class="google-signin-wrapper">
    <div ref="buttonContainer" class="google-button-slot" />

    <div v-if="isGsiLoading || isRendering" class="google-loading-state">
      <Loader2 class="loading-icon animate-spin" :size="18" />
      <span>Carregando Google...</span>
    </div>

    <div v-else-if="gsiLoadError" class="google-error-state">
      <AlertCircle class="error-icon" :size="16" />
      <span>Não foi possível carregar o serviço do Google. Use login local.</span>
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

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>
