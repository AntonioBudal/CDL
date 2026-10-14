# Tarefas: EXP-008 — Detecção de Linhas em Manuscrito Real

* **Entradas:** [`spec.md`](./spec.md) e [`plan.md`](./plan.md), ambos `APPROVED` em 2026-10-13
* **Status:** `APPROVED` por delegação — o usuário, ao aprovar o plano em 2026-10-13, autorizou seguir sem parar
  ("pode continuar ... use o que você acha mais relevante ... continue executando"), incluindo instalações
* **Decisões tomadas por delegação:** download do `rapidocr` autorizado; exceção do BRESSAY estendida ao EXP-008;
  Florence-2 fora (exige executar código baixado com o modelo)

Convenções: cada fase termina com testes do harness e `ruff` limpos e um commit
`FNN(document-inteligence) [EXP-008] <fase>`. Medições de teste só a partir de árvore limpa. Testes só com dados
fictícios. Nenhuma imagem, recorte ou transcrição dos datasets vai para o Git, para relatórios ou para o chat.

---

## Fase 1 — Preparação

- [x] **T001** Medir RAM livre e disco.
- [x] **T002** Copiar do EXP-007 o necessário do harness (supervisor, worker, adaptadores `base`, `docufcn`,
  `reference`, `fakes`, `evaluate`, `gnhk`, `bressay`) e do EXP-002 o baseline clássico (`classic.py` e seu
  adaptador, com os parâmetros calibrados lá). Prefixo `@@EXP008`. Testes correspondentes.
- [x] **T003** `candidates.json`: quatro candidatos com licenças, pesos e SHA-256.
- [x] **T004** `prepare.py`: conjuntos de calibração (150 fotos do treino do GNHK, por sorteio com semente; 154
  páginas de validação do BRESSAY, ampliadas 3×), manifestos fora do Git e `subsets.json` versionado.
- [x] **T005** Reproduzir os números do EXP-007 a partir do layout já detectado. **Parar** se não baterem.

## Fase 2 — Método

- [x] **T006** Testes e `merge.py`: fusão transitiva de fragmentos (sobreposição vertical, distância horizontal,
  diferença de inclinação).
- [x] **T007** Testes e `coverage.py`: cobertura das linhas verdadeiras e área detectada fora de qualquer linha.

## Fase 3 — Candidato novo

- [x] **T008** Ambiente `envs/ppocr` (`rapidocr` + ONNX Runtime); ler `MODEL_LICENSES.md` e conferir com o card;
  registrar em `docs/models-and-licensing.md`; SHA-256 dos modelos. **Parar** se a licença contradisser o card.
- [x] **T009** `adapters/ppocr.py` (só detecção) e ensaio em poucas páginas.

## Fase 4 — Calibração

- [x] **T010** `detect.py`: cada candidato nos dois conjuntos de calibração.
- [x] **T011** `calibrate.py`: busca em grade dos parâmetros da fusão por candidato; `calibration.json`.

## Fase 5 — Teste

- [x] **T012** Cada candidato nos conjuntos de teste, uma vez (o `docufcn-norhand` reutiliza as detecções do
  EXP-007).
- [x] **T013** `run.py`: F1 bruto e fundido, cobertura, classes de erro, teto de fusão, custo, saídas em LDF 2.0,
  vereditos de H1 a H5. Relatório a partir de árvore limpa.

## Fase 6 — Análise e fecho

- [x] **T014** `RESULTS.md` (com a análise de falhas), ADR-006 (`PROPOSED`), índice de ADRs, roteiro,
  `docs/models-and-licensing.md`, `CLAUDE.md`.
- [x] **T015** Verificação final e submissão ao usuário.
