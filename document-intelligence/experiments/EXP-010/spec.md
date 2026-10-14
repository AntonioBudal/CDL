# EXP-010 — Outros Reconhecedores do PP-OCR e Efeito da Resolução da Linha (especificação e plano)

**Created**: 2026-10-14 · **Status**: `DELEGATED` — escrito e executado por delegação do usuário ("planeje as
próximas e continue executando"); revisado com os resultados.

**Input**: ADR-007 (`PROPOSED`): o PP-OCRv6 small rec lê as linhas do EXP-001 com CER 38,5 %; acentos com 80 % de
erro; a página ampliada 3× leu melhor que os recortes nativos.

## Pergunta e hipóteses

Algum reconhecedor do mesmo ecossistema, sem nenhum treino, lê português manuscrito melhor que o PP-OCRv6 small? E
quanto a escala do recorte da linha muda a leitura?

- **H1:** algum dos dois alternativos (PP-OCRv6 **medium**, multilíngue; PP-OCRv5 **latino** mobile) reduz o CER das
  398 linhas do EXP-001 em pelo menos 5 pontos (≤ 33,5 %).
- **H2:** ampliar o recorte da linha (2× ou 3×, bicúbico) antes da leitura reduz o CER em pelo menos 2 pontos.
- **H3:** algum reconhecedor atinge o critério de adoção do EXP-001 (CER ≤ 12 %, WER ≤ 25 %). Esperado: não.
- **H4:** custo ≤ 150 ms por linha e ≤ 2 GiB.

## Conjuntos e método

* **Linhas do EXP-001** (398, BRESSAY teste) — comparação principal; **linhas do GNHK** (1.918, inglês, celular) —
  controle de que o modelo lê manuscrito.
* Três reconhecedores × três escalas (1×, 2×, 3×) nas linhas do EXP-001; os três reconhecedores em 1× no GNHK.
* Mesma métrica do EXP-009 (CER/WER micro, NFC; CER por classe de caractere). Nenhum parâmetro escolhido olhando o
  teste: as escalas e os modelos são todos reportados.
* **Modelos novos:** `PP-OCRv6_rec_medium.onnx` (SHA-256 `eef44482…`) e `latin_PP-OCRv5_rec_mobile.onnx` (SHA-256
  `b20bd37c…`), baixados pelo próprio `rapidocr` do repositório do projeto (ModelScope, `RapidAI/RapidOCR`, versão
  3.10.0), com o SHA-256 publicado no pacote conferido. Licença: Apache-2.0 nos cards oficiais
  `PaddlePaddle/PP-OCRv6_medium_rec_onnx` e `PaddlePaddle/latin_PP-OCRv5_mobile_rec_onnx` — `LICENSE STATUS:
  VERIFIED`, conforme declarado.
* Download autorizado pelo usuário em 2026-10-13 ("se precisar instalar algo está autorizado").
* Mesmas regras de privacidade: nenhum texto de referência ou lido no Git, em relatórios ou no chat.

## Tarefas

- [ ] **T001** Baixar e conferir os dois modelos; registrar licenças.
- [ ] **T002** Generalizar o leitor de linha do EXP-009 (modelo e escala como opções), com teste da escala.
- [ ] **T003** Rodar 3 modelos × 3 escalas nas linhas do EXP-001 e 3 modelos × 1× no GNHK.
- [ ] **T004** Relatório, ADR (ou atualização do ADR-007), registros, verificação.
