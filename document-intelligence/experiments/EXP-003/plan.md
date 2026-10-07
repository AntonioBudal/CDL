# Experiment Plan: EXP-003 — Reconstrução Espacial e Ordem de Leitura

**Diretório**: `experiments/EXP-003/` | **Date**: 2026-10-05 | **Spec**: [spec.md](./spec.md)

**Status**: `APPROVED` pelo usuário em 2026-10-07, com um ajuste: **sem módulo comum** — o código reaproveitado
é copiado para dentro de `experiments/EXP-003/`. Uma execução dos detectores (em vez de três) foi aprovada.

## Summary

Estender o gerador de páginas para registrar a ordem de leitura e produzir três famílias de layout; implementar
métricas de ordem e três ordenadores algorítmicos; medi-los primeiro sobre o layout verdadeiro e depois sobre o
layout detectado pela combinação do ADR-002 (retificação por contorno + Doc-UFCN `norhand` + Heron), separando o
erro de ordenação do erro herdado da detecção.

## Technical Context

**Language/Version**: Python 3.14 (harness). Os detectores rodam nos ambientes já instalados do EXP-002
(`envs/docufcn` em Python 3.10, `envs/heron` em 3.14).

**Primary Dependencies**: nenhuma nova. Harness: Pillow, NumPy, OpenCV, jsonschema, pytest (mesmo lock do EXP-002).

**Storage**: páginas em `dataset/processed/exp-003/` (fora do Git, ~180 MiB); manifestos em
`dataset/fixtures/exp-003/`; relatórios em `evaluation/benchmarks/`.

**Testing**: métricas de ordem em `src/leitorum_di/metrics/` com testes de valores à mão; testes do harness sem modelos.

**Target Platform**: Windows 11, i5-8265U, 7,9 GB RAM, CPU-only.

**Performance Goals (critérios de avaliação)**: acurácia de ordem de blocos ≥ 0,95 (layout verdadeiro) e ≥ 0,85
(layout detectado); ordenação ≤ 50 ms por página.

**Constraints**: sem downloads novos; sem modelos novos; inferência offline; teto de 20 GB (uso atual 7,5 GB;
acréscimo previsto < 0,5 GB).

**Scale/Scope**: `dev` com 30 páginas e `test` com 180 (3 famílias × 3 níveis de degradação × 20 páginas);
3 ordenadores × 2 fontes de layout.

## Constitution Check

| Princípio | Situação |
| :--- | :--- |
| 1 — Local-first | PASS: nada de rede; pesos já baixados e conferidos no EXP-002. |
| 2 — Evidência antes de decisão | PASS: parâmetros dos ordenadores calibrados só no `dev`. |
| 3 — Reprodutibilidade | PASS: geração por seeds; commits limpos antes de medir; hashes de páginas e pesos. |
| 4 — Reconhecimento × interpretação | PASS: só geometria; a ordem é derivada de posição, não de texto. |
| 6 — Medir antes de otimizar | PASS: algoritmos em Python puro/NumPy. |
| 7 — Experimentos antes de features | PASS: em `src/` só métricas genéricas de ordem. |
| 8 — LDF como contrato | PASS: saída em `structure.reading_order`, validada; lacunas registradas, contrato intocado. |
| Governança de escopo e licenças | PASS: nada fora de `document-intelligence/`; nenhum componente novo com licença a verificar. |

## Verdade de chão da ordem de leitura

O gerador passa a registrar `reading_order` (lista de ids de blocos) e a ordem das linhas em cada bloco:

1. título;
2. blocos do fluxo principal, de cima para baixo;
3. **nota de margem** logo depois do parágrafo ao lado do qual foi escrita (cada nota guarda o id do parágrafo-âncora);
4. **caixa de destaque lateral** logo depois do parágrafo que ela acompanha;
5. **caixa gráfica** na posição vertical em que aparece no fluxo;
6. dentro do bloco, linhas de cima para baixo (na nota vertical, na direção da escrita).

## Famílias de layout

| Família | Conteúdo | O que testa |
| :--- | :--- | :--- |
| `single` | título, parágrafos, eventual diagrama (como no EXP-002, sem notas) | caso base |
| `margin` | 2–4 notas de margem ancoradas a parágrafos distintos, horizontais e verticais | ancoragem lateral |
| `callout` | 1–2 parágrafos estreitados com uma caixa de destaque à direita (texto curto dentro de uma moldura), além de notas de margem ocasionais | leitura lado a lado |

A caixa de destaque é um bloco `paragraph` (texto com moldura), não um `graphic_box`. Duas colunas ficam fora
(decisão registrada na spec §6).

## Métricas

- **Acurácia de ordem** = 1 − distância de edição entre a sequência prevista e a verdadeira, dividida pelo maior
  dos dois comprimentos. Calculada para blocos (critério principal) e para linhas.
- **Tau de Kendall** sobre os elementos presentes nas duas sequências (complementar; ignora faltas e sobras).
- **Layout detectado**: os blocos previstos são casados com os verdadeiros (IoU ≥ 0,5, mesmo casamento do
  EXP-002) e a sequência prevista é reescrita com os ids verdadeiros. Blocos previstos sem par e blocos
  verdadeiros sem par entram na distância de edição e são contados à parte.
- **Decomposição da perda**: (a) acurácia com layout verdadeiro; (b) acurácia com layout detectado;
  (c) acurácia com layout detectado restrita aos blocos casados — a diferença (a − c) é erro de ordenação
  causado por geometria imprecisa, e (c − b) é erro herdado de blocos faltando ou sobrando.

As métricas genéricas (distância de edição normalizada, tau de Kendall) ficam em
`src/leitorum_di/metrics/ordering.py`, em Python puro, com testes.

## Ordenadores

| Id | Método | Parâmetros a calibrar no `dev` |
| :--- | :--- | :--- |
| `naive` | ordena blocos pelo topo e, em empate, pela esquerda | tolerância de empate vertical |
| `xycut` | corte XY recursivo: divide por faixas horizontais vazias e depois por faixas verticais | largura mínima das faixas vazias |
| `anchored` | separa o fluxo principal das regiões laterais (margem e destaque) pela posição em relação à borda do texto; ordena o fluxo de cima para baixo e insere cada região lateral depois do bloco principal com maior sobreposição vertical | limiares de lateralidade e de sobreposição |

Linhas dentro do bloco: ordenação pelo centro projetado na direção perpendicular à linha de base (estimada pelo
polígono), para tolerar inclinação.

Atribuição de linhas a blocos no layout detectado: pelo centro da linha dentro da caixa do bloco; linhas sem bloco
formam um bloco próprio e são contadas.

## Fontes de layout

1. **Verdadeiro**: linhas e blocos do manifesto.
2. **Detectado (direção do ADR-002)**: retificação por contorno → Doc-UFCN `norhand` (linhas, levadas de volta às
   coordenadas originais) + Heron na imagem original (blocos). Uma execução por página do `test` do EXP-003 —
   aqui o objetivo é a acurácia de ordem, não a latência dos detectores (já medida no EXP-002).

## Protocolo de medição

- Ordenadores rodam no processo do harness: tempo por página com `perf_counter_ns` (3 repetições, mediana) e pico
  de alocação com `tracemalloc`. Sem subprocesso: não há modelo a isolar, e o custo esperado é de milissegundos.
- Detectores rodam com o supervisor do EXP-002 e os mesmos limites (2 GB, RAM livre ≥ 1 GiB, espera de até 600 s).
- Seed 1234; commits limpos antes de cada medição.

## Critérios de parada

| Situação | Ação |
| :--- | :--- |
| RAM livre < 1 GiB após a espera, na etapa de detecção | `SKIPPED`; avisar o usuário para liberar memória |
| Detector estoura memória, carga ou tempo | `ABORTED`, como no EXP-002 |
| Ordenador > 5 s numa página | registrar como falha do método naquela página |
| Uso local previsto > 20 GB | parar e perguntar |

## Project Structure

```text
experiments/EXP-003/
├── spec.md  plan.md  tasks.md
├── harness/
│   ├── pages/                      # cópia do gerador do EXP-002 + ordem de leitura e famílias de layout
│   ├── supervisor.py  worker.py    # cópias do EXP-002, sem alteração de comportamento
│   ├── rectify.py  evaluate.py  to_ldf.py
│   ├── adapters/                   # cópias: reference, docufcn, heron, rectifiers
│   ├── generate.py
│   ├── orderers.py                 # naive, xycut, anchored
│   ├── order_eval.py               # casamento, reescrita de ids, decomposição da perda
│   ├── detect.py                   # roda a combinação do ADR-002 e guarda o layout detectado
│   └── calibrate.py  run.py  analyze.py
├── tests/
├── calibration.json
└── RESULTS.md

src/leitorum_di/metrics/ordering.py # distância de edição normalizada, tau de Kendall
dataset/fixtures/exp-003/           # manifestos dev/test com ordem de leitura
dataset/processed/exp-003/          # páginas e layouts detectados (fora do Git)
```

**Structure Decision (decisão do usuário, 2026-10-07):** nada de `experiments/common/`. O código reaproveitado do
EXP-002 é **copiado** para `experiments/EXP-003/harness/`; os diretórios do EXP-001 e do EXP-002 não são alterados.
Os ambientes `uv` e os pesos do EXP-002 são reutilizados por caminho, sem reinstalar nem baixar.

## Uso de disco previsto

Páginas novas ~0,2 GB; layouts detectados e relatórios < 0,1 GB. Total do projeto ≈ 7,8 GB.

## Riscos

| Risco | Mitigação |
| :--- | :--- |
| Ordem verdadeira "trivial" demais | três famílias; a família `single` serve de controle; resultados sempre separados por família |
| Regras do ordenador `anchored` ajustadas ao gerador | calibração só no `dev`; limitação declarada; comparação com `xycut`, que não conhece o gerador |
| Heron fraco em nota de margem (AP 0,53 no EXP-002) domina o erro de ponta a ponta | a decomposição da perda separa esse efeito |
| Caixa de destaque confundida com caixa gráfica pelo Heron | medido e reportado por família |
| RAM livre insuficiente na etapa de detecção | aviso prévio; a etapa algorítmica (Fases 1 e 2) não depende disso |

## Fases previstas *(as tarefas detalhadas vêm depois da aprovação deste plano)*

1. Cópia do harness, gerador com ordem de leitura e famílias, métricas de ordem, conjuntos `dev`/`test` — sem modelos.
2. Ordenadores, calibração no `dev` e avaliação sobre o layout verdadeiro.
3. Layout detectado nas páginas do `test` e avaliação de ponta a ponta com a decomposição da perda.
4. Ordem das linhas dentro do bloco, com e sem retificação.
5. Análise, relatório, ADR e aceite.

## Commits

Um commit por fase, `FNN(document-inteligence) EXP-003 <nome da fase>`, com o código commitado antes de cada medição.

## Complexity Tracking

| Desvio | Por que é necessário | Alternativa mais simples rejeitada porque |
| :--- | :--- | :--- |
| Cópia do harness do EXP-002 para o EXP-003 | decisão do usuário: cada experimento fica autocontido | um módulo comum foi proposto e recusado |
| Ordenadores medidos no próprio processo | não há modelo a isolar; custo de milissegundos | subprocesso por ordenador acrescentaria ruído maior que o próprio tempo medido |
| Uma execução (não três) dos detectores | só a saída importa aqui; a latência deles já foi medida no EXP-002 | repetir triplicaria ~15 min de máquina sem informação nova (as saídas são determinísticas) |
