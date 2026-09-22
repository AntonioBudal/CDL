# Implementation Plan: Autenticação e Gestão de Sessões (F02)

**Branch**: `029-autenticacao-gestao-sessoes` | **Date**: 2026-09-21 | **Spec**: [spec.md](spec.md)  

**Input**: Feature specification from `specs/029-autenticacao-gestao-sessoes/spec.md`

---

## Summary

Implementar a camada nativa de autenticação por credenciais locais e o gerenciamento seguro de sessões multi-dispositivo no Caderno de Leitura. A entrega inclui proteção de senhas com algoritmo adaptativo Argon2id (`argon2-cffi`), emissão de identificadores de sessão opacos transportados em cookies `HttpOnly`, janela deslizante de 30 dias de inatividade, assistente obrigatório de primeiro acesso para definição da senha mestra do proprietário legado, controle de auto-registro configurável (`ALLOW_REGISTRATION`), painel de dispositivos conectados com revogação remota e encerramento global de outras sessões (*logout-all*), além de telas completas de autenticação no frontend Vue 3 e proteção por guardas de rota.

---

## Technical Context

**Language/Version**: Python 3.13 / 3.14 (64-bit) no Windows; TypeScript / Node.js 24 no frontend.  
**Primary Dependencies**: FastAPI, SQLAlchemy 2.0 (Mapped Columns declarativos), Alembic, Pydantic v2, `argon2-cffi`, Uvicorn.  
**Frontend Stack**: Vue 3, Vue Router 4, Pinia/Reatividade Vue, Vite, Tailwind/CSS.  
**Storage**: SQLite 3 local em modo Write-Ahead Logging (WAL) com chaves estrangeiras ativas (`PRAGMA foreign_keys = ON`).  
**Testing**: `pytest` com fixture `tmp_path` e isolamento total para o backend; `npm test` para o frontend.  
**Target Platform**: Windows local (processo único `iniciar.py` atendendo PC e dispositivos móveis via rede/Tailscale).  
**Project Type**: Web Application com API REST local (`/api`) e interface SPA em Vue 3.  
**Performance Goals**: Hash e verificação Argon2id em ~100-250ms; validação de sessão em < 5ms por requisição; persistência de atividade throttleada (10 min).  
**Constraints**: Zero exposição de senhas ou tokens crus em logs/banco; transporte de sessão exclusivamente via cookie `HttpOnly`; isolamento hermético entre usuários; suporte retrocompatível com fallback de desenvolvimento nos testes.  
**Scale/Scope**: Múltiplas sessões simultâneas por usuário (PC + mobile), controle de concorrência e integridade transacional.  

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **Art. I — Proteção do Acervo e Privacidade:** A migração adiciona credenciais e sessões sem expor nem adulterar anotações do acervo. Textos reais e dados do banco continuam estritamente privados.
- [x] **Art. II — Isolamento Estrito de Testes:** Todas as novas suítes de teste de autenticação e sessões utilizam instâncias temporárias em `tmp_path`. O banco ativo (`backend/data/caderno.db`) não é tocado.
- [x] **Art. III — Fidelidade Tecnológica:** FastAPI + SQLAlchemy 2.0 + Alembic (`batch_alter_table` para SQLite) + `argon2-cffi` + cookies `HttpOnly` com proteção CSRF `SameSite=Lax`.
- [x] **Art. IV — Governança por Especificação Delimitada:** Escopo restrito à Feature 02 (Autenticação Local e Gestão de Sessões). Integração social/Google OAuth fica estritamente reservada para a Feature 03.
- [x] **Art. V — Resiliência Operacional e Migrações Seguras:** Migração Alembic `0012` aditiva, reversível (`downgrade` limpo) e idempotente, testada em bancos descartáveis.

---

## Project Structure

### Documentation (this feature)

```text
specs/029-autenticacao-gestao-sessoes/
├── spec.md                   # Especificação de requisitos e critérios de aceite
├── plan.md                   # Este plano de implementação técnica
├── research.md               # Pesquisa técnica e decisões de arquitetura
├── data-model.md             # Modelo de dados e especificação de entidades
├── quickstart.md             # Guia de validação e cenários de teste executáveis
├── contracts/                # Contratos de interface e segurança da API
│   ├── auth-api.yaml         # OpenAPI 3.0 dos endpoints de autenticação e sessões
│   └── session-lifecycle.md  # Contrato do ciclo de vida e transporte da sessão
├── checklists/               # Checklists de qualidade
│   └── requirements.md       # Checklist de validação da especificação
└── tasks.md                  # Tarefas atômicas de implementação (gerado em /speckit-tasks)
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── core/
│   │   ├── config.py                 # Configurações de sessão, expiração e flags de registro
│   │   ├── security.py               # [NEW] Utilitários criptográficos Argon2id e hashing de tokens
│   │   └── user_agent.py             # [NEW] Utilitário de formatação amigável de dispositivos
│   ├── dependencies.py               # Atualização de CurrentUser para validar cookies de sessão
│   ├── models/
│   │   ├── user.py                   # Adição de email, role e relacionamentos
│   │   ├── local_credential.py       # [NEW] Modelo SQLAlchemy LocalCredential
│   │   └── user_session.py           # [NEW] Modelo SQLAlchemy UserSession
│   ├── routers/
│   │   └── auth.py                   # Endpoints: /login, /logout, /register, /setup-owner, /sessions, /logout-all
│   ├── schemas/
│   │   ├── auth.py                   # [NEW] Schemas de requisição/resposta de autenticação e sessões
│   │   └── user.py                   # Atualização de UserRead com campos públicos seguros
│   └── services/
│       └── session_service.py        # [NEW] Regras de negócio de criação, validação e revogação de sessões
├── migrations/
│   └── versions/
│       └── 0012_add_credentials_and_sessions.py  # [NEW] Migração Alembic
└── tests/
    ├── test_password_security.py     # [NEW] Teste de hash e verificação Argon2id
    ├── test_session_lifecycle.py     # [NEW] Teste de login, logout, expiração e sliding window
    └── test_device_management.py     # [NEW] Teste de listagem, revogação remota e logout-all

frontend/
├── src/
│   ├── components/
│   │   └── auth/                     # [NEW] Componentes de formulário de login/registro/setup
│   ├── router/
│   │   └── index.ts                  # Guardas de navegação (redirecionamento de não autenticados)
│   ├── services/
│   │   └── api.ts                    # Métodos de auth (login, logout, register, setupOwner, getSessions)
│   ├── stores/
│   │   └── auth.ts                   # [NEW] Store reativa de estado do usuário e sessão
│   └── views/
│       ├── LoginView.vue             # [NEW] Tela de autenticação com credenciais
│       ├── RegisterView.vue          # [NEW] Tela de criação de nova conta
│       ├── SetupOwnerView.vue        # [NEW] Tela de primeiro acesso para definir senha mestra
│       └── SettingsView.vue          # Painel de sessões ativas e dispositivos conectados
```

**Structure Decision**: Padrão modular em FastAPI + Vue 3 seguindo a arquitetura consolidada do Caderno de Leitura, isolando a lógica criptográfica em `core/security.py` e o ciclo de vida de sessões em `services/session_service.py`.

---

## Complexity Tracking

> **Nenhuma violação à Constituição identificada.** O uso de `argon2-cffi` adere integralmente à diretriz do Roadmap 0.5. As tabelas `local_credentials` e `user_sessions` utilizam chaves estrangeiras com integridade referencial em cascata (`CASCADE`) e índices de busca em `session_token_hash`.
