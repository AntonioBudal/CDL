# EXP-000: Relatório de Resultados e Homologação de Fundação

* **Status:** `ACCEPTED` / `CONCLUÍDO` (homologado e aceito formalmente pelo usuário)
* **Data da Conclusão:** 2026-09-30
* **Auditor Responsável:** Claude Code
* **Decisão Arquitetural Gerada:** N/A (nenhuma tecnologia nova adotada)
* **Última atualização:** 2026-09-30

---

## 1. Resumo Executivo da Execução

Executado no Windows 11 do usuário (Python 3.14.3, uv 0.11.21). Reverificação final em 2026-09-30,
com os comandos rodados diretamente pelo Claude Code a partir de `document-intelligence/`:

* `uv sync`: **exit 0**, 16 pacotes resolvidos / 15 conferidos, sem alertas de conflito.
* `uv run pytest`: **20 passed em 0,42 s** (pytest) / **1,93 s** de relógio total incluindo o `uv run` — < 5 s.
* `uv run ruff check .`: **All checks passed**.
* `uv run python -m leitorum_di.benchmark`: exit 0; 7 amostras em 2,77 ms; RSS 21,0 → 21,1 MiB; pico de alocação Python 14 096 bytes.
* Inventário de hardware/SO registrado em `environment.md` (i5-8265U, 7,9 GB RAM, MX110 2 GB → baseline **CPU-only**).
* Métricas CER/WER/IoU conferidas contra valores calculados manualmente (§2).

O ambiente está **apto a suportar o EXP-001 em CPU**. O usuário aceitou o EXP-000 e autorizou o avanço para o EXP-001 pelo ciclo Spec Kit (§5).

---

## 2. Validação da Infraestrutura de Métricas

| Métrica | Fixture Sintética Testada | Resultado Esperado | Resultado Obtido | Status |
| :--- | :--- | :--- | :--- | :--- |
| **CER** (Character Error Rate) | `synthetic-line-sample.json` syn-001 | 0.0 | 0.0 | PASS |
| **CER** | syn-002 (`definicao`→`definição`: 2 substituições / 32) | 0.0625 (cálculo manual) | 0.0625 | PASS (sem `expected_cer` na fixture) |
| **CER** | syn-003 (`Capítulo`→`Capitulo`, `Sintéticos`→`Sinteticos`: 2 / 34) | 0.0588 (cálculo manual) | 0.058823… | PASS (sem `expected_cer` na fixture) |
| **WER** (Word Error Rate) | syn-001 / syn-002 / syn-003 | 0.0 / 0.25 (1 de 4) / 0.5 (2 de 4) | 0.0 / 0.25 / 0.5 | PASS (só syn-001 é verificado pelos testes) |
| **IoU** (Bounding Box) | [0,0,10,10] vs [0,0,10,10] | 1.000 | 1.0 | PASS |
| **IoU** | syn-003 [0,0,100,100] vs [50,0,150,100] | 0.3333 | 0.3333333333333333 | PASS |
| **CER / WER / IoU** | syn-004 | 3/19, 3/4, 0.5 (fixture) | 0.157894…, 0.75, 0.5 | PASS |
| **CER / WER / IoU** | syn-005 | 1/16, 1/3, 0.0 (fixture) | 0.0625, 0.3333…, 0.0 | PASS |
| **CER / WER / IoU** | syn-006 | 2/13, 1/3, 1.0 (fixture) | 0.153846…, 0.3333…, 1.0 | PASS |
| **CER / WER / IoU** | syn-007 | 1/7, 0.0, 1.0 (fixture) | 0.142857…, 0.0, 1.0 | PASS |
| **Tempo de Execução dos Testes** | Suíte inteira de fundação (20 testes) | < 5.0 s | 0,42 s (pytest); 1,93 s total com `uv run` | PASS |
| **`uv run pytest` (Windows)** | Suíte completa | 100% passando | 20 passed | PASS |
| **`uv sync` (Windows)** | Ambiente | sem alertas de conflito | exit 0, sem alertas | PASS |
| **`uv run ruff check .`** | Projeto inteiro | 0 violações | All checks passed (Windows) | PASS |

---

## 3. Conformidade com a Constituição

* [x] **Princípio 1 (Local-First):** nenhum import/URL de rede em `src/` e `tests/`; única dependência runtime: `pydantic`.
* [x] **Princípio 2 (Evidência):** as 7 amostras da fixture trazem `expected_cer/wer/iou` derivados à mão; os valores obtidos no Windows coincidem (§2).
* [x] **Princípio 3 (Reprodutibilidade):** versões em `environment.md`; `freeze_seeds` e log de benchmark (tempo, RSS, pico de alocação) implementados e executados no Windows.
* [x] **Princípio 6 (Medir antes de otimizar):** baseline puro Python (Levenshtein O(m·n) em listas), sem código nativo.
* [x] **Princípio 8 (LDF como Contrato Soberano):** o EXP-000 não troca dados com o Leitorum; nenhum acoplamento fora do LDF foi introduzido (contrato em `src/leitorum_di/contracts/ldf.py` e `docs/schemas/ldf-1.0.schema.json`).

**Regra de governança de escopo (fronteira técnica — `AGENTS.md` §1–2, não é um princípio numerado da constituição):**

* [x] Nenhum arquivo fora de `document-intelligence/` alterado; `tests/test_boundary.py` passa. Bloqueio técnico por hook/sandbox não testado.

---

## 4. Desafios e Ajustes Encontrados

1. **Sandbox do agente sem Windows/PyPI:** a primeira tentativa falhou (403); resolvido executando `collect_environment.ps1` na máquina do usuário. Nada foi contornado.
2. **Locale cp1252 / console:** `locale.getpreferredencoding()` = cp1252 e o PowerShell 5.1 corrompe acentos na exibição; sempre usar `encoding="utf-8"`.
3. **Cobertura da fixture — RESOLVIDO:** fixture com 7 amostras (acentos `ç ã é õ`, caixa, inserção, deleção, pontuação, IoU 1/0.5/⅓/0), todas com `expected_cer/wer/iou` derivados à mão por frações; `test_metrics.py` valida **todas** as amostras e a cobertura do manifesto.
4. **Normalização do WER — RESOLVIDO:** `calculate_wer` remove pontuação de borda (Unicode `P*`), preserva acentos, caixa e pontuação interna; documentado em `docs/metrics.md` §4. **APROVADA pelo usuário em 2026-09-30** — regra mantida (evita penalização dupla de pontuação, já coberta pelo CER).
5. **Python 3.14 — RESOLVIDO:** classifier `Programming Language :: Python :: 3.14` adicionado ao `pyproject.toml`.
6. **Template — RESOLVIDO:** o rótulo "Princípio 8 (Fronteira)" foi corrigido para "LDF como Contrato Soberano"; a fronteira técnica passou a constar como regra de governança de escopo (§3).
7. **Seeds e log de benchmark — RESOLVIDO:** `leitorum_di.reproducibility` (`freeze_seeds`, `environment_snapshot`) e `leitorum_di.benchmark` (`python -m leitorum_di.benchmark [--out ...]`: ms/amostra, RSS, pico de alocação, seeds; schema `leitorum-di-benchmark/1`). A leitura de RSS no Windows (ctypes/psapi) foi **confirmada no Windows** em 2026-09-30 (retornou 21 995 520 → 22 134 784 bytes, não `None`). `PYTHONHASHSEED` não é efetivo em processo já iniciado (`pythonhashseed_effective: false`); só `random` é semeado.

**Verificação anterior (sandbox Linux, Python 3.12, sem pytest):** `ruff check` limpo; 17 testes via runner mínimo.

**Reverificação final (Windows 11, Python 3.14.3, 2026-09-30):** `uv sync` exit 0 sem alertas; `uv run pytest` 20 passed em 0,42 s; `uv run ruff check .` limpo; benchmark exit 0. Pendência anterior de reexecução no Windows **encerrada**.

**Itens em aberto:** nenhum dos itens 1–7. Permanece apenas a observação de que o bloqueio técnico de escrita fora de `document-intelligence/` (hook/sandbox) não foi testado.

---

## 5. Homologação para Próxima Etapa

- [x] Critérios de aceite do README atendidos: ambiente registrado; métricas CER/WER/IoU com testes passando; pytest < 5 s; ruff com 0 violações; RESULTS preenchido; `uv sync` sem alertas (reconfirmado no Windows).
- [x] O domínio está **AUTORIZADO** a avançar para o **EXP-001** — aceite formal do usuário em 2026-09-30, com a condição de seguir o ciclo Spec Kit adaptado a experimentos (Specify → Plan → Tasks) e apresentar especificação/plano **antes** de qualquer código de avaliação, inferência ou download de pesos.

*Assinatura do Agente Executor:* `Claude Code (claude-sonnet-5-5), 2026-09-30` — auditoria assinada; **EXP-001 não iniciado**.

*Reverificação no Windows:* `Claude Code (claude-opus-5-5), 2026-09-30` — os seis critérios de aceite conferidos por execução direta; **EXP-001 não iniciado**.
