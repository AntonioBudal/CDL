export type ResourceVisibility = 'inherit' | 'private' | 'friends' | 'custom' | 'public'
export type BookVisibility = 'private' | 'friends' | 'public'

export interface ResourceOwnerSummary {
  id: string
  username: string
  display_name: string
  avatar_url?: string | null
}

export type ResourceOwner = ResourceOwnerSummary

export interface ResourcePermissionItem {
  user_id: string
  username: string
  display_name: string
  avatar_url?: string | null
  created_at: string
}

export interface ResourcePermissionsRead {
  resource_type: string
  resource_id: number
  visibility: ResourceVisibility
  effective_visibility: ResourceVisibility
  is_owner: boolean
  permissions: ResourcePermissionItem[]
}

export interface SharedStudySummary {
  id: number
  title: string
  book_id: number
  book_title: string
  chapter_id?: number | null
  chapter_name?: string | null
  owner_id: string
  owner_username: string
  owner_display_name: string
  owner_avatar_url?: string | null
  visibility: string
  updated_at: string
}

export interface SharedStudiesResponse {
  items: SharedStudySummary[]
  total: number
}

export interface SharedBookSummary {
  id: number
  title: string
  author?: string | null
  subtitle?: string | null
  cover_image?: string | null
  owner_id: string
  owner_username: string
  owner_display_name: string
  owner_avatar_url?: string | null
  visibility: string
  updated_at: string
}

export interface SharedBooksResponse {
  items: SharedBookSummary[]
  total: number
}
