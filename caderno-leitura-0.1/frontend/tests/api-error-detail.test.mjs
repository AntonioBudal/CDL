import test from 'node:test'
import assert from 'node:assert/strict'
import { detailMessage } from '../src/services/api.ts'

test('detailMessage retorna string direta quando detail for string', () => {
  const msg = detailMessage({ detail: 'Nome de usuário já está em uso.' }, 409)
  assert.equal(msg, 'Nome de usuário já está em uso.')
})

test('detailMessage formata erros de validação 422 com rótulos amigáveis e remove prefixo Value error', () => {
  const payload422 = {
    detail: [
      {
        loc: ['body', 'username'],
        msg: 'Value error, O nome de usuário deve conter apenas letras sem acento, números, ponto (.) ou hífen (-), sem espaços.',
        type: 'value_error',
      },
    ],
  }
  const msg = detailMessage(payload422, 422)
  assert.match(msg, /letras sem acento/i)
  assert.ok(!msg.includes('Value error,'))
})

test('detailMessage adiciona rótulo de campo amigável quando a mensagem não contém o nome do campo', () => {
  const payload422 = {
    detail: [
      {
        loc: ['body', 'email'],
        msg: 'value is not a valid email address',
        type: 'value_error',
      },
    ],
  }
  const msg = detailMessage(payload422, 422)
  assert.equal(msg, 'E-mail: value is not a valid email address')
})

test('detailMessage trata erro 500 com mensagem padrão amigável', () => {
  const msg = detailMessage({}, 500)
  assert.match(msg, /indisponível/i)
})
