// F0.12.07: convites pendentes de círculos de leitura (contador do menu "Mais"; sem sininho no 0.12).
import { computed, ref } from 'vue'
import { api } from '../services/api.ts'

const pending = ref(0)

export function useCircleInvites() {
  const count = computed(() => pending.value)

  async function refresh(signal?: AbortSignal): Promise<number> {
    try {
      pending.value = (await api.getCircleInviteCount(signal)).count
    } catch {
      // Sem contador quando a API não responde; a página Círculos mostra os convites.
    }
    return pending.value
  }

  function setCount(value: number) {
    pending.value = Math.max(0, value)
  }

  return { count, refresh, setCount }
}
