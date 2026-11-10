# Feature Specification: F0.11.05 — Referências em 3 Escopos (ABNT, APA, BibTeX, CSL-JSON)

**Feature Branch**: `107-referencias-tres-escopos`

**Created**: 2026-11-09

**Status**: Concluída em 2026-11-09

**Input**: Item "referências em 3 escopos (CSL-JSON, BibTeX, ABNT/APA)" do Roadmap 0.11 no HANDOFF. Quinta feature do
lote 1 do 0.11: **fecha o lote** com `npm test`, `pytest` completo e build. **Sem migração, sem backend.**

---

## 1. Contexto (auditoria de 2026-11-09, só código)

| Ponto | Situação | Onde |
|---|---|---|
| Os 3 escopos | Definidos na F0.10.06 (`referenceScopes.ts`): **obra** (livro), **trecho** (capítulo + localização do estudo) e **obras citadas** (linhas da seção Referências) | `utils/referenceScopes.ts` |
| Dados da obra | Desde a F0.11.04: autor, título, subtítulo, ano, **editora, local, ISBN** | `models/book.py`, `types.ts` |
| Formatos hoje | Só ABNT, e só a partir de um destaque (citação e referência) ou da prévia da Importar | `utils/citationFormatter.ts` |
| Onde falta | Página do livro, página do estudo e Biblioteca não oferecem referência; não há APA, BibTeX nem CSL-JSON | `views/BookView.vue`, `views/StudyView.vue`, `views/BooksView.vue` |

---

## 2. User Stories

### US1 — Referência da obra em 4 formatos (P1)

**Acceptance**:
1. Na página do livro (menu de ações), **"Referência"** abre um painel com abas **ABNT · APA · BibTeX · CSL-JSON**,
   a referência gerada e os botões **Copiar** e **Baixar** (`.txt`, `.txt`, `.bib`, `.json`).
2. Formatos, com os dados que o Leitorum guarda:
   - **ABNT (NBR 6023)**: `SOBRENOME, Nome. *Título*: subtítulo. Local: Editora, ano.` (mesma regra da F0.11.04).
   - **APA (7ª ed.)**: `Sobrenome, N. N., & Sobrenome, N. (ano). *Título: Subtítulo*. Editora.` (sem ano: `(s.d.)`).
   - **BibTeX**: `@book{sobrenome1997titulo, author = {Sobrenome, Nome and …}, title = {…}, …}` com acentos e
     caracteres especiais escapados; chave estável (sobrenome + ano + primeira palavra do título, sem acento).
   - **CSL-JSON**: `{"id", "type": "book", "title", "author": [{"family", "given"}], "issued": {"date-parts":
     [[ano]]}, "publisher", "publisher-place", "ISBN"}`.
3. Campos ausentes simplesmente não aparecem (nada inventado). Um aviso curto lista o que falta ("sem editora e
   local — complete em Editar livro").

### US2 — Trecho: citação com a localização do estudo (P1)

**Acceptance**:
1. Na página do estudo, **"Referência"** (no menu de mais opções) mostra o mesmo painel da obra **mais** a chamada no
   texto: ABNT `(Sobrenome, ano, p. 32–34)` e APA `(Sobrenome, ano, p. 32–34)` / `pp.` para intervalo, com a localização
   do estudo; BibTeX e CSL-JSON levam `pages`/`page` (ou `note` para posição de e-book) e o capítulo em `chapter`/
   `note`.

### US3 — Obras citadas, como escritas (P2)

**Acceptance**:
1. No mesmo painel do estudo, a seção **"Obras citadas neste estudo"** lista as linhas da seção Referências, **como o
   leitor escreveu** (sem tentar estruturar), com "Copiar lista" e "Baixar .txt".
2. BibTeX e CSL-JSON **não** recebem as obras citadas (não há dados estruturados); o painel diz isso.

### US4 — Bibliografia do acervo (P2)

**Acceptance**: na Biblioteca, **"Baixar bibliografia"** gera, para os livros **visíveis com os filtros atuais**, um
arquivo em ABNT (`.txt`, ordem alfabética), APA (`.txt`), BibTeX (`.bib`, chaves únicas) ou CSL-JSON (`.json`).

### Edge Cases

- Autor ausente: ABNT entra pelo título (regra atual); APA começa pelo título; BibTeX sem `author`; CSL sem `author`.
- Autores "Sobrenome, Nome" e "Nome Sobrenome", sufixos (Júnior/Filho/Neto/Sobrinho) e 2+ autores (APA com `&` antes do
  último; mais de 20 autores com reticências; BibTeX com `and`).
- Título com chaves, `%`, `&`, `_` → escapados no BibTeX; `"` e quebras de linha → JSON válido.
- Chaves BibTeX repetidas na bibliografia → sufixo `a`, `b`, …
- Celular: abas roláveis, texto da referência com quebra; botões de 44 px.

---

## 3. Requirements

- **FR-001**: `utils/referenceFormats.ts` (puro): `bookReferenceData(book)` → dados normalizados (autores com
  `family`/`given`); `toABNT`, `toAPA`, `toBibTeX`, `toCSL`, cada um com variante de trecho (`locator`, `chapter`);
  `apaInTextCall`; `bibliography(books, format)`; `bibtexKey` com desempate.
- **FR-002**: `components/references/ReferencePanel.vue` (abas, texto, Copiar com `copyRich`, Baixar via `Blob`, aviso
  de campos ausentes, `aria-live`), usado em `BookView` e `StudyView` (com trecho e obras citadas).
- **FR-003**: `BooksView`: "Baixar bibliografia" com escolha do formato, sobre `filteredBooks`.
- **FR-004**: Sem backend nem migração; tudo calculado no navegador a partir dos dados já carregados.
- **FR-005**: Só tokens, `.quiet`, 44 px, contraste ≥ 4,5:1 nos 10 temas.

## 4. Success Criteria

- **SC-001**: Testes do `referenceFormats` (cada formato com dados completos e parciais, nomes, sufixos, vários
  autores, escapes BibTeX, JSON válido, trecho com página/intervalo/posição, chaves únicas, ordem da bibliografia).
- **SC-002**: Testes de tela (painel nas duas páginas, obras citadas, botão da Biblioteca).
- **SC-003**: Navegador (dados fictícios): copiar e baixar nos 4 formatos, 1366 e 375 px, contraste nos 10 temas.
- **SC-004**: **Fecho do lote 1 do 0.11:** `npm test`, `pytest` completo (sozinho, banco descartável) e build; falha de
  feature anterior em commit próprio; HANDOFF e RETOMADA; levar ao `main`.

## 5. Fora do escopo

- Estruturar as "obras citadas" escritas à mão (exigiria um analisador de referências; possível item futuro).
- RIS, Zotero/Mendeley direto, outros estilos (Chicago, MLA).
- Referência de capítulo de livro com organizador ("In:"), artigos, sites.
