import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)
const srcDir = path.resolve(__dirname, '../src')

// 10 Temas Canônicos da Feature 9.5
const EXPECTED_CANONICAL_THEMES = [
  'papel-fosco',
  'noite-suave',
  'cinza-neutro',
  'grafite',
  'monocromatico',
  'pergaminho',
  'e-ink',
  'solario',
  'fiorde',
  'voltagem',
]

const OBSOLETE_THEMES = ['porcelana', 'breu', 'vinil', 'sequoia', 'vespera']

const EXPECTED_SIMPLIFIED_NAMES = {
  pergaminho: 'Sépia',
  'e-ink': 'E-Ink',
  solario: 'Solarized',
  fiorde: 'Nord',
  voltagem: 'Cyber',
  'papel-fosco': 'Papel Fosco',
  'noite-suave': 'Noite Suave',
  'cinza-neutro': 'Cinza Neutro',
  grafite: 'Grafite',
  monocromatico: 'Monocromático',
}

test('US1/US2: appearance-bootstrap.js define catálogo oficial exato de 10 temas com nomes simplificados', () => {
  const bootstrapPath = path.join(srcDir, 'appearance-bootstrap.js')
  const content = fs.readFileSync(bootstrapPath, 'utf8')

  // Extrair o bloco de temas
  const themeMatch = content.match(/field\('theme',\s*'[^']+',\s*'[^']+',\s*\[([\s\S]*?)\]\)/)
  assert.ok(themeMatch, 'Bloco de definição do campo theme deve existir')

  const themeBlock = themeMatch[1]
  const entries = [...themeBlock.matchAll(/\['([^']+)',\s*'([^']+)'\]/g)].map(m => ({
    id: m[1],
    label: m[2],
  }))

  assert.equal(entries.length, 10, 'Catálogo deve ter exatamente 10 temas')
  assert.equal(entries[0].id, 'papel-fosco', 'Papel Fosco deve ser o primeiro tema (padrão oficial)')

  for (const expId of EXPECTED_CANONICAL_THEMES) {
    const found = entries.find(e => e.id === expId)
    assert.ok(found, `Tema ${expId} deve estar presente no catálogo`)
    assert.equal(found.label, EXPECTED_SIMPLIFIED_NAMES[expId], `Rótulo de ${expId} deve ser ${EXPECTED_SIMPLIFIED_NAMES[expId]}`)
  }

  for (const obs of OBSOLETE_THEMES) {
    const found = entries.find(e => e.id === obs)
    assert.equal(found, undefined, `Tema obsoleto ${obs} não deve estar no catálogo`)
  }
})

test('US1: appearance-bootstrap.js possui mapa de migração automática para temas legados', () => {
  const bootstrapPath = path.join(srcDir, 'appearance-bootstrap.js')
  const content = fs.readFileSync(bootstrapPath, 'utf8')

  assert.ok(content.includes("porcelana: 'papel-fosco'"), 'porcelana deve migrar para papel-fosco')
  assert.ok(content.includes("breu: 'noite-suave'"), 'breu deve migrar para noite-suave')
  assert.ok(content.includes("vinil: 'grafite'"), 'vinil deve migrar para grafite')
  assert.ok(content.includes("sequoia: 'noite-suave'"), 'sequoia deve migrar para noite-suave')
  assert.ok(content.includes("vespera: 'noite-suave'"), 'vespera deve migrar para noite-suave')
  assert.ok(content.includes("light: 'papel-fosco'"), 'light genérico deve migrar para papel-fosco')
  assert.ok(content.includes("dark: 'noite-suave'"), 'dark genérico deve migrar para noite-suave')
})

test('US1: usePreferences.ts define CANONICAL_THEME_IDS, resolveCanonicalTheme e previne reset genérico', async () => {
  const prefsPath = path.join(srcDir, 'composables/usePreferences.ts')
  const content = fs.readFileSync(prefsPath, 'utf8')

  assert.ok(content.includes('CANONICAL_THEME_IDS'), 'Deve exportar CANONICAL_THEME_IDS')
  assert.ok(content.includes('resolveCanonicalTheme'), 'Deve exportar resolveCanonicalTheme')
  assert.ok(content.includes("theme_mode: 'papel-fosco'"), 'Valor padrão de theme_mode deve ser papel-fosco')
  assert.ok(content.includes("localStorage.getItem(STORAGE_KEY_APPEARANCE)"), 'loadFromLocal deve sincronizar com caderno.aparencia.v2')
})

test('US1: main.ts executa leitura síncrona de preferências antes de montar o Vue', () => {
  const mainPath = path.join(srcDir, 'main.ts')
  const content = fs.readFileSync(mainPath, 'utf8')

  const loadIdx = content.indexOf('usePreferences().loadFromLocal()')
  const mountIdx = content.indexOf("mount('#app')")

  assert.ok(loadIdx !== -1, 'main.ts deve chamar usePreferences().loadFromLocal()')
  assert.ok(mountIdx !== -1, 'main.ts deve chamar mount(#app)')
  assert.ok(loadIdx < mountIdx, 'loadFromLocal() deve ocorrer estritamente antes de mount(#app)')
})

test('US2: palettes.css define tokens obrigatórios para os 10 temas e purga obsoletos', () => {
  const palettesPath = path.join(srcDir, 'palettes.css')
  const content = fs.readFileSync(palettesPath, 'utf8')

  for (const obs of OBSOLETE_THEMES) {
    assert.ok(
      !content.includes(`data-theme="${obs}"`),
      `palettes.css não deve conter seletor do tema obsoleto ${obs}`
    )
  }

  const requiredTokens = [
    '--color-page',
    '--color-surface',
    '--color-surface-soft',
    '--color-text',
    '--color-muted',
    '--color-border',
    '--color-border-strong',
    '--color-accent',
    '--color-on-accent',
  ]

  for (const themeId of EXPECTED_CANONICAL_THEMES) {
    assert.ok(
      content.includes(`data-theme="${themeId}"`) || (themeId === 'papel-fosco' && content.includes(':root,')),
      `palettes.css deve definir regras para ${themeId}`
    )
  }

  for (const token of requiredTokens) {
    assert.ok(content.includes(token), `Token ${token} deve estar presente em palettes.css`)
  }
})

test('US2: style.css e appearance-advanced.css purgam seletores de temas obsoletos', () => {
  const stylePath = path.join(srcDir, 'style.css')
  const advPath = path.join(srcDir, 'appearance-advanced.css')
  const styleContent = fs.readFileSync(stylePath, 'utf8')
  const advContent = fs.readFileSync(advPath, 'utf8')

  for (const obs of OBSOLETE_THEMES) {
    assert.ok(
      !styleContent.includes(`data-theme='${obs}'`) && !styleContent.includes(`data-theme="${obs}"`),
      `style.css não deve conter o tema obsoleto ${obs}`
    )
    assert.ok(
      !advContent.includes(`data-theme='${obs}'`) && !advContent.includes(`data-theme="${obs}"`),
      `appearance-advanced.css não deve conter o tema obsoleto ${obs}`
    )
  }

  assert.ok(styleContent.includes("data-theme='noite-suave'"), 'style.css deve incluir noite-suave')
  assert.ok(styleContent.includes("data-theme='grafite'"), 'style.css deve incluir grafite')
  assert.ok(advContent.includes("data-theme='noite-suave'"), 'appearance-advanced.css deve incluir noite-suave')
})

test('US2: HeatmapCalendar.vue inclui temas escuros noite-suave e grafite', () => {
  const heatmapPath = path.join(srcDir, 'components/HeatmapCalendar.vue')
  const content = fs.readFileSync(heatmapPath, 'utf8')

  assert.ok(content.includes("data-theme='noite-suave'"), 'HeatmapCalendar deve conter seletor noite-suave')
  assert.ok(content.includes("data-theme='grafite'"), 'HeatmapCalendar deve conter seletor grafite')
  for (const obs of OBSOLETE_THEMES) {
    assert.ok(!content.includes(`data-theme='${obs}'`), `HeatmapCalendar não deve conter ${obs}`)
  }
})

test('US3: SharedStudiesList.vue trava SVG do estado vazio em no máximo 120px', () => {
  const filePath = path.join(srcDir, 'components/library/SharedStudiesList.vue')
  const content = fs.readFileSync(filePath, 'utf8')

  assert.ok(content.includes('empty-state-svg'), 'SVG do estado vazio deve possuir classe empty-state-svg')
  assert.ok(content.includes('max-width: 120px'), 'Estilo deve impor max-width: 120px')
  assert.ok(content.includes('max-height: 120px'), 'Estilo deve impor max-height: 120px')
})

test('US3: StudyView.vue estrutura .share-action com inline-flex, gap de 8px, nowrap e SVG em 1.2em', () => {
  const filePath = path.join(srcDir, 'views/StudyView.vue')
  const content = fs.readFileSync(filePath, 'utf8')

  assert.ok(content.includes('.share-action {'), '.share-action deve ser estilizado')
  assert.ok(content.includes('white-space: nowrap'), '.share-action deve impedir quebra de linha com nowrap')
  assert.ok(content.includes('gap: 8px'), '.share-action deve ter gap de 8px')
  assert.ok(content.includes('.share-action svg'), '.share-action svg deve ter regras explícitas')
  assert.ok(content.includes('width: 1.2em'), '.share-action svg deve ter width: 1.2em')
  assert.ok(content.includes('height: 1.2em'), '.share-action svg deve ter height: 1.2em')
})

test('US3 & US4: ExportModal.vue trava inputs em 24px e utiliza tokens canônicos do tema', () => {
  const filePath = path.join(srcDir, 'components/ExportModal.vue')
  const content = fs.readFileSync(filePath, 'utf8')

  assert.ok(content.includes('width: 24px'), 'Inputs de seleção devem ter width: 24px')
  assert.ok(content.includes('height: 24px'), 'Inputs de seleção devem ter height: 24px')
  assert.ok(content.includes('flex-shrink: 0'), 'Inputs de seleção devem ter flex-shrink: 0')

  assert.ok(content.includes('var(--color-surface'), 'Modal deve usar --color-surface')
  assert.ok(content.includes('var(--color-text'), 'Modal deve usar --color-text')
  assert.ok(content.includes('var(--color-muted'), 'Modal deve usar --color-muted')
  assert.ok(content.includes('var(--color-border'), 'Modal deve usar --color-border')
  assert.ok(content.includes('var(--color-accent'), 'Modal deve usar --color-accent')

  assert.ok(!content.includes('var(--color-bg,'), 'Não deve conter var(--color-bg,')
  assert.ok(!content.includes('var(--color-primary,'), 'Não deve conter var(--color-primary,')
})

test('US4: StudyStatusBadge.vue e GroupSection.vue garantem contraste adaptativo', () => {
  const badgePath = path.join(srcDir, 'components/StudyStatusBadge.vue')
  const groupPath = path.join(srcDir, 'components/views/GroupSection.vue')
  const badgeContent = fs.readFileSync(badgePath, 'utf8')
  const groupContent = fs.readFileSync(groupPath, 'utf8')

  assert.ok(badgeContent.includes("data-theme='noite-suave'"), 'StudyStatusBadge deve ter regras para temas escuros')
  assert.ok(badgeContent.includes('var(--color-surface'), 'Dropdown de status deve usar --color-surface')
  assert.ok(badgeContent.includes('var(--color-border'), 'Dropdown de status deve usar --color-border')

  assert.ok(groupContent.includes("data-theme='noite-suave'"), 'GroupSection deve calibrar contraste em temas escuros')
  assert.ok(groupContent.includes('var(--color-surface'), 'Cabeçalho de grupo deve usar --color-surface')
  assert.ok(groupContent.includes('var(--color-border'), 'Cabeçalho de grupo deve usar --color-border')
  assert.ok(groupContent.includes('color: #ffffff'), 'GroupSection deve garantir texto branco em fundos escuros')
})
