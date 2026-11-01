<script setup lang="ts">
import { computed } from 'vue'
import { AlertCircle, AlertTriangle, Check, CloudOff, RefreshCw } from 'lucide-vue-next'
import { useSync } from '../../composables/useSync.ts'

const { status, isOnline, isSyncing, syncNow } = useSync()

const label = computed(() => {
  if (!isOnline.value || status.value === 'offline') {
    return 'Offline — dados retidos no dispositivo'
  }
  switch (status.value) {
    case 'syncing':
      return 'Sincronizando…'
    case 'conflict':
      return 'Conflito de concorrência'
    case 'error':
      return 'Falha na conexão'
    case 'idle':
    default:
      return 'Sincronizado'
  }
})

function handleManualSync() {
  if (!isSyncing.value && isOnline.value) {
    syncNow(false, 0)
  }
}
</script>

<template>
  <button
    type="button"
    class="sync-status-badge quiet"
    :class="[`status-${status}`, { 'is-offline': !isOnline }]"
    :aria-label="`Status de sincronização: ${label}. Clique para sincronizar agora.`"
    :title="`Status: ${label}. Clique para sincronizar agora.`"
    :disabled="isSyncing || !isOnline"
    @click="handleManualSync"
  >
    <span class="icon-container" aria-hidden="true">
      <RefreshCw v-if="status === 'syncing'" :size="15" class="spin-icon" />
      <CloudOff v-else-if="!isOnline || status === 'offline'" :size="15" />
      <AlertTriangle v-else-if="status === 'conflict'" :size="15" />
      <AlertCircle v-else-if="status === 'error'" :size="15" />
      <Check v-else :size="15" />
      <span class="status-dot" aria-hidden="true"></span>
    </span>
  </button>
</template>

<style scoped>
.sync-status-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 34px;
  height: 34px;
  min-width: 34px;
  padding: 0;
  border-radius: 9999px;
  border: 1px solid transparent;
  background: transparent;
  color: var(--color-muted);
  cursor: pointer;
  transition: background-color 150ms ease, color 150ms ease, border-color 150ms ease;
  line-height: 1;
}

.sync-status-badge:hover:not(:disabled) {
  background-color: var(--color-surface-hover);
  color: var(--color-text);
  border-color: var(--color-border);
}

.sync-status-badge:focus-visible {
  outline: var(--focus-width, 3px) solid var(--color-accent);
  outline-offset: 2px;
}

.sync-status-badge:disabled {
  cursor: default;
  opacity: 0.75;
}

/* O botão usa a variante .quiet (texto do tema); o estado aparece no ponto, com o rótulo em title e aria-label. */
.icon-container {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.status-dot {
  position: absolute;
  right: -3px;
  bottom: -3px;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--color-success);
  box-shadow: 0 0 0 2px var(--color-surface);
}

.status-syncing .status-dot {
  background: var(--color-link);
}

.status-offline .status-dot,
.is-offline .status-dot {
  background: var(--color-warning-marker, var(--color-warning));
}

.status-conflict .status-dot,
.status-error .status-dot {
  background: var(--color-error-marker);
}

.spin-icon {
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

/* Alvo de toque de 44 px, como os vizinhos do header. */
@media (pointer: coarse) {
  .sync-status-badge {
    min-width: 44px;
  }
}

@media (prefers-reduced-motion: reduce) {
  .sync-status-badge,
  .spin-icon {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
</style>
