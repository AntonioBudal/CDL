# EXP-020 — Escala Automática Medida na Linha Inclinada (especificação, plano e tarefas)

**Created**: 2026-10-26 · **Status**: `ACCEPTED` / `CONCLUÍDO` — não adotado (por delegação, 2026-10-26; resultados em [RESULTS.md](./RESULTS.md))

**Input**: EXP-019 (páginas do BRESSAY degradadas como fotos). Na degradação leve, o leitor ajustado foi de 11,8 %
para 21,6 % de CER de página. Diagnóstico com as leituras já feitas (só alturas, nenhum texto): a altura da
**caixa alinhada aos eixos** das linhas sobe 40 % (mediana por página) em relação à página limpa, enquanto a
altura do **quadrilátero** da linha sobe só 10 %; com isso, 129 de 185 páginas recebem escala menor que na
digitalização, e nenhuma maior. A regra de escala do EXP-013 mede a linha inclinada como se fosse mais alta.

## Pergunta e hipóteses

Medir a altura no quadrilátero da linha (média dos dois lados curtos), em vez da caixa alinhada aos eixos,
recupera parte da perda em condições de foto sem mudar o resultado nas digitalizações?

- **H1:** degradação leve, leitor ajustado: CER de página cai pelo menos 2 pontos (EXP-019: 21,6 %).
- **H2:** degradação forte, leitor ajustado: CER de página não piora.
- **H3:** página digitalizada, leitor ajustado: CER de página a até 0,3 ponto do EXP-017 (11,8 %).

## Método

* Pipeline do EXP-019 com uma só mudança em `median_height`: altura de cada linha = média dos comprimentos dos
  lados 1→2 e 3→0 do quadrilátero detectado (cai para a caixa quando não há quadrilátero). Alvo de 80 px e o
  resto iguais. Nenhum parâmetro novo.
* Só o leitor ajustado (o original mede o mesmo efeito; fica para depois se H1 se confirmar).
* Conjuntos: as páginas degradadas do EXP-019 (leve e forte) e as digitalizadas do EXP-017, uma vez.
* Custo: 3 rodadas × ~20 min, depois da cadeia EXP-019 → EXP-018.

## Tarefas

- [x] **T001** Harness (cópia do EXP-019) com a altura no quadrilátero; testes com linhas fictícias inclinadas.
- [x] **T002** Rodar os três conjuntos; pontuar; relatório; registrar no ADR-008.
