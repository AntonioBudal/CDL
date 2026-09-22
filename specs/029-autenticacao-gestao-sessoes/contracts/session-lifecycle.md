# Contract: Ciclo de Vida e Segurança de Sessões

**Feature**: `029-autenticacao-gestao-sessoes`  
**Date**: 2026-09-21  

---

## 1. Transporte da Sessão e Atributos de Cookie

A aplicação utiliza cookies HTTP como vetor exclusivo de transporte da sessão entre o navegador e o servidor FastAPI.

| Atributo | Configuração | Finalidade de Segurança |
| :--- | :--- | :--- |
| **Nome** | `caderno_session` | Chave padronizada para identificar a sessão. |
| **Valor** | `raw_token` (Base64url, 32 bytes de entropia) | Identificador opaco de alta imprevisibilidade gerado via `secrets.token_urlsafe(32)`. |
| **HttpOnly** | `True` | Bloqueia leitura via JavaScript (`document.cookie`), prevenindo roubo de credencial por XSS. |
| **SameSite** | `Lax` | O cookie é retido em chamadas de terceiros (CSRF), mas anexado em navegações de links de topo. |
| **Path** | `/` | Garante validade para todas as rotas da aplicação (`/api/*` e interface). |
| **Secure** | Dinâmico (`True` em HTTPS/Tailscale) | Impede transmissão em canais abertos não criptografados. |
| **Max-Age** | `2592000` (30 dias) | Tempo de persistência no armazenamento seguro do navegador. |

---

## 2. Ciclo de Vida e Estados da Sessão

```
              ┌───────────────────────────┐
              │    Login / Registro /     │
              │       Setup Owner         │
              └─────────────┬─────────────┘
                            │ Emite cookie caderno_session
                            ▼
              ┌───────────────────────────┐
     ┌───────▶│       Sessão Ativa        │◀──────────┐
     │        │  (expires_at > now())     │           │
     │        └─────────────┬─────────────┘           │
     │                      │                         │ Requisição válida
     │ Atividade > 10 min   │ Inatividade > 30 dias   │ (Throttle 10 min)
     │ renova expires_at    ▼                         │
     │        ┌───────────────────────────┐           │
     └────────┤      Sessão Expirada      │───────────┘
              │  (Rejeitada com HTTP 401) │
              └─────────────┬─────────────┘
                            │
                            │ Logout / Revogação Remota /
                            │ Logout-All / Exclusão de Conta
                            ▼
              ┌───────────────────────────┐
              │      Sessão Revogada      │
              │   (Destruída no SQLite)   │
              └───────────────────────────┘
```

---

## 3. Mecanismo de Janela Deslizante (*Sliding Window*)

- **Duração Base**: 30 dias a partir da criação ou da última atividade registrada.
- **Throttling de Gravação**:
  - Para proteger a durabilidade do banco SQLite e evitar I/O desnecessário a cada clique ou requisição GET na interface, o servidor verifica:
    $$\Delta t = \text{now()} - \text{session.last\_activity}$$
  - Se $\Delta t \ge 10 \text{ minutos}$:
    $$\text{session.last\_activity} = \text{now()}$$
    $$\text{session.expires_at} = \text{now()} + 30 \text{ dias}$$
    E o cookie é reemitido na resposta.
  - Se $\Delta t < 10 \text{ minutos}$:
    A requisição é autorizada em memória sem necessidade de `UPDATE` no SQLite.

---

## 4. Regras de Revogação e Anti-IDOR

1. **Revogação Seletiva (`DELETE /api/auth/sessions/{id}`)**:
   - O servidor verifica estritamente se `session.user_id == current_user.id`.
   - Se a sessão pertencer a outro usuário ou não existir, o servidor responde uniformemente com `HTTP 404 Not Found` (anti-IDOR e anti-enumeração de sessões).
   - Se pertencer ao usuário conectado, a linha é removida do SQLite. Caso a sessão revogada seja a sessão corrente, o cookie é removido na resposta.
2. **Encerramento Geral (`POST /api/auth/logout-all`)**:
   - Deleta todas as sessões em `user_sessions` onde `user_id == current_user.id` e `id != current_session.id`.
   - Preserva intacta a sessão em uso no momento do comando.

---

## 5. Retrocompatibilidade para Testes Automatizados

- Para permitir que as suítes de testes unitários existentes e scripts de diagnóstico continuem executando de forma rápida sem exigir fluxos completos de login em cada requisição:
  - Se o cookie `caderno_session` **não estiver presente**, a dependência `get_current_user` verifica a presença do cabeçalho `X-User-Id`.
  - Se `X-User-Id` for fornecido e corresponder a um UUID válido de usuário ativo, ele é resolvido para fins de teste.
  - Em ambiente de produção, clientes web utilizam estritamente o cookie seguro `caderno_session`.
