# Implementation Plan: F10 — Segurança, Auditoria, Ciclo de Vida da Conta e Google OAuth

**Branch**: `039-seguranca-auditoria-conta` | **Date**: 2026-09-26 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/039-seguranca-auditoria-conta/spec.md`

## Summary

Implementar a blindagem integral da aplicação conforme o OWASP e a LGPD:
1. Controle de taxa de requisições (*Rate Limiting*) em memória com janela deslizante para mitigar ataques de força bruta, associado a mensagens genéricas unificadas contra enumeração de contas.
2. Autenticação prática e sem atrito com Google OAuth 2.0 (redirecionamento/callback e GIS ID Token com auto-associação e provisionamento sem senha).
3. Trilha de auditoria estruturada (`AuditLog`) com sanitização ativa e consulta administrativa segura.
4. Ciclo de vida da conta com desativação temporária (e reativação explícita no login com confirmação do titular) e exclusão física transacional em cascata (Direito ao Esquecimento).
5. Portabilidade completa do acervo em arquivo ZIP contendo pastas com Markdown legível e arquivo `dados_acervo.json` consolidado.
6. Painel de Segurança e Privacidade nas configurações do frontend (`SettingsView.vue`) e botão Google na tela de autenticação (`LoginView.vue`).

---

## Technical Context

**Language/Version**: Python 3.13 (Backend) | TypeScript 5.8 / Node.js 24 (Frontend)  
**Primary Dependencies**:
- Backend: FastAPI, SQLAlchemy 2.0, Alembic, Pydantic v2, `google-auth`, `argon2-cffi`, `python-multipart`
- Frontend: Vue 3 (Composition API), Vite, Vue Router, Lucide Icons  
**Storage**: SQLite 3 local em modo Write-Ahead Logging (WAL) com chaves estrangeiras ativas (`PRAGMA foreign_keys = ON`)  
**Testing**: `pytest` (Backend com bancos descartáveis `tmp_path`) | `node --test` / Vitest (Frontend)  
**Target Platform**: Windows local (PowerShell, Uvicorn processo único) com acesso em rede privada Tailscale  
**Project Type**: Aplicação Web cliente-servidor monoprocesso local  
**Performance Goals**:
- Rate limit interception: < 5ms
- Google OAuth auto-provisioning: < 1000ms
- Exportação de acervo (ZIP): < 3s para acervos com 500 estudos
- Desativação / Reativação: < 100ms  
**Constraints**:
- Zero impacto no banco de dados ativo de produção durante testes automatizados.
- Zero segredos (senhas, hashes ou tokens) em logs de auditoria.
- Preservação estrita da integridade referencial do SQLite.  
**Scale/Scope**: Multiusuário local (de 1 a dezenas de leitores em rede doméstica/privada).

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Artigo Constitucional | Regra do Projeto | Status de Conformidade |
|---|---|---|
| **Art. I — Proteção Absoluta do Acervo** | O acervo é estritamente privado. Textos do usuário não são expostos em logs. Exclusão física transacional e exportação limpa. | **APROVADO**: AuditLog sanitiza 100% dos metadados e omite segredos e conteúdo pessoal. |
| **Art. II — Isolamento Estrito de Testes** | Testes usam `tmp_path` e portas efêmeras, sem tocar em `backend/data/caderno.db`. | **APROVADO**: Todas as suítes utilizam bancos SQLite temporários. |
| **Art. III — Fidelidade Tecnológica** | Python 3.13, FastAPI, SQLAlchemy 2, Alembic, Vue 3, SQLite WAL sem cloud externa. | **APROVADO**: Processo único local via `iniciar.py`, Google OAuth usa apenas bibliotecas locais padrão. |
| **Art. IV — Governança por SDD** | Fatias orientadas ao Spec Kit (specify $\to$ clarify $\to$ plan $\to$ tasks $\to$ implement). | **APROVADO**: Ciclo formal seguido à risca na Feature 10. |
| **Art. V — Resiliência Operacional** | Atomicidade de transações, validação de integridade referencial do SQLite. | **APROVADO**: Exclusão definitiva em transação atômica única com rollback defensivo. |

---

## Project Structure

### Documentation (this feature)

```text
specs/039-seguranca-auditoria-conta/
├── spec.md              # Especificação de requisitos e cenários
├── checklists/
│   └── requirements.md  # Checklist de qualidade de requisitos
├── plan.md              # Este plano de implementação
├── research.md          # Pesquisa técnica e decisões de arquitetura
├── data-model.md        # Esquema relacional, entidades e regras de transição
├── contracts/
│   └── security-lifecycle-api.yaml # Contratos OpenAPI dos endpoints
└── quickstart.md        # Guia de validação ponta a ponta
```

### Source Code (Concrete Implementation Paths)

```text
caderno-leitura-0.1/
├── backend/
│   ├── app/
│   │   ├── core/
│   │   │   ├── config.py             # Configurações de Google OAuth e Rate Limit
│   │   │   └── rate_limiter.py       # Gerenciador em memória de rate limiting e janelas deslizantes
│   │   ├── models/
│   │   │   ├── audit_log.py          # Modelo relacional AuditLog
│   │   │   └── user.py               # Extensão com status, deactivated_at, lockout fields
│   │   ├── schemas/
│   │   │   ├── audit_log.py          # Schemas Pydantic para auditoria
│   │   │   └── account.py            # Schemas para desativação, reativação e exclusão
│   │   ├── services/
│   │   │   ├── audit_service.py      # Serviço central de auditoria com sanitização
│   │   │   ├── account_service.py    # Ciclo de vida (desativação, reativação, exclusão em cascata)
│   │   │   ├── export_service.py     # Compilação e streaming de arquivo ZIP com Markdown e JSON
│   │   │   ├── google_auth_service.py# Suporte estendido a OAuth 2.0 Web Redirect + GIS
│   │   │   └── auth_service.py       # Integração com lockout por conta e reativação explícita
│   │   └── routers/
│   │       ├── auth.py               # Rotas com rate limiting, /google/login e /google/callback
│   │       ├── account.py            # Endpoints /api/account/deactivate, /reactivate, DELETE e /export
│   │       └── admin.py              # Endpoint /api/admin/audit-logs
│   ├── migrations/versions/
│   │   └── 0019_add_audit_logs_and_user_lifecycle.py # Migração Alembic para auditoria e status
│   └── tests/
│       ├── test_rate_limit.py        # Testes de bloqueio 429 e Retry-After
│       ├── test_audit_log.py         # Testes de gravação de eventos e ausência de segredos
│       ├── test_account_lifecycle.py # Testes de desativação, reativação explícita e exclusão em cascata
│       ├── test_account_export.py    # Testes de geração do pacote ZIP completo
│       └── test_google_oauth_web.py  # Testes de fluxo web e auto-associação Google
│
└── frontend/
    └── src/
        ├── api/
        │   └── account.ts            # Cliente de API para ciclo de vida e exportação
        ├── components/
        │   ├── auth/
        │   │   └── GoogleSignInButton.vue # Botão refinado de login com Google
        │   └── settings/
        │       ├── SecuritySettings.vue   # Seção de segurança, sessões e ciclo de vida da conta
        │       └── ReactivateAccountModal.vue # Modal de confirmação explícita de reativação
        ├── views/
        │   ├── LoginView.vue         # Integração destacada do botão Google e fluxo de reativação
        │   └── SettingsView.vue      # Nova aba/área "Segurança e Privacidade"
        └── tests/
            └── security_lifecycle.test.mjs # Testes automatizados de UI e fluxo de ciclo de vida
```

---

## Complexity Tracking

> Nenhuma violação das restrições constitucionais foi identificada. O design preserva a simplicidade operacional, a execução local em processo único, o isolamento dos dados e o uso exclusivo do SQLite local no Windows.
