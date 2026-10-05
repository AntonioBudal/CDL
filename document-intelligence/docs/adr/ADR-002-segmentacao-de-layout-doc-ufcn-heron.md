# ADR-002: Direção para segmentação de layout — Doc-UFCN para linhas, Heron para blocos, retificação por contorno

* **Status:** PROPOSED
* **Data:** 2026-10-05
* **Decisores:** Usuário (decisão); Claude Code (proposta)
* **Experimento de Suporte:** [EXP-002](../../experiments/EXP-002/RESULTS.md)
* **Status de Licença:** `LICENSE STATUS: VERIFIED` para as opções propostas (Doc-UFCN: código BSD-3-Clause, pesos MIT; Docling Heron: Apache-2.0; OpenCV: Apache-2.0). A evidência comparativa inclui o docTR, `LICENSE STATUS: NEEDS VALIDATION`, que não é proposto.

---

## 1. Contexto e Declaração do Problema

Antes de reconhecer texto ou ordenar a leitura, o pipeline precisa localizar, numa foto de página de caderno, as
linhas de texto e os blocos (título, parágrafo, nota de margem, caixa gráfica). O EXP-002 comparou um método
clássico, três modelos e dois retificadores de perspectiva em 180 páginas sintéticas com geometria conhecida, em
CPU, na máquina-alvo.

Este ADR define a **direção técnica** para os próximos experimentos. Não promove nenhum componente a produto:
isso exige validação em fotos reais e uma especificação própria no ciclo Spec Kit.

---

## 2. Drivers de Decisão (Critérios de Avaliação)

* **Driver 1:** Local-first e custo zero.
* **Driver 2:** Acurácia medida — linhas: F1 ≥ 0,90 (limpo) e ≥ 0,80 (degradado); blocos: mAP@0,5 ≥ 0,70.
* **Driver 3:** Custo em CPU — ≤ 2 s por página e ≤ 2 GB — e instalação só por wheels em Windows/`uv`.
* **Driver 4:** Licença permissiva de código e pesos; nada de AGPL.
* **Driver 5:** Preservação da fronteira com o produto principal e do contrato LDF.

---

## 3. Opções Consideradas

### Opção A: Baseline clássico (OpenCV) para linhas, com regras geométricas para blocos
* **Pontos Positivos (+):** sem pesos; 0,6 s por página; 93 MiB.
* **Pontos Negativos (-):** F1 de 0,85 em páginas limpas e 0,40 no nível forte (0,58 com retificação); blocos por
  regras com mAP de 0,26; muito sensível ao limiar de binarização.

### Opção B: docTR para linhas
* **Pontos Positivos (+):** instalação simples em Python 3.14.
* **Pontos Negativos (-):** pesos sem licença declarada; F1 de 0,84 / 0,69 / 0,39; fragmenta linhas inclinadas;
  2,1 s e 923 MiB.

### Opção C: Doc-UFCN (`norhand`) para linhas + retificação por contorno + Docling Heron para blocos
* **Pontos Positivos (+):**
  * Linhas: única combinação que cumpre a meta — 0,93 (limpo), 0,92 / 0,85 (leve / forte).
  * Blocos: mAP de 0,78, com `title` 0,99 e `paragraph` 0,91.
  * Retificação por contorno: 0,13 s, 60 MiB, sem pesos.
  * Licenças verificadas; tudo por wheels; cada componente abaixo de 1 GB.
* **Pontos Negativos (-):**
  * Tempo: ~2,6 s por página para linhas e ~4,4 s para linhas + blocos (meta: 2 s).
  * Doc-UFCN exige Python 3.10 e fixa `torch` 2.1.0; pesos em pickle.
  * Funde linhas vizinhas (principal modo de falha); curvatura da página não é corrigida.
  * `margin_note` no Heron fica em 0,53; retificação por contorno tem falhas grandes no nível forte.
  * Tudo medido só em páginas sintéticas.

### Opção D: Doc-UFCN para linhas e também para a folha (`docufcn-page`)
* **Pontos Positivos (+):** mais estável no nível forte (até 0,88 com a variante `historical`).
* **Pontos Negativos (-):** 2,5 s a mais por página, estourando ainda mais a meta de tempo.

---

## 4. Decisão Escolhida

Propõe-se a **Opção C como direção de trabalho**, com estas condições:

1. **Linhas:** Doc-UFCN `norhand` é o candidato de referência para os próximos experimentos. O baseline clássico e
   o docTR ficam descartados (o docTR também pela licença).
2. **Blocos:** Docling Heron é o candidato de referência para `title`, `paragraph` e `graphic_box`. As regras
   geométricas ficam descartadas. `margin_note` permanece em aberto.
3. **Retificação:** contorno clássico como etapa padrão antes da detecção de linhas; o `docufcn-page` fica como
   alternativa só se a medição em fotos reais mostrar que o contorno falha demais.
4. **Nenhum destes componentes entra em `src/leitorum_di/` agora.** Antes disso são necessários: (a) medição em
   fotos reais de caderno, com dados de licença e consentimento resolvidos; (b) uma decisão sobre a meta de 2 s,
   que a combinação não cumpre nesta máquina; (c) uma especificação de produto no Spec Kit.
5. **Contrato LDF:** as três lacunas registradas no EXP-002 (região de `graphic_box`, divergência entre o modelo
   Pydantic e o JSON Schema, `title` × `heading`) precisam de decisão própria antes de qualquer integração.

---

## 5. Evidência Empírica do Experimento

* **Experimento:** [EXP-002](../../experiments/EXP-002/RESULTS.md) e [análise de falhas](../../experiments/EXP-002/failure-analysis.md)
* **Linhas (F1, caixa, IoU ≥ 0,5; limpo / leve / forte):**
  * `docufcn-norhand-line`: 0,928 / 0,883 / 0,784; com `contour`: — / 0,920 / 0,845
  * `docufcn-historical-line`: 0,917 / 0,863 / 0,799; com `contour`: — / 0,900 / 0,799
  * `classic`: 0,847 / 0,743 / 0,397; `doctr`: 0,842 / 0,694 / 0,391
* **Blocos (mAP@0,5):** Heron 0,781; regras 0,26–0,45.
* **Custo:** Doc-UFCN 2,3–2,5 s e 650–830 MiB; Heron 1,7–1,9 s e 758 MiB; `contour` 0,13 s e 60 MiB.
* **Limitações Observadas:** dados sintéticos; curvatura não corrigida; linhas fundidas; blocos não medidos com
  retificação; sombra e desfoque não isolados.

---

## 6. Consequências

### Consequências Positivas
* O EXP-003 (ordem de leitura) pode partir de saídas reais de detectores, não só da verdade de chão.
* Fica definido um par de candidatos com licença verificada e um harness para medir alternativas.
* Abordagens fracas (regras de blocos, baseline clássico) deixam de consumir esforço.

### Consequências Negativas / Trade-offs
* Dois modelos em dois ambientes Python distintos (3.10 e 3.14), com `torch` 2.1.0 preso pelo Doc-UFCN.
* A meta de 2 s por página não é cumprida; será preciso revisá-la ou medir alternativas (por exemplo, um único
  modelo para linhas e blocos, ou exportação para ONNX — só com medição que justifique, pelo Princípio 6).
* A decisão vale para páginas sintéticas; pode mudar com fotos reais.
* Combinado com o ADR-001, o pipeline ainda não tem reconhecedor de texto.

### Conformidade com a Constituição
* [x] Princípio 1: Local-first garantido.
* [x] Princípio 2: Evidência antes de decisão — baseada nas medições do EXP-002.
* [x] Princípio 3: Reprodutibilidade — manifesto em `RESULTS.md` §7.
* [x] Princípio 6: Medição antes de otimização nativa — nenhuma otimização adotada.
* [x] Princípio 8: LDF como fronteira contratual preservado — lacunas registradas, contrato intocado.
