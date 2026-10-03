export interface SecurityErrorResponse {
  detail: string
  error_id?: string
}

export interface SecurityPolicyConfig {
  cspEnforced: boolean
  corsAllowedOrigins: string[]
}
