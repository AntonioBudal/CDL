# Feature Specification: F0.10.10 — Correções Reservadas do Roadmap 0.10

**Feature Branch**: `102-correcoes-reservadas-010`

**Created**: 2026-11-07

**Status**: Concluída em 2026-11-07

**Input**: Feature 10 do Roadmap 0.10 ("Correções reservadas"). O repositório não tinha lista; em 2026-11-07 o usuário
aprovou os seis itens abaixo (um do HANDOFF, três das pendências do HANDOFF §5 e dois achados no lote 2). Última
feature do lote 2: fecha com `npm test`, `pytest` completo (sozinho, banco descartável) e build.

---

## 1. Itens (auditoria de 2026-11-07, só código)

| # | Item | Situação hoje | Onde |
|---|---|---|---|
| 1 | Três botões de sessão na Revisão | O hub mostra **"Praticar Revisão Agora"** (faixa de prontidão), **"Iniciar Sessão Estruturada"** e **"Prática Rápida neste Hub"** — o primeiro e o terceiro chamam a mesma função (`startReview`). O resumo do fim de sessão diz **"Revisar mais 10"** fixo, mesmo com sessão de 5 ou 15 | `views/ReviewHubView.vue`, `components/review/ReviewStatsHeader.vue`, `components/review/ReviewSummaryModal.vue` |
| 2 | "Software Livre" sem licença | Rodapé global (`App.vue`, `components/layout/AppFooter.vue`) e a página Apoie (`SupportView.vue`) dizem "software livre"; o repositório não tem arquivo de licença | — |
| 3 | Digitalização: erro passageiro parece definitivo | Para `busy` (outra página sendo lida) e `low_memory`, a tela diz "Não foi possível ler esta foto", descarta a foto e só oferece "Tentar outra foto" | `views/DigitizeNotebookView.vue`, `composables/useDigitizeDraft.ts` |
| 4 | `/compartilhado/{id}` anunciado sem existir | O `robots.txt` libera `/compartilhado/` e o sitemap lista os estudos públicos nessa rota, que **não existe** no frontend (404) | `services/seo_service.py` |
| 5 | Cópia da tela do estudo fora do padrão | A barra flutuante copia `> "trecho"\n>\n> — *Estudo*, Capítulo, (Livro)`, sem autor nem ano | `views/StudyView.vue`, `composables/useTextSelection.ts` |
| 6 | Teste sensível a CRLF | `tests/superclasses.test.mjs` procura `button,\n  .button` no CSS; num checkout com CRLF (como o worktree) falha sem defeito real | `frontend/tests/superclasses.test.mjs` |

---

## 2. User Stories

### US1 — Um jeito claro de começar a revisar (P1)

**Acceptance**:
1. O hub passa a ter **duas** entradas, sem repetição: o botão principal da faixa de prontidão, **"Praticar agora
   (N itens)"**, e, abaixo, uma única ação secundária **"Sessão registrada (até N itens)"** com uma linha explicando a
   diferença: "Fica no histórico e pode ser retomada depois." O botão "Prática Rápida neste Hub" sai.
2. N respeita o tamanho escolhido (5/10/15) e o que há de elegível; o aviso do balde (sessão registrada usa todos os
   níveis) continua.
3. O resumo do fim de sessão mostra **"Revisar mais N"** com o tamanho escolhido (prop nova `moreCount`).
4. A ação secundária usa `.quiet` (só a principal tem o destaque).

### US2 — Texto da licença fiel ao repositório (P1)

**Acceptance**: o rodapé passa a dizer **"Código-fonte público"** (com link para o repositório, que já aparece na
landing); a página Apoie troca "como software livre" por "com código-fonte público". Nenhum outro texto afirma
"software livre" ou "open source".

### US3 — Digitalização: tentar de novo com a mesma foto (P1)

**Acceptance**:
1. Para `busy` e `low_memory`, o título vira **"Não deu para ler agora"**, a mensagem do servidor continua, a foto
   fica guardada e o botão principal é **"Tentar de novo"** (reenvia a mesma foto); "Tentar outra foto" vira
   secundário.
2. Os demais erros não mudam (título, foto descartada, "Tentar outra foto").

### US4 — Nada de anunciar página que não existe (P1)

**Acceptance**:
1. Uma constante `PUBLIC_STUDY_PAGES_ENABLED = False` em `seo_service.py`: desligada, o `robots.txt` não tem
   `Allow: /compartilhado/` e o sitemap lista só as páginas institucionais.
2. Ligada (para o 1.0, quando a rota existir), volta o comportamento atual, com os mesmos filtros de privacidade.
3. Os testes existentes passam a cobrir os dois estados.

### US5 — Cópia da tela do estudo no padrão ABNT (P2)

**Acceptance**: "Citação" na barra flutuante copia **citação indireta** no formato da F0.10.05, com a localização
do estudo quando for página: `trecho (Sobrenome, ano, p. 32–34).` (usa `abntCallWithLocator` da F0.10.06). O
aviso "Citação copiada" continua. `formatQuoteText` fica no código (tem teste próprio e outros usos possíveis).

### US6 — Teste indiferente a quebra de linha (P2)

**Acceptance**: `superclasses.test.mjs` normaliza CRLF para LF ao ler os arquivos; passa no worktree e no checkout
principal.

### Edge Cases

- Revisão sem itens pendentes: a ação secundária some junto com a principal desabilitada (como hoje).
- Digitalização: "Tentar de novo" com o servidor ainda ocupado → volta à mesma tela, sem perder a foto.
- Cópia no estudo sem autor ou sem ano → regras da F0.10.05 (`Título...`, `[s. d.]`).

---

## 3. Requirements

- **FR-001**: `ReviewHubView` sem o botão duplicado; rótulos novos; `ReviewStatsHeader` mostra N no botão principal
  (prop `practiceCount`); `ReviewSummaryModal` com `moreCount`.
- **FR-002**: Textos de licença em `App.vue`, `AppFooter.vue`, `SupportView.vue`.
- **FR-003**: `useDigitizeDraft`: `TRANSIENT_CODES = ['busy', 'low_memory']`; nesses casos não libera a foto; novo
  `retry()`; `DigitizeNotebookView` com título e botões condicionais.
- **FR-004**: `seo_service.PUBLIC_STUDY_PAGES_ENABLED`; `generate_robots_txt` e `get_public_sitemap_items` respeitam.
- **FR-005**: `referenceScopes.formatIndirectCitationWithLocator(text, scopes)`; `StudyView.handleCopyQuote` usa.
- **FR-006**: `superclasses.test.mjs` com leitura normalizada.
- **FR-007**: Sem migração.

## 4. Success Criteria

- **SC-001**: Testes novos (`frontend/tests/feature-102-correcoes-reservadas.test.mjs`,
  `backend/tests/test_seo_public_pages_flag.py`) e os existentes de SEO, revisão, digitalização e barra flutuante
  ajustados ao comportamento novo.
- **SC-002**: Navegador com dados fictícios: hub com duas entradas e "Revisar mais 5"; rodapé; digitalização com
  erro passageiro simulado (rota interceptada no navegador); `robots.txt` e `sitemap.xml`; cópia no estudo.
- **SC-003**: **Fecho do lote 2:** `npm test`, `pytest` completo (sozinho, com `CADERNO_DATABASE_PATH` descartável) e
  build; falha de feature anterior vai em commit próprio.
- **SC-004**: Commit; levar ao `main`; atualizar `docs/contexto/HANDOFF.md` e `RETOMADA.md` e levá-los ao `main`.

## 5. Fora do escopo

- Escolher e adicionar uma licença (decisão do dono do projeto).
- Criar a rota `/compartilhado/{id}` (1.0).
- Mudar a lógica da sessão registrada (balde continua fora, por exigir migração).
