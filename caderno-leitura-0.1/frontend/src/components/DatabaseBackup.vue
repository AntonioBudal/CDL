<script setup lang="ts">
import { onBeforeUnmount, ref } from 'vue'
import { downloadBackupBundle } from '../services/api.ts'

const emit = defineEmits<{
  (e: 'openRestore'): void
}>()

const busy = ref(false)
const status = ref('')
const error = ref('')
let controller: AbortController | null = null

function cancelBackup() {
  controller?.abort()
}

onBeforeUnmount(cancelBackup)

async function downloadBundle() {
  if (busy.value) return

  busy.value = true
  error.value = ''
  status.value = 'Preparando pacote completo de backup com capas e manifesto…'

  const request = new AbortController()
  controller = request

  try {
    const result = await downloadBackupBundle(request.signal)
    status.value = `Download concluído: ${result.filename}. Confira a pasta de downloads.`
  } catch (cause) {
    if (!request.signal.aborted) {
      status.value = ''
      error.value =
        cause instanceof Error ? cause.message : 'Não foi possível baixar o pacote de backup.'
    }
  } finally {
    if (request.signal.aborted) {
      status.value = 'Download cancelado.'
    }
    controller = null
    busy.value = false
  }
}

async function downloadBackup() {
  if (busy.value) return

  busy.value = true
  error.value = ''
  status.value = 'Preparando uma cópia do banco…'

  const request = new AbortController()
  controller = request

  try {
    const response = await fetch('/api/backup', {
      headers: { Accept: 'application/octet-stream' },
      cache: 'no-store',
      signal: request.signal,
    })

    if (!response.ok) {
      const data: unknown = await response.json().catch(() => null)
      const detail =
        typeof data === 'object' &&
        data !== null &&
        'detail' in data &&
        typeof data.detail === 'string'
          ? data.detail
          : `Não foi possível gerar o backup (HTTP ${response.status}).`

      throw new Error(detail)
    }

    status.value = 'Recebendo o arquivo…'

    const file = await response.blob()
    const signature = await file.slice(0, 16).text()

    if (signature !== 'SQLite format 3\0') {
      throw new Error(
        'A resposta recebida não é um banco SQLite. Verifique o servidor.',
      )
    }

    if (request.signal.aborted) return

    const disposition = response.headers.get('Content-Disposition') ?? ''
    const filename =
      disposition.match(/filename="(caderno-[0-9TZ-]+\.db)"/i)?.[1] ??
      `caderno-${new Date().toISOString().replace(/[:.]/g, '-')}.db`

    const url = URL.createObjectURL(file)
    const link = document.createElement('a')

    link.href = url
    link.download = filename
    link.hidden = true
    document.body.appendChild(link)

    try {
      link.click()
    } finally {
      link.remove()
      window.setTimeout(() => URL.revokeObjectURL(url), 60_000)
    }

    status.value =
      `Download solicitado: ${filename}. Confira os downloads deste dispositivo.`
  } catch (cause) {
    if (!request.signal.aborted) {
      status.value = ''
      error.value =
        cause instanceof TypeError
          ? 'Falha de conexão. Verifique se o servidor está aberto e se o dispositivo está conectado à rede.'
          : cause instanceof Error
            ? cause.message
            : 'Não foi possível baixar o backup. Tente novamente.'
    }
  } finally {
    if (request.signal.aborted) {
      status.value = 'Download cancelado.'
    }

    controller = null
    busy.value = false
  }
}
</script>

<template>
  <section class="panel backup-panel" aria-labelledby="backup-title">
    <h2 id="backup-title">Backup e Restauração do Acervo</h2>

    <p id="backup-description">
      Baixe uma cópia completa com seus livros, capítulos, estudos, anotações e capas físicas, ou restaure um backup salvo.
    </p>

    <p class="muted">
      As preferências de aparência ficam salvas separadamente em cada navegador.
    </p>

    <div class="actions wrap" style="gap: 0.75rem;">
      <button
        type="button"
        class="primary"
        :disabled="busy"
        :aria-busy="busy"
        aria-describedby="backup-description"
        @click="downloadBundle"
      >
        {{ busy ? 'Preparando pacote…' : 'Baixar pacote completo (.zip)' }}
      </button>

      <button
        type="button"
        class="secondary"
        :disabled="busy"
        @click="downloadBackup"
      >
        Baixar apenas banco (.db)
      </button>

      <button
        type="button"
        class="secondary"
        :disabled="busy"
        @click="emit('openRestore')"
      >
        Restaurar acervo…
      </button>

      <button
        v-if="busy"
        type="button"
        class="secondary"
        @click="cancelBackup"
      >
        Cancelar
      </button>
    </div>

    <p class="backup-status muted" role="status" aria-atomic="true">
      {{ status }}
    </p>

    <p v-if="error" class="notice error" role="alert">
      {{ error }}
    </p>

    <details class="backup-restore">
      <summary>Instruções de restauração e segurança</summary>

      <p>
        A restauração substitui o acervo atual pelo conteúdo do backup escolhido (arquivo <code>.zip</code> com capas ou <code>.db</code> avulso).
      </p>

      <p>
        <strong>Salvaguarda Automática:</strong> Antes de qualquer substituição de dados, o sistema gera automaticamente uma cópia prévia de segurança (<code>caderno-pre-restauracao-*.db</code>), permitindo reversão em caso de imprevistos.
      </p>
    </details>
  </section>
</template>

<style scoped>
.backup-panel {
  margin-top: calc(var(--space-unit) * 1.5);
}

.backup-status {
  min-height: 1.6em;
}

.backup-restore {
  border-top: var(--border-width) solid var(--color-border);
  padding-top: var(--space-unit);
}

.backup-restore summary {
  min-height: 2.75rem;
  padding-block: calc(var(--space-unit) * .5);
  cursor: pointer;
  font-weight: 650;
}

.backup-restore p {
  line-height: 1.7;
  overflow-wrap: anywhere;
}
</style>