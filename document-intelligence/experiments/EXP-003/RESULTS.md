# EXP-003: Relatório de Resultados — Reconstrução Espacial e Ordem de Leitura

* **Status:** `AWAITING USER ACCEPTANCE`
* **Execução:** 2026-10-07
* **Executor:** Claude Code
* **Decisão arquitetural gerada:** [ADR-003](../../docs/adr/ADR-003-ordem-de-leitura-por-ancoragem.md) (`PROPOSED`)
* **Artefatos do ciclo:** [spec.md](./spec.md) · [plan.md](./plan.md) · [tasks.md](./tasks.md)

> **Licenças.** Os ordenadores são algoritmos próprios, sem pesos. O layout detectado usa os componentes do ADR-002,
> todos `LICENSE STATUS: VERIFIED` (Doc-UFCN: BSD-3-Clause / MIT; Docling Heron: Apache-2.0; OpenCV: Apache-2.0),
> com os mesmos pesos e SHA-256 do EXP-002. Nenhum download foi feito neste experimento.

---

## 1. Resposta à pergunta do experimento

**Pergunta:** dadas as linhas e os blocos de uma página, um método barato e sem modelo os coloca na ordem de
leitura? E quanto se perde quando a entrada vem dos detectores do EXP-002?

**Resposta:** com as posições exatas, **sim** — o ordenador por ancoragem acerta 98,3 % da ordem e custa 2 ms por
página. Com o layout detectado, **não**: a acurácia de ponta a ponta cai para 77 %, e quase toda a perda vem da
detecção de blocos (blocos faltando e sobrando), não do método de ordenação.

| Hipótese | Veredito | Evidência |
| :--- | :--- | :--- |
| H1 — layout verdadeiro: acurácia de blocos ≥ 0,95 em todas as famílias | **Confirmada** para `anchored` | 0,983 no geral; 1,000 / 0,981 / 0,971 (`single` / `margin` / `callout`) |
| H2 — layout detectado: ≥ 0,85 | **Refutada** | melhor resultado 0,777; restrito aos blocos casados, 0,950–0,953 |
| H3 — a ordenação ingênua basta em coluna única, mas falha com regiões laterais | **Confirmada em parte** | `naive`: 1,000 em `single`, 0,965 em `margin` (passa), 0,898 em `callout` (falha) |
| H4 — ≤ 50 ms por página, sem modelo | **Confirmada** | mediana de 1,4–6,8 ms; pico de alocação de 11 MB |

---

## 2. Resultados

Conjunto `test`: 180 páginas sintéticas (3 famílias × 3 níveis × 20), 1.785 blocos, 3.783 linhas. Parâmetros
calibrados só no `dev` (30 páginas). Árvore limpa em todas as medições.

### 2.1 Layout verdadeiro (isola o método de ordenação)

| Ordenador | Blocos | `single` | `margin` | `callout` | Linhas | Páginas perfeitas | ms/página |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `anchored` | **0,983** | 1,000 | 0,981 | 0,971 | 0,991 | 93 % | 2,2 |
| `anchored+deskew` | 0,981 | 1,000 | 0,987 | 0,957 | 0,989 | 92 % | 4,2 |
| `naive` | 0,954 | 1,000 | 0,965 | 0,898 | 0,964 | 82 % | 1,4 |
| `naive+deskew` | 0,949 | 1,000 | 0,953 | 0,896 | 0,961 | 79 % | 4,0 |
| `xycut` | 0,816 | 1,000 | 0,602 | 0,903 | 0,917 | 52 % | 1,6 |
| `xycut+deskew` | 0,816 | 1,000 | 0,599 | 0,907 | 0,917 | 52 % | 4,0 |

Por nível de degradação (`anchored`): 0,990 limpo, 0,993 leve, 0,966 forte.

* O **corte XY** falha justamente no caso típico de caderno: lê a nota de margem (à esquerda) antes do parágrafo
  que ela comenta (169 parágrafos fora de ordem na família `margin`).
* A **ordenação ingênua** funciona melhor do que o previsto com notas de margem, porque a nota começa um pouco
  abaixo do topo do parágrafo; falha quando o destaque lateral começa na mesma altura do parágrafo.
* **Endireitar as caixas** pelo ângulo das linhas não ajudou: os métodos já toleram a inclinação testada.

### 2.2 Layout detectado (ADR-002: contorno → Doc-UFCN `norhand` + Heron)

Ponto de operação dos blocos calibrado no `dev`: confiança ≥ 0,4, NMS com IoU 0,7, contenção 0,6.

| Ordenador | Blocos (ponta a ponta) | Só blocos casados | `single` | `margin` | `callout` | Linhas | Páginas perfeitas |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `naive` | **0,777** | 0,953 | 0,874 | 0,714 | 0,762 | 0,703 | 30 % |
| `anchored` | 0,773 | 0,950 | 0,870 | 0,707 | 0,760 | 0,703 | 32 % |
| `xycut+deskew` | 0,717 | 0,873 | 0,874 | 0,562 | 0,754 | 0,703 | 25 % |
| `xycut` | 0,698 | 0,847 | 0,874 | 0,518 | 0,744 | 0,701 | 25 % |

Dos 1.785 blocos verdadeiros, **203 (11 %) ficaram sem par** e o detector devolveu **188 blocos a mais**.

### 2.3 Decomposição da perda (`anchored`)

| Etapa | Acurácia de blocos | Perda |
| :--- | ---: | ---: |
| Layout verdadeiro | 0,983 | — |
| Layout detectado, só blocos casados | 0,950 | −0,033 (ordenação com geometria imprecisa) |
| Layout detectado, sequência completa | 0,773 | −0,178 (blocos faltando ou sobrando) |

**84 % da perda vem da detecção de blocos**, não da ordenação. Com o layout detectado, `naive` e `anchored` ficam
empatados: a vantagem do `anchored` (regiões laterais) desaparece porque as notas de margem são justamente os
blocos que o Heron mais erra (AP de 0,53 no EXP-002).

### 2.4 Linhas dentro do bloco e efeito da retificação

| Fonte das linhas | Acurácia de ordem de linhas | Limpo | Leve | Forte | Só linhas casadas |
| :--- | ---: | ---: | ---: | ---: | ---: |
| Verdadeiras (`anchored`) | 0,991 | 0,995 | 0,997 | 0,982 | — |
| Detectadas, com retificação por contorno | 0,703 | 0,773 | 0,743 | 0,603 | 0,946 |
| Detectadas, sem retificação | 0,690 | 0,768 | 0,720 | 0,590 | 0,946 |

A retificação melhora a ordem das linhas em 1,3 ponto no geral (2,3 no nível leve). Aqui também a perda está na
detecção (linhas fundidas, perdidas ou atribuídas ao bloco errado); entre as linhas casadas a ordem acerta 94,6 %.

### 2.5 Ponto de operação do Heron

Com o limiar de 0,3 usado no EXP-002 (adequado para calcular AP), o Heron devolveu 3.561 blocos para 1.785
verdadeiros e a acurácia de ponta a ponta ficou em 0,46. Calibrar limiar e supressão de duplicatas no `dev`
elevou-a para 0,77. O relatório com os blocos brutos foi mantido
(`BENCHMARK-20261007-exp-003-order-detected-rectified-raw-blocks.json`).

### 2.6 Onde a ordem se perde (layout detectado, `anchored`)

Blocos verdadeiros fora de ordem ou ausentes, por família: `margin` — 74 notas de margem e 60 parágrafos;
`callout` — 21 caixas de destaque, 17 parágrafos, 11 notas, 11 caixas gráficas; `single` — 21 parágrafos,
7 caixas gráficas, 3 títulos.

---

## 3. Critérios de sucesso da spec

| Critério | Situação |
| :--- | :--- |
| SC-001 — verdade de chão de ordem e métricas testadas | Atendido |
| SC-002 — acurácia por método, família e fonte do layout, com veredito de H1–H4 | Atendido |
| SC-003 — decomposição da perda entre ordenação e detecção | Atendido (§2.3) |
| SC-004 — saídas válidas no LDF (`reading_order`) | Atendido: 180/180 válidas em todas as medições |
| SC-005 — ADR | Atendido: ADR-003 `PROPOSED` |
| SC-006 — escopo, testes, `ruff`, disco | Atendido (§6) |

---

## 4. Desvios em relação ao plano

| Planejado | O que ocorreu |
| :--- | :--- |
| Módulo comum `experiments/common/` | Recusado pelo usuário: o harness do EXP-002 foi copiado para dentro do EXP-003 |
| Três ordenadores | Medidos seis: cada método com e sem endireitamento das caixas |
| Blocos do Heron direto na ordenação | Foi preciso calibrar um ponto de operação (limiar + NMS) no `dev`; exigiu rodar a detecção também no `dev` |
| Três execuções dos detectores | Uma, como aprovado; os ordenadores foram medidos em 3 repetições |
| Parada a cada checkpoint | Execução contínua, por instrução do usuário em 2026-10-07 |
| Análise por inclinação da folha (T019) | Substituída pela análise por nível de degradação e por tipo de bloco fora de ordem |

---

## 5. Limitações

* **Páginas sintéticas com ordem "bem-comportada".** A nota de margem sempre começa na primeira linha do parágrafo
  que comenta, e o destaque lateral fica alinhado ao seu parágrafo. Em cadernos reais as notas aparecem em qualquer
  altura, com setas e chaves; a regra de ancoragem não foi testada nesses casos.
* **Sem duas colunas** nem textos em sentidos diferentes na mesma página (fora do escopo aprovado).
* **O ordenador `anchored` conhece o gerador** em parte (limiares calibrados no `dev` do mesmo gerador).
* **Lacuna do LDF:** `reading_order` só aceita blocos; as caixas gráficas (102 no layout verdadeiro, 140 no
  detectado) ficam fora da ordem serializada, embora tenham sido avaliadas.
* **Blocos sem retificação:** o Heron rodou na imagem original; não foi medido se retificar antes melhora os blocos.
* A decomposição usa casamento por IoU ≥ 0,5 sem olhar o tipo; um bloco detectado com o tipo errado conta como casado.

---

## 6. Manifesto de reprodutibilidade (Princípio 3)

| Item | Valor |
| :--- | :--- |
| Hardware / SO | i5-8265U, 7,9 GB RAM, Windows 11 Pro, CPU-only — [`../EXP-000/environment.md`](../EXP-000/environment.md) |
| Ambientes | os do EXP-002, reutilizados por caminho: `envs/harness` (Python 3.14.3), `envs/docufcn` (3.10.20, `torch` 2.1.0), `envs/heron` (3.14.3, `transformers` 5.18.0) |
| Pesos | `docufcn-norhand-line` e `heron`, revisões e SHA-256 em `experiments/EXP-002/candidates.json`, conferidos antes da carga |
| Dados | manifestos em `dataset/fixtures/exp-003/` (seeds 40000+ no `dev`, 50000+ no `test`); imagens regeneráveis com `harness/generate.py`; fontes OFL do EXP-002 |
| Calibração | [`calibration.json`](./calibration.json): ordenadores sobre o layout verdadeiro do `dev`; ponto de operação dos blocos sobre o layout detectado do `dev` |
| Commits das medições | layout verdadeiro: `e98c722`; layout detectado: `5f8418c`; árvore limpa em ambas |
| Detecção (uma execução) | contorno 178 ms e 64 MiB; Doc-UFCN 2,6 s e 649–807 MiB; Heron 1,8 s e 764 MiB por página |
| Parâmetros | seed 1234; tempo dos ordenadores pela mediana de 3 execuções por página |
| Relatórios | `evaluation/benchmarks/BENCHMARK-20261007-exp-003-*.json` e `ANALYSIS-20261007-exp-003-reading-order.json` |

Para reproduzir (a partir de `document-intelligence/`):

```powershell
uv run --project experiments/EXP-002/envs/harness python experiments/EXP-003/harness/run.py --out evaluation/benchmarks/ordem-layout-verdadeiro.json
```

**Verificação final (2026-10-07):** `uv run pytest` — 38 passed; testes do harness do EXP-003 — 46 passed;
`uv run ruff check .` — limpo; EXP-001 e EXP-002 intocados; nada fora de `document-intelligence/`; páginas e layouts
detectados fora do Git; uso de disco de 8,2 GB (teto de 20 GB).

---

## 7. Conformidade com a Constituição

* [x] **Princípio 1 (Local-first):** tudo local; nenhuma rede usada.
* [x] **Princípio 2 (Evidência antes de decisão):** calibração só no `dev`; ADR baseado nas medições.
* [x] **Princípio 3 (Reprodutibilidade):** §6.
* [x] **Princípio 4 (Reconhecimento × interpretação):** a ordem vem só da geometria; nenhum texto foi lido.
* [x] **Princípio 6 (Medir antes de otimizar):** Python puro e NumPy; custo de milissegundos.
* [x] **Princípio 7 (Experimentos antes de features):** em `src/` entraram só métricas genéricas de ordem.
* [x] **Princípio 8 (LDF como contrato soberano):** saídas validadas; lacuna registrada; contrato intocado.

---

## 8. Homologação

- [x] Entregáveis do EXP-003 concluídos e submetidos ao usuário.
- [ ] EXP-003 **ACEITO** — decisão do usuário.
- [ ] ADR-003 aceito, rejeitado ou ajustado — decisão do usuário.
- [ ] Próximo passo — decisão do usuário. **EXP-004 não iniciado.**

*Assinatura do agente executor:* `Claude Code (claude-opus-5-5), 2026-10-07`
