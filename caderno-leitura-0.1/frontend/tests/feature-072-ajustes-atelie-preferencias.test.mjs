import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'

const srcDir = path.resolve(process.cwd(), 'src')

test('Setup: Tipos e catálogo CANONICAL_THEME_PREVIEWS declarados em settings.ts', () => {
  const typesPath = path.resolve(srcDir, 'types/settings.ts')
  assert.ok(fs.existsSync(typesPath), 'types/settings.ts deve existir')
  const content = fs.readFileSync(typesPath, 'utf-8')

  assert.ok(content.includes('export type CanonicalThemeId'), 'Deve declarar CanonicalThemeId')
  assert.ok(content.includes('export interface ThemePaletteColors'), 'Deve declarar ThemePaletteColors')
  assert.ok(content.includes('export interface ThemePreviewItem'), 'Deve declarar ThemePreviewItem')
  assert.ok(content.includes('export const CANONICAL_THEME_PREVIEWS'), 'Deve exportar CANONICAL_THEME_PREVIEWS')

  // Verifica presença de todos os 10 temas canônicos
  const canonicalIds = [
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

  for (const id of canonicalIds) {
    assert.ok(content.includes(`'${id}'`), `Catálogo deve incluir o tema ${id}`)
  }
})

test('US1: ThemePreviewGrid implementa galeria de temas estilo Windows 11 com caixas de amostra de cor e WAI-ARIA', () => {
  const compPath = path.resolve(srcDir, 'components/ThemePreviewGrid.vue')
  assert.ok(fs.existsSync(compPath), 'ThemePreviewGrid.vue deve existir')

  const content = fs.readFileSync(compPath, 'utf-8')

  // Semântica acessível WAI-ARIA
  assert.ok(content.includes('role="radiogroup"'), 'Deve conter role="radiogroup"')
  assert.ok(content.includes('role="radio"'), 'Deve conter role="radio"')
  assert.ok(content.includes('aria-checked'), 'Deve conter atributo aria-checked')

  // Box gráfico de cores reais do tema
  assert.ok(content.includes('theme-color-box') || content.includes('theme-preview-box'), 'Deve conter caixa de amostra de cor')
  assert.ok(content.includes('colors.page'), 'Deve usar cor de página no mockup')
  assert.ok(content.includes('colors.surface'), 'Deve usar cor de superfície no mockup')
  assert.ok(content.includes('colors.text'), 'Deve usar cor de texto no mockup')
  assert.ok(content.includes('colors.accent'), 'Deve usar cor de acento no mockup')

  // Indicador de seleção ativa
  assert.ok(content.includes('is-active') || content.includes('is-selected'), 'Deve conter classe de tema ativo')

  // Navegação por teclado
  assert.ok(content.includes('Arrow') || content.includes('keydown'), 'Deve implementar navegação por teclado')

  // Ausência de emojis
  const emojiRegex = /[\u{1F300}-\u{1F9FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}]/u
  assert.ok(!emojiRegex.test(content), 'ThemePreviewGrid.vue não deve conter emojis')
})

test('US1: AppearanceControls integra ThemePreviewGrid para o campo theme', () => {
  const compPath = path.resolve(srcDir, 'components/AppearanceControls.vue')
  assert.ok(fs.existsSync(compPath), 'AppearanceControls.vue deve existir')

  const content = fs.readFileSync(compPath, 'utf-8')
  assert.ok(content.includes('ThemePreviewGrid'), 'AppearanceControls deve importar ou utilizar ThemePreviewGrid')
})

test('US2: AppearancePreview implementa bancada de leitura viva responsiva', () => {
  const compPath = path.resolve(srcDir, 'components/AppearancePreview.vue')
  assert.ok(fs.existsSync(compPath), 'AppearancePreview.vue deve existir')

  const content = fs.readFileSync(compPath, 'utf-8')
  assert.ok(content.includes('appearance-preview'), 'Deve conter contêiner appearance-preview')
  assert.ok(content.includes('preferences'), 'Deve receber e observar preferences')
})

test('US3: SettingsView estrutura layout moderno com menu lateral vertical de 5 seções', () => {
  const viewPath = path.resolve(srcDir, 'views/SettingsView.vue')
  assert.ok(fs.existsSync(viewPath), 'SettingsView.vue deve existir')

  const content = fs.readFileSync(viewPath, 'utf-8')

  // 5 seções de ajustes
  const expectedSections = ['perfil', 'aparencia', 'leitura', 'sistema', 'conta']
  for (const sec of expectedSections) {
    assert.ok(content.includes(`'${sec}'`) || content.includes(`"${sec}"`), `SettingsView deve conter a seção ${sec}`)
  }

  // Navegação vertical
  assert.ok(content.includes('settings-nav') || content.includes('settings-sidebar-nav'), 'Deve conter menu de navegação vertical')
  assert.ok(content.includes('route.query.tab') || content.includes('selectTab'), 'Deve sincronizar seção com query string da rota')
})

test('US4 & US5: SettingsView preserva validação defensiva de avatar (<= 2MB) e segurança da conta', () => {
  const viewPath = path.resolve(srcDir, 'views/SettingsView.vue')
  const content = fs.readFileSync(viewPath, 'utf-8')

  // Limite de 2MB no upload de avatar
  assert.ok(content.includes('2 * 1024 * 1024') || content.includes('2097152') || content.includes('2MB'), 'Deve validar tamanho máximo de 2MB para avatar')

  // Ausência de emojis
  const emojiRegex = /[\u{1F300}-\u{1F9FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}]/u
  assert.ok(!emojiRegex.test(content), 'SettingsView.vue não deve conter emojis')
})
