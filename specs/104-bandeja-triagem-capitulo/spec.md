# Feature Specification: F0.11.02 — Bandeja de Triagem por Capítulo

**Feature Branch**: `104-bandeja-triagem-capitulo`

**Created**: 2026-11-09

**Status**: Concluída em 2026-11-09

**Input**: Segundo item do Roadmap 0.11 no HANDOFF ("bandeja de triagem por capítulo"). O plano mestre não detalha;
a leitura abaixo vem da auditoria. Segunda feature do lote 1 do 0.11. **Com migração** (`0035`).

---

## 1. Contexto (auditoria de 2026-11-09, só código)

| Ponto | Situação | Onde |
|---|---|---|
| Mesa de Triagem (Inbox) | **Existe**: capturas rápidas com abas Na mesa / Promovidas / Vinculadas / Arquivadas, busca, promover para estudo (via Importar) e vincular a um estudo existente | `views/InboxView.vue`, `routers/inbox.py`, `models/inbox_capture.py` |
| Destino da captura | Só o **livro** (`book_id`, opcional). Não há capítulo: quem lê o livro com capítulos não tem como separar as ideias de cada um | `InboxCapture`, `QuickCaptureModal.vue` |
| Página do livro | Mostra os estudos do capítulo escolhido; nada das capturas pendentes daquele livro ou capítulo | `views/BookView.vue` |
| Promover | Abre a Importar com `promote_inbox_id`; preenche o livro da captura, mas o capítulo fica para escolher | `views/ImportView.vue` |
| Implantação | Como na F0.11.01: o `alembic upgrade head` faz o snapshot validado e o `iniciar.py` só sobe com o banco na última revisão. **A 0034 ainda não foi aplicada no banco ativo**; um único `upgrade head` aplicará 0034 e 0035 | HANDOFF §3 |

---

## 2. User Stories

### US1 — Capturar já no capítulo (P1)

**Acceptance**:
1. A captura rápida ganha "Capítulo (opcional)", que aparece depois de escolher o livro e lista os capítulos dele.
2. Aberta a partir da página de um livro com capítulo escolhido, a captura já vem com livro e capítulo preenchidos.
3. Escolher um capítulo grava também o livro dele; trocar de livro limpa o capítulo.
4. A API recusa capítulo de outro livro ou de outro leitor (404, sem revelar que existe).

### US2 — A bandeja do capítulo na página do livro (P1)

**Acceptance**:
1. Na lista de capítulos, cada capítulo com capturas pendentes mostra a contagem (ex.: "3 na bandeja").
2. Na área do capítulo escolhido, acima dos estudos, a seção **"Bandeja do capítulo"** (recolhível, aberta quando há
   itens) lista as capturas pendentes daquele capítulo: texto (até 3 linhas, expansível), fonte e data.
3. Ações por item: **"Virar estudo"** (abre a Importar já com livro, capítulo e o texto, como a promoção atual),
   **"Arquivar"** e **"Abrir na Mesa de Triagem"**. Arquivar atualiza a lista e as contagens sem recarregar a página.
4. Capturas do livro **sem capítulo** aparecem numa linha "N capturas do livro sem capítulo" com link para a Mesa já
   filtrada pelo livro.

### US3 — Mesa de Triagem sabe do capítulo (P2)

**Acceptance**: o cartão da captura mostra "Livro · Capítulo"; editar a captura permite trocar o capítulo; a Mesa
aceita `?livro=ID` na URL para abrir filtrada.

### Edge Cases

- Capítulo excluído: as capturas dele ficam só com o livro (`ON DELETE SET NULL`) e voltam a "sem capítulo".
- Livro na lixeira: a bandeja some com a página; as capturas continuam na Mesa.
- Captura promovida ou vinculada sai da bandeja (só `status = inbox` aparece).
- Celular: a bandeja ocupa a largura; ações quebram linha; alvos de 44 px.

---

## 3. Requirements

- **FR-001**: Migração `0035_inbox_capture_chapter`: `inbox_captures.chapter_id` (inteiro nulo,
  `REFERENCES chapters(id) ON DELETE SET NULL`) e índice `(user_id, chapter_id, status)`. `ADD COLUMN` simples;
  nenhum dado muda.
- **FR-002**: Schemas com `chapter_id` (criar, editar, ler) e `chapter_name` na leitura; serviço valida dono e
  coerência livro/capítulo e preenche o livro a partir do capítulo.
- **FR-003**: `GET /api/inbox?chapter_id=` e `GET /api/inbox/book-tray?book_id=` → `{ by_chapter: {id: n},
  without_chapter: n }` (só `status = inbox`, só do dono).
- **FR-004**: Frontend: `QuickCaptureModal` com capítulo (e capítulo padrão vindo da página do livro);
  `components/books/ChapterTray.vue` na `BookView`; contagens na lista de capítulos; Importar preenche o capítulo da
  captura promovida; `CaptureItemCard` mostra e edita o capítulo; `InboxView` lê `?livro=`.
- **FR-005**: Só tokens, `.quiet` nos secundários, 44 px, contraste ≥ 4,5:1 nos 10 temas.

## 4. Success Criteria

- **SC-001**: Backend: migração sobe e desce com dados fictícios; criar/editar com capítulo; capítulo de outro livro
  ou leitor → 404; livro preenchido pelo capítulo; troca de livro limpa capítulo; contagens da bandeja; exclusão do
  capítulo zera o vínculo; snapshot antes da 0035.
- **SC-002**: Frontend: modal com capítulo, bandeja com ações, contagens, Importar com capítulo, `?livro=`.
- **SC-003**: Navegador (banco temporário): capturar de dentro do capítulo, ver na bandeja, virar estudo, arquivar;
  1366, 375 e 320 px; contraste nos 10 temas.
- **SC-004**: Build e testes novos e vizinhos (Inbox, Importar, livro); commit; levar ao `main`.

## 5. Fora do escopo

- Arrastar capturas entre capítulos; triagem em lote.
- Estado de leitura por capítulo.
- Capturas automáticas a partir de destaques ou de leitores externos (KOReader/Readest é outro item do 0.11).
