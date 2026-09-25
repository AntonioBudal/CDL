import type { Book, Study, StudyCanvasNode } from '../types.ts'
import type { UserPreferences } from './preferences.ts'

export type SyncStatus = 'idle' | 'syncing' | 'offline' | 'conflict' | 'error'

export interface ConflictData {
  detail: string
  entity_id: number
  entity_type: 'study' | 'book' | 'preference'
  server_version: number
  server_updated_at: string
  server_data: Record<string, unknown>
}

export interface SyncDeletedItems {
  book_ids: number[]
  study_ids: number[]
}

export interface SyncUpdatedItems {
  books: Book[]
  studies: Study[]
  canvas_nodes: StudyCanvasNode[]
  preferences?: UserPreferences | null
}

export interface SyncChangesResponse {
  server_time: string
  updated: SyncUpdatedItems
  deleted: SyncDeletedItems
}
