# Implementation Plan: F0.6.10 — Segurança de Autenticação, Abuso e Infraestrutura

**Branch**: `049-seguranca-auth-infraestrutura` | **Date**: 2026-10-03 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/049-seguranca-auth-infraestrutura/spec.md`

---

## Summary

Implementar a camada de defesa contra força bruta, abuso de requisições e exposição indevida da infraestrutura no Leitorum (F0.6.10):
1. **Rate Limiting Baseado em Risco e Bloqueio de Falhas**: Evolução do limitador em memória para bloquear por 60 segundos IPs com 5 falhas consecutivas de login em 1 minuto, além de cota global de 30 req/min nas rotas de autenticação, respondendo com HTTP 429 e `Retry-After: 60`.
2. **Resolução Segura de IP de Proxy**: Extração confiável do IP do cliente dando precedência a `CF-Connecting-IP` (Cloudflare Tunnel) e `X-Forwarded-For`, com sanitização de formato.
3. **Governança Adaptativa de Cookies de Sessão**: Cookies `HttpOnly`, `SameSite=Lax` com detecção dinâmica de HTTPS/`X-Forwarded-Proto` para atribuição da flag `Secure=True`, além de invalidação atômica e exclusão segura no logout.
4. **Blindagem de Recursos Privados**: Testes e auditoria de controle de acesso (RBAC) garantindo que backups, dados de outros usuários e arquivos internos não sofram bypass.

---

## Technical Context

**Language/Version**: Python 3.13 (64-bit Windows), TypeScript 5.x / Vue 3  
**Primary Dependencies**: FastAPI, Starlette, SQLAlchemy 2.0, Uvicorn  
**Storage**: SQLite local (modo WAL com foreign keys ativadas) + estruturas voláteis thread-safe em memória para rate limiting  
**Testing**: pytest (com `TestClient`, `tmp_path` e isolamento total), node --test  
**Target Platform**: Windows local (atendendo desktop e dispositivos móveis na rede e via Cloudflare Tunnel)  
**Project Type**: Aplicação Web local de processo único (Backend FastAPI + SPA Vue 3)  
**Performance Goals**: Latência adicionada pela verificação de taxa e resolução de IP < 1ms por requisição  
**Constraints**: Zero chamadas para serviços externos pagos/nuvem; preservação absoluta dos dados de produção; uso exclusivo de bancos descartáveis em testes  
**Scale/Scope**: Processo único local com múltiplos dispositivos conectados simultaneamente  

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Princípio I (Privacidade do Acervo)**: Nenhum dado do usuário ou do banco ativo `backend/data/caderno.db` é acessado ou exposto. **PASS**.
- **Princípio II (Isolamento de Testes)**: Todas as suítes de teste utilizam exclusivamente bancos SQLite em `tmp_path` descartáveis. **PASS**.
- **Princípio III (Fidelidade Arquitetural)**: Stack Python 3.13, FastAPI e SQLite mantida sem dependências externas adicionais. **PASS**.
- **Princípio IV (Governança SDD)**: Ciclo formal executado via Spec Kit em branches/pastas delimitadas, gerando 1 commit atômico ao final. **PASS**.
- **Princípio V (Resiliência)**: Invalidação de sessão transacional segura e tratamento de erros defensivo. **PASS**.

---

## Project Structure

### Documentation (this feature)

```text
specs/049-seguranca-auth-infraestrutura/
├── plan.md              # Este plano de implementação
├── research.md          # Decisões técnicas consolidadas (D1 a D5)
├── data-model.md        # Entidades conceituais e contratos de dados
├── quickstart.md        # 5 cenários executáveis de validação
├── contracts/           # Contratos OpenAPI de rate limiting e sessão
│   └── auth-security-api.yaml
└── checklists/
    └── requirements.md  # Checklist de qualidade (100% PASS)
```

### Source Code

```text
caderno-leitura-0.1/
├── backend/
│   ├── app/
│   │   ├── core/
│   │   │   ├── rate_limiter.py       # Rate limiter volumétrico + rastreador de falhas de login
│   │   │   └── config.py             # Configurações de taxa e helpers
│   │   ├── services/
│   │   │   ├── auth_service.py       # Integração com registro de falhas e sucessos de autenticação
│   │   │   └── session_service.py    # Emissão adaptativa de cookie e invalidação atômica
│   │   └── routers/
│   │       ├── auth.py               # Proteção com rate limiter nas rotas /api/auth/*
│   │       └── backups.py            # Validação de RBAC estrito (apenas admin)
│   └── tests/
│       ├── test_security_rate_limiting.py         # Testes de 429, Retry-After e falhas consecutivas
│       ├── test_security_cookies_and_sessions.py  # Testes de HttpOnly, SameSite, Secure adaptativo e logout
│       ├── test_security_proxy_ip_extraction.py   # Testes de CF-Connecting-IP e sanitização de IP
│       └── test_security_privileged_access.py     # Testes de RBAC em backups e recursos privados
└── frontend/
    └── src/
        └── services/
            └── api.ts                             # Tratamento defensivo de resposta 429 no cliente
```

---

## Planned Phases

- **Phase 0 (Research & Foundation)**: Documentação das decisões de rate limiting em memória, extração de IP de túnel e governança adaptativa de cookies em `research.md`. *(Concluída)*
- **Phase 1 (Design & Contracts)**: Criação de `data-model.md`, `contracts/auth-security-api.yaml`, `quickstart.md` e preenchimento de `plan.md`. *(Concluída)*
- **Phase 2 (Implementation via speckit-tasks)**: Geração de tarefas atômicas sequenciadas em `tasks.md` divididas em User Story 1 (Rate Limiting/Força Bruta), User Story 2 (Cookies e Sessão) e User Story 3 (Identificação de Proxy e RBAC), seguida da implementação e validação via `speckit-implement`.
