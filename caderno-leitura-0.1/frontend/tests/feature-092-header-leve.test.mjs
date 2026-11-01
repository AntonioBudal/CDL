import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

// F0.10.01 — a regra global de <button> em appearance-advanced.css pinta todo botão com o destaque; os controles
// secundários do header e das páginas de livros usam a variante .quiet para voltar a ser neutros.
const srcDir = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../src')
const read = (rel) => fs.readFileSync(path.join(srcDir, rel), 'utf-8')

// Atributo class de cada <button> que contém a classe indicada (estática ou ligada).
function buttonClasses(source, marker) {
  const out = []
  const re = /<button\b[\s\S]*?>/g
  let m
  while ((m = re.exec(source)) !== null) {
    const tag = m[0]
    if (!tag.includes(marker)) continue
    const stat = tag.match(/\sclass="([^"]*)"/)
    const bound = tag.match(/\s:class="([^"]*)"/)
    out.push(`${stat ? stat[1] : ''} ${bound ? bound[1] : ''}`)
  }
  return out
}

test('1. appearance-advanced.css define .quiet depois de todas as regras globais de botão', () => {
  const css = read('appearance-advanced.css')
  const base = css.indexOf(":root :is(button, .button).quiet:not([role='tab']):not(.group-toggle-btn) {")
  const hover = css.indexOf(":root :is(button, .button).quiet:not([role='tab']):not(.group-toggle-btn):hover:not(:disabled) {")
  const disabled = css.indexOf(":root :is(button, .button).quiet:not([role='tab']):not(.group-toggle-btn):disabled {")
  assert.ok(base > 0 && hover > 0 && disabled > 0, 'As 3 regras .quiet (base, hover, disabled) devem existir')

  // A especificidade empata com outline/ghost/block; a variante só vence se vier depois delas.
  for (const marker of [
    "[data-button-style='outline'] :is(button",
    "[data-button-style='ghost'] :is(button",
    "[data-button-width='block'] :is(button",
    '.secondary:not',
  ]) {
    assert.ok(css.lastIndexOf(marker) < base, `.quiet deve vir depois de ${marker}`)
  }

  const body = css.slice(base, css.indexOf('}', base))
  assert.match(body, /--button-bg:\s*var\(--quiet-bg,\s*transparent\)/)
  assert.match(body, /--button-fg:\s*var\(--color-text\)/)
  assert.match(body, /--button-border:\s*var\(--quiet-border,\s*transparent\)/)
  assert.match(body, /--button-hover-fg:\s*var\(--color-hover-text/)
  assert.match(body, /width:\s*auto/)
})

test('2. Controles secundários do header e das páginas de livros usam .quiet', () => {
  const cases = [
    ['components/layout/GlobalHeader.vue', 'search-trigger-btn', 1],
    ['components/layout/GlobalHeader.vue', 'btn-notifications-trigger', 1],
    ['components/layout/NavigationTabs.vue', 'more-trigger-btn', 1],
    ['components/sync/SyncStatusBadge.vue', 'sync-status-badge', 1],
    ['components/layout/UserDropdown.vue', 'user-trigger-btn', 1],
    ['components/layout/MobileTabBar.vue', 'mobile-more-trigger', 1],
    ['views/BookView.vue', 'pill-tool-btn', 3],
    ['components/LibraryToolbar.vue', 'search-clear-btn', 1],
    ['components/LibraryToolbar.vue', 'category-clear-btn', 1],
    ['components/LibraryToolbar.vue', 'clear-filters-btn', 1],
  ]
  for (const [file, marker, count] of cases) {
    const classes = buttonClasses(read(file), marker)
    assert.equal(classes.length, count, `${file}: esperava ${count} botão(ões) ${marker}`)
    for (const c of classes) assert.match(c, /\bquiet\b/, `${file}: ${marker} deve ter a classe quiet`)
  }
})

test('3. "Capturar" continua como a única ação com destaque no header', () => {
  const classes = buttonClasses(read('components/layout/GlobalHeader.vue'), 'quick-capture-trigger-btn')
  assert.equal(classes.length, 1)
  assert.doesNotMatch(classes[0], /\bquiet\b/, 'Capturar não pode receber .quiet')
})

test('4. Na estante, só o modo de visualização não selecionado fica neutro', () => {
  const classes = buttonClasses(read('components/LibraryToolbar.vue'), 'view-mode-btn')
  assert.equal(classes.length, 2)
  assert.ok(classes.some((c) => /quiet:\s*viewMode !== 'grid'/.test(c)), 'Grade: quiet quando não selecionado')
  assert.ok(classes.some((c) => /quiet:\s*viewMode !== 'list'/.test(c)), 'Lista: quiet quando não selecionado')
})

test('5. Os estilos tocados não trazem hex de fallback', () => {
  const sync = read('components/sync/SyncStatusBadge.vue')
  assert.doesNotMatch(sync, /#b45309|#dc2626/, 'SyncStatusBadge: sem hex de fallback nas cores de estado')
  const toolbar = read('components/LibraryToolbar.vue')
  assert.doesNotMatch(toolbar, /var\(--muted|var\(--text,|var\(--bg-hover/, 'LibraryToolbar: só tokens reais')
  assert.doesNotMatch(toolbar, /#3b82f6|#888\b|#111\b/, 'LibraryToolbar: sem hex de fallback')
})
