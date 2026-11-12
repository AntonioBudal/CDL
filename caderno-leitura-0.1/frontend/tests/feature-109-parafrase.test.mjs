import './helpers/normalize-eol.mjs'
import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'
import {
  abntQuoteCall,
  buildSourceIndex,
  checkParaphrase,
  jaccard,
  longestCommonRun,
  markAsQuote,
  normalizeWords,
  splitSentences,
  stripMarkdown,
  trigrams,
} from '../src/utils/paraphraseCheck.ts'

const srcDir = path.resolve(process.cwd(), 'src')
const read = (rel) => fs.readFileSync(path.resolve(srcDir, rel), 'utf-8')

const FONTE = [
  'O herói trágico cai por causa de um erro de julgamento e não por maldade ou vício.',
  'A plateia sente piedade porque o sofrimento é imerecido e sente temor porque o herói é semelhante a ela.',
  'Por isso a tragédia produz a purificação dessas emoções no espectador comum.',
].join(' ')

const index = () => buildSourceIndex([{ label: 'Fichamento da fonte', text: FONTE }])

test('109: normalização, frases, trigramas e medidas', () => {
  assert.deepEqual(normalizeWords('Ação, É  já!'), ['acao', 'e', 'ja'])
  assert.deepEqual(splitSentences('Primeira frase. Segunda "com ponto. dentro" aqui!\n> citação em bloco.\nTerceira'),
    ['Primeira frase.', 'Segunda "com ponto. dentro" aqui!', 'Terceira'])
  assert.equal(stripMarkdown('- **Termo** em [[conceito:Mímese]] e [[Estudo|3]] e [link](http://x.invalid)'),
    'Termo em Mímese e Estudo e link')
  assert.equal(trigrams(['a', 'b', 'c', 'd']).size, 2)
  assert.equal(jaccard(new Set(['x', 'y']), new Set(['y', 'z'])), 1 / 3)
  assert.equal(longestCommonRun(['a', 'b', 'c', 'x'], ['z', 'a', 'b', 'c']), 3)
})

test('109: cópia, troca de poucas palavras e paráfrase real', () => {
  const r = checkParaphrase({
    summary: 'O herói trágico cai por causa de um erro de julgamento e não por maldade ou vício.',
    explanation: 'A plateia sente piedade porque a dor é imerecida e sente temor porque o herói é parecido com ela.',
    concepts: 'Quem assiste se reconhece no protagonista e por isso teme que o mesmo destino o alcance um dia.',
  }, index())
  assert.equal(r.total, 3)
  assert.deepEqual(r.flagged.map((f) => [f.section, f.level]), [['summary', 'copy'], ['explanation', 'close']])
  assert.equal(r.copies, 1)
  assert.equal(r.flagged[0].score, 1)
  assert.equal(r.flagged[0].sourceLabel, 'Fichamento da fonte')
  assert.ok(r.flagged[0].sourceParts.some((p) => p.shared && p.text.includes('herói trágico')))
  assert.ok(r.flagged[1].score >= 0.25 && r.flagged[1].score < 0.5, String(r.flagged[1].score))
})

test('109: citação declarada, frase curta e sequência longa', () => {
  const r = checkParaphrase({
    summary: [
      '"O herói trágico cai por causa de um erro de julgamento e não por maldade ou vício." (FICTÍCIA, 2020, p. 3).',
      '> A plateia sente piedade porque o sofrimento é imerecido e sente temor.',
      'O herói trágico cai.',
      'Segundo a autora, em tom bem pessoal e com muitas palavras minhas antes, a plateia sente piedade porque o sofrimento é imerecido e sente temor porque o herói é semelhante, o que eu discuto longamente adiante com outros exemplos e muitos comentários próprios sobre o caso.',
    ].join('\n'),
  }, index())
  assert.equal(r.total, 1, 'aspas, bloco > e frase curta ficam de fora')
  assert.equal(r.flagged.length, 1)
  assert.equal(r.flagged[0].level, 'copy')
  assert.ok(r.flagged[0].run >= 12 && r.flagged[0].score < 0.5)
})

test('109: trecho marcado como citação literal no estudo não é verificado', () => {
  const sentence = 'O herói trágico cai por causa de um erro de julgamento e não por maldade ou vício.'
  const declared = [{ section: 'summary', text: 'erro de julgamento e não por **maldade**' }]
  const r = checkParaphrase({ summary: sentence, explanation: sentence }, index(), declared)
  assert.deepEqual(r.flagged.map((f) => f.section), ['explanation'], 'só vale para a seção marcada')
  assert.equal(r.total, 1)
  assert.equal(checkParaphrase({ summary: sentence }, index(), [{ section: 'summary', text: 'o' }]).flagged.length, 1,
    'trecho curto demais não esconde a frase')
})

test('109: sem fonte não sinaliza nada', () => {
  const r = checkParaphrase({ summary: 'O herói trágico cai por causa de um erro de julgamento e não por maldade.' },
    buildSourceIndex([]))
  assert.deepEqual(r, { flagged: [], total: 1, copies: 0 })
})

test('109: fonte grande em tempo razoável', () => {
  const vocab = Array.from({ length: 3000 }, (_, i) => `palavra${i}`)
  let seed = 7
  const rnd = () => { seed = (seed * 1103515245 + 12345) % 2147483648; return seed / 2147483648 }
  const sentences = []
  for (let i = 0; i < 10000; i += 1) {
    sentences.push(Array.from({ length: 20 }, () => vocab[Math.floor(rnd() * vocab.length)]).join(' ') + '.')
  }
  const target = sentences[5000]
  const t0 = performance.now()
  const big = buildSourceIndex([{ label: 'Fichamento da fonte', text: sentences.join(' ') }])
  const t1 = performance.now()
  const summary = Array.from({ length: 40 }, (_, i) => (i === 20 ? target : `Frase própria número ${i} sem relação nenhuma com a fonte.`)).join(' ')
  const r = checkParaphrase({ summary }, big)
  const t2 = performance.now()
  assert.equal(r.copies, 1)
  assert.ok(t1 - t0 < 3000, `índice ${Math.round(t1 - t0)} ms`)
  assert.ok(t2 - t1 < 300, `verificação ${Math.round(t2 - t1)} ms`)
})

test('109: marcar como citação', () => {
  const call = abntQuoteCall('Ana Fictícia', 2020)
  assert.equal(call, '(FICTÍCIA, 2020, p. )')
  assert.equal(abntQuoteCall('Ana Fictícia', null), '(FICTÍCIA, [s. d.], p. )')
  const text = 'Antes.\n- O herói cai por um "erro" de julgamento.\nDepois.'
  assert.equal(markAsQuote(text, '- O herói cai por um "erro" de julgamento.', call),
    "Antes.\n- “O herói cai por um 'erro' de julgamento” (FICTÍCIA, 2020, p. ).\nDepois.")
  assert.equal(markAsQuote(text, 'Frase que não existe.', call), null)
})

test('109: painel nas telas de edição e importação; API', () => {
  const panel = read('components/studies/ParaphrasePanel.vue')
  assert.match(panel, /checkParaphrase\(/)
  assert.match(panel, /aria-live="polite"/)
  assert.match(panel, /Marcar como citação/)
  assert.match(panel, /Nenhuma frase muito próxima da fonte\./)
  assert.match(read('views/StudyEditView.vue'), /<ParaphrasePanel/)
  assert.match(read('views/ImportView.vue'), /<ParaphrasePanel/)
  assert.doesNotMatch(read('views/ImportView.vue'), /local-source/, 'o fichamento não é fonte')
  assert.match(panel, /checkParaphrase\(sections\.value, index\.value, declared\.value\)/)
  const api = read('services/api.ts')
  assert.match(api, /\/studies\/\$\{studyId\}\/paraphrase-sources/)
  assert.match(api, /\/chapters\/\$\{chapterId\}\/paraphrase-sources/)
})
