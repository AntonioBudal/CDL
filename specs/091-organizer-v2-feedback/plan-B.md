# Plano Técnico da Fatia 091-B: Registro Silencioso do Feedback (`leitorum-feedback/1`)

**Feature**: `091-organizer-v2-feedback`, fatia B | **Date**: 2026-10-28 | **Spec**: [spec.md](spec.md)

**Base**:
- [spec.md](spec.md): US2 e US4; FR-005 a FR-010 e FR-016; SC-002, SC-003, SC-006 e SC-007; decisões Q2, Q4 e Q5;
- referência do diff: `document-intelligence/experiments/EXP-024/harness/diff_signal.py` (commit `f1f5c8d`).

**Status**: Concluído em 2026-10-28 ([tasks-B.md](tasks-B.md), B001 a B027). O banco do D: está em `0033`, e o primeiro
registro real foi conferido só por contagens. Desvio: teto de 80 linhas lidas em vez de 400 (B008).

---

## Summary

1. Depois de salvar um estudo pela digitalização ou depois de "Organizar nas 4 seções", o navegador manda **num
   segundo pedido**, em silêncio, o que o organizador sugeriu. O envio é como o da foto de conferência da 090-C:
   uma falha nunca desfaz o estudo nem aparece ao leitor.
2. O servidor monta o registro `leitorum-feedback/1` **a partir do estudo salvo**, sem confiar no cliente para as
   seções nem para o texto lido:
   - **organizador:** cada trecho sugerido é procurado nas 4 seções salvas e marcado como mantido, movido, editado
     ou apagado;
   - **leitura (só na digitalização):** cada linha de `source_response` é alinhada ao texto salvo, e as correções de
     leitura viram `human_corrections` do LDF 2.0.
3. **Uma migração (`0033`)** cria as duas tabelas da feature: `organizer_feedback`, usada aqui, e
   `organizer_user_state`, vazia até a fatia C. Assim o banco do D: passa por uma única parada.
4. Um parágrafo na página "Sobre" explica o registro local (Q2).
5. A leitura não muda: nenhuma pós-correção (FR-016).

## Technical Context

- **Backend:**
  - Python 3.13, FastAPI, SQLAlchemy 2, Alembic e SQLite, com `PRAGMA foreign_keys=ON` (já ligado em
    `app/db/session.py`);
  - só biblioteca padrão para o diff (`difflib`, `unicodedata`, `re`).
- **Frontend:** Vue 3 e TypeScript; composables `useSectionOrganizer`, `useDigitizeDraft` e `useImportDraft`.
- **Custo:** o registro roda num pedido separado, depois do salvamento, então não atrasa o estudo.
  - o alinhamento da leitura é O(linhas × trechos), com teto de 400 linhas lidas (o mesmo teto de unidades do
    organizador);
  - acima disso, o registro sai sem a parte de leitura.
- **Tamanho:** teto de 256 KB por registro (FR-009). Acima, sai sem a parte de leitura; se ainda passar, o registro
  não é gravado e o log leva só o código.

## Constitution Check

| Regra | Como a fatia cumpre |
| :--- | :--- |
| Privacidade (AGENTS §1) | o registro fica no banco local, como o estudo, e não sai para exportação nem para o chat; testes só com textos fictícios; logs só com códigos e contagens |
| Banco ativo (AGENTS §2) | migração `0033` no banco do D: só com o serviço parado, snapshot verificado e sua aprovação (tarefa final, como a C036) |
| Spec Kit fatiado (§4) | plano → tarefas → implementação, com aprovação em cada um |
| Commit (§6) | um commit no fim da 091 |
| Pós-correção desligada (FR-016) | nenhum código da fatia altera o texto lido ou a revisão |

## Design

### 1. Migração `0033_organizer_feedback`

**`organizer_feedback`:**

| Coluna | Tipo | Regra |
| :--- | :--- | :--- |
| `id` | Integer PK | |
| `user_id` | String(36) | FK `users.id`, `ON DELETE CASCADE` |
| `study_id` | Integer | FK `studies.id`, `ON DELETE CASCADE`, **único** (um registro por estudo) |
| `schema` | String(32) | `'leitorum-feedback/1'` |
| `origin` | String(12) | CHECK `IN ('digitize', 'import')` |
| `reviewed` | Boolean | organização salva, não revertida (Q4); é o que a fatia C conta |
| `artifact_sha256` | String(64) | do artefato que fez a sugestão; vazio sem organização |
| `payload` | Text | JSON da §3 |
| `size_bytes` | Integer | |
| `created_at` | DateTime | |

Índice `(user_id, reviewed)`.

**`organizer_user_state`** (só criada; a fatia C a usa):

| Coluna | Tipo | Regra |
| :--- | :--- | :--- |
| `user_id` | String(36) PK | FK `users.id`, `ON DELETE CASCADE` |
| `artifact_sha256` | String(64) | |
| `reviewed_count` | Integer | |
| `state` | Text | JSON |
| `updated_at` | DateTime | |

- O `downgrade` apaga as duas tabelas.
- Modelos em `app/models/organizer_feedback.py`, registrados como os outros.
- O `CASCADE` cobre todos os caminhos de exclusão definitiva, sem código novo neles:
  - estudo excluído, um a um ou ao esvaziar a lixeira;
  - livro excluído, que leva capítulos e estudos;
  - conta excluída.

  Cada caminho ganha um teste (§6).

### 2. `app/services/organizer/feedback_signal.py`

- **Origem:** cópia literal de `diff_signal.py` do EXP-024, com o mesmo tipo de cabeçalho do `engine.py`: não
  editar sem repetir no experimento.
- **O que se usa:**
  - `align_units` e `to_organizer_patch`, para o organizador;
  - `align_reading` e `to_ldf_corrections`, para a leitura;
  - os limiares `DEFAULTS` do EXP-024 (cobertura 0,6; leitura até 0,35; reescrita acima de 0,6 ou com 2 palavras
    novas), sem mudança.
- Nenhuma função grava ou registra texto.

### 3. `app/services/organizer/feedback.py` e o documento `leitorum-feedback/1`

`record_feedback(session, study, user, request) -> code`. Pré-condições (senão, devolve um código e não grava):
- o estudo é do usuário e foi criado há no máximo 10 minutos;
- ainda não tem registro;
- `origin = digitize` exige `source_response` não vazio.

```json
{
  "schema": "leitorum-feedback/1",
  "created_at": "2026-10-28T20:30:00Z",
  "origin": "digitize",
  "organizer": {
    "engine": { "version": "2", "sha256": "9f6530a3…", "adapter": null },
    "outcome": "saved",
    "text": "texto organizado, como foi enviado ao organizador",
    "segments": [{ "index": 0, "start": 0, "end": 37, "section": "summary", "confidence": 0.81, "review": false }],
    "saved_sections": { "summary": "…", "explanation": "…", "concepts": "…", "references": "…" },
    "units": [{ "index": 0, "outcome": "kept", "final": "summary", "ratio": 1.0 }],
    "patch": [{ "op": "replace", "path": "/segments/7/section", "value": "references" }]
  },
  "reading": {
    "lines": 31,
    "kinds": { "same": 20, "ocr": 8, "rewrite": 2, "ambiguous": 1 },
    "human_corrections": [{
      "id": "corr-line-4", "author": "leitor", "timestamp": "…", "reason": "ocr-fix",
      "target": { "collection": "recognition.lines", "id": "line-4" },
      "ops": [{ "op": "replace", "path": "/text", "value": "linha revisada" }]
    }]
  }
}
```

- **`organizer`:** só existe se houve organização.
  - com `outcome: "reverted"`, ficam sem `saved_sections`, `units` e `patch`, e `reviewed = false`;
  - `saved_sections` é a cópia das 4 seções **no momento do salvamento** (Q5), lida do estudo no banco;
  - `units` e `patch` saem de `align_units` contra essas seções.
- **`reading`:** só existe na digitalização.
  - as linhas de `source_response` (`line-{k}`, `k` = posição na lista de linhas) são alinhadas às seções salvas;
  - só as do tipo `ocr` viram `human_corrections`;
  - as reescritas entram só na contagem, sem texto (spec, casos de borda).
- **`author`:** é `"leitor"`, porque o registro já guarda `user_id` na coluna.
- **Teto (FR-009):** acima de 256 KB, sai sem `reading`; se ainda passar, não grava (`too_large`).

### 4. API: `POST /api/studies/{study_id}/organizer-feedback`

- **Corpo:** `{ "origin": "digitize" | "import", "organizer": { "engine": {...}, "outcome": "saved" | "reverted", "text": "...", "segments": [...] } | null }`.
- **Validação com Pydantic:**
  - `text` com até 50 000 caracteres;
  - até 400 trechos;
  - `start` e `end` dentro do texto.
- **Respostas:**
  - `204` sempre que o pedido for válido, gravando ou não (já existe registro, estudo antigo, origem sem texto
    lido);
  - `404` para estudo de outro usuário;
  - `422` para corpo inválido.
- O resultado não muda a tela: o cliente ignora a resposta.
- **Log:** uma linha com o código (`recorded`, `exists`, `stale`, `too_large`, `no_source`, `error`) e contagens
  (trechos, correções, bytes). Nunca texto, título nem id do estudo.
- **Erro interno:** é capturado, vira `error` no log e responde `204`. O estudo já está salvo e nada é desfeito.

### 5. Frontend

**`useSectionOrganizer`:**
- guarda, ao organizar, o `engine` da resposta e os trechos com `start`, `end`, `section`, `confidence` e `review`
  (hoje guarda só `index`, `text` e `review`);
- `suggestion()` devolve `{ engine, outcome, text, segments }`, ou `null` se nunca organizou;
- ao **voltar para o texto único**, a última sugestão é guardada com `outcome: "reverted"`. Uma nova organização
  a substitui.

**`useDigitizeDraft.save()`:** depois do `createStudy` e da foto, chama `gateway.sendFeedback?.(id, payload)` sem
`await` bloqueante. O `catch` vazio é de propósito, com comentário. Payload:
- `origin: "digitize"`;
- `organizer: organizer.suggestion()`, com `outcome: "saved"` se ainda estiver organizado.

Na digitalização, o registro sai sempre, organizada ou não, porque a leitura tem diff.

**`useImportDraft`:**
- `organizeUnassigned()` guarda também `engine`, `text` e `segments` da resposta;
- `undoOrganize()` marca a sugestão como `reverted`;
- `save()` só envia se houve organização, com `origin: "import"`.

**Fiação:**
- `api.sendOrganizerFeedback` em `services/api.ts`;
- tipos em `types/organize.ts`;
- as views passam o gateway.

**`AboutView`:** um parágrafo na seção de privacidade (texto final nas tarefas, para sua revisão):

> Quando você digitaliza uma página ou usa "Organizar nas 4 seções", o Leitorum guarda localmente, junto do
> estudo, o que foi sugerido e o que você corrigiu, para melhorar a organização. Esses dados não saem do seu
> computador e são apagados junto com o estudo.

### 6. Testes

**Backend** (banco descartável em `tmp_path`, textos fictícios):

- **`test_feedback_signal.py`:**
  - os casos do `test_diff_signal.py` do EXP-024, portados: trecho mantido, movido, editado e apagado; leitura `ocr`,
    `rewrite` e `ambiguous`; `human_corrections` e patch;
  - igualdade com a referência.
- **`test_organizer_feedback_api.py`:**
  - os 4 caminhos de SC-002, mais os que não gravam: importado sem organização (o cliente não envia), estudo de
    outro usuário, estudo com mais de 10 minutos, segundo envio, origem `digitize` sem `source_response`;
  - documento válido: chaves esperadas, `reviewed` certo, `saved_sections` igual ao estudo;
  - teto de 256 KB: sem `reading` e, se ainda passar, `too_large`;
  - erro interno forçado (`monkeypatch`): `204`, estudo intacto, nada gravado (SC-003);
  - logs da suíte sem nenhum texto fictício (SC-006).
- **`test_organizer_feedback_cascade.py`:** o registro some com o estudo excluído, com a lixeira esvaziada, com o
  livro excluído e com a conta excluída.
- **`test_migration_0033.py`** (como o `test_migration_0032.py`): `0033` sobe e desce num banco descartável. Com
  `PRAGMA foreign_keys` ligado, as FKs conferem.
- **Exportação:** o ZIP de portabilidade não contém `organizer_feedback` (FR-008).

**Frontend** (`npm test`, gateways falsos):
- digitalização organizada, digitalização sem organizar, organização revertida e importação organizada mandam o
  payload esperado;
- importação sem organizar não manda nada;
- uma falha no `sendFeedback` deixa `phase = 'saved'` e nenhuma mensagem de erro;
- o `sendFeedback` só é chamado depois do `createStudy` bem-sucedido.

### 7. Documentação

- `contracts/organizer-feedback.contract.md` (novo): rota, corpo, códigos e o esquema `leitorum-feedback/1`;
- `data-model.md` da 091: as duas tabelas;
- `RETOMADA.md`: entrada da 091-B;
- `AMBIENTE-E-VALIDACAO.md`: a migração `0033` na lista.

## Ambiente real (tarefas finais, com você)

Como na C036:
1. Você para o serviço como administrador. Eu confiro `Stopped` pelo `Get-Service` e pelo log do NSSM.
2. Snapshot consistente do banco do D: pela API de backup, com conferência de integridade e segunda cópia por
   SHA-256.
3. `alembic upgrade head` no banco do D: (`0032` → `0033`), com as variáveis apontando de propósito para ele.
4. Você religa o serviço.
5. Conferência:
   - você digitaliza ou organiza um estudo de teste (seu, com texto que preferir);
   - eu confiro **só contagens**: 1 registro novo, com o tamanho e o `reviewed` esperados;
   - nunca o conteúdo.

## Fases (detalhadas no `tasks-B.md`)

1. Linha de base dos testes.
2. Migração e modelos.
3. `feedback_signal`, `feedback` e a rota.
4. Frontend.
5. Página "Sobre" e documentação.
6. Validação completa.
7. Ambiente real.

## Riscos

| Risco | Mitigação |
| :--- | :--- |
| Registro guardar texto pessoal em mais um lugar | mesmo banco local e mesma privacidade do estudo; apagado em cascata; fora da exportação; Q5 aprovada |
| Pedido do feedback falhar em silêncio e ninguém saber | log com código e contagens por pedido; a fatia C e o futuro EXP vão contar os registros |
| Cliente forjar um registro | só o dono do estudo; só nos 10 minutos depois da criação; um por estudo; seções e texto lido vêm do banco, não do cliente |
| Diff lento em página grande | pedido separado do salvamento; teto de 400 linhas lidas; teto de 256 KB |
| Migração no banco do D: | um snapshot verificado antes; serviço parado conferido pelo log do NSSM (lição da A015) |
