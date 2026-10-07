# Tasks: EXP-003 — Reconstrução Espacial e Ordem de Leitura

**Input**: [spec.md](./spec.md), [plan.md](./plan.md)

**Status**: `APPROVED` pelo usuário em 2026-10-07, com a instrução de **não parar a cada checkpoint**: a execução segue por todas as fases e só para no aceite final (ou em bloqueio real).

**Formato**: `[ID] [P?] [Cenário] Descrição` — `[P]` = pode rodar em paralelo; C1–C4 = cenários da spec.

Cada fase termina num checkpoint: reporto e só sigo com autorização. Nenhum download ou instalação é previsto;
só a Fase 3 usa modelos (os do EXP-002, já instalados) e precisa de RAM livre.

---

## Fase 0 — Portões

- [x] T001 Spec aprovada (2026-10-05) e plano aprovado com ajuste (2026-10-07: sem módulo comum; uma execução dos detectores).
- [x] T002 Usuário aprova `tasks.md` (2026-10-07).

## Fase 1 — Cenário 1: dados com ordem de leitura e métricas (sem modelos)

- [ ] T003 [C1] Copiar do EXP-002 para `experiments/EXP-003/harness/` o gerador (`pages/`, `generate.py`), `supervisor.py`, `worker.py`, `rectify.py`, `evaluate.py`, `to_ldf.py` e os adaptadores `reference`, `docufcn`, `heron` e `rectifiers`; conferir que os testes copiados passam sem alterar nada no EXP-002.
- [ ] T004 [C1] Gerador: registrar `reading_order` dos blocos, a ordem das linhas em cada bloco e o parágrafo-âncora de cada nota de margem; testes de consistência (todo bloco aparece uma vez; âncoras válidas).
- [ ] T005 [C1] Gerador: famílias `single`, `margin` (2–4 notas ancoradas, horizontais e verticais) e `callout` (parágrafo estreitado + caixa de destaque com moldura à direita); testes de geometria e de ordem por família.
- [ ] T006 [P] [C1] `src/leitorum_di/metrics/ordering.py`: acurácia de ordem (distância de edição normalizada) e tau de Kendall, com testes de valores calculados à mão em `tests/`.
- [ ] T007 [C1] Gerar e congelar `dev` (30 páginas) e `test` (180: 3 famílias × 3 níveis × 20) em `dataset/fixtures/exp-003/` e `dataset/processed/exp-003/`; conferir visualmente uma página de cada família com a ordem desenhada.
- [ ] T008 [C1] `harness/order_eval.py`: avaliação de ordem de blocos e de linhas sobre layout verdadeiro; ordenador de referência dá 1,0 e permutações conhecidas dão o valor esperado.
- [ ] T009 [C1] `to_ldf.py`: preencher `structure.reading_order` e validar contra o JSON Schema; contar as caixas gráficas que não cabem no campo.
- [ ] T010 [C1] `pytest`, `ruff`; commit da fase.

**Checkpoint 1**: dados e métricas prontos, sem modelos. Reportar.

## Fase 2 — Cenário 2: ordenadores sobre o layout verdadeiro

- [ ] T011 [C2] `harness/orderers.py`: `naive`, `xycut` e `anchored`, com testes em layouts pequenos construídos à mão (coluna única, nota de margem, destaque lateral).
- [ ] T012 [C2] `harness/calibrate.py`: calibrar os parâmetros de cada ordenador **só** no `dev`; gravar `calibration.json`.
- [ ] T013 [C2] Commit limpo; medir os três ordenadores no `test` com layout verdadeiro: acurácia de blocos e tau de Kendall por família e por nível, ms por página (mediana de 3 repetições) e pico de alocação; saídas validadas no LDF.

**Checkpoint 2**: tabela dos ordenadores com layout verdadeiro e veredito parcial de H1, H3 e H4. Reportar.

## Fase 3 — Cenário 3: layout detectado (precisa de RAM livre)

- [ ] T014 [C3] `harness/detect.py`: nas 180 páginas do `test`, rodar retificação por contorno → Doc-UFCN `norhand` (linhas levadas de volta às coordenadas originais) e Heron na imagem original (blocos), uma execução cada, com o supervisor e os limites do EXP-002; guardar o layout detectado fora do Git.
- [ ] T015 [C3] `order_eval.py`: casamento de blocos previstos com verdadeiros (IoU ≥ 0,5), reescrita da sequência com ids verdadeiros, contagem de blocos sem par e as três acurácias da decomposição da perda; testes com casos à mão.
- [ ] T016 [C3] Commit limpo; medir os três ordenadores sobre o layout detectado e montar a tabela de ponta a ponta com a decomposição (ordenação × detecção), por família e por nível.

**Checkpoint 3**: resultado de ponta a ponta e veredito de H2. Reportar.

## Fase 4 — Cenário 4: linhas dentro do bloco

- [ ] T017 [C4] Ordenação de linhas dentro do bloco pela projeção perpendicular à linha de base; testes com blocos inclinados e nota vertical.
- [ ] T018 [C4] Medir a acurácia de ordem de linhas com layout verdadeiro e com layout detectado, com e sem retificação das linhas.

**Checkpoint 4**: ordem de linhas. Reportar.

## Fase 5 — Análise, relatório e decisão

- [ ] T019 `harness/analyze.py`: erros por família, por tipo de bloco deslocado na ordem e por inclinação da folha.
- [ ] T020 `experiments/EXP-003/RESULTS.md` com veredito de H1–H4, desvios, limitações e manifesto de reprodutibilidade.
- [ ] T021 ADR em `docs/adr/` com a decisão sobre o método de ordenação.
- [ ] T022 Conferência final: testes, `ruff`, nada fora de `document-intelligence/`, dados gerados fora do Git, disco abaixo de 20 GB, EXP-001 e EXP-002 intocados.
- [ ] T023 Submeter ao usuário para aceite. **Não iniciar o EXP-004 antes do aceite.**

---

## Dependências

- T002 → Fase 1 → Fase 2 → Fase 3 → Fase 4 → Fase 5.
- Na Fase 1: T003 → T004 → T005 → T007; T006 em paralelo; T008 e T009 dependem de T004–T006.
- As Fases 1 e 2 não usam modelos e podem rodar com pouca RAM livre; a Fase 3 exige ≥ 1 GiB disponível.
- T017 pode ser adiantada junto da Fase 2, mas a medição T018 depende do layout detectado (T014).
