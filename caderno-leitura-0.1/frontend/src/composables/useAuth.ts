import { useAuthStore } from '../stores/auth.ts'

export function useAuth() {
  return useAuthStore()
}

export default useAuth
