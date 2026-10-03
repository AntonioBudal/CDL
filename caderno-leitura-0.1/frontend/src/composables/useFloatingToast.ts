import { ref, readonly, onBeforeUnmount, getCurrentInstance, type Ref } from 'vue'
import type { FloatingToastPayload } from '../types/toast.ts'

export interface UseFloatingToastReturn {
  visible: Readonly<Ref<boolean>>
  message: Readonly<Ref<string>>
  colorDot: Readonly<Ref<string | null>>
  showToast: (payload: FloatingToastPayload) => void
  hideToast: () => void
}

const DEFAULT_TOAST_DURATION = 1800 // 1.8 segundos

export function useFloatingToast(defaultDuration: number = DEFAULT_TOAST_DURATION): UseFloatingToastReturn {
  const visible = ref(false)
  const message = ref('')
  const colorDot = ref<string | null>(null)
  let timerId: ReturnType<typeof setTimeout> | null = null

  function hideToast() {
    if (timerId !== null) {
      clearTimeout(timerId)
      timerId = null
    }
    visible.value = false
  }

  function showToast(payload: FloatingToastPayload) {
    // Cancelamento atômico de timer anterior
    if (timerId !== null) {
      clearTimeout(timerId)
      timerId = null
    }

    message.value = payload.message
    colorDot.value = payload.colorDot ?? null
    visible.value = true

    const duration = payload.duration ?? defaultDuration
    timerId = setTimeout(() => {
      visible.value = false
      timerId = null
    }, duration)
  }

  if (getCurrentInstance()) {
    onBeforeUnmount(() => {
      hideToast()
    })
  }

  return {
    visible: readonly(visible),
    message: readonly(message),
    colorDot: readonly(colorDot),
    showToast,
    hideToast,
  }
}
