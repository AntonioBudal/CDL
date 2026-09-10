<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { fetchHealth, type HealthResponse } from '../services/api'

const state = ref<'loading' | 'success' | 'error'>('loading')
const health = ref<HealthResponse | null>(null)
const detail = ref('')
let activeRequest: AbortController | null = null
let disposed = false

const title = computed(() => ({
  loading: 'Verificando conexão…',
  success: 'Backend conectado',
  error: 'Backend indisponível',
})[state.value])

async function checkConnection() {
  if (activeRequest || disposed) return

  state.value = 'loading'
  health.value = null
  detail.value = ''
  const controller = new AbortController()
  activeRequest = controller
  const timeout = window.setTimeout(() => controller.abort(), 8000)

  try {
    const response = await fetchHealth(controller.signal)
    if (disposed) return
    health.value = response
    state.value = 'success'
  } catch (error: unknown) {
    if (disposed) return
    state.value = 'error'
    detail.value = controller.signal.aborted
      ? 'O servidor não respondeu em até 8 segundos.'
      : error instanceof Error
        ? error.message
        : 'Não foi possível verificar a conexão.'
  } finally {
    window.clearTimeout(timeout)
    activeRequest = null
  }
}

onMounted(() => { void checkConnection() })
onBeforeUnmount(() => {
  disposed = true
  activeRequest?.abort()
})
</script>

<template>
  <section class="connection-page">
    <header class="page-header">
      <p class="edition">Diagnóstico</p>
      <h1>Conexão local</h1>
      <p class="intro">Verificação da comunicação entre a interface e o servidor local.</p>
    </header>

    <section class="connection-panel" aria-labelledby="connection-title" :aria-busy="state === 'loading'">
      <div class="status" :data-state="state" role="status" aria-live="polite" aria-atomic="true">
        <p class="eyebrow">Conexão local</p>
        <h2 id="connection-title">{{ title }}</h2>
        <p v-if="state === 'loading'">Consultando o servidor deste PC.</p>
        <p v-else-if="state === 'success'">A interface recebeu uma resposta válida do FastAPI.</p>
        <template v-else>
          <p>Confira se o backend está rodando na porta 8000 e tente novamente.</p>
          <p class="error-detail">{{ detail }}</p>
        </template>
      </div>

      <dl class="request-info">
        <div>
          <dt>Requisição</dt>
          <dd><code>GET /api/health</code></dd>
        </div>
        <div v-if="health">
          <dt>Versão da API</dt>
          <dd>{{ health.version }}</dd>
        </div>
      </dl>

      <div v-if="health" class="response">
        <p class="response-label">Resposta do servidor</p>
        <pre>{{ JSON.stringify(health, null, 2) }}</pre>
      </div>

      <button type="button" :disabled="state === 'loading'" @click="checkConnection">
        {{ state === 'loading' ? 'Verificando…' : 'Verificar novamente' }}
      </button>
    </section>
  </section>
</template>
