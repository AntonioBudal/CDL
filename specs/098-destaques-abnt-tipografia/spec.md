# Feature Specification: F0.10.05 — Destaques: Cópia ABNT e Tipografia Citação × Anotação

**Feature Branch**: `098-destaques-abnt-tipografia`

**Created**: 2026-11-07

**Status**: Concluída em 2026-11-07

**Input**: Feature 05 do Roadmap 0.10 ("Destaques: cópia ABNT, tipografia citação × anotação"). Primeira feature do
lote 2 (F0.10.05 a F0.10.10): entre features, `npm run build` e os testes novos; suítes completas no fecho do lote.

---

## 1. Contexto (auditoria de 2026-11-07, só código; nenhum dado real lido)

| Ponto | Situação | Onde |
|---|---|---|
| Botão "Copiar" com ABNT e Markdown | **Existe**, mas o formato não é ABNT: sai `"trecho" (ALBERTO MANGUEL, Título, cap. Capítulo).` — nome inteiro em vez do sobrenome, título e capítulo no lugar do ano, sem referência | `utils/citationFormatter.ts`, `components/highlights/HighlightCard.vue` |
| O que é citação | Quase todo destaque é feito sobre o **texto do próprio leitor** (Resumo, Explicação, Conceitos, Referências) ou sobre o fichamento importado (`source_response`). O tipo `quote` existe no banco e no filtro "Citações", mas **nenhuma tela cria** um destaque desse tipo. Hoje todo cartão aparece entre aspas, em serifa, e é copiado como citação direta do livro, mesmo quando é paráfrase do leitor | `types.ts`, `views/StudyView.vue`, `HighlightCard.vue` |
| Tipografia | O trecho usa serifa com aspas decorativas (`.editorial-quote`); a nota pessoal usa sans (`.reader-note-box`). Falta separar **palavras do autor** de **texto do leitor** | `style.css` (bloco F0.8.02) |
| Dados para ABNT | `books` tem `author`, `title`, `subtitle` e `year`; não tem editora, cidade, edição nem página. A API da biblioteca devolve só `book_author` e `book_title` | `models/book.py`, `services/study_highlight_service.py` |
| Botões do cartão | Nenhum controle secundário usa `.quiet`: a regra global (0,4,0) pinta Copiar, a seta de formatos, os itens do menu, Editar, Adicionar reflexão, Cancelar e Excluir com a cor de destaque | `appearance-advanced.css`, `HighlightCard.vue` |
| Menu de formatos | Não fecha com Esc nem com clique fora; o aviso "Copiado" não é anunciado a leitores de tela | `HighlightCard.vue` |

**Decisão de dados:** sem migração. "Citação literal" usa o tipo `quote` que já existe (o `PATCH` do destaque já
aceita `kind`); o ano e o subtítulo do livro passam a vir na resposta da biblioteca.

---

## 2. User Stories

### US1 — Marcar um destaque como citação literal (P1)

Como leitor, quero dizer quais destaques são palavras do autor, para que só eles sejam tratados como citação.

**Acceptance**:
1. Nos cartões dos tipos Destaque, Anotação e Citação, um controle "Citação literal" (`aria-pressed`) alterna o tipo
   entre `quote` e o tipo comum (`note` se houver nota, senão `highlight`). Pergunta e Termo Oculto não mostram o
   controle (são itens de revisão).
2. A mudança é gravada pelo `PATCH` existente; em caso de erro, o cartão volta ao estado anterior e mostra um aviso.
3. O filtro "Citações" e o resumo passam a refletir as marcações (já contam `kind = quote`).

### US2 — Tipografia que separa o livro do leitor (P1)

**Acceptance**:
1. **Citação literal**: serifa, aspas tipográficas e o rótulo "Citação", como hoje.
2. **Texto do leitor** (qualquer outro tipo): sans, **sem aspas**, com o rótulo da seção de origem ("Do seu Resumo",
   "Da sua Explicação", "Dos seus Conceitos", "Das suas Referências", "Do fichamento importado").
3. A nota pessoal continua em sans, abaixo, subordinada ao trecho, igual nos dois casos.
4. Só tokens de cor; contraste ≥ 4,5:1 nos 10 temas para rótulos e textos novos.

### US3 — Copiar no padrão ABNT (P1)

**Acceptance**:
1. "Copiar" de uma **citação literal** gera citação direta (NBR 10520:2023): `"trecho" (Manguel, 1997).` Aspas duplas
   internas viram simples. Sem página no banco, a chamada sai sem `p.`.
2. "Copiar" de **texto do leitor** gera citação indireta: `trecho (Manguel, 1997).`, sem aspas.
3. Chamada de autoria: sobrenome em maiúsculas e minúsculas (regra de 2023); aceita "Nome Sobrenome" e
   "Sobrenome, Nome"; agrega Júnior, Filho, Neto e Sobrinho ao sobrenome; dois ou três autores (separados por `;`,
   ` e `, ` and ` ou `&`) viram `Sobrenome1; Sobrenome2`; quatro ou mais, `Sobrenome1 et al.`. Sem autor: primeira
   palavra do título seguida de `...`. Sem ano: `[s. d.]`.
4. Novo item no menu: **Referência (NBR 6023)**: `MANGUEL, Alberto. Uma história da leitura: subtítulo. 1997.`
   Quando o navegador permitir, a cópia leva também uma versão HTML com o título em itálico (para colar no editor de
   texto); senão, só texto puro.
5. O formato Markdown continua, agora com o ano.
6. O menu de formatos fecha com Esc, com clique fora e depois de copiar; o foco volta ao gatilho. "Copiado" é
   anunciado numa região `aria-live="polite"`.

### US4 — Botões calmos no cartão (P2)

**Acceptance**: Copiar, seta de formatos, itens do menu, Citação literal, Editar, Adicionar reflexão, Cancelar,
Excluir e Cancelar exclusão usam `.quiet`; "Salvar nota" e "Confirmar" exclusão mantêm o destaque. Alvos de 44 px
nos controles do cabeçalho e do rodapé.

### Edge Cases

- Autor de uma palavra só ("Platão") e sem ano → `(Platão, [s. d.])`.
- Trecho com quebras de linha → colapsadas num espaço na cópia ABNT; o Markdown mantém as linhas com `> `.
- Livro sem título (não deveria existir) → "Obra sem título", como hoje.
- Celular: o menu de formatos não sai da tela em 320 px.

---

## 3. Requirements

- **FR-001**: `HighlightLibraryItemRead` ganha `book_year: int | None` e `book_subtitle: str` (sem migração).
- **FR-002**: `citationFormatter.ts` reescrito: `abntAuthorCall(author, title)`, `formatCitationABNT(item, { literal })`,
  `formatReferenceABNT(item)` (texto e HTML), Markdown com ano; `formatCitationPlain` mantido.
- **FR-003**: `HighlightCard` usa `isLiteral = kind === 'quote'` na tipografia, no rótulo e na cópia; emite
  `toggle-literal`; `HighlightsLibraryView` grava com `updateStudyHighlight(..., { kind })` e reverte em erro.
- **FR-004**: Menu de formatos com Esc, clique fora, foco de volta e `aria-live`.
- **FR-005**: `.quiet` nos controles secundários do cartão.
- **FR-006**: Sem migração; a cópia na tela do estudo (`formatQuoteText`) não muda nesta feature.

## 4. Success Criteria

- **SC-001**: Teste de backend: a biblioteca devolve `book_year` e `book_subtitle` (com e sem ano).
- **SC-002**: Testes de frontend: formatador (sobrenomes, sufixos, vários autores, sem autor, sem ano, aspas internas,
  direta × indireta, referência em texto e HTML) e cartão (controle literal só nos tipos certos, tipografia, `.quiet`,
  menu com Esc, `aria-live`). Os testes antigos do formatador passam a esperar o formato novo.
- **SC-003**: Navegador com dados fictícios ("Livro de Teste", autor fictício): alternar citação literal, copiar os
  formatos, 1366 e 375 px, contraste nos 10 temas.
- **SC-004**: `npm run build` e os testes novos e vizinhos de Destaques passando; commit; levar ao `main`.

## 5. Fora do escopo

- Página da citação (`p. X`): exigiria campo novo e migração; fica para as referências em 3 escopos do 0.11.
- Editora, cidade e edição na referência (mesmo motivo); APA e BibTeX (0.11).
- Cópia na tela do estudo (barra flutuante) e exportação em lote de destaques.
