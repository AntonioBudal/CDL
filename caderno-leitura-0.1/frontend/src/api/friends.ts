import { api } from '../services/api.ts'
import type {
  FriendBlockedItem,
  FriendItem,
  FriendRequestsResponse,
  FriendsSummary,
  FriendshipActionResponse,
  FriendshipStatusResponse,
} from '../types.ts'

export const friendsApi = {
  sendFriendRequest: (username: string): Promise<FriendshipActionResponse> =>
    api.sendFriendRequest(username),
  acceptFriendRequest: (requestId: number): Promise<FriendshipActionResponse> =>
    api.acceptFriendRequest(requestId),
  rejectFriendRequest: (requestId: number): Promise<FriendshipActionResponse> =>
    api.rejectFriendRequest(requestId),
  cancelFriendRequest: (requestId: number): Promise<FriendshipActionResponse> =>
    api.cancelFriendRequest(requestId),
  removeFriend: (username: string): Promise<FriendshipActionResponse> =>
    api.removeFriend(username),
  blockUser: (username: string): Promise<FriendshipActionResponse> =>
    api.blockUser(username),
  unblockUser: (username: string): Promise<FriendshipActionResponse> =>
    api.unblockUser(username),
  getFriends: (signal?: AbortSignal): Promise<FriendItem[]> =>
    api.getFriends(signal),
  getFriendRequests: (signal?: AbortSignal): Promise<FriendRequestsResponse> =>
    api.getFriendRequests(signal),
  getBlockedUsers: (signal?: AbortSignal): Promise<FriendBlockedItem[]> =>
    api.getBlockedUsers(signal),
  getFriendsSummary: (signal?: AbortSignal): Promise<FriendsSummary> =>
    api.getFriendsSummary(signal),
  getRelationStatus: (username: string, signal?: AbortSignal): Promise<FriendshipStatusResponse> =>
    api.getRelationStatus(username, signal),
}

export default friendsApi
