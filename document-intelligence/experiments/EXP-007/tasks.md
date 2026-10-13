# Tarefas: EXP-007 — Validação do Layout e da Ordem de Leitura em Imagens Reais

* **Entradas:** [`spec.md`](./spec.md) e [`plan.md`](./plan.md), ambos `APPROVED` em 2026-10-12
* **Status:** `EXECUTADO` em 2026-10-13 — aguardando aceite do experimento e do ADR-005
* **Execução:** contínua, sem parar a cada fase; parada só no aceite final ou em bloqueio real (RAM livre abaixo
  de 1 GiB que não se resolve esperando, disco perto do teto, verdade de chão inutilizável, dependência nova)

Convenções: `[P]` = pode ser feita em paralelo com as vizinhas. Cada fase termina com os testes do harness e
`ruff` limpos e um commit `FNN(document-inteligence) [EXP-007] <fase>`. Medições só a partir de árvore limpa.
Testes só com imagens e anotações fictícias geradas em `tmp_path`. Nenhuma imagem, recorte ou transcrição dos
datasets vai para o Git, para relatórios ou para o chat.

---

## Fase 1 — Preparação

- [x] **T001** Medir disco e RAM livre; registrar no relatório de execução.
- [x] **T002** Copiar do EXP-003 para `experiments/EXP-007/harness/` só o necessário: supervisor, worker,
  adaptadores (`base`, `docufcn`, `heron`, `rectifiers`, `fakes`), `evaluate`, `rectify`, `orderers`,
  `postprocess`, `order_eval`. Prefixo de protocolo `@@EXP007`. Copiar os testes correspondentes e ajustá-los.
- [x] **T003** `candidates.json` do EXP-007 com os mesmos pesos e SHA-256 do EXP-002 (`docufcn-norhand-line`,
  `heron`), o retificador por contorno e os estados de licença.
- [x] **T004** `harness/prepare.py`: extrai de cada zip só a divisão oficial de teste para
  `dataset/processed/exp-007/`; grava `subsets.json` (nomes e SHA-256, sem conteúdo). Confere os hashes dos zips.
- [x] **T005** Teste que garante EXP-001 a EXP-003 intactos continua verde; conferir `.gitignore` para
  `dataset/raw/exp-007/` e `dataset/processed/exp-007/`.

## Fase 2 — Verdade de chão (Cenários 1 a 3; SC-001)

- [x] **T006** [P] Testes de `gnhk.py` com anotações fictícias: agrupamento por `line_idx`, retângulo mínimo de
  linha inclinada, linha só impressa ou só com marca especial vira "ignorar", foto sem linha utilizável.
- [x] **T007** [P] `harness/gnhk.py`: linhas (caixa e polígono) e regiões a ignorar por foto. Não lê nem grava o
  campo de texto além de testar as marcas especiais.
- [x] **T008** [P] Testes de `bressay.py` com página e recortes fictícios: localização exata, recorte ausente,
  recorte repetido, parágrafo de uma linha, ordem pela numeração.
- [x] **T009** [P] `harness/bressay.py`: localiza cada recorte de linha e de parágrafo na página; devolve linhas,
  blocos, pertencimento e ordem. Recorte não localizado é contado; página incompleta sai da medição.
- [x] **T010** Gerar os manifestos com geometria em `dataset/processed/exp-007/` (fora do Git), incluindo a versão
  ampliada 3× das páginas do BRESSAY com a geometria escalada.
- [x] **T011** Relatório de verdade de chão: fotos e páginas utilizáveis, taxa de localização, contagem de linhas,
  blocos e regiões ignoradas. **Parar e perguntar** se ficar abaixo de 100 + 100 (SC-001).

## Fase 3 — Detecção (Cenário 4)

- [x] **T012** `harness/detect.py` adaptado: linhas com Doc-UFCN e blocos com Heron; no GNHK, linhas também sobre
  a imagem retificada, levadas de volta à foto original; registro de tempo e memória por foto; falha por foto é
  contada, não descartada.
- [x] **T013** Ensaio com os adaptadores falsos (sem modelo) nas duas bases, para validar o fluxo de ponta a ponta.
- [x] **T014** Detecção no GNHK (172 fotos): com e sem retificação.
- [x] **T015** Detecção no BRESSAY (199 páginas): ampliada 3× e nativa.
- [x] **T016** Conferir critérios de parada e uso de disco depois das execuções.

## Fase 4 — Avaliação (Cenário 4; SC-004)

- [x] **T017** `harness/run.py`: F1 de linhas por caixa e por polígono (GNHK e BRESSAY); taxa de sucesso da
  retificação (GNHK); F1 e mAP de blocos sem classe, com o ponto de operação do EXP-003 (BRESSAY); acurácia de
  ordem com parágrafos verdadeiros e detectados, ordenadores `naive` e `anchored` com os parâmetros do EXP-003.
- [x] **T018** `harness/to_ldf2.py`: todas as saídas pelo `build_document`; contar documentos válidos.
- [x] **T019** Gravar `BENCHMARK-*-exp-007-*.json` a partir de árvore limpa, com manifesto de reprodutibilidade.

## Fase 5 — Análise e fecho (Cenário 5; SC-002, SC-003, SC-005, SC-006)

- [x] **T020** `harness/analyze.py`: comparação sintético × real por métrica; no GNHK, por região de origem da
  foto (prefixo do nome do arquivo) e com/sem retificação; no BRESSAY, ampliada × nativa; decomposição das perdas.
- [x] **T021** `failure-analysis.md`: onde a perda acontece, só com números e nomes de arquivo.
- [x] **T022** `RESULTS.md`: veredito de H1 a H6, desvios do plano, limitações, manifesto de reprodutibilidade,
  conformidade; `LICENSE STATUS: NEEDS VALIDATION` na parte que depende do BRESSAY; atribuição do GNHK.
- [x] **T023** ADR-005 (`PROPOSED`), ou proposta de revisão dos ADR-002/003, conforme os dados; índice de ADRs.
- [x] **T024** Atualizar `docs/roadmap-experiments.md`, `docs/models-and-licensing.md` e `CLAUDE.md`.
- [x] **T025** Verificação final: suíte principal, testes do harness, `ruff`, nada fora de
  `document-intelligence/`, nenhum conteúdo de dataset rastreado pelo Git, disco dentro do teto.
- [x] **T026** Submeter ao usuário para aceite. Não iniciar o EXP-004.

---

## Dependências

```text
Fase 1 → Fase 2 → Fase 3 → Fase 4 → Fase 5
```

T006–T009 são independentes entre si. T014 e T015 não rodam ao mesmo tempo (memória).

## Rastreabilidade

| Critério | Tarefas |
| :--- | :--- |
| SC-001 verdade de chão em ≥ 100 + 100 | T009–T011 |
| SC-002 veredito de H1 a H6 | T017, T020, T022 |
| SC-003 análise de falhas | T020, T021 |
| SC-004 saídas válidas em LDF 2.0 | T018 |
| SC-005 nada de conteúdo no Git, disco no teto | T004, T005, T016, T025 |
| SC-006 ADR | T023 |
