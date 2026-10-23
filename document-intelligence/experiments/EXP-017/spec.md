# EXP-017 — Teto de Ponta a Ponta com o Leitor Ajustado (especificação, plano e tarefas)

**Created**: 2026-10-22 · **Status**: `ACCEPTED` / `CONCLUÍDO` (por delegação, 2026-10-22; resultados em [RESULTS.md](./RESULTS.md))

**Input**: EXP-014 (ajuste fino experimental com as linhas de treino do BRESSAY: CER de linha 29,7 % → 13,6 %) e
EXP-015 (pipeline do ADR-008 com leitura direta: redações 27,5 % de CER de página, fotos 27,4 %).

## Pergunta e hipóteses

Quanto do ganho de linha do ajuste fino chega ao texto de página, com detecção, fusão, recorte e correção lexical
reais? A resposta estima o que um ajuste fino com dados **com licença para produto** daria, e por isso orienta o
pedido de dados ao usuário. O modelo ajustado no BRESSAY continua **só experimental** (`NEEDS VALIDATION`).

- **H1:** redações (BRESSAY, divisão oficial de teste, autores fora do treino): CER de página ≤ 20 % (EXP-015:
  27,5 %).
- **H2:** fotos em inglês (GNHK): o CER de página não piora mais de 3 pontos (EXP-015: 27,4 %). O ajuste foi só em
  português, então piora é possível; o valor mede o custo de especializar.
- **H3:** a exportação para ONNX reproduz o modelo PyTorch (diferença máxima ≤ 1e-4 nas probabilidades, em linhas
  fictícias de várias larguras); 100 % LDF 2.0 válido; custo por página igual ao do EXP-015 (mesma arquitetura).

## Método

1. **Exportação** (ambiente `EXP-014/envs/ft`): `models/exp-014/best.pt` → `models/exp-017/rec-ft-bressay.onnx`
   (fora do Git), com lote e largura dinâmicos e a lista de caracteres do original nos metadados. Paridade com
   o PyTorch em linhas fictícias de 320 a 1600 px.
2. **Pipeline**: cópia do EXP-015 com uma só mudança, o arquivo do modelo de leitura (caminho e SHA-256 nas
   opções). Detecção, escala automática (alvo 80 px), fusão, recorte, margem de 640 px, decodificação e correção
   lexical ficam iguais. Nenhum parâmetro novo.
3. **Teste**: os dois conjuntos de teste do EXP-015, uma vez; pontuação igual à do EXP-015.

## Tarefas

- [x] **T001** Exportar e conferir a paridade (sonda com linhas fictícias).
- [x] **T002** Harness (cópia do EXP-015) com o modelo configurável e testes.
- [x] **T003** Rodar os dois conjuntos de teste; pontuar; relatório; registrar no ADR-009.
