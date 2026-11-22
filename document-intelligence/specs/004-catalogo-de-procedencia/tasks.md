# Tarefas: F-DI-13.03 — Catálogo de procedência (E2)

**Entrada:** [spec.md](./spec.md) e [plan.md](./plan.md).

- [x] T001 Adicionar Pillow ao `pyproject.toml` e ao registro de licenças.
- [x] T002 Testes que falham primeiro (`tests/tools/test_catalogo.py`, dados fictícios): fontes, itens,
  armazenamento por conteúdo, reimportação idempotente, bloqueio, pendente sem arquivo, revisão por fonte,
  rejeição que apaga e contamina, ciclos de experimento × produto, conferência de promoção, tetos, integridade,
  resumo do conteúdo de treino sem texto.
- [x] T003 `tools/catalogo/`: esquema, API Python e comandos (`fonte`, `ingerir`, `pendentes`, `revisar`,
  `ciclo`, `promover-conferir`, `resumo-treino`, `uso`, `verificar`).
- [x] T004 Importar as amostras aprovadas do EXP-043 (SC-002) para `D:\Leitorum-DI\` e conferir as contagens.
- [x] T005 `uv run pytest`, `uv run ruff check .`; README da ferramenta; `CLAUDE.md`, estratégia (E2) e roadmap;
  commit `F-DI-13.03(document-inteligence) catálogo de procedência`.

## Registro da execução (2026-11-22)

* **T001:** Pillow 13.0.0 (MIT-CMU, publicada em 2026-10-16) no `pyproject.toml` e no registro de licenças.
* **T002/T003:** `tools/catalogo/` (esquema SQLite, armazenamento por conteúdo, API e comandos);
  `tests/tools/test_catalogo.py` com 20 testes (inclusive rejeição que apaga, bloqueia e contamina, ciclo de
  produto só com `APPROVED`, tetos, integridade, importador idempotente). Dois ajustes na execução: o WebP não
  tem modo de 1 canal (trocado por PNG, 60× mais rápido) e um commit por item era lento no HD (lotes de 500 e
  totais de espaço em memória: de 45 para 9 ms por linha).
* **T004:** amostras aprovadas do EXP-043 importadas em `D:\Leitorum-DI\`: 16 fontes, **7.709 linhas**, criadas =
  linhas únicas de cada manifesto em todas as fontes (no POPP, 46 linhas repetidas na amostra reconhecidas como
  existentes), nenhuma recusa; reimportação cria 0; integridade sem problema; 391 MB (~51 KB por linha);
  nenhum pendente (as amostras pendentes já tinham sido apagadas no EXP-043).
* **T005:** `uv run pytest` 296 passaram; `uv run ruff check .` limpo; README da ferramenta.

