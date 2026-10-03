# Quickstart Guide: F0.6.9 — Segurança de Aplicação e Dados

**Feature**: `048-seguranca-aplicacao-dados`  
**Date**: 2026-10-03  
**Status**: Ready  

Este guia define cenários executáveis e herméticos para validação das camadas de segurança implementadas nesta feature.

---

## Pré-requisitos e Ambiente

- Todos os testes utilizam bancos SQLite temporários descartáveis em `tmp_path` e portas efêmeras (Princípio II da Constituição).
- O banco ativo local (`backend/data/caderno.db`) permanece 100% intocado.

---

## Cenário 1: Neutralização de Injeção XSS e Sanitização de Links

**Objetivo**: Provar que payloads XSS conhecidos em Markdown são completamente neutralizados sem quebrar recursos legítimos de leitura ativa.

**Comando de Execução**:
```bash
npm test -- frontend/tests/security_xss_sanitization.test.mjs
```

**Verificações**:
1. String contendo `<script>alert(1)</script>` é neutralizada, não resultando em nenhum elemento `<script>` no DOM renderizado.
2. Link no formato `[Exploit](javascript:alert(1))` ou `[Exploit](vbscript:...)` tem seu atributo `href` neutralizado ou removido, impedindo execução no clique.
3. Trecho com tags `<img>` e eventos inline (`onerror="alert(1)"`) tem os atributos de evento eliminados.
4. Recursos legítimos de leitura ativa (`<mark>`, botões `.study-occlusion-btn`, tags `.study-question-target`) permanecem intactos e interativos.

---

## Cenário 2: Cabeçalhos HTTP de Segurança e CSP em Modo Enforce

**Objetivo**: Validar a injeção incondicional dos cabeçalhos de proteção e integridade das diretivas CSP.

**Comando de Execução**:
```bash
backend\.venv\Scripts\python.exe -m pytest backend/tests/test_security_headers_and_csp.py
```

**Verificações**:
1. Requisição para `/api/health` ou qualquer rota retorna:
   - `Content-Security-Policy` contendo `default-src 'self'`, `frame-ancestors 'self'`, `https://accounts.google.com` e `https://fonts.googleapis.com`.
   - `X-Content-Type-Options: nosniff`.
   - `Referrer-Policy: strict-origin-when-cross-origin`.
   - `Permissions-Policy: camera=(), microphone=(), geolocation=()`.
   - `X-Frame-Options: SAMEORIGIN`.
2. Rotas privadas mantêm `X-Robots-Tag: noindex, nofollow`.

---

## Cenário 3: Mascaramento de Erros 500 com Correlação por `error_id`

**Objetivo**: Confirmar que exceções inesperadas do servidor não expõem detalhes técnicos na resposta HTTP, fornecendo um UUID para correlação.

**Comando de Execução**:
```bash
backend\.venv\Scripts\python.exe -m pytest backend/tests/test_security_error_masking.py
```

**Verificações**:
1. Rota de teste disparando `raise RuntimeError("Falha de conexão interna secreta: C:\\Users\\User\\...")` responde com status 500.
2. Corpo da resposta contém `{"detail": "Ocorreu um erro interno no servidor.", "error_id": "<uuid>"}`.
3. Nenhuma informação sobre arquivos locais, tracebacks de Python ou nomes de tabelas está presente no JSON retornado.

---

## Cenário 4: Imunidade a Injeção SQL na Busca Global e Filtros

**Objetivo**: Submeter payloads maliciosos de injeção SQL aos endpoints de busca e consulta para verificar parametrização estrita.

**Comando de Execução**:
```bash
backend\.venv\Scripts\python.exe -m pytest backend/tests/test_security_sql_injection.py
```

**Verificações**:
1. Busca por `' OR '1'='1` ou `' UNION SELECT NULL, NULL --` executa sem erro sintático e retorna apenas estudos cujo título ou conteúdo contenham a string literal.
2. Nenhum dado de outros usuários ou registros não autorizados vaza na consulta.

---

## Cenário 5: Bloqueio de Acesso a Arquivos Sensíveis de Infraestrutura

**Objetivo**: Garantir que requisições estáticas para `.env`, `.git` ou arquivos `.db` sejam estritamente bloqueadas.

**Comando de Execução**:
```bash
backend\.venv\Scripts\python.exe -m pytest backend/tests/test_security_static_blocking.py
```

**Verificações**:
1. Requisição para `/.env` ou `/backend/data/caderno.db` retorna `404 Not Found`.
2. Requisições com tentativas de *path traversal* (`/../../.env`) são rejeitadas.
