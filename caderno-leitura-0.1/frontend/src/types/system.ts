// Painel de Sistema (F0.10.03): espelho de backend/app/schemas/system.py.
export interface BackupStatus {
  enabled: boolean
  interval_hours: number
  keep: number
  count: number
  last_at: string | null
  overdue: boolean
  secondary_configured: boolean
}

export interface SystemStatus {
  version: string
  commit: string | null
  schema_revision: string | null
  expected_schema_revisions: string[]
  google_auth_enabled: boolean
  secure_delete: boolean
  backups: BackupStatus | null
}

export interface IntegrityResult {
  ok: boolean
  detail: string | null
  checked_at: string
}
