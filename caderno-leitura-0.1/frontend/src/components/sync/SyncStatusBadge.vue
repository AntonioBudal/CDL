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
    class="sync-status-badge"
    :class="[`status-${status}`, { 'is-offline': !isOnline }]"
    :aria-label="`Status de sincronização: ${label}. Clique para sincronizar agora.`"
    :title="`Status: ${label}. Clique para sincronizar agora.`"
    :disabled="isSyncing || !isOnline"
    @click="handleManualSync"
  >
    <span class="icon-container" aria-hidden="true">
      <RefreshCw v-if="status === 'syncing'" :size="13" class="spin-icon" />
      <CloudOff v-else-if="!isOnline || status === 'offline'" :size="13" />
      <AlertTriangle v-else-if="status === 'conflict'" :size="13" />
      <AlertCircle v-else-if="status === 'error'" :size="13" />
      <Check v-else :size="13" />
    </span>
    <span class="badge-text">{{ label }}</span>
  </button>
</template>

<style scoped>
.sync-status-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.25rem 0.55rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 500;
  border: 1px solid var(--color-border, #e5e7eb);
  background: var(--color-bg, #ffffff);
  color: var(--color-text-muted, #6b7280);
  cursor: pointer;
  transition: all 0.15s ease-in-out;
  line-height: 1;
}

.sync-status-badge:hover:not(:disabled) {
  border-color: var(--color-border-hover, #d1d5db);
  background: var(--color-bg-hover, #f9fafb);
  color: var(--color-text, #111827);
}

.sync-status-badge:disabled {
  cursor: default;
  opacity: 0.85;
}

.status-idle {
  color: var(--color-text-muted, #6b7280);
}

.status-syncing {
  color: var(--color-primary, #2563eb);
  border-color: rgba(37, 99, 235, 0.25);
  background: rgba(37, 99, 235, 0.05);
}

.status-offline,
.is-offline {
  color: var(--color-warning-text, #b45309);
  border-color: rgba(245, 158, 11, 0.3);
  background: rgba(245, 158, 11, 0.08);
}

.status-conflict,
.status-error {
  color: var(--color-danger, #dc2626);
  border-color: rgba(220, 38, 38, 0.3);
  background: rgba(220, 38, 38, 0.08);
}

.icon-container {
  display: inline-flex;
  align-items: center;
  justify-content: center;
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

.badge-text {
  white-space: nowrap;
}
</style>
