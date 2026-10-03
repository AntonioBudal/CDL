# Technical Research: F0.6.10 — Segurança de Autenticação, Abuso e Infraestrutura

**Feature**: `049-seguranca-auth-infraestrutura`  
**Date**: 2026-10-03  
**Status**: Completed  

---

## Decisão 1: Arquitetura do Rate Limiter e Bloqueio Escalonado de Falhas

### Contexto
Para proteger o Leitorum contra ataques de força bruta de senhas e ataques volumétricos contra endpoints sensíveis (`/api/auth/*`), o sistema necessita de uma estratégia de limitação de taxa em memória eficiente, sem dependência de serviços externos pesados como Redis, uma vez que a aplicação opera como processo único local (FastAPI/Uvicorn).

### Decisão
Evoluir o `InMemoryRateLimiter` em `backend/app/core/rate_limiter.py` com duas camadas complementares:
1. **Camada Volumétrica (Janela Deslizante Geral)**: Teto de 30 requisições por minuto por IP em endpoints de autenticação (`/api/auth/*`), descartando timestamps mais antigos que 60 segundos com bloqueio thread-safe (`threading.Lock`).
2. **Camada de Falhas Consecutivas (`AuthFailureTracker`)**: Rastreia erros de autenticação (HTTP 401 por credenciais inválidas). Se o mesmo IP acumular 5 falhas consecutivas dentro de uma janela deslizante de 60 segundos, entra em estado de bloqueio (lockout) por 60 segundos. Autenticações bem-sucedidas zeram imediatamente o contador de falhas daquele IP.

### Rationale
- Cumpre a decisão alinhada **Q1: A** sem onerar requisições de leitura normais.
- A memória consumida é desprezível (deques de floats contendo timestamps recentes e contadores inteiros), com limpeza automática de chaves expiradas.
- O tempo de resposta para verificação em memória é sub-milissegundo (< 0.2ms).

### Alternativas Consideradas
- *Token Bucket tradicional*: Mais complexo para implementar bloqueio baseado especificamente no resultado da autenticação (sucesso vs falha).
- *Redis/Memcached*: Violaria a Constituição (Princípio III - Execução local única e sem dependências pesadas de infraestrutura).
- *Bloqueio permanente de conta*: Inadequado para ambientes multiusuário locais ou familiares, pois um invasor poderia propositalmente travar a conta da vítima tentando senhas erradas (Denial of Service contra o usuário). O bloqueio deve ser por endereço IP de origem.

---

## Decisão 2: Identificação Segura do IP do Cliente em Proxies e Cloudflare Tunnel

### Contexto
Quando o Leitorum é acessado via Cloudflare Tunnel (`cloudflared`) ou proxy reverso local (Nginx/Traefik), o endereço retornado por `request.client.host` é o de loopback (`127.0.0.1` ou rede privada). Se o rate limiter usar esse IP, todos os clientes da internet compartilhariam a mesma cota e poderiam sofrer bloqueios mútuos.

### Decisão
Implementar função canônica `get_client_ip(request: Request) -> str` com a seguinte ordem de precedência:
1. `CF-Connecting-IP`: Cabeçalho fornecido e garantido pelo Cloudflare Tunnel/Edge.
2. `X-Forwarded-For`: Primeiro IP da lista separada por vírgulas (removendo espaços e porta, se presente).
3. `X-Real-IP`: Cabeçalho padrão de proxies Nginx.
4. `request.client.host`: Fallback para conexões diretas sem proxy.
5. `127.0.0.1`: Fallback final caso o cliente não informe endereço de rede.

Adicionalmente, sanitizar a string resultante para garantir que contenha apenas caracteres válidos de endereço IPv4 ou IPv6 (evitando ataques de injeção ou chaves gigantes em memória).

### Rationale
- Garante total compatibilidade com a topologia documentada no Roadmap 0.6 (`Internet -> Cloudflare -> Tunnel -> Windows -> Leitorum`).
- Isola cotas por usuário/rede real, prevenindo colisão de bloqueios.

### Alternativas Consideradas
- *Confiar cegamente em qualquer cabeçalho*: Sem validação de formato, poderia abrir brechas de poluição de chaves em memória.
- *Usar apenas `request.client.host`*: Quebraria imediatamente o rate limiter atrás do Cloudflare Tunnel, bloqueando todos os usuários como se fossem `127.0.0.1`.

---

## Decisão 3: Política Adaptativa para Flag `Secure` e Governança de Cookies

### Contexto
Para evitar vazamento de cookies de sessão em trânsito, a flag `Secure` deve estar presente em ambientes HTTPS. No entanto, o Leitorum é projetado para operar também em ambientes locais offline e redes privadas sem HTTPS (`http://localhost:8000`). Se a flag `Secure` for forçada incondicionalmente em HTTP puro, os navegadores rejeitam o cookie e o login quebra.

### Decisão
Adotar a estratégia **Q2: A (Adaptativo / Proxy-Aware)** em `backend/app/services/session_service.py`:
- `resolve_cookie_secure(request: Request | None) -> bool`:
  1. Se `CADERNO_COOKIE_SECURE` estiver explicitamente definido no ambiente, respeita o booleano configurado.
  2. Se a requisição contiver `X-Forwarded-Proto: https` ou `CF-Visitor: {"scheme":"https"}` ou `request.url.scheme == "https"`, retorna `True`.
  3. Caso contrário, retorna `False`.

Sempre emitir cookies com:
- `httponly=True`
- `samesite="lax"`
- `path="/"`

### Rationale
- Funciona sem intervenção manual tanto em `localhost` (dev/testes) quanto via Cloudflare Tunnel em produção HTTPS.
- Inibe ataques de roubo de cookies via scripts maliciosos (XSS) e mitiga ataques de CSRF.

### Alternativas Consideradas
- *Exigir flag estrita por `.env`*: Causaria atrito em configurações rápidas e testes automatizados.
- *Forçar `Secure=True` sempre*: Inviabilizaria o uso local offline do sistema sem configuração de certificados SSL locais.

---

## Decisão 4: Invalidação Atômica no Logout e Prevenção de Fixação de Sessão

### Contexto
O logout deve garantir que nem o cliente continue portando o cookie de sessão, nem o servidor continue aceitando aquele identificador em novas requisições.

### Decisão
1. Ao efetuar logout (`POST /api/auth/logout`):
   - Localizar o registro `UserSession` no banco a partir do token recebido.
   - Deletar/revogar atomicamente o registro do banco de dados (`session.delete(user_session); session.commit()`).
   - Emitir `response.delete_cookie(key=SESSION_COOKIE_NAME, path="/", httponly=True, samesite="lax", secure=secure)`.
2. Em transições de autenticação (login bem-sucedido):
   - Sempre gerar um novo token criptograficamente seguro via `generate_session_token()` (`secrets.token_urlsafe(32)`), garantindo que identificadores pré-autenticação não sejam reutilizados.

### Rationale
- Atende aos requisitos OWASP de gerenciamento de sessão e previne replay de sessão.

---

## Decisão 5: Auditoria e Bloqueio de Recursos Restritos e Mídias Privadas

### Contexto
Arquivos e rotas de administração não podem depender de anonimato ou URLs obscuras.

### Decisão
- Assegurar que todas as rotas em `/api/admin/*`, `/api/backups/*`, `/api/sync/*` e endpoints de ciclo de vida da conta validem o papel do usuário (`role == "admin"`) e a propriedade do registro (`user_id == current_user.id`).
- Rotas de cópia de segurança e snapshots exigem explicitamente usuário autenticado com permissão de administrador (`admin`), retornando HTTP 403 Forbidden para usuários comuns e 401 para visitantes não autenticados.
- Testes automatizados herméticos devem comprovar essas restrições.
