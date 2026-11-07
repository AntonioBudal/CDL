/**
 * Copia texto para a área de transferência, com uma versão HTML opcional (ex.: título em itálico).
 * Ordem: ClipboardItem (texto + HTML) → writeText → textarea com execCommand.
 * Devolve true se alguma das tentativas não lançou erro.
 */
export async function copyRich(text: string, html?: string): Promise<boolean> {
  const nav = typeof navigator !== 'undefined' ? navigator : undefined
  const ClipboardItemCtor = (globalThis as { ClipboardItem?: typeof ClipboardItem }).ClipboardItem

  if (html && nav?.clipboard?.write && ClipboardItemCtor) {
    try {
      await nav.clipboard.write([
        new ClipboardItemCtor({
          'text/plain': new Blob([text], { type: 'text/plain' }),
          'text/html': new Blob([html], { type: 'text/html' }),
        }),
      ])
      return true
    } catch {
      // segue para writeText
    }
  }

  if (nav?.clipboard?.writeText) {
    try {
      await nav.clipboard.writeText(text)
      return true
    } catch {
      // segue para o textarea
    }
  }

  return fallbackCopy(text)
}

function fallbackCopy(text: string): boolean {
  if (typeof document === 'undefined') return false
  try {
    const textArea = document.createElement('textarea')
    textArea.value = text
    textArea.setAttribute('readonly', '')
    textArea.style.position = 'fixed'
    textArea.style.left = '-999999px'
    textArea.style.top = '-999999px'
    document.body.appendChild(textArea)
    textArea.select()
    const ok = document.execCommand('copy')
    textArea.remove()
    return ok
  } catch {
    return false
  }
}
