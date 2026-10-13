# Plano: EXP-008 — Detecção de Linhas em Manuscrito Real

* **Especificação:** [`spec.md`](./spec.md) (`APPROVED` em 2026-10-13)
* **Status:** `DRAFT` — aguardando aprovação do usuário
* **Próximo artefato:** `tasks.md`, só depois da aprovação deste plano

---

## 1. Resumo

Comparar, em manuscrito real, quatro detectores de linha, cada um na saída bruta e com um pós-processamento de
fusão de fragmentos calibrado fora do teste. Reaproveita a verdade de chão, o harness e os ambientes do EXP-007.
Um único download novo, pequeno, que depende da sua aprovação (§3).

## 2. Dados

| Papel | Conjunto | Tamanho | Situação |
| :--- | :--- | ---: | :--- |
| Calibração | GNHK, treino oficial — amostra fixa por sorteio com semente | 150 de 515 fotos | zip já no disco, SHA-256 registrado no EXP-007 |
| Calibração | BRESSAY, validação oficial | 154 páginas | zip já no disco |
| Teste | GNHK, teste oficial | 172 fotos | verdade de chão do EXP-007 |
| Teste | BRESSAY, teste oficial, ampliado 3× | 185 páginas | verdade de chão do EXP-007 |

* O BRESSAY é usado só na escala ampliada 3×: o EXP-007 mostrou que a escala não muda o resultado (0,372 e 0,359).
* Sem retificação (ADR-005).
* As listas de arquivos de calibração, com hash, são gravadas e versionadas antes de qualquer medição. Calibração e
  teste vêm de divisões oficiais diferentes; não há página em comum.
* Licenças: GNHK `VERIFIED` (CC-BY-4.0, conforme declarado); BRESSAY `NEEDS VALIDATION`, com a exceção já
  concedida para o EXP-007 — **preciso que você confirme que ela vale também para o EXP-008** (§8).

## 3. Candidatos

Licenças conforme declaradas nas fontes oficiais, consultadas em 2026-10-13; não é parecer jurídico. Cada uma é
conferida de novo na instalação, antes de rodar.

| Id | O que é | Código | Pesos | Situação |
| :--- | :--- | :--- | :--- | :--- |
| `docufcn-norhand` | Doc-UFCN, o detector do ADR-002 | BSD-3-Clause | MIT | já instalado; resultado do EXP-007 é a linha de base |
| `docufcn-historical` | Doc-UFCN `generic-historical-line` | BSD-3-Clause | MIT | pesos já no disco (EXP-002) |
| `classic` | baseline clássico do EXP-002 (OpenCV) | Apache-2.0 | sem pesos | já no harness |
| `ppocr-det` | detector de linhas de texto PP-OCRv5 (mobile), executado pelo pacote `rapidocr` com ONNX Runtime | Apache-2.0 (`rapidocr`); MIT (ONNX Runtime) | Apache-2.0 no card `PaddlePaddle/PP-OCRv5_mobile_det` | **download novo**: wheel de cerca de 27 MB com os modelos, mais o ONNX Runtime |

Sobre o `ppocr-det`:

* É o único candidato novo que encontrei com código e pesos de licença permissiva declarada e instalação por wheel.
* O wheel traz um arquivo `MODEL_LICENSES.md`; ele é lido na instalação. Se contradisser o card, o candidato fica
  `NEEDS VALIDATION` e eu paro para perguntar.
* Se o ONNX Runtime não tiver wheel para o Python 3.14, o ambiente desse candidato usa outra versão do Python
  gerenciada pelo `uv` dentro da pasta, como já foi feito para o PyLaia.
* Só a etapa de detecção é usada. O reconhecimento de texto do pacote não é chamado.

Não entram:

| Candidato | Motivo |
| :--- | :--- |
| Kraken | sem wheels no Windows (EXP-002) |
| docTR | pesos sem licença declarada (EXP-002) |
| Qualquer coisa com `ultralytics` | AGPL, excluída por decisão sua |
| Surya | código GPL e pesos com restrição de uso comercial |
| Florence-2 (Microsoft, MIT) | exige executar código baixado junto com o modelo e é pesado para CPU; fica de fora, a menos que você peça (§8) |

## 4. Método

### Fusão de fragmentos

Dois fragmentos são unidos quando estão na mesma faixa vertical e próximos na horizontal:

* sobreposição vertical mínima, como fração da altura do menor;
* distância horizontal máxima, em alturas medianas de linha da página;
* diferença máxima de inclinação.

A fusão é transitiva (componentes conexos). Os três parâmetros são escolhidos por busca em grade, **só nos
conjuntos de calibração**, por candidato, maximizando o F1 médio dos dois conjuntos. A grade e o resultado ficam
num arquivo versionado. Cada candidato é reportado bruto e fundido.

Além disso, só para os Doc-UFCN: o tamanho mínimo de componente (`min_cc`) entra na mesma busca.

### Medidas

* **Principal:** F1 de linhas com IoU ≥ 0,5 por caixa, como no EXP-002 e no EXP-007.
* **Complementar (H5):** cobertura — fração da área de cada linha verdadeira coberta por detecções atribuídas a
  ela, e fração da área detectada que cai fora de qualquer linha verdadeira ou região ignorada.
* **Diagnóstico:** as quatro classes de erro do EXP-007 (partida, desalinhada, fundida, não vista) e o teto de
  fusão ideal, para cada candidato.
* **Custo:** tempo por página e pico de memória, pelo supervisor.

### Ordem das medições

1. Recalcular os números do EXP-007 a partir do layout já detectado (mesmo arquivo, mesmo avaliador). Se não
   baterem, a execução para.
2. Rodar cada candidato na calibração; calibrar a fusão.
3. Rodar cada candidato no teste, uma vez, com os parâmetros já fixados. O `docufcn-norhand` reutiliza no teste as
   detecções do EXP-007.

## 5. Estrutura

```text
experiments/EXP-008/
├── spec.md  plan.md  tasks.md  RESULTS.md  failure-analysis.md
├── candidates.json              candidatos, licenças, pesos e hashes
├── subsets.json                 listas de calibração (nomes e hashes)
├── calibration.json             grade e parâmetros escolhidos, por candidato
├── envs/ppocr/                  ambiente isolado do candidato novo
├── harness/                     cópia do necessário do EXP-007, mais:
│   ├── merge.py                 fusão de fragmentos
│   ├── coverage.py              medida por cobertura
│   ├── adapters/ppocr.py  adapters/classic.py (cópia do EXP-002)
│   └── prepare.py  detect.py  calibrate.py  run.py  analyze.py
└── tests/                       só com dados fictícios
```

Dados fora do Git em `dataset/processed/exp-008/`. A verdade de chão de teste é lida de
`dataset/processed/exp-007/` (não é diretório de experimento; não é modificada).

## 6. Fases e custo

| Fase | Entrega | Tempo de máquina estimado |
| :--- | :--- | ---: |
| 1. Preparação | cópia do harness, conjuntos de calibração, reprodução do EXP-007 | 5 min |
| 2. Método | `merge.py`, `coverage.py`, testes | — |
| 3. Candidato novo | auditoria de licença na instalação, ambiente, adaptador, ensaio | 5 min |
| 4. Calibração | 4 candidatos em 304 páginas; busca em grade | 35 min |
| 5. Teste | 3 candidatos em 357 páginas (o quarto reutiliza o EXP-007) | 25 min |
| 6. Análise e fecho | comparação, análise de falhas, `RESULTS.md`, ADR-006 | — |

Estimativa pelos custos medidos: Doc-UFCN cerca de 3 s por página; clássico e `ppocr-det` abaixo de 1 s (a
confirmar). Total em torno de uma hora de máquina. Disco: menos de 1 GB a mais (imagens de calibração e o ambiente
novo); total previsto perto de 11 GB, dentro do teto de 20 GB.

**Memória:** as fases 4 e 5 carregam modelos e precisam de 1 GiB de RAM livre, como no EXP-007. Vale deixar o
Firefox fechado quando aprovar as tarefas.

## 7. Riscos

| Risco | Tratamento |
| :--- | :--- |
| A fusão calibrada no GNHK e no BRESSAY não generalizar para caderno | Declarado como limitação; os dois conjuntos são reportados separados, e a grade mostra a sensibilidade aos parâmetros |
| O `ppocr-det` detectar palavras, e não linhas | A mesma fusão se aplica; o resultado bruto e o fundido são reportados |
| `MODEL_LICENSES.md` contradizer o card | Paro e pergunto antes de rodar |
| ONNX Runtime sem wheel compatível | Outra versão do Python no ambiente do candidato; se ainda assim não instalar, o candidato é registrado como excluído |
| Nenhum candidato atingir as metas | É um resultado válido: o ADR dirá que não há detector pronto e recomendará o caminho (ajuste de pesos ou dados próprios) |
| Vazamento de conteúdo de terceiros | Mesmas regras do EXP-007: só números e nomes de arquivo saem de `dataset/` |

## 8. Pontos para sua aprovação

1. **Download do candidato `ppocr-det`** (`rapidocr`, cerca de 27 MB, mais o ONNX Runtime), em ambiente isolado
   dentro da pasta.
2. **Exceção do BRESSAY** estendida ao EXP-008, nas mesmas condições.
3. **Florence-2 fica de fora**, como proposto? Se quiser incluí-lo, entra como candidato extra, com download de
   cerca de 0,5 GB e execução de código do repositório do modelo em revisão fixada.
