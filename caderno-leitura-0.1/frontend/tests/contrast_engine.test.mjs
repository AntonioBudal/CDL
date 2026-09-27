import test from 'node:test'
import assert from 'node:assert/strict'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)
const contrastPath = path.resolve(__dirname, '../src/utils/contrast.ts')

// Carregamento dinâmico do módulo TypeScript/JavaScript compilável
// Como o node test runner executa via ESM, podemos importar contrast.ts se apoiado ou testar funções do utilitário
test('Motor de Contraste WCAG 2.1 — parseCssColor', async () => {
  const { parseCssColor } = await import('../src/utils/contrast.ts')

  // Hexadecimal 3 dígitos
  assert.deepEqual(parseCssColor('#fff'), [255, 255, 255, 1])
  assert.deepEqual(parseCssColor('#000'), [0, 0, 0, 1])

  // Hexadecimal 6 dígitos
  assert.deepEqual(parseCssColor('#ffffff'), [255, 255, 255, 1])
  assert.deepEqual(parseCssColor('#18181b'), [24, 24, 27, 1])

  // Hexadecimal 8 dígitos (com alfa)
  const hexAlpha = parseCssColor('#ffffff80')
  assert.equal(hexAlpha[0], 255)
  assert.equal(hexAlpha[1], 255)
  assert.equal(hexAlpha[2], 255)
  assert.ok(Math.abs(hexAlpha[3] - 0.5) < 0.02)

  // rgb(...) e rgba(...)
  assert.deepEqual(parseCssColor('rgb(255, 255, 255)'), [255, 255, 255, 1])
  assert.deepEqual(parseCssColor('rgba(100, 150, 200, 0.75)'), [100, 150, 200, 0.75])

  // Nomes de cores comuns
  assert.deepEqual(parseCssColor('white'), [255, 255, 255, 1])
  assert.deepEqual(parseCssColor('black'), [0, 0, 0, 1])
  assert.deepEqual(parseCssColor('transparent'), [0, 0, 0, 0])
})

test('Motor de Contraste WCAG 2.1 — getRelativeLuminance e getContrastRatio', async () => {
  const { getRelativeLuminance, getContrastRatio } = await import('../src/utils/contrast.ts')

  // Preto puro tem luminância 0
  assert.equal(getRelativeLuminance([0, 0, 0]), 0)

  // Branco puro tem luminância 1
  assert.equal(getRelativeLuminance([255, 255, 255]), 1)

  // Razão de contraste preto vs branco é 21:1
  const maxRatio = getContrastRatio(1, 0)
  assert.equal(Math.round(maxRatio), 21)

  // Mesma cor tem razão de 1:1
  assert.equal(getContrastRatio(0.5, 0.5), 1)

  // Branco vs cinza médio (#767676) atinge limiar de 4.54:1 (WCAG AA)
  const midGrayLum = getRelativeLuminance([118, 118, 118])
  const ratio = getContrastRatio(1, midGrayLum)
  assert.ok(ratio >= 4.5, `Ratio esperado >= 4.5, obteve ${ratio}`)
})

test('Motor de Contraste WCAG 2.1 — blendAlpha', async () => {
  const { blendAlpha } = await import('../src/utils/contrast.ts')

  // 50% de branco sobre fundo preto resulta em cinza médio [128, 128, 128]
  const blended = blendAlpha([255, 255, 255, 0.5], [0, 0, 0])
  assert.ok(Math.abs(blended[0] - 127.5) <= 1)
  assert.ok(Math.abs(blended[1] - 127.5) <= 1)
  assert.ok(Math.abs(blended[2] - 127.5) <= 1)

  // 100% de opacidade mantém primeiro plano
  assert.deepEqual(blendAlpha([24, 24, 27, 1], [255, 255, 255]), [24, 24, 27])

  // 0% de opacidade retorna fundo
  assert.deepEqual(blendAlpha([24, 24, 27, 0], [255, 255, 255]), [255, 255, 255])
})

test('Motor de Contraste WCAG 2.1 — getAccessibleTextColor em temas canônicos', async () => {
  const { getAccessibleTextColor } = await import('../src/utils/contrast.ts')

  // Fundo Branco puro (#ffffff) -> deve escolher texto escuro com contraste >= 4.5
  const whiteRes = getAccessibleTextColor('#ffffff')
  assert.equal(whiteRes.isDarkBackground, false)
  assert.equal(whiteRes.meetsAA, true)
  assert.ok(whiteRes.contrastRatio >= 4.5)
  assert.equal(whiteRes.textColor, '#18181b')

  // Fundo Noite Suave (#1e1e24) -> deve escolher texto claro com contraste >= 4.5
  const darkRes = getAccessibleTextColor('#1e1e24')
  assert.equal(darkRes.isDarkBackground, true)
  assert.equal(darkRes.meetsAA, true)
  assert.ok(darkRes.contrastRatio >= 4.5)
  assert.equal(darkRes.textColor, '#ffffff')

  // Fundo Grafite (#222222) -> deve escolher texto claro
  const graphiteRes = getAccessibleTextColor('#222222')
  assert.equal(graphiteRes.isDarkBackground, true)
  assert.equal(graphiteRes.meetsAA, true)
  assert.ok(graphiteRes.contrastRatio >= 4.5)
  assert.equal(graphiteRes.textColor, '#ffffff')

  // Fundo Papel Fosco (#f5f5f5) -> deve escolher texto escuro
  const paperRes = getAccessibleTextColor('#f5f5f5')
  assert.equal(paperRes.isDarkBackground, false)
  assert.equal(paperRes.meetsAA, true)
  assert.ok(paperRes.contrastRatio >= 4.5)
  assert.equal(paperRes.textColor, '#18181b')

  // Opções personalizadas de cor e limiar
  const customRes = getAccessibleTextColor('#3b82f6', {
    lightColor: '#f8fafc',
    darkColor: '#0f172a',
    targetRatio: 3.0,
  })
  assert.ok(customRes.contrastRatio >= 3.0)
  assert.ok(['#f8fafc', '#0f172a'].includes(customRes.textColor))
})

test('Motor de Contraste WCAG 2.1 — useAccessibleContrast composable', async () => {
  const { ref } = await import('vue')
  const { useAccessibleContrast } = await import('../src/composables/useAccessibleContrast.ts')

  const bg = ref('#ffffff')
  const { styles, isDark } = useAccessibleContrast(bg)

  assert.equal(isDark.value, false)
  assert.equal(styles.value['--dynamic-fg'], '#18181b')
  assert.ok(styles.value['--dynamic-hover-bg'])
  assert.ok(styles.value['--dynamic-active-bg'])

  // Altera para tema escuro reativamente
  bg.value = '#1e1e24'
  assert.equal(isDark.value, true)
  assert.equal(styles.value['--dynamic-fg'], '#ffffff')
})

