# ADR-006: Detecção de linhas pelo detector de texto do PP-OCR, com fusão de fragmentos

* **Status:** PROPOSED
* **Data:** 2026-10-14
* **Decisores:** Usuário (decisão); Claude Code (proposta)
* **Experimento de Suporte:** [EXP-008](../../experiments/EXP-008/RESULTS.md)
* **Status de Licença:** `rapidocr` 3.10.0 (Apache-2.0), pesos PP-OCRv6 small det (Apache-2.0, conforme o `MODEL_LICENSES.md` do wheel e o card oficial) e ONNX Runtime (MIT) — `LICENSE STATUS: VERIFIED`, conforme declarado. Evidência: GNHK (`VERIFIED`) e BRESSAY (`NEEDS VALIDATION`, não embasa produto). A decisão se sustenta só com o GNHK.

---

## 1. Contexto e Declaração do Problema

O ADR-005 registrou que o Doc-UFCN `norhand`, direção de linhas do ADR-002, não funciona em manuscrito real (F1
0,345 em fotos de celular) e exigiu benchmark real para qualquer componente de layout. O EXP-008 comparou quatro
detectores nesse benchmark, brutos e com uma fusão de fragmentos calibrada fora do teste.

---

## 2. Drivers de Decisão

* **Driver 1:** F1 de linhas em imagens reais (GNHK como critério principal, por licença e por ser foto de celular).
* **Driver 2:** Local-first, CPU, instalação por wheels, licenças verificadas.
* **Driver 3:** Custo ≤ 3 s e ≤ 2 GiB por página.
* **Driver 4:** Saída representável em LDF 2.0.

---

## 3. Opções Consideradas

| Opção | GNHK (fundido) | BRESSAY (fundido) | Custo |
| :--- | ---: | ---: | ---: |
| A — PP-OCRv6 small det (`rapidocr`) + fusão | **0,812** | **0,982** | 2,4–2,8 s |
| B — Doc-UFCN `norhand` + fusão | 0,428 | 0,675 | 2,9–3,6 s |
| C — Doc-UFCN `generic-historical-line` + fusão | 0,205 | 0,562 | 2,9–3,9 s |
| D — clássico (OpenCV) + fusão | 0,186 | 0,233 | 1,0–3,7 s |

---

## 4. Decisão Escolhida

**Opção A** como direção de trabalho para detecção de linhas:

1. O detector de texto do PP-OCRv6 small, executado com ONNX Runtime pelo `rapidocr`, só a etapa de detecção, com
   a fusão de fragmentos calibrada no EXP-008 (sobreposição vertical 0,7; distância 1,0 altura de linha;
   inclinação até 20°).
2. O Doc-UFCN sai da direção de trabalho para linhas. O ADR-002 já estava substituído nesse ponto pelo ADR-005;
   este ADR preenche a lacuna.
3. Continua experimental: nada entra em `src/` nem em `pyproject.toml` sem validação em página de caderno
   fotografada e spec de produto.

---

## 5. Evidência

Benchmark do commit `74c34ea`, árvore limpa, divisões oficiais de teste (172 fotos, 185 páginas). Calibração em
conjuntos separados (treino do GNHK, validação do BRESSAY).

* `ppocr-det`: precisão 0,793 e revocação 0,832 no GNHK; cobertura de 95 % da área das linhas.
* Lidera também pela medida de cobertura de área, em que o Doc-UFCN deixa 30 % a 38 % da área das linhas de fora.
* F1 entre 0,793 e 0,818 nas quatro regiões de origem das fotos.
* Todas as saídas válidas em LDF 2.0.

---

## 6. Consequências

### Positivas

* Pela primeira vez há uma etapa do pipeline validada em imagens reais.
* É mais rápida que a anterior e usa menos memória.
* O mesmo pacote traz um reconhecedor de texto, que pode ser medido em português sem dependência nova (ver
  próximo passo).

### Negativas / Trade-offs

* **Não é caderno.** Pauta impressa, margens e anotações sobrepostas não foram testadas.
* **Erro restante:** no GNHK, linhas vizinhas fundidas (190 de 367 linhas perdidas). Afeta o que vier depois
  (leitura, ordem).
* **Dependência nova num ambiente isolado** (`rapidocr`, ONNX Runtime). A biblioteca baixa modelos sob demanda em
  outras configurações; aqui só o modelo embutido no wheel é usado, com SHA-256 conferido.
* A fusão foi calibrada nos mesmos datasets do teste (divisões diferentes): a generalização para cadernos é
  hipótese.

### Próximo passo sugerido

Medir o reconhecedor de texto que vem no mesmo pacote (PP-OCRv6 small rec) em linhas manuscritas em português,
contra a referência do EXP-001, e o pipeline detecção → leitura de ponta a ponta. Se ler português manuscrito
melhor que os candidatos do ADR-001, muda a premissa mais pesada do projeto.

### Conformidade com a Constituição

* [x] Local-first, sem rede na inferência.
* [x] Evidência antes de decisão: teste lido uma vez, parâmetros só da calibração.
* [x] Licenças declaradas; BRESSAY fora de qualquer decisão de produto.
* [x] Privacidade: nada de conteúdo de terceiros no Git ou em relatórios.
