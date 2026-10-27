# Implementation Plan: Digitalizar Caderno — Trava de Memória que Recusa Toda Leitura

**Branch**: `088-memoria-digitalizacao` | **Date**: 2026-10-27 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/088-memoria-digitalizacao/spec.md` (aprovada em 2026-10-27)

## Summary

A trava de memória da digitalização passa a medir, no Windows, a **memória comprometível disponível**
(`ullAvailPageFile` de `GlobalMemoryStatusEx`), em vez da RAM física (`ullAvailPhys`). O mínimo padrão passa de
2048 MB para **2304 MB**: o pico comprometido medido do motor (1 205 MB) mais 1 GiB, arredondado para cima em
múltiplos de 256 MB.

O serviço também passa a registrar no log:

- na recusa por memória: a grandeza medida, o disponível e o mínimo;
- na saída do motor com código diferente de 0: o código e o nome do tipo da exceção.

Só o backend muda. O contrato da API, as mensagens, o frontend e o contrato `motor-cli` ficam como estão.

---

## Technical Context

**Language/Version**: Python 3.13 (backend). Motor sem mudança.
**Primary Dependencies**: `ctypes` (já usado), `logging`, `re`.
**Storage**: nenhum. O serviço não toca o banco.
**Testing**: `pytest` com o motor falso (`tests/fake_motor.py`) e banco em `tmp_path`, como na 086. O teste do motor
real (`test_digitize_motor_smoke.py`) só roda com o motor instalado.
**Target Platform**: Windows 11 local (referência: 8 GB de RAM, ~82 % de uso, arquivo de paginação grande).
**Constraints**: nunca registrar texto lido, nome do arquivo enviado nem caminhos temporários. A saída de erro do
motor pode trazer avisos da biblioteca de detecção com caminhos dos modelos, que também não vão para o log.

---

## Constitution Check

| Princípio | Situação |
| :--- | :--- |
| I. Proteção do acervo | OK. Só imagens sintéticas; logs sem texto lido. Teste dedicado (SC-003). |
| II. Isolamento de testes | OK. Banco em `tmp_path`; memória simulada por `monkeypatch`; motor falso. |
| III. Fidelidade arquitetural | OK. Mesma pilha. Nenhuma dependência nova. |
| IV. Spec-Driven | OK. Spec aprovada; plano e tarefas com aprovação antes de implementar. |
| V. Migrações seguras | Não se aplica: sem migração. |

---

## Design

### D1. Medida de memória (FR-001, FR-003)

Em `app/services/digitize_service.py`:

- `IS_WINDOWS = os.name == "nt"`, no nível do módulo, para os testes simularem a plataforma sem trocar `os.name`.
- `_windows_memory_status() -> _MemoryStatus | None` isola a chamada a `GlobalMemoryStatusEx`. Os testes a
  substituem por uma estrutura com valores fictícios.
- `free_memory_bytes()` vira `available_memory() -> MemoryReading | None`, com
  `MemoryReading(measure: str, available: int)`, um `NamedTuple`:
  - Windows: `measure="commit"`, `available=ullAvailPageFile`;
  - Linux: `measure="physical"`, `available=MemAvailable` (sem mudança);
  - sem medida possível: `None`, e o pedido segue (como na 086).
- Em `preview()`, a recusa compara `reading.available` com `get_digitize_min_free_bytes()`. Código, status e
  mensagem do `503 low_memory` não mudam (FR-004).

**Por que `ullAvailPageFile`**: é o quanto ainda pode ser comprometido (o limite de commit do sistema menos o já
comprometido), e é quando ele acaba que as alocações falham. Com a RAM física cheia, o Windows pagina, e a leitura
fica mais lenta sem falhar.

### D2. Mínimo padrão (FR-002)

Em `app/core/config.py`, `DEFAULT_DIGITIZE_MIN_FREE_MB` passa de `2048` para `2304`. O comentário registra a
origem (pico comprometido de 1 205 MB numa página sintética de 12 MP com ampliação 3×, mais 1 GiB de reserva).
`get_digitize_min_free_bytes()` e `LEITORUM_DIGITIZE_MIN_FREE_MB` continuam iguais; só a grandeza comparada muda
(D1).

### D3. Log da recusa por memória (FR-005)

Antes de levantar o `low_memory`:

```
digitize: low_memory, memória commit disponível 1843 MB, mínimo 2304 MB
```

O registro sai em nível `WARNING`. A linha de desfecho existente (`digitize: <código>, <ms> ms`) continua.

### D4. Log da falha do motor (FR-006, FR-007)

- `run_engine` já manda o `stderr` do motor para `<pasta temporária>/motor.log`. O nome vira a constante
  `MOTOR_LOG`.
- Nova função `motor_error_type(log_path: Path) -> str`:
  - lê no máximo os últimos 4 KB do arquivo, em bytes, e decodifica como UTF-8 com `errors="replace"`;
  - procura, da última linha para a primeira, a primeira que seja **um identificador Python**
    (`^[A-Za-z_][A-Za-z0-9_.]{0,79}$`), formato do que o `__main__` do motor escreve (`IntegrityError`,
    `ValueError`, `RuntimeError` etc.);
  - linhas com espaço, barra, dois-pontos ou códigos de cor (avisos do RapidOCR com caminhos) nunca casam, e o
    texto lido não chega ao `stderr` pelo contrato do motor;
  - sem linha válida ou sem arquivo: devolve `"desconhecido"`.
- Em `preview()`, logo após `run_engine` e antes de qualquer `raise` por código de saída diferente de 0
  (2, 3 ou outro), registra em `WARNING`:

```
digitize: motor saiu com código 1 (RuntimeError)
```

- A pasta temporária só é apagada depois, no `finally`, como hoje (SC-002 da 086 mantido).

### D5. Teste do motor real

`tests/test_digitize_motor_smoke.py` pula a leitura real quando há "pouca memória livre" com a medida antiga
(RAM física < 1536 MB). No computador de referência, isso pulava o teste sempre. Por isso a 086 passou na suíte
sem nunca ter lido uma página pelo caminho real. O `skipif` passa a usar a mesma regra do serviço:
`available_memory()` abaixo de `get_digitize_min_free_bytes()`.

### D6. Documentos da 086

Notas curtas de "alterado pela 088" onde a 086 cita o mínimo de 2 GiB de RAM física:

- `research.md` R8;
- `plan.md` (linha da recusa abaixo de 2 GiB);
- `contracts/digitize-api.contract.md` (linha do `503 low_memory`);
- `quickstart.md` (linha "Memória (FR-011)").

O `tasks.md` da 086 fica como registro histórico.

---

## Testes (em `tests/test_digitize_api.py`, motor falso)

| Teste | Cobre |
| :--- | :--- |
| `test_windows_low_physical_but_ample_commit_reads` | **a causa**: Windows simulado, RAM física 1 200 MB, commit 18 000 MB, mínimo padrão (variável removida) ⇒ `200` e o motor é chamado |
| `test_windows_low_commit_is_refused_and_logged` | Windows simulado, RAM física 6 000 MB, commit 1 024 MB ⇒ `503 low_memory`, motor não chamado, log com `commit`, `1024 MB` e `2304 MB` |
| `test_min_free_env_applies_to_commit` | `LEITORUM_DIGITIZE_MIN_FREE_MB=20000` com commit 18 000 MB ⇒ `503` (FR-003) |
| `test_default_min_free_is_peak_plus_reserve` | `get_digitize_min_free_bytes()` sem variável = 2304 MB |
| `test_engine_failure_logs_exit_code_and_type` | modo `crash` ⇒ log com `código 1` e `RuntimeError` |
| `test_engine_failure_log_ignores_noisy_stderr` | modo novo `noisy_crash` no motor falso: escreve uma linha de aviso com caminho, uma linha com texto fictício ("Livro de Teste") e por último `ValueError`, e sai com 1 ⇒ log com `ValueError`, sem o caminho nem o texto |
| `motor_error_type` (unitário, `tmp_path`) | arquivo ausente, vazio, só ruído ⇒ `"desconhecido"`; linha final válida ⇒ o tipo |

Os testes existentes que substituem `free_memory_bytes` (`test_low_memory_is_refused_before_engine`,
`test_unmeasurable_memory_does_not_block`, `test_free_memory_is_measured_on_this_machine`) passam a substituir
`available_memory`, com o mesmo comportamento esperado. `test_logs_have_no_text_nor_temp_paths` continua e passa a
cobrir também as novas linhas de log.

---

## Validação manual (agente, só dados sintéticos)

1. `pytest` do backend com o interpretador do venv, depois de conferir que `app.__file__` aponta para este
   worktree. A falha ambiental conhecida `test_iniciar_rejects_relative_database_path` é aceita.
2. O teste do motor real passa a rodar no computador de referência (D5), se o motor estiver instalado no
   ambiente apontado por `LEITORUM_MOTOR_PYTHON`.
3. O script de reprodução do diagnóstico chama `digitize_service.preview` com a página sintética, o mínimo
   padrão e o motor real ⇒ `OK` com 3 linhas (SC-001), sem `LEITORUM_DIGITIZE_MIN_FREE_MB=0`.

**Pendente com o usuário**: enviar uma foto pela tela `/digitalizar` com o servidor reiniciado. O status do motor
fica em cache, e o código novo só vale depois de reiniciar o `iniciar.py`.

---

## Project Structure

```text
specs/088-memoria-digitalizacao/
├── spec.md
├── plan.md            # este arquivo
└── tasks.md           # próximo passo (speckit.tasks)

caderno-leitura-0.1/backend/
├── app/core/config.py                     # D2
├── app/services/digitize_service.py       # D1, D3, D4
└── tests/
    ├── fake_motor.py                      # modo noisy_crash
    ├── test_digitize_api.py               # testes novos e ajustados
    └── test_digitize_motor_smoke.py       # D5

specs/086-digitalizar-caderno-estudo/      # D6: notas "alterado pela 088"
```

## Complexity Tracking

Nenhuma violação a justificar.
