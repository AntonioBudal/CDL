# EXP-002: Relatório de Resultados — Detecção de Layout e Segmentação de Linhas e Blocos

* **Status:** `AWAITING USER ACCEPTANCE`
* **Período de execução:** 2026-10-02 a 2026-10-05
* **Executor:** Claude Code
* **Decisão arquitetural gerada:** [ADR-002](../../docs/adr/ADR-002-segmentacao-de-layout-doc-ufcn-heron.md) (`PROPOSED`)
* **Artefatos do ciclo:** [spec.md](./spec.md) · [plan.md](./plan.md) · [tasks.md](./tasks.md) · [failure-analysis.md](./failure-analysis.md)

> **Licenças.** Doc-UFCN (código BSD-3-Clause, pesos MIT), Docling Heron (Apache-2.0) e OpenCV (Apache-2.0):
> `LICENSE STATUS: VERIFIED`, conforme declarado nas fontes oficiais. `doctr`: `LICENSE STATUS: NEEDS VALIDATION` —
> pesos sem licença declarada; uso experimental local autorizado pelo usuário; **não pode ser promovido a produto**.

---

## 1. Resposta à pergunta do experimento

**Pergunta:** existe um método local, em CPU, com licença verificada, que localize linhas e blocos de uma página
de caderno fotografada? E a retificação de perspectiva compensa o seu custo?

**Resposta: sim, em páginas sintéticas, com duas ressalvas (tempo e validade externa).**

* **Linhas:** o Doc-UFCN (variante `norhand`) com retificação por contorno atinge F1 de 0,93 em páginas limpas e
  0,92 / 0,85 nos níveis leve / forte. É a única família que cumpre a meta, e só com retificação.
* **Blocos:** o Docling Heron atinge mAP@0,5 de 0,78, mesmo treinado em documentos impressos.
* **Retificação:** o método clássico por contorno custa 0,13 s por página e melhora todos os detectores.
* **Ressalva de tempo:** a combinação de linhas custa ~2,6 s por página (meta: 2 s); linhas e blocos juntos, ~4,4 s.
* **Ressalva de validade:** tudo foi medido em páginas **sintéticas**; não há medição em fotos reais de caderno.

| Hipótese | Veredito |
| :--- | :--- |
| H1 — linhas: F1 ≥ 0,90 limpo e ≥ 0,80 degradado | **Confirmada com retificação**, só para o Doc-UFCN |
| H2 — blocos: mAP@0,5 ≥ 0,70 | **Confirmada para o Heron** (0,781); refutada para as regras geométricas (0,26–0,45) |
| H3 — ≤ 2 s por página e ≤ 2 GB | **Parcial:** memória sempre abaixo de 1 GB; no tempo passam só o baseline clássico e o Heron |
| H4 — baseline clássico resolve páginas limpas | **Refutada:** 0,847 em páginas limpas; 0,743 / 0,397 nas degradadas |
| H5 — retificação: +5 pontos por ≤ 0,5 s | **Confirmada para o contorno** em 3 de 4 detectores (no limite para o Doc-UFCN `norhand`: +4,9) |

---

## 2. Resultados principais

Conjunto `test`: 180 páginas sintéticas (60 limpas, 60 leves, 60 fortes), 3.548 linhas; CPU, 4 threads; 3 repetições
`OK` por combinação, com métricas idênticas entre repetições.

### Linhas (F1, caixa, IoU ≥ 0,5)

| Detector | Licença | Limpo | Leve | Forte | Leve + `contour` | Forte + `contour` | ms/página | Pico |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `docufcn-norhand-line` | `VERIFIED` | 0,928 | 0,883 | 0,784 | **0,920** | **0,845** | 2.498 | 652–826 MiB |
| `docufcn-historical-line` | `VERIFIED` | 0,917 | 0,863 | 0,799 | 0,900 | 0,799 | 2.458 | 649–822 MiB |
| `classic` | `VERIFIED` | 0,847 | 0,743 | 0,397 | 0,781 | 0,578 | 596 | 93 MiB |
| `doctr` | `NEEDS VALIDATION` | 0,842 | 0,694 | 0,391 | 0,794 | 0,511 | 2.138 | 923 MiB |

Com o retificador `docufcn-page` (2,5 s a mais por página): `norhand` 0,917 / 0,852; `historical` 0,882 / 0,878;
`classic` 0,783 / 0,717; `doctr` 0,670 / 0,662.

### Blocos (AP@0,5)

| Fonte | `title` | `paragraph` | `margin_note` | `graphic_box` | mAP | ms/página | Pico |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `heron` | 0,985 | 0,910 | 0,533 | 0,697 | **0,781** | 1.729–1.942 | 758 MiB |
| melhor conjunto de regras (sobre `doctr`) | 0,864 | 0,642 | 0,246 | 0,038 | 0,447 | +205 | — |

### Retificação isolada (120 páginas degradadas)

| Retificador | ms/página | Pico | Erro dos cantos (mediana) leve / forte |
| :--- | ---: | ---: | :--- |
| `contour` | 124–133 | 60 MiB | 5,9 px / 30,7 px (máx. 381 px) |
| `docufcn-page` | 2.453–2.538 | 657 MiB | 78,7 px / 75,8 px (máx. 162 px) |

Caso de borda de ~12 MP (10 páginas): `contour` 0,53 s e 122 MiB; `norhand` 2,6 s e 678 MiB; F1 0,884 → 0,932.

Tabelas completas, F1 por inclinação e curvatura e modos de falha: [failure-analysis.md](./failure-analysis.md).

---

## 3. Critérios de sucesso da spec

| Critério | Situação |
| :--- | :--- |
| SC-001 — baseline clássico e ≥ 1 modelo verificado, limpo e degradado | Atendido: baseline + Doc-UFCN (2 variantes) + Heron, `VERIFIED`; `doctr` sob exceção |
| SC-002 — P/R/F1, mAP, latência e memória, com veredito de H1–H4 (e H5) | Atendido |
| SC-003 — análise de falhas por degradação e por tipo de bloco | **Atendido em parte:** por nível, inclinação, curvatura e tipo de bloco; sombra e desfoque não foram isolados por página |
| SC-004 — saídas validadas contra o schema do LDF | Atendido: 100 % válidas; lacuna de `graphic_box` registrada (§5) |
| SC-005 — ADR; `docs/models-and-licensing.md` atualizado | Atendido: ADR-002 `PROPOSED` |
| SC-006 — escopo, testes, `ruff`, teto de 20 GB | Atendido (§7) |

---

## 4. Desvios em relação ao plano

| Planejado | O que ocorreu |
| :--- | :--- |
| Kraken como candidato | Excluído: depende de `coremltools`, sem wheels para Windows |
| Blocos só por regras | A Fase 1 encontrou o Docling Heron, que entrou como detector de layout |
| `docufcn-line` como um candidato | Medidas as duas variantes de pesos (`historical` e `norhand`) |
| Baseline clássico por perfis de projeção | A primeira versão não removia a pauta inclinada; passou a usar aberturas morfológicas em 9 ângulos, o que o deixou mais lento na calibração (0,6 s por página na medição final) |
| Blocos com retificação | Não medidos: a Fase 4 cobriu só linhas |
| Rodada do `large` com "a melhor combinação" | Feita com `contour` + `docufcn-norhand-line`, com e sem retificação |
| RAM livre ≥ 1 GiB | A primeira tentativa da Fase 3 foi interrompida com 250–500 MiB disponíveis; o usuário liberou memória e tudo rodou sem espera, com o limite intacto |
| Análise por sombra e desfoque | O gerador não registra se a sombra foi sorteada; ficaram embutidos no nível |

---

## 5. Achados sobre o contrato LDF

1. **`graphic_box` não tem como guardar a região no LDF 1.0:** `structure.diagrams[]` só tem nós e arestas.
   O conversor registra o diagrama vazio e conta a lacuna.
2. **Dois contratos divergentes:** o modelo Pydantic `leitorum_di.contracts.ldf` não corresponde ao JSON Schema
   versionado (estrutura `document`, tipos de bloco `title` / `diagram_region`, sem bbox). O experimento validou
   contra o JSON Schema e não alterou nenhum dos dois.
3. **`title` × `heading`:** o tipo de bloco aprovado para o experimento é `title`; no JSON Schema ele é `heading`.

Nenhuma mudança de contrato foi feita; são decisões do usuário.

---

## 6. Limitações

* **Páginas sintéticas.** Fontes manuscritas regulares, pauta perfeita, degradações simuladas. Os números medem
  robustez relativa entre métodos, não o desempenho em fotos reais de caderno. Caligrafia real, páginas
  amassadas, dedos, dobras e fundos variados não estão representados.
* **Blocos por regras calibrados no gerador.** As regras foram ajustadas no `dev` (mesmo gerador, outras seeds),
  e vários parâmetros ficaram na borda da grade testada.
* **Caixa alinhada aos eixos.** O critério principal usa a caixa do LDF; para linhas inclinadas ela é pouco
  precisa. O F1 por polígono do melhor candidato é menor (0,82 sem retificação; 0,85 com).
* **Curvatura não é corrigida** pela homografia; o nível forte continua sendo o ponto fraco.
* **Latência** medida com a máquina em uso leve (3 GB de RAM disponível); `torch` do Doc-UFCN é a versão 2.1.0,
  fixada pela biblioteca.
* **`margin_note` no Heron** usa uma correspondência aproximada de classes.
* Sem dataset real anotado, e sem repetição com outras seeds do gerador.

---

## 7. Manifesto de reprodutibilidade (Princípio 3)

| Item | Valor |
| :--- | :--- |
| Hardware / SO | i5-8265U (4c/8t), 7,9 GB RAM, Windows 11 Pro, CPU-only — [`../EXP-000/environment.md`](../EXP-000/environment.md) |
| Harness | Python 3.14.3; OpenCV 5.0.0.93, NumPy 2.5.3, Pillow 12.3.0 — `envs/harness/uv.lock` |
| Doc-UFCN | Python 3.10.20; `doc-ufcn` 0.1.9; `torch` 2.1.0+cpu — `envs/docufcn/uv.lock` |
| Heron | Python 3.14.3; `transformers` 5.18.0; `torch` 2.14.1+cpu — `envs/heron/uv.lock` |
| docTR | Python 3.14.3; `python-doctr` 1.1.0; `torch` 2.14.1+cpu — `envs/doctr/uv.lock` |
| Pesos | revisões e SHA-256 em [`candidates.json`](./candidates.json); conferidos antes de cada carga |
| Dados | manifestos em `dataset/fixtures/exp-002/` (seeds, parâmetros de degradação, SHA-256 por imagem); imagens regeneráveis com `harness/generate.py` |
| Calibração | [`calibration.json`](./calibration.json), só no conjunto `dev` |
| Commits das medições | Fase 3: árvore limpa em `009b019`/`50e62f2`; Fase 4: `9b1f64c`. (O campo `git.commit` dos relatórios traz o HEAD do repositório inteiro, que inclui commits do produto principal; `dirty: false` refere-se só a `document-intelligence/`.) |
| Parâmetros | seed 1234; aquecimento de 2 páginas; lote 1; Doc-UFCN com entrada de 768 px; Heron com limiar 0,3; docTR `fast_base`; imagens acima de 2.500 px reduzidas no baseline |
| Limites | 2 GB de pico; carga ≤ 120 s; mediana das 10 primeiras páginas ≤ 20 s; ≤ 30 min por execução; RAM livre ≥ 1 GiB |
| Relatórios | `evaluation/benchmarks/BENCHMARK-2026100{2,3,4,5}-exp-002-*.json` e `ANALYSIS-20261005-exp-002-*.json` |

Para reproduzir uma medição (a partir de `document-intelligence/`, com ambientes e pesos instalados):

```powershell
uv run --project experiments/EXP-002/envs/harness python experiments/EXP-002/harness/run.py --candidate docufcn-norhand-line --repeats 3 --assemble-blocks
```

**Verificação final (2026-10-05):** `uv run pytest` — 33 passed; testes do harness do EXP-002 — 33 passed;
`uv run ruff check .` — limpo; nenhum arquivo meu fora de `document-intelligence/`; pesos, páginas geradas e
predições fora do Git; uso de disco de 7,5 GB em ambientes, pesos e dados (teto de 20 GB).

---

## 8. Conformidade com a Constituição

* [x] **Princípio 1 (Local-first):** inferência offline; rede só para pacotes, pesos e fontes.
* [x] **Princípio 2 (Evidência antes de decisão):** nada adotado; o ADR propõe direção com base nas medições.
* [x] **Princípio 3 (Reprodutibilidade):** §7.
* [x] **Princípio 4 (Reconhecimento × interpretação):** só geometria; nenhum texto lido.
* [x] **Princípio 6 (Medir antes de otimizar):** sem otimização nativa.
* [x] **Princípio 7 (Experimentos antes de features):** modelos só em `experiments/EXP-002/`; em `src/` entraram apenas métricas genéricas de detecção.
* [x] **Princípio 8 (LDF como contrato soberano):** saídas validadas contra o JSON Schema; lacunas registradas, contrato intocado.

**Regra de governança de escopo:** nenhum arquivo fora de `document-intelligence/` foi alterado por este
experimento; nenhum binário instalado no sistema; nenhuma biblioteca AGPL.

---

## 9. Homologação

- [x] Entregáveis do EXP-002 concluídos e submetidos ao usuário.
- [ ] EXP-002 **ACEITO** — decisão do usuário.
- [ ] ADR-002 aceito, rejeitado ou ajustado — decisão do usuário.
- [ ] Próximo passo — decisão do usuário. **EXP-003 não iniciado.**

*Assinatura do agente executor:* `Claude Code (claude-opus-5-5), 2026-10-05`
