# Tarefas: EXP-028A — Referência v3 linha a linha e piso de ruído humano

**Entrada:** [spec.md](./spec.md) e [plan.md](./plan.md).

## Fase 1 — preparar (sem o usuário)

- [x] T001 Testes que falham primeiro (`tests/test_exp028a.py`, páginas fictícias): rascunho por alinhamento,
  sorteios reproduzíveis, exportação v3, medidas H1–H4.
- [x] T002 `draws.py`: sortear 5 páginas para a 2ª passada cega e o `dev-val` (10 de 31); gravar manifestos com
  semente e hash **antes** de qualquer medida.
- [x] T003 `seed_drafts.py`: rascunho do Gemini alinhado às caixas nas 19 páginas sem 1ª passada; relatório só
  com contagens (palavras alinhadas, sobras por página).
- [x] T004 Ferramenta: modo "caixas rápidas" na explicação da etapa 1 (sem ajustar cantos) e marca das páginas
  da 2ª passada cega na lista.

## Fase 2 — anotação (o usuário, ~2,5 h)

- [ ] T005 1ª passada nas 19 páginas, com o caderno ao lado; conferir o tempo nas 5 primeiras (abandono se
  > 15 min/página).
- [ ] T006 2ª passada cega nas 5 páginas sorteadas, ≥ 2 dias depois da 1ª.

## Fase 3 — medir e registrar

- [ ] T007 `export_v3.py`: `referencia-v3/` e `splits/test-manifest-v3.json` (hashes).
- [ ] T008 `measure.py` (funções do `score.py` do EXP-027) contra a v3: H1–H4; `report.md` só com números.
- [ ] T009 Registrar no `CLAUDE.md` e no roadmap; commit `EXP-028A(document-inteligence) …`.

## Registro da execução

**Fase 1 (2026-11-20):**

* **T001:** `tests/test_exp028a.py`, 9 testes com páginas fictícias (alinhamento, sorteios congelados,
  rascunho pela ferramenta, exportação que recusa página incompleta, H1–H4). `export_v3.py` e `measure.py`
  ficaram prontos e testados para a fase 3.
* **T002:** sorteios gravados antes de qualquer medida, em `EXP-027-analise-50-paginas/splits/` (onde a
  ferramenta lê): 2ª passada cega `p14, p22, p27, p36, p38` (5 de 20; a p14 é também a página sem ancoragem no
  Gemini); `dev-val` `p03, p09, p12, p13, p29, p34, p39, p42, p47, p50` (10 de 31, todos os estratos), anotação
  pendente até haver imagens.
* **T003:** rascunho do Gemini alinhado às caixas nas 19 páginas sem 1ª passada (a p14 ficou de fora): 2.283
  palavras, 1.718 (75 %) casadas com uma palavra do motor, 565 levadas pela vizinha; 17 de 369 caixas sem
  rascunho.
* **T004:** ferramenta — marca "2ª cega" nas 5 páginas, 2ª passada abrindo no modo cego, aviso de espera de 2
  dias depois da 1ª, e o aviso de modo rápido de caixas nas páginas de imagem reduzida (+1 teste). Conferido no
  navegador só por estado da página (sem olhar imagem nem texto); a p14 não mudou.

**Ponto de controle da fase 2 (2026-11-20, 5 primeiras páginas, só números):**

* Tempo ativo (caixas + 1ª passada): p10 5,0 min, p11 10,9, p14 12,1 (rascunho do motor), p15 6,8, p16 1,8 —
  nenhuma acima do limite de abandono (15 min); seguir.
* Linhas sem confirmar na 1ª passada: p10 3 de 10, p11 2 de 20, p15 2 de 12 (estas 2 escritas só na 2ª
  passada). p15 e p16 receberam 2ª passada sem terem sido sorteadas (descartada da H2, que usa só as 5
  sorteadas).
* Três defeitos da ferramenta explicam isso, corrigidos: (1) a linha só conta com `Enter`, mas a tela só
  avisava das que faltavam depois de chegar ao fim — agora avisa sempre e a lista mostra `1ª 7/10`; (2) o modo
  da 2ª passada passava de uma página para outra (ficava "cego" depois de abrir uma sorteada) — agora é por
  página; (3) nada dizia que a 2ª passada era só para as sorteadas — agora há aviso. Na 1ª passada, uma linha
  sem 1ª mas com texto na 2ª abre com esse texto, para o autor confirmar.

