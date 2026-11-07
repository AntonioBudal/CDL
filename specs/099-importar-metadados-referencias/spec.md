# Feature Specification: F0.10.06 — Importar: Faixa de Metadados da Obra e Ganchos para Referências em 3 Escopos

**Feature Branch**: `099-importar-metadados-referencias`

**Created**: 2026-11-07

**Status**: Concluída em 2026-11-07

**Input**: Feature 06 do Roadmap 0.10 ("Importar: faixa de metadados, ganchos para referências em 3 escopos"). O
plano mestre não detalha os itens; a leitura abaixo vem da auditoria e se apoia na F0.10.05 (cópia ABNT) e no item
"referências em 3 escopos (CSL-JSON, BibTeX, ABNT/APA)" do Roadmap 0.11. Segunda feature do lote 2.

---

## 1. Contexto (auditoria de 2026-11-07, só código)

| Ponto | Situação | Onde |
|---|---|---|
| Faixa de metadados | **Existe** uma faixa compacta com Livro, Capítulo, Localização e Título. Ela mostra só o **título** do livro: autor, ano e subtítulo, que a citação ABNT da F0.10.05 usa, não aparecem; um livro sem autor ou sem ano só é notado depois, na cópia (`[s. d.]`, "Livro...") | `views/ImportView.vue`, `style.css` (`.import-top-bar`) |
| Completar o livro | Só pela página do livro. A API já aceita `PATCH /api/books/{id}` com `author`, `subtitle`, `year` e `expected_version` | `routers/books.py`, `services/api.ts` (`updateBook`) |
| Localização | Texto livre ("p. 32–34", "Loc. 1820"), sem interpretação. Aparece duas vezes (faixa e "Ajuste manual"), com rótulos diferentes ("Localização" × "Página ou localização") | `ImportView.vue`, `StudyEditorFields.vue` |
| Referências | Os dados de uma referência estão espalhados em 3 escopos — **obra** (livro), **trecho** (capítulo e localização do estudo) e **obras citadas** (seção Referências do estudo) — e nada os reúne. O 0.11 vai precisar disso para CSL-JSON, BibTeX e ABNT/APA | `models/book.py`, `models/study.py` |

**Decisão de dados:** sem migração e sem campo novo. Os "ganchos" são um módulo puro do frontend que lê os três
escopos dos dados que já existem; o 0.11 consome o mesmo módulo.

---

## 2. User Stories

### US1 — Ver e completar os dados da obra ao importar (P1)

Como leitor, quero ver autor, ano e subtítulo do livro escolhido já na faixa de metadados e completar o que faltar
sem sair da tela.

**Acceptance**:
1. Com um livro escolhido, a faixa ganha uma segunda linha: `Autor · Ano · Subtítulo` do livro. Campo vazio aparece
   como "sem autor", "sem ano" (texto em tom neutro, não erro).
2. Faltando autor ou ano, um aviso curto explica o efeito ("A citação ABNT sairá com [s. d.]") e um botão
   "Completar dados do livro" abre, na própria faixa, os campos Autor, Ano e Subtítulo.
3. Salvar usa o `PATCH` existente com `expected_version`; em conflito (409) ou erro, mostra a mensagem e mantém o que
   foi digitado. Sucesso atualiza a linha e a lista de livros, sem perder o rascunho da importação.
4. Livro sem permissão de edição (`can_edit === false`) mostra a linha sem o botão.

### US2 — Prévia da referência em 3 escopos (P1)

**Acceptance**:
1. Abaixo da linha da obra, uma prévia "Como este estudo será citado" com três itens:
   - **Obra**: completa (autor e ano) ou o que falta;
   - **Trecho**: capítulo e localização interpretada (`p. 32–34`, `loc. 1820`) ou "sem localização";
   - **Obras citadas**: quantas linhas há na seção Referências da prévia (ou "nenhuma").
2. Mostra a chamada ABNT que resultaria, com a página quando a localização for de página:
   `(Fictícia, 2001, p. 32–34)`. Sem localização de página, sem `p.`.
3. A prévia se atualiza ao trocar livro, capítulo, localização ou a seção Referências.

### US3 — Localização com um só nome (P2)

**Acceptance**: o campo da faixa passa a se chamar "Página ou localização", como no ajuste manual, com o mesmo
exemplo ("p. 32–34 ou Loc. 1820"). A duplicidade dos campos continua (o ajuste manual é o editor completo); os dois
seguem ligados ao mesmo valor.

### Edge Cases

- Localização "32-34", "pp. 32–34", "p.32", "pág. 7" → página; "Loc. 1820", "posição 1820" → `loc.`; texto que não se
  encaixa ("cap. 3, início") → mostrado como está, sem `p.` na chamada.
- Ano fora de 1000–2100 → recusado no campo (o backend já recusa) com mensagem clara.
- Trocar de livro com o formulário "Completar" aberto → fecha sem salvar.
- Celular (375 px e 320 px): a linha da obra e a prévia quebram linha, sem rolagem lateral.

---

## 3. Requirements

- **FR-001**: Novo `utils/referenceScopes.ts` (puro, sem Vue): `parseLocator(location)` → `{ kind: 'page' | 'loc' |
  'raw' | 'none', value }`; `buildReferenceScopes({ book, chapter, location, referencesText })` → `{ work, passage,
  cited }` com `missing` em cada escopo; `abntCallWithLocator(scopes)` reutilizando `abntAuthorCall` da F0.10.05.
- **FR-002**: Novo `components/import/ImportWorkMetaStrip.vue`: linha da obra, aviso, formulário "Completar dados do
  livro" (emite o livro atualizado) e a prévia dos 3 escopos.
- **FR-003**: `ImportView.vue` usa o componente dentro da faixa e atualiza `books` ao salvar.
- **FR-004**: Rótulo e exemplo da localização unificados.
- **FR-005**: Só tokens de cor, `.quiet` nos controles secundários, alvos de 44 px, contraste ≥ 4,5:1 nos 10 temas.
- **FR-006**: Sem migração; backend sem mudança.

## 4. Success Criteria

- **SC-001**: Testes do `referenceScopes` (localizadores, escopos completos e incompletos, linhas de Referências,
  chamada com e sem página).
- **SC-002**: Testes do componente e da view (linha da obra, aviso só quando falta, botão só com `can_edit`,
  `expected_version` no `PATCH`, rótulo unificado).
- **SC-003**: Navegador com dados fictícios: livro sem ano → completar → prévia atualiza; localização de página e de
  posição; 1366 e 375 px; contraste nos 10 temas.
- **SC-004**: `npm run build` e testes novos e vizinhos da Importar; commit; levar ao `main`.

## 5. Fora do escopo

- Exportar CSL-JSON, BibTeX, APA; editora, cidade e edição; ISBN (tudo no 0.11).
- Interpretar cada linha da seção Referências como uma obra estruturada (0.11).
- Usar a localização do estudo na cópia dos Destaques (a biblioteca não devolve a localização; pode entrar no 0.11).
- Remover a duplicidade dos campos Título e Localização entre a faixa e o ajuste manual.
