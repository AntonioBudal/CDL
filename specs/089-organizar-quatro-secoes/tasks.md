# Tasks: Organizar nas 4 Seções

**Input**: Design documents from `specs/089-organizar-quatro-secoes/`
**Prerequisites**:
- [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md), [data-model.md](data-model.md);
- [contracts/organize-api.contract.md](contracts/organize-api.contract.md), [quickstart.md](quickstart.md).

## Organization

As fases seguem o plano. A fase 2 é o **portão de paridade**: se o organizador do produto não reproduzir o
EXP-023 em 144 de 144 casos, a fatia para para decisão do usuário.

Caminhos relativos à raiz do repositório (`C:\Users\User\caderno`):
- `L/` = `caderno-leitura-0.1/`;
- `DI/` = `document-intelligence/`.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode rodar em paralelo (arquivos distintos, sem dependência mútua)
- **[Story]**: história atendida (US1, US2, US3, US4)

**Regras em todas as tarefas**:
- nunca abrir, ler ou alterar `L/backend/data/caderno.db`;
- o `pytest` roda sempre com `CADERNO_DATABASE_PATH` apontando para um banco descartável já migrado;
- só textos fictícios;
- nenhum texto organizado em log.

---

## Phase 1: Setup — linha de base

- [X] T001 Registrar a linha de base:
  - `pytest` em `L/backend`, com `CADERNO_DATABASE_PATH` descartável;
  - `npm test` e `npm run build` em `L/frontend`;
  - só contagens, sem alterar nada.

---

## Phase 2: Foundational — paridade e organizador do backend (PORTÃO)

- [X] T002 Criar `DI/experiments/EXP-023/harness/export_parity.py`.
  - Para as 24 páginas de teste nas 6 condições (CER 0, 10 e 25 %, com e sem geometria), roda o
    `organizer.Organizer` com o `organizer-v1.json`.
  - Grava em `DI/experiments/EXP-023/artifacts/parity-v1.json`:
    - por caso: `text`, `lines` (`text`, `bbox`, `confidence`) e o resultado esperado (`segments` com `start`,
      `end`, `text`, `section`, `confidence` e `review`, além de `sections` e `explicit_headings`);
    - o SHA-256 do artefato usado.
  - Commit no `DI/` (`F06(document-inteligence) [EXP-023] …`).
- [X] T003 Copiar o artefato e o fixture byte a byte:
  - `DI/experiments/EXP-023/artifacts/organizer-v1.json` e `.sha256` para `L/backend/app/data/organizer/`;
  - `parity-v1.json` para `L/backend/tests/fixtures/organizer-parity-v1.json`.

  Conferir os SHA-256 depois da cópia.
- [X] T004 Criar `L/backend/app/services/organizer/engine.py`.
  - É uma cópia de `DI/experiments/EXP-023/harness/organizer.py` (commit `58dac1e`).
  - Única mudança: um cabeçalho de origem. Nenhuma alteração de lógica.
  - Criar também o `__init__.py`.
- [X] T005 Criar `L/backend/app/services/organizer/loader.py`:
  - carga preguiçosa sob `threading.Lock`, com conferência do SHA-256;
  - estado em cache (`available` / `not_installed` / `integrity_failed`);
  - `status()`;
  - `organize(text, lines)`:
    - limites de 50 000 caracteres e 400 trechos;
    - devolve as seções, os trechos com `text`, `explicit_headings`, `review_count` e os avisos `suggestion` e
      `single_section`;
    - remove o campo interno `marginals`;
  - `reset_cache()` para testes;
  - logs só com contagem e tempo.
- [X] T006 Criar `L/backend/tests/test_organizer_parity.py`:
  - confere o SHA-256 do fixture e do artefato;
  - exige igualdade exata em 144 de 144 casos (trechos, seções, `explicit_headings`).

  **PORTÃO:** se falhar, parar e reportar.

**Checkpoint**: paridade 144/144 provada antes de qualquer rota ou tela.

---

## Phase 3: Backend — contrato e geometria

- [X] T007 [P] Criar `L/backend/app/schemas/organize.py` com `OrganizeLineInput`, `OrganizeRequest`,
  `OrganizeSegmentRead`, `OrganizeRead` e `OrganizeStatusRead` (data-model §1).
- [X] T008 Em `L/backend/app/routers/imports.py`, adicionar `GET /imports/organize/status` e
  `POST /imports/organize`:
  - `CurrentUser` e `Cache-Control: no-store`;
  - erros `{detail, code}`: `413 too_large`, `422 empty_text` e `503 unavailable`.
- [X] T009 Adicionar `bbox` a `DigitizeLineRead`, em `L/backend/app/schemas/digitize.py`, e passá-lo em
  `to_preview` (`L/backend/app/services/digitize_service.py`), vindo das caixas do motor.
  - Atualizar o motor falso dos testes para devolver caixas.
  - Acrescentar a asserção em `L/backend/tests/test_digitize_api.py`.
- [X] T010 Criar `L/backend/tests/test_organize_api.py` (banco `tmp_path`, textos fictícios), cobrindo:
  - **status:** disponível e indisponível (artefato ausente ou com SHA errado, via monkeypatch do caminho);
  - **resposta 200:**
    - nada se perde e `text == texto[start:end]`;
    - as seções são a junção dos trechos;
    - cabeçalhos explícitos são respeitados;
    - a política de referências da spec vale (referência ABNT, `p. 42 — comentário`, citação em linha própria);
    - linhas com `bbox` são aceitas;
  - **erros:** `413` por caracteres e por trechos; `422` para texto vazio; `401` sem sessão; `503` com o artefato
    ausente;
  - **sem efeitos colaterais:** nenhuma escrita no banco (contagem de estudos igual antes e depois) e nenhum texto
    em `caplog`;
  - **tempo:** p95 abaixo de 1 s nas páginas do fixture.

**Checkpoint**: contrato da API completo, com a 086 estendida de forma aditiva.

---

## Phase 4: User Story 1 — Organizar o texto digitalizado (P1) [MVP]

**Objetivo**: 4 editores preenchidos com os trechos originais, avisos e "Seções para conferir".
**Teste independente**: com o gateway falso, `organize()` monta exatamente as seções da resposta. Na tela, o
modo organizado aparece com aviso e lista de conferência.

- [X] T011 [P] [US1] Criar `L/frontend/src/types/organize.ts` com `OrganizeLine`, `OrganizeSegment`,
  `OrganizeResult`, `OrganizeStatus` e os códigos de erro. Acrescentar `bbox` em `DigitizeLine`
  (`L/frontend/src/types/digitize.ts`).
- [X] T012 [US1] Em `L/frontend/src/services/api.ts`, adicionar `getOrganizeStatus(signal)` e
  `organizeText(payload, signal)`.
- [X] T013 [US1] Criar `L/frontend/src/composables/useSectionOrganizer.ts`, com o gateway injetável (research
  R6, data-model §3):
  - `organize`, com cancelamento por `AbortController`, ignorando um segundo pedido enquanto o primeiro está em
    andamento (clique duplo);
  - `move`, `revert`, `edited`, `reviewItems` (com `movable`) e `reset`;
  - mapeamento de erros para português.
- [X] T014 [US1] Criar `L/frontend/src/components/OrganizedSectionsEditor.vue`:
  - 4 `textarea` rotuladas, ligadas por `v-model`;
  - no desktop, empilhadas;
  - abaixo de 768 px, um `tablist` com contagem de trechos para conferir por aba, navegação por setas e
    `aria-selected`;
  - tokens semânticos, alvos de 44 px e `:focus-visible`.
- [X] T015 [US1] Em `L/frontend/src/views/DigitizeNotebookView.vue`, na revisão:
  - consultar o status uma vez ao montar;
  - o botão "Organizar nas 4 seções" fica ao lado da escolha de seção, desativado com explicação se indisponível;
  - durante o pedido, mostrar um esqueleto no formato dos 4 editores;
  - no modo organizado: aviso permanente de sugestão, lista "Seções para conferir" com seletor "Mover para…" (ou
    "já editado") e `OrganizedSectionsEditor`;
  - mandar as linhas lidas, com `bbox`, junto do texto;
  - mostrar o aviso `single_section` quando vier na resposta (edge case "tudo numa seção só");
  - quando a leitura teve muitas linhas incertas, mostrar a dica de corrigir o texto antes de organizar (edge case
    "texto com muito erro");
  - esconder a lista "Linhas para conferir" do texto único enquanto o modo organizado estiver ativo. Ela volta ao
    voltar para o texto único.

**Checkpoint US1**: o texto revisado vira 4 seções sugeridas e revisáveis.

---

## Phase 5: User Story 2 — Desfazer e salvar com segurança (P1) [MVP]

- [X] T016 [US2] Em `L/frontend/src/composables/useDigitizeDraft.ts`:
  - integrar o `useSectionOrganizer`;
  - `save()` com as 4 seções no modo organizado e `source_response` sempre igual a `preview.text`;
  - `canSave` exigindo ao menos uma seção com texto;
  - `dirty` incluindo o modo organizado;
  - `reset()` desligando o modo organizado.
- [X] T017 [US2] Na view, adicionar:
  - "Voltar para texto único", com `window.confirm` quando houver edição, restaurando o `snapshot` exato;
  - foco no editor único ao voltar e na primeira seção ao organizar.
- [X] T018 [P] [US2] Criar `L/frontend/tests/feature-089-organizar-quatro-secoes.test.mjs` com testes do
  composable (gateway falso, textos fictícios):
  - a montagem inicial é igual às seções da resposta;
  - `move` com editores intactos remonta origem e destino na ordem original;
  - `move` com a origem editada remove a substring;
  - um trecho editado aparece com `movable` falso;
  - `revert` devolve o `snapshot` exato;
  - `edited` funciona;
  - um erro `503` vira mensagem;
  - `cancel` funciona.

  E testes do `useDigitizeDraft`: o payload do `save()` organizado e o bloqueio com as 4 seções vazias.

**Checkpoint US2**: fluxo completo, com organizar → mover → voltar → organizar → salvar.

---

## Phase 6: User Story 3 — Importação (P2)

- [X] T019 [US3] Em `L/frontend/src/composables/useImportDraft.ts`:
  - `organizeUnassigned()` acrescenta as seções sugeridas com `\n\n` e esvazia `unassigned_text`;
  - `undoOrganize()`;
  - descartar o snapshot numa nova prévia.

  O gateway da importação ganha `organize`.
- [X] T020 [US3] Em `L/frontend/src/views/ImportView.vue`, no painel "Conteúdo Não Classificado":
  - o botão "Organizar automaticamente" só aparece se a função estiver disponível;
  - "Desfazer organização" aparece enquanto houver snapshot;
  - aviso de sugestão.
- [X] T021 [P] [US3] No teste `feature-089-…`, cobrir:
  - `organizeUnassigned()` acrescenta e esvazia;
  - `undoOrganize()` restaura o estado exato;
  - uma nova prévia descarta o snapshot;
  - o botão não aparece sem texto não classificado (verificação da view).

**Checkpoint US3**: importação sem cabeçalhos distribuída e reversível.

---

## Phase 7: User Story 4 — Estados, temas e celular (P3)

- [X] T022 [US4] Revisar o CSS das telas tocadas:
  - só tokens, sem cores fixas;
  - ícones SVG;
  - `prefers-reduced-motion`;
  - hierarquia `h1 → h2 → h3`.

  No teste `feature-089-…`, verificar a ausência de cores hexadecimais e de emojis, `min-height: 44px`,
  `:focus-visible` e `role="tablist"` no componente.

---

## Phase 8: Validação e registro

- [X] T023 Rodar `pytest` (com `CADERNO_DATABASE_PATH` descartável), `npm test` e `npm run build`, e comparar com
  a linha de base do T001 (SC-007).
- [~] T024 Seguir o quickstart §3 e §4 num servidor de validação com banco temporário e porta própria:
  - p95 do `organize` nas 144 páginas (SC-001) e tempo de carga do artefato;
  - fluxos pela API;
  - artefato ausente (SC-005).

  Os itens visuais (temas, 320 px, teclado, celular) ficam listados para o usuário e não são marcados sem
  execução.
- [X] T025 Atualizar `L/docs/contexto/RETOMADA.md` e o `quickstart.md` com os resultados. Marcar as tarefas e
  criar **um** commit `feature — organizar nas 4 seções`, com o Leitorum e `specs/089-*`.

---

**Estado do T024 (2026-10-27):** a latência, os fluxos pela API e o artefato ausente foram validados pelo agente (quickstart §5). Pendentes com o usuário: os itens visuais e o celular.

## Dependencies & Execution Order

- **T001** → **Fase 2 (T002 → T003 → T004 → T005 → T006, portão)** → Fase 3 (T007 [P], depois T008, T009 e T010) →
  US1 → US2 → US3 → US4 → Fase 8.
- O T009 é independente das rotas novas, mas fica na fase 3 por ser contrato de backend.
- A US2 depende da US1, porque usa o mesmo composable e a mesma view.
- A US3 usa a API da fase 3 e pode rodar depois da US1.

## Cobertura (requisito → tarefas)

| Requisito | Tarefas |
| :--- | :--- |
| FR-001 | T005, T007, T008, T010 |
| FR-002 | T004, T005, T010, T013 |
| FR-003 | T004, T010 |
| FR-004 | T004, T010 |
| FR-005 | T003, T005, T006 |
| FR-006 | T013–T018 |
| FR-007 | T009, T011, T015 |
| FR-008 | T019–T021 |
| FR-009 | T015, T020 |
| FR-010 | T008, T010 |
| FR-011 | T005, T010, T015, T020, T024 |
| NR-001 | nenhuma migração; T025 confere |
| NR-002 | T004, T005 (só biblioteca padrão) |
| NR-003 | T005, T010 |
| NR-004 | T003 |
| NR-005 | T014, T022 |
| NR-006 | T001, T010, T023 |
| NR-007 | T015, T020, T022 |
| SC-001 | T010, T024 |
| SC-002 | T010, T013 |
| SC-003 | T002, T006 |
| SC-004 | T015, T017 |
| SC-005 | T010, T024 |
| SC-006 | T014, T022, T024 |
| SC-007 | T023 |
