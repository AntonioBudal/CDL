# Feature Specification: F0.12.02 — Estudos Publicados na Web (`/compartilhado/:id`)

**Feature Branch**: `115-estudos-publicados`

**Created**: 2026-11-14

**Status**: Concluída em 2026-11-14

**Input**: Item "cadernos públicos indexáveis (inclui criar a rota `/compartilhado/:id`)" do Roadmap **0.12**
(antigo 1.0; `docs/contexto/ROADMAP-0.12.md`) e HANDOFF §5. Segunda feature do 0.12, lote 1 (depois da F0.12.01,
versões). Rascunho escrito em 2026-11-14 como spec 114 e renumerado; **ainda não aprovado**. **Com migração (`0040`).**

---

## 1. Contexto (auditoria de 2026-11-14, só código)

| Ponto | Situação | Onde |
|---|---|---|
| "Público" hoje | `visibility = public` (estudo, ou livro com estudo em `inherit`) = **visível para qualquer pessoa com conta nesta instalação**; visitante sem login não lê nada (`can_read_study` exige usuário) | `services/sharing_service.py` |
| `/compartilhado/{id}` | **Não existe**. O sitemap já sabe montar essas URLs, mas está desligado (`PUBLIC_STUDY_PAGES_ENABLED = False`) | `services/seo_service.py` |
| Indexação | Cabeçalho `noindex` em tudo, exceto `/`, `/sobre`, `/apoie` e o prefixo `/compartilhado/` (já previsto) | `core/security_headers.py` |
| Renderização | O Markdown é renderizado só no navegador (Vue); o servidor não tem renderizador de Markdown nem biblioteca de limpeza de HTML | `frontend/src/services/markdown.ts` |
| Rotas do servidor | Roteadores vêm antes do *fallback* da interface, então uma rota `GET /compartilhado/{id}` do servidor tem prioridade | `main.py`, `frontend.py` |

**Decisão central (privacidade):** publicar na web é uma **escolha explícita por estudo** (`published_at`), separada da
visibilidade. Nada que hoje está "público" para a instalação passa a ser público na internet sem o dono pedir.

---

## 2. User Stories

### US1 — Publicar um estudo (P1)

**Acceptance**:
1. No estudo (painel de compartilhamento), o dono vê **"Publicar na web"** com um aviso do que sai: título, as **4
   seções** (Resumo, Explicação, Conceitos, Referências), a referência do livro e o nome de exibição do autor. **Não
   saem**: notas pessoais, fichamento da fonte, destaques, capítulo de outros estudos, e-mail ou nome de usuário.
2. Ao publicar, aparece o endereço `…/compartilhado/<id>` com **"Copiar link"** e **"Abrir"**; **"Despublicar"** tira
   do ar na hora (a página passa a responder 404 e sai do sitemap).
3. Estudo na lixeira, livro na lixeira ou conta desativada → página 404 (sem desfazer a escolha).
4. Em Ajustes → Privacidade, a lista **"Publicados na web"** mostra todos os publicados, com despublicar.

### US2 — Página pública (P1)

**Acceptance**:
1. `GET /compartilhado/<id>` (sem login) devolve **HTML gerado no servidor**, legível sem JavaScript: título, autor
   (nome de exibição), livro (título, autor, ano), as seções preenchidas, a referência ABNT e "Escrito no Leitorum".
2. Markdown das seções num renderizador **próprio e restrito**: tudo é escapado antes; depois só títulos, parágrafos,
   listas, citações, negrito, itálico, código e links `http(s)` (com `rel="nofollow ugc noopener"`). Imagens não saem
   (as do acervo são privadas).
3. Menções: `[[Título|id]]` vira link só se o estudo citado também estiver publicado; senão, só o texto. `[[conceito:X]]`
   vira só o termo. Trechos de cadernos de síntese não existem em estudos.
4. Metadados para buscadores e redes: `<title>`, `description` (começo do resumo), `canonical`, Open Graph e JSON-LD
   (`Article`); idioma `pt-BR`.
5. Cabeçalhos: sem `noindex` (o prefixo já é indexável); CSP sem script; `Cache-Control: public, no-cache` (o
   navegador sempre confere com o servidor; com `max-age=300`, previsto antes, uma página despublicada continuava
   aparecendo por até 5 minutos — achado na execução).

### US3 — Buscadores (P2)

**Acceptance**:
1. `robots.txt` passa a ter `Allow: /compartilhado/` e o `sitemap.xml` lista **só** os estudos publicados e
   disponíveis (`PUBLIC_STUDY_PAGES_ENABLED` vira consulta a `published_at`).
2. Aviso honesto no painel: a página só fica alcançável por quem está fora da rede se o Leitorum estiver exposto
   (domínio próprio ou Tailscale Funnel); o endereço usado é o de `APP_BASE_URL`.

### Edge Cases

- Despublicar e publicar de novo mantém o mesmo endereço (o id do estudo).
- Estudo sem nenhuma seção preenchida não pode ser publicado (422). Na prática não acontece: o banco já exige ao
  menos uma seção (`ck_studies_analysis_not_blank`); a guarda fica como reserva.
- Id inexistente, não publicado ou de conta bloqueada → mesma página 404 (não revela que existe).
- Celular: página pública de uma coluna, fonte confortável, sem rolagem lateral.

---

## 3. Requirements

- **FR-001**: Migração `0040_study_published_at`: `studies.published_at` (`DATETIME` anulável, `ADD COLUMN` simples) e
  índice `ix_studies_published_at`.
- **FR-002**: `services/public_markdown.py` (puro): `render_public_markdown(text, link_for_study)` com escape primeiro;
  `excerpt(text, 160)`.
- **FR-003**: `services/public_study_service.py`: `publish`, `unpublish`, `list_published(user)`,
  `get_public_study(id)` (regras de disponibilidade), `render_public_page(...)`.
- **FR-004**: Rotas: `POST/DELETE /api/studies/{id}/publication` (só o dono), `GET /api/studies/published`,
  `GET /compartilhado/{id}` (HTML, sem login); `seo_service` usa `published_at`.
- **FR-005**: Frontend: `components/sharing/PublishToWebCard.vue` no painel de compartilhamento do estudo;
  `components/settings/PublishedStudiesCard.vue` em Ajustes. Só tokens, `.quiet`, 44 px, contraste ≥ 4,5:1 nos 10
  temas.

## 4. Success Criteria

- **SC-001**: Testes do renderizador: escape de HTML/`<script>`/atributos, links só `http(s)`, `javascript:` recusado,
  listas, citações, títulos, código, menção a estudo publicado × não publicado, conceito.
- **SC-002**: Testes de API e página: publicar/despublicar (só o dono; outro leitor 404), estudo vazio recusado, página
  sem login com as 4 seções e **sem** notas/fichamento/destaques/e-mail/usuário, 404 para não publicado, lixeira, livro
  na lixeira e conta desativada; cabeçalhos (sem `noindex`, CSP, cache); `robots.txt` e `sitemap.xml` só com
  publicados.
- **SC-003**: Migração: `test_migration_matches_models` e upgrade/downgrade em banco descartável.
- **SC-004**: Navegador (dados fictícios): publicar pelo painel, abrir a página sem sessão (janela anônima simulada),
  despublicar e ver 404, lista em Ajustes; página pública em 375 e 1366 px; contraste da página e dos cartões.
- **SC-005**: Build e testes novos e vizinhos; versão sobe para **`0.12.0-alpha.2`** (`VERSION`, `package.json`,
  `package-lock.json`) e a F0.12.02 fica marcada como entregue em `data/versionHistory.ts` (regra do HANDOFF §2);
  commit; levar ao `main`. Migração não aplicada ao banco ativo.

## 5. Fora do escopo

- Publicar livros inteiros, cadernos de síntese ou perfis; página índice de todos os publicados.
- Comentários de visitantes; contagem de visitas.
- Expor o Leitorum à internet (domínio, Funnel): configuração do dono.
