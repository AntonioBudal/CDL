import { computed, ref } from 'vue'
import { profileApi } from '../api/profile.ts'
import type {
  UserProfilePrivate,
  UserProfilePublic,
  UserProfileUpdate,
  UserSearchItem,
} from '../types.ts'

const currentProfile = ref<UserProfilePrivate | null>(null)
const isLoading = ref<boolean>(false)
const isSaving = ref<boolean>(false)
const profileError = ref<string | null>(null)

export function getInitials(name?: string | null): string {
  if (!name || !name.trim()) return 'CL'
  const parts = name.trim().split(/\s+/).filter(Boolean)
  if (parts.length === 1) {
    return parts[0].substring(0, 2).toUpperCase()
  }
  return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase()
}

export function useProfile() {
  const profile = computed(() => currentProfile.value)
  const loading = computed(() => isLoading.value)
  const saving = computed(() => isSaving.value)
  const error = computed(() => profileError.value)
  const initials = computed(() =>
    getInitials(currentProfile.value?.display_name || currentProfile.value?.username)
  )

  async function fetchProfile(signal?: AbortSignal): Promise<UserProfilePrivate | null> {
    isLoading.value = true
    profileError.value = null
    try {
      const data = await profileApi.getMyProfile(signal)
      currentProfile.value = data
      return data
    } catch (err: unknown) {
      if (err instanceof Error && err.name === 'AbortError') return null
      profileError.value = err instanceof Error ? err.message : 'Falha ao carregar perfil'
      return null
    } finally {
      isLoading.value = false
    }
  }

  async function updateProfile(payload: UserProfileUpdate): Promise<UserProfilePrivate> {
    isSaving.value = true
    profileError.value = null
    try {
      const updated = await profileApi.updateMyProfile(payload)
      currentProfile.value = updated
      return updated
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Falha ao salvar perfil'
      profileError.value = msg
      throw err
    } finally {
      isSaving.value = false
    }
  }

  async function uploadAvatar(file: File): Promise<string> {
    isSaving.value = true
    profileError.value = null
    try {
      const res = await profileApi.uploadAvatar(file)
      if (currentProfile.value) {
        currentProfile.value.avatar_url = res.avatar_url
      }
      return res.avatar_url
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Falha ao enviar avatar'
      profileError.value = msg
      throw err
    } finally {
      isSaving.value = false
    }
  }

  async function deleteAvatar(): Promise<void> {
    isSaving.value = true
    profileError.value = null
    try {
      const res = await profileApi.deleteAvatar()
      if (currentProfile.value) {
        currentProfile.value.avatar_url = res.avatar_url
      }
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Falha ao remover avatar'
      profileError.value = msg
      throw err
    } finally {
      isSaving.value = false
    }
  }

  async function useGoogleAvatar(): Promise<UserProfilePrivate> {
    return await updateProfile({ use_google_avatar: true })
  }

  async function fetchPublicProfile(username: string, signal?: AbortSignal): Promise<UserProfilePublic> {
    return await profileApi.getUserPublicProfile(username, signal)
  }

  async function searchUsers(query?: string, signal?: AbortSignal): Promise<UserSearchItem[]> {
    return await profileApi.searchUsers(query, signal)
  }

  return {
    profile,
    loading,
    saving,
    error,
    initials,
    fetchProfile,
    updateProfile,
    uploadAvatar,
    deleteAvatar,
    useGoogleAvatar,
    fetchPublicProfile,
    searchUsers,
  }
}

export default useProfile
