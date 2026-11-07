import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'
import {
  abntAuthorCall,
  formatCitationABNT,
  formatCitationMarkdown,
  formatReferenceABNT,
  parsePersonName,
  splitAuthors,
} from '../src/utils/citationFormatter.ts'

const srcDir = path.resolve(process.cwd(), 'src')
const read = (rel) => fs.readFileSync(path.resolve(srcDir, rel), 'utf-8')

const base = {
  selected_text: 'Trecho fictício de teste.',
  book_title: 'Livro de Teste',
  book_subtitle: '',
  book_author: 'Ana Fictícia',
  book_year: 2001,
  chapter_title: 'Capítulo 1',
}

// ---------- Chamada de autoria (NBR 10520:2023) ----------

test('098: sobrenome de "Nome Sobrenome" e de "Sobrenome, Nome"', () => {
  assert.equal(abntAuthorCall('Ana Fictícia'), 'Fictícia')
  assert.equal(abntAuthorCall('Fictícia, Ana'), 'Fictícia')
  assert.equal(parsePersonName('Fictícia, Ana Maria').given, 'Ana Maria')
})

test('098: sufixos Júnior, Filho, Neto e Sobrinho ficam com o sobrenome', () => {
  assert.equal(abntAuthorCall('Carlos Teste Júnior'), 'Teste Júnior')
  assert.equal(abntAuthorCall('Pedro Exemplo Filho'), 'Exemplo Filho')
  assert.equal(abntAuthorCall('João Modelo Neto'), 'Modelo Neto')
  assert.equal(abntAuthorCall('Rui Amostra Sobrinho'), 'Amostra Sobrinho')
})

test('098: autor de um nome só', () => {
  assert.equal(abntAuthorCall('Platão'), 'Platão')
})

test('098: dois ou três autores separados por ponto e vírgula; quatro ou mais com et al.', () => {
  assert.deepEqual(splitAuthors('Ana Fictícia; Bia Teste'), ['Ana Fictícia', 'Bia Teste'])
  assert.equal(abntAuthorCall('Ana Fictícia e Bia Teste'), 'Fictícia; Teste')
  assert.equal(abntAuthorCall('Ana Fictícia & Bia Teste and Caio Modelo'), 'Fictícia; Teste; Modelo')
  assert.equal(abntAuthorCall('A Um; B Dois; C Três; D Quatro'), 'Um et al.')
})

test('098: sem autor, entra pela primeira palavra do título com reticências', () => {
  assert.equal(abntAuthorCall('', 'Livro de Teste'), 'Livro...')
  assert.equal(abntAuthorCall(null, null), 'Obra...')
})

// ---------- Citação direta × indireta ----------

test('098: citação literal vira citação direta com aspas e chamada (Sobrenome, ano)', () => {
  assert.equal(
    formatCitationABNT(base, { literal: true }),
    '"Trecho fictício de teste." (Fictícia, 2001).'
  )
})

test('098: texto do leitor vira citação indireta, sem aspas e sem ponto duplicado', () => {
  assert.equal(formatCitationABNT(base), 'Trecho fictício de teste (Fictícia, 2001).')
  assert.equal(formatCitationABNT(base, { literal: false }), 'Trecho fictício de teste (Fictícia, 2001).')
})

test('098: aspas duplas internas viram simples; quebras de linha colapsam; sem ano vira [s. d.]', () => {
  const item = { ...base, selected_text: 'Ele disse "olá"\ne saiu', book_year: null }
  assert.equal(formatCitationABNT(item, { literal: true }), `"Ele disse 'olá' e saiu" (Fictícia, [s. d.]).`)
})

test('098: sem página no banco, a chamada não inventa p.', () => {
  assert.ok(!formatCitationABNT(base, { literal: true }).includes('p.'))
})

// ---------- Referência (NBR 6023) ----------

test('098: referência em texto e HTML com título em itálico e subtítulo', () => {
  const ref = formatReferenceABNT({ ...base, book_subtitle: 'um subtítulo' })
  assert.equal(ref.text, 'FICTÍCIA, Ana. Livro de Teste: um subtítulo. 2001.')
  assert.equal(ref.html, 'FICTÍCIA, Ana. <i>Livro de Teste</i>: um subtítulo. 2001.')
})

test('098: referência com vários autores, sem ano e sem autor', () => {
  assert.equal(
    formatReferenceABNT({ ...base, book_author: 'Ana Fictícia; Bia Teste', book_year: null }).text,
    'FICTÍCIA, Ana; TESTE, Bia. Livro de Teste. [s. d.].'
  )
  assert.equal(formatReferenceABNT({ ...base, book_author: '' }).text, 'LIVRO de Teste. 2001.')
})

test('098: referência escapa HTML do título', () => {
  const ref = formatReferenceABNT({ ...base, book_title: 'A <b> & C' })
  assert.ok(ref.html.includes('<i>A &lt;b&gt; &amp; C</i>'))
})

test('098: Markdown mantém as linhas com > e leva o ano', () => {
  const md = formatCitationMarkdown({ ...base, selected_text: 'Linha 1\nLinha 2' })
  assert.equal(md, '> Linha 1\n> Linha 2\n>\n— Ana Fictícia, *Livro de Teste* (2001), Capítulo 1')
})

// ---------- Cartão ----------

test('098: cartão separa citação literal (serifa, aspas) de texto do leitor (sans, sem aspas)', () => {
  const card = read('components/highlights/HighlightCard.vue')
  assert.match(card, /isLiteral = computed\(\(\) => props\.item\.kind === 'quote'\)/)
  assert.match(card, /v-if="isLiteral"[\s\S]*?literal-quote/)
  assert.match(card, /class="highlight-quote reader-excerpt"/)
  assert.match(card, /reader-excerpt-text/)
  for (const label of ['Do seu Resumo', 'Da sua Explicação', 'Dos seus Conceitos', 'Das suas Referências', 'Do fichamento importado']) {
    assert.ok(card.includes(label), `rótulo de origem: ${label}`)
  }
  // o bloco do texto do leitor não tem aspas decorativas
  const readerBlock = card.slice(card.indexOf('class="highlight-quote reader-excerpt"'), card.indexOf('<!-- Área de Anotação'))
  assert.ok(!readerBlock.includes('editorial-quote-mark'))
})

test('098: controle "Citação literal" só para Destaque, Anotação e Citação, com aria-pressed', () => {
  const card = read('components/highlights/HighlightCard.vue')
  assert.match(card, /LITERAL_TOGGLE_KINDS: HighlightKind\[\] = \['highlight', 'note', 'quote'\]/)
  assert.match(card, /v-if="canToggleLiteral"/)
  assert.match(card, /:aria-pressed="isLiteral"/)
  assert.match(card, /'toggle-literal'/)
})

test('098: cópia usa a citação certa, a referência com HTML e o menu acessível', () => {
  const card = read('components/highlights/HighlightCard.vue')
  assert.match(card, /formatCitationABNT\(props\.item, \{ literal: isLiteral\.value \}\)/)
  assert.match(card, /formatReferenceABNT\(props\.item\)/)
  assert.match(card, /copyRich\(text, html\)/)
  assert.ok(card.includes('Referência (NBR 6023)'))
  assert.match(card, /event\.key === 'Escape'/)
  assert.match(card, /addEventListener\('pointerdown'/)
  assert.match(card, /copyTriggerRef\.value\?\.focus\(\)/)
  assert.match(card, /aria-live="polite"/)
})

test('098: controles secundários do cartão usam .quiet; Salvar e Confirmar mantêm o destaque', () => {
  const card = read('components/highlights/HighlightCard.vue')
  for (const cls of [
    'btn-copy-quote quiet',
    'btn-copy-dropdown-trigger quiet',
    'copy-menu-item quiet',
    'btn-literal-toggle quiet',
    'btn-edit-note-inline quiet',
    'btn-add-note-inline quiet',
    'btn-cancel quiet',
    'btn-delete quiet',
    'btn-cancel-delete quiet',
  ]) {
    assert.ok(card.includes(cls), `${cls}`)
  }
  assert.ok(!/btn-save[^"]*quiet/.test(card))
  assert.ok(!/btn-confirm-delete[^"]*quiet/.test(card))
})

test('098: biblioteca grava o tipo com reversão em erro e ajusta o resumo', () => {
  const view = read('views/HighlightsLibraryView.vue')
  assert.match(view, /updateStudyHighlight\(studyId, id, \{ kind: nextKind \}\)/)
  assert.match(view, /target\.kind = previousKind/)
  assert.equal((view.match(/@toggle-literal="handleToggleLiteral"/g) || []).length, 2)
})

test('098: tipo da biblioteca tem ano e subtítulo do livro', () => {
  const types = read('types.ts')
  assert.match(types, /book_year\?: number \| null/)
  assert.match(types, /book_subtitle\?: string/)
})
