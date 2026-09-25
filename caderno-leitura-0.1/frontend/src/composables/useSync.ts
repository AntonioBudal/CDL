import { computed, reactive } from 'vue'
import { syncApi } from '../api/sync.ts'
import type { SyncChangesResponse, SyncStatus } from '../types.ts'

const STORAGE_KEY_LAST_SYNC = 'caderno_last_sync_time'

// Estado compartilhado em nível de módulo (singleton reativo)
const state = reactive({
  status: 'idle' as SyncStatus,
  isOnline: typeof navigator !== 'undefined' ? navigator.onLine : true,
  lastSyncTime: typeof localStorage !== 'undefined' ? localStorage.getItem(STORAGE_KEY_LAST_SYNC) : null,
  lastError: null as string | null,
})

let debounceTimer: ReturnType<typeof setTimeout> | null = null
let activeListenersCount = 0

export function useSync() {
  const isSyncing = computed(() => state.status === 'syncing')
  const status = computed(() => state.status)
  const isOnline = computed(() => state.isOnline)
  const lastSyncTime = computed(() => state.lastSyncTime)
  const lastError = computed(() => state.lastError)

  async function performSync(forceFull = false): Promise<SyncChangesResponse | null> {
    if (!state.isOnline) {
      state.status = 'offline'
      return null
    }

    state.status = 'syncing'
    state.lastError = null

    try {
      const since = forceFull ? null : state.lastSyncTime
      const response = await syncApi.fetchChanges(since)

      state.lastSyncTime = response.server_time
      if (typeof localStorage !== 'undefined') {
        localStorage.setItem(STORAGE_KEY_LAST_SYNC, response.server_time)
      }

      state.status = 'idle'
      state.isOnline = true

      // Dispara evento global para que views e stores possam atualizar seus caches se desejado
      if (typeof window !== 'undefined') {
        window.dispatchEvent(
          new CustomEvent<SyncChangesResponse>('caderno:sync-applied', { detail: response })
        )
      }

      return response
    } catch (err: any) {
      if (typeof navigator !== 'undefined' && !navigator.onLine) {
        state.isOnline = false
        state.status = 'offline'
      } else if (err?.status === 0) {
        state.isOnline = false
        state.status = 'offline'
      } else {
        state.status = 'error'
      }
      state.lastError = err instanceof Error ? err.message : 'Falha na sincronização'
      return null
    }
  }

  function syncNow(forceFull = false, debounceMs = 500) {
    if (debounceTimer) {
      clearTimeout(debounceTimer)
      debounceTimer = null
    }

    if (debounceMs <= 0) {
      return performSync(forceFull)
    }

    debounceTimer = setTimeout(() => {
      debounceTimer = null
      performSync(forceFull)
    }, debounceMs)
  }

  function handleOnline() {
    state.isOnline = true
    syncNow(false, 300)
  }

  function handleOffline() {
    state.isOnline = false
    state.status = 'offline'
  }

  function handleVisibilityChange() {
    if (typeof document !== 'undefined' && document.visibilityState === 'visible') {
      syncNow(false, 500)
    }
  }

  function handleFocus() {
    syncNow(false, 800)
  }

  function setStatus(newStatus: SyncStatus) {
    state.status = newStatus
  }

  function setOnline(online: boolean) {
    state.isOnline = online
    if (!online) {
      state.status = 'offline'
    } else if (state.status === 'offline') {
      state.status = 'idle'
    }
  }

  function resetLastSync() {
    state.lastSyncTime = null
    if (typeof localStorage !== 'undefined') {
      localStorage.removeItem(STORAGE_KEY_LAST_SYNC)
    }
  }

  function attachListeners() {
    if (typeof window === 'undefined') return
    if (activeListenersCount === 0) {
      window.addEventListener('online', handleOnline)
      window.addEventListener('offline', handleOffline)
      document.addEventListener('visibilitychange', handleVisibilityChange)
      window.addEventListener('focus', handleFocus)
    }
    activeListenersCount++
  }

  function detachListeners() {
    if (typeof window === 'undefined') return
    activeListenersCount = Math.max(0, activeListenersCount - 1)
    if (activeListenersCount === 0) {
      window.removeEventListener('online', handleOnline)
      window.removeEventListener('offline', handleOffline)
      document.removeEventListener('visibilitychange', handleVisibilityChange)
      window.removeEventListener('focus', handleFocus)
    }
  }

  return {
    status,
    isOnline,
    isSyncing,
    lastSyncTime,
    lastError,
    syncNow,
    performSync,
    setStatus,
    setOnline,
    resetLastSync,
    attachListeners,
    detachListeners,
  }
}
