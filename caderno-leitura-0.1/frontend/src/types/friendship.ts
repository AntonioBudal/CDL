export type FriendshipStatus = 'pending' | 'accepted' | 'blocked';

export type RelationPerspectiveStatus =
  | 'none'
  | 'pending_sent'
  | 'pending_received'
  | 'friends'
  | 'blocked_by_me'
  | 'blocked_by_them';

export interface FriendUser {
  id: string;
  username: string;
  display_name: string;
  avatar_url: string | null;
  bio: string | null;
}

export interface FriendItem {
  friendship_id: number;
  user: FriendUser;
  since: string;
}

export interface FriendRequestItem {
  request_id: number;
  user: FriendUser;
  direction: 'sent' | 'received';
  created_at: string;
}

export interface FriendRequestsResponse {
  received: FriendRequestItem[];
  sent: FriendRequestItem[];
}

export interface FriendBlockedItem {
  friendship_id: number;
  user: FriendUser;
  blocked_at: string;
}

export interface FriendsSummary {
  friends_count: number;
  pending_received_count: number;
  pending_sent_count: number;
}

export interface FriendshipStatusResponse {
  relation_status: RelationPerspectiveStatus;
  request_id?: number | null;
  since?: string | null;
}

export interface FriendshipActionResponse {
  ok: boolean;
  message: string;
  status: 'none' | 'pending' | 'accepted' | 'blocked';
}

export type SocialActiveTab = 'friends' | 'requests' | 'discover' | 'blocked';

export interface BookplateCardProps {
  username: string;
  displayName: string;
  avatarUrl?: string | null;
  bio?: string | null;
  friendsCount: number;
  pendingCount?: number;
}

export interface BookplateCardEmits {
  (e: 'copied', handle: string): void;
  (e: 'shared', url: string): void;
}

export interface BookplateCardState {
  isStamped: boolean;
  isSharing: boolean;
  shareFeedback: string | null;
}
