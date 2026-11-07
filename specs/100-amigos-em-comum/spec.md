# Feature Specification: F0.10.07 — Amigos: Leituras e Estudos em Comum

**Feature Branch**: `100-amigos-em-comum`

**Created**: 2026-11-07

**Status**: Concluída em 2026-11-07

**Input**: Feature 07 do Roadmap 0.10 ("Amigos: leituras e estudos em comum"). Terceira feature do lote 2.

---

## 1. Contexto (auditoria de 2026-11-07, só código)

| Ponto | Situação | Onde |
|---|---|---|
| Amizades | **Completo**: pedido, aceite, recusa, cancelamento, desfazer, bloqueio, resumo, status | `routers/friends.py`, `views/FriendsView.vue` |
| Perfil de outro leitor | Mostra só o cartão (nome, bio, contagem de amigos, estatísticas se liberadas). Nada sobre o que os dois leem | `routers/users.py` (`GET /api/users/{username}`), `views/UserProfileView.vue` |
| Compartilhados comigo | Aba na Biblioteca com estudos de terceiros e filtro por `@autor`; a API de livros compartilhados existe. Não há como chegar ali já filtrado por um amigo | `routers/sharing.py`, `components/library/SharedStudiesList.vue`, `views/BooksView.vue` |
| Livros em comum | **Não existe**. Cada leitor tem a própria linha em `books`; não há ISBN (fica para o 0.11). A única pista é título e autor | `models/book.py` |
| Permissões | `can_read_book` e `can_read_study` (privado, amigos, personalizado, público; bloqueio vence tudo) | `services/sharing_service.py` |

**Decisão de privacidade:** "em comum" usa **só os livros e estudos do amigo que você já pode ler** pelas regras
atuais. Um livro privado dele nunca aparece, nem como contagem. Do seu lado, entram todos os seus livros (são seus).
Por isso a lista pode ser diferente vista de cada lado — é o comportamento correto.

---

## 2. User Stories

### US1 — Ver as leituras em comum no perfil de um amigo (P1)

Como leitor, ao abrir o perfil de um amigo, quero ver quais livros nós dois temos.

**Acceptance**:
1. No perfil de um **amigo** (amizade aceita), abaixo do cartão, a seção "Em comum com você" lista os livros em
   comum: título e autor, com dois links — "Seu livro" (`/livros/:id`) e, quando houver estudos dele legíveis,
   quantos são.
2. Correspondência por **título normalizado** (sem acentos, caixa, pontuação e espaços repetidos; ignora o subtítulo
   depois de `:`) e, quando os dois livros têm autor, também pelo **sobrenome** do primeiro autor normalizado.
3. Livros do amigo que você não pode ler (privados, ou excluídos) não entram. Sem livros em comum: "Nenhuma leitura
   em comum entre os livros que ele compartilha com você."
4. No seu próprio perfil, de quem não é amigo, ou com bloqueio, a seção não aparece (a API responde 404 para bloqueio
   e usuário inexistente; para não amigo, `is_friend: false` sem listas).

### US2 — Ver os estudos dele sobre esses livros (P1)

**Acceptance**:
1. Em cada livro em comum, os estudos do amigo legíveis por você (até 5 por livro, mais recentes primeiro): título e
   capítulo, com link para a leitura do estudo (rota `study` com o livro dele, como na aba Compartilhados).
2. Estudos privados ou na lixeira não entram.

### US3 — Tudo o que ele compartilhou com você (P2)

**Acceptance**:
1. A seção mostra "N estudos compartilhados com você" (total, não só dos livros em comum) com o link "Ver todos",
   que abre a Biblioteca na aba Compartilhados já filtrada por `@usuario` (`/livros?aba=compartilhados&autor=usuario`).
2. A Biblioteca passa a aceitar esses parâmetros de URL; sem eles, nada muda.

### Edge Cases

- Livro do amigo "Dom Casmurro: romance" e o seu "dom casmurro" → em comum (subtítulo ignorado).
- Mesmo título com autores diferentes (ex.: duas obras chamadas "Poemas") → não é comum.
- Um dos lados sem autor → compara só o título.
- Vários livros seus com o mesmo título → aparecem agrupados num só item com o primeiro link.
- Amizade desfeita com o perfil aberto → ao recarregar, a seção some.
- Limites: até 30 livros em comum e 5 estudos por livro; um aviso diz quando há mais.

---

## 3. Requirements

- **FR-001**: `GET /api/users/{username}/in-common` → `{ is_friend, books: [{ title, author, my_book_id,
  friend_book_id, friend_studies: [{ id, title, chapter_name, book_id, updated_at }], friend_studies_total }],
  books_truncated, shared_with_me_total }`. Bloqueio ou usuário inexistente → 404; o próprio usuário → 404 também
  (não faz sentido); não amigo → `is_friend: false` e listas vazias.
- **FR-002**: Leitura dos livros e estudos do amigo pelas mesmas regras de `can_read_book` / `can_read_study`
  (filtradas em SQL para não carregar o acervo inteiro); o total compartilhado reaproveita
  `get_shared_studies_for_user(author=...)`.
- **FR-003**: Normalização em função própria e testada (`normalize_title_key`, `first_author_surname_key`).
- **FR-004**: `components/profile/ProfileInCommon.vue` no `UserProfileView` (só quando não é o dono); estados de
  carga, vazio e erro; só tokens, `.quiet`, alvos de 44 px.
- **FR-005**: `BooksView` e `SharedStudiesList` leem `aba` e `autor` da URL.
- **FR-006**: Sem migração.

## 4. Success Criteria

- **SC-001**: Testes de backend: amigo com livros em comum (título com acento/caixa/subtítulo, autor diferente,
  autor ausente), livro privado do amigo fora, estudo privado fora, não amigo, bloqueio (404), si mesmo (404),
  total compartilhado, limites.
- **SC-002**: Testes de frontend: seção só para não dono, links, vazio, "Ver todos" com os parâmetros; Biblioteca
  abrindo na aba e com o filtro da URL.
- **SC-003**: Navegador com dois usuários fictícios (banco temporário): perfil do amigo com livros e estudos em
  comum, link "Ver todos", 1366 e 375 px, contraste nos 10 temas.
- **SC-004**: `npm run build` e testes novos e vizinhos; commit; levar ao `main`.

## 5. Fora do escopo

- Correspondência por ISBN ou por identificador de obra (0.11, com ISBN).
- Contagem de livros em comum nos cartões da lista de amigos (exigiria uma chamada por amigo; pode vir depois).
- Destaques e citações em comum; círculos de leitura (1.0).
