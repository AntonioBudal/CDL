# EXP-024 — Tarefas

**Spec:** [spec.md](./spec.md) · **Plano:** [plan.md](./plan.md) · **Estado:** [STATE.md](./STATE.md)

**Ciclo de cada fase:**
1. investigar;
2. planejar a fase;
3. implementar;
4. verificar (`pytest`, `ruff`, invariantes);
5. corrigir;
6. atualizar o `STATE.md`;
7. commit `FNN(document-inteligence) [EXP-024] …`;
8. relatório da fase.

**Paradas obrigatórias para revisão do usuário:** fim da F01 e fim da F05.

Caminhos relativos a `document-intelligence/`; `E` = `experiments/EXP-024`; `O` =
`uv run --frozen --project experiments/EXP-023/envs/organizer`.

---

## F00 — Diagnóstico e linha de base (concluída, commit `7a63891`)

- [x] T000 Leitura dos documentos de partida; linha de base: `uv run pytest` (239), `ruff`, testes do EXP-023
  (14); disco 13,97 GB; SHA-256 do `organizer-v1.json`; `E/STATE.md`.

## F01 — Especificação, plano e tarefas

- [x] T001 `E/spec.md`: matriz das 6 estratégias, travas, decisões de Categoria 2 e hipóteses H1–H5.
- [x] T002 `E/plan.md`: ambiente, arquivos, estado, algoritmos, calibração, testes.
- [x] T003 `E/tasks.md` (este arquivo) e `E/STATE.md`. Commit `F01 … especificacao, plano e tarefas da melhoria
  continua autonoma`. **Parar para revisão.**

## F02 — Fluxos longitudinais e simulador

- [x] T010 `E/data/perfis.json`: pelo menos 4 perfis.
  - P1: referências em lista Markdown com "Título — Autor" e links;
  - P2: ordem própria, conceitos primeiro;
  - P3: ABNT e corrido reflexivo;
  - P4: misto e telegráfico.
- [x] T011 `E/data/livros.json`: 2 a 3 livros fictícios por perfil, com termos acentuados de propósito.
- [x] T012 `E/data/frases/`: bancos de frases fictícias por seção e estilo, com lacunas de vocabulário do livro.
- [x] T013 `E/data/confusoes-escritores.json`: confundidores recorrentes sintéticos por escritor, declarados como
  sintéticos.
- [x] T014 `E/data/canario.json`: 8 páginas fictícias do portão-sombra.
- [x] T015 Congelar: `E/data/SHA256SUMS`, gravado no `STATE.md` **antes** de qualquer código do motor.
- [x] T016 `E/harness/streams.py`: fluxos de validação e de teste por perfil (40 de adaptação e 12 *holdout* por
  livro), determinísticos.
- [x] T017 `E/harness/simulator.py`:
  - leitura ruidosa (EXP-023 `noise.corrupt` mais confundidores);
  - confiança calibrada na 086;
  - leitor simulado R1, R2 e R3;
  - pacote `leitorum-feedback/1`.
- [x] T018 `E/tests/test_simulator.py` (plan §6). Verificar com `O python -m pytest E/tests` e `uv run ruff check .`.
- [x] T019 `STATE.md` (hashes, contagens, vazamento zero). Commit `F02 … fluxos longitudinais sinteticos e
  simulador de feedback`.

## F03 — Motor adaptativo e travas

- [x] T020 `E/harness/state.py`: schema `leitorum-learning-state/1`, poda determinística, (de)serialização.
- [x] T021 `E/harness/diff_signal.py`:
  - alinhamento de unidades e de leitura;
  - `classify_edit`;
  - JSON Patch: LDF 2.0 `human_corrections` e `organizer-result/1`.
- [x] T022 `E/harness/adaptive_organizer.py`:
  - centróides hierárquicos incrementais;
  - pistas novas de referência e `ref_shape_user` (peso 0 na âncora);
  - regressão logística online ancorada com projeção;
  - $\beta$ e $T_{\text{user}}$;
  - `review_order` por $g_i$;
  - `click` com re-decodificação e passo local (E4b).
- [x] T023 `E/harness/adaptive_ocr_corrector.py`:
  - léxico de escopo;
  - confusões pessoais com prior global e suporte mínimo;
  - canal ruidoso com proteção;
  - logístico de `low_confidence`;
  - curadoria.
- [x] T024 `E/harness/safety_gate.py`: gate de recompensa, projeção, portão-sombra (sementes e canário),
  snapshot e rollback.
- [x] T025 `E/tests/test_diff_signal.py` e `E/tests/test_adaptive_engine.py` (plan §6), incluindo atualização
  destrutiva injetada → rollback, isolamento por `user_id` e p95 < 25 ms.
- [x] T026 `ruff` sem avisos; `STATE.md`; commit `F03 … motor autonomo de melhoria continua e travas
  anti-regressao`.

## F04 — Calibração, curvas, ablações, estresse e D-usuário

- [x] T030 `E/harness/calibrate.py`: grade só nos fluxos de validação, gravando `E/artifacts/thresholds.json`
  (SHA-256 no `STATE.md`) e os limiares finais das hipóteses, **antes** do teste.
- [x] T031 `E/harness/evaluate.py --split test`, uma vez. Mede:
  - escada cumulativa e *leave-one-out*;
  - curvas em $t = 1, 5, 10, 20, 40$ (Organizador e leitura);
  - R3 com e sem travas;
  - E4 com $k = 0..3$ cliques e três ordens;
  - custo (latência e KB do estado);
  - replay de 500 estudos.
- [x] T032 `E/harness/dusuario_continual.py`, **com o banco ativo do D:**, escolhido pelo usuário na revisão da F01:
  - cópia pela API de backup em pasta temporária, origem e cópia em `mode=ro`, apagada no `finally`;
  - avaliação prequencial com $T_{\text{user}}$ desligado;
  - só números.
- [x] T033 Revisor (subagente) audita os JSON de benchmark: só números e chaves fixas. Gravar em
  `evaluation/benchmarks/`.
- [x] T034 `STATE.md`; commit `F04 … calibracao, curvas de aprendizado, ablacoes e benchmarks`.

## F05 — Resultados e fechamento

- [x] T040 `E/RESULTS.md`: veredito de H1–H5, tabelas de ablação, curvas, R3, D-usuário, limites e comandos de
  reprodução.
- [x] T041 (não aplicável: portão não atingido, sem ADR-011) Se o portão de adoção for atingido, `docs/adr/ADR-011-melhoria-continua-autonoma.md`:
  - schema do estado por usuário;
  - contrato do pacote de feedback;
  - garantias de segurança;
  - proposta do LDF 2.1 para as 4 seções.
- [x] T042 `CLAUDE.md` (estado) e `STATE.md`; validação global (`uv run pytest`, `uv run ruff check .` e testes do
  EXP-023 e do EXP-024); `git status` limpo.
- [x] T043 Commit `F05 … resultados, ADR-011 e fechamento do experimento`. **Parar para revisão.**

## Dependências

T010–T015 (dados congelados) → T016–T018 → T020–T025 → T030 (limiares congelados) → T031 → T032–T033 → T040–T043.
