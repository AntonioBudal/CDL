import { api } from '../services/api.ts'
import type { UserPreferences, UserPreferencesPatch } from '../types.ts'

export const preferencesApi = {
  getPreferences: (signal?: AbortSignal): Promise<UserPreferences> =>
    api.getUserPreferences(signal),
  updatePreferences: (
    payload: UserPreferencesPatch,
  ): Promise<UserPreferences> => api.updateUserPreferences(payload),
}

export default preferencesApi
