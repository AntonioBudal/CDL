# Tarefas: F-DI-13.01 — Ferramenta de caixas e linhas

**Entrada:** [spec.md](./spec.md) e [plan.md](./plan.md). Sem modelo novo, sem dependência nova, sem mudança fora
de `document-intelligence/`.

- [x] T001 Schema `di-annotation/1` e `store.py` (validação, `$` equilibrado, `line_id` estável, hashes, versão,
  gravação atômica); testes que falham primeiro em `tests/tools/test_anotar.py` com páginas fictícias.
- [x] T002 `prepare.py` (ambiente do motor): foto → JPEG de trabalho orientado + caixas e texto do motor;
  conferência do hash contra `splits/pages-sha256.json`; retomável. Testado com fotos fictícias.
- [x] T003 `server.py`: rotas da API, só `127.0.0.1`, recusa de `../` e de foto sem hash conferido; testes de
  rota em processo.
- [x] T004 Interface — caixas: foto com zoom e arrasto, criar/ajustar (4 cantos)/apagar, origem, ordem.
- [x] T005 Interface — texto: recorte acima do campo, `Enter` para a próxima, `$…$`, rascunho importado com
  sobras e destaque de divergência, regra "escreva o que está no papel".
- [x] T006 2ª passada (revisão e cega), estado por página na lista, tempo ativo por passada.
- [x] T007 Conferência no navegador com páginas fictícias (SC-004); `uv run pytest` e `uv run ruff check .`
  (SC-002, SC-003); `README.md` da ferramenta.
- [x] T008 Registrar no `CLAUDE.md` do subprojeto e no roadmap; commit
  `F-DI-13.01(document-inteligence) ferramenta de caixas e linhas`.
- [ ] T009 (com o usuário, quando as fotos voltarem) anotar 1 página real e medir a SC-001 (≤ 10 min);
  só o tempo e o resultado do schema vão para o registro, nunca o conteúdo.

## Registro da execução (2026-11-20)

* **T001–T003:** `store.py` (schema, `$`, `line_id`, hashes, versão, gravação atômica), `prepare.py` (hash →
  `pNN`, orientação EXIF, caixas do motor, retomável) e `server.py` (só `127.0.0.1`, recusa de `Host` de fora,
  caminhos com `..` e foto sem hash conferido). `tests/tools/test_anotar.py`: 34 testes com páginas fictícias,
  1 deles roda o `prepare.py` no ambiente do motor (pula se o ambiente não existir).
* **T004–T006:** interface em `static/` (canvas, sem framework, sem CDN; CSP só `'self'`).
* **T007:** conferido no navegador com 3 "fotos" fictícias (pauta + rabiscos, uma com EXIF de rotação), caixas
  iniciais do motor real: criar, ajustar canto, apagar (o id `L010` apagado não volta: `next_line_id` 11),
  reordenar, caixas prontas, 1ª passada com `Enter`, `Ctrl+M` e `$` desequilibrado bloqueado, rascunho importado
  com sobras e destaque de divergência, 2ª passada cega (sem rascunho nem sobras), linha vazia recusada, tema
  claro e escuro; arquivo gravado válido no schema e com `content_sha256` conferido. Achados e corrigidos na
  conferência: canvas medido antes do aviso do teste congelado aparecer (cliques deslocados na vertical; agora
  com `ResizeObserver`), barra do alto que quebrava a linha ao mostrar "não gravada", edição feita durante uma
  gravação em andamento (agora regrava em seguida) e área de rascunho visível na 2ª passada.
  `uv run pytest`: 273 passaram; `uv run ruff check .`: limpo.
* **T009** fica aberta até as fotos voltarem para `dataset/raw/exp-027/fotos/`.

## Fotos do teste congelado (2026-11-20)

* As 20 fotos do teste congelado chegaram como PNG de até 512 px (as originais não estão disponíveis); o usuário
  decidiu usá-las assim. O registro de hashes do EXP-027 não tinha as fotos reais (só 2 entradas sintéticas, agora
  retiradas): `register.py` registrou as 20 pela ordem de horário informada pelo usuário, com `low_resolution` e a
  origem, e a ferramenta mostra o aviso. +2 testes (`register`, aviso): 36 na ferramenta.

