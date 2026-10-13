# EXP-007: Relatório de Resultados — Validação do Layout e da Ordem de Leitura em Imagens Reais

* **Status:** `ACCEPTED` / `CONCLUÍDO` (aceito pelo usuário em 2026-10-13)
* **Execução:** 2026-10-12 e 2026-10-13
* **Executor:** Claude Code
* **Decisão arquitetural gerada:** [ADR-005](../../docs/adr/ADR-005-layout-nao-confirmado-em-imagens-reais.md) (`ACCEPTED`)
* **Artefatos do ciclo:** [spec.md](./spec.md) · [plan.md](./plan.md) · [tasks.md](./tasks.md) · [failure-analysis.md](./failure-analysis.md)

> **Licenças.** Pipeline: Doc-UFCN (BSD-3-Clause / MIT), Docling Heron (Apache-2.0) e OpenCV (Apache-2.0), todos
> `LICENSE STATUS: VERIFIED`, com os mesmos pesos e SHA-256 do EXP-002. Dados: **GNHK**, CC-BY-4.0 conforme
> declarado no repositório oficial — `LICENSE STATUS: VERIFIED` (Lee, Chung e Lee, *GNHK: A Dataset for English
> Handwriting in the Wild*, ICDAR 2021). **BRESSAY**: `LICENSE STATUS: NEEDS VALIDATION` — uso experimental local
> autorizado pelo usuário em 2026-10-12; **os resultados que dependem dele não podem embasar decisão de produto**.

---

## 1. Resposta à pergunta do experimento

**Pergunta:** o que os EXP-002 e EXP-003 mediram em páginas sintéticas se mantém em imagens reais?

**Resposta: não.** A detecção de linhas cai de 0,78–0,93 para **0,35–0,37**, tanto em fotos de celular quanto em
caligrafia portuguesa. A retificação por contorno **piora** o resultado. O detector de blocos devolve o texto como
um bloco único. As páginas sintéticas superestimaram o pipeline, e a direção do ADR-002 não está confirmada.

O que se manteve: o custo, a robustez de execução, o método de ordenação e o formato LDF 2.0.

| Hipótese | Veredito | Evidência |
| :--- | :--- | :--- |
| H1 — linhas em foto real: F1 a no máximo 0,10 do sintético | **Refutada** | GNHK: 0,345 sem retificação (meta 0,684); 0,239 com (meta 0,745) |
| H2 — a retificação acha a folha em ≥ 70 % das fotos e não piora | **Refutada** | devolve um quadrilátero em 100 % das fotos, mas o F1 cai de 0,345 para 0,239 |
| H3 — linhas em caligrafia portuguesa: F1 a no máximo 0,05 do sintético limpo | **Refutada** | BRESSAY: 0,372 ampliado 3×, 0,359 nativo (meta 0,878) |
| H4 — parágrafos detectados com F1 ≥ 0,70 | **Refutada**, com ressalva | F1 0,354; 99 % dos parágrafos perdidos estão dentro de um bloco detectado maior (granularidade, não localização) |
| H5 — ordem ≥ 0,90 com parágrafos verdadeiros e ≥ 0,75 com detectados | **Refutada** | 1,000 com os verdadeiros (trivial nestes dados); 0,239 com os detectados |
| H6 — custo na mesma faixa dos experimentos anteriores | **Confirmada** | 5,0 s (GNHK) e 5,5 s (BRESSAY) por página, contra 4,6 s no sintético; pico de 1,31 GiB |

---

## 2. Resultados

Benchmark: [`BENCHMARK-20261013-exp-007-real-images.json`](../../evaluation/benchmarks/BENCHMARK-20261013-exp-007-real-images.json),
commit `8bf4e5f`, árvore limpa. Pipeline, pesos e parâmetros idênticos aos dos ADR-002 e ADR-003; nada foi
ajustado nestes dados. Divisões oficiais de teste.

### 2.1 Verdade de chão

| Conjunto | Origem | Utilizável | Linhas | Blocos | Observação |
| :--- | :--- | ---: | ---: | ---: | :--- |
| GNHK | 172 fotos de celular (teste oficial) | 172 | 2.189 | — | 250 regiões ignoradas (linhas só impressas ou ilegíveis); linhas formadas a partir de 10.066 palavras |
| BRESSAY | 199 páginas (teste oficial) | 185 | 5.496 | 771 | 99,7 % dos 6.750 recortes localizados com correlação ≥ 0,99; 14 páginas com recorte não localizado ficaram fora |

### 2.2 Linhas (Doc-UFCN `norhand`, IoU ≥ 0,5 por caixa)

| Conjunto | Precisão | Revocação | **F1** | Previstas / verdadeiras | Sintético de referência |
| :--- | ---: | ---: | ---: | ---: | :--- |
| GNHK, foto original | 0,260 | 0,512 | **0,345** | 4.309 / 2.189 | 0,784 (degradação forte) |
| GNHK, retificada | 0,171 | 0,394 | **0,239** | 5.042 / 2.189 | 0,845 (degradação forte) |
| BRESSAY ampliado 3× (principal) | 0,300 | 0,488 | **0,372** | 8.934 / 5.496 | 0,928 (limpa) |
| BRESSAY nativo | 0,287 | 0,478 | **0,359** | 9.146 / 5.496 | 0,928 (limpa) |

O detector encontra o texto (só 3 % a 7 % das falhas são linhas não vistas), mas o parte em fragmentos: 1,5 caixa
por linha verdadeira. Uma fusão ideal dos fragmentos levaria o F1 a 0,54 (GNHK) e 0,71 (BRESSAY), ainda abaixo do
sintético. Detalhes em [failure-analysis.md](./failure-analysis.md) §1.

### 2.3 Retificação por contorno (GNHK)

Devolveu quadrilátero em 172 de 172 fotos. O F1 de linhas cai em todas as faixas, e mais onde o recorte é maior:
0,294 → 0,280 quando o quadrilátero ocupa ≥ 90 % da foto; 0,382 → 0,159 quando ocupa menos de 60 %.

### 2.4 Blocos (Heron, sem olhar a classe; BRESSAY)

| Conjunto | AP50 | Precisão | Revocação | **F1** | Detectados / verdadeiros |
| :--- | ---: | ---: | ---: | ---: | ---: |
| Ampliado 3× | 0,334 | 0,530 | 0,266 | **0,354** | 387 / 771 |
| Nativo | 0,325 | 0,527 | 0,257 | **0,345** | 376 / 771 |

Ponto de operação do EXP-003 (confiança ≥ 0,4; NMS 0,7; contenção 0,6). Em 109 de 185 páginas o detector devolveu
um bloco só para o texto inteiro.

### 2.5 Ordem de leitura (BRESSAY ampliado 3×)

| Ordenador | Parágrafos verdadeiros | Blocos detectados | Só blocos casados | ms/página |
| :--- | ---: | ---: | ---: | ---: |
| `anchored` | 1,000 | 0,239 | 1,000 | 0,4 |
| `naive` | 1,000 | 0,244 | 1,000 | 0,3 |

### 2.6 Custo (mediana por página, CPU)

| Etapa | GNHK | BRESSAY 3× | BRESSAY nativo | Sintético (EXP-003) | Pico de memória |
| :--- | ---: | ---: | ---: | ---: | ---: |
| Retificação | 0,17 s | — | — | 0,18 s | 63 MiB |
| Doc-UFCN | 2,9–3,0 s | 3,6 s | 3,5 s | 2,6 s | 842–901 MiB |
| Heron | 1,8 s | 1,9 s | 2,1 s | 1,8 s | 760–1.345 MiB |

Continua acima da meta de 2 s por página do EXP-002, como já se sabia.

### 2.7 Saída em LDF 2.0

| Conjunto | Documentos | Válidos | Linhas | Regiões | Não representáveis |
| :--- | ---: | ---: | ---: | ---: | ---: |
| GNHK | 172 | 172 | 5.241 | 978 | 0 |
| BRESSAY 3× | 185 | 185 | 8.934 | 387 | 0 |
| BRESSAY nativo | 185 | 185 | 9.146 | 376 | 0 |

---

## 3. Critérios de sucesso

| Critério | Resultado |
| :--- | :--- |
| SC-001 — verdade de chão em ≥ 100 fotos e ≥ 100 páginas | Atendido: 172 e 185 |
| SC-002 — veredito de H1 a H6 com a referência sintética | Atendido (§1) |
| SC-003 — análise de falhas por etapa | Atendido: [failure-analysis.md](./failure-analysis.md) |
| SC-004 — 100 % das saídas válidas em LDF 2.0 | Atendido: 542 de 542 |
| SC-005 — nenhum conteúdo no Git; nada fora da pasta; disco no teto | Atendido (§6) |
| SC-006 — ADR | Atendido: ADR-005 `ACCEPTED` |

---

## 4. Desvios em relação ao plano

| Planejado | O que ocorreu |
| :--- | :--- |
| Download do GNHK pelo usuário, com aceite de termos | A página oficial saiu do ar; baixado pelo agente, com autorização do usuário, pelos links do Google Drive publicados pelo autor no repositório oficial. Não houve tela de termos |
| Sorteio de 150 fotos e 150 páginas | Divisões oficiais de teste inteiras (172 e 199), aprovado no plano |
| Fotos do GNHK no tamanho original | Lado maior limitado a 2.048 px (a escala em que o pipeline foi validado), com a anotação escalada junto; mediana original de 9,6 MP. Decidido antes de qualquer medição |
| Imagens copiadas como estão | 35 fotos tinham rotação nos metadados e a anotação segue a imagem girada; a rotação foi aplicada e as imagens de trabalho regravadas em JPEG de qualidade 95, sem metadados |
| Falha de uma página derruba a execução (comportamento herdado) | A falha passa a ser contada na página; não ocorreu nenhuma |
| Avaliador copiado sem mudanças | Acrescentado um atalho no IoU por polígono (envelopes disjuntos dão zero sem rasterizar); o resultado é o mesmo, a avaliação ficou viável em tempo |
| Detecção logo após a aprovação | Bloqueada por cerca de 8 horas: RAM livre abaixo de 1 GiB. O limite não foi relaxado; a execução retomou quando o usuário liberou memória |
| Tempos medidos sem interferência | Um script de conferência meu rodou ao mesmo tempo que a detecção do BRESSAY nativo e o início do GNHK (retificação e começo do Doc-UFCN retificado). Os tempos dessas execuções podem estar um pouco inflados; as métricas de acerto não são afetadas |
| Análise por região de origem e por condição | Feita por região (prefixo do nome do arquivo) e por faixa de área do quadrilátero; acrescentados o teto de fusão de fragmentos e a absorção de blocos |

---

## 5. Limitações

* **Nenhum dos dois conjuntos é o caso de uso.** O GNHK é em inglês e não é caderno de estudo; o BRESSAY é em
  português, mas são recortes de redação, não fotos de celular. Página de caderno brasileiro fotografada continua
  sem medição.
* **Ordem de leitura com notas de margem em imagem real não foi medida** (sem verdade de chão).
* **A verdade de chão de linha do GNHK é derivada**; texto não anotado numa foto vira detecção errada. O BRESSAY,
  com verdade de chão exata, dá o mesmo resultado, o que sustenta a conclusão.
* **O critério de IoU ≥ 0,5 com a linha inteira pune fragmentos.** Não há reconhecedor de texto para medir se
  fragmentos seriam aproveitáveis.
* **Tipos de bloco não foram avaliados** (só existe "parágrafo" na verdade de chão do BRESSAY).
* **Uma execução** de cada detector.
* **Lacuna do LDF 2.0 encontrada:** cada etapa aceita um único componente, e o layout usa dois modelos (linhas e
  blocos). Foram descritos num componente composto. Cabe numa versão 2.1; não foi alterado aqui.

---

## 6. Manifesto de reprodutibilidade (Princípio 3)

| Item | Valor |
| :--- | :--- |
| Hardware / SO | i5-8265U, 7,9 GB RAM, Windows 11 Pro, CPU-only — [`../EXP-000/environment.md`](../EXP-000/environment.md) |
| Ambientes | os do EXP-002, por caminho e com `--frozen`: `envs/harness`, `envs/docufcn`, `envs/heron` |
| Pesos e parâmetros | [`candidates.json`](./candidates.json): entradas e SHA-256 copiados do EXP-002; filtro de blocos e ordenadores do EXP-003 |
| GNHK | `test_data.zip`, SHA-256 `6f3d65d91535d1665050afd83a9f3831394d80accfae88c5b91bbb990781eacb`; `train_data.zip` (não usado), SHA-256 `a8a841f504761a7df91c5104cff1d85d534dd5834af99c2d68baecb7c6cddda2` |
| BRESSAY | `dataset/raw/exp-001/bressay.zip`, DOI 10.5281/zenodo.11637681, lista `bressay/sets/test.txt` |
| Arquivos usados | [`subsets.json`](./subsets.json): nome e SHA-256 de cada arquivo de origem |
| Commit da medição | `8bf4e5f`, árvore limpa |
| Parâmetros | seed 1234; uma execução por detector; ordenadores pela mediana de 3 execuções |
| Relatórios | `evaluation/benchmarks/BENCHMARK-20261013-exp-007-real-images.json`, `ANALYSIS-20261013-exp-007-real-images.json`, `ANALYSIS-20261012-exp-007-ground-truth.json` |

Para reproduzir (a partir de `document-intelligence/`, com os zips nos caminhos acima):

```powershell
$h = "experiments/EXP-002/envs/harness"
uv run --frozen --project $h python experiments/EXP-007/harness/prepare.py --report evaluation/benchmarks/gt.json
uv run --frozen --project $h python experiments/EXP-007/harness/detect.py --set bressay-x3
uv run --frozen --project $h python experiments/EXP-007/harness/detect.py --set bressay-native
uv run --frozen --project $h python experiments/EXP-007/harness/detect.py --set gnhk
uv run --frozen --project $h python experiments/EXP-007/harness/run.py --out evaluation/benchmarks/bench.json
uv run --frozen --project $h python experiments/EXP-007/harness/analyze.py --benchmark evaluation/benchmarks/bench.json --out evaluation/benchmarks/analysis.json
```

**Verificação final (2026-10-13):** `uv run pytest` — 239 passed; testes do harness do EXP-007 — 55 passed; `uv run ruff check .` — limpo; EXP-001 a EXP-003 intactos (teste de congelamento); nada fora de `document-intelligence/`; nenhuma imagem ou arquivo dos datasets rastreado pelo Git; `dataset/` com 5,8 GB (2,8 GB a mais que antes do experimento: 1,0 GB do GNHK e 1,8 GB de imagens de trabalho), total da pasta em torno de 10 GB, dentro do teto de 20 GB.

---

## 7. Conformidade com a Constituição

* [x] **Local-first:** o único acesso à rede foi o download do GNHK, autorizado pelo usuário.
* [x] **Evidência antes de decisão:** nada foi calibrado nestes dados; o ADR-005 decorre das medições.
* [x] **Reprodutibilidade:** §6.
* [x] **Privacidade:** nada do acervo do usuário; nenhuma imagem, recorte ou transcrição de terceiros no Git, em
  relatório ou no chat; o texto das transcrições não foi usado.
* [x] **Sem modelos prematuros:** nenhum modelo, peso ou dependência nova.
* [x] **Experimentos aceitos intactos:** EXP-001 a EXP-003 só lidos; ambientes com `--frozen`.
* [x] **LDF como contrato:** 542 saídas válidas em LDF 2.0; lacuna registrada, contrato intocado.

---

## 8. Homologação

- [x] Entregáveis do EXP-007 concluídos e submetidos ao usuário.
- [x] EXP-007 **ACEITO** pelo usuário em 2026-10-13.
- [x] ADR-005 **aceito** pelo usuário em 2026-10-13.
- [x] Próximo passo: EXP-008 (detecção de linhas em manuscrito real), escolhido pelo usuário. **EXP-004 não iniciado.**

*Assinatura do agente executor:* `Claude Code (claude-opus-5-5), 2026-10-13`
