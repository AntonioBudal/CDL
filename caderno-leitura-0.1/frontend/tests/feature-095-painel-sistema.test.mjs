import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

// F0.10.03 — painel de Sistema: versão e commit do servidor e da interface, revisão do banco, backups, integridade
// e o que a exclusão apaga.
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')
const read = (rel) => fs.readFileSync(path.join(root, rel), 'utf-8')

test('o build embute o commit da interface', () => {
  const vite = read('vite.config.ts')
  assert.match(vite, /__BUILD_COMMIT__:\s*JSON\.stringify\(/)
  assert.match(vite, /git rev-parse --short=7 HEAD/)
  assert.match(read('src/build-info.d.ts'), /declare const __BUILD_COMMIT__: string/)
})

test('o card compara os commits e só acusa divergência quando os dois são conhecidos', () => {
  const card = read('src/components/settings/SystemSovereigntyCard.vue')
  assert.match(card, /__BUILD_COMMIT__/)
  assert.match(card, /Reinicie o serviço Leitorum/)
  assert.match(card, /commitMismatch = computed\(\(\) =>[\s\S]{0,200}!== UNKNOWN/)
  assert.match(card, /const UNKNOWN = 'desconhecido'/)
  assert.match(card, /rode as migrações/)
})

test('integridade e backups só para administrador; exclusão explicada com o que o código faz', () => {
  const card = read('src/components/settings/SystemSovereigntyCard.vue')
  assert.match(card, /v-if="isAdmin"[\s\S]{0,400}Verificar integridade/)
  assert.match(card, /secure_delete|zera o conteúdo/)
  assert.match(card, /\/\.well-known\/security\.txt/)
  assert.doesNotMatch(card, /para sempre|inviolável|100% seguro/i)
})

test('a aba Sistema usa o card e mostra o backup manual só para administrador', () => {
  const view = read('src/views/SettingsView.vue')
  assert.match(view, /<SystemSovereigntyCard/)
  assert.match(view, /<DatabaseBackup\s+v-if="authStore\.isAdmin\.value"/)
  const api = read('src/services/api.ts')
  assert.match(api, /getSystemStatus:/)
  assert.match(api, /runIntegrityCheck:/)
})
