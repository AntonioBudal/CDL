/** F0.11.08: "há 3 meses", "há 1 ano" (Memória do dia). */
export function timeAgo(createdAt: string, now: Date = new Date()): string {
  const created = new Date(createdAt)
  const months = (now.getFullYear() - created.getFullYear()) * 12 + (now.getMonth() - created.getMonth())
    - (now.getDate() < created.getDate() ? 1 : 0)
  if (months >= 12) {
    const years = Math.floor(months / 12)
    return years === 1 ? 'há 1 ano' : `há ${years} anos`
  }
  if (months >= 1) return months === 1 ? 'há 1 mês' : `há ${months} meses`
  const days = Math.max(1, Math.floor((now.getTime() - created.getTime()) / 86_400_000))
  return `há ${days} dias`
}
