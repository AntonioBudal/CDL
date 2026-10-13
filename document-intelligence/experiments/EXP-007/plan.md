# Plano: EXP-007 — Validação do Layout e da Ordem de Leitura em Imagens Reais

* **Especificação:** [`spec.md`](./spec.md) (`APPROVED` em 2026-10-12)
* **Status:** `DRAFT` — aguardando aprovação do usuário
* **Próximo artefato:** `tasks.md`, só depois da aprovação deste plano

---

## 1. O que já se sabe dos dados (auditoria de estrutura, 2026-10-12)

Feita só sobre nomes de arquivo, campos e contagens; nenhum conteúdo foi lido ou exibido.

### GNHK

* A página oficial de download saiu do ar (redireciona para a página inicial do produto). Os arquivos vieram dos
  links do **Google Drive publicados pelo autor do dataset** no repositório oficial
  (`GoodNotes/GNHK-dataset`, issue 3, comentário de 2022-03-28). Download autorizado pelo usuário. Não houve tela de
  termos; valem os termos do README oficial (CC-BY-4.0).
* `train_data.zip` 724 MB, SHA-256 `a8a841f5…cddda2`; `test_data.zip` 286 MB, SHA-256 `6f3d65d9…81eacb`.
  Em `dataset/raw/exp-007/gnhk/`, fora do Git.
* 687 fotos (515 treino, 172 teste), um JSON por foto. Cada palavra tem `polygon` (quatro cantos), `line_idx`
  inteiro, `type` (`H` manuscrito, `P` impresso) e `text`. **As linhas podem ser formadas** agrupando por
  `line_idx`: 10 184 linhas no total, mediana de 12 por foto.
* Há marcas especiais no campo de texto (`%NA%`, `%SC%`, `%math%`), usadas aqui só como sinal de "região a ignorar".

### BRESSAY

* 1 000 páginas; divisão oficial: 647 treino, 154 validação, **199 teste**.
* **Os recortes são subimagens exatas da página:** em 6 páginas sondadas, todos os recortes de linha e de parágrafo
  foram localizados com correlação 1,000. A verdade de chão de posição é recuperável sem erro.
* **Achado que muda a medição:** as "páginas" são pequenas (cerca de 480 × 530 px, linhas de 17 a 23 px de altura)
  e recortadas rente ao texto. Não são fotos de folha inteira. As páginas sintéticas tinham 1 240 × 1 754 px e
  linhas de cerca de 50 px.
* **Achado que enfraquece H5:** os parágrafos ficam empilhados de cima para baixo, sem regiões laterais. A ordem
  de leitura é quase trivial; um resultado alto diz pouco.

## 2. Decisões de método

| Tema | Decisão | Motivo |
| :--- | :--- | :--- |
| Subconjuntos | **Divisões oficiais de teste**: 172 fotos do GNHK e 199 páginas do BRESSAY, inteiras | Fixas, públicas e reproduzíveis; substituem o sorteio de 150 previsto na spec (FR-002). Treino e validação não são tocados |
| Linhas no GNHK | Uma linha = palavras com o mesmo `line_idx`; contorno = retângulo mínimo que envolve os polígonos das palavras | Regra única, testável com casos fictícios |
| Linhas ignoradas no GNHK | Linhas só com palavras impressas (`P`) ou só com marcas especiais viram regiões "ignorar": detecção sobre elas não conta como acerto nem como erro | Mesmo mecanismo `ignore` dos EXP-002/003 |
| Escala no BRESSAY | Duas condições declaradas antes de medir: **ampliada 3×** (principal; linha com ~55 px, a escala em que o pipeline foi validado e a de uma foto de celular) e **nativa** (secundária) | Sem isso, mediríamos resolução de imagem, não caligrafia. As duas são reportadas; o veredito usa a principal |
| Retificação | GNHK: medido com e sem. BRESSAY: sem (não há folha a endireitar) | As páginas do BRESSAY já são recortes |
| Blocos no BRESSAY | Classe ignorada; ponto de operação do Heron igual ao calibrado no EXP-003 (limiar 0,4; NMS 0,7; contenção 0,6) | Só existe "parágrafo" na verdade de chão; nada é recalibrado |
| Ordem no BRESSAY | Ordenadores `naive` e `anchored` com os parâmetros de `experiments/EXP-003/calibration.json` | Sem recalibrar |
| Critério de acerto | IoU ≥ 0,5 por caixa, como antes; no GNHK também IoU por polígono, porque as linhas são inclinadas | Caixa alinhada aos eixos penaliza linha inclinada (limitação já anotada no EXP-002) |
| Repetições | Uma execução dos detectores, como aprovado no EXP-003 | Custo; os modelos são determinísticos em CPU |

## 3. Estrutura

```text
experiments/EXP-007/
├── spec.md  plan.md  tasks.md  RESULTS.md  failure-analysis.md
├── subsets.json                 listas de arquivos e hashes (sem conteúdo)
├── harness/                     cópia do necessário do EXP-003 (supervisor, worker, adaptadores
│   │                            docufcn/heron/retificador, evaluate, orderers, postprocess, order_eval)
│   ├── gnhk.py                  verdade de chão de linhas a partir das palavras
│   ├── bressay.py               localização dos recortes; linhas, parágrafos e ordem
│   ├── prepare.py               extrai as divisões de teste e grava os manifestos
│   ├── detect.py  run.py  analyze.py
│   └── to_ldf2.py               saída pelo conversor de referência (LDF 2.0)
└── tests/                       só com imagens e anotações fictícias geradas em tmp_path

dataset/raw/exp-007/gnhk/        zips (fora do Git)
dataset/processed/exp-007/       imagens extraídas, manifestos com geometria, layouts detectados (fora do Git)
evaluation/benchmarks/           BENCHMARK-*-exp-007-*.json e ANALYSIS-*.json (só números e identificadores)
```

Ambientes: os do EXP-002, por caminho e com `--frozen` (`harness`, `docufcn`, `heron`). Pesos: os mesmos, com
SHA-256 conferido antes da carga. Nenhuma dependência nova.

O manifesto com geometria fica **fora do Git**: mesmo sem texto, ele é derivado de dados de terceiros. No Git
entram `subsets.json` (nomes e hashes), relatórios numéricos e código.

## 4. Fases

| Fase | Entrega | Verificação |
| :--- | :--- | :--- |
| 1. Preparação | cópia do harness; `prepare.py`; `subsets.json`; registro de licenças | testes do harness copiado passam; EXP-001 a 003 intactos |
| 2. Verdade de chão | `gnhk.py`, `bressay.py`, com testes fictícios | taxa de localização no BRESSAY medida nas 199 páginas; fotos do GNHK sem linha utilizável listadas; SC-001 |
| 3. Detecção | linhas (Doc-UFCN) e blocos (Heron) nos dois conjuntos; retificação no GNHK | relatórios brutos; critérios de parada respeitados |
| 4. Avaliação | F1 de linhas, F1/mAP de blocos, ordem, taxa de retificação; saídas em LDF 2.0 | SC-004: 100 % válidas |
| 5. Análise e fecho | comparação sintético × real, análise de falhas, `RESULTS.md`, ADR | SC-002, SC-003, SC-005, SC-006 |

Estimativa de tempo de máquina, pelos custos medidos no EXP-003 (Doc-UFCN 2,6 s, Heron 1,8 s, contorno 0,2 s por
página): GNHK 172 × (2 × 2,6 + 1,8 + 0,2) ≈ 21 min; BRESSAY 199 × 2 escalas × (2,6 + 1,8) ≈ 29 min. Fotos de
celular são maiores que as páginas sintéticas; o tempo real pode ser maior. Disco: cerca de 1 GB a mais (zips já
baixados) e até 1 GB de imagens extraídas; total previsto abaixo de 10 GB, dentro do teto de 20 GB.

## 5. Riscos

| Risco | Tratamento |
| :--- | :--- |
| Fotos grandes estouram memória ou tempo | Critérios de parada dos experimentos anteriores; se uma foto falhar, é contada como falha, não descartada |
| RAM livre abaixo de 1 GiB | A execução espera (`--wait-free-s`) e, persistindo, para e avisa |
| Verdade de chão de linha do GNHK difere do que o detector chama de linha (por exemplo, linha partida em duas colunas) | Reportar F1 por caixa e por polígono, e analisar os casos na análise de falhas |
| A condição ampliada 3× favorecer ou prejudicar artificialmente | As duas condições são reportadas lado a lado; a escolha da principal está fixada aqui, antes de medir |
| H5 trivial | Declarado; o veredito dirá "atendida, mas pouco informativa" se for o caso |
| Vazamento de conteúdo de terceiros | Relatórios só com números e nomes de arquivo; testes só com dados fictícios; manifesto com geometria fora do Git |

## 6. Conformidade

* **Local-first:** o único acesso à rede foi o download do dataset, já feito.
* **Licenças:** GNHK `VERIFIED` pelo declarado (CC-BY-4.0), com atribuição; BRESSAY `NEEDS VALIDATION`, exceção
  estendida. Relatórios e ADR levam a marca na parte que depende do BRESSAY.
* **Privacidade:** nada do acervo do usuário; conteúdo de terceiros não sai de `dataset/`.
* **Experimentos aceitos:** EXP-001 a 003 só lidos; ambientes com `--frozen`.
* **LDF:** saídas em 2.0 pelo conversor de referência.

## 7. Pontos para sua aprovação

1. **Divisões oficiais de teste** (172 + 199) no lugar do sorteio de 150 + 150.
2. **BRESSAY ampliado 3× como condição principal**, com a nativa reportada ao lado.
3. **H5 fica como está**, sabendo que a ordem no BRESSAY é quase trivial.
