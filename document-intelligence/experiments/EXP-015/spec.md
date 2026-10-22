# EXP-015 — Pipeline com Leitura Direta e Margem (especificação, plano e tarefas)

**Created**: 2026-10-22 · **Status**: `DELEGATED` (autonomia permanente do usuário, 2026-10-18)

**Input**: ADR-008 (pipeline de referência com escala automática, EXP-013) e ADR-009 (leitura direta pelo ONNX
Runtime com 640 px de margem: CER de linha 41,9 % → 29,7 %).

## Pergunta e hipóteses

Trocar só a leitura do pipeline (mesmo modelo PP-OCRv6 small, sem treino, sem BRESSAY no modelo) melhora o texto
de página de ponta a ponta?

- **H1:** redações (BRESSAY, escala original, escala automática): CER de página cai pelo menos 5 pontos em relação
  ao EXP-013 (35,9 %).
- **H2:** fotos de celular (GNHK, inglês): CER de página não piora mais de 1 ponto (27,3 %).
- **H3:** custo ≤ 6 s por página na mediana; 100 % LDF 2.0 válido.

## Método

O pipeline do EXP-013 (detecção `rapidocr`, fusão, escala automática com alvo de 80 px, recorte) com a leitura
trocada pela do EXP-014: ONNX Runtime direto, altura 48 px, proporção mantida, margem de 640 px à direita,
decodificação gulosa. Correção lexical só no português. Nenhum parâmetro novo; conjuntos de teste do EXP-013, uma
vez.

## Tarefas

- [x] **T001** Harness (cópia do EXP-013) com o leitor direto e testes.
- [ ] **T002** Rodar os dois conjuntos de teste; pontuar; relatório; atualizar o ADR-008.
