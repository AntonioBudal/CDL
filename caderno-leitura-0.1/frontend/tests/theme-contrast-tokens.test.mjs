import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'

// Contraste mínimo (WCAG AA, 4,5:1) dos pares de texto dos 10 temas, calculado direto do palettes.css.
// Origem: conferência visual das features 086 e 089 (Grafite e Noite Suave reprovavam em texto secundário, link e
// mensagem de erro).

const css = fs.readFileSync(path.resolve(process.cwd(), 'src/palettes.css'), 'utf-8')
const themes = [...css.matchAll(/:root\[data-theme="([\w-]+)"\]\s*\{([\s\S]*?)\}/g)].map(([, name, body]) => ({
  name,
  vars: Object.fromEntries([...body.matchAll(/(--[\w-]+):\s*(#[0-9a-fA-F]{3,6})/g)].map(([, k, v]) => [k, v])),
}))

function luminance(hex) {
  let h = hex.slice(1)
  if (h.length === 3) h = [...h].map(c => c + c).join('')
  const [r, g, b] = [0, 2, 4].map(i => parseInt(h.slice(i, i + 2), 16) / 255)
    .map(v => (v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4))
  return 0.2126 * r + 0.7152 * g + 0.0722 * b
}

function ratio(a, b) {
  const [la, lb] = [luminance(a), luminance(b)]
  return (Math.max(la, lb) + 0.05) / (Math.min(la, lb) + 0.05)
}

test('os 10 temas estão no palettes.css', () => {
  assert.deepEqual(themes.map(t => t.name).sort(), [
    'cinza-neutro', 'e-ink', 'fiorde', 'grafite', 'monocromatico', 'noite-suave', 'papel-fosco', 'pergaminho', 'solario', 'voltagem',
  ])
})

test('texto secundário, link, erro e texto sobre o destaque têm contraste mínimo de 4,5:1 em todos os temas', () => {
  const failures = []
  for (const { name, vars } of themes) {
    const link = vars['--color-link'] ?? vars['--color-accent']
    const pairs = {
      'texto secundário sobre superfície': [vars['--color-muted'], vars['--color-surface']],
      'texto secundário sobre página': [vars['--color-muted'], vars['--color-page']],
      'link sobre superfície': [link, vars['--color-surface']],
      'link sobre página': [link, vars['--color-page']],
      'mensagem de erro': [vars['--color-error-text'], vars['--color-error-bg']],
      'texto sobre o destaque': [vars['--color-on-accent'], vars['--color-accent']],
    }
    for (const [label, [fg, bg]] of Object.entries(pairs)) {
      const value = ratio(fg, bg)
      if (value < 4.5) failures.push(`${name}: ${label} ${value.toFixed(2)}`)
    }
  }
  assert.deepEqual(failures, [])
})

test('Grafite e Noite Suave: link sobre fundos de selo e aba e texto sutil passam de 4,5:1 (revisão das outras telas)', () => {
  const failures = []
  for (const { name, vars } of themes.filter(t => ['grafite', 'noite-suave'].includes(t.name))) {
    const pairs = {
      'link sobre superfície suave': [vars['--color-link'], vars['--color-surface-soft']],
      'link sobre seleção': [vars['--color-link'], vars['--color-selected-bg']],
      'texto sutil sobre superfície': [vars['--color-subtle'], vars['--color-surface']],
      'texto sutil sobre superfície suave': [vars['--color-subtle'], vars['--color-surface-soft']],
      'texto sutil sobre página': [vars['--color-subtle'], vars['--color-page']],
      'aviso': [vars['--color-warning-text'], vars['--color-warning-bg']],
    }
    for (const [label, [fg, bg]] of Object.entries(pairs)) {
      const value = ratio(fg, bg)
      if (value < 4.5) failures.push(`${name}: ${label} ${value.toFixed(2)}`)
    }
  }
  assert.deepEqual(failures, [])
})

test('Papel Fosco, Cinza Neutro, Pergaminho e Solarized: texto sutil, link, sucesso e selos de status passam de 4,5:1 sobre os fundos', () => {
  const failures = []
  const status = ['rascunho', 'estudo', 'revisado', 'concluido'].map(s => `--color-status-${s}-text`)
  for (const { name, vars } of themes.filter(t => ['papel-fosco', 'cinza-neutro', 'pergaminho', 'solario'].includes(t.name))) {
    const link = vars['--color-link'] ?? vars['--color-accent']
    for (const bg of ['--color-page', '--color-surface', '--color-surface-soft', '--color-surface-inset', '--color-selected-bg']) {
      const pairs = { 'texto sutil': vars['--color-subtle'], link, sucesso: vars['--color-success-text'] }
      for (const s of status) pairs[s.slice(8)] = vars[s]
      for (const [label, fg] of Object.entries(pairs)) {
        const value = ratio(fg, vars[bg])
        if (value < 4.5 && !(label === 'texto sutil' && bg === '--color-selected-bg')) failures.push(`${name}: ${label} sobre ${bg} ${value.toFixed(2)}`)
      }
    }
  }
  assert.deepEqual(failures, [])
})

test('E-Ink e Monocromático: o texto passa de 4,5:1 sobre os fundos de hover e os tons suaves, e a seleção usa o texto de seleção', () => {
  const failures = []
  for (const { name, vars } of themes.filter(t => ['e-ink', 'monocromatico'].includes(t.name))) {
    const link = vars['--color-link'] ?? vars['--color-accent']
    const texts = { texto: vars['--color-text'], secundário: vars['--color-muted'], sutil: vars['--color-subtle'], link, hover: vars['--color-hover-text'], 'hover de aba': vars['--color-tab-hover-text'] }
    // Esses fundos recebem texto comum em muitos componentes, que trocam o fundo no hover sem trocar a cor do texto.
    for (const bg of ['--color-surface-hover', '--color-tab-hover', '--color-card-hover', '--color-primary-subtle', '--color-accent-subtle', '--accent-subtle']) {
      for (const [label, fg] of Object.entries(texts)) {
        const value = ratio(fg, vars[bg])
        if (value < 4.5) failures.push(`${name}: ${label} sobre ${bg} ${value.toFixed(2)}`)
      }
    }
    const selected = ratio(vars['--color-selected-text'], vars['--color-selected-bg'])
    if (selected < 4.5) failures.push(`${name}: seleção ${selected.toFixed(2)}`)
  }
  assert.deepEqual(failures, [])
})

test('regra com o fundo de seleção usa o texto de seleção (no E-Ink e no Monocromático a seleção é preta)', () => {
  const offenders = []
  const walk = dir => {
    for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
      const full = path.join(dir, entry.name)
      if (entry.isDirectory()) walk(full)
      else if (/\.(css|vue)$/.test(entry.name)) {
        const content = fs.readFileSync(full, 'utf-8').replace(/\/\*[\s\S]*?\*\//g, '')
        for (const [, selector, body] of content.matchAll(/([^{}]+)\{([^{}]*)\}/g)) {
          if (!/(?:^|[;\s{])background(?:-color)?:\s*var\(--color-selected-bg\b/.test(body)) continue
          const color = body.match(/(?:^|[;\s{])color:\s*([^;]+);/)
          if (!color || !/selected-text|on-accent/.test(color[1])) offenders.push(`${path.relative(process.cwd(), full)}: ${selector.trim().split('\n').pop()}`)
        }
      }
    }
  }
  walk(path.resolve(process.cwd(), 'src'))
  assert.deepEqual(offenders, [])
  const book = fs.readFileSync(path.resolve(process.cwd(), 'src/views/BookView.vue'), 'utf-8')
  assert.match(book, /\.chapter-pill\.selected \.chapter-pill-num \{\s*color: var\(--color-selected-text\);/)
})

test('E-Ink: o hover sublinha em vez de inverter, e as capas geradas têm fundo preto', () => {
  const themesCss = fs.readFileSync(path.resolve(process.cwd(), 'src/themes.css'), 'utf-8')
  assert.match(themesCss, /:root\[data-theme='e-ink'\] :is\(a, button, \[role='tab'\], \[role='button'\], summary\):hover:not\(:disabled\) \{\s*text-decoration: underline;/)
  assert.match(themesCss, /:root\[data-theme='e-ink'\] \.book-cover-placeholder \{\s*background-color: #000000 !important;/)
})

test('nenhuma regra usa a cor de destaque (ou os apelidos --color-primary e --accent) como cor de texto: o texto usa --color-link', () => {
  const offenders = []
  const walk = dir => {
    for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
      const full = path.join(dir, entry.name)
      if (entry.isDirectory()) walk(full)
      else if (/\.(css|vue)$/.test(entry.name)) {
        const content = fs.readFileSync(full, 'utf-8')
        if (/(?<![-\w])color:\s*var\(--(?:color-accent|color-primary|accent)\s*[,)]/.test(content)) offenders.push(path.relative(process.cwd(), full))
      }
    }
  }
  walk(path.resolve(process.cwd(), 'src'))
  assert.deepEqual(offenders, [])
})

test('o link usa o token próprio, e a tela de digitalização dá 44 px aos links das ações', () => {
  const style = fs.readFileSync(path.resolve(process.cwd(), 'src/style.css'), 'utf-8')
  assert.match(style, /\.text-link \{ color: var\(--color-link\);/)
  const tokens = fs.readFileSync(path.resolve(process.cwd(), 'src/tokens.css'), 'utf-8')
  assert.match(tokens, /--color-link: var\(--color-accent\);/)
  const view = fs.readFileSync(path.resolve(process.cwd(), 'src/views/DigitizeNotebookView.vue'), 'utf-8')
  assert.match(view, /\.exit-card \.text-link,\n\.actions \.text-link \{\n {2}display: inline-flex;\n {2}align-items: center;\n {2}min-height: 44px;/)
})
