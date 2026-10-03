# Quickstart Guide: F0.6.10 — Segurança de Autenticação, Abuso e Infraestrutura

**Feature**: `049-seguranca-auth-infraestrutura`  
**Date**: 2026-10-03  
**Status**: Ready  

Este guia define cenários executáveis e herméticos para validação das camadas de segurança de autenticação, rate limiting e infraestrutura.

---

## Pré-requisitos e Ambiente

- Todos os testes utilizam bancos SQLite temporários descartáveis em `tmp_path` e instâncias isoladas (Princípio II da Constituição).
- O banco ativo local (`backend/data/caderno.db`) permanece 100% intocado.

---

## Cenário 1: Mitigação de Força Bruta por Falhas Consecutivas e Rate Limiting Volumétrico

**Objetivo**: Provar que 5 falhas consecutivas de login por IP acionam bloqueio temporário de 60 segundos com cabeçalho `Retry-After`.

**Comando de Execução**:
```bash
backend\.venv\Scripts\python.exe -m pytest backend/tests/test_security_rate_limiting.py
```

**Verificações**:
1. 4 requisições consecutivas com senha inválida recebem status 401 (Credenciais inválidas).
2. A 5ª requisição com senha inválida recebe status 429 (Too Many Requests).
3. A resposta 429 inclui o cabeçalho `Retry-After: 60` (ou tempo restante correspondente) e mensagem em português.
4. Requisições subsequentes dentro da janela de 60 segundos são bloqueadas antes mesmo de tocar o banco de dados.
5. Um login bem-sucedido zera o contador de falhas acumuladas para aquele IP.

---

## Cenário 2: Governança Adaptativa de Cookies de Sessão

**Objetivo**: Validar que os cookies de autenticação utilizam atributos de segurança adequados tanto em desenvolvimento local quanto atrás de proxy HTTPS.

**Comando de Execução**:
```bash
backend\.venv\Scripts\python.exe -m pytest backend/tests/test_security_cookies_and_sessions.py -k test_cookie_security_flags
```

**Verificações**:
1. Requisição direta em HTTP puro (`http://localhost:8000`) emite cookie com `HttpOnly=True`, `SameSite=Lax` e `Secure=False`.
2. Requisição portando cabeçalho de proxy seguro `X-Forwarded-Proto: https` ou `CF-Visitor: {"scheme":"https"}` emite cookie com `Secure=True`.
3. Em nenhuma circunstância o cookie de sessão é acessível via `document.cookie` no frontend.

---

## Cenário 3: Invalidação Atômica no Logout e Prevenção de Fixação de Sessão

**Objetivo**: Confirmar que o encerramento da sessão revoga permanentemente o identificador no servidor e instrui a exclusão do cookie.

**Comando de Execução**:
```bash
backend\.venv\Scripts\python.exe -m pytest backend/tests/test_security_cookies_and_sessions.py -k test_session_invalidation_on_logout
```

**Verificações**:
1. Realizar login e obter o cookie de sessão.
2. Executar `POST /api/auth/logout`.
3. Inspecionar o cabeçalho `Set-Cookie` e verificar a instrução de expiração imediata (`Max-Age=0`).
4. Tentar acessar `/api/auth/me` ou qualquer endpoint protegido com o token anterior e receber status 401 (Não Autorizado).

---

## Cenário 4: Extração Segura de IP do Cliente (Cloudflare Tunnel e Proxies)

**Objetivo**: Garantir que o IP real seja extraído fidedignamente para correta aplicação de cotas e auditoria.

**Comando de Execução**:
```bash
backend\.venv\Scripts\python.exe -m pytest backend/tests/test_security_proxy_ip_extraction.py
```

**Verificações**:
1. Requisição com cabeçalho `CF-Connecting-IP: 203.0.113.195` resolve o IP do cliente como `203.0.113.195`.
2. Requisição sem Cloudflare mas com `X-Forwarded-For: 198.51.100.42, 10.0.0.1` extrai o primeiro IP `198.51.100.42`.
3. Requisição contendo caracteres espúrios ou formatação maliciosa de porta no IP é devidamente sanitizada.

---

## Cenário 5: Controle Estrito de Acesso a Backups e Dados Privados

**Objetivo**: Verificar que endpoints administrativos e de infraestrutura exigem privilégios elevados.

**Comando de Execução**:
```bash
backend\.venv\Scripts\python.exe -m pytest backend/tests/test_security_privileged_access.py
```

**Verificações**:
1. Visitante não autenticado tentando acessar `/api/backups` recebe 401.
2. Usuário com papel `user` tentando acessar `/api/backups` recebe 403 (Proibido).
3. Apenas usuário com papel `admin` obtém autorização 200 para gerenciar backups.
