// Textos das imagens do cofre (feature 090-C): tamanhos, validade e nível de uso.
import type { MediaItem, UsageLevel, VaultState } from '../types/media.ts'

const KIB = 1024
const MIB = KIB * 1024
const GIB = MIB * 1024

/** Tamanho como o Windows mostra: base 1024, rótulos KB, MB e GB, vírgula decimal. */
export function formatBytes(value: number): string {
  const bytes = Math.max(0, value)
  if (bytes >= GIB) {
    const gb = bytes / GIB
    return `${Number.isInteger(gb) ? gb : gb.toFixed(1).replace('.', ',')} GB`
  }
  if (bytes >= MIB) return `${Math.round(bytes / MIB)} MB`
  if (bytes === 0) return '0 KB'
  return `${Math.max(1, Math.round(bytes / KIB))} KB`
}

/** "expira em 3 dias", "expira hoje", "Mantida permanentemente" ou "Não expira". */
export function validityText(item: Pick<MediaItem, 'kind' | 'keep_forever' | 'days_left'>): string {
  if (item.kind !== 'notebook_page') return 'Não expira'
  if (item.keep_forever) return 'Mantida permanentemente'
  if (item.days_left === null) return 'Não expira'
  if (item.days_left <= 0) return 'expira hoje'
  return item.days_left === 1 ? 'expira em 1 dia' : `expira em ${item.days_left} dias`
}

/** Data curta (dd/mm/aaaa) no fuso do navegador. */
export function shortDate(iso: string): string {
  const date = new Date(iso)
  const pad = (value: number) => String(value).padStart(2, '0')
  return `${pad(date.getDate())}/${pad(date.getMonth() + 1)}/${date.getFullYear()}`
}

export const LEVEL_LABELS: Record<UsageLevel, string> = {
  normal: 'Normal',
  high: 'Quase cheio',
  full: 'Cheio',
}

export function usageText(used: number, quota: number, count?: number): string {
  const base = `${formatBytes(used)} de ${formatBytes(quota)} utilizados`
  if (count === undefined) return base
  return `${base} (${count} ${count === 1 ? 'imagem' : 'imagens'})`
}

export const VAULT_STATE_TEXT: Record<VaultState, string> = {
  ready: '',
  key_missing: 'O cofre de imagens está trancado: a chave não está instalada neste computador. Para reinstalá-la, '
    + 'rode instalar.py --media-key --restore com o código de recuperação.',
  key_mismatch: 'O cofre de imagens está trancado: a chave instalada não é a deste acervo. Reinstale a chave certa '
    + 'com instalar.py --media-key --restore e o código de recuperação.',
  storage_unavailable: 'O cofre de imagens não está disponível: confira se o HD de armazenamento está conectado.',
}
