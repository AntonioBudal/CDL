# Feature Specification: F0.11.04 — ISBN Sob Demanda (BrasilAPI e Open Library)

**Feature Branch**: `106-isbn-sob-demanda`

**Created**: 2026-11-09

**Status**: Concluída em 2026-11-09

**Input**: Item "ISBN (BrasilAPI e Open Library, só sob demanda)" do Roadmap 0.11 no HANDOFF. Quarta feature do lote 1
do 0.11. **Com migração** (`0036`) e **com uma nova saída de rede** (só quando o leitor pede).

---

## 1. Contexto (auditoria de 2026-11-09, só código)

| Ponto | Situação | Onde |
|---|---|---|
| ISBN | **Não existe** no modelo nem na tela | `models/book.py` |
| Dados para ABNT | Faltam **editora** e **local de publicação** (a referência da F0.10.05 sai só com autor, título e ano) | `utils/citationFormatter.ts` |
| Cadastro e edição do livro | Gaveta "Novo livro" (título, autor, categorias) e `BookEditModal` (título, autor, subtítulo, ano, categorias, capa) | `views/BooksView.vue`, `components/BookEditModal.vue` |
| Saídas de rede hoje | Só login com Google (se ativado) e baixar capa por endereço (`httpx`, com validação contra endereços internos) — é o que a landing promete em "Seus dados" e no Desafio F12 | `services/cover_service.py`, `components/landing/SovereigntySection.vue` |

**Consequência:** buscar por ISBN é uma terceira conexão externa. Ela só acontece quando o leitor clica em "Buscar",
sai do **servidor** (o navegador continua falando só com o Leitorum, então a CSP e o Desafio F12 não mudam) e pode ser
desligada pelo administrador. O texto da landing é atualizado para dizer isso.

---

## 2. User Stories

### US1 — Preencher os dados do livro pelo ISBN (P1)

**Acceptance**:
1. No cadastro (gaveta "Novo livro") e na edição do livro, um campo **ISBN** com o botão **"Buscar dados"**.
2. O ISBN é conferido antes de buscar (ISBN-10 ou ISBN-13, com ou sem hífens, dígito verificador válido; ISBN-10 é
   convertido para 13). Inválido → mensagem no campo, sem ir à rede.
3. A busca tenta a **BrasilAPI** e, se não achar, a **Open Library**. O resultado aparece como **sugestão**: título,
   subtítulo, autores, ano, editora, local e a fonte ("Dados da BrasilAPI"). O leitor escolhe **"Usar estes dados"**
   (preenche os campos vazios; campos já preenchidos só mudam se ele marcar "substituir o que já está preenchido") ou
   descarta. Nada é gravado sem o leitor salvar o formulário.
4. Não encontrado nas duas → "Não encontrei este ISBN na BrasilAPI nem na Open Library". Fora do ar ou sem internet →
   "Não foi possível consultar agora". Tempo máximo de 5 s por serviço.

### US2 — Guardar ISBN, editora e local (P1)

**Acceptance**:
1. Migração `0036_book_isbn_publisher`: colunas `isbn` (13 dígitos, nulo), `publisher` e `publication_place` (texto,
   nulo) em `books`; índice `(user_id, isbn)`. Aditiva; nenhum dado muda.
2. A API aceita e devolve os três; o ISBN gravado é sempre o ISBN-13 sem hífens.
3. A página do livro mostra "Editora · Local · ISBN" quando houver.
4. A **referência ABNT** da F0.10.05 passa a usar local e editora quando existirem:
   `MANGUEL, Alberto. Uma história da leitura. São Paulo: Companhia das Letras, 1997.` Sem local: `[S. l.]`; sem
   editora: `[s. n.]` — só quando o outro existe (sem os dois, continua como hoje).
5. Exportação (JSON da conta e Markdown do livro) leva os três campos.

### US3 — Transparência e controle (P1)

**Acceptance**:
1. A consulta sai do servidor, com um `User-Agent` genérico ("Leitorum"), sem cookies, sem dados do leitor além do
   ISBN; só para `brasilapi.com.br` e `openlibrary.org` (lista fixa no código).
2. `LEITORUM_ISBN_LOOKUP=off` desliga a busca: o botão some e a rota responde 404.
3. A landing ("Seus dados" → "Conexões externas") passa a dizer: "Só no login com Google, se ativado, ao buscar uma
   capa por endereço e ao buscar dados de um livro pelo ISBN — sempre a seu pedido." O painel do Desafio F12 ganha
   a nota de que essas consultas saem do servidor, não do navegador.

### Edge Cases

- ISBN já usado em outro livro do mesmo leitor → aviso ("Você já tem este ISBN em ‹título›"), sem bloquear.
- Open Library com vários autores e ano em texto ("March 1997") → extrai o ano de 4 dígitos.
- Resposta muito grande ou fora do formato → tratada como "não encontrado".
- Celular: o botão "Buscar dados" fica ao lado do campo ou abaixo; sugestão em cartão com ações de 44 px.

---

## 3. Requirements

- **FR-001**: Migração `0036`, modelo, schemas (`BookCreate`, `BookPatch`, `BookRead`) com validação/normalização do
  ISBN.
- **FR-002**: `services/isbn_service.py`: `normalize_isbn` (10/13, checksum), `lookup_isbn` (BrasilAPI → Open Library,
  `httpx` com timeout de 5 s, sem redirecionar para outros domínios, resposta até 512 KB), mapeamento para
  `{title, subtitle, authors, year, publisher, place, source}`.
- **FR-003**: `GET /api/books/isbn/{isbn}` → sugestão ou 404/422/503; respeita `LEITORUM_ISBN_LOOKUP`; também devolve
  `existing_book` quando o leitor já tem o ISBN. `GET /api/system/status` informa `isbn_lookup_enabled`.
- **FR-004**: Frontend: `components/books/IsbnLookup.vue` (campo, botão, sugestão, aplicar) na gaveta de novo livro e no
  `BookEditModal`; editora/local/ISBN na página do livro; `formatReferenceABNT` com local e editora.
- **FR-005**: Landing e Desafio F12 atualizados; testes que fixam o texto antigo ajustados.
- **FR-006**: Só tokens, `.quiet`, 44 px, contraste ≥ 4,5:1 nos 10 temas.

## 4. Success Criteria

- **SC-001**: Testes de backend sem rede (respostas da BrasilAPI e da Open Library simuladas com `httpx.MockTransport`):
  checksum e conversão 10→13, BrasilAPI encontrada, queda para a Open Library, nenhuma das duas, serviço fora do ar,
  resposta inválida, chave desligada (404), ISBN duplicado avisado, migração sobe e desce com dados fictícios e com
  snapshot antes, exportação com os campos.
- **SC-002**: Testes de frontend: componente, aplicar sem sobrescrever, referência ABNT com local/editora, textos da
  landing.
- **SC-003**: Navegador com a busca simulada (servidor de validação com um transporte falso via variável de teste, sem
  rede real): cadastro e edição, 1366 e 375 px, contraste nos 10 temas.
- **SC-004**: Build, testes novos e vizinhos; commit; levar ao `main`.

## 5. Fora do escopo

- Busca por título/autor (sem ISBN); importar capa pela busca (já existe "capa por endereço").
- Edição, páginas e assunto (o 0.11 de referências decide o que mais guardar).
- Consultar ISBN no navegador (a CSP continua `connect-src 'self'`).
