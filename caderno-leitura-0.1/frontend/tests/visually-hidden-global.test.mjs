import './helpers/normalize-eol.mjs'
import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'

// Correção de 2026-11-15: a classe era usada sem definição em algumas telas e o texto para leitor de tela aparecia.
test('classe visually-hidden definida globalmente', () => {
  const css = fs.readFileSync(path.resolve(process.cwd(), 'src', 'style.css'), 'utf-8')
  assert.match(css, /\.visually-hidden \{\s*position: absolute !important;[\s\S]*clip: rect\(0, 0, 0, 0\);/)
})
