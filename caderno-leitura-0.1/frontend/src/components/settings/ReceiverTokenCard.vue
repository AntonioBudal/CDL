<script setup lang="ts">
/**
 * F0.11.09 (spec 111): "Receber destaques". Token de recepção para o Readest (formato Readwise) e instruções para
 * o KOReader (arquivo JSON). O token aparece uma vez só; o servidor guarda apenas o hash.
 */
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { api } from '../../services/api'
import type { ReceiverTokenStatus } from '../../types'

const status = ref<ReceiverTokenStatus | null>(null)
const freshToken = ref('')
const busy = ref(false)
const message = ref('')
const error = ref('')

const receiverUrl = computed(() => `${window.location.origin}/api/receptor/readwise/v2`)

function formatDate(value: string | null | undefined): string {
  if (!value) return 'nunca'
  return new Date(value).toLocaleString('pt-BR', { dateStyle: 'short', timeStyle: 'short' })
}

async function load() {
  try {
    status.value = await api.getReceiverToken()
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Não foi possível ler o token de recepção.'
  }
}

async function issue() {
  busy.value = true
  error.value = ''
  message.value = ''
  try {
    const issued = await api.issueReceiverToken()
    freshToken.value = issued.token
    status.value = issued.status
    message.value = 'Token gerado. Copie agora: ele não aparece de novo.'
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Não foi possível gerar o token.'
  } finally {
    busy.value = false
  }
}

async function revoke() {
  busy.value = true
  error.value = ''
  try {
    await api.revokeReceiverToken()
    freshToken.value = ''
    status.value = { active: false }
    message.value = 'Token revogado. O Readest não consegue mais enviar destaques com ele.'
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Não foi possível revogar o token.'
  } finally {
    busy.value = false
  }
}

async function copy(text: string, what: string) {
  try {
    await navigator.clipboard.writeText(text)
    message.value = `${what} copiado.`
  } catch {
    message.value = `Não consegui copiar; selecione ${what.toLowerCase()} e copie à mão.`
  }
}

onMounted(load)
</script>

<template>
  <section class="receiver-card" aria-labelledby="receiver-heading">
    <h3 id="receiver-heading" class="receiver-title">Receber destaques</h3>
    <p class="receiver-muted">
      Os destaques recebidos entram na caixa de entrada, no livro de mesmo título (ou num livro novo).
    </p>

    <h4 class="receiver-subtitle">Readest (envio automático)</h4>
    <ol class="receiver-steps">
      <li>Gere um token aqui e copie a URL e o token.</li>
      <li>No Readest: Configurações → Sincronizar → Readwise → Avançado → URL personalizada; cole a URL e, como
        token, o token daqui.</li>
    </ol>

    <div class="receiver-field">
      <span class="receiver-label">URL para o Readest</span>
      <code class="receiver-code">{{ receiverUrl }}</code>
      <button type="button" class="quiet receiver-button" @click="copy(receiverUrl, 'URL')">Copiar URL</button>
    </div>

    <div v-if="freshToken" class="receiver-field receiver-fresh">
      <span class="receiver-label">Seu token (aparece só agora)</span>
      <code class="receiver-code">{{ freshToken }}</code>
      <button type="button" class="quiet receiver-button" @click="copy(freshToken, 'Token')">Copiar token</button>
    </div>
    <p v-else-if="status?.active" class="receiver-muted">
      Token ativo: <code>{{ status.hint }}…</code> · criado em {{ formatDate(status.created_at) }} · último uso:
      {{ formatDate(status.last_used_at) }}. Gerar outro faz o atual parar de valer na hora.
    </p>
    <p v-else-if="status" class="receiver-muted">Nenhum token ativo.</p>

    <div class="receiver-actions">
      <button type="button" class="quiet receiver-button" :disabled="busy" @click="issue">
        {{ status?.active ? 'Gerar outro' : 'Gerar token' }}
      </button>
      <button v-if="status?.active" type="button" class="quiet receiver-button" :disabled="busy" @click="revoke">
        Revogar
      </button>
    </div>
    <p class="receiver-muted">
      O celular precisa alcançar o Leitorum (mesma rede ou Tailscale). A versão web do Readest não funciona: o
      navegador bloqueia o envio para outro endereço.
    </p>

    <h4 class="receiver-subtitle">KOReader (arquivo)</h4>
    <p class="receiver-muted">
      No KOReader: menu de anotações → Exportar destaques → escolha <strong>JSON</strong>. Depois envie o arquivo em
      <RouterLink to="/inbox/importar-leitor" class="receiver-link">Importar de leitor digital</RouterLink>.
    </p>

    <p v-if="error" class="receiver-error" role="alert">{{ error }}</p>
    <p class="receiver-muted" role="status" aria-live="polite">{{ message }}</p>
  </section>
</template>

<style scoped>
.receiver-card {
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: 14px 16px;
  margin-top: 20px;
  background: var(--color-surface);
  color: var(--color-text);
  min-width: 0;
}
.receiver-title {
  margin: 0 0 4px;
  font-size: 1.1rem;
}
.receiver-subtitle {
  margin: 14px 0 4px;
  font-size: 1rem;
}
.receiver-steps {
  margin: 4px 0 8px;
  padding-left: 1.2rem;
}
.receiver-muted {
  color: var(--color-muted);
  font-size: 0.92rem;
  margin: 6px 0;
}
.receiver-error {
  color: var(--color-danger-text);
}
.receiver-field {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px 10px;
  margin: 8px 0;
  min-width: 0;
}
.receiver-label {
  flex-basis: 100%;
  font-size: 0.85rem;
  color: var(--color-muted);
}
.receiver-code {
  overflow-wrap: anywhere;
  word-break: break-all;
  min-width: 0;
  max-width: 100%;
}
.receiver-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin: 8px 0;
}
.receiver-button {
  min-height: 44px;
  max-width: 100%;
  white-space: normal;
}
.receiver-link {
  color: var(--color-link);
}
</style>
