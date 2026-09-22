# Research & Technical Decisions: Autenticação e Gestão de Sessões (F02)

Este documento consolida as pesquisas técnicas, decisões de arquitetura e justificativas para a implementação da **Feature 02 (Autenticação e Gestão de Sessões)**.

---

## 1. Algoritmo de Derivação de Senhas: Argon2id

- **Decisão**: Utilizar estritamente a biblioteca `argon2-cffi` com o algoritmo **Argon2id** (variante híbrida recomendada contra ataques de canal lateral e ataques paralelos em GPU/ASIC).
  - Parâmetros padrão recomendados pela OWASP e pela biblioteca:
    - Tipo: `argon2.Type.ID`
    - Custo de tempo (`time_cost` / iterações): `2`
    - Custo de memória (`memory_cost`): `64 MiB` (`65536 KiB`)
    - Paralelismo (`parallelism`): `1` thread
    - Tamanho do hash gerado: `32` bytes
- **Rationale**:
  - O Roadmap 0.5 estabelece como inegociável a proibição de MD5, SHA-256 ou cifras reversíveis para armazenamento de senhas.
  - Argon2 foi o vencedor da *Password Hashing Competition (PHC)* e é o padrão da indústria e da OWASP para senhas locais.
  - `argon2-cffi` possui compilação C nativa com bindings Python de alta velocidade, executando uma derivação em ~100-200ms em hardware convencional sem bloquear o loop de eventos de forma prejudicial.
- **Alternativas Consideradas**:
  - *bcrypt*: Muito popular, mas vulnerável a aceleração maciça em ASICs comparado ao Argon2id e limitado a 72 bytes de entrada.
  - *PBKDF2-HMAC-SHA256*: Disponível nativamente na biblioteca padrão (`hashlib`), porém sem proteção contra uso de memória massiva (muito vulnerável a GPU mining).
  - *scrypt*: Bom, mas com configuração mais complexa e menor suporte moderno que Argon2id.

---

## 2. Identificação, Formato e Armazenamento de Sessões

- **Decisão**:
  1. O cliente recebe um token de sessão opaco e aleatório de 256 bits gerado com `secrets.token_urlsafe(32)` (43 caracteres alfanuméricos seguros para URL).
  2. No banco de dados SQLite, o servidor **NUNCA** armazena o token de sessão em texto claro. O servidor armazena o hash criptográfico do token: `session_token_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()`.
  3. Cada requisição calcula o SHA-256 do token recebido no cookie e realiza a busca indexada em `user_sessions.session_token_hash`.
- **Rationale**:
  - O armazenamento apenas do hash do token de sessão no banco previne que um atacante com acesso de leitura acidental ao arquivo SQLite (ex.: em backups ou compartilhamento indevido) consiga se passar pelos usuários logados.
  - O cálculo de SHA-256 é extremamente veloz (< 0.05ms) e permite indexação B-Tree com busca em $O(1)$ no SQLite.
- **Alternativas Consideradas**:
  - *JSON Web Tokens (JWT) Stateless*: Considerado e descartado. JWTs não permitem revogação remota instantânea pelo painel de dispositivos sem a introdução de uma lista de revogação/blacklist no banco, anulando a vantagem de serem stateless e aumentando o risco de tokens roubados continuarem válidos até expirarem.
  - *Sessões no SQLite com token em texto claro*: Mais simples, mas deixa os tokens expostos em backups da base de dados.

---

## 3. Transporte Seguro de Sessão: Cookies HTTP

- **Decisão**: Utilizar cookies HTTP configurados com:
  - `key="caderno_session"`
  - `httponly=True`: Impede acesso por scripts JavaScript (`document.cookie`), blindando o sistema contra roubo de sessão via vulnerabilidades de Cross-Site Scripting (XSS).
  - `samesite="lax"`: Garante proteção nativa do navegador contra Cross-Site Request Forgery (CSRF) em requisições de terceiros, enquanto permite navegação fluida ao abrir links diretos.
  - `path="/"`: Válido para toda a aplicação.
  - `secure`: Determinado dinamicamente: `True` se a requisição chegar via HTTPS ou pelo túnel Tailscale (`request.url.scheme == "https"` ou `request.headers.get("x-forwarded-proto") == "https"`), ou configurado explicitamente por `SESSION_COOKIE_SECURE=true`.
  - `max_age=2592000` (30 dias em segundos).
- **Rationale**:
  - Atende plenamente aos requisitos de segurança do Roadmap 0.5 e aos padrões de cookies do RFC 6265bis.
  - A proteção `SameSite=Lax` é o padrão moderno em navegadores Chromium/Gecko/WebKit, dispensando a complexidade de tokens CSRF manuais para chamadas da SPA.
- **Alternativas Consideradas**:
  - *Armazenamento em LocalStorage*: Descartado por ser vulnerável a leitura direta por XSS.
  - *SameSite=Strict*: Muito restritivo para navegação a partir de links externos ou favoritos no celular (o usuário sempre pareceria deslogado no primeiro clique).

---

## 4. Política de Renovação Deslizante (Sliding Window Throttle)

- **Decisão**:
  - A expiração é de 30 dias a partir da última atividade.
  - Para evitar escritas excessivas no SQLite (`UPDATE user_sessions SET last_activity = ..., expires_at = ...`) a cada requisição de leitura estática ou ping de API, a atualização do carimbo no banco só é gravada se houver decorrido mais de **10 minutos** desde a última atividade registrada da sessão, ou em rotas com comandos de modificação.
- **Rationale**:
  - O SQLite local no modo WAL é rápido, mas evitar centenas de `UPDATE` desnecessários por minuto poupa I/O de disco e reduz concorrência desnecessária no banco, sem comprometer a exatidão da janela de 30 dias.
- **Alternativas Consideradas**:
  - *Atualizar last_activity a cada requisição*: Sobrecarga desnecessária de I/O em navegações rápidas na interface.
  - *Sem renovação (expiração fixa)*: Frustra o usuário com deslogamentos periódicos após 30 dias, mesmo usando a aplicação diariamente.

---

## 5. Assistente Obrigatório de Primeiro Acesso do Proprietário Legado

- **Decisão**:
  - O backend expõe `GET /api/auth/config` retornando `{ "owner_setup_required": bool, "allow_registration": bool }`.
  - `owner_setup_required` é `True` se a conta canônica `DEFAULT_OWNER_ID` não possuir credencial registrada em `local_credentials`.
  - Quando `owner_setup_required` for verdadeiro, o frontend redireciona qualquer tentativa de navegação para `/primeiro-acesso` (`SetupOwnerView.vue`).
  - O endpoint `POST /api/auth/setup-owner` aceita a nova senha, valida tamanho mínimo (8 caracteres), cria a `LocalCredential` do proprietário, gera uma sessão e devolve o cookie autenticado. O endpoint é travado permanentemente assim que a senha for cadastrada uma única vez.
- **Rationale**:
  - Respeita a decisão da clarificação Q1 (Opção A): garante que o proprietário legado nunca fique bloqueado sem conseguir entrar, mas também não permite que o sistema permaneça desprotegido na rede local.

---

## 6. Identificação Amigável de Dispositivos

- **Decisão**:
  - Implementar parser simples e leve em `backend/app/core/user_agent.py` que analisa o cabeçalho `User-Agent` e sintetiza um rótulo legível para o usuário:
    - Ex.: "Chrome no Windows", "Safari no iPhone", "Firefox no Linux", "Aplicativo / Outro".
  - Obter o endereço IP da conexão (`request.client.host` ou cabeçalho `X-Forwarded-For`).
- **Rationale**:
  - Usuários leigos não entendem strings cruas de User-Agent (`Mozilla/5.0 (Windows NT 10.0; Win64; x64)...`). O rótulo amigável permite identificar com facilidade no painel de Ajustes se o dispositivo é o seu notebook, computador da sala ou celular.
