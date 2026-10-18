# EXP-008: Relatório de Resultados — Detecção de Linhas em Manuscrito Real

* **Status:** `ACCEPTED` / `CONCLUÍDO` (aceito por delegação do usuário em 2026-10-18)
* **Execução:** 2026-10-13 e 2026-10-14, com as decisões delegadas pelo usuário ao aprovar o plano
* **Executor:** Claude Code
* **Decisão arquitetural gerada:** [ADR-006](../../docs/adr/ADR-006-deteccao-de-linhas-pp-ocr.md) (`ACCEPTED`)
* **Artefatos do ciclo:** [spec.md](./spec.md) · [plan.md](./plan.md) · [tasks.md](./tasks.md)

> **Licenças.** Candidatos: Doc-UFCN (BSD-3-Clause / MIT), clássico (OpenCV, Apache-2.0) e **PP-OCRv6 small det**
> via `rapidocr` 3.10.0 (código Apache-2.0; pesos Apache-2.0 conforme o `MODEL_LICENSES.md` do wheel e o card
> oficial `PaddlePaddle/PP-OCRv6_small_det_onnx`; ONNX Runtime, MIT) — todos `LICENSE STATUS: VERIFIED`, conforme
> declarado; não é parecer jurídico. Dados: GNHK, CC-BY-4.0 — `VERIFIED`; BRESSAY — `LICENSE STATUS: NEEDS
> VALIDATION`, exceção experimental estendida ao EXP-008 por delegação do usuário; **não embasa produto**.

---

## 1. Resposta à pergunta do experimento

**Pergunta:** existe um detector de linhas local, com licença verificada, que funcione em manuscrito real?

**Resposta: sim.** O detector de texto do PP-OCRv6 (via `rapidocr`), com uma fusão de fragmentos calibrada fora do
teste, atinge **F1 0,812** nas fotos de celular do GNHK e **0,982** nas páginas em português do BRESSAY. O
Doc-UFCN do ADR-002 fica em 0,428 e 0,675 mesmo com a fusão. O PP-OCR também é o mais rápido dos modelos.

| Hipótese | Veredito | Evidência |
| :--- | :--- | :--- |
| H1 — a fusão leva o Doc-UFCN `norhand` a ≥ 80 % do teto (≥ 0,43 GNHK, ≥ 0,57 BRESSAY) | **Refutada, por pouco** | 0,428 no GNHK (meta 0,43); 0,675 no BRESSAY (atendida) |
| H2 — algum candidato com F1 ≥ 0,60 no GNHK e ≥ 0,70 no BRESSAY | **Confirmada** | `ppocr-det`: 0,812 e 0,982 (fundido); 0,739 e 0,970 bruto |
| H3 — o clássico fica abaixo dos modelos | **Confirmada** | clássico: 0,186 e 0,233 |
| H4 — melhor candidato ≤ 3 s por página e ≤ 2 GiB | **Confirmada** | `ppocr-det`: 2,4 s e 2,8 s; pico de 858 MiB |
| H5 — o veredito não muda quando a medida é a cobertura de área | **Confirmada** | o `ppocr-det` lidera nas duas medidas, nos dois conjuntos |

---

## 2. Resultados

Benchmark: [`BENCHMARK-20261014-exp-008-line-detection.json`](../../evaluation/benchmarks/BENCHMARK-20261014-exp-008-line-detection.json),
commit `74c34ea`, árvore limpa. Teste: as divisões oficiais usadas no EXP-007 (172 fotos, 2.189 linhas; 185
páginas, 5.496 linhas). Calibração: 150 fotos do treino do GNHK e 136 páginas da validação do BRESSAY. Os números
do EXP-007 foram reproduzidos exatamente antes de qualquer medição nova.

### 2.1 F1 de linhas (IoU ≥ 0,5 por caixa)

| Candidato | GNHK bruto | GNHK fundido | BRESSAY bruto | BRESSAY fundido | Média fundida |
| :--- | ---: | ---: | ---: | ---: | ---: |
| **`ppocr-det`** | 0,739 | **0,812** | 0,970 | **0,982** | **0,897** |
| `docufcn-norhand` (ADR-002) | 0,345 | 0,428 | 0,372 | 0,675 | 0,552 |
| `docufcn-historical` | 0,107 | 0,205 | 0,199 | 0,562 | 0,383 |
| `classic` | 0,139 | 0,186 | 0,066 | 0,233 | 0,209 |

`ppocr-det` fundido: precisão 0,793 e revocação 0,832 no GNHK; 0,971 e 0,994 no BRESSAY.

### 2.2 Fusão de fragmentos calibrada

| Candidato | Parâmetros escolhidos na calibração | Calibração: bruto → fundido |
| :--- | :--- | :--- |
| `ppocr-det` | sobreposição vertical 0,7; distância 1,0 altura de linha; inclinação 20° | 0,860 → 0,897 |
| `docufcn-norhand` | 0,5; 40 alturas; 45° | 0,317 → 0,540 |
| `docufcn-historical` | 0,3; 40 alturas; 45° | 0,155 → 0,376 |
| `classic` | 0,5; 40 alturas; 45° | 0,096 → 0,192 |

Para os Doc-UFCN e o clássico, o melhor ponto ficou na borda da grade, mesmo depois de ampliada (de 12 para 40
alturas e de 20° para 45°, ainda só na calibração): o que funciona para eles é unir tudo o que está na mesma faixa
horizontal. Para o PP-OCR basta unir vizinhos muito próximos; ele já entrega a linha quase inteira.

### 2.3 Cobertura de área (medida complementar, fundido)

| Candidato | GNHK: coberto / fora | BRESSAY: coberto / fora |
| :--- | :--- | :--- |
| `ppocr-det` | 0,948 / 0,139 | 0,985 / 0,030 |
| `docufcn-norhand` | 0,695 / 0,180 | 0,621 / 0,003 |
| `docufcn-historical` | 0,513 / 0,186 | 0,611 / 0,006 |
| `classic` | 0,581 / 0,161 | 0,524 / 0,024 |

O Doc-UFCN não só parte as linhas: deixa de fora 30 % a 38 % da área delas.

### 2.4 Onde o `ppocr-det` ainda erra

| Conjunto | Linhas não casadas | Fundidas com a vizinha | Partidas | Desalinhadas | Não vistas |
| :--- | ---: | ---: | ---: | ---: | ---: |
| GNHK | 367 de 2.189 | 190 | 91 | 59 | 27 |
| BRESSAY | 34 de 5.496 | 2 | 4 | 4 | 24 |

No GNHK o erro dominante passa a ser **fundir linhas vizinhas**: a fusão às vezes junta linhas muito próximas,
e o detector bruto já junta algumas. Por região de origem das fotos, o F1 fundido fica entre 0,793 e 0,818 —
variação pequena, ao contrário do Doc-UFCN.

### 2.5 Custo (mediana por página, CPU)

| Candidato | GNHK | BRESSAY 3× | Pico de memória |
| :--- | ---: | ---: | ---: |
| `ppocr-det` | 2,4 s | 2,8 s | 760–858 MiB |
| `docufcn-norhand` | 2,9 s | 3,6 s | 842–901 MiB |
| `docufcn-historical` | 2,9 s | 3,9 s | 846–912 MiB |
| `classic` | 1,0 s | 3,7 s | 104–304 MiB |

### 2.6 Saída em LDF 2.0

Todas as saídas fundidas foram gravadas em LDF 2.0: 1.424 de 1.428 documentos válidos. As 4 exceções são do
`classic` (2 por conjunto): linhas que ficam com área nula ao serem recortadas à imagem; o conversor recusa e elas
são contadas, não escondidas. Os outros três candidatos: 100 % válidos.

---

## 3. Critérios de sucesso

| Critério | Resultado |
| :--- | :--- |
| SC-001 — benchmark com calibração e teste separados; EXP-007 reproduzido | Atendido |
| SC-002 — ao menos três candidatos medidos | Atendido: quatro |
| SC-003 — veredito de H1 a H5 | Atendido (§1) |
| SC-004 — 100 % das saídas válidas em LDF 2.0 | Atendido para os três modelos; o `classic` tem 4 de 357 documentos não representáveis por caixa degenerada, contados |
| SC-005 — nada de conteúdo no Git; nada fora da pasta; disco no teto | Atendido (§6) |
| SC-006 — ADR | Atendido: ADR-006 `ACCEPTED` |

---

## 4. Desvios em relação ao plano

| Planejado | O que ocorreu |
| :--- | :--- |
| PP-OCRv5 mobile det | O wheel do `rapidocr` 3.10.0 traz o **PP-OCRv6 small det** (Apache-2.0, card oficial conferido); usado sem download adicional |
| Aprovar tarefas, download e exceção do BRESSAY uma a uma | Decididos por delegação: o usuário aprovou o plano e autorizou seguir sem parar, inclusive com instalações |
| `min_cc` dos Doc-UFCN na busca em grade | Fora: exigiria rodar o modelo de novo para cada valor; a fusão é aplicada sobre a saída |
| Grade da fusão até 12 alturas e 20° | Ampliada até 40 alturas e 45° porque três candidatos ficaram na borda; feito só com os conjuntos de calibração, antes de qualquer leitura do teste |
| Calibração com 154 páginas do BRESSAY | 136 utilizáveis (18 com recorte não localizado, mesma regra do EXP-007) |
| Execução de uma vez | O `ppocr-det` e o `classic` falharam na primeira tentativa por dois erros de código do adaptador e do carregador, corrigidos com testes; foram rodados depois dos Doc-UFCN, sem concorrência |

---

## 5. Limitações

* **Ainda não é caderno.** O GNHK é em inglês e o BRESSAY não é foto de celular. Página de caderno pautado
  brasileiro fotografada segue sem medição; a pauta impressa pode confundir um detector de texto.
* **Calibração e teste do mesmo dataset.** A fusão foi calibrada no treino do GNHK e na validação do BRESSAY e
  testada nas divisões de teste dos mesmos datasets: mede generalização dentro deles.
* **O BRESSAY é fácil para o PP-OCR** (0,97 já sem fusão): recortes de redação escaneados, sem fundo. O número
  que mais pesa é o do GNHK.
* **A verdade de chão de linha do GNHK é derivada** das palavras; a cobertura (0,95) sugere que boa parte do erro
  restante é de agrupamento, não de tinta perdida.
* **Detecção sem leitura.** O PP-OCR também tem um reconhecedor de texto; ele não foi usado aqui.
* Uma execução de cada detector.

---

## 6. Manifesto de reprodutibilidade

| Item | Valor |
| :--- | :--- |
| Hardware / SO | i5-8265U, 7,9 GB RAM, Windows 11 Pro, CPU-only |
| Ambientes | `experiments/EXP-002/envs/{harness,docufcn}` com `--frozen`; `experiments/EXP-008/envs/ppocr` (Python 3.12, `rapidocr` 3.10.0, `onnxruntime` 1.31.0, lock versionado) |
| Modelo novo | `PP-OCRv6_det_small.onnx`, SHA-256 `090f04abcd9d9a7498bc4ebf677e4cb9bdce1fe4197ddb7e529f1ef44e1ff94f`, conferido antes da carga |
| Candidatos e licenças | [`candidates.json`](./candidates.json) |
| Conjuntos | calibração em [`subsets.json`](./subsets.json); teste em `experiments/EXP-007/subsets.json` |
| Calibração | [`calibration.json`](./calibration.json), com a grade inteira |
| Commit da medição | `74c34ea`, árvore limpa |
| Relatório | `evaluation/benchmarks/BENCHMARK-20261014-exp-008-line-detection.json` |

```powershell
$h = "experiments/EXP-002/envs/harness"
uv run --frozen --project $h python experiments/EXP-008/harness/prepare.py
uv run --frozen --project $h python experiments/EXP-008/harness/detect.py --candidate ppocr-det --set test-gnhk
# ... um comando por candidato e conjunto (ver detect.py) ...
uv run --frozen --project $h python experiments/EXP-008/harness/calibrate.py
uv run --frozen --project $h python experiments/EXP-008/harness/run.py --out evaluation/benchmarks/bench.json
```

**Verificação final (2026-10-14):** `uv run pytest` — 239 passed; testes do harness do EXP-008 — 39 passed; `uv run ruff check .` — limpo; EXP-001 a EXP-003 intactos; nada fora de `document-intelligence/`; nenhum arquivo de dataset rastreado pelo Git; disco abaixo do teto de 20 GB.

---

## 7. Conformidade com a Constituição

* [x] **Local-first:** o modelo novo veio dentro do wheel; nenhuma rede na inferência.
* [x] **Evidência antes de decisão:** parâmetros escolhidos só na calibração; teste lido uma vez.
* [x] **Sem modelos prematuros:** nada entrou em `pyproject.toml` nem em `src/`; o candidato vive no seu ambiente.
* [x] **Privacidade:** nenhuma imagem, recorte ou transcrição de terceiros no Git, em relatório ou no chat.
* [x] **Experimentos aceitos intactos:** EXP-001 a EXP-003 e EXP-007 só lidos.
* [x] **LDF:** saídas em 2.0 validadas.

---

## 8. Homologação

- [x] Entregáveis do EXP-008 concluídos e submetidos ao usuário.
- [x] EXP-008 **ACEITO** (aceito por delegação do usuário em 2026-10-18).
- [x] ADR-006 aceito (aceito por delegação do usuário em 2026-10-18).

*Assinatura do agente executor:* `Claude Code (claude-opus-5-5), 2026-10-14`
