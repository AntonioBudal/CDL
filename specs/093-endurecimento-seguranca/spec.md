# Feature Specification: F0.10.02 — Endurecimento de Segurança e Privacidade Verificável

**Feature Branch**: `093-endurecimento-seguranca`

**Created**: 2026-11-01

**Status**: Concluída em 2026-11-01.

**Input**: seção 2.2 do plano mestre de 2026-11-01 (OWASP ASVS L2, LGPD, "Confiança Verificável") e os itens 1 a
7 da auditoria de segurança do mesmo dia. Esta feature vem antes do painel de Sistema (F0.10.03) e da seção de
confiança da landing, para que essas telas só afirmem o que já é verdade.

---

## 1. Contexto (auditoria de 2026-11-01)

**Já existe:** Argon2 para senhas, cookies HttpOnly e SameSite=Lax, limite de tentativas e bloqueio de conta, CSP,
`nosniff`, X-Frame-Options, Permissions-Policy, Markdown com `html: false` mais sanitização, snippets de busca
escapados antes de marcar os termos, consultas pelo ORM, estado anti-CSRF no OAuth do Google, exclusão permanente
de conta e exportação completa.

**Lacunas que esta feature fecha:**

| # | Lacuna | Onde está hoje |
|---|---|---|
| 1 | CSP libera `fonts.googleapis.com`/`fonts.gstatic.com` (as fontes são locais) e `img-src https:` (qualquer imagem externa num Markdown vira pixel de rastreamento) | `backend/app/core/security_headers.py` |
| 2 | `script-src 'unsafe-inline'`, exigido pelo bootstrap de aparência injetado inline no `index.html` | plugin `appearance-before-paint` em `frontend/vite.config.ts` |
| 3 | Domínios do Google na CSP mesmo quando o login com Google está desligado | `security_headers.py` (política fixa) |
| 4 | `Referrer-Policy: strict-origin-when-cross-origin`; o plano mestre pede `same-origin` | `security_headers.py` |
| 5 | `X-Robots-Tag: noindex` só em `/api`, `/dashboard`, `/livros`, `/admin` e `/estudos/`; faltam `/destaques`, `/revisao`, `/inbox`, `/ajustes`, `/amigos`, `/lixeira`, `/importar` e os aliases | `security_headers.py` |
| 6 | Proteção contra CSRF só por SameSite=Lax; nenhuma conferência de `Origin` | — |
| 7 | Sem `/.well-known/security.txt` (RFC 9116) | — |
| 8 | Exclusão permanente não apaga fisicamente: o SQLite deixa o conteúdo nas páginas livres e no WAL | `backend/app/db/session.py`, `services/trash_service.py`, `services/account_service.py` |

---

## 2. User Scenarios & Testing *(mandatory)*

### User Story 1 — Nenhuma conexão externa que o leitor não escolheu (Priority: P1)

Como leitor, quero que a aba Rede do navegador mostre só o meu servidor, a menos que eu use o login com Google.

**Independent Test**: com `GOOGLE_CLIENT_ID` vazio, a CSP de qualquer resposta não cita nenhum domínio externo;
com ele definido, cita só `accounts.google.com`.

**Acceptance Scenarios**:

1. **Given** o login com Google desligado, **When** qualquer página carrega, **Then** a CSP tem `script-src 'self'`,
   `connect-src 'self'`, `frame-src 'self'`, `img-src 'self' data: blob:` e `font-src 'self'`, sem domínio externo.
2. **Given** o login com Google ligado, **When** a página carrega, **Then** só `https://accounts.google.com` é
   acrescentado a `script-src`, `connect-src` e `frame-src`.
3. **Given** um estudo com `![](https://exemplo.com/x.png)`, **When** é exibido, **Then** o navegador não busca a
   imagem (bloqueio da CSP); imagens enviadas ao Leitorum continuam aparecendo.

### User Story 2 — Nenhum script inline (Priority: P1)

Como mantenedor, quero tirar `'unsafe-inline'` de `script-src` sem perder a aplicação do tema antes da primeira
pintura.

**Independent Test**: o `index.html` do build não tem `<script>` executável inline; o tema salvo aparece sem
"piscar" o tema padrão.

**Acceptance Scenarios**:

1. **Given** o build, **When** se lê `dist/index.html`, **Then** o bootstrap é um `<script src="/appearance-bootstrap.js">`
   clássico (bloqueante) no `<head>`, e o único outro `<script>` inline é o JSON-LD (`type="application/ld+json"`,
   que não executa).
2. **Given** um leitor com tema escuro salvo, **When** recarrega a página, **Then** o tema escuro está aplicado antes
   do primeiro quadro, como hoje.
3. **Given** o servidor de desenvolvimento do Vite, **When** roda, **Then** o bootstrap continua inline (a CSP do
   backend não vale ali).

### User Story 3 — Áreas privadas fora dos buscadores (Priority: P1)

Como leitor, quero que nenhuma tela privada seja indexada, mesmo as que ainda não existem.

**Independent Test**: só `/`, `/sobre`, `/apoie`, `/compartilhado/*`, `/robots.txt`, `/sitemap.xml` e
`/.well-known/*` respondem sem `X-Robots-Tag: noindex, nofollow`.

**Acceptance Scenarios**:

1. **Given** `/destaques`, `/revisao`, `/inbox`, `/ajustes`, `/login`, `/@usuario` ou uma rota nova, **When**
   respondem, **Then** trazem `X-Robots-Tag: noindex, nofollow`.
2. **Given** `/`, `/sobre` ou `/compartilhado/12`, **When** respondem, **Then** não trazem `X-Robots-Tag`.

### User Story 4 — Pedidos de outro site são recusados (Priority: P1)

Como leitor autenticado, quero que um site malicioso não consiga alterar os meus dados usando o meu cookie.

**Independent Test**: um `POST` para `/api/...` com `Origin: https://malicioso.example` recebe 403; o mesmo pedido
sem `Origin` (cliente de testes, scripts locais) ou com a origem do próprio servidor passa.

**Acceptance Scenarios**:

1. **Given** `POST`, `PUT`, `PATCH` ou `DELETE` em `/api/*` com `Origin` diferente do host do pedido, de
   `X-Forwarded-Host` e das origens confiáveis, **When** chega ao servidor, **Then** a resposta é 403 com
   `{"detail": "Origem do pedido não autorizada."}` e nada é gravado.
2. **Given** o acesso pelo celular via Tailscale (com ou sem proxy HTTPS na frente), **When** o leitor salva um
   estudo, **Then** o pedido passa (o `Origin` bate com o `Host` ou com o `X-Forwarded-Host`).
3. **Given** um pedido sem `Origin` e com `Sec-Fetch-Site: cross-site`, **When** chega, **Then** é recusado; sem
   `Origin` e sem `Sec-Fetch-Site`, passa.
4. **Given** `GET`, `HEAD` ou `OPTIONS`, **When** chega, **Then** a conferência não se aplica.

### User Story 5 — Contato de segurança público (Priority: P2)

Como pesquisador de segurança, quero saber como relatar uma falha.

**Independent Test**: `GET /.well-known/security.txt` responde 200 em `text/plain` com `Contact:` e `Expires:`
válidos (RFC 9116).

**Acceptance Scenarios**:

1. **Given** nenhuma configuração, **When** se pede o arquivo, **Then** `Contact:` aponta para
   `https://github.com/AntonioBudal/CDL/security/advisories/new` e `Expires:` fica a até 365 dias no futuro.
2. **Given** `LEITORUM_SECURITY_CONTACT` definido, **When** se pede o arquivo, **Then** `Contact:` usa esse valor.

### User Story 6 — Excluir é apagar de verdade (Priority: P1)

Como leitor, quero que, ao excluir permanentemente um item ou a conta, o conteúdo não fique recuperável no arquivo
do banco.

**Independent Test**: num banco descartável, depois de criar um estudo com um texto-sentinela fictício e
excluí-lo permanentemente, o texto não aparece nos bytes do `.db` nem do `-wal`.

**Acceptance Scenarios**:

1. **Given** qualquer conexão nova, **When** é aberta, **Then** `PRAGMA secure_delete` vale 1.
2. **Given** exclusão permanente de livro ou estudo, esvaziar a lixeira, expurgo de 30 dias ou exclusão de conta,
   **When** termina, **Then** roda `PRAGMA wal_checkpoint(TRUNCATE)` e o sentinela some do `.db` e do `-wal`.

### Edge Cases

- **Backups**: cópias feitas antes da exclusão continuam com o conteúdo até serem rotacionadas. A feature não mexe
  em backups; isso é registrado como limitação (e vira texto honesto no painel de Sistema da F0.10.03).
- **Checkpoint ocupado**: com leitores abertos, o `TRUNCATE` pode não completar; a exclusão não falha por isso, e o
  servidor registra o resultado em log (sem conteúdo).
- **Imagens externas já escritas em estudos**: deixam de carregar. É a intenção da CSP; o caminho é enviá-las pela
  área de imagens. O conteúdo do estudo não é alterado.
- **Proxy na frente**: `X-Forwarded-Host` só é aceito como alternativa ao `Host`, nunca para liberar origem
  externa; origens extras vêm de `LEITORUM_TRUSTED_ORIGINS` e de `CADERNO_CORS_ORIGINS`.
- **Futuros receptores (KOReader, Readest, no Roadmap 0.11)**: autenticam por token e virão com isenção explícita
  da conferência de origem; não há isenção nesta feature.
- **`style-src 'unsafe-inline'` permanece**: Vue aplica estilos dinâmicos e há atributos `style` nos templates;
  o risco de injeção de estilo é baixo com o HTML do Markdown desligado. Registrado como pendência conhecida.

---

## 3. Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: A CSP é montada por função: base `default-src 'self'; script-src 'self'; style-src 'self'
  'unsafe-inline'; font-src 'self' data:; img-src 'self' data: blob:; connect-src 'self'; frame-src 'self';
  object-src 'none'; frame-ancestors 'self'; base-uri 'self'; form-action 'self'`.
- **FR-002**: Com `is_google_auth_enabled()`, `https://accounts.google.com` entra em `script-src`, `connect-src` e
  `frame-src` (e em nenhum outro lugar); sem ele, nenhum domínio externo aparece.
- **FR-003**: O build gera `dist/appearance-bootstrap.js` (catálogo de fontes mais o código atual) e o `index.html`
  o referencia por `<script src>` clássico no `<head>`; no `vite dev`, o bootstrap segue inline.
- **FR-004**: `Referrer-Policy: same-origin`.
- **FR-005**: `X-Robots-Tag: noindex, nofollow` em toda resposta, exceto nas rotas públicas: `/`, `/sobre`,
  `/apoie`, prefixo `/compartilhado/`, `/robots.txt`, `/sitemap.xml` e prefixo `/.well-known/`.
- **FR-006**: Middleware de origem: em `POST`, `PUT`, `PATCH` e `DELETE` sob `/api/`, recusa com 403 quando
  `Origin` existe e não bate com o `Host`, com o `X-Forwarded-Host` nem com as origens confiáveis
  (`CADERNO_CORS_ORIGINS` e `LEITORUM_TRUSTED_ORIGINS`); sem `Origin`, recusa só se `Sec-Fetch-Site` for
  `cross-site` ou `same-site`.
- **FR-007**: `GET /.well-known/security.txt` (RFC 9116) com `Contact`, `Expires` (data de hoje + 365 dias, ISO
  8601 em UTC), `Preferred-Languages: pt, en` e `Canonical` montado com a origem do pedido.
- **FR-008**: `PRAGMA secure_delete=ON` em toda conexão do engine.
- **FR-009**: `PRAGMA wal_checkpoint(TRUNCATE)` depois do commit em `permanent_delete_book`,
  `permanent_delete_study`, `empty_trash`, `purge_expired_trash` e `delete_account_permanently`; falha do
  checkpoint é registrada em log e não desfaz a exclusão.
- **FR-010**: Nenhum dado real é lido nos testes; o sentinela é fictício e o banco é descartável (`tmp_path`).
- **FR-011**: Nada muda no fluxo de login local, na sessão, nas rotas ou no esquema do banco (sem migração).

### Key Entities

Nenhuma nova. Muda a configuração da conexão SQLite (pragmas), não o esquema.

---

## 4. Success Criteria *(mandatory)*

- **SC-001**: Testes de backend cobrem a CSP com e sem Google, `Referrer-Policy`, a lista de rotas públicas do
  `X-Robots-Tag`, os 4 casos da US4, o `security.txt` e o sentinela da US6.
- **SC-002**: `dist/index.html` sem `<script>` executável inline (teste de frontend sobre o plugin e conferência do
  build).
- **SC-003**: No navegador (servidor de validação), a aba Rede de `/livros` e `/` mostra só `localhost:8010`, o
  console não registra violação de CSP, e o tema salvo aparece sem piscar.
- **SC-004**: Salvar um estudo, excluir para a lixeira e restaurar funcionam pelo navegador com a conferência de
  origem ativa.
- **SC-005**: `npm run build` passa (regra das 5 features: as suítes completas rodam no marco da 5ª feature, ou
  antes se algo desta feature exigir).

---

## 5. Fora do escopo

- Trocar o sanitizador de lista de bloqueio por lista de permissão (com `html: false`, o risco atual é baixo);
  pendência para uma feature própria.
- Remover `style-src 'unsafe-inline'`.
- Tokens anti-CSRF por formulário (a conferência de origem mais SameSite=Lax cobre o modelo atual).
- Painel de Sistema com hash do build e integridade (F0.10.03) e a seção de confiança da landing (F0.10.08).
- Limpeza de backups antigos.

## 6. Assumptions

- O acesso pelo celular usa o mesmo host do servidor ou um proxy que preenche `X-Forwarded-Host`; outros arranjos
  são cobertos por `LEITORUM_TRUSTED_ORIGINS`.
- O `public/appearance.js` não é referenciado por nenhum arquivo; não é tocado aqui.

## 7. Achado registrado (fora do escopo)

O `sitemap.xml` (`seo_service.get_public_sitemap_items`) e o `robots.txt` anunciam `/compartilhado/{id}`, e o
JSON-LD de artigo usa o mesmo caminho, mas o router do frontend não tem essa rota: os links caem na página 404. A
correção pertence à feature "Cadernos públicos indexáveis" do Roadmap 1.0. Aqui o prefixo só entra na lista de
rotas públicas do `X-Robots-Tag`, o que é inofensivo enquanto a rota não existe.
