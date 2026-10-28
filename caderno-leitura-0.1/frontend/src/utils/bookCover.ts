import type { Book, CoverResponse } from '../types'

/**
 * Livro como fica depois de enviar, importar ou remover a capa.
 *
 * O servidor muda o `updated_at` do livro ao trocar a capa. Sem levar a data nova, o próximo "Salvar" do formulário
 * manda a data antiga em `expected_updated_at` e recebe conflito de concorrência.
 */
export function bookAfterCoverChange(book: Book, res: CoverResponse): Book {
  return { ...book, cover_image: res.cover_image, updated_at: res.updated_at ?? book.updated_at }
}
