import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'

const srcDir = path.resolve(process.cwd(), 'src')

test('Setup: Tipos e contratos da Feature 071 declarados em friendship.ts', () => {
  const typesPath = path.resolve(srcDir, 'types/friendship.ts')
  assert.ok(fs.existsSync(typesPath), 'types/friendship.ts deve existir')
  const content = fs.readFileSync(typesPath, 'utf-8')

  assert.ok(content.includes('export type SocialActiveTab'), 'Deve declarar SocialActiveTab')
  assert.ok(content.includes("'friends' | 'requests' | 'discover' | 'blocked'"), 'SocialActiveTab deve conter as 4 abas')
  assert.ok(content.includes('export interface BookplateCardProps'), 'Deve declarar BookplateCardProps')
  assert.ok(content.includes('export interface BookplateCardEmits'), 'Deve declarar BookplateCardEmits')
  assert.ok(content.includes('export interface BookplateCardState'), 'Deve declarar BookplateCardState')
})

test('US1: BookplateCard implementa Ex-Líbris digital, selo de cópia de 1200ms e Web Share API', () => {
  const compPath = path.resolve(srcDir, 'components/BookplateCard.vue')
  assert.ok(fs.existsSync(compPath), 'BookplateCard.vue deve existir')

  const content = fs.readFileSync(compPath, 'utf-8')

  // Estrutura do Ex-Líbris Digital
  assert.ok(content.includes('bookplate-card'), 'Deve conter container bookplate-card')
  assert.ok(content.includes('bookplate-avatar'), 'Deve conter elemento de avatar')
  assert.ok(content.includes('bookplate-handle') || content.includes('@{{'), 'Deve conter exibição do @identificador')

  // Microinteração do Selo em 1200ms
  assert.ok(content.includes('1200'), 'Deve conter duração de 1200ms para o selo de confirmação')
  assert.ok(content.includes('is-stamped'), 'Deve conter classe CSS .is-stamped')
  assert.ok(content.includes('scale(') || content.includes('transform'), 'Deve conter aceleração por GPU no selo')

  // Compartilhamento via Web Share API e Fallback
  assert.ok(content.includes('navigator.share'), 'Deve verificar e suportar navigator.share')
  assert.ok(content.includes('navigator.clipboard.writeText'), 'Deve conter fallback para cópia do link do perfil')

  // Imunidade cromática e banimento de emojis
  assert.ok(!content.includes('#2563eb'), 'Não deve conter hex rígido #2563eb')
  assert.ok(!content.includes('#111827'), 'Não deve conter hex rígido #111827')
  assert.ok(!content.includes('#dc2626'), 'Não deve conter hex rígido #dc2626')
  const emojiRegex = /[\u{1F300}-\u{1F9FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}]/u
  assert.ok(!emojiRegex.test(content), 'BookplateCard.vue não deve conter emojis')
})

test('US1: FriendsView integra BookplateCard permanentemente no topo', () => {
  const viewPath = path.resolve(srcDir, 'views/FriendsView.vue')
  assert.ok(fs.existsSync(viewPath), 'FriendsView.vue deve existir')

  const content = fs.readFileSync(viewPath, 'utf-8')
  assert.ok(content.includes('BookplateCard'), 'FriendsView deve importar e integrar BookplateCard')
  assert.ok(content.includes('<BookplateCard'), 'FriendsView deve renderizar <BookplateCard>')
})

test('US2: Cartões de Conexão Literária com data amigável, estante pública e FriendActionButtons', () => {
  const viewPath = path.resolve(srcDir, 'views/FriendsView.vue')
  const content = fs.readFileSync(viewPath, 'utf-8')

  // Cartão com link para estante do leitor (/u/:username)
  assert.ok(content.includes('/u/') || content.includes('/@'), 'Deve conter link de navegação para a estante do leitor')
  assert.ok(content.includes('formatDate') || content.includes('desde'), 'Deve conter formatação de data amigável')

  // Integração com FriendActionButtons
  assert.ok(content.includes('FriendActionButtons'), 'Deve integrar FriendActionButtons no cartão')

  // Verificação de segurança e diálogo defensivo em FriendActionButtons
  const buttonsPath = path.resolve(srcDir, 'components/FriendActionButtons.vue')
  const buttonsContent = fs.readFileSync(buttonsPath, 'utf-8')
  assert.ok(buttonsContent.includes('role="dialog"'), 'FriendActionButtons deve conter diálogo com role="dialog"')
  assert.ok(buttonsContent.includes('aria-modal="true"'), 'FriendActionButtons deve conter modal com aria-modal="true"')
  assert.ok(buttonsContent.includes('min-height: 44px') || buttonsContent.includes('44px'), 'Botões devem ter alvo tátil mínimo de 44px')
})

test('US3: Estados vazios enriquecidos "Círculo em Formação" e busca debounced de 300ms', () => {
  const viewPath = path.resolve(srcDir, 'views/FriendsView.vue')
  const content = fs.readFileSync(viewPath, 'utf-8')

  // Estado acolhedor Círculo em Formação
  assert.ok(content.includes('Círculo em Formação') || content.includes('círculo em formação') || content.includes('circulo em formacao') || content.includes('Círculo de leitura em formação'), 'Deve conter estado acolhedor de círculo em formação')

  // Busca na aba Descobrir com debounce de 300ms
  assert.ok(content.includes('300'), 'Deve conter debounce de 300ms para busca')
  assert.ok(content.includes('searchQuery') || content.includes('executeSearch'), 'Deve executar busca de leitores')
  assert.ok(content.includes('sugest') || content.includes('descobrir') || content.includes('Explorar') || content.includes('Descubra'), 'Deve apresentar sugestões ou guia na aba de descoberta')
})

test('US4: Navegação por 4 Abas com contadores e acessibilidade WAI-ARIA', () => {
  const viewPath = path.resolve(srcDir, 'views/FriendsView.vue')
  const content = fs.readFileSync(viewPath, 'utf-8')

  // Estrutura WAI-ARIA
  assert.ok(content.includes('role="tablist"'), 'Barra de abas deve ter role="tablist"')
  assert.ok(content.includes('role="tab"'), 'Botões de abas devem ter role="tab"')
  assert.ok(content.includes('role="tabpanel"'), 'Painéis de abas devem ter role="tabpanel"')
  assert.ok(content.includes(':aria-selected='), 'Abas devem alternar :aria-selected')
  assert.ok(content.includes('aria-controls='), 'Abas devem apontar para seus respectivos aria-controls')

  // 4 Abas canônicas
  assert.ok(content.includes('Círculo de Leitura') || content.includes('Meus Amigos'), 'Deve conter aba Círculo de Leitura')
  assert.ok(content.includes('Solicitações'), 'Deve conter aba Solicitações')
  assert.ok(content.includes('Descobrir Leitores'), 'Deve conter aba Descobrir Leitores')
  assert.ok(content.includes('Bloqueados'), 'Deve conter aba Bloqueados')

  // Imunidade cromática e banimento de emojis
  const emojiRegex = /[\u{1F300}-\u{1F9FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}]/u
  assert.ok(!emojiRegex.test(content), 'FriendsView.vue não deve conter emojis')
  assert.ok(!content.includes('#2563eb'), 'Não deve conter hex rígido #2563eb')
  assert.ok(!content.includes('#111827'), 'Não deve conter hex rígido #111827')
  assert.ok(!content.includes('#dc2626'), 'Não deve conter hex rígido #dc2626')
})
