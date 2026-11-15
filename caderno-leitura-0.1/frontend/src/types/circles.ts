// F0.12.07 (spec 120): círculos de leitura com trava anti-spoiler.

export interface CircleUser {
  id: string | null
  username: string
  display_name: string
}

export interface CircleSummary {
  id: number
  name: string
  book_title: string
  book_author: string | null
  role: 'owner' | 'member'
  member_count: number
  part_count: number
  progress: number
  finished: boolean
}

export interface CircleInvite {
  id: number
  name: string
  book_title: string
  book_author: string | null
  invited_by: CircleUser
}

export interface CircleListResponse {
  circles: CircleSummary[]
  invites: CircleInvite[]
}

export interface CirclePart {
  id: number
  position: number
  name: string
  post_count: number
  visible: boolean
}

export interface CircleMember extends CircleUser {
  role: 'owner' | 'member'
  status: 'invited' | 'active'
  progress: number
  finished: boolean
}

export interface CircleDetail {
  id: number
  name: string
  book_title: string
  book_author: string | null
  isbn: string | null
  role: 'owner' | 'member'
  progress: number
  finished: boolean
  my_book_id: number | null
  parts: CirclePart[]
  members: CircleMember[]
}

export interface CirclePost {
  id: number
  part_id: number
  body: string
  author: CircleUser
  created_at: string
  edited_at: string | null
  can_edit: boolean
  can_delete: boolean
}

export interface CirclePartPosts {
  part_id: number
  locked: boolean
  count: number
  posts: CirclePost[]
}

export interface InvitableFriend {
  id: string
  username: string
  display_name: string
}
