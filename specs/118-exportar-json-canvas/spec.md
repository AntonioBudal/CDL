# Feature Specification: F0.12.05 — Exportar o livro em JSON Canvas

**Feature Branch**: `118-exportar-json-canvas`

**Created**: 2026-11-15

**Status**: Concluída

**Input**: Item "quadro espacial com exportação JSON Canvas" do `docs/contexto/ROADMAP-0.12.md`. **Decisão do usuário
(2026-11-15): só a exportação**, sem refazer o quadro na tela. Quinta feature do 0.12 (fecha o lote: suítes
completas). **Sem migração.**

---

## 1. Contexto (auditoria de 2026-11-15)

| Ponto | Situação | Onde |
|---|---|---|
| Quadro na tela | **Removido** em 2026-10-12 (commit `7398da2`, ~9 mil linhas: quadro, mapa e árvore); o `ROADMAP-0.9` registrou que não volta | `docs/contexto/ROADMAP-0.9.md` |
| Dados que sobraram | Posição/tamanho/cor de cada estudo no quadro (`study_canvas_nodes`), molduras (`canvas_frames`: título, cor, posição, tamanho) e relações entre estudos (`study_relations`: tipo e descrição) | `models/study_canvas_node.py`, `canvas_frame.py`, `study_relation.py` |
| Exportar | Livro e estudo em Markdown/TXT pelo modal "Exportar anotações" | `components/ExportModal.vue`, `services/export_service.py` |

**Formato:** [JSON Canvas 1.0](https://jsoncanvas.org/) (aberto; usado pelo Obsidian e outros): `{"nodes": [...],
"edges": [...]}`. Nó: `id`, `type` (`text`, `file`, `link`, `group`), `x`, `y`, `width`, `height` (inteiros), `color`
opcional (`"1"`–`"6"` ou `#RRGGBB`); `text` traz Markdown; `group` traz `label`. Aresta: `id`, `fromNode`, `toNode`,
`fromSide`/`toSide` opcionais, `toEnd` (padrão `arrow`), `label` e `color` opcionais.

---

## 2. User Stories

### US1 — Levar o livro para um quadro (P1)

**Acceptance**:
1. No modal "Exportar anotações" do **livro**, um formato novo: **"JSON Canvas (Obsidian)"** → baixa
   `<título do livro>.canvas`.
2. **Cada estudo** (fora da lixeira) vira um nó de **texto**: `## Título` + o **Resumo** (ou a primeira seção
   preenchida), sem notas pessoais nem fichamento; altura estimada pelo tamanho do texto.
3. **Relações** entre estudos do livro viram **setas** com rótulo do tipo ("Complementa", "Contradiz", "Depende de",
   "Mesmo tema", "Desdobramento de", "Relacionado com") e a descrição, se houver.
4. **Posições:** estudos com posição salva no quadro antigo mantêm `x`, `y`, `width`, `height` e cor; as molduras
   salvas viram **grupos** com o título e a cor. Estudos sem posição são organizados automaticamente: **uma coluna por
   capítulo**, cada capítulo num grupo com o nome do capítulo, colocados à direita do que já tinha posição.
5. Cores: as do quadro antigo convertidas para as 6 cores do formato (vermelho 1, laranja 2, amarelo 3, verde 4,
   ciano 5, roxo 6); cor desconhecida fica sem cor.

### Edge Cases

- Livro sem estudos: arquivo válido com `nodes` e `edges` vazios.
- Relação com um dos estudos na lixeira ou em outro livro: não entra.
- Texto com `"`, `\`, quebras de linha e emoji: JSON válido (gerado com `json`, nunca por texto concatenado).
- Livro de outro leitor ou na lixeira: 404.

---

## 3. Requirements

- **FR-001**: `services/json_canvas_export.py`: `build_book_canvas(session, user_id, book_id) -> dict` (nós de estudo,
  grupos de moldura e de capítulo, arestas), `auto_layout`, mapa de cores, estimativa de altura; ids estáveis
  (`study-<id>`, `frame-<id>`, `chapter-<id>`, `relation-<id>`).
- **FR-002**: `GET /api/books/{id}/canvas/export` → `application/json`, `Content-Disposition` com o nome
  `<título>.canvas`.
- **FR-003**: `components/ExportModal.vue`: formato "JSON Canvas (Obsidian)" só no escopo livro; `api.exportBookCanvas`.
- **FR-004**: Versão `0.12.0-alpha.5` e F0.12.05 marcada; texto do `ROADMAP-0.12.md` atualizado para "exportar JSON
  Canvas" (sem quadro na tela).

## 4. Success Criteria

- **SC-001**: Testes: estrutura válida do JSON Canvas (campos obrigatórios, tipos, inteiros, ids únicos, toda aresta
  aponta para nós existentes); posições salvas preservadas; layout automático por capítulo sem sobreposição; molduras
  como grupos; relações como arestas com rótulo; estudo na lixeira fora; nada de notas/fichamento; escape de texto;
  livro vazio; isolamento (404).
- **SC-002**: Navegador (dados fictícios): baixar o `.canvas` pelo modal; conferir o JSON.
- **SC-003**: Fecho do lote: `npm test` e `pytest` completos (banco descartável); build; falha antiga em commit
  próprio; versão `alpha.5`; commit; levar ao `main`.

## 5. Fora do escopo

- Quadro espacial na tela (decisão da 0.9 mantida).
- Importar `.canvas` de volta; exportar sínteses ou o acervo inteiro como quadro.
- Nós de arquivo (`file`) apontando para `.md` de um cofre do Obsidian (cada estudo vai como texto, num arquivo só).
