# Feature Specification: F0.12.04 — Feeds RSS, Atom e JSON

**Feature Branch**: `117-feeds`

**Created**: 2026-11-15

**Status**: Concluída em 2026-11-15

**Input**: Item "feeds RSS/Atom/JSON" do `docs/contexto/ROADMAP-0.12.md` (depende da F0.12.02). Quarta feature do 0.12.
**Sem migração.**

---

## 1. Contexto (auditoria de 2026-11-15, só código)

| Ponto | Situação | Onde |
|---|---|---|
| Conteúdo público | Só os **estudos publicados na web** (F0.12.02), disponíveis (fora da lixeira, livro ativo, conta ativa) | `services/public_study_service.py` (`list_available`) |
| HTML seguro | Markdown restrito com escape primeiro | `services/public_markdown.py` |
| Rotas do servidor | `robots.txt`, `sitemap.xml`, `security.txt`, manifesto; `/compartilhado/{id}` | `routers/seo.py`, `routers/public_studies.py` |
| Feeds | **Não existem** | — |

**Decisão:** feeds **da instalação**, só com o que já é público (os estudos publicados); nada de feed por usuário (o
nome de usuário nunca aparece nas páginas públicas, e criar um identificador público novo seria outra decisão).

---

## 2. User Stories

### US1 — Acompanhar os estudos publicados num leitor de feeds (P1)

**Acceptance**:
1. Três endereços públicos, sem login, com os **50 estudos publicados mais recentes** (pela data de publicação):
   - `/feed.xml` — **RSS 2.0** (`application/rss+xml`);
   - `/feed.atom` — **Atom 1.0** (`application/atom+xml`);
   - `/feed.json` — **JSON Feed 1.1** (`application/feed+json`).
2. Cada item: título, link para `/compartilhado/<id>` (com `APP_BASE_URL`), data de publicação e de atualização, autor
   (nome de exibição), resumo (começo do texto) e o **conteúdo em HTML** das seções, gerado pelo mesmo Markdown
   restrito da página pública (só o que a página já mostra).
3. O feed traz o título "Leitorum — estudos publicados", o endereço do site e a data do item mais novo.
4. Sem estudos publicados: feed válido e vazio.

### US2 — Descoberta e uso (P2)

**Acceptance**:
1. A página pública de cada estudo anuncia os três feeds (`<link rel="alternate" type="…">`).
2. Em Ajustes → "Publicados na web", os três endereços com "Copiar".
3. Cabeçalhos: `Cache-Control: public, no-cache` (despublicar sai do feed na próxima leitura) e `ETag`; pedido com o
   mesmo `ETag` recebe **304** (leitores de feed economizam banda). `robots.txt` lista os feeds como permitidos.

### Edge Cases

- Estudo despublicado, na lixeira, livro na lixeira ou conta desativada: sai do feed (mesma regra da página).
- Menção a estudo não publicado: só texto (regra da F0.12.02).
- Caracteres especiais e `]]>` no texto: escapados pelo gerador de XML (nunca concatenação de texto cru).

---

## 3. Requirements

- **FR-001**: `services/feed_service.py`: `feed_items(session, limit=50)` (a partir de `list_available`), `build_rss`,
  `build_atom` (com `xml.etree.ElementTree`) e `build_json_feed` (com `json`), além do `ETag` (hash do corpo).
- **FR-002**: `routers/feeds.py`: `GET` (e `HEAD`) `/feed.xml`, `/feed.atom`, `/feed.json`, com 304 por `If-None-Match`.
- **FR-003**: `public_study_service.render_page` com os `<link rel="alternate">`; `seo_service.generate_robots_txt` com
  `Allow` para os feeds.
- **FR-004**: `components/settings/PublishedStudiesCard.vue` com os endereços dos feeds e "Copiar".
- **FR-005**: Versão `0.12.0-alpha.4` e F0.12.04 marcada na linha do tempo.

## 4. Success Criteria

- **SC-001**: Testes: os três feeds com estudos fictícios publicados (só os disponíveis, ordem, limite, campos), XML bem
  formado e com os elementos obrigatórios de RSS 2.0 e Atom 1.0 (`id`, `updated`, `title`, `link`), JSON Feed com
  `version` 1.1, `items[].id/url/content_html`; texto com `<script>`, `&` e `]]>` escapado; feed vazio; despublicar tira o
  item; `ETag` e 304; nenhum campo privado (notas, fichamento, e-mail, nome de usuário) no conteúdo.
- **SC-002**: Navegador: abrir os três feeds; links na página pública e em Ajustes.
- **SC-003**: Build e testes novos e vizinhos; versão `alpha.4`; commit; levar ao `main`.

## 5. Fora do escopo

- Feed por autor, por livro ou por conceito; feed das sínteses.
- WebSub/PubSubHubbub e notificação ativa a leitores.
