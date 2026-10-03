# Experiment Specification: EXP-002 — Detecção de Layout e Segmentação de Linhas e Blocos

**Diretório do experimento**: `experiments/EXP-002/`

**Created**: 2026-10-02

**Status**: `APPROVED` pelo usuário em 2026-10-02, com ajustes (§6). Plano e tarefas autorizados na mesma resposta.
Nenhum código, instalação ou download foi feito.

**Input**: `docs/roadmap-experiments.md` §3 (EXP-002), `docs/ldf.md`, `docs/schemas/ldf-1.0.schema.json`, resultados e
infraestrutura do EXP-001 (aceito em 2026-10-02) e ADR-001.

**Pré-requisito**: EXP-001 `ACCEPTED`. O EXP-002 não depende de um reconhecedor de texto: localiza regiões, não as lê.

---

## 1. Pergunta e Hipóteses

**Pergunta central:** existe um método local, em CPU, com código e pesos de licença verificada, que localize as
**linhas de texto** e os **blocos** (`title`, `paragraph`, `margin_note`, `graphic_box`) de uma página de caderno
fotografada com qualidade suficiente para alimentar as etapas seguintes do pipeline? E a retificação de perspectiva
melhora esse resultado o bastante para justificar o seu custo?

- **H1 (linhas):** algum candidato atinge F1 ≥ 0,90 na detecção de linhas (IoU ≥ 0,5) em páginas limpas e F1 ≥ 0,80
  em páginas com degradações típicas de foto de celular.
- **H2 (blocos):** algum candidato atinge mAP@0,5 ≥ 0,70 nos tipos de bloco do escopo.
- **H3 (custo):** ≤ 2 s por página (mediana, CPU) e ≤ 2 GB de pico de memória.
- **H4 (baseline clássico — hipótese, não premissa):** um método sem aprendizado (projeções/morfologia) atinge H1 em
  páginas pautadas e limpas, mas degrada com perspectiva, curvatura e sombra. Pode ser refutada em qualquer sentido.
- **H5 (retificação):** retificar a perspectiva antes de segmentar aumenta o F1 de linhas na camada degradada em pelo
  menos 5 pontos, com custo adicional ≤ 0,5 s por página.

As metas de F1, mAP, tempo e memória são os **critérios de avaliação** dos candidatos (decisão do usuário,
2026-10-02); o experimento conclui com veredito explícito contra cada uma.

---

## 2. Cenários Experimentais *(equivalente a User Stories)*

### Cenário 1 — Benchmark de layout validado com páginas sintéticas de geometria conhecida (P1)

Páginas de caderno geradas com texto fictício, cuja posição exata de cada linha e bloco é conhecida, e um detector de
referência que devolve a verdade de chão.

**Por que P1:** sem anotações reais, só páginas geradas dão verdade de chão exata; e o harness precisa ser validado
antes de qualquer modelo (como no EXP-001).

**Teste independente:** detector de referência produz F1 = 1,0 e mAP = 1,0; detector falso com deslocamentos
conhecidos produz os valores esperados calculados à mão.

**Aceite:**
1. **Dado** o manifesto de páginas sintéticas, **quando** o benchmark roda com o detector de referência, **então** F1 = mAP = 1,0 e o log registra tempo, memória, seeds e hashes.
2. **Dado** um detector que estoura memória ou tempo, **quando** o benchmark o executa, **então** ele é encerrado e registrado como `ABORTED` sem afetar os demais.

### Cenário 2 — Detecção de linhas: baseline clássico × modelos (P2)

Cada candidato com licença verificada (ou exceção do usuário) roda em subprocesso isolado sobre páginas limpas e
degradadas.

**Aceite:** tabela por candidato com Precision, Recall e F1 de linhas (IoU 0,5 e 0,75), IoU médio dos pares
casados, ms por página (mediana, p95) e pico de memória, separada por nível de degradação.

### Cenário 3 — Blocos e caixas gráficas (P3)

Para os candidatos que produzem regiões, mAP@0,5 e AP por tipo: `title`, `paragraph`, `margin_note` e
`graphic_box` (caixa/diagrama, só a região — o grafo é do EXP-005). Listas e tabelas ficam fora.

**Aceite:** tabela por tipo de bloco; candidatos que só detectam linhas ficam registrados como "não se aplica".

### Cenário 4 — Retificação de perspectiva (P2)

Cada detector de linhas roda com e sem retificação prévia na camada degradada; o custo da retificação (tempo e
memória) é medido separadamente do custo da detecção.

**Aceite:** tabela F1 sem × com retificação, por detector e por tipo de degradação, e tabela de custo da etapa de
retificação isolada.

### Casos de borda

- Página sem texto, ou com uma única linha.
- Linhas que se tocam (ascendentes/descendentes) e texto sobre a pauta.
- Nota de margem vertical ou inclinada.
- Página fotografada com perspectiva forte, curvatura perto da lombada, sombra da mão, desfoque leve.
- Imagem muito grande (foto de 12 MP): precisa caber no orçamento de memória e tempo.

---

## 3. Requisitos

### Funcionais

- **FR-001**: O benchmark DEVE receber imagens de página inteira e anotações de linhas (bbox e polígono) e blocos (bbox, tipo).
- **FR-002**: Detecção de linhas avaliada por casamento um-para-um com IoU de caixas (limiares 0,5 e 0,75): Precision, Recall, F1 e IoU médio. Blocos avaliados por mAP@0,5 e AP por tipo.
- **FR-003**: Medir por candidato: ms por página (mediana, p95), tempo de carga e pico de memória do processo — com o supervisor do EXP-001 e os mesmos limites (2 GB; carga ≤ 120 s; RAM livre ≥ 1 GiB).
- **FR-004**: A saída de cada candidato DEVE ser convertida para o formato do LDF (`lines[].bbox/polygon`, `blocks[].type/bbox/line_ids`) e validada contra `ldf-1.0.schema.json` (Princípio 8).
- **FR-005**: Só entram candidatos com `LICENSE STATUS: VERIFIED` para código e pesos, ou com exceção explícita do usuário; registro em `docs/models-and-licensing.md` e em `candidates.json`.
- **FR-006**: Tudo instalável por wheels em ambientes `uv` isolados do experimento; nenhum binário no sistema; nada pesado no `pyproject.toml` principal.
- **FR-007**: Inferência offline; nenhuma imagem sai da máquina; nenhuma foto do usuário é usada.
- **FR-008**: Manifesto de reprodutibilidade completo (commit limpo, locks, revisões e SHA-256 dos pesos, seeds, dados, hardware).
- **FR-009**: Respeitar o teto de 20 GB de dados locais em `document-intelligence/`; perguntar antes de ultrapassar.
- **FR-010**: Dados: páginas sintéticas "fotográficas" com geometria conhecida (aprovado). Dataset público anotado só como complemento, se tiver licença verificada.
- **FR-011**: Retificação medida como etapa separada: F1 com e sem, e custo próprio (ms, memória).
- **FR-012**: Candidatos que dependem de bibliotecas AGPL estão excluídos.

### Entidades

- **Página**: id, imagem, SHA-256, dimensões, origem (`synthetic` | `real`), nível de degradação, licença.
- **Linha anotada**: id, bbox, polígono, bloco a que pertence.
- **Bloco anotado**: id, tipo (`title` | `paragraph` | `margin_note` | `graphic_box`), bbox, linhas.
- **Candidato** e **Execução**: como no EXP-001.

---

## 4. Candidatos Iniciais *(licenças a verificar na Fase 1)*

| # | Candidato | Tipo | Detecta | Situação conhecida hoje |
| :- | :--- | :--- | :--- | :--- |
| — | *Atualização da Fase 1 (2026-10-02): Docling Heron entra como detector de layout; docTR fica `NEEDS VALIDATION`; Kraken excluído. Ver `candidates.json`.* | | | |
| A | Baseline clássico (perfis de projeção + morfologia, em Pillow/NumPy ou OpenCV) | sem aprendizado | linhas, blocos simples | sem pesos; OpenCV é Apache-2.0 (a confirmar a versão) |
| B | Kraken — segmentador de linhas de base (`blla`) | rede neural | linhas (baseline + polígono), regiões | código Apache-2.0 (a confirmar); licença do modelo padrão a verificar |
| C | Doc-UFCN com modelos Teklia (`doc-ufcn-generic-historical-line`, `doc-ufcn-norhand-v1-line`, `doc-ufcn-generic-page`) | rede neural (FCN) | linhas, página | pesos MIT declarados no Hugging Face (visto em 2026-09-30); código a verificar |
| ~~D~~ | ~~`Teklia/yolov11-generic-page`~~ | detector YOLO | página/regiões | **Excluído** (decisão do usuário): a biblioteca `ultralytics` é AGPL-3.0 |

Outros candidatos podem entrar na Fase 1 se tiverem licença verificada e rodarem em CPU dentro do orçamento.
Nenhum é escolhido a priori (`docs/models-and-licensing.md` §1).

---

## 5. Critérios de Sucesso do Experimento

- **SC-001**: Benchmark com o baseline clássico e ≥ 1 modelo com licença verificada, nas camadas limpa e degradada.
- **SC-002**: Para cada candidato: Precision/Recall/F1 de linhas, mAP de blocos (quando aplicável), latência e memória, com veredito contra H1–H4.
- **SC-003**: Análise de falhas por tipo de degradação (perspectiva, curvatura, sombra, desfoque) e por tipo de bloco.
- **SC-004**: Saídas de todos os candidatos validadas contra o schema do LDF.
- **SC-005**: ADR com a decisão; `docs/models-and-licensing.md` atualizado.
- **SC-006**: Nada alterado fora de `document-intelligence/`; testes e `ruff` verdes; teto de 20 GB respeitado.

O experimento é bem-sucedido se responder à pergunta com evidência reproduzível, mesmo que nenhum candidato atinja as hipóteses.

---

## 6. Decisões do Usuário *(Clarify — respondido em 2026-10-02)*

1. **Dados:** páginas sintéticas fotográficas aprovadas.
2. **Blocos:** `title`, `paragraph`, `margin_note`, `graphic_box`. Listas e tabelas fora.
3. **YOLO / Ultralytics (AGPL):** excluído.
4. **Retificação de perspectiva:** incluída no EXP-002, comparando com e sem, e medindo o custo separadamente.
5. **Baseline clássico:** tratado como hipótese (H4), não como premissa.
6. **Metas de F1, mAP, tempo e memória:** mantidas como critérios de avaliação.

### Perguntas originais (histórico)

1. **Dados reais anotados.** O projeto não tem fotos de caderno anotadas, e fotos suas estão fora (privacidade). Opções:
   - **(a) Recomendada:** páginas sintéticas "fotográficas" — caderno pautado gerado com texto fictício em fonte
     manuscrita (Caveat e, se a licença fechar, outras OFL), títulos, notas de margem e caixas, com degradações
     simuladas (perspectiva, curvatura, sombra, iluminação, desfoque). Verdade de chão exata; mede robustez, mas não
     substitui foto real.
   - **(b) Complementar:** dataset público de páginas manuscritas com anotação de linhas/regiões, se algum tiver
     licença verificada (a pesquisar na Fase 1). O BRESSAY tem páginas e recortes de linha, mas, até onde vi, não
     traz coordenadas — a confirmar.
   - **(c)** Só sintético limpo: valida o harness, mas não responde à robustez.
2. **Tipos de bloco.** Proponho o subconjunto `heading`, `paragraph`, `margin_note` e `graphic` (região de caixa ou
   diagrama, sem o grafo). `list_item` e `table` ficam fora desta rodada. Concorda?
3. **AGPL-3.0 (`ultralytics`).** Excluo candidatos que dependem de bibliotecas AGPL, ou aceita para uso só experimental?
4. **Detecção e retificação da página** (achar as bordas da folha e corrigir a perspectiva antes de segmentar):
   proponho medir como pré-processamento opcional dentro deste experimento, só na camada degradada. Ou prefere um
   experimento separado?

---

## 7. Fora de Escopo

- Reconhecimento do texto (EXP-001 / ADR-001), ordem de leitura (EXP-003), classificação semântica (EXP-004), grafo de diagramas (EXP-005).
- Treino ou ajuste fino de modelos de layout.
- GPU (baseline CPU-only).
- Fotos reais do usuário ou do acervo do Leitorum.
- Integração com o backend; código de produto em `src/leitorum_di/` além de utilitários genéricos (ex.: métricas de detecção).

## 8. Premissas

- Máquina-alvo e limites iguais aos do EXP-001; reaproveitamento do supervisor, do portão de licença e do formato de relatório.
- IoU de caixas já validado no EXP-000; métricas de detecção (casamento, AP) serão novas e testadas com casos calculados à mão.
- Espaço estimado para esta rodada: < 3 GB adicionais (total previsto < 7 GB, abaixo do teto de 20 GB).
