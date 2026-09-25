export type VisibilityLevel = 'public' | 'friends' | 'private';

export interface ProfileReadingStats {
  total_books: number;
  total_studies: number;
  current_streak_days: number;
}

export interface UserProfilePublic {
  username: string;
  display_name: string;
  avatar_url: string | null;
  bio: string | null;
  profile_visibility: VisibilityLevel;
  is_private: boolean;
  reading_stats?: ProfileReadingStats | null;
  created_at: string;
}

export interface UserProfilePrivate {
  user_id: string;
  username: string;
  display_name: string;
  email: string | null;
  avatar_url: string | null;
  bio: string | null;
  profile_visibility: VisibilityLevel;
  dashboard_visibility: VisibilityLevel;
  is_discoverable: boolean;
  show_reading_stats: boolean;
  has_google_avatar: boolean;
  google_avatar_url: string | null;
  reading_stats: ProfileReadingStats;
  created_at: string;
  updated_at: string;
}

export interface UserProfileUpdate {
  username?: string;
  display_name?: string;
  bio?: string | null;
  profile_visibility?: VisibilityLevel;
  dashboard_visibility?: VisibilityLevel;
  is_discoverable?: boolean;
  show_reading_stats?: boolean;
  use_google_avatar?: boolean;
}

export interface UserSearchItem {
  username: string;
  display_name: string;
  avatar_url: string | null;
  bio: string | null;
}
