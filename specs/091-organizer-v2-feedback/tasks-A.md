# Tasks — Fatia 091-A: Organizador v2 no Lugar do v1

**Input**:
- [spec.md](spec.md): US1, FR-001 a FR-004 (só `engine.version`), SC-001 e SC-007; decisão Q1;
- [plan-A.md](plan-A.md): §1 a §5.

**Escopo da fatia A**:
- `engine_v2.py`, cópia do motor de referência do EXP-025;
- `loader.py` passa a carregar o `organizer-v2.json`;
- paridade com os 192 casos do v2 e não regressão contra os 144 do v1.

Sem banco, sem migração e sem mudança de tela.

Caminhos relativos a `C:\Users\User\caderno`:
- `L/` = `caderno-leitura-0.1/`;
- `E25/` = `document-intelligence/experiments/EXP-025/`.

**Regras em todas as tarefas**:
- **Dados:** só fictícios (páginas MIT do EXP-023 e do EXP-024).
- **Banco:** o `pytest` roda com `CADERNO_DATABASE_PATH` descartável, mais `LEITORUM_STORAGE_ROOT=""` e
  `LEITORUM_SECONDARY_BACKUP_DIR=""`. Nenhum teste toca o banco ativo nem o `D:\`. Nenhum `alembic`.
- **Logs:** nunca com texto organizado.
- **`document-intelligence/`:** nada é alterado lá; artefato e fixture são só copiados.
- **Build:** não rodar `npm run build` em paralelo com o `pytest`.

---

## Phase 1: Setup

- [x] A001 Linha de base: `pytest` (635 aprovados e 1 pulado), `npm test` (653) e `npm run build` (ok).

## Phase 2: Artefatos e fixtures (plan-A §3)

- [x] A002 Copiar `E25/artifacts/organizer-v2.json` e `organizer-v2.sha256` para `L/backend/app/data/organizer/`.
  - conferir o SHA-256 `9f6530a32726d593142b7a2de3bce3efc1c0095abf3a91335364db6343978aee` nos bytes copiados;
  - conferir que o arquivo não tem quebra de linha.
- [x] A003 Copiar `E25/artifacts/parity-v2.json` para `L/backend/tests/fixtures/organizer-parity-v2.json` e conferir o
  SHA-256 `6726ddc4ce9049ec45f393fe84ef9412d70068cbb0c49819ade91e5713b71573`.
- [x] A004 Remover `L/backend/app/data/organizer/organizer-v1.json` e `organizer-v1.sha256`.
  - manter `L/backend/tests/fixtures/organizer-parity-v1.json`;
  - procurar referências restantes a `organizer-v1` no backend (`grep`) e listar as que ficam de propósito.
    **Ficam:** a docstring do `Model` no `engine.py` (cópia literal) e o fixture do v1 no teste de não regressão.

## Phase 3: Motor e carga (plan-A §1 e §2) — US1, FR-001 a FR-004

- [x] A005 Criar `L/backend/app/services/organizer/engine_v2.py` como cópia de `E25/harness/organizer_v2.py`.
  - **cabeçalho:** cópia literal do commit `f8ab9e0`; não editar sem repetir no experimento e regenerar o fixture;
  - **adaptações, só estas:**
    - o import passa a ser `from app.services.organizer import engine as org`;
    - saem o `sys.path` e o `ARTIFACT`;
    - `load(path)` vira `from_artifact(data: dict) -> OrganizerV2`, com as mesmas duas checagens.
- [x] A006 Atualizar `L/backend/app/services/organizer/loader.py`.
  - mudar `ARTIFACT`, `EXPECTED_SHA256` e `VERSION = "2"`;
  - construir o organizador por `engine_v2.from_artifact`;
  - atualizar o docstring (EXP-025, ADR-011);
  - conferir que o `ValueError` das checagens cai em `integrity_failed`.

## Phase 4: Testes (plan-A §4)

- [x] A007 Reescrever `L/backend/tests/test_organizer_parity.py` para o v2.
  - fixture e SHA-256 do v2; `artifact_sha256` igual a `loader.EXPECTED_SHA256`;
  - `status()` com `version: "2"`;
  - 192 de 192 casos com igualdade exata (SC-001);
  - **não regressão contra o v1:** nos 144 casos do fixture do v1, seções iguais em todos, e resultado idêntico em
    todo caso em que nenhuma pista dispara em nenhum trecho. Esperado: 140 casos sem pista, todos idênticos.
- [x] A008 Criar `L/backend/tests/test_organizer_v2.py`.
  - **pistas:** as 4 expressões e modos de `engine_v2.EXTRA_CUES` são iguais às do artefato instalado; `cue_values`
    dispara no exemplo fictício de cada pista e não dispara numa frase comum;
  - **comportamento:** uma página fictícia com `- A margem e o centro — Lúcia Dantas` põe essa linha em Referências;
  - **artefato adulterado** (cópia em `tmp_path`; `ARTIFACT` e `EXPECTED_SHA256` trocados por `monkeypatch` para o
    SHA recalculado): `extra_cues` alterado dá `integrity_failed`, e colunas novas fora do fim de `feature_names`
    também.
- [x] A009 Atualizar `L/backend/tests/test_organize_api.py`.
  - `version: "1"` passa a `"2"`;
  - o arquivo falso passa a se chamar `organizer-v2.json`;
  - os demais testes continuam sem mudança e verdes.

## Phase 5: Documentação (plan-A §5)

- [x] A010 Em `specs/089-organizar-quatro-secoes/contracts/organize-api.contract.md`:
  - versão `"2"` e SHA novo nos exemplos;
  - nota: "trocado para o v2 pela feature 091, fatia A (ADR-011)".
- [x] A011 Entrada da 091-A em `L/docs/contexto/RETOMADA.md`: o que mudou, como voltar ao v1 e a conferência
  pendente no serviço.

## Phase 6: Validação

- [x] A012 Rodar a validação completa, em sequência: `pytest` (variáveis descartáveis), depois `npm test`, depois
  `npm run build`. Comparar com a linha de base: o número de testes só pode subir, sem nenhum novo pulado.
  **Resultado:** `pytest` 646 aprovados e 1 pulado (+11); `npm test` 653; build ok.
- [x] A013 Revisar o diff da fatia:
  - nenhum arquivo do `document-intelligence/` alterado;
  - nenhum texto em log;
  - `engine.py` intocado.
- [x] A014 Marcar a fatia A como implementada no `plan-A.md` e nos checkboxes daqui.
  - **Sem commit:** pela regra 1 feature = 1 commit, o commit sai no fim da 091, depois das fatias B e C.

## Phase 7: Conferência no serviço real (com o usuário)

- [x] A015 O usuário reinicia o serviço `Leitorum`. Depois, eu confiro:
  - `GET /api/imports/organize/status` responde `version: "2"`;
  - pelo `127.0.0.1:8000`, organizar um texto fictício com `- A margem e o centro — Lúcia Dantas` põe a linha em
    Referências;
  - nenhum estudo salvo, nenhum acesso ao banco.

  **Resultado (28/10/2026):**
  - as duas primeiras tentativas de reinício não chegaram ao serviço. O processo seguia das 13:46, e o log do NSSM
    não tinha nenhum STOP;
  - na terceira (`Stop-Service` e `Start-Service` como administrador), o serviço subiu às 20:08:03;
  - o usuário abriu `/api/imports/organize/status` logado: `version "2"`;
  - a linha de referência em lista foi conferida no mesmo código e artefato, em processo separado, sem banco: foi
    para Referências.

---

## Dependências

- A001 → A002 a A004 → A005 → A006 → A007 a A009 → A012 → A013 → A014 → A015.
- A010 e A011 podem correr junto com a Phase 4.
