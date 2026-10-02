# EXP-001: Relatório de Resultados — HTR em Linhas Manuscritas Isoladas (PT-BR)

* **Status:** `AWAITING USER ACCEPTANCE`
* **Período de execução:** 2026-09-30 a 2026-10-02
* **Executor:** Claude Code
* **Decisão arquitetural gerada:** [ADR-001](../../docs/adr/ADR-001-nao-adotar-htr-pronto-sem-portugues.md) (`PROPOSED`)
* **Artefatos do ciclo:** [spec.md](./spec.md) · [plan.md](./plan.md) · [tasks.md](./tasks.md) · [error-analysis.md](./error-analysis.md)

> **Licenças.** `trocr-small-handwritten`: `LICENSE STATUS: NEEDS VALIDATION` — pesos sem licença declarada; uso
> experimental local autorizado pelo usuário; **não pode ser promovido a feature de produto**.
> Dataset BRESSAY: `LICENSE STATUS: NEEDS VALIDATION` — CC-BY-4.0 nos metadados do Zenodo, mas o README do dataset
> restringe a pesquisa e ensino não comerciais; uso experimental local autorizado em 2026-10-01; conteúdo fora do Git.
> PyLaia (código e pesos Teklia): `LICENSE STATUS: VERIFIED` conforme declarado nas fontes oficiais.
>
> BRESSAY: Neto et al., *BRESSAY: A Brazilian Portuguese Dataset for Offline Handwritten Text Recognition*, ICDAR 2024
> (DOI 10.5281/zenodo.11637681).

---

## 1. Resposta à pergunta do experimento

**Pergunta:** existe hoje um reconhecedor de linha manuscrita, com código e pesos de licença verificada, que rode
na máquina-alvo em CPU dentro de 2 GB e leia português manuscrito com qualidade útil?

**Resposta: não, entre os candidatos avaliados.** Nenhum dos três lê português manuscrito real: no BRESSAY o CER
fica entre 69 % e 95 % e praticamente nenhuma palavra sai correta. Todos cabem com folga no orçamento de memória;
nenhum atinge o de latência.

| Hipótese | Veredito | Evidência |
| :--- | :--- | :--- |
| H1 — CER ≤ 12 % e WER ≤ 25 % sem adaptação | **Refutada** | melhor CER em manuscrito real: 69,4 %; melhor em linhas sintéticas limpas: 17,0 % |
| H2 — ≤ 150 ms/linha e ≤ 2 GB | **Refutada na latência**, confirmada na memória | 179 ms (melhor caso, sintético) a 717 ms; pico máximo de 585 MiB |
| H0 — modelos sem treino em português falham nos diacríticos | **Confirmada** | 83–100 % de erro em vogais acentuadas e cedilha |

---

## 2. Resultados

CPU, 4 threads, decodificação gulosa, sem modelo de linguagem, 3 repetições (predições idênticas entre elas).

| Candidato | Licença | Dataset | CER | WER | Mediana ms/linha | p95 ms | Carga | Pico de memória | Status |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | :--- |
| `pylaia-rimes` | `VERIFIED` | sintético | 22,3 % | 68,8 % | 179 | 253–273 | ~10 s | 474 MiB | OK ×3 |
| `pylaia-iam` | `VERIFIED` | sintético | 24,6 % | 81,0 % | 181–186 | 251–285 | ~10 s | 473 MiB | OK ×3 |
| `trocr-small-handwritten` | `NEEDS VALIDATION` | sintético | 17,0 % | 46,2 % | 790–798 | 969–1.049 | ~30 s | 573 MiB | OK ×3 |
| `pylaia-rimes` | `VERIFIED` | BRESSAY | 94,7 % | 99,7 % | 407–408 | 546–582 | ~9 s | 503 MiB | OK ×2, SKIPPED ×1 |
| `pylaia-iam` | `VERIFIED` | BRESSAY | 79,3 % | 99,4 % | 402–408 | 550–605 | ~8 s | 499 MiB | OK ×3 |
| `trocr-small-handwritten` | `NEEDS VALIDATION` | BRESSAY | 69,4 % | 102,9 % | 705–717 | 907–922 | ~24 s | 585 MiB | OK ×3 |

* **Sintético:** 200 frases fictícias em PT-BR renderizadas com a fonte Caveat (8.107 caracteres). Mede custo e
  isola o efeito do alfabeto; não é métrica de HTR real.
* **BRESSAY:** 398 linhas de 199 autores do split de teste oficial (34.994 caracteres).
* **SKIPPED:** uma repetição do `pylaia-rimes` no BRESSAY não iniciou por falta de RAM livre (< 1 GiB) mesmo
  após 180 s de espera. O limite não foi relaxado.
* Reconhecedor de referência ("eco"): CER = WER = 0, 0,4–0,7 ms/linha, 20 MiB — valida o harness.

### Principais achados da análise de erros

1. **O alfabeto é um teto estrutural.** TrOCR e PyLaia-IAM erram 100 % das vogais acentuadas e cedilhas; o
   PyLaia-RIMES conhece só os acentos do francês (faltam `á í ó ú ã õ`).
2. **Fora dos acentos, o TrOCR é o melhor em texto limpo** (3,4 % de erro em minúsculas simples); ignorando
   diacríticos seu CER sintético cai de 17,0 % para 10,9 %.
3. **Em manuscrito real o modo de falha muda:** o PyLaia quase não emite texto (61–91 % dos caracteres ausentes);
   o TrOCR emite texto do tamanho certo, mas com metade dos caracteres trocada.
4. **A resolução do BRESSAY pesa, mas não explica tudo:** altura mediana de 23 px; mesmo nas linhas de 45 px ou
   mais o CER fica entre 61 % e 83 %.

Detalhes, tabelas por classe de caractere e confusões mais frequentes: [error-analysis.md](./error-analysis.md).

---

## 3. Critérios de sucesso da spec

| Critério | Situação |
| :--- | :--- |
| SC-001 — ≥ 2 candidatos executados | **Atendido com ressalva:** 3 executados, de 2 famílias; só os 2 PyLaia são `VERIFIED`. O TrOCR rodou sob exceção. |
| SC-002 — CER, WER, latência e memória por candidato, com veredito | Atendido (§1 e §2) |
| SC-003 — análise de erros por classe de caractere PT-BR | Atendido (`error-analysis.md`) |
| SC-004 — `docs/models-and-licensing.md` preenchido, inclusive recusados | Atendido |
| SC-005 — ADR com a decisão | Atendido: ADR-001, `PROPOSED`, aguardando o usuário |
| SC-006 — nada alterado fora de `document-intelligence/`; pytest e ruff verdes | Atendido (§6) |

Critérios de aceite de `EXP-001-context.md` §5: benchmark entre duas abordagens ✔; análise de erros ✔; verificação
de licença dos pesos ✔ (com as duas pendências acima); ADR ✔; nenhum acoplamento com o backend ✔.

---

## 4. Desvios em relação ao plano

| Planejado | O que ocorreu |
| :--- | :--- |
| Baseline de texto impresso (Tesseract) | Excluído: exige binário no sistema. EasyOCR excluído: pesos sem licença declarada e sem suporte a manuscrito. Não há baseline impresso. |
| Um ambiente `uv` do experimento | Três: `envs/harness`, `envs/pylaia` (Python 3.10, torch 1.13), `envs/trocr` (Python 3.14). |
| BRESSAY `VERIFIED` (Fase 1) | Rebaixado a `NEEDS VALIDATION` na Fase 3 ao ler o README do dataset; usado por exceção do usuário. |
| Dados reais do usuário | Não fornecidos, por privacidade; substituídos pelo BRESSAY. |
| Rodada extra limitada a 4 threads | Não foi necessária: o padrão do PyTorch nesta máquina já é 4 threads. |
| TrOCR via `TrOCRProcessor` | O tokenizador legado não carrega no `transformers` 5; o adaptador decodifica os ids com o SentencePiece. Geração com `use_cache=True`. |
| RAM livre ≥ 1 GiB para iniciar | A máquina oscila em torno desse valor; adicionada espera (`--wait-free-s`) sem relaxar o limite. |

O `uv` baixou por conta própria o CPython 3.10 para `%APPDATA%\uv\python` (fora da pasta, fora do PATH); aprovado
pelo usuário.

---

## 5. Limitações

* O BRESSAY são redações digitalizadas em baixa resolução, não fotos de caderno; o resultado mostra a falha em
  manuscrito PT-BR real, mas não mede o caso de uso do Leitorum.
* Um único subconjunto de 398 linhas, sem as linhas com rasura ou trecho ilegível (um pouco mais limpo que o dataset).
* Modelos usados como publicados: sem adaptação, sem modelo de linguagem, sem ajuste de pré-processamento.
* Latência medida com a máquina em uso normal (~1 GiB de RAM livre); os tempos podem variar com a carga.
* Nenhum candidato com treino em português foi encontrado com licença utilizável, então a comparação não inclui um.
* Confiança por linha não foi registrada (FR-006 previa registrá-la "quando o modelo a expõe"; não foi extraída).

---

## 6. Manifesto de reprodutibilidade (Princípio 3)

| Item | Valor |
| :--- | :--- |
| Hardware / SO | i5-8265U (4c/8t), 7,9 GB RAM, Windows 11 Pro 10.0.26300, CPU-only — [`../EXP-000/environment.md`](../EXP-000/environment.md) |
| Supervisor | Python 3.14.3, `uv` 0.11.21, `envs/harness/uv.lock` |
| PyLaia | Python 3.10.20, `pylaia` 1.1.2, `torch` 1.13.1+cpu — `envs/pylaia/uv.lock` |
| TrOCR | Python 3.14.3, `transformers` 5.18.0, `torch` 2.14.1+cpu — `envs/trocr/uv.lock` |
| Pesos | revisões e SHA-256 em [`candidates.json`](./candidates.json); conferidos antes de cada carga |
| Commits das medições | sintético: `277d5e2` (PyLaia), `0b47660` (TrOCR); BRESSAY: `e0e4600`; todos com árvore limpa |
| Dataset sintético | `dataset/fixtures/exp-001/synthetic-manifest.json`, SHA-256 `4e57398cd000…`; imagens regeneráveis (Pillow 12.3.0) |
| Dataset BRESSAY | `bressay.zip` MD5 `e4a4093304efff8322b605c8b79aa957`; seleção em `dataset/fixtures/exp-001/bressay-selection.json` (ids e hashes); `harness/bressay_subset.py`, seed 1234 |
| Parâmetros | seed 1234; aquecimento de 3 linhas; lote 1; decodificação gulosa; PyLaia com altura fixa de 128 px; TrOCR `max_new_tokens=128` |
| Limites | 2 GB de pico; carga ≤ 120 s; mediana das 20 primeiras linhas ≤ 1.500 ms; ≤ 20 min por execução; RAM livre ≥ 1 GiB |
| Relatórios | `evaluation/benchmarks/BENCHMARK-*-exp-001-*.json` e `ANALYSIS-20261001-exp-001-*.json` |

Para reproduzir uma medição (a partir de `document-intelligence/`, com ambientes e pesos instalados):

```powershell
uv run --project experiments/EXP-001/envs/harness python experiments/EXP-001/harness/run.py --candidate pylaia-rimes --repeats 3 --wait-free-s 180
```

**Verificação final (2026-10-02):** `uv run pytest` — 24 passed; testes do harness — 39 passed; `uv run ruff check .`
— limpo; nenhum arquivo alterado fora de `document-intelligence/`; pesos, dataset e predições do BRESSAY fora do Git.

---

## 7. Conformidade com a Constituição

* [x] **Princípio 1 (Local-first):** inferência offline; rede só para pacotes, pesos e dataset. Modelos de plataforma excluídos.
* [x] **Princípio 2 (Evidência antes de decisão):** nenhum modelo adotado; o ADR propõe não adotar, com base nas medições.
* [x] **Princípio 3 (Reprodutibilidade):** §6.
* [x] **Princípio 4 (Reconhecimento × interpretação):** saída bruta avaliada; sem léxico ou modelo de linguagem.
* [x] **Princípio 6 (Medir antes de otimizar):** sem quantização nem código nativo próprio.
* [x] **Princípio 7 (Experimentos antes de features):** código de modelos só em `experiments/EXP-001/`; `src/` recebeu apenas utilitários genéricos de medição.
* [x] **Princípio 8 (LDF como contrato soberano):** nenhuma troca de dados com o Leitorum.

**Regra de governança de escopo:** nenhum arquivo fora de `document-intelligence/` foi alterado; nenhum binário
instalado no sistema.

---

## 8. Homologação

- [x] Entregáveis do EXP-001 concluídos e submetidos ao usuário.
- [ ] EXP-001 **ACEITO** — decisão do usuário.
- [ ] ADR-001 aceito ou rejeitado — decisão do usuário.
- [ ] Autorização para o próximo passo — decisão do usuário. **EXP-002 não iniciado.**

*Assinatura do agente executor:* `Claude Code (claude-opus-5-5), 2026-10-02`
