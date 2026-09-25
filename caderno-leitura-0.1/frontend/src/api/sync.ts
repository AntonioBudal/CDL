import { api } from '../services/api.ts'
import type { SyncChangesResponse } from '../types.ts'

export const syncApi = {
  fetchChanges: (since?: string | null, signal?: AbortSignal): Promise<SyncChangesResponse> =>
    api.fetchSyncChanges(since, signal),
}

export default syncApi
