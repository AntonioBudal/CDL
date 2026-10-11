import test from 'node:test'
import assert from 'node:assert/strict'
import {
  formatCitationABNT,
  formatCitationMarkdown,
  formatCitationPlain,
} from '../src/utils/citationFormatter.ts'

test('T023 - citationFormatter: formatCitationABNT gera referência acadêmica completa', () => {
  const item = {
    selected_text: 'A leitura é um ato de criação partilhada entre o autor e o leitor.',
    book_title: 'Uma História da Leitura',
    book_author: 'Alberto Manguel',
    chapter_title: 'O Leitor Silencioso',
  }

  const result = formatCitationABNT(item)
  assert.equal(
    result,
    '"A leitura é um ato de criação partilhada entre o autor e o leitor." (ALBERTO MANGUEL, Uma História da Leitura, cap. O Leitor Silencioso).'
  )
})

test('T023 - citationFormatter: formatCitationABNT trata graciosamente campos ausentes', () => {
  const item = {
    selected_text: 'Texto sem autor nem capítulo.',
    book_title: 'Livro Anônimo',
    book_author: null,
    chapter_title: null,
  }

  const result = formatCitationABNT(item)
  assert.equal(result, '"Texto sem autor nem capítulo." (Livro Anônimo).')
})

test('T023 - citationFormatter: formatCitationMarkdown gera bloco de citação Markdown', () => {
  const item = {
    selected_text: 'O hábito da leitura acalma os ânimos e eleva o espírito.',
    book_title: 'Ensaios',
    book_author: 'Montaigne',
    chapter_title: 'Dos Livros',
  }

  const result = formatCitationMarkdown(item)
  assert.ok(result.startsWith('> O hábito da leitura acalma os ânimos e eleva o espírito.'))
  assert.ok(result.includes('— Montaigne, *Ensaios* (Dos Livros)'))
})

test('T023 - citationFormatter: formatCitationMarkdown trata ausência de autor e capítulo', () => {
  const item = {
    selected_text: 'Citação isolada.',
    book_title: 'Fragmentos',
    book_author: '',
    chapter_title: '',
  }

  const result = formatCitationMarkdown(item)
  assert.equal(result, '> Citação isolada.\n>\n— *Fragmentos*')
})

test('T023 - citationFormatter: formatCitationPlain gera texto puro legível', () => {
  const item = {
    selected_text: 'Passagem rápida.',
    book_title: 'Caderno',
    book_author: 'Autor',
    chapter_title: 'Capítulo 1',
  }

  const result = formatCitationPlain(item)
  assert.equal(result, '"Passagem rápida." — Autor - Caderno [Capítulo 1]')
})
