# Contract: Motor Centralizado de Contraste WCAG 2.1 e Composable

**Package**: `frontend/src/utils/contrast.ts` e `frontend/src/composables/useAccessibleContrast.ts`

---

## 1. Funções Utilitárias Puras (`contrast.ts`)

```typescript
/**
 * Normaliza qualquer cor CSS válida para RGBA [r, g, b, a] normalizado (0-255 para RGB, 0-1 para A).
 */
export function parseCssColor(color: string): [number, number, number, number]

/**
 * Calcula a luminância relativa conforme especificação WCAG 2.1.
 * Retorna valor entre 0.0 (preto absoluto) e 1.0 (branco absoluto).
 */
export function getRelativeLuminance(rgb: [number, number, number]): number

/**
 * Calcula a razão de contraste entre duas luminâncias relativas.
 * Retorna número entre 1.0 (mesma cor) e 21.0 (preto contra branco).
 */
export function getContrastRatio(l1: number, l2: number): number

/**
 * Composição alfa (Alpha Blending) de uma cor de primeiro plano sobre um fundo opaco.
 */
export function blendAlpha(
  foreground: [number, number, number, number],
  background: [number, number, number]
): [number, number, number]

/**
 * Função Canônica Centralizada:
 * Determina a cor de primeiro plano com maior legibilidade e conformidade WCAG para um determinado fundo.
 */
export function getAccessibleTextColor(
  backgroundColor: string,
  options?: {
    targetRatio?: number       // Padrão: 4.5
    lightColor?: string        // Padrão: '#ffffff'
    darkColor?: string         // Padrão: '#18181b'
    parentBackground?: string  // Padrão: '#ffffff'
    highContrast?: boolean     // Padrão: false
  }
): ContrastResult
```

---

## 2. Composable Reativo (`useAccessibleContrast.ts`)

```typescript
import { computed, type Ref } from 'vue'
import type { DynamicThemeVariables } from '../types'

/**
 * Composable que gera reativamente o conjunto de variáveis CSS para elementos com fundo dinâmico.
 * Injeta no estilo inline do elemento:
 *   --dynamic-fg
 *   --dynamic-hover-bg
 *   --dynamic-hover-fg
 *   --dynamic-active-bg
 *   --dynamic-active-fg
 *   --dynamic-border
 */
export function useAccessibleContrast(
  backgroundColor: Ref<string> | string,
  options?: {
    targetRatio?: number
    lightColor?: string
    darkColor?: string
  }
): {
  styles: Ref<Record<string, string>>
  result: Ref<ContrastResult>
  isDark: Ref<boolean>
}
```

---

## 3. Contrato de Uso em Componentes e Folhas de Estilo

1. **No Componente Vue**:
   ```vue
   <script setup lang="ts">
   import { useAccessibleContrast } from '@/composables/useAccessibleContrast'
   const { styles } = useAccessibleContrast(props.backgroundColor)
   </script>

   <template>
     <button class="dynamic-button" :style="styles">
       <Icon name="check" :size="16" />
       <span>Salvar</span>
     </button>
   </template>
   ```

2. **Na Folha de Estilo (CSS)**:
   ```css
   .dynamic-button {
     background-color: var(--button-bg);
     color: var(--dynamic-fg, currentColor);
     border: 1px solid var(--dynamic-border, transparent);
     transition: background-color 0.15s ease, color 0.15s ease;
   }

   .dynamic-button:hover:not(:disabled) {
     background-color: var(--dynamic-hover-bg);
     color: var(--dynamic-hover-fg);
   }

   .dynamic-button:active:not(:disabled),
   .dynamic-button[aria-selected='true'] {
     background-color: var(--dynamic-active-bg);
     color: var(--dynamic-active-fg);
   }

   .dynamic-button svg {
     stroke: currentColor;
     fill: none;
   }
   ```
