import { computed, ref } from 'vue'
import { api } from '../services/api.ts'

const pendingCount = ref<number>(0)
const isCountLoading = ref<boolean>(false)

export function useInboxCount() {
  const count = computed(() => pendingCount.value)
  const loading = computed(() => isCountLoading.value)

  async function refreshCount(signal?: AbortSignal): Promise<number> {
    isCountLoading.value = true
    try {
      const data = await api.getInboxCount(signal)
      pendingCount.value = data.count
      return data.count
    } catch {
      return pendingCount.value
    } finally {
      isCountLoading.value = false
    }
  }

  function increment(amount = 1): void {
    pendingCount.value = Math.max(0, pendingCount.value + amount)
  }

  function decrement(amount = 1): void {
    pendingCount.value = Math.max(0, pendingCount.value - amount)
  }

  function setCount(newCount: number): void {
    pendingCount.value = Math.max(0, newCount)
  }

  return {
    count,
    pendingCount: count,
    loading,
    refreshCount,
    increment,
    decrement,
    setCount,
  }
}
