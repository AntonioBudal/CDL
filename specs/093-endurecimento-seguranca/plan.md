# Implementation Plan: F0.10.02 — Endurecimento de Segurança e Privacidade Verificável

**Branch**: `093-endurecimento-seguranca` | **Date**: 2026-11-01 | **Spec**: [spec.md](spec.md)

**Status**: Executado em 2026-11-01.

## Summary

Quatro frentes, todas sem migração:

1. **Cabeçalhos:** a CSP passa a ser montada por função (sem domínios de fontes, `img-src` só local, Google só
   quando o login com Google está ativo, `object-src 'none'`); `Referrer-Policy: same-origin`; `X-Robots-Tag`
   invertido para lista de rotas públicas.
2. **Sem script inline:** o plugin do Vite passa a emitir `appearance-bootstrap.js` no build e a referenciá-lo por
   `<script src>`; com isso sai `'unsafe-inline'` de `script-src`.
3. **Origem dos pedidos:** middleware novo recusa `POST`/`PUT`/`PATCH`/`DELETE` em `/api/` vindos de outra origem.
4. **Apagar de verdade:** `PRAGMA secure_delete=ON` em toda conexão e `wal_checkpoint(TRUNCATE)` depois das
   exclusões permanentes; mais `/.well-known/security.txt`.

## Technical Context

**Language/Version**: Python 3.13 (FastAPI, Starlette, SQLAlchemy 2); Vite 8 (plugin em `vite.config.ts`).

**Primary Dependencies**: as atuais; nenhuma nova.

**Storage**: SQLite em WAL; só pragmas de conexão, sem mudança de esquema.

**Testing**: `pytest` com `tmp_path` e `TestClient` (novos testes em `backend/tests/`); `node --test` para o plugin;
servidor de validação para aba Rede, console e tema.

**Target Platform**: servidor local no Windows, acessado pelo PC e pelo celular (rede local ou Tailscale).

**Constraints**: nenhum dado real; o banco ativo não é tocado; o login local e a sessão não mudam; o acesso pelo
celular não pode quebrar.

**Scale/Scope**: ~5 arquivos de backend, 1 do frontend, 3 testes novos de backend e 1 de frontend.

## Constitution Check

| Regra | Situação |
|---|---|
| Dados do usuário nunca lidos | OK: testes com sentinela fictício em `tmp_path`; navegador com o banco de validação |
| Banco ativo intocado, sem migração | OK: só pragmas, aplicados por conexão |
| Zero IA externa e telemetria; nada de CDN | Reforçado: a CSP passa a proibir domínios externos fora do login com Google |
| Testes a cada 5 features | Esta é a 2ª do lote; valida com `npm run build` e os testes novos (backend e frontend) |
| 1 feature = 1 commit, logo após o build | OK |

## Decisões técnicas

1. **CSP por função** (`security_headers.py`). `build_csp(google_enabled: bool) -> str`; o middleware chama
   `is_google_auth_enabled()` a cada pedido (a função só lê variável de ambiente, custo desprezível) para refletir a
   configuração sem reiniciar. `font-src` mantém `data:` porque algumas fontes de ícone podem vir embutidas.
2. **Bootstrap externo** (`vite.config.ts`). O plugin ganha dois modos:
   - `transformIndexHtml(html, ctx)`: com `ctx.server` (dev), injeta inline como hoje; no build, troca o marcador por
     `<script src="/appearance-bootstrap.js"></script>` (clássico, sem `defer`/`async`, portanto bloqueante e
     executado antes da primeira pintura, como o inline);
   - `generateBundle()`: emite o asset `appearance-bootstrap.js` com o mesmo conteúdo de hoje
     (`window.cadernoFontCatalog=…;` mais o código).

   O arquivo sai na raiz do `dist` e é servido pelo `register_frontend` com `Cache-Control: no-cache` (mesmo
   tratamento do `index.html`), então um build novo é visto de imediato.
3. **`X-Robots-Tag` por lista de permissão.** Conjunto exato `{"/", "/sobre", "/apoie", "/robots.txt",
   "/sitemap.xml"}` e prefixos `("/compartilhado/", "/.well-known/")`; tudo o mais recebe `noindex, nofollow`.
   Arquivos estáticos (`/assets/`, `/fonts/`) também recebem, o que é inofensivo.
4. **Middleware de origem** (`backend/app/core/origin_guard.py`, novo). Registrado logo depois do
   `SecurityHeadersMiddleware`, para que a resposta 403 também leve os cabeçalhos de segurança.
   - Métodos protegidos: `POST`, `PUT`, `PATCH`, `DELETE`; só sob `/api/`.
   - Com `Origin`: aceita se o `netloc` da origem for igual ao `Host`, ao `X-Forwarded-Host` (primeiro valor) ou a
     uma origem confiável (`get_cors_allowed_origins()` mais `LEITORUM_TRUSTED_ORIGINS`, separadas por vírgula).
     `Origin: null` é recusado.
   - Sem `Origin`: recusa se `Sec-Fetch-Site` for `cross-site` ou `same-site`; aceita se for `same-origin`, `none`
     ou ausente (o `TestClient`, `curl` e os scripts locais seguem funcionando).
   - Resposta de recusa: `JSONResponse(status_code=403, content={"detail": "Origem do pedido não autorizada."})`;
     log em nível `warning` com método, caminho e a origem recusada (nunca corpo nem cookies).
5. **`security.txt`** (`routers/seo.py`). Rota `GET /.well-known/security.txt`, `text/plain; charset=utf-8`:

   ```text
   Contact: <LEITORUM_SECURITY_CONTACT ou https://github.com/AntonioBudal/CDL/security/advisories/new>
   Expires: <hoje + 365 dias, AAAA-MM-DDT00:00:00Z>
   Preferred-Languages: pt, en
   Canonical: <origem do pedido>/.well-known/security.txt
   ```

   A configuração fica em `core/config.py` (`get_security_contact()`), no padrão das demais.
6. **Apagar de verdade** (`db/session.py` e serviços).
   - `_configure_connection` passa a executar também `PRAGMA secure_delete=ON` (fora de transação, como o
     `foreign_keys`). Com ele, o SQLite sobrescreve com zeros o conteúdo apagado nas páginas do banco.
   - O WAL ainda guarda as versões antigas das páginas até o checkpoint. Novo `checkpoint_after_purge(session)` em
     `services/persistence.py`: executa `PRAGMA wal_checkpoint(TRUNCATE)` depois do commit e registra em log o
     resultado `(busy, log, checkpointed)`, sem lançar erro.
   - Chamado no fim de `permanent_delete_book`, `permanent_delete_study`, `empty_trash`, `purge_expired_trash` e
     `delete_account_permanently`.
   - `VACUUM` não entra: bloqueia o banco e, com `secure_delete`, o conteúdo apagado já foi zerado.
7. **O que não muda:** `style-src 'unsafe-inline'`, o sanitizador e os backups (Fora do escopo e Edge Cases da
   spec).

## Arquivos e mudanças

| Arquivo | Mudança |
|---|---|
| `backend/app/core/security_headers.py` | `build_csp()`, `Referrer-Policy: same-origin`, lista de rotas públicas do `X-Robots-Tag` |
| `backend/app/core/origin_guard.py` (novo) | middleware de origem |
| `backend/app/core/config.py` | `get_trusted_origins()`, `get_security_contact()` |
| `backend/app/main.py` | registro do `OriginGuardMiddleware` |
| `backend/app/routers/seo.py` | rota `/.well-known/security.txt` |
| `backend/app/db/session.py` | `PRAGMA secure_delete=ON` |
| `backend/app/services/persistence.py` | `checkpoint_after_purge()` |
| `backend/app/services/trash_service.py`, `account_service.py` | chamada ao checkpoint depois das exclusões |
| `frontend/vite.config.ts` | bootstrap externo no build, inline no dev |
| `backend/tests/test_security_headers_and_csp.py` | atualizar as asserções antigas (Referrer-Policy e domínios de fontes, que esta feature muda de propósito) |
| `backend/tests/test_security_hardening.py` (novo) | CSP com e sem Google, `X-Robots-Tag`, origem, `security.txt` |
| `backend/tests/test_secure_delete.py` (novo) | pragma e sentinela no `.db` e no `-wal` |
| `frontend/tests/feature-093-bootstrap-externo.test.mjs` (novo) | plugin emite o arquivo e não deixa script inline |
| `caderno-leitura-0.1/docs/contexto/RETOMADA.md` | registro |

## Testes

- **CSP:** sem `GOOGLE_CLIENT_ID`, nenhum `https://` na política; com ele, só `https://accounts.google.com` e só nas
  três diretivas. Nenhum `'unsafe-inline'` em `script-src`.
- **Rotas públicas:** parametrizado com `/`, `/sobre`, `/apoie`, `/compartilhado/1`, `/robots.txt`,
  `/sitemap.xml`, `/.well-known/security.txt` (sem cabeçalho) e `/destaques`, `/revisao`, `/inbox`, `/ajustes`,
  `/login`, `/@alguem`, `/rota-que-nao-existe` (com cabeçalho).
- **Origem:** `POST` com origem externa (403 e nada gravado), com a própria origem (passa), com
  `X-Forwarded-Host` correspondente (passa), sem `Origin` e `Sec-Fetch-Site: cross-site` (403), sem nenhum dos dois
  (passa), `GET` com origem externa (passa), origem em `LEITORUM_TRUSTED_ORIGINS` (passa).
- **`security.txt`:** 200, `text/plain`, `Contact` padrão e configurado, `Expires` entre hoje e 365 dias.
- **Sentinela:** banco em `tmp_path`, estudo fictício com `"SENTINELA-093-FICTICIO"` repetido; exclusão
  permanente; os bytes do `.db` e do `-wal` não contêm o sentinela. Mesmo teste para esvaziar a lixeira e para a
  exclusão de conta. Controle: sem `secure_delete`, o sentinela aparece (prova de que o teste detecta).
- **Plugin:** importa a configuração do Vite, roda `transformIndexHtml` em modo build e em modo dev e confere a
  saída; confere que `generateBundle` emite `appearance-bootstrap.js` com `cadernoFontCatalog`.
- **Navegador:** aba Rede de `/` e `/livros` só com `localhost:8010`; console sem violação de CSP; tema salvo
  aplicado antes da pintura; salvar estudo, mandar para a lixeira e restaurar.

## Riscos

| Risco | Mitigação |
|---|---|
| Acesso pelo celular por proxy recusado pela conferência de origem | `X-Forwarded-Host` aceito; `LEITORUM_TRUSTED_ORIGINS` como saída; teste específico; o registro em log mostra a origem recusada |
| `Referrer-Policy: same-origin` atrapalhar o login com Google | O fluxo usa redirecionamento OAuth com `state` (não depende de `Referer`) e o botão GIS usa a origem do script; não há como testar sem `GOOGLE_CLIENT_ID`, então fica registrado para conferir no ambiente real |
| Bootstrap externo atrasar o tema | Script clássico no `<head>`, bloqueante, servido do próprio servidor; conferência visual de "sem piscar" |
| `wal_checkpoint(TRUNCATE)` lento ou ocupado | Só nas exclusões permanentes (raras); não lança erro; resultado em log |
| Teste antigo de cabeçalhos exige os valores velhos | Atualizado de propósito, com comentário citando a F0.10.02 |

## Project Structure

```text
specs/093-endurecimento-seguranca/
├── spec.md
├── plan.md        # este arquivo
└── tasks.md
```
