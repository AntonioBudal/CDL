# Experiment Plan: EXP-002 — Detecção de Layout e Segmentação de Linhas e Blocos

**Diretório**: `experiments/EXP-002/` | **Date**: 2026-10-02 | **Spec**: [spec.md](./spec.md)

**Status**: `APPROVED` pelo usuário em 2026-10-02 (incluindo `graphic_box` → `structure.diagrams[]`).

## Revisão pós-Fase 1 (2026-10-02)

- **Docling Heron entra** como detector de layout (blocos), Apache-2.0, pesos em safetensors. Correspondência de
  classes: `Title`/`Section-header` → `title`; `Text` → `paragraph`; `Picture` → `graphic_box`;
  `Footnote`/`Page-header`/`Page-footer` → `margin_note` (aproximação). O mAP de blocos passa a comparar
  "Heron" com "detector de linhas + regras".
- **docTR** fica `NEEDS VALIDATION` (pesos sem licença declarada) e só entra com exceção do usuário.
- Ambientes: `envs/harness`, `envs/docufcn`, `envs/heron` e, condicionalmente, `envs/doctr`.

## Summary

Gerar páginas de caderno sintéticas "fotográficas" com a posição exata de cada linha e bloco; construir um harness
de detecção (métricas, supervisor, conversão para LDF) validado com um detector de referência; e então medir, em CPU,
um baseline clássico e os modelos de licença verificada na detecção de linhas, a montagem de blocos e o efeito da
retificação de perspectiva, com o custo de cada etapa medido separadamente.

## Technical Context

**Language/Version**: Python 3.14 no projeto principal e no harness; ambientes isolados por candidato quando a
biblioteca exigir outra versão (Doc-UFCN: Python 3.10).

**Primary Dependencies**: projeto principal inalterado (`pydantic`). Harness: Pillow, NumPy, OpenCV
(`opencv-python-headless`, Apache-2.0), fontTools, pytest. Um ambiente por candidato com modelo.

**Storage**: arquivos locais. Páginas geradas em `dataset/processed/exp-002/` (fora do Git, regeneráveis); manifestos
em `dataset/fixtures/exp-002/`; pesos em `models/exp-002/`; relatórios em `evaluation/benchmarks/`.

**Testing**: `pytest` no projeto principal para as métricas genéricas; testes do harness no ambiente do harness, sem
nenhum modelo instalado.

**Target Platform**: Windows 11, i5-8265U, 7,9 GB RAM, CPU-only.

**Performance Goals (critérios de avaliação)**: F1 de linhas ≥ 0,90 (limpo) e ≥ 0,80 (degradado); mAP@0,5 de blocos
≥ 0,70; ≤ 2 s por página; ≤ 2 GB de pico.

**Constraints**: inferência offline; só wheels; nada de AGPL; teto de 20 GB de dados locais (uso atual ~3,5 GB).

**Scale/Scope**: 180 páginas de teste (3 níveis de degradação × 60) + 30 páginas de desenvolvimento; ~25 linhas
por página (~4.500 linhas de teste); 3 detectores de linhas × 3 modos de retificação.

## Verificação prévia de candidatos (2026-10-02, por resolução a seco de wheels para Windows)

| Candidato | Resultado | Consequência |
| :--- | :--- | :--- |
| Baseline clássico (OpenCV 5.0 + NumPy, Python 3.14) | resolve só com wheels | **entra** |
| Doc-UFCN 0.1.9 (código BSD-3-Clause; Python 3.10; `torch` 2.1.0) | resolve só com wheels | **entra**; pesos Teklia MIT declarados, a reconfirmar na Fase 1 |
| docTR 1.1.0 (`python-doctr`, Apache-2.0; Python 3.14; `torch` 2.14) | resolve com wheels, exceto `langdetect` (sdist em Python puro) | **novo candidato**; licença dos pesos pré-treinados a verificar na Fase 1 |
| Kraken 7.1.1 e 5.3.0 (Apache-2.0) | **não resolve**: depende de `coremltools`, sem wheels para Windows | **excluído** (FR-006: só wheels) |
| YOLO / `ultralytics` | — | **excluído** (AGPL, decisão do usuário) |

Nenhum candidato prevê os quatro tipos de bloco do escopo. Por isso os blocos serão montados por **regras
geométricas sobre as linhas detectadas** (ver "Montagem de blocos"), aplicadas igualmente à saída de cada detector.
Isso é declarado como limitação: o mAP de blocos mede "detector + regras", não um detector de layout treinado. Se a
Fase 1 encontrar um modelo de layout com licença verificada, instalável por wheels e que rode em CPU, ele entra como
candidato adicional.

## Constitution Check

| Princípio | Situação |
| :--- | :--- |
| 1 — Local-first | PASS: inferência offline; rede só para pacotes, pesos e fontes. |
| 2 — Evidência antes de decisão | PASS: nenhum detector é adotado; as regras de blocos são calibradas só no conjunto de desenvolvimento. |
| 3 — Reprodutibilidade | PASS: commits limpos antes de medir; locks por ambiente; geração determinística com seeds; hashes de páginas e pesos. |
| 4 — Reconhecimento × interpretação | PASS: só geometria; nenhum texto é lido. |
| 6 — Medir antes de otimizar | PASS: sem otimização nativa; imagens grandes reduzidas por parâmetro registrado. |
| 7 — Experimentos antes de features | PASS: código de candidatos em `experiments/EXP-002/`; em `src/` só métricas genéricas de detecção. |
| 8 — LDF como contrato | PASS: saídas convertidas e validadas pelo contrato `leitorum_di.contracts.ldf` / JSON Schema. |
| Governança de escopo | PASS: nada fora de `document-intelligence/`; nada instalado no sistema. |
| Licenças | PASS: AGPL excluído; portão de licença do EXP-001 reaproveitado. |

## Gerador de páginas sintéticas

1. **Página limpa** (1240 × 1754 px, proporção A4): fundo de papel levemente texturizado, pauta horizontal
   (espaçamento sorteado de 44–56 px) e linha de margem.
2. **Conteúdo** com texto fictício em PT-BR (gerador de frases do EXP-001, ampliado):
   - `title`: 1 linha no topo, fonte maior, às vezes sublinhada;
   - `paragraph`: 2–4 blocos de 2–7 linhas apoiadas na pauta, com variação de inclinação (±2°), deslocamento de
     linha de base e espaçamento entre palavras;
   - `margin_note`: 0–2 notas curtas na margem, menores, às vezes giradas até 90°;
   - `graphic_box`: 0–1 diagrama simples (caixas/elipses ligadas por setas, com rótulos curtos).
3. **Variedade de "escritores"**: Caveat mais 3–4 fontes manuscritas OFL (a verificar na Fase 1), cor de tinta e
   espessura sorteadas por página.
4. **Verdade de chão**: para cada linha, a máscara de tinta renderizada dá o polígono (retângulo rotacionado mínimo)
   e a bbox justa. Texto dentro de `graphic_box` é região "ignorar": não conta como acerto nem como erro de linha.
5. **Degradações fotográficas** em 3 níveis (limpo, leve, forte), aplicadas à imagem **e** à geometria:
   página sobre fundo de mesa; homografia (cantos sorteados); curvatura cilíndrica perto da lombada; gradiente de
   iluminação e sombra; desfoque; ruído; compressão JPEG. Perspectiva e curvatura transformam os pontos dos
   polígonos (densificados) e a bbox é recalculada. O manifesto guarda também os 4 cantos da folha na imagem final
   (verdade de chão da retificação).
6. **Conjuntos**: `dev` (30 páginas, seeds próprias) só para calibrar o baseline e as regras de blocos; `test`
   (180 páginas) congelado, nunca usado para ajuste. Um pequeno conjunto `large` (10 páginas a ~12 MP) só para o
   caso de borda de memória.

## Métricas

- **Linhas**: casamento guloso um-para-um por IoU decrescente; Precision, Recall, F1 em IoU ≥ 0,5 (critério principal)
  e ≥ 0,75; IoU médio dos pares casados. Duas variantes de IoU: bbox alinhada aos eixos (a do LDF) e polígono
  (rasterizado). Predições cuja maior parte cai em região "ignorar" são descartadas da contagem.
- **Blocos**: AP@0,5 por tipo (interpolação de 101 pontos, no estilo COCO) e mAP; detectores sem confiança usam 1,0.
- **Retificação**: erro médio dos cantos da folha (px) e F1 de linhas com e sem retificação. As predições feitas na
  imagem retificada voltam para as coordenadas originais pela homografia inversa antes da avaliação.
- **Custo**: ms por página (mediana, p95) e pico de memória, separados em retificação, detecção e montagem de blocos.

As métricas genéricas sobre caixas (casamento, P/R/F1, AP) ficam em `src/leitorum_di/metrics/detection.py`, em Python
puro, com testes de valores calculados à mão. A IoU de polígono (que precisa de rasterização) fica no harness.

## Correspondência com o LDF

Os tipos de bloco aprovados não coincidem um a um com o enum de `structure.blocks[].type` do LDF 1.0
(`heading`, `paragraph`, `list_item`, `text_block`, `table`, `margin_note`):

| Tipo do EXP-002 | No LDF 1.0 |
| :--- | :--- |
| `title` | bloco `heading` (o papel semântico `title` é do EXP-004) |
| `paragraph` | bloco `paragraph` |
| `margin_note` | bloco `margin_note` |
| `graphic_box` | sem tipo de bloco; vai para `structure.diagrams[]` com a bbox da região e `nodes`/`edges` vazios, se o schema aceitar. Se não aceitar, a lacuna é registrada no relatório |

O schema do LDF **não** é alterado neste experimento; qualquer mudança de contrato exige decisão própria.

## Candidatos e modos

| Etapa | Variantes |
| :--- | :--- |
| Retificação | `none`; `contour` (OpenCV: maior quadrilátero da folha + homografia); `docufcn-page` (máscara de página do Doc-UFCN + homografia), se o modelo de página fechar licença |
| Detecção de linhas | `classic` (binarização adaptativa, remoção da pauta, perfis de projeção e componentes conexos); `docufcn-line`; `doctr` (detecção de palavras + agrupamento em linhas do próprio docTR) |
| Montagem de blocos | regras únicas para todos: agrupamento por espaçamento vertical e alinhamento; `title` pela altura e posição no topo; `margin_note` pela posição relativa à margem; `graphic_box` por componentes de tinta grandes que não são linhas |

Cada combinação retificação × detector roda em subprocesso isolado com o supervisor do EXP-001 (generalizado para
devolver geometria em vez de texto).

## Protocolo de medição

- Aquecimento: 2 páginas descartadas após a carga.
- 3 repetições por combinação; mediana das medianas.
- Lote 1; threads padrão; seed 1234; espera de até 180 s por RAM livre ≥ 1 GiB antes de cada repetição.
- Imagens acima de 2.500 px no lado maior são reduzidas antes da detecção, com o fator registrado e as predições
  reescaladas.

## Critérios de parada

| Situação | Ação |
| :--- | :--- |
| Pico de memória > 2,0 GB | `ABORTED: memory` |
| Carga do modelo > 120 s | `ABORTED: load timeout` |
| Mediana das 10 primeiras páginas > 20 s (10× a meta) | `ABORTED: latency` |
| Execução > 30 min | `ABORTED: wall time` |
| Licença não verificada sem exceção, ou SHA-256 divergente | `REFUSED` |
| RAM livre < 1 GiB após a espera | `SKIPPED` |
| Uso local previsto > 20 GB | parar e perguntar ao usuário |

## Project Structure

```text
experiments/EXP-002/
├── spec.md  plan.md  tasks.md
├── candidates.json                 # candidatos, revisões, licenças, SHA-256
├── envs/harness/                   # Pillow, NumPy, OpenCV, fontTools, pytest (+ leitorum-di local)
├── envs/docufcn/                   # Python 3.10, doc-ufcn, torch 2.1
├── envs/doctr/                     # Python 3.14, python-doctr, torch 2.14
├── harness/
│   ├── pages/                      # gerador de páginas e degradações
│   ├── adapters/                   # referência, falsos, classic, docufcn, doctr, retificadores
│   ├── supervisor.py  worker.py    # derivados do EXP-001, generalizados
│   ├── blocks.py                   # montagem de blocos por regras
│   ├── evaluate.py  analyze.py     # métricas de detecção, IoU de polígono, análise por degradação
│   ├── to_ldf.py                   # conversão e validação contra o contrato LDF
│   └── run.py
├── tests/
├── environment.md
└── RESULTS.md

src/leitorum_di/metrics/detection.py   # casamento, P/R/F1, AP (genérico, sem dependências)
dataset/fixtures/exp-002/              # frases, manifestos, fontes OFL
dataset/processed/exp-002/             # páginas geradas (fora do Git)
models/exp-002/                        # pesos (fora do Git)
```

**Structure Decision**: o harness do EXP-001 não é alterado (experimento aceito). O supervisor e o worker são
copiados para o EXP-002 e generalizados; se o padrão se repetir no EXP-003, a extração para um módulo comum será
proposta separadamente.

## Uso de disco previsto

Ambientes: ~1,0 GB (Doc-UFCN, `torch` 2.1) + ~0,7 GB (docTR) + ~0,1 GB (harness). Pesos: < 0,3 GB. Páginas: ~0,4 GB.
Total adicional ≈ 2,5 GB → ~6 GB no total, abaixo do teto de 20 GB.

## Riscos

| Risco | Mitigação |
| :--- | :--- |
| Pesos do docTR ou do Doc-UFCN sem licença verificável | Ficam fora ou pedem exceção do usuário; o baseline clássico garante pelo menos uma linha de comparação. |
| Páginas sintéticas fáceis demais ou irreais | Três níveis de degradação; análise por tipo de degradação; limitação declarada no relatório. |
| Regras de blocos ajustadas ao gerador | Calibração só no `dev`, com seeds diferentes do `test`; regras únicas para todos os detectores. |
| Curvatura não corrigida por homografia | Medida à parte por tipo de degradação; correção de curvatura fica fora desta rodada. |
| RAM livre oscilando perto de 1 GiB | Espera de até 180 s; repetições `SKIPPED` registradas. |

## Commits

Seguindo o padrão do usuário: um commit por fase, `FNN(document-inteligence) EXP-002 <nome da fase>`, com o código
commitado antes de cada medição para os relatórios apontarem para árvore limpa.

## Complexity Tracking

| Desvio | Por que é necessário | Alternativa mais simples rejeitada porque |
| :--- | :--- | :--- |
| Três ambientes `uv` | Doc-UFCN exige Python 3.10 e `torch` 2.1; docTR usa `torch` 2.14. | Um ambiente único não resolve. |
| Supervisor copiado do EXP-001 | O EXP-001 está aceito e não deve mudar. | Editar o harness aceito alteraria a reprodutibilidade do EXP-001. |
| Blocos por regras | Nenhum candidato instalável prevê os tipos de bloco do escopo. | Sem isso, H2 ficaria sem resposta. |
