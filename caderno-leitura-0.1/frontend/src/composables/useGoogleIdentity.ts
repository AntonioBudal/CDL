import { ref } from 'vue'
import { useAuthStore } from '../stores/auth.ts'

const isGsiLoaded = ref<boolean>(false)
const isGsiLoading = ref<boolean>(false)
const gsiLoadError = ref<boolean>(false)

export function useGoogleIdentity() {
  const authStore = useAuthStore()

  function loadGsiScript(): Promise<boolean> {
    if (typeof window === 'undefined') return Promise.resolve(false)

    // Se a feature está desativada no servidor, não tenta carregar nenhum script externo
    if (!authStore.googleAuthEnabled.value || !authStore.googleClientId.value) {
      return Promise.resolve(false)
    }

    if (window.google?.accounts?.id) {
      isGsiLoaded.value = true
      return Promise.resolve(true)
    }

    if (isGsiLoaded.value) return Promise.resolve(true)

    if (isGsiLoading.value) {
      return new Promise((resolve) => {
        const interval = setInterval(() => {
          if (window.google?.accounts?.id) {
            clearInterval(interval)
            isGsiLoaded.value = true
            resolve(true)
          } else if (gsiLoadError.value) {
            clearInterval(interval)
            resolve(false)
          }
        }, 50)
      })
    }

    isGsiLoading.value = true
    gsiLoadError.value = false

    return new Promise((resolve) => {
      const script = document.createElement('script')
      script.src = 'https://accounts.google.com/gsi/client'
      script.async = true
      script.defer = true
      script.onload = () => {
        isGsiLoaded.value = true
        isGsiLoading.value = false
        resolve(true)
      }
      script.onerror = () => {
        gsiLoadError.value = true
        isGsiLoading.value = false
        // Degradação graciosa: erro de rede não impede uso da aplicação
        resolve(false)
      }
      document.head.appendChild(script)
    })
  }

  function initializeAndRenderButton(
    container: HTMLElement,
    onSuccess: (credential: string) => void,
    options: Partial<google.accounts.id.GsiButtonConfiguration> = {},
  ): boolean {
    if (typeof window === 'undefined' || !window.google?.accounts?.id) {
      return false
    }

    const clientId = authStore.googleClientId.value
    if (!clientId) return false

    try {
      window.google.accounts.id.initialize({
        client_id: clientId,
        callback: (response: google.accounts.id.CredentialResponse) => {
          if (response.credential) {
            onSuccess(response.credential)
          }
        },
      })

      const config: google.accounts.id.GsiButtonConfiguration = {
        type: 'standard',
        theme: 'outline',
        size: 'large',
        shape: 'rectangular',
        text: 'signin_with',
        logo_alignment: 'left',
        locale: 'pt-BR',
        ...options,
      }
      window.google.accounts.id.renderButton(container, config)
      return true
    } catch {
      return false
    }
  }

  return {
    isGsiLoaded,
    isGsiLoading,
    gsiLoadError,
    loadGsiScript,
    initializeAndRenderButton,
  }
}
