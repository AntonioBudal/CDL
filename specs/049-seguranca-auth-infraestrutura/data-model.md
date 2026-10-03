# Data Model: F0.6.10 — Segurança de Autenticação, Abuso e Infraestrutura

**Feature**: `049-seguranca-auth-infraestrutura`  
**Date**: 2026-10-03  
**Status**: Ready  

---

## 1. Entidades de Domínio

### 1.1 `AuthFailureRecord` (Em Memória / Efêmero)
Estrutura thread-safe para contabilizar falhas consecutivas de autenticação por endereço IP e gerenciar períodos de bloqueio (lockout).

| Campo | Tipo | Descrição |
|---|---|---|
| `ip` | `str` | Endereço IP do cliente sanitizado (chave do registro) |
| `failure_timestamps` | `deque[float]` | Fila de timestamps Unix das tentativas incorretas nos últimos 60 segundos |
| `locked_until` | `float` | Timestamp Unix até o qual novas tentativas de autenticação estão bloqueadas (0 se desbloqueado) |

**Regras de Transição de Estado**:
1. Ao ocorrer erro de credenciais inválidas (HTTP 401):
   - Adiciona `now` em `failure_timestamps`.
   - Remove timestamps mais antigos que `now - 60`.
   - Se `len(failure_timestamps) >= 5`: define `locked_until = now + 60` (bloqueio ativo).
2. Ao ocorrer login bem-sucedido:
   - Limpa `failure_timestamps` e define `locked_until = 0` para o IP correspondente.
3. Ao expirar o tempo (`now >= locked_until`):
   - O estado de bloqueio é desativado automaticamente, permitindo novas tentativas.

---

### 1.2 `RateLimitBucket` (Em Memória / Efêmero)
Estrutura para cálculo de limite volumétrico de requisições por janela deslizante.

| Campo | Tipo | Descrição |
|---|---|---|
| `key` | `str` | Identificador composto `{client_ip}:{path_prefix}` |
| `timestamps` | `deque[float]` | Fila de timestamps Unix das requisições registradas |
| `window_seconds` | `int` | Tamanho da janela deslizante (padrão: 60s) |
| `max_requests` | `int` | Limite de requisições permitidas na janela (padrão: 30 para `/api/auth/*`) |

**Regras de Validação**:
- Se `len(timestamps) >= max_requests`, calcula `retry_after = ceil(timestamps[0] + window_seconds - now)` e rejeita com HTTP 429.
- Caso contrário, registra o timestamp atual e autoriza o processamento.

---

### 1.3 `UserSession` (Entidade Persistida no SQLite)
Entidade existente no banco de dados (`user_sessions`), cuja integridade e ciclo de vida são reforçados.

```text
Table: user_sessions
  id                 INTEGER PRIMARY KEY AUTOINCREMENT
  user_id            TEXT NOT NULL (FK -> users.id, ON DELETE CASCADE)
  session_token_hash TEXT NOT NULL UNIQUE (SHA-256 do token opaco)
  device_name        TEXT NOT NULL
  ip_address         TEXT NOT NULL
  user_agent         TEXT NOT NULL
  created_at         TIMESTAMP NOT NULL
  last_activity      TIMESTAMP NOT NULL
  expires_at         TIMESTAMP NOT NULL
```

**Políticas de Segurança do Modelo**:
- Tokens brutos nunca são armazenados; apenas o hash criptográfico `session_token_hash`.
- Logout apaga atomicamente a tupla da tabela, impedindo reuso.
- Renovações de atividade possuem throttle temporal (`SESSION_ACTIVITY_THROTTLE_SECONDS`) para evitar writes excessivos no SQLite WAL.

---

### 1.4 `ClientIpContext` (Objeto de Valor em Execução)
Representa a resolução segura do endereço de rede do cliente a partir da requisição HTTP.

| Atributo | Tipo | Descrição |
|---|---|---|
| `raw_ip` | `str` | String de IP extraída de `CF-Connecting-IP`, `X-Forwarded-For` ou socket |
| `normalized_ip` | `str` | IP limpo de portas, espaços e delimitadores |
| `is_loopback` | `bool` | Indica se é endereço local (`127.0.0.1`, `::1`) |
| `is_valid` | `bool` | Indica se o formato é sintaticamente válido como IPv4/IPv6 |
