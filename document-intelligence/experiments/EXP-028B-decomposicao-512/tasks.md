# Tarefas: EXP-028B — De onde vem o erro: caixas ou leitura (em imagens de 512 px)

**Entrada:** [spec.md](./spec.md) e [plan.md](./plan.md). Sem tarefa do usuário, sem download, sem treino.

- [x] T001 Testes que falham primeiro (`tests/test_exp028b.py`): imagem fictícia com linhas desenhadas e caixas
  conhecidas; leituras A/B/C geram os arquivos esperados; decomposição com textos fictícios dá as partes certas.
- [x] T002 `read_boxes.py` no ambiente do motor: leituras A, B e C das 4 páginas; rodar duas vezes e conferir
  que dá o mesmo resultado.
- [x] T003 `decompose.py`: CER de página A/B/C, partes (detecção, ordem, leitor), CER por linha em B, custo da
  resolução (A em 512 px × 69,8 % nas originais).
- [x] T004 `report.md` só com números (H1–H3); benchmark versionado; registrar no `CLAUDE.md` e no roadmap
  (inclusive a mudança de ordem da F-DI-13.02); commit `EXP-028B(document-inteligence) …`.

## Registro da execução (2026-11-20)

* **T001:** 3 testes (decomposição com textos fictícios, marcas da referência retiradas, leitor do produto
  rodando sobre caixas dadas numa página fictícia, duas rodadas iguais). Achado do teste: trocar a ordem de
  duas linhas pode custar mais que perder uma; a decomposição é um caminho e uma parte pode sair negativa.
* **T002:** leituras A, B e C nas 4 páginas, duas rodadas idênticas; 62 linhas nas caixas do autor, 65 nas do
  produto.
* **T003/T004:** A 64,3 %, C 53,4 %, B 50,9 %: detecção 10,9 pontos, ordem 2,5, leitor 50,9. Custo da
  resolução −5,5 pontos (512 px melhor que a leitura das originais, que tem bem menos texto). Benchmark
  `BENCHMARK-20261120-exp-028b.json` (só números; maior texto do arquivo: 23 caracteres).

