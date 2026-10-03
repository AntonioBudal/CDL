# Tasks: EXP-002 — Detecção de Layout e Segmentação de Linhas e Blocos

**Input**: [spec.md](./spec.md), [plan.md](./plan.md)

**Status**: `APPROVED` em 2026-10-02. **Fases 0 e 1 concluídas**; Fase 2 aguardando autorização.

**Formato**: `[ID] [P?] [Cenário] Descrição` — `[P]` = pode rodar em paralelo; C1–C4 = cenários da spec.

Cada fase termina num checkpoint: reporto ao usuário e só sigo com autorização. Downloads de pesos acontecem só a
partir da Fase 3.

---

## Fase 0 — Portões

- [x] T001 Spec aprovada com ajustes (2026-10-02).
- [x] T002 Usuário aprova `plan.md` e `tasks.md`.

## Fase 1 — Licenças e ambientes (sem download de pesos)

- [x] T003 Verificar licenças, com URL e data: Doc-UFCN (código no repositório oficial; pesos `doc-ufcn-generic-historical-line`, `doc-ufcn-norhand-v1-line`, `doc-ufcn-generic-page`), docTR (código e pesos pré-treinados de detecção), OpenCV 5.0. Registrar em `docs/models-and-licensing.md` e criar `experiments/EXP-002/candidates.json` com revisões fixas e SHA-256 publicados.
- [x] T004 Registrar as exclusões com motivo: Kraken (sem wheels de `coremltools` no Windows) e YOLO/`ultralytics` (AGPL).
- [x] T005 [P] Escolher e verificar 3–4 fontes manuscritas OFL adicionais (licença, glifos de `á é í ó ú â ê ô ã õ à ç` e maiúsculas).
- [x] T006 [P] Procurar um modelo de layout com licença verificada, instalável por wheels e viável em CPU que preveja blocos; registrar o achado (inclusive "nenhum").
- [x] T007 Criar `envs/harness`, `envs/docufcn` e `envs/doctr` com `uv lock` (sem instalar) e registrar versões em `experiments/EXP-002/environment.md`, com a estimativa de disco.

**Checkpoint 1**: lista final de candidatos e ambientes resolvíveis. Reportar. *(Atingido em 2026-10-02.)*

Resultado da Fase 1 (detalhes em `candidates.json`, `environment.md` e `docs/models-and-licensing.md`):

- `VERIFIED`: baseline clássico (OpenCV, Apache-2.0); Doc-UFCN (código BSD-3-Clause pelo PyPI; pesos de linha e de
  página MIT); **Docling Heron** (Apache-2.0, safetensors) — encontrado em T006 como detector de layout com classes
  mapeáveis para `title`, `paragraph`, `graphic_box` (e, por aproximação, `margin_note`); treinado em documentos impressos.
- `NEEDS VALIDATION`: docTR — código Apache-2.0, mas os pesos não declaram licença e vêm de um domínio da Mindee.
  Fora, salvo exceção do usuário.
- Excluídos: Kraken (sem wheels de `coremltools` no Windows), YOLO/`ultralytics` (AGPL), PP-DocLayout (exige PaddlePaddle; não avaliado).
- 5 fontes manuscritas OFL (Caveat + 4 do `google/fonts`), todas com glifos PT-BR completos.
- 4 ambientes resolvidos só com `uv lock`; disco previsto de ~6–7 GB no total.

## Fase 2 — Cenário 1: gerador de páginas e harness (sem modelos)

- [ ] T008 [C1] Ampliar as frases fictícias PT-BR e gerar o conteúdo das páginas (títulos, parágrafos, notas, rótulos de diagrama) em `dataset/fixtures/exp-002/`.
- [ ] T009 [C1] Gerador de página limpa com pauta, margem, fontes e verdade de chão por máscara de tinta (`harness/pages/`), com testes de geometria.
- [ ] T010 [C1] Degradações fotográficas (fundo, homografia, curvatura, iluminação, sombra, desfoque, ruído, JPEG) aplicadas à imagem e aos polígonos, com testes de que a geometria acompanha a imagem; cantos da folha no manifesto.
- [ ] T011 [C1] Gerar e congelar os conjuntos `dev` (30), `test` (180, 3 níveis) e `large` (10) com manifestos e SHA-256; imagens em `dataset/processed/exp-002/`.
- [ ] T012 [P] [C1] `src/leitorum_di/metrics/detection.py`: casamento guloso por IoU, Precision/Recall/F1, IoU médio, AP/mAP — com testes de valores calculados à mão em `tests/`.
- [ ] T013 [C1] IoU de polígono por rasterização e regiões "ignorar" no avaliador do harness, com testes.
- [ ] T014 [C1] Supervisor e worker derivados do EXP-001, devolvendo geometria; detector de referência e detectores falsos (memória, tempo, falha, deslocamento conhecido).
- [ ] T015 [C1] `harness/to_ldf.py`: conversão para o LDF 1.0 (tabela de correspondência do plano) e validação pelo contrato; registrar se `graphic_box` cabe em `diagrams[]`.
- [ ] T016 [C1] Testes do harness: referência dá F1 = mAP = 1,0; deslocamentos conhecidos dão os valores esperados; limites geram `ABORTED`; candidato sem licença gera `REFUSED`; saída válida no LDF.
- [ ] T017 [C1] `pytest`, `ruff`; executar o benchmark com o detector de referência no `test` e guardar o log.

**Checkpoint 2**: harness demonstrado sem modelos. Reportar.

## Fase 3 — Cenários 2 e 3: detectores de linhas e blocos

- [ ] T018 [C2] Baseline `classic` (binarização adaptativa, remoção da pauta, perfis de projeção, componentes conexos), com parâmetros calibrados **só** no `dev` e registrados.
- [ ] T019 [C3] `harness/blocks.py`: regras de montagem de blocos calibradas **só** no `dev`; testes com páginas de referência.
- [ ] T020 [C2] Instalar `envs/docufcn` e `envs/doctr`; baixar pesos das revisões fixadas para `models/exp-002/`, conferindo SHA-256 antes da carga. **Primeira etapa com download de pesos.** Medir o disco antes.
- [ ] T021 [P] [C2] Adaptador `docufcn-line`.
- [ ] T022 [P] [C2] Adaptador `doctr` (detecção + agrupamento em linhas).
- [ ] T023 [C2] Commit limpo; executar os 3 detectores × 3 níveis de degradação (sem retificação), 3 repetições, e a montagem de blocos sobre cada saída; validar as saídas no LDF.

**Checkpoint 3**: tabela de linhas e blocos sem retificação. Reportar.

## Fase 4 — Cenário 4: retificação de perspectiva

- [ ] T024 [C4] Retificador `contour` (OpenCV) e, se a licença fechar, `docufcn-page`; inversão da homografia para avaliar nas coordenadas originais; testes com cantos conhecidos.
- [ ] T025 [C4] Medir a retificação isolada: erro dos cantos (px), ms por página, pico de memória.
- [ ] T026 [C4] Executar os detectores com cada retificador na camada degradada e comparar com `none`; registrar o custo total (retificação + detecção).
- [ ] T027 [C4] Caso de borda `large` (~12 MP): memória e tempo da melhor combinação.

**Checkpoint 4**: tabela com × sem retificação e custo isolado. Reportar.

## Fase 5 — Análise de falhas

- [ ] T028 F1 por tipo de degradação (perspectiva, curvatura, sombra, desfoque) e por tipo de bloco; principais modos de falha (linhas fundidas, quebradas, perdidas, falsos positivos na pauta).
- [ ] T029 Veredito de H1–H5 com os critérios de avaliação aprovados.

**Checkpoint 5**: análise concluída. Reportar.

## Fase 6 — Relatório e decisão

- [ ] T030 `experiments/EXP-002/RESULTS.md` com manifesto de reprodutibilidade, desvios e limitações.
- [ ] T031 ADR em `docs/adr/` com a decisão sobre segmentação e retificação.
- [ ] T032 Conferência final: testes, `ruff`, nada fora de `document-intelligence/`, pesos e páginas fora do Git, disco abaixo de 20 GB.
- [ ] T033 Submeter ao usuário para aceite. **Não iniciar o EXP-003 antes do aceite.**

---

## Dependências

- T002 → Fase 1 → Fase 2 → Fase 3 → Fase 4 → Fase 5 → Fase 6.
- Na Fase 2: T008 → T009 → T010 → T011; T012 e T013 em paralelo com T009–T011; T014–T016 dependem de T011–T013.
- T018 e T019 não dependem de downloads e podem começar logo após o Checkpoint 2; T021/T022 dependem de T020.
- A Fase 4 depende dos adaptadores da Fase 3.
