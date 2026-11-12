# Feature Specification: F0.11.09 — Receptor KOReader/Readest

**Feature Branch**: `111-receptor-koreader-readest`

**Created**: 2026-11-12

**Status**: Concluída em 2026-11-12

**Input**: Item "receptor KOReader/Readest" do Roadmap 0.11 no HANDOFF; a spec 093 já previa "receptores que
autenticam por token". Quarta feature do lote 2 do 0.11. **Com migração (`0038`).**

---

## 1. Contexto (auditoria de 2026-11-12: código e documentação pública dos dois leitores)

| Ponto | Situação | Onde |
|---|---|---|
| Importação de leitores | Kindle (`My Clippings.txt`) e Kobo (`KoboReader.sqlite`) por arquivo, para a Mesa, com prévia, livro sugerido e deduplicação | `services/ereader_import/`, `views/EreaderImportView.vue` (F0.11.03) |
| Autenticação | Só sessão por cookie (e `X-User-Id` em testes). **Não há token** para clientes externos | `dependencies.py` |
| Conferência de origem | Pedido sem `Origin` (aplicativo nativo) passa; com `Origin` de fora, 403 | `core/origin_guard.py` |
| **Readest** | Envia destaques ao **Readwise** com **URL própria configurável** ("Advanced → Custom URL"): `GET {base}/auth/` (espera 204) e `POST {base}/highlights/` com `Authorization: Token <token>` e `{"highlights": [{text, title, author, note, location, location_type, highlighted_at, color, source_type: "readest", category: "books", …}]}` | documentação e `ReadwiseClient.ts` do Readest |
| **KOReader** | O alvo Readwise do exportador tem a URL **fixa** (`readwise.io`); não serve. O exportador **JSON** grava um arquivo (`version: "json/1.0.0"`) com um livro (`title`, `author`, `entries`) ou vários (`documents: [...]`); cada entrada traz `text`, `note`, `page`, `chapter`, `time` (época Unix) | `plugins/exporter.koplugin/target/json.lua`, `clip.lua` do KOReader |

**Decisão:** dois caminhos, um por leitor, ambos caindo na **Mesa** pelo mesmo serviço da F0.11.03:
1. **Readest → receptor compatível com Readwise** (envio automático pelo próprio Readest), autenticado por **token de
   recepção** do leitor.
2. **KOReader → arquivo JSON do exportador**, na tela de importação de leitores (que passa a aceitar três formatos).

---

## 2. User Stories

### US1 — Token de recepção (P1)

**Acceptance**:
1. Em Configurações → **"Receber destaques"**: botão **"Gerar token"**. O token aparece **uma vez** (com "Copiar"),
   junto da URL para colar no Readest: `<endereço do Leitorum>/api/receptor/readwise/v2`.
2. Depois só se vê o começo do token (`lt_ab12…`), quando foi criado e o último uso. "Gerar outro" substitui o
   anterior (que para de funcionar na hora); "Revogar" apaga.
3. O servidor guarda só o **hash SHA-256** do token. Um token por leitor.

### US2 — Readest envia destaques para o Leitorum (P1)

**Acceptance**:
1. `GET /api/receptor/readwise/v2/auth/` com `Authorization: Token <token>` → **204**; token ausente ou errado → 401.
2. `POST /api/receptor/readwise/v2/highlights/` com o corpo do Readwise → cada destaque vira **captura na Mesa**:
   texto (+ "Nota: …"), indicação de origem "Readest · p. 12 · 12/11/2026"; livro **existente** quando título (e
   autor) batem com a regra da F0.11.03, senão **livro novo**. Reenvio do mesmo destaque não duplica.
3. Resposta 200 no formato do Readwise (lista por livro com `id`, `title`, `author`, `modified_highlights`), para o
   Readest aceitar.
4. Os dois caminhos aceitam com e sem a barra final; o `POST` não depende de cookie nem de `Origin` (isenção explícita,
   prevista na spec 093, só para `/api/receptor/`).
5. Limites: até 1000 destaques por pedido e 20 mil caracteres por texto/nota; acima disso, 413/422 sem gravar nada.

### US3 — KOReader pelo arquivo JSON do exportador (P1)

**Acceptance**:
1. A tela "Importar do Kindle ou Kobo" passa a se chamar **"Importar de leitor digital"** e aceita também o `.json`
   do exportador do KOReader (um livro ou vários), com a mesma prévia, escolha de livro e deduplicação.
2. Cada entrada vira captura com "KOReader · p. 12 · cap. Capítulo 1 · 12/11/2026"; `time` (época) vira a data.
3. JSON que não é do KOReader → mensagem clara ("Não reconheci este arquivo…").

### US4 — Instruções na tela (P2)

**Acceptance**:
1. A seção "Receber destaques" explica, em passos curtos: Readest (Configurações → Sincronizar → Readwise → Avançado
   → URL personalizada + token) e KOReader (Exportar destaques → JSON → importar o arquivo aqui), com link para a tela
   de importação.
2. Aviso honesto: o celular precisa alcançar o Leitorum (mesma rede ou Tailscale); a versão web do Readest não
   funciona (o navegador bloqueia por origem).

### Edge Cases

- Destaque sem texto, ou marcador de página do Readest ("Page 12", "Position …") sem nota: ignorado e contado como
  pulado.
- A seção fica em Configurações → **Leitura**; com o Readest ativo, os botões são "Gerar outro" e "Revogar" (o aviso
  de que o anterior para de valer fica no texto, para o botão caber em 375 px).
- Token revogado durante o uso: próximo pedido recebe 401.
- Conta desativada: token não autentica.
- Logs nunca registram token, corpo ou texto dos destaques (só contagens).
- Celular: seção em uma coluna; botões de 44 px; o token quebra linha sem rolagem lateral.

---

## 3. Requirements

- **FR-001**: Migração `0038_receiver_tokens`: tabela `receiver_tokens` (`user_id` PK → `users.id` `ON DELETE
  CASCADE`, `token_hash` único, `token_hint`, `created_at`, `last_used_at`), nomes pela convenção.
- **FR-002**: `services/receiver_tokens.py`: `issue_token`, `revoke_token`, `token_status`, `authenticate(raw)`
  (hash + comparação, atualiza `last_used_at`, recusa conta inativa). Rotas da conta: `GET/POST/DELETE
  /api/account/receiver-token`.
- **FR-003**: `routers/receiver.py`: `GET …/auth/`, `POST …/highlights/` (com e sem barra); `origin_guard` isenta só
  `/api/receptor/`; `services/ereader_import/readwise.py` converte o corpo em `EreaderParseResult(source="readest")`
  e `receive_parsed(...)` grava com livro sugerido ou novo.
- **FR-004**: `services/ereader_import/koreader.py` (puro): `parse_koreader_json(bytes)`; `detect_format` reconhece o
  JSON (`version` começando com `json/`).
- **FR-005**: Frontend: seção "Receber destaques" em Configurações (`ReceiverTokenCard.vue`), título e texto da tela de
  importação. Só tokens, `.quiet`, 44 px, contraste ≥ 4,5:1 nos 10 temas.

## 4. Success Criteria

- **SC-001**: Testes puros: JSON do KOReader (um livro, vários, entradas sem texto, `time`), corpo Readwise (campos,
  autor vazio, `location_type`), detecção de formato.
- **SC-002**: Testes de API: token (gerar, hash guardado, substituir, revogar, isolamento), `auth/` 204/401,
  `highlights/` grava na Mesa com livro existente/novo, reenvio sem duplicar, limites, sem `Origin` e com `Origin` de
  fora (passa pela isenção, mas sem cookie não autentica ninguém), conta inativa, token nunca nos logs.
- **SC-003**: Migração: `test_migration_matches_models` e teste de upgrade/downgrade em banco descartável.
- **SC-004**: Navegador (dados fictícios): gerar/copiar/revogar token, URL mostrada, importação do JSON do KOReader;
  um envio simulado no formato do Readest chega à Mesa; 1366 e 375 px; contraste nos 10 temas.
- **SC-005**: Build e testes novos e vizinhos; commit; levar ao `main`. A migração **não** é aplicada ao banco ativo.

## 5. Fora do escopo

- Receptor para o KOReader por rede (o alvo Readwise dele tem URL fixa; o alvo Joplin exigiria imitar outra API
  inteira). Fica o arquivo JSON.
- Sincronização de progresso (KOSync) e de volta para o leitor; edição/remoção remota de destaques.
- CORS para a versão web do Readest.
