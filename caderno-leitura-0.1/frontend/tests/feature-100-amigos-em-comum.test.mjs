import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'

const srcDir = path.resolve(process.cwd(), 'src')
const read = (rel) => fs.readFileSync(path.resolve(srcDir, rel), 'utf-8')

test('100: API e tipos de leituras em comum', () => {
  const api = read('services/api.ts')
  assert.match(api, /getInCommon: \(username: string, signal\?: AbortSignal\) =>/)
  assert.match(api, /`\/users\/\$\{encodeURIComponent\(username\)\}\/in-common`/)
  const types = read('types.ts')
  for (const name of ['InCommonStudy', 'InCommonBook', 'InCommonResponse']) {
    assert.match(types, new RegExp(`export interface ${name} \\{`))
  }
  assert.match(types, /shared_with_me_total: number/)
})

test('100: perfil mostra a seção só para outro leitor', () => {
  const view = read('views/UserProfileView.vue')
  assert.match(view, /import ProfileInCommon from '..\/components\/profile\/ProfileInCommon.vue'/)
  assert.match(view, /<ProfileInCommon v-if="!isOwner" :username="publicProfile\.username" \/>/)
})

test('100: seção some para quem não é amigo e tem estados de carga, erro e vazio', () => {
  const comp = read('components/profile/ProfileInCommon.vue')
  assert.match(comp, /loading\.value \|\| !!loadError\.value \|\| !!data\.value\?\.is_friend/)
  assert.ok(comp.includes('Procurando leituras em comum…'))
  assert.ok(comp.includes('role="alert"'))
  assert.ok(comp.includes('Nenhuma leitura em comum entre os livros que @'))
  assert.match(comp, /class="quiet in-common-retry"/)
})

test('100: links para o seu livro, para o estudo do amigo e para "Ver todos" filtrado', () => {
  const comp = read('components/profile/ProfileInCommon.vue')
  assert.match(comp, /:to="`\/livros\/\$\{book\.my_book_id\}`"/)
  assert.match(comp, /name: 'study', params: \{ bookId: study\.book_id, studyId: study\.id \}/)
  assert.match(comp, /query: \{ aba: 'compartilhados', autor: props\.username \}/)
  assert.ok(comp.includes('Ver todos'))
  assert.match(comp, /book\.friend_studies_total > book\.friend_studies\.length/)
})

test('100: Biblioteca abre na aba Compartilhados e passa o @autor da URL', () => {
  const books = read('views/BooksView.vue')
  assert.match(books, /route\.query\.aba === 'compartilhados' \? 'compartilhados' : 'meus-livros'/)
  assert.match(books, /<SharedStudiesList :initial-author="sharedAuthorFromUrl" \/>/)
  const list = read('components/library/SharedStudiesList.vue')
  assert.match(list, /defineProps<\{ initialAuthor\?: string \}>\(\)/)
  assert.match(list, /const authorFilter = ref\(\(props\.initialAuthor \|\| ''\)\.replace\(\/\^@\/, ''\)\)/)
})
