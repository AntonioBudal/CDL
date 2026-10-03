/**
 * Tipagens para o micro-toast flutuante de ferramentas e contexto de toque mobile.
 * Feature: 051-mobile-toque-microtoast
 */

export interface FloatingToastPayload {
  /** Mensagem textual concisa (ex: "Destaque aplicado", "Trecho ocultado") */
  message: string
  /** Ponto cromático opcional para representar a cor do marca-texto ativo */
  colorDot?: string
  /** Duração em milissegundos antes do desaparecimento (padrão: 1800ms) */
  duration?: number
}

export interface FloatingToastState {
  visible: boolean
  message: string
  colorDot: string | null
  timerId: ReturnType<typeof setTimeout> | null
}

export interface TouchTapContext {
  /** Timestamp em ms do último toque concluído (touchend) */
  lastTapTimestamp: number
  /** Coordenada X na viewport do último toque */
  lastTapX: number
  /** Coordenada Y na viewport do último toque */
  lastTapY: number
  /** Coordenada X de início do toque corrente (touchstart) */
  touchStartX: number
  /** Coordenada Y de início do toque corrente (touchstart) */
  touchStartY: number
  /** Flag indicando se o gesto em andamento excedeu a tolerância e virou scroll */
  isScrolling: boolean
}
