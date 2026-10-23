# EXP-018 — Curva de Aprendizado do Ajuste Fino (especificação, plano e tarefas)

**Created**: 2026-10-22 · **Status**: `DELEGATED` (autonomia permanente do usuário, 2026-10-18)

**Input**: EXP-014 (ajuste fino: CER de validação 32,0 % → 13,5 % em 392 passos de 16 linhas, ou seja, ~6,3 mil
linhas vistas uma vez, sorteadas das 647 páginas de treino do BRESSAY) e EXP-017 (de ponta a ponta: redações
27,5 % → 11,8 %). Falta saber **quantas páginas com licença para produto pedir**.

## Pergunta e hipóteses

Com o mesmo orçamento de treino do EXP-014 (392 passos), quanto do ganho se obtém com poucas páginas, cada uma lida
várias vezes?

- **H1:** com 50 páginas (~1,5 mil linhas) o CER de validação fica ≤ 18 %, isto é, mais de 3/4 do ganho do EXP-014.
- **H2:** com 16 páginas (~500 linhas) o CER de validação fica abaixo de 25 % (ganho de pelo menos 7 pontos).
- **H3:** com 150 páginas (~4,5 mil linhas) o resultado fica a até 1 ponto do EXP-014.

Os limiares são palpites de partida; o produto do experimento é a curva, que vira a recomendação de quantas páginas
pedir.

## Método

* Treino do EXP-014 copiado, com duas mudanças: `--pages N` (sorteio de N páginas inteiras do treino, semente fixa;
  todas as linhas de cada página) e `--steps 392` (orçamento por passos em vez de minutos, para os três pontos
  terem o mesmo número de atualizações). Taxa 5e-5, lote 16, margem 640 px, semente 1234, como no EXP-014.
* Pontos: 16, 50 e 150 páginas. O ponto de referência (todas as 647, ~6,3 mil linhas vistas) é o do EXP-014.
* Medida principal: CER no mesmo subconjunto de validação do EXP-014 (1 537 linhas), **no último passo** (sem
  escolher o melhor passo pela validação). Avaliações intermediárias a cada 98 passos, só para registro.
* Pesos em `models/exp-018/` (fora do Git, só experimento; BRESSAY `NEEDS VALIDATION`). Conjuntos de teste não são
  usados.
* Custo esperado: ~2,5 h de CPU por ponto, rodados um por vez (≥ 1 GiB de RAM livre).

## Tarefas

- [x] **T001** Treino com `--pages` e `--steps`; testes do sorteio por página.
- [ ] **T002** Três treinos (16, 50, 150 páginas).
- [ ] **T003** Curva, relatório e recomendação de quantidade de dados; registrar no ADR-009.
