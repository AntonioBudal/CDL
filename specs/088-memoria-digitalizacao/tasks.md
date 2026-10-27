# Tasks: Digitalizar Caderno — Trava de Memória que Recusa Toda Leitura

**Input**: Design documents from `specs/088-memoria-digitalizacao/`
**Prerequisites**: [spec.md](spec.md) (aprovada), [plan.md](plan.md) (aprovado)

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode rodar em paralelo (arquivos distintos, sem dependência mútua)
- **[Story]**: história da spec (US1 = ler com a RAM física apertada; US2 = saber por que falhou)
- Caminhos relativos a `caderno-leitura-0.1/backend/`, salvo indicação

**Regras de toda a fatia**:

- só imagens sintéticas e banco em `tmp_path`;
- nunca abrir `backend/data/caderno.db` nem fotos reais;
- `pytest` sempre com `C:\Users\User\caderno\caderno-leitura-0.1\backend\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider`,
  rodado a partir de `caderno-leitura-0.1/backend` do worktree, depois de conferir que `app.__file__` aponta para ele.

---

## Phase 1: Setup

- [x] T001 Rodar os testes de digitalização como linha de base (`tests/test_digitize_api.py`,
  `tests/test_digitize_motor_smoke.py`) e anotar quantos passam e quantos são pulados. Esperado: o teste de leitura
  do motor real aparece como pulado ("pouca memória livre").

---

## Phase 2: Testes primeiro (devem falhar antes da Phase 3)

- [x] T002 [P] [US2] Em `tests/fake_motor.py`, adicionar o modo `noisy_crash`. Ele escreve no `stderr`, nesta
  ordem: uma linha de aviso com um caminho fictício de modelo, a linha `Livro de Teste` e `ValueError`. Depois sai
  com código 1. Atualizar a docstring da lista de modos.
- [x] T003 [US1] Em `tests/test_digitize_api.py`, criar a fixture `windows_memory(physical_mb, commit_mb)`.
  - Ela faz `monkeypatch` de `digitize_service.IS_WINDOWS = True` e de `digitize_service._windows_memory_status`.
  - Ela devolve uma `_MemoryStatus` com `ullAvailPhys` e `ullAvailPageFile` nos valores pedidos.
- [x] T004 [US1] Escrever os testes do D1 e do D2 em `tests/test_digitize_api.py`:
  - `test_windows_low_physical_but_ample_commit_reads`: **a causa**. Física 1 200 MB, commit 18 000 MB, sem
    `LEITORUM_DIGITIZE_MIN_FREE_MB` (`delenv`) ⇒ `200`, e o rastro do motor falso existe;
  - `test_windows_low_commit_is_refused_and_logged`: física 6 000 MB, commit 1 024 MB ⇒ `503 low_memory`, motor
    não chamado, `caplog` com `commit`, `1024 MB` e `2304 MB`;
  - `test_min_free_env_applies_to_commit`: variável `20000`, commit 18 000 MB ⇒ `503 low_memory`;
  - `test_default_min_free_is_peak_plus_reserve`: sem a variável, `get_digitize_min_free_bytes() == 2304 * 2**20`.
- [x] T005 [US2] Escrever os testes do D4 em `tests/test_digitize_api.py`:
  - `test_engine_failure_logs_exit_code_and_type`: modo `crash` ⇒ `caplog` com `código 1` e `RuntimeError`;
  - `test_engine_failure_log_ignores_noisy_stderr`: modo `noisy_crash` ⇒ `caplog` com `ValueError`, sem
    `Livro de Teste` e sem o caminho fictício;
  - `test_motor_error_type` (unitário em `tmp_path`): arquivo ausente, arquivo vazio e arquivo só com ruído ⇒
    `"desconhecido"`; última linha válida ⇒ o tipo.
- [x] T006 [US1] Ajustar os testes existentes que substituem `free_memory_bytes` para substituir
  `available_memory`:
  - `test_low_memory_is_refused_before_engine`;
  - `test_unmeasurable_memory_does_not_block`;
  - `test_free_memory_is_measured_on_this_machine`, que passa a exigir `measure == "commit"` no Windows.
- [x] T007 Rodar os testes de digitalização e confirmar que os novos falham pelos motivos esperados (função ou
  atributo ausente, mínimo antigo, log ausente).

---

## Phase 3: Implementação

- [x] T008 [US1] Em `app/core/config.py`, mudar `DEFAULT_DIGITIZE_MIN_FREE_MB` para `2304`, com um comentário
  sobre a origem (pico comprometido de 1 205 MB mais 1 GiB), e atualizar a docstring de
  `get_digitize_min_free_bytes()` (D2).
- [x] T009 [US1] Em `app/services/digitize_service.py`, implementar o D1:
  - `IS_WINDOWS`;
  - `_windows_memory_status()`;
  - `MemoryReading`;
  - `available_memory()`, no lugar de `free_memory_bytes()`;
  - a comparação em `preview()` usando `reading.available`;
  - a docstring do módulo citando a medida.
- [x] T010 [US2] Em `app/services/digitize_service.py`, implementar o D3: o log `WARNING` da recusa por memória,
  com a medida, o disponível e o mínimo em MB.
- [x] T011 [US2] Em `app/services/digitize_service.py`, implementar o D4:
  - a constante `MOTOR_LOG`;
  - a função `motor_error_type()`, que lê no máximo 4 KB e aceita só uma linha com formato de identificador;
  - o log `WARNING` com o código de saída e o tipo, emitido antes dos `raise` por código diferente de 0.
- [x] T012 [P] [US1] Em `tests/test_digitize_motor_smoke.py`, trocar o `skipif` de memória pela regra do serviço
  (`available_memory()` abaixo de `get_digitize_min_free_bytes()`) e atualizar a docstring (D5).
- [x] T013 Rodar os testes de digitalização: todos os da Phase 2 passam.

---

## Phase 4: Documentos

- [x] T014 [P] Acrescentar notas "alterado pela 088" na 086 (D6), sem reescrever o histórico:
  - `specs/086-digitalizar-caderno-estudo/research.md` R8;
  - `plan.md` (linha da recusa);
  - `contracts/digitize-api.contract.md` (linha do `503 low_memory`);
  - `quickstart.md` (linha "Memória (FR-011)").
- [x] T015 Atualizar o **Status** de `specs/088-memoria-digitalizacao/spec.md` com o resultado da validação.

---

## Phase 5: Validação

- [x] T016 Rodar o `pytest` completo do backend. Esperado: tudo verde, exceto a falha ambiental conhecida
  `test_iniciar_rejects_relative_database_path`. Comparar a contagem com a linha de base da T001.
- [x] T017 Rodar o teste do motor real com `LEITORUM_MOTOR_PYTHON` apontando para o motor instalado no checkout
  principal. Ele deve rodar, não ser pulado, e passar.
- [x] T018 Rodar o script de reprodução do diagnóstico (página sintética, mínimo padrão, motor real,
  `CADERNO_DATABASE_PATH` em pasta temporária) ⇒ `OK` com 3 linhas (SC-001).
- [x] T019 Conferir no `caplog` dos testes que não aparece texto lido, nome do arquivo enviado nem caminho
  temporário (SC-003).

---

## Phase 6: Entrega

- [x] T020 Apresentar ao usuário o diff, os resultados da T016 à T019 e a validação pendente: enviar uma foto pela
  tela `/digitalizar` depois de reiniciar o `iniciar.py`.
- [x] T021 Só com o aceite do usuário: um commit atômico com spec, plano, tarefas, código, testes e notas da 086,
  com a mensagem `correção — digitalização usa memória comprometível` e a linha de coautoria.

---

## Dependências

- T002 a T006 antes de T007; T007 antes da Phase 3.
- T009 antes de T010 e T011, que mexem no mesmo arquivo e por isso rodam em sequência.
- T012 depende de T009, porque usa `available_memory`.
- Phase 5 depois das Phases 3 e 4; T021 só depois do aceite da T020.
