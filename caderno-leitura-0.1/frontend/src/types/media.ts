// Imagens guardadas no cofre (feature 090): uso, cota e lista.

export type MediaKind = 'notebook_page' | 'avatar' | 'cover'
export type MediaStatus = 'active' | 'missing'
export type UsageLevel = 'normal' | 'high' | 'full'
export type VaultState = 'ready' | 'key_missing' | 'key_mismatch' | 'storage_unavailable'
export type MediaSort = 'created_desc' | 'size_desc' | 'expires_asc'

export interface MediaItem {
  id: string
  kind: MediaKind
  status: MediaStatus
  book: { id: number; title: string; in_trash: boolean } | null
  study: { id: number; title: string; reading_status: string; in_trash: boolean } | null
  byte_size: number
  width: number
  height: number
  keep_forever: boolean
  created_at: string
  expires_at: string | null
  days_left: number | null
}

export interface MediaUsage {
  user: { used_bytes: number; quota_bytes: number; count: number; percent: number; level: UsageLevel }
  /** Só o administrador recebe os números; os demais, o nível. */
  server: {
    level: UsageLevel
    used_bytes?: number
    quota_bytes?: number
    disk_free_bytes?: number | null
    percent?: number
  }
  vault?: { state: VaultState }
}

export interface MediaListParams {
  kind?: MediaKind | ''
  book_id?: number | null
  sort?: MediaSort
  limit?: number
  offset?: number
}

export interface MediaList {
  items: MediaItem[]
  next_offset: number | null
}

export type BulkDeleteRequest =
  | { filter: 'completed_studies'; dry_run: boolean }
  | { filter: 'older_than_days'; days: number; dry_run: boolean }
  | { ids: string[]; dry_run: boolean }

export interface BulkDeleteResult {
  matched: number
  freed_bytes: number
  deleted: number
}

export interface StudyPhotoResult {
  item: MediaItem
  usage: MediaUsage
}

export const MEDIA_RETENTION_DAYS = 30
export const MEDIA_KIND_LABELS: Record<MediaKind, string> = {
  notebook_page: 'Página digitalizada',
  avatar: 'Foto de perfil',
  cover: 'Capa de livro',
}
