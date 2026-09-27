export type NotificationEventType =
  | 'friend_request'
  | 'friend_accepted'
  | 'study_shared'
  | 'system_alert'

export interface NotificationActorRead {
  id: string
  username: string
  display_name: string
  avatar_url?: string | null
}

export interface NotificationItem {
  id: string
  user_id: string
  actor?: NotificationActorRead | null
  event_type: NotificationEventType
  payload: Record<string, any>
  read_at?: string | null
  created_at: string
}

export interface NotificationListResponse {
  items: NotificationItem[]
  total: number
  unread_count: number
}

export interface UnreadCountResponse {
  unread_count: number
}

export interface BroadcastNotificationRequest {
  title: string
  message: string
  severity?: 'info' | 'warning' | 'critical'
  link?: string | null
}

export interface BroadcastNotificationResponse {
  dispatched_count: number
  message: string
}

export interface NotificationPurgeResponse {
  purged_count: number
  retention_days: number
  message: string
}
