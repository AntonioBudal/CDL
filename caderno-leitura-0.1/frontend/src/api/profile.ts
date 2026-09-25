import { api } from '../services/api.ts'
import type {
  UserProfilePrivate,
  UserProfilePublic,
  UserProfileUpdate,
  UserSearchItem,
} from '../types.ts'

export const profileApi = {
  getMyProfile: (signal?: AbortSignal): Promise<UserProfilePrivate> =>
    api.getMyProfile(signal),
  updateMyProfile: (payload: UserProfileUpdate): Promise<UserProfilePrivate> =>
    api.updateMyProfile(payload),
  uploadAvatar: (file: File): Promise<{ avatar_url: string }> =>
    api.uploadAvatar(file),
  deleteAvatar: (): Promise<{ avatar_url: string | null }> =>
    api.deleteAvatar(),
  getUserPublicProfile: (username: string, signal?: AbortSignal): Promise<UserProfilePublic> =>
    api.getUserPublicProfile(username, signal),
  searchUsers: (query?: string, signal?: AbortSignal): Promise<UserSearchItem[]> =>
    api.searchUsers(query, signal),
}

export default profileApi
