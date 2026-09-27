import { api } from '../services/api.ts'
import type {
  BroadcastNotificationRequest,
  BroadcastNotificationResponse,
  NotificationItem,
  NotificationListResponse,
  NotificationPurgeResponse,
  UnreadCountResponse,
} from '../types/notifications.ts'
import type { NotificationReadAllResponse } from '../services/api.ts'

export const notificationsApi = {
  getNotifications: (
    params?: { unread_only?: boolean; limit?: number; offset?: number },
    signal?: AbortSignal,
  ): Promise<NotificationListResponse> => api.getNotifications(params, signal),

  getUnreadCount: (signal?: AbortSignal): Promise<UnreadCountResponse> =>
    api.getUnreadCount(signal),

  markAsRead: (notificationId: string): Promise<NotificationItem> =>
    api.markNotificationAsRead(notificationId),

  markAllAsRead: (): Promise<NotificationReadAllResponse> =>
    api.markAllNotificationsAsRead(),

  broadcastNotification: (
    payload: BroadcastNotificationRequest,
  ): Promise<BroadcastNotificationResponse> =>
    api.broadcastNotification(payload),

  purgeNotifications: (
    retentionDays?: number,
  ): Promise<NotificationPurgeResponse> => api.purgeNotifications(retentionDays),
}

export default notificationsApi
