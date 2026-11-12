# Feature Specification: F0.11.06 — Léxico de Conceitos e `[[conceito:…]]`

**Feature Branch**: `108-lexico-conceitos`

**Created**: 2026-11-12

**Status**: Concluída em 2026-11-12

**Input**: Item "léxico de conceitos e `[[ ]]`" do Roadmap 0.11 no HANDOFF. Primeira feature do lote 2 do 0.11.
**Sem migração.**

---

## 1. Contexto (auditoria de 2026-11-12, só código)

| Ponto | Situação | Onde |
|---|---|---|
| `[[ ]]` | **Existe para estudos**: `[[Título]]` ou `[[Título|id]]` com autocompletar no editor, link na leitura e *backlinks* (tabela `study_mentions`). `[[Título]]` sem estudo correspondente vira um link para a busca da Biblioteca | `services/study_mention_service.py`, `services/markdown.ts`, `components/StudyEditorFields.vue`, `components/MarkdownContent.vue` |
| Conceitos | Cada estudo tem a seção **Conceitos**, em texto livre (normalmente "**Termo**: definição" ou "Termo — definição" por linha). Não há visão que junte os conceitos do acervo | `models/study.py` |
| Léxico | **Não existe**. (O `lexicon` do organizador da digitalização é outra coisa: vocabulário para classificar seções.) | `services/organizer/adapter_state.py` |

**Decisão de dados:** sem migração. O léxico é **derivado** na hora das seções Conceitos e das menções
`[[conceito:…]]` dos estudos do próprio leitor (fora da lixeira). Nada novo fica guardado; editar o estudo atualiza o
léxico.

---

## 2. User Stories

### US1 — Ver o léxico do acervo (P1)

**Acceptance**:
1. Nova página **Léxico** (`/conceitos`, no menu "Mais" e no menu do usuário) com a lista de conceitos em ordem
   alfabética, busca e, por conceito, quantas definições e em quantos livros aparece.
2. Um conceito vem das linhas da seção Conceitos que seguem um destes formatos (um termo curto, até 80 caracteres):
   `- **Termo**: definição`, `**Termo** — definição`, `Termo: definição`, `Termo – definição`, ou um título
   `### Termo` seguido do parágrafo. Linhas que não se encaixam são ignoradas (não viram conceito).
3. Termos iguais com acento, caixa ou plural simples diferentes ("Mímese", "mimese") se juntam numa entrada (chave
   normalizada sem acento e caixa; o rótulo mostrado é a grafia mais frequente).

### US2 — Página do conceito (P1)

**Acceptance**:
1. `/conceitos/:chave` mostra o termo, **todas as definições** (texto, livro, capítulo, estudo, com link para o
   estudo) e os **lugares onde o conceito é mencionado** com `[[conceito:Termo]]` (trecho de contexto e link).
2. Conceito sem definição, só mencionado, também tem página ("Ainda sem definição nos seus estudos").

### US3 — `[[conceito:Termo]]` nos estudos (P1)

**Acceptance**:
1. Na leitura, `[[conceito:Termo]]` vira um link para a página do conceito, com aparência diferente da menção a
   estudo (sublinhado pontilhado e rótulo "conceito" para leitores de tela).
2. No editor, ao digitar `[[`, o autocompletar oferece também os conceitos do léxico (marcados "Conceito"); escolher um
   insere `[[conceito:Termo]]`. Digitar `[[conceito:` filtra só conceitos.
3. A menção a estudo (`[[Título]]`, `[[Título|id]]`) continua igual.

### Edge Cases

- Conceito definido em estudo que foi para a lixeira some do léxico; volta ao restaurar.
- Termo com mais de 80 caracteres, linha que é só negrito sem definição, lista de marcadores sem ":" → não viram
  conceito.
- `[[conceito:]]` vazio → texto comum.
- Acervo grande: a lista é paginada (100 por página) e a busca é feita no servidor.
- Celular: lista em uma coluna; definições empilhadas; 44 px.

---

## 3. Requirements

- **FR-001**: `services/concept_lexicon.py` (puro na parte de análise): `parse_concepts(text)` → `[(termo, definição)]`;
  `concept_key(termo)` (sem acento, caixa, pontuação; plural simples "s" final só quando o resto já existe como chave);
  `extract_concept_mentions(text)` → `[(termo, trecho)]`; `build_lexicon(session, user_id)` agregando por chave.
- **FR-002**: `GET /api/concepts?q=&page=` → `{ items: [{key, term, definitions, books, mentions}], total }`;
  `GET /api/concepts/{key}` → `{ key, term, definitions: [...], mentions: [...] }` (404 se não existir).
  `GET /api/studies/search-candidates` ganha os conceitos (tipo `concept`) para o autocompletar, ou uma rota irmã
  `GET /api/concepts/candidates?q=`.
- **FR-003**: `markdown.ts`: `[[conceito:Termo]]` → `<a class="study-concept-mention" href="/conceitos/<chave>">`;
  `MarkdownContent` navega para o conceito.
- **FR-004**: `StudyEditorFields`: autocompletar com conceitos; `views/LexiconView.vue` e `views/ConceptView.vue`;
  rotas `lexicon` e `concept` (registradas nos contratos 076/081); entradas no menu.
- **FR-005**: Só tokens, `.quiet`, 44 px, contraste ≥ 4,5:1 nos 10 temas.

## 4. Success Criteria

- **SC-001**: Testes de backend: formatos aceitos e recusados da seção Conceitos, chave normalizada e junção de grafias,
  menções `[[conceito:…]]`, estudo na lixeira fora, isolamento entre leitores, busca, paginação, 404.
- **SC-002**: Testes de frontend: render de `[[conceito:…]]` sem afetar `[[Título|id]]`, autocompletar com conceitos,
  páginas, rotas nos contratos.
- **SC-003**: Navegador (dados fictícios): léxico, página do conceito, link a partir do estudo, autocompletar; 1366 e
  375 px; contraste nos 10 temas.
- **SC-004**: Build e testes novos e vizinhos; commit; levar ao `main`.

## 5. Fora do escopo

- Editar o léxico à parte dos estudos (renomear, fundir, apagar conceitos manualmente).
- Cartões de revisão de conceitos e "conceitos frágeis" (item "evolução da revisão" do 0.11).
- Grafo de conceitos; léxico compartilhado entre amigos.
