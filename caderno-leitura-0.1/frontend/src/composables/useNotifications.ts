import { computed, ref } from 'vue'
import { notificationsApi } from '../api/notifications.ts'
import { friendsApi } from '../api/friends.ts'
import type { NotificationItem } from '../types/notifications.ts'

const notificationsList = ref<NotificationItem[]>([])
const unreadCount = ref<number>(0)
const totalCount = ref<number>(0)
const isLoading = ref<boolean>(false)
const isOpen = ref<boolean>(false)
const unreadFilter = ref<boolean>(false)
const notificationError = ref<string | null>(null)

let pollingTimer: ReturnType<typeof setInterval> | null = null
let isPollingActive = false

export function useNotifications() {
  const notifications = computed(() => notificationsList.value)
  const unread = computed(() => unreadCount.value)
  const total = computed(() => totalCount.value)
  const loading = computed(() => isLoading.value)
  const open = computed(() => isOpen.value)
  const filterUnread = computed(() => unreadFilter.value)
  const error = computed(() => notificationError.value)

  async function fetchUnreadCount(signal?: AbortSignal): Promise<number> {
    try {
      const data = await notificationsApi.getUnreadCount(signal)
      unreadCount.value = data.unread_count
      return data.unread_count
    } catch {
      return unreadCount.value
    }
  }

  async function fetchNotifications(signal?: AbortSignal): Promise<NotificationItem[]> {
    isLoading.value = true
    notificationError.value = null
    try {
      const data = await notificationsApi.getNotifications(
        {
          unread_only: unreadFilter.value,
          limit: 30,
        },
        signal,
      )
      notificationsList.value = data.items
      totalCount.value = data.total
      unreadCount.value = data.unread_count
      return data.items
    } catch (err: unknown) {
      if (err instanceof Error && err.name === 'AbortError') return notificationsList.value
      notificationError.value = err instanceof Error ? err.message : 'Falha ao carregar notificações.'
      return notificationsList.value
    } finally {
      isLoading.value = false
    }
  }

  async function markAsRead(notificationId: string): Promise<boolean> {
    try {
      await notificationsApi.markAsRead(notificationId)
      // Atualização otimista no estado local
      const found = notificationsList.value.find((n) => n.id === notificationId)
      if (found && !found.read_at) {
        found.read_at = new Date().toISOString()
        unreadCount.value = Math.max(0, unreadCount.value - 1)
      }
      return true
    } catch {
      return false
    }
  }

  async function markAllAsRead(): Promise<boolean> {
    try {
      await notificationsApi.markAllAsRead()
      const now = new Date().toISOString()
      notificationsList.value.forEach((n) => {
        if (!n.read_at) {
          n.read_at = now
        }
      })
      unreadCount.value = 0
      return true
    } catch {
      return false
    }
  }

  function setUnreadFilter(value: boolean) {
    unreadFilter.value = value
    void fetchNotifications()
  }

  function toggleDropdown() {
    isOpen.value = !isOpen.value
    if (isOpen.value) {
      void fetchNotifications()
      void fetchUnreadCount()
    }
  }

  function openDropdown() {
    if (!isOpen.value) {
      isOpen.value = true
      void fetchNotifications()
      void fetchUnreadCount()
    }
  }

  function closeDropdown() {
    isOpen.value = false
  }

  async function respondFriendRequest(
    notificationId: string,
    friendshipId: number,
    action: 'accept' | 'reject',
  ): Promise<{ ok: boolean; message: string }> {
    try {
      if (action === 'accept') {
        const res = await friendsApi.acceptFriendRequest(friendshipId)
        await markAsRead(notificationId)
        return { ok: true, message: res.message || 'Amizade aceita com sucesso.' }
      } else {
        const res = await friendsApi.rejectFriendRequest(friendshipId)
        await markAsRead(notificationId)
        return { ok: true, message: res.message || 'Solicitação recusada.' }
      }
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Não foi possível processar a solicitação.'
      return { ok: false, message: msg }
    }
  }

  function handleWindowFocus() {
    void fetchUnreadCount()
    if (isOpen.value) {
      void fetchNotifications()
    }
  }

  function startPolling(intervalMs = 45000) {
    if (isPollingActive) return
    isPollingActive = true

    void fetchUnreadCount()

    if (typeof window !== 'undefined') {
      window.addEventListener('focus', handleWindowFocus)
      pollingTimer = setInterval(() => {
        void fetchUnreadCount()
      }, intervalMs)
    }
  }

  function stopPolling() {
    if (!isPollingActive) return
    isPollingActive = false

    if (pollingTimer) {
      clearInterval(pollingTimer)
      pollingTimer = null
    }

    if (typeof window !== 'undefined') {
      window.removeEventListener('focus', handleWindowFocus)
    }
  }

  return {
    notifications,
    unread,
    total,
    loading,
    open,
    filterUnread,
    error,
    fetchUnreadCount,
    fetchNotifications,
    markAsRead,
    markAllAsRead,
    setUnreadFilter,
    toggleDropdown,
    openDropdown,
    closeDropdown,
    respondFriendRequest,
    startPolling,
    stopPolling,
  }
}

export default useNotifications
