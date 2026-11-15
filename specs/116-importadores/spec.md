# Feature Specification: F0.12.03 — Importadores (Goodreads, StoryGraph, BookWyrm, Readwise, Omnivore)

**Feature Branch**: `116-importadores`

**Created**: 2026-11-15

**Status**: Concluída em 2026-11-15

**Input**: Item "importadores (Readwise, Goodreads, StoryGraph, Omnivore, BookWyrm)" do `docs/contexto/ROADMAP-0.12.md`.
Terceira feature do 0.12. **Sem migração.**

---

## 1. Contexto (auditoria de 2026-11-15: código e formatos públicos)

| Ponto | Situação | Onde |
|---|---|---|
| Livro | Já tem `reading_state` (`quero_ler`, `lendo`, `lido`, `abandonado`), datas de início/fim, ISBN, editora, local e ano (F0.11.01/.04). **Não tem nota (estrelas) nem resenha** | `models/book.py` |
| Importar destaques | "Importar de leitor digital": Kindle, Kobo, KOReader, com prévia, livro sugerido, deduplicação e Mesa (F0.11.03/.09) | `services/ereader_import/`, `views/EreaderImportView.vue` |
| Importar biblioteca | **Não existe** importação de lista de livros de outro serviço | — |

**Formatos (pesquisados em 2026-11-15):**

| Serviço | O que exporta | Confirmação |
|---|---|---|
| **Goodreads** | CSV da biblioteca: `Book Id, Title, Author, Author l-f, Additional Authors, ISBN, ISBN13, My Rating, …, Publisher, Binding, Number of Pages, Year Published, Original Publication Year, Date Read, Date Added, Bookshelves, …, Exclusive Shelf, My Review, …`; ISBN como `="0123…"`; datas `AAAA/MM/DD`; estantes `to-read`, `currently-reading`, `read` | Arquivo de exemplo e importador do BookWyrm (código aberto) |
| **The StoryGraph** | CSV: `Title, Authors, Contributors, ISBN/UID, Format, Read Status, Date Added, Last Date Read, Dates Read, Read Count, …, Star Rating, Review, …, Tags, Owned?`; autores separados por vírgula; datas `AAAA/MM/DD` | Arquivo de exemplo do BookWyrm (`did-not-finish` e "Dates Read" preenchido **não confirmados**) |
| **BookWyrm** | CSV: `title, author_text, <ids, isbn_10, isbn_13…>, pages, start_date, finish_date, stopped_date, rating, review_name, review_cw, review_content, review_published, shelf, shelf_name, shelf_date` | Código-fonte do BookWyrm (identificadores das estantes não confirmados; padrão do projeto: `to-read`, `reading`, `read`, `stopped-reading`) |
| **Omnivore** (encerrado em 2024) | ZIP: `metadata_*.json` (`title, author, url, slug, savedAt…`) e `highlights/<slug>.md` (`> trecho`, nota depois de linha em branco) | Código-fonte do Omnivore |
| **Readwise** | CSV de destaques (colunas comuns: `Highlight, Book Title, Book Author, Note, Location, Highlighted at…`) | **Não confirmado** (página de exportação exige login; sem exemplo público) |

**Decisão:** dois caminhos, conforme o que cada serviço exporta:
1. **Biblioteca** (Goodreads, StoryGraph, BookWyrm) → **livros** com estado e datas de leitura.
2. **Destaques** (Readwise, Omnivore) → **capturas na Mesa**, pela tela que já existe para Kindle/Kobo/KOReader.

---

## 2. User Stories

### US1 — Trazer a biblioteca de outro serviço (P1)

**Acceptance**:
1. Nova tela **"Importar biblioteca"** (`/livros/importar`), com entrada discreta na página Livros ("Importar de outro
   serviço"). Aceita o CSV do Goodreads, do StoryGraph ou do BookWyrm e **reconhece o serviço pelo cabeçalho**.
2. **Prévia** (nada gravado): uma linha por livro, com título, autor, ISBN, estado e datas convertidos, e a situação:
   **"novo"** ou **"já no acervo"** (mesmo ISBN-13/10, ou mesmo título normalizado + sobrenome do primeiro autor, a
   regra da F0.10.07/F0.11.03). Ação por livro: criar / atualizar estado e datas (só nos já existentes) / pular; padrão
   "criar" para novos e "pular" para existentes. Botões "todos" e filtro por estado.
3. Conversão de estado: `to-read`/`want to read` → **Quero ler**; `currently-reading`/`reading` → **Lendo**;
   `read` → **Lido**; `did-not-finish`/`stopped-reading` → **Abandonado**; outras estantes → sem estado. Datas:
   Goodreads `Date Read` → fim; StoryGraph `Last Date Read` → fim; BookWyrm `start_date`/`finish_date`/`stopped_date`.
   Ano: `Year Published` (ou `Original Publication Year`). ISBN sem o `="…"` e sem traços. Autores múltiplos juntados
   com "; " (o separador do Leitorum).
4. **Resenhas** (opcional, desmarcado): "Trazer as resenhas como capturas na Mesa" → cada resenha vira uma captura no
   livro, com origem "Resenha do Goodreads · 12/03/2024"; HTML da resenha vira texto.
5. **Notas em estrelas não são importadas** (o Leitorum não tem esse campo) — dito na prévia.
6. Resultado: "N livros criados, M atualizados, K pulados", com link para Livros.

### US2 — Destaques do Readwise e do Omnivore (P1)

**Acceptance**:
1. A tela "Importar de leitor digital" passa a reconhecer também o **CSV do Readwise** (colunas `Highlight` e
   `Book Title`) e o **ZIP do Omnivore** (`metadata_*.json` + `highlights/*.md`), com a mesma prévia, escolha de livro
   e deduplicação.
2. Readwise: cada linha vira captura; `Note` vira "Nota: …"; origem "Readwise · pos. 123 · 12/03/2024". O leitor de
   colunas é tolerante (nomes sem diferença de maiúsculas, colunas extras ignoradas, datas em ISO ou `AAAA-MM-DD HH:MM`).
3. Omnivore: cada artigo com destaques vira um "livro" na prévia (título e autor do artigo; o leitor escolhe criar,
   juntar a um livro existente ou pular); cada bloco `> trecho` vira captura, com a nota quando houver.

### US3 — Segurança e limites (P1)

**Acceptance**:
1. Nada é gravado na prévia; o arquivo não fica no servidor.
2. CSV até 10 MB e 20 mil linhas; ZIP até 50 MB, lido **na memória** (nada extraído no disco), só os arquivos
   esperados, com limite de 200 MB descompactados e de 5 mil arquivos (proteção contra "zip bomb").
3. Arquivo não reconhecido: mensagem dizendo quais formatos são aceitos.

### Edge Cases

- CSV com BOM, separador `;` (Excel em português) ou fim de linha CRLF: aceitos.
- Linha sem título: pulada e contada.
- O mesmo livro duas vezes no arquivo: uma linha na prévia.
- Atualizar estado de livro existente não apaga datas que o arquivo não traz.
- Celular: prévia em cartões empilhados; alvos de 44 px; sem rolagem lateral.

---

## 3. Requirements

- **FR-001**: `services/library_import/` (puro): `detect_library_format(bytes)`, `parse_goodreads`, `parse_storygraph`,
  `parse_bookwyrm` → `LibraryParseResult(service, rows, skipped)`; `normalize_isbn`, `parse_date`, mapa de estados.
- **FR-002**: `services/library_import/service.py`: `build_preview(session, user, parsed)` (casamento com o acervo) e
  `run_import(session, user, parsed, choices, with_reviews)`; rotas `POST /api/books/import-library/preview` e
  `POST /api/books/import-library/import` (multipart, como a F0.11.03).
- **FR-003**: `services/ereader_import/readwise_csv.py` e `omnivore.py` (puros) + detecção em `detect_format`; rótulos
  "Readwise" e "Omnivore".
- **FR-004**: Frontend: `views/LibraryImportView.vue` (`/livros/importar`, rota `library-import`, nos contratos 076/081),
  link na página Livros; textos da tela de leitor digital citando os novos formatos. Só tokens, `.quiet`, 44 px,
  contraste ≥ 4,5:1 nos 10 temas.
- **FR-005**: Versão `0.12.0-alpha.3` e F0.12.03 marcada na linha do tempo (regra do HANDOFF §2).

## 4. Success Criteria

- **SC-001**: Testes puros com arquivos fictícios nos formatos acima: detecção dos 3 CSVs de biblioteca e dos 2 de
  destaques; ISBN `="…"`; datas `AAAA/MM/DD` e ISO; estados; autores múltiplos; BOM, `;` e CRLF; Omnivore com
  trecho+nota e nota sem trecho; ZIP com arquivo estranho, grande demais ou com muitos arquivos recusado.
- **SC-002**: Testes de API: prévia não grava; casamento por ISBN e por título/autor; criar/atualizar/pular; resenhas
  opcionais na Mesa; isolamento entre leitores; limites (413/422).
- **SC-003**: Navegador (dados fictícios): importar um CSV de cada serviço de biblioteca e um de cada serviço de
  destaques; 375 e 1366 px; contraste nos 10 temas.
- **SC-004**: Build e testes novos e vizinhos; versão `alpha.3`; commit; levar ao `main`.

## 5. Fora do escopo

- Notas em estrelas, estantes personalizadas, "Dates Read" múltiplas releituras (fica só a última data).
- Importar pela API/conta dos serviços (só arquivo exportado).
- Exportar do Leitorum para esses formatos.
- Confirmação do formato do Readwise com um arquivo real: **pedir ao usuário um teste** com o próprio export depois da
  entrega (o leitor é tolerante, mas o cabeçalho real não pôde ser conferido).
