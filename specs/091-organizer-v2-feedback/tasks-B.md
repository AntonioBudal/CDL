# Tasks — Fatia 091-B: Registro Silencioso do Feedback (`leitorum-feedback/1`)

**Input**:
- [spec.md](spec.md): US2 e US4; FR-005 a FR-010 e FR-016; SC-002, SC-003, SC-006 e SC-007; decisões Q2, Q4 e Q5;
- [plan-B.md](plan-B.md): §1 a §7 e "Ambiente real".

**Escopo da fatia B**:
- migração `0033`, com as tabelas `organizer_feedback` e `organizer_user_state` (esta só é criada);
- diff do EXP-024 portado (`feedback_signal.py`);
- montagem do registro e a rota `POST /api/studies/{id}/organizer-feedback`;
- envio silencioso pela digitalização e pela importação organizada;
- parágrafo na página "Sobre".

Caminhos relativos a `C:\Users\User\caderno`:
- `L/` = `caderno-leitura-0.1/`;
- `E24/` = `document-intelligence/experiments/EXP-024/`.

**Regras em todas as tarefas**:
- **Dados:** testes só em `tmp_path`, com textos fictícios.
- **Ambiente do `pytest`:** `CADERNO_DATABASE_PATH` descartável, `LEITORUM_STORAGE_ROOT=""` e
  `LEITORUM_SECONDARY_BACKUP_DIR=""`.
- **Banco ativo:** nenhum `alembic` nem acesso ao banco ativo ou ao `D:\` antes da Phase 7.
- **Logs:** só códigos e contagens; nunca texto, título ou id de estudo.
- **`document-intelligence/`:** nada é alterado lá; o diff é só copiado.
- **Build:** não rodar `npm run build` em paralelo com o `pytest`.

---

## Phase 1: Setup

- [x] B001 Linha de base: `pytest` 646 aprovados e 1 pulado, `npm test` 653 e `npm run build` ok (medida da A012, mesma árvore).

## Phase 2: Migração e modelos (plan-B §1)

- [x] B002 Criar `L/backend/migrations/versions/0033_organizer_feedback.py` (`down_revision = "0032_media_completed_seen"`).
  - criar `organizer_feedback`:
    - colunas, FKs com `CASCADE` e `study_id` único;
    - CHECK de `origin`;
    - índice `(user_id, reviewed)`;
  - criar `organizer_user_state`;
  - `downgrade` apaga as duas.
- [x] B003 Criar `L/backend/app/models/organizer_feedback.py` com `OrganizerFeedback` e `OrganizerUserState`.
  - seguir o padrão de `encrypted_media.py` (`UTCDateTime`, `utc_now`);
  - registrar onde os modelos são importados para o metadata.
- [x] B004 Criar `L/backend/tests/test_migration_0033.py`, no molde do `test_migration_0032.py`:
  - sobe e desce num banco descartável;
  - colunas, índice e unicidade de `study_id`;
  - com `PRAGMA foreign_keys=ON`, apagar o estudo apaga o registro.

## Phase 3: Backend (plan-B §2 a §4) — US2, US4

- [x] B005 Criar `L/backend/app/services/organizer/feedback_signal.py` como cópia literal de `E24/harness/diff_signal.py`.
  - cabeçalho no padrão do `engine.py`, com o commit de origem;
  - não editar sem repetir no experimento.
- [x] B006 Criar `L/backend/tests/test_feedback_signal.py` portando os casos de `E24/tests/test_diff_signal.py`:
  - trechos mantido, movido, editado e apagado;
  - leitura `ocr`, `rewrite` e `ambiguous`;
  - `to_ldf_corrections` e `to_organizer_patch`;
  - os `DEFAULTS` iguais aos do EXP-024.
- [x] B007 Criar `L/backend/app/schemas/organizer_feedback.py` (Pydantic) com o corpo da rota:
  - `origin` ∈ `digitize`, `import`;
  - `organizer` opcional:
    - `engine` com `version`, `sha256` e `adapter` (`null`);
    - `outcome` ∈ `saved`, `reverted`;
    - `text` com até 50 000 caracteres;
    - até 400 `segments`, com `0 ≤ start < end ≤ len(text)` e `section` entre as 4.
- [x] B008 Criar `L/backend/app/services/organizer/feedback.py` com `record_feedback(session, study, user_id, body) -> str`.
  - **pré-condições:** estudo do usuário, criado há no máximo 10 minutos e sem registro; `digitize` exige
    `source_response`;
  - **montagem do documento** (plan-B §3):
    - `saved_sections` lidas do estudo;
    - `units` e `patch` por `align_units` e `to_organizer_patch`;
    - `reading` por `align_reading` e `to_ldf_corrections` (`line-{k}`, `author: "leitor"`), com teto de 400 linhas
      lidas;
    - **desvio:** teto de **80** linhas lidas. Medido: 40 linhas levam 0,4 s; 120, 2,6 s; 400, 26,6 s. Uma página
      de caderno tem em torno de 40 linhas;
  - **`reviewed`** = organização com `outcome: "saved"`;
  - **teto de 256 KB:** sem `reading` primeiro e, se ainda passar, devolve `too_large` sem gravar;
  - **códigos:** `recorded`, `exists`, `stale`, `too_large`, `no_source`.
- [x] B009 Criar a rota `POST /api/studies/{study_id}/organizer-feedback` em `L/backend/app/routers/studies.py` (ou num
  router novo `organizer_feedback.py`, se o de estudos estiver grande demais).
  - estudo de outro usuário dá `404`; corpo inválido dá `422`; o resto, `204`;
  - exceção interna é capturada, vira o código `error` no log e responde `204`;
  - uma linha de log por pedido: código, trechos, correções e bytes.
- [x] B010 Criar `L/backend/tests/test_organizer_feedback_api.py`:
  - **caminhos que gravam (SC-002):**
    - digitalizado sem organização: só `reading`;
    - digitalizado e organizado: `organizer` e `reading`, `reviewed = true`;
    - importado e organizado: só `organizer`;
    - organização revertida: `outcome: "reverted"`, `reviewed = false`, sem `saved_sections`;
  - **caminhos que não gravam:**
    - estudo de outro usuário (`404`);
    - estudo com mais de 10 minutos (relógio por `monkeypatch`);
    - segundo envio (`exists`);
    - `digitize` sem `source_response`;
    - corpo inválido (`422`);
  - **documento:**
    - `schema`, chaves esperadas;
    - `saved_sections` igual ao estudo;
    - uma correção `ocr` vira `human_corrections`;
    - uma reescrita entra só na contagem, sem texto;
  - **teto:** página fictícia grande sai sem `reading`; acima disso, `too_large` e nada gravado;
  - **falha forçada** (`monkeypatch` em `record_feedback`): `204`, estudo intacto e nada gravado (SC-003);
  - **logs:** nenhum texto fictício nem título (SC-006).
- [x] B011 Criar `L/backend/tests/test_organizer_feedback_cascade.py`: o registro some quando
  - o estudo é excluído de vez;
  - a lixeira é esvaziada;
  - o livro é excluído de vez;
  - a conta é excluída (`delete_account_permanently`).

  Além disso, o ZIP de portabilidade não traz nada do registro (FR-008).

  **Acréscimo:** `delete_account_permanently` apaga as duas tabelas de forma explícita, no padrão das outras tabelas
  do usuário, além da cascata.

## Phase 4: Frontend (plan-B §5)

- [x] B012 Em `L/frontend/src/types/organize.ts`, os tipos `OrganizerFeedbackRequest` e `OrganizerSuggestion`. Em
  `L/frontend/src/services/api.ts`, a função `sendOrganizerFeedback(studyId, payload)`.
- [x] B013 Em `useSectionOrganizer.ts`:
  - guardar `engine` e os trechos com `start`, `end`, `section`, `confidence` e `review`;
  - `suggestion()` devolve a sugestão com o `outcome` atual, ou `null`;
  - `revert()` guarda a última sugestão como `reverted`, e uma nova organização a substitui;
  - `reset()` limpa tudo.
- [x] B014 Em `useDigitizeDraft.ts`, o gateway ganha `sendFeedback?` opcional.
  - no `save()`, depois do `createStudy` e da foto, enviar `{ origin: "digitize", organizer: organizer.suggestion() }`;
  - o envio não bloqueia o salvamento, e o `catch` é silencioso, com comentário (FR-007);
  - a `DigitizeNotebookView` passa `api.sendOrganizerFeedback`.
- [x] B015 Em `useImportDraft.ts`:
  - `organizeUnassigned()` guarda `engine`, `text` e `segments`;
  - `undoOrganize()` marca a sugestão como `reverted`;
  - `save()` envia `{ origin: "import", organizer }` só se houve organização;
  - a `ImportView` passa o gateway.
- [x] B016 Testes de frontend, nos arquivos de teste existentes dos composables:
  - digitalização organizada, digitalização sem organizar, organização revertida e importação organizada mandam o
    payload esperado;
  - importação sem organizar não manda nada;
  - falha no `sendFeedback` deixa o estudo salvo (`phase = 'saved'`) e nenhuma mensagem;
  - nada é enviado se o `createStudy` falha.

## Phase 5: Página "Sobre" e documentação (plan-B §5 e §7)

- [x] B017 Em `L/frontend/src/views/AboutView.vue`, na seção de privacidade, este parágrafo (**texto para você
  revisar antes da implementação**):

  > Quando você digitaliza uma página ou usa "Organizar nas 4 seções", o Leitorum guarda localmente, junto do
  > estudo, o que foi sugerido e o que você corrigiu, para melhorar a organização. Esses dados não saem do seu
  > computador e são apagados junto com o estudo.

  Teste: o texto aparece na página.
- [x] B018 Criar `specs/091-organizer-v2-feedback/contracts/organizer-feedback.contract.md`, com a rota, o corpo, os
  códigos e o esquema `leitorum-feedback/1`.
- [x] B019 Criar `specs/091-organizer-v2-feedback/data-model.md`, com as duas tabelas.
- [x] B020 Atualizar `L/docs/contexto/AMBIENTE-E-VALIDACAO.md` (migração `0033`) e `L/docs/contexto/RETOMADA.md`
  (entrada da 091-B).

## Phase 6: Validação

- [x] B021 Validação completa, em sequência: `pytest` (variáveis descartáveis), `npm test` e `npm run build`.
  - comparar com a linha de base: os testes só sobem, sem nenhum pulado novo;
  - conferir que a lista de rotas autorizadas tem a rota nova, se houver contrato de rotas (como nas features 076
    e 081).

  **Resultado:** `pytest` 674 aprovados e 1 pulado (+28); `npm test` 662 (+9); build ok. Os contratos 076 e 081
  são de rotas de tela; a fatia não cria tela nova.
- [x] B022 Revisar o diff da fatia:
  - nenhum arquivo do `document-intelligence/` alterado;
  - `engine.py` e `engine_v2.py` intocados;
  - nenhum texto em log;
  - nenhuma pós-correção de leitura (FR-016).
- [x] B023 Marcar a fatia B como implementada (plano e checkboxes). Sem commit: ele sai no fim da 091.

## Phase 7: Ambiente real (com o usuário)

- [x] B024 Você para o serviço `Leitorum` como administrador. Eu confiro duas coisas: o estado `Stopped` e o evento
  de STOP do NSSM, com o horário.
- [x] B025 Snapshot do banco do D: pela API de backup, para `D:\Leitorum\backups\caderno-pre-migracao-<data>.db`.
  - `PRAGMA integrity_check` = `ok`;
  - segunda cópia conferida por SHA-256;
  - revisão `0032_media_completed_seen` confirmada antes de migrar.
- [x] B026 `alembic upgrade head` no banco do D:, com as variáveis apontando de propósito para ele. Confirmar a
  revisão `0033_organizer_feedback` e as duas tabelas vazias.
  **Resultado B024–B026 (28/10/2026):**
  - **Parada:** os dois primeiros pedidos não chegaram ao serviço. A parada valeu às 20:38:20, conferida pelo
    `Get-Service`, pelo log do NSSM e pela porta 8000 livre.
  - **Antes da migração** (só leitura): revisão `0032`, `quick_check` ok, WAL vazio.
  - **Migração:** o auto mode do Claude Code bloqueou a primeira tentativa. O usuário autorizou no chat, e a
    migração rodou às 20:42.
  - **Snapshot:** `caderno-pre-migracao-20261028-234228.db` (revisão `0032`), com `quick_check` e
    `foreign_key_check` ok e o mesmo SHA-256 nas três cópias:
    - `D:\Leitorum\db\backups`;
    - `D:\Leitorum\backups`, copiado depois;
    - `Documents\Leitorum-backups`.
  - **Banco:** em `0033_organizer_feedback`, `quick_check` ok, sem FK órfã, as duas tabelas vazias.
  - **Lição:** definir `CADERNO_DATABASE_PATH` desliga a regra da raiz. Por isso o snapshot foi para
    `D:\Leitorum\db\backups` e não para `D:\Leitorum\backups`. Na próxima, rodar só com o `.env`, sem essa
    variável.
- [x] B027 Você religa o serviço. Depois, salva um estudo pela digitalização ou pela importação organizada, com o
  texto que preferir. Eu confiro **só contagens**, nunca o conteúdo:
  - 1 registro novo;
  - origem;
  - `reviewed`;
  - tamanho em bytes;
  - presença das partes `organizer` e `reading`.

  **Resultado (28/10/2026):**
  - o serviço voltou às 20:45:30;
  - o usuário digitalizou um estudo de teste;
  - conferência numa cópia temporária pela API de backup, apagada no fim, **só com contagens**:
    - 1 registro, origem `digitize`, `reviewed = true`, 1 920 bytes, esquema `leitorum-feedback/1`;
    - organizador na versão 2, com o SHA-256 do v2, desfecho `saved`: 4 trechos, todos mantidos, sem movimentos;
    - leitura: 13 linhas, todas iguais ao lido, sem correções;
    - estado do adaptador vazio.

---

## Dependências

- B001 → B002 → B003 → B004 → B005 → B006 → B007 → B008 → B009 → B010 → B011.
- B012 → B013 → B014 e B015 → B016.
- A Phase 4 pode começar depois da B009, porque o contrato da rota já está fixo.
- B017 a B020 podem correr junto com a Phase 4.
- B021 → B022 → B023 → B024 → B025 → B026 → B027.
