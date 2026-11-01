import test from 'node:test'
import assert from 'node:assert/strict'

// F0.10.02 — o bootstrap de aparência deixa de ser inline no build, para a CSP não precisar de 'unsafe-inline'.
const { default: config } = await import('../vite.config.ts')
const plugin = config.plugins.find((p) => p && p.name === 'appearance-before-paint')
const HTML = '<html><head><!-- appearance-bootstrap --></head><body><script id="schema-json-ld" type="application/ld+json">{}</script></body></html>'

// <script> executáveis inline: sem src e sem type de dados (application/ld+json não executa).
function inlineExecutableScripts(html) {
  return [...html.matchAll(/<script\b([^>]*)>/g)].filter(([, attrs]) => !/\bsrc=/.test(attrs) && !/type="application\/ld\+json"/.test(attrs))
}

test('no build, o marcador vira <script src> e não sobra script executável inline', () => {
  const out = plugin.transformIndexHtml.handler(HTML, {})
  assert.match(out, /<script src="\/appearance-bootstrap\.js"><\/script>/)
  assert.doesNotMatch(out, /<script src="\/appearance-bootstrap\.js"[^>]*\b(defer|async|type=)/, 'Script clássico e bloqueante, antes da pintura')
  assert.deepEqual(inlineExecutableScripts(out), [])
})

test('no servidor de desenvolvimento, o bootstrap continua inline', () => {
  const out = plugin.transformIndexHtml.handler(HTML, { server: {} })
  assert.match(out, /<script>window\.cadernoFontCatalog=/)
})

test('o build emite appearance-bootstrap.js com o catálogo de fontes e o código', () => {
  const emitted = []
  plugin.generateBundle.call({ emitFile: (file) => emitted.push(file) })
  assert.equal(emitted.length, 1)
  assert.equal(emitted[0].type, 'asset')
  assert.equal(emitted[0].fileName, 'appearance-bootstrap.js')
  assert.match(emitted[0].source, /^window\.cadernoFontCatalog=\{/)
  assert.match(emitted[0].source, /factoryReset/)
  assert.doesNotMatch(emitted[0].source, /<\/script/i)
})
