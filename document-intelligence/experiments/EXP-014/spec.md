# EXP-014 — Adaptação do Reconhecedor à Caligrafia Brasileira (proposta)

**Created**: 2026-10-18 · **Status**: `ACCEPTED` / `CONCLUÍDO` (executado por delegação em 2026-10-22; resultados em [RESULTS.md](./RESULTS.md)). Texto original da proposta abaixo. A execução
exige treino de modelo, que é de outra ordem de custo que os experimentos anteriores (ver §Viabilidade).

**Input**: ADR-007 e ADR-008: o pipeline completo funciona, mas o reconhecedor PP-OCRv6 small erra ~34 % dos
caracteres em caligrafia brasileira (14,8 % em inglês). Pós-processamento (EXP-011) e escala (EXP-010, EXP-013) já
foram explorados.

## Pergunta

Quanto um ajuste fino do reconhecedor com manuscrito em português reduz o erro de leitura?

## Hipóteses

- **H1:** ajuste fino do PP-OCRv6 small rec com as linhas de **treino** do BRESSAY (cerca de 19 mil) leva o CER das
  398 linhas do EXP-001 abaixo de 20 %.
- **H2:** o ganho se mantém em linhas de autores que não estavam no treino (as divisões oficiais já separam
  autores).
- **H3:** a inferência continua ≤ 150 ms por linha.

## Restrições que esta proposta respeita

* **Licença:** o BRESSAY só permite pesquisa não comercial (`NEEDS VALIDATION`). Um modelo ajustado nele é
  **experimental e não pode ir para o produto**. Para o produto, o mesmo procedimento teria de ser repetido com
  dados com licença adequada — por exemplo, páginas escritas para esse fim com consentimento, ou um dataset
  português com licença comercial verificada.
* **Local-first:** treino local; nada enviado a serviços externos.
* **Disco e memória:** dentro do teto de 20 GB; treino limitado a lotes que caibam em ~1,5 GiB de RAM livre.

## Viabilidade (o que precisa ser resolvido antes de executar)

* O ajuste fino oficial é feito com o PaddlePaddle (PaddleOCR). Rodar em CPU nesta máquina (i5-8265U, 7,9 GB) é
  possível, mas lento: estimativa grosseira de uma a várias horas por época, com várias épocas necessárias. A
  GPU MX110 (2 GB) dificilmente é utilizável.
* Alternativa mais leve: congelar o extrator de características e treinar só a cabeça CTC num ambiente PyTorch
  convertido do ONNX — exige trabalho de conversão e validação próprios.
* Primeira tarefa do plano: medir o custo real de uma época numa amostra pequena antes de comprometer horas de
  máquina.

## Plano resumido

**Revisão de 2026-10-22 (delegação):** em vez do PaddlePaddle, a primeira tentativa usa o próprio modelo ONNX
convertido para PyTorch (`onnx2torch`, MIT; PyTorch CPU, BSD-3-Clause), num ambiente isolado. Evita instalar o
PaddlePaddle e o repositório de treino; se a conversão não preservar a saída do modelo, volta-se ao PaddleOCR.

0. **Viabilidade (Fase 1):** converter o PP-OCRv6 small rec; conferir que a saída do PyTorch coincide com a do
   ONNX Runtime em recortes fictícios; cronometrar ida e volta (forward + backward com perda CTC) num lote de 16
   linhas; estimar o tempo por época nas ~19 mil linhas de treino. Decisão registrada no relatório.
1. Ambiente isolado e verificação de licenças.
2. Exportar linhas de treino e validação do BRESSAY (recortes exatos, como no EXP-011), ampliadas 2×.
3. Medir o custo de uma época em 1.000 linhas; decidir o orçamento de treino.
4. Ajustar, escolher a época pela validação, medir uma vez no teste (398 linhas do EXP-001 e todas as linhas de
   teste), com e sem a correção lexical.
5. ADR com o ganho medido e o que seria necessário para levar a técnica ao produto com dados licenciados.
