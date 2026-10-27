# EXP-021 — Ajuste Fino com Degradações de Foto (especificação, plano e tarefas)

**Created**: 2026-10-26 · **Status**: `ACCEPTED` — concluído por delegação em 2026-10-26 ([RESULTS](./RESULTS.md)) (autonomia permanente do usuário, 2026-10-18)

**Input**: EXP-019 e EXP-020. O leitor ajustado (EXP-014/017) vai de 11,8 % de CER de página na digitalização
para 21,6 % na foto leve e 70,6 % na forte; a escala não é a causa (EXP-020). Na foto leve só 4 % das linhas
deixam de ser detectadas, então o ponto principal é o leitor diante de letras borradas, com ruído e com luz
irregular. O ajuste do EXP-014 só viu digitalizações limpas.

## Pergunta e hipóteses

Treinar o leitor com as linhas degradadas como foto (aumento de dados) reduz a perda em condições de foto sem
piorar a digitalização? A resposta orienta o pedido de dados ao usuário: se o aumento resolver, digitalizações
servem; se não, as páginas pedidas precisam ser fotos.

- **H1:** foto leve: CER de página cai pelo menos 3 pontos (21,6 %).
- **H2:** digitalizada: CER de página não piora mais de 1 ponto (11,8 %).
- **H3:** foto forte: CER de página cai (70,6 %); sem limiar, porque a detecção também falha nesse nível.

## Método

* **Treino:** o do EXP-018 (retomável) com todas as 647 páginas de treino do BRESSAY, mesmo orçamento do EXP-014
  (392 passos de 16 linhas, taxa 5e-5, margem 640 px, semente 1234), partindo do modelo original. Única mudança:
  cada linha do lote é degradada com probabilidade 0,5.
* **Degradação de linha** (fixada antes de rodar, a partir dos níveis do EXP-002; nada ajustado no teste): nível
  sorteado entre leve e forte; gradiente de luz (brilho mínimo 0,55–0,82), desfoque gaussiano (σ 0,5–1,1), ruído
  (σ 2–5), JPEG (qualidade 65–88) e inclinação pequena (±3°). Gerador próprio, com semente por passo, para não
  mudar a ordem dos lotes.
* **Exportação** para ONNX como no EXP-017 (paridade ≤ 1e-4).
* **Medida:** pipeline do EXP-019 (escala pela caixa, ADR-008) com o novo leitor, nas 185 páginas de teste
  digitalizadas, leves e fortes; uma vez cada. Também o CER de validação de linha (limpa), como no EXP-014.
* Pesos em `models/exp-021/` (fora do Git, só experimento; BRESSAY `NEEDS VALIDATION`).
* Custo: ~3,3 h de treino + ~1 h de leitura, com ≥ 1,5 GB de RAM livre antes de cada etapa.

## Tarefas

- [x] **T001** Degradação de linha com testes; treino com `--augment`; exportação; harness de leitura.
- [x] **T002** Treino, exportação e paridade.
- [x] **T003** Três leituras; pontuação; relatório; registrar no ADR-009.
