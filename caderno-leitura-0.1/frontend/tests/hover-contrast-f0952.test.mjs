import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)
const srcDir = path.resolve(__dirname, '../src')

// Helper para converter hex em luminância relativa (WCAG 2.1)
function hexToLuminance(hex) {
  const cleanHex = hex.replace('#', '').trim()
  const r = parseInt(cleanHex.substring(0, 2), 16) / 255
  const g = parseInt(cleanHex.substring(2, 4), 16) / 255
  const b = parseInt(cleanHex.substring(4, 6), 16) / 255

  const toLinear = (c) => (c <= 0.04045 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4))
  return 0.2126 * toLinear(r) + 0.7152 * toLinear(g) + 0.0722 * toLinear(b)
}

function getContrastRatio(hex1, hex2) {
  const l1 = hexToLuminance(hex1)
  const l2 = hexToLuminance(hex2)
  const lighter = Math.max(l1, l2)
  const darker = Math.min(l1, l2)
  return (lighter + 0.05) / (darker + 0.05)
}

const CANONICAL_THEMES = [
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

test('palettes.css define tokens de contraste para hover em todos os 10 temas', () => {
  const palettesContent = fs.readFileSync(path.join(srcDir, 'palettes.css'), 'utf8')

  for (const theme of CANONICAL_THEMES) {
    const themeRegex = theme === 'papel-fosco'
      ? /:root,\s*:root\[data-theme="papel-fosco"\]\s*\{([\s\S]*?)\}/
      : new RegExp(`:root\\[data-theme="${theme}"\\]\\s*\\{([\\s\\S]*?)\\}`)

    const match = palettesContent.match(themeRegex)
    assert.ok(match, `Tema ${theme} deve ter bloco de regras em palettes.css`)

    const block = match[1]
    assert.ok(block.includes('--color-hover-text:'), `Tema ${theme} deve definir --color-hover-text`)
    assert.ok(block.includes('--color-tab-hover-text:'), `Tema ${theme} deve definir --color-tab-hover-text`)
    assert.ok(block.includes('--color-accent-hover-text:'), `Tema ${theme} deve definir --color-accent-hover-text`)
  }
})

test('Contraste WCAG: todo hover possui contraste satisfatório (>= 4.5:1)', () => {
  const palettesContent = fs.readFileSync(path.join(srcDir, 'palettes.css'), 'utf8')

  function extractToken(block, token) {
    const regex = new RegExp(`${token}:\\s*(#[0-9a-fA-F]{6})`)
    const match = block.match(regex)
    return match ? match[1] : null
  }

  for (const theme of CANONICAL_THEMES) {
    const themeRegex = theme === 'papel-fosco'
      ? /:root,\s*:root\[data-theme="papel-fosco"\]\s*\{([\s\S]*?)\}/
      : new RegExp(`:root\\[data-theme="${theme}"\\]\\s*\\{([\\s\\S]*?)\\}`)

    const match = palettesContent.match(themeRegex)
    const block = match[1]

    const surfaceHover = extractToken(block, '--color-surface-hover')
    const hoverText = extractToken(block, '--color-hover-text')
    const tabHover = extractToken(block, '--color-tab-hover')
    const tabHoverText = extractToken(block, '--color-tab-hover-text')
    const accentHover = extractToken(block, '--color-accent-hover')
    const accentHoverText = extractToken(block, '--color-accent-hover-text')

    assert.ok(surfaceHover && hoverText, `Tema ${theme} deve ter surface-hover e hover-text válidos`)
    assert.ok(tabHover && tabHoverText, `Tema ${theme} deve ter tab-hover e tab-hover-text válidos`)
    assert.ok(accentHover && accentHoverText, `Tema ${theme} deve ter accent-hover e accent-hover-text válidos`)

    const surfaceRatio = getContrastRatio(surfaceHover, hoverText)
    const tabRatio = getContrastRatio(tabHover, tabHoverText)
    const accentRatio = getContrastRatio(accentHover, accentHoverText)

    assert.ok(
      surfaceRatio >= 4.5,
      `Tema ${theme}: contraste da superfície no hover (${surfaceHover} x ${hoverText}) deve ser >= 4.5:1 (atual: ${surfaceRatio.toFixed(2)})`
    )
    assert.ok(
      tabRatio >= 4.5,
      `Tema ${theme}: contraste de abas no hover (${tabHover} x ${tabHoverText}) deve ser >= 4.5:1 (atual: ${tabRatio.toFixed(2)})`
    )
    assert.ok(
      accentRatio >= 4.5,
      `Tema ${theme}: contraste de destaque no hover (${accentHover} x ${accentHoverText}) deve ser >= 4.5:1 (atual: ${accentRatio.toFixed(2)})`
    )

    // Regra explícita do usuário: fundo escuro -> texto claro; fundo claro -> texto escuro
    const surfaceLuminance = hexToLuminance(surfaceHover)
    const hoverTextLuminance = hexToLuminance(hoverText)
    if (surfaceLuminance < 0.4) {
      assert.ok(
        hoverTextLuminance > 0.5,
        `Tema ${theme}: fundo de hover escuro (${surfaceHover}) deve ter texto claro (atual: ${hoverText})`
      )
    } else {
      assert.ok(
        hoverTextLuminance < 0.4,
        `Tema ${theme}: fundo de hover claro (${surfaceHover}) deve ter texto escuro (atual: ${hoverText})`
      )
    }
  }
})

test('GroupSection.vue atualiza títulos, ícones e contadores no hover', () => {
  const groupContent = fs.readFileSync(path.join(srcDir, 'components/views/GroupSection.vue'), 'utf8')

  assert.ok(groupContent.includes('.group-toggle-btn:hover'), 'Deve conter regra .group-toggle-btn:hover')
  assert.ok(groupContent.includes('var(--color-hover-text)'), 'Deve usar --color-hover-text no hover')
  assert.ok(groupContent.includes('.group-toggle-btn:hover .group-title'), 'Deve estilizar título no hover')
  assert.ok(groupContent.includes('.group-toggle-btn:hover .group-chevron-wrap'), 'Deve estilizar chevron no hover')
  assert.ok(groupContent.includes('.group-toggle-btn:hover .group-count-badge'), 'Deve estilizar contador no hover')
})

test('StudyGridView.vue e StudyListView.vue possuem contraste adaptativo no hover', () => {
  const gridContent = fs.readFileSync(path.join(srcDir, 'components/views/StudyGridView.vue'), 'utf8')
  const listContent = fs.readFileSync(path.join(srcDir, 'components/views/StudyListView.vue'), 'utf8')

  assert.ok(gridContent.includes('.study-card:hover'), 'StudyGridView deve ter hover no card')
  assert.ok(gridContent.includes('var(--color-surface-hover)'), 'StudyGridView card deve ter surface-hover')
  assert.ok(gridContent.includes('.study-card:hover .card-title-link'), 'Título do card deve se adaptar no hover')

  assert.ok(listContent.includes('.study-row-item:hover'), 'StudyListView deve ter hover na linha')
  assert.ok(listContent.includes('.study-row-item:hover .row-title-link'), 'Título da linha deve se adaptar no hover')
  assert.ok(listContent.includes('.study-row-item:hover .location-tag'), 'Tag de localização deve se adaptar no hover')
  assert.ok(listContent.includes('.study-row-item:hover .row-date'), 'Data da linha deve se adaptar no hover')
  assert.ok(listContent.includes('color: var(--color-text'), 'Link do título na lista deve usar --color-text')
})

test('FriendsView.vue e SettingsView.vue aplicam contraste nas abas e opções', () => {
  const friendsContent = fs.readFileSync(path.join(srcDir, 'views/FriendsView.vue'), 'utf8')
  const settingsContent = fs.readFileSync(path.join(srcDir, 'views/SettingsView.vue'), 'utf8')
  const mobileNavContent = fs.readFileSync(path.join(srcDir, 'mobile-navigation.css'), 'utf8')

  assert.ok(friendsContent.includes('.tab-btn:hover'), 'FriendsView deve ter hover nas abas')
  assert.ok(friendsContent.includes('var(--color-tab-hover)'), 'FriendsView deve usar --color-tab-hover')
  assert.ok(friendsContent.includes('var(--color-tab-hover-text)'), 'FriendsView deve usar --color-tab-hover-text')

  assert.ok(settingsContent.includes('.radio-option:hover'), 'SettingsView deve ter hover nos radio options')
  assert.ok(settingsContent.includes('.checkbox-option:hover'), 'SettingsView deve ter hover nos checkbox options')
  assert.ok(settingsContent.includes('var(--color-hover-text)'), 'SettingsView deve usar --color-hover-text nos options')

  assert.ok(mobileNavContent.includes('.settings-tab:hover'), 'mobile-navigation.css deve ter hover em .settings-tab')
  assert.ok(mobileNavContent.includes('var(--color-tab-hover-text)'), 'mobile-navigation.css deve usar --color-tab-hover-text')
})
