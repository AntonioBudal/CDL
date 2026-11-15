import './helpers/normalize-eol.mjs'
import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'

// F0.12.08 (spec 121): uma tela, um nome; sem metáforas nem inglês na interface.
const SRC = path.resolve(process.cwd(), 'src')
const read = (rel) => fs.readFileSync(path.join(SRC, rel), 'utf-8')
// A linha do tempo é histórica (mantém os nomes da época); Icon.vue só importa ícones.
// F0.12.09: o arquivo em inglês usa os nomes em inglês (Dashboard, Inbox) de propósito.
const SKIP = new Set(['data/versionHistory.ts', 'components/ui/Icon.vue', 'i18n/messages/en.ts'])

function files(dir = SRC) {
  return fs.readdirSync(dir, { withFileTypes: true }).flatMap((entry) => {
    const full = path.join(dir, entry.name)
    if (entry.isDirectory()) return files(full)
    return /\.(vue|ts)$/.test(entry.name) ? [full] : []
  })
}

/** Tira comentários (HTML, bloco e linha) para olhar só o que pode aparecer na tela. */
function visible(text) {
  return text
    .replace(/<!--[\s\S]*?-->/g, '')
    .replace(/\/\*[\s\S]*?\*\//g, '')
    .replace(/(^|[^:'"`])\/\/.*$/gm, '$1')
}

const OLD_PHRASES = [
  'Cockpit', 'Dashboard 2.0', 'Central de Revisão', 'Bancada', 'Active Recall', 'Mesa de Triagem',
  'Triagem e Captura', 'Despejo', 'Ateliê', 'Salão', 'correspondência intelectual', 'Destaques e Anotações',
  'Gerenciamento de Acervo', 'expurgo', 'Minhas Imagens e Espaço', 'Ajustes &', 'Meu Perfil', 'Perfil Público',
  'Léxico', 'Cadernos de síntese', 'Encerrar Sessão', 'Amigos e Leitores', 'Caixa de Entrada', 'Importar Estudo',
  'Painel de Administração',
]

test('121: nenhum nome antigo nos textos visíveis', () => {
  const found = []
  for (const file of files()) {
    const rel = path.relative(SRC, file).replaceAll('\\', '/')
    if (SKIP.has(rel)) continue
    const text = visible(fs.readFileSync(file, 'utf-8'))
    for (const phrase of OLD_PHRASES) if (text.includes(phrase)) found.push(`${rel}: ${phrase}`)
    // Inglês só como palavra solta (nomes internos como InboxView ou getDashboard ficam).
    for (const match of text.matchAll(/(?<![A-Za-z.])(Inbox|Dashboard)(?![A-Za-z])/g)) found.push(`${rel}: ${match[1]}`)
  }
  assert.deepEqual(found, [])
})

test('121: nomes novos nos menus e nas abas do navegador', () => {
  const router = read('router/index.ts')
  for (const [name, title] of [
    ['dashboard', 'Painel'], ['inbox', 'Caixa de entrada'], ['highlights', 'Destaques'], ['review', 'Revisão'],
    ['friends', 'Amigos'], ['media-space', 'Minhas imagens'], ['lexicon', 'Conceitos'],
  ]) {
    assert.match(router, new RegExp(`name: '${name}'[^\\n]*meta: \\{ title: '${title}' \\}`), name)
  }
  // F0.12.09: menus por chave; os nomes em português ficam em src/i18n/messages/pt-BR.ts.
  const pt = read('i18n/messages/pt-BR.ts')
  for (const [key, label] of [
    ['dashboard', 'Painel'], ['inbox', 'Caixa de entrada'], ['concepts', 'Conceitos'], ['myProfile', 'Meu perfil'],
    ['friends', 'Amigos'], ['import', 'Importar'], ['settings', 'Ajustes'], ['logout', 'Sair'], ['syntheses', 'Sínteses'],
    ['myImages', 'Minhas imagens'],
  ]) assert.match(pt, new RegExp(`    ${key}: '${label}',`), key)
  const nav = read('components/layout/NavigationTabs.vue')
  for (const key of ['dashboard', 'inbox', 'concepts']) assert.match(nav, new RegExp(`label: t\\('nav\\.${key}'\\)`))
  // Entre 768 e 1259 px só os ícones (o nome fica para o leitor de tela e como dica).
  assert.match(nav, /@media \(min-width: 768px\) and \(max-width: 1259px\) \{\n\s+\.nav-tab-link \.tab-label \{\n\s+position: absolute;/)
  assert.match(nav, /:title="item\.label"/)
  const mobile = read('components/navigation/MobileMoreMenu.vue')
  for (const key of ['myProfile', 'inbox', 'friends', 'import', 'concepts', 'settings', 'logout']) {
    assert.match(mobile, new RegExp(`drawer-item-label">\\{\\{ t\\('nav\\.${key}'\\) \\}\\}<`), key)
  }
  assert.match(read('components/layout/MobileTabBar.vue'), /mobile-tab-label">\{\{ t\('nav\.dashboard'\) \}\}</)
  const user = read('components/layout/UserDropdown.vue')
  for (const key of ['myProfile', 'concepts', 'syntheses', 'myImages', 'logout']) {
    assert.match(user, new RegExp(`<span>\\{\\{ t\\('nav\\.${key}'\\) \\}\\}</span>`), key)
  }
})

test('121: títulos e subtítulos das telas', () => {
  assert.match(read('views/DashboardView.vue'), /<h1>Painel<\/h1>/)
  assert.match(read('views/ReviewHubView.vue'), /Pratique lembrando: responda às perguntas e complete os trechos escondidos\./)
  assert.match(read('views/InboxView.vue'), /Anote ideias rápidas e decida depois o que vira estudo\./)
  assert.match(read('views/FriendsView.vue'), /Encontre leitores, veja leituras em comum e responda aos pedidos de amizade\./)
  assert.match(read('views/HighlightsLibraryView.vue'), /Os trechos que você marcou e as notas que escreveu\./)
  assert.match(read('views/TrashView.vue'), /Itens excluídos ficam aqui por 30 dias e depois são apagados de vez\./)
  assert.match(read('views/LexiconView.vue'), /<h1 id="lexicon-heading">Conceitos<\/h1>/)
  assert.match(read('views/MediaSpaceView.vue'), /<h1 id="media-space-title">Minhas imagens<\/h1>/)
})
