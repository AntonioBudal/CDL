import { computed, ref } from 'vue'
import { friendsApi } from '../api/friends.ts'
import type {
  FriendBlockedItem,
  FriendItem,
  FriendRequestsResponse,
  FriendsSummary,
  FriendshipActionResponse,
  FriendshipStatusResponse,
} from '../types.ts'

const friendsList = ref<FriendItem[]>([])
const requestsData = ref<FriendRequestsResponse>({ received: [], sent: [] })
const blockedList = ref<FriendBlockedItem[]>([])
const summaryData = ref<FriendsSummary>({
  friends_count: 0,
  pending_received_count: 0,
  pending_sent_count: 0,
})

const isLoading = ref<boolean>(false)
const friendsError = ref<string | null>(null)
const actionInProgress = ref<Record<string, boolean>>({})

export function useFriends() {
  const friends = computed(() => friendsList.value)
  const requests = computed(() => requestsData.value)
  const blockedUsers = computed(() => blockedList.value)
  const summary = computed(() => summaryData.value)
  const loading = computed(() => isLoading.value)
  const error = computed(() => friendsError.value)
  const pendingReceivedCount = computed(() => summaryData.value.pending_received_count)

  async function fetchSummary(signal?: AbortSignal): Promise<FriendsSummary | null> {
    try {
      const data = await friendsApi.getFriendsSummary(signal)
      summaryData.value = data
      return data
    } catch {
      return null
    }
  }

  async function fetchFriends(signal?: AbortSignal): Promise<FriendItem[]> {
    isLoading.value = true
    friendsError.value = null
    try {
      const data = await friendsApi.getFriends(signal)
      friendsList.value = data
      return data
    } catch (err: unknown) {
      if (err instanceof Error && err.name === 'AbortError') return friendsList.value
      friendsError.value = err instanceof Error ? err.message : 'Falha ao carregar amigos.'
      return friendsList.value
    } finally {
      isLoading.value = false
    }
  }

  async function fetchRequests(signal?: AbortSignal): Promise<FriendRequestsResponse> {
    isLoading.value = true
    friendsError.value = null
    try {
      const data = await friendsApi.getFriendRequests(signal)
      requestsData.value = data
      return data
    } catch (err: unknown) {
      if (err instanceof Error && err.name === 'AbortError') return requestsData.value
      friendsError.value = err instanceof Error ? err.message : 'Falha ao carregar solicitações.'
      return requestsData.value
    } finally {
      isLoading.value = false
    }
  }

  async function fetchBlocked(signal?: AbortSignal): Promise<FriendBlockedItem[]> {
    isLoading.value = true
    friendsError.value = null
    try {
      const data = await friendsApi.getBlockedUsers(signal)
      blockedList.value = data
      return data
    } catch (err: unknown) {
      if (err instanceof Error && err.name === 'AbortError') return blockedList.value
      friendsError.value = err instanceof Error ? err.message : 'Falha ao carregar usuários bloqueados.'
      return blockedList.value
    } finally {
      isLoading.value = false
    }
  }

  async function sendRequest(username: string): Promise<FriendshipActionResponse> {
    actionInProgress.value[username] = true
    friendsError.value = null
    try {
      const res = await friendsApi.sendFriendRequest(username)
      await fetchSummary()
      return res
    } catch (err: unknown) {
      friendsError.value = err instanceof Error ? err.message : 'Falha ao enviar solicitação.'
      throw err
    } finally {
      actionInProgress.value[username] = false
    }
  }

  async function acceptRequest(requestId: number): Promise<FriendshipActionResponse> {
    const key = `accept-${requestId}`
    actionInProgress.value[key] = true
    friendsError.value = null
    try {
      const res = await friendsApi.acceptFriendRequest(requestId)
      requestsData.value.received = requestsData.value.received.filter((r) => r.request_id !== requestId)
      await Promise.all([fetchSummary(), fetchFriends()])
      return res
    } catch (err: unknown) {
      friendsError.value = err instanceof Error ? err.message : 'Falha ao aceitar solicitação.'
      throw err
    } finally {
      actionInProgress.value[key] = false
    }
  }

  async function rejectRequest(requestId: number): Promise<FriendshipActionResponse> {
    const key = `reject-${requestId}`
    actionInProgress.value[key] = true
    friendsError.value = null
    try {
      const res = await friendsApi.rejectFriendRequest(requestId)
      requestsData.value.received = requestsData.value.received.filter((r) => r.request_id !== requestId)
      await fetchSummary()
      return res
    } catch (err: unknown) {
      friendsError.value = err instanceof Error ? err.message : 'Falha ao recusar solicitação.'
      throw err
    } finally {
      actionInProgress.value[key] = false
    }
  }

  async function cancelRequest(requestId: number): Promise<FriendshipActionResponse> {
    const key = `cancel-${requestId}`
    actionInProgress.value[key] = true
    friendsError.value = null
    try {
      const res = await friendsApi.cancelFriendRequest(requestId)
      requestsData.value.sent = requestsData.value.sent.filter((r) => r.request_id !== requestId)
      await fetchSummary()
      return res
    } catch (err: unknown) {
      friendsError.value = err instanceof Error ? err.message : 'Falha ao cancelar solicitação.'
      throw err
    } finally {
      actionInProgress.value[key] = false
    }
  }

  async function removeFriend(username: string): Promise<FriendshipActionResponse> {
    const key = `remove-${username}`
    actionInProgress.value[key] = true
    friendsError.value = null
    try {
      const res = await friendsApi.removeFriend(username)
      friendsList.value = friendsList.value.filter((f) => f.user.username.toLowerCase() !== username.toLowerCase())
      await fetchSummary()
      return res
    } catch (err: unknown) {
      friendsError.value = err instanceof Error ? err.message : 'Falha ao desfazer amizade.'
      throw err
    } finally {
      actionInProgress.value[key] = false
    }
  }

  async function blockUser(username: string): Promise<FriendshipActionResponse> {
    const key = `block-${username}`
    actionInProgress.value[key] = true
    friendsError.value = null
    try {
      const res = await friendsApi.blockUser(username)
      friendsList.value = friendsList.value.filter((f) => f.user.username.toLowerCase() !== username.toLowerCase())
      requestsData.value.received = requestsData.value.received.filter((r) => r.user.username.toLowerCase() !== username.toLowerCase())
      requestsData.value.sent = requestsData.value.sent.filter((r) => r.user.username.toLowerCase() !== username.toLowerCase())
      await Promise.all([fetchSummary(), fetchBlocked()])
      return res
    } catch (err: unknown) {
      friendsError.value = err instanceof Error ? err.message : 'Falha ao bloquear usuário.'
      throw err
    } finally {
      actionInProgress.value[key] = false
    }
  }

  async function unblockUser(username: string): Promise<FriendshipActionResponse> {
    const key = `unblock-${username}`
    actionInProgress.value[key] = true
    friendsError.value = null
    try {
      const res = await friendsApi.unblockUser(username)
      blockedList.value = blockedList.value.filter((b) => b.user.username.toLowerCase() !== username.toLowerCase())
      await fetchSummary()
      return res
    } catch (err: unknown) {
      friendsError.value = err instanceof Error ? err.message : 'Falha ao desbloquear usuário.'
      throw err
    } finally {
      actionInProgress.value[key] = false
    }
  }

  async function getRelationStatus(username: string, signal?: AbortSignal): Promise<FriendshipStatusResponse> {
    try {
      return await friendsApi.getRelationStatus(username, signal)
    } catch {
      return { relation_status: 'none' }
    }
  }

  function isActionLoading(key: string): boolean {
    return Boolean(actionInProgress.value[key])
  }

  return {
    friends,
    requests,
    blockedUsers,
    summary,
    loading,
    error,
    pendingReceivedCount,
    fetchSummary,
    fetchFriends,
    fetchRequests,
    fetchBlocked,
    sendRequest,
    acceptRequest,
    rejectRequest,
    cancelRequest,
    removeFriend,
    blockUser,
    unblockUser,
    getRelationStatus,
    isActionLoading,
  }
}
