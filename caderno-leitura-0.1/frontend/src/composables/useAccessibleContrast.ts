import { computed, isRef, unref, type ComputedRef, type Ref } from 'vue'
import { getAccessibleTextColor } from '../utils/contrast.ts'
import type { ContrastCalculationOptions, ContrastResult, DynamicThemeVariables } from '../types.ts'

/**
 * Composable que avalia reativamente a cor de fundo e gera variáveis CSS locais
 * prontas para injeção via :style no elemento raiz do componente.
 *
 * Garante que estados normais, hover e active/selected mantenham contraste WCAG.
 */
export function useAccessibleContrast(
  backgroundColor: Ref<string> | string,
  options?: ContrastCalculationOptions
): {
  styles: ComputedRef<Record<string, string>>
  result: ComputedRef<ContrastResult>
  isDark: ComputedRef<boolean>
} {
  const currentBg = computed(() => {
    return isRef(backgroundColor) ? unref(backgroundColor) : backgroundColor
  })

  const result = computed(() => {
    return getAccessibleTextColor(currentBg.value, options)
  })

  const isDark = computed(() => result.value.isDarkBackground)

  const styles = computed<Record<string, string>>(() => {
    const dark = isDark.value
    const fg = result.value.textColor

    // Cores de hover e active dinâmicas calibradas
    const hoverBg = dark ? 'rgba(255, 255, 255, 0.08)' : 'rgba(0, 0, 0, 0.05)'
    const activeBg = dark ? 'rgba(255, 255, 255, 0.14)' : 'rgba(0, 0, 0, 0.10)'

    // Recalcula o contraste sobre os novos backgrounds compostos
    const hoverContrast = getAccessibleTextColor(hoverBg, {
      ...options,
      parentBackground: currentBg.value,
    })

    const activeContrast = getAccessibleTextColor(activeBg, {
      ...options,
      parentBackground: currentBg.value,
    })

    const border = dark ? 'rgba(255, 255, 255, 0.12)' : 'rgba(0, 0, 0, 0.12)'

    const vars: DynamicThemeVariables = {
      '--dynamic-fg': fg,
      '--dynamic-hover-bg': hoverBg,
      '--dynamic-hover-fg': hoverContrast.textColor,
      '--dynamic-active-bg': activeBg,
      '--dynamic-active-fg': activeContrast.textColor,
      '--dynamic-border': border,
    }

    return vars as unknown as Record<string, string>
  })

  return {
    styles,
    result,
    isDark,
  }
}
