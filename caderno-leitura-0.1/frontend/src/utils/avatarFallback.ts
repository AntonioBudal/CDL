// Feature 090-B: avatar que não carrega (cofre trancado, arquivo ausente, link externo fora do ar) não mostra o
// ícone de imagem quebrada. Um único tratador global cobre todas as telas: a imagem vira um pixel transparente e
// aparece só o fundo do círculo, que já usa os tokens do tema. As capas têm tratamento próprio (BookCover.vue).

export const TRANSPARENT_PIXEL = 'data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7'

interface ImageLike {
  tagName?: string
  src?: string
  dataset?: Record<string, string | undefined>
  getAttribute?: (name: string) => string | null
}

/** Decide se a imagem com erro é um avatar (rota de avatares ou elemento marcado como avatar). */
export function isAvatarImage(target: ImageLike): boolean {
  if (!target || (target.tagName ?? '').toUpperCase() !== 'IMG') return false
  const src = target.getAttribute?.('src') ?? target.src ?? ''
  if (src.startsWith('data:')) return false
  const className = target.getAttribute?.('class') ?? ''
  return src.includes('/api/avatars/') || /avatar/i.test(className)
}

/** Troca a imagem quebrada pelo pixel transparente, uma única vez. */
export function handleAvatarError(target: ImageLike): boolean {
  if (!isAvatarImage(target) || target.dataset?.avatarFallback) return false
  if (target.dataset) target.dataset.avatarFallback = '1'
  target.src = TRANSPARENT_PIXEL
  return true
}

export function installAvatarFallback(root: Pick<Document, 'addEventListener'> = document): void {
  // Erros de imagem não sobem pelo DOM; a captura no documento pega todos.
  root.addEventListener('error', event => { handleAvatarError(event.target as ImageLike) }, true)
}
