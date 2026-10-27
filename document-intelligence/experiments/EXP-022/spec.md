# EXP-022 — Páginas do BRESSAY Impressas e Fotografadas com Celular (especificação, plano e tarefas)

**Created**: 2026-10-27 · **Status**: `DELEGATED` (autonomia permanente do usuário, 2026-10-18; teste pedido pelo
usuário em 2026-10-27)

**Input**: EXP-019 a EXP-021. Toda a medida em condições de foto até aqui é **sintética** (degradação do EXP-002
sobre a digitalização). Não há banco público de fotos de manuscrito em português com transcrição (busca de
2026-10-27: LHTR.br são formulários digitalizados com texto fixo; PorTEXTO sem download nem licença). O usuário
não tem fotos de caderno; aceitou imprimir páginas de teste do BRESSAY e fotografá-las com o celular.

## Pergunta e hipóteses

Como o pipeline do ADR-008 se sai numa **foto de celular de verdade** de manuscrito em português com transcrição
conhecida, e a degradação sintética do EXP-019 representa bem essa condição?

- **H1:** com o leitor ajustado, o CER de página nas fotos fica entre o da digitalização (11,8 % nas 185
  páginas) e o da foto leve sintética (21,6 %). Comparação nas mesmas páginas.
- **H2:** o pipeline roda em fotos de 12 MP sem erro e dentro de 1 GiB de memória de pico, com 100 % LDF 2.0
  válido.

## Método

* **Páginas:** 15 das 185 de teste do BRESSAY (EXP-017), sorteadas com semente fixa (`exp-022`).
* **Impressão:** cada página ampliada 4× (Lanczos; as originais têm ~524 × 573 px) e centralizada numa folha A4 a
  300 dpi, sem rótulo nem número (nada que o leitor possa ler além da redação). PDF fora do Git, em
  `dataset/processed/exp-022/imprimir.pdf`.
* **Fotos (usuário):** uma foto por folha, celular na câmera normal, folha inteira no quadro, luz ambiente, sem
  flash nem recorte; arquivos originais (sem compressão de mensageiro) em `dataset/raw/exp-022/fotos/`.
* **Associação foto → página:** sem rótulos, cada foto é lida e associada à página de teste cuja referência dá o
  menor CER (atribuição um-a-um). As 15 redações são de autores e textos diferentes; a margem entre o melhor e o
  segundo par é registrada.
* **Medida:** pipeline do EXP-019 (escala pela caixa) com o leitor original e com o ajustado (EXP-017), uma vez.
  Comparação com as mesmas 15 páginas digitalizadas (EXP-017) e na foto leve e forte sintéticas (EXP-019).
* **Limitação conhecida:** a fonte impressa é uma digitalização de baixa resolução ampliada; a foto mede a câmera
  real sobre essa fonte, não sobre tinta original.
* Licença: BRESSAY `NEEDS VALIDATION`, uso só experimental local; impressões e fotos não saem da máquina, nada no
  Git, em relatório ou no chat.

## Tarefas

- [x] **T001** Sorteio das páginas e PDF para impressão.
- [ ] **T002** (usuário) Imprimir e fotografar.
- [ ] **T003** Harness de leitura das fotos com associação por menor CER; rodar os dois leitores; pontuar;
  relatório.
