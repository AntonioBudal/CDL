# EXP-001 — Isolated Line Handwritten Text Recognition (Contexto e Requisitos)

> [!NOTE]
> O **EXP-000** foi aceito em 2026-09-30 e o bloqueio foi levantado. O EXP-001 segue o ciclo Spec Kit adaptado a
> experimentos: ver [`EXP-001/spec.md`](./EXP-001/spec.md), [`plan.md`](./EXP-001/plan.md) e [`tasks.md`](./EXP-001/tasks.md).
> **Nenhuma execução (código de avaliação, inferência ou download de pesos) antes da aprovação da especificação/plano.**

* **Status:** `SPECIFICATION — AWAITING USER REVIEW` (execução não iniciada)
* **Responsável:** Claude Code
* **Domínio:** Handwritten Text Recognition (HTR) — Linhas Manuscritas Isoladas

---

## 1. Visão Geral e Hipótese

O objetivo do **EXP-001** será avaliar e comparar abordagens leves e viáveis localmente para a tarefa de **Reconhecimento de Texto Manuscrito (HTR)** em **linhas recortadas e isoladas** de texto manuscrito em **língua portuguesa**.

Uma vez recortada a imagem de uma linha de caderno (suporte horizontal, pautado ou pontilhado), o pipeline deve converter os pixels na sequência textual correta, preservando acentuação gráfica (`á`, `ã`, `ç`, `ê`, etc.) e pontuação básica.

---

## 2. Abordagens Técnicas a Comparar (Local-First)

O Claude Code deverá avaliar candidatos que cumpram a Constituição (código aberto, pesos livres, custo zero de inferência, sem APIs pagas):

1. **Abordagens Baseadas em CNN-RNN-CTC:**
   - Modelos clássicos de HTR leves (ex: CRNN, PyLaia ou implementações PyTorch equivalentes).
   - Prós: Baixíssimo consumo de VRAM/RAM, inferência rápida em CPU.
   - Contras: Podem exigir alinhamento fino e vocabulário explícito.
2. **Abordagens Baseadas em Transformers de Visão / Encoder-Decoder:**
   - Modelos como TrOCR (versão `small` ou `base`), Donut (recortado) ou similares com pesos abertos.
   - Prós: Alta acurácia em reconhecimento de escrita cursiva e mista.
   - Contras: Maior consumo de memória e latência por linha; necessidade de pesos permissivos (`LICENSE STATUS: VERIFIED`).
3. **Baseline Tradicional (Tesseract / EasyOCR adaptado):**
   - Servirá exclusivamente como linha de base (baseline) comparativa.

---

## 3. Requisitos de Entrada e Idioma

* **Entrada:** Imagens de linhas isoladas (escala de cinza ou RGB), dimensões variáveis (ex: altura padronizada em 32px a 64px, largura proporcional).
* **Idioma:** Português do Brasil (PT-BR), cobrindo:
  - Vogais acentuadas: `á, é, í, ó, ú, â, ê, ô, ã, õ, à`.
  - Cedilha: `ç, Ç`.
  - Pontuação: vírgulas, pontos finais, dois pontos, hifens, aspas, parênteses e pontos de interrogação.
  - Dígitos numéricos: `0-9`.

---

## 4. Métricas e Limiares de Avaliação (Hipóteses Iniciais)

* **CER (Character Error Rate):** $\le 12\%$ no conjunto de validação de escrita cursiva em português (meta inicial para linhas limpas).
* **WER (Word Error Rate):** $\le 25\%$ no conjunto de validação.
* **Tempo de Inferência:** $\le 150 \text{ ms}$ por linha em CPU moderna (ou $\le 30 \text{ ms}$ com GPU local).
* **Uso de Memória RAM/VRAM:** $\le 2.0 \text{ GB}$ durante a inferência.

---

## 5. Critérios de Aceite para Conclusão do EXP-001

Quando for executado, o Claude Code deverá entregar:
1. Benchmark comparativo documentado entre pelo menos duas abordagens viáveis.
2. Análise detalhada de erros (confusão frequente entre caracteres acentuados, números e letras semelhantes como `l` vs `1`, `O` vs `0`).
3. Verificação formal de licença dos pesos utilizados (`models-and-licensing.md`).
4. Decisão arquitetural registrada via ADR em `docs/adr/`.
5. Nenhum código de acoplamento com o backend do Leitorum fora do formato LDF.
