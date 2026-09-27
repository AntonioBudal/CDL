import type { ContrastCalculationOptions, ContrastResult } from '../types.ts'

/**
 * Normaliza qualquer cor CSS comum (Hex 3/6/8 dígitos, rgb(), rgba(), named colors)
 * para uma tupla [r, g, b, a] com r,g,b em 0-255 e a em 0.0-1.0.
 */
export function parseCssColor(color: string): [number, number, number, number] {
  if (!color || typeof color !== 'string') {
    return [0, 0, 0, 1]
  }

  const c = color.trim().toLowerCase()

  // Cores nomeadas comuns
  if (c === 'transparent') return [0, 0, 0, 0]
  if (c === 'white') return [255, 255, 255, 1]
  if (c === 'black') return [0, 0, 0, 1]

  // Hexadecimal (#fff, #ffffff, #ffffff80)
  if (c.startsWith('#')) {
    const hex = c.slice(1)
    if (hex.length === 3) {
      const r = parseInt(hex[0] + hex[0], 16)
      const g = parseInt(hex[1] + hex[1], 16)
      const b = parseInt(hex[2] + hex[2], 16)
      return [r, g, b, 1]
    }
    if (hex.length === 4) {
      const r = parseInt(hex[0] + hex[0], 16)
      const g = parseInt(hex[1] + hex[1], 16)
      const b = parseInt(hex[2] + hex[2], 16)
      const a = parseInt(hex[3] + hex[3], 16) / 255
      return [r, g, b, a]
    }
    if (hex.length === 6) {
      const r = parseInt(hex.slice(0, 2), 16)
      const g = parseInt(hex.slice(2, 4), 16)
      const b = parseInt(hex.slice(4, 6), 16)
      return [r, g, b, 1]
    }
    if (hex.length === 8) {
      const r = parseInt(hex.slice(0, 2), 16)
      const g = parseInt(hex.slice(2, 4), 16)
      const b = parseInt(hex.slice(4, 6), 16)
      const a = parseInt(hex.slice(6, 8), 16) / 255
      return [r, g, b, a]
    }
  }

  // rgb(...) ou rgba(...)
  const rgbMatch = c.match(/rgba?\(\s*([0-9.]+)\s*,\s*([0-9.]+)\s*,\s*([0-9.]+)(?:\s*,\s*([0-9.]+))?\s*\)/)
  if (rgbMatch) {
    const r = Math.min(255, Math.max(0, parseFloat(rgbMatch[1])))
    const g = Math.min(255, Math.max(0, parseFloat(rgbMatch[2])))
    const b = Math.min(255, Math.max(0, parseFloat(rgbMatch[3])))
    const a = rgbMatch[4] !== undefined ? Math.min(1, Math.max(0, parseFloat(rgbMatch[4]))) : 1
    return [r, g, b, a]
  }

  // Se estiver no browser e for variável CSS ou outro formato complexo
  if (typeof window !== 'undefined' && typeof document !== 'undefined') {
    try {
      const probe = document.createElement('div')
      probe.style.color = color
      document.body.appendChild(probe)
      const computed = window.getComputedStyle(probe).color
      document.body.removeChild(probe)
      if (computed && computed !== color) {
        return parseCssColor(computed)
      }
    } catch {
      // Ignora falhas de probe no DOM
    }
  }

  return [0, 0, 0, 1]
}

/**
 * Calcula a luminância relativa conforme a fórmula canônica da WCAG 2.1:
 * L = 0.2126 * R' + 0.7152 * G' + 0.0722 * B'
 * onde R', G', B' são os valores lineares sRGB.
 */
export function getRelativeLuminance(rgb: [number, number, number]): number {
  const linear = rgb.map(val => {
    const s = val / 255
    return s <= 0.03928 ? s / 12.92 : Math.pow((s + 0.055) / 1.055, 2.4)
  })

  return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]
}

/**
 * Calcula a razão de contraste entre duas luminâncias relativas:
 * ratio = (L1 + 0.05) / (L2 + 0.05) onde L1 >= L2
 */
export function getContrastRatio(l1: number, l2: number): number {
  const lighter = Math.max(l1, l2)
  const darker = Math.min(l1, l2)
  return (lighter + 0.05) / (darker + 0.05)
}

/**
 * Composição alfa (Alpha Blending) de uma cor sobre um fundo opaco.
 */
export function blendAlpha(
  foreground: [number, number, number, number],
  background: [number, number, number]
): [number, number, number] {
  const [r1, g1, b1, a] = foreground
  const [r2, g2, b2] = background

  const r = Math.round(r1 * a + r2 * (1 - a))
  const g = Math.round(g1 * a + g2 * (1 - a))
  const b = Math.round(b1 * a + b2 * (1 - a))

  return [r, g, b]
}

/**
 * Determina automaticamente uma cor de primeiro plano legível e acessível
 * a partir de uma cor de fundo, avaliando luminância e limiares da WCAG 2.1.
 */
export function getAccessibleTextColor(
  backgroundColor: string,
  options?: ContrastCalculationOptions
): ContrastResult {
  const targetRatio = options?.targetRatio ?? (options?.highContrast ? 7.0 : 4.5)
  const lightCandidate = options?.lightColor ?? '#ffffff'
  const darkCandidate = options?.darkColor ?? '#18181b'
  const parentBg = options?.parentBackground ? parseCssColor(options.parentBackground) : [255, 255, 255, 1]

  const parsedBg = parseCssColor(backgroundColor)
  const effectiveBgRgb: [number, number, number] =
    parsedBg[3] < 1
      ? blendAlpha(parsedBg, [parentBg[0], parentBg[1], parentBg[2]])
      : [parsedBg[0], parsedBg[1], parsedBg[2]]

  const bgLum = getRelativeLuminance(effectiveBgRgb)

  const lightRgb = parseCssColor(lightCandidate)
  const darkRgb = parseCssColor(darkCandidate)

  const lightLum = getRelativeLuminance([lightRgb[0], lightRgb[1], lightRgb[2]])
  const darkLum = getRelativeLuminance([darkRgb[0], darkRgb[1], darkRgb[2]])

  const lightRatio = getContrastRatio(bgLum, lightLum)
  const darkRatio = getContrastRatio(bgLum, darkLum)

  // Escolhe a cor com maior razão de contraste
  const chosenColor = lightRatio >= darkRatio ? lightCandidate : darkCandidate
  const chosenRatio = Math.max(lightRatio, darkRatio)

  const isDark = bgLum < 0.5

  return {
    textColor: chosenColor,
    contrastRatio: parseFloat(chosenRatio.toFixed(2)),
    meetsAA: chosenRatio >= targetRatio,
    meetsAAA: chosenRatio >= 7.0,
    luminance: parseFloat(bgLum.toFixed(4)),
    isDarkBackground: isDark,
  }
}
