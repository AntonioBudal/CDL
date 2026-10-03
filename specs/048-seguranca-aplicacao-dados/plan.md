# Implementation Plan: F0.6.9 — Segurança de Aplicação e Dados

**Branch**: `048-seguranca-aplicacao-dados` | **Date**: 2026-10-03 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/048-seguranca-aplicacao-dados/spec.md`

---

## Summary

Fortalecer as camadas de segurança de código, entrada de dados e exposição do Leitorum agora que a aplicação está acessível publicamente na internet. A entrega contempla:
1. Imunização contra XSS e validação de URLs no parser Markdown do frontend, preservando os recursos legítimos de leitura ativa.
2. Injeção incondicional de cabeçalhos HTTP de segurança (`Content-Security-Policy` em modo *Enforce*, `X-Content-Type-Options: nosniff`, `Referrer-Policy`, `Permissions-Policy`, `X-Frame-Options` e `frame-ancestors 'self'`).
3. Política CORS restrita para ambiente same-origin com parametrização controlada por variável de ambiente.
4. Mascaramento global de falhas internas 500 do backend com resposta genérica e correlação via `error_id` UUID registrado exclusivamente nos logs do servidor.
5. Auditoria empírica de queries e testes automatizados contra injeção SQL.
6. Bloqueio estrito de acesso público a arquivos de infraestrutura e verificação da chave de sessão na inicialização.

---

## Technical Context

**Language/Version**: Python 3.13 (backend) e TypeScript 5 / Vue 3 (frontend)  
**Primary Dependencies**: FastAPI, Uvicorn, SQLAlchemy 2.0, Markdown-it, Vue 3, Vite  
**Storage**: SQLite local em modo WAL (sem alteração de schema relacional para esta feature)  
**Testing**: pytest (backend) e Node test runner (frontend)  
**Target Platform**: Windows 11 local (servidor único via `iniciar.py`) atendendo acessos web e mobile  
**Project Type**: Aplicação web full-stack com arquitetura same-origin  
**Performance Goals**: Sobrecarga de sanitização imperceptível (<15ms por documento) e overhead de middleware <2ms por requisição  
**Constraints**: Não quebrar componentes interativos de leitura ativa nem a autenticação com Google Identity Services (GIS)  
**Scale/Scope**: Todas as rotas da API, endpoints públicos e renderizador de fichamentos  

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Princípio I: Proteção Absoluta do Acervo e Privacidade de Dados**: PASS. A feature impede vazamento de dados do acervo via injeção de scripts (XSS), injeção SQL ou mensagens de erro detalhadas.
- **Princípio II: Isolamento Estrito de Testes e Operações Locais**: PASS. Todas as novas suítes de teste de segurança rodam contra instâncias descartáveis e bancos temporários em `tmp_path`, sem tocar em `backend/data/caderno.db`.
- **Princípio III: Fidelidade Arquitetural e Tecnológica**: PASS. Mantém a stack Python 3.13, FastAPI, Vue 3, TypeScript, Uvicorn e SQLite local WAL sem inclusão de serviços em nuvem ou dependências pagas.
- **Princípio IV: Governança por Especificação Delimitada (Spec-Driven Development)**: PASS. O ciclo segue rigorosamente a sequência Spec Kit (`specify` → `clarify` → `plan` → `tasks` → `analyze` → `implement`).
- **Princípio V: Resiliência Operacional, Transações e Migrações Seguras**: PASS. Zero alterações estruturais no schema existente; configurações de segurança são puramente defensivas e seguras por padrão.

---

## Project Structure

### Documentation (this feature)

```text
specs/048-seguranca-aplicacao-dados/
├── plan.md              # Este documento de planejamento técnico
├── research.md          # Decisões arquiteturais D1 a D6
├── data-model.md        # Modelos de configuração e contratos de segurança
├── quickstart.md        # Cenários executáveis de validação
├── contracts/           # Contrato OpenAPI dos cabeçalhos e erro 500
│   └── security-headers-api.yaml
├── checklists/          # Checklist de qualidade dos requisitos
│   └── requirements.md
└── tasks.md             # Tarefas atômicas (próxima fase: /speckit-tasks)
```

### Source Code Touched

```text
caderno-leitura-0.1/
├── backend/
│   ├── app/
│   │   ├── core/
│   │   │   ├── config.py             # Configurações de CORS e segredo de sessão
│   │   │   └── security_headers.py   # Middleware de cabeçalhos de segurança e CSP
│   │   ├── errors.py                 # Exception handler global 500 com error_id
│   │   ├── frontend.py               # Bloqueio estrito de arquivos sensíveis (.env, .db)
│   │   ├── main.py                   # Registro de middlewares e auditoria no lifespan
│   │   └── schemas/
│   │       └── security.py           # Schema SecurityErrorResponse
│   └── tests/
│       ├── test_security_headers_and_csp.py   # Validação de cabeçalhos e CSP
│       ├── test_security_error_masking.py     # Validação de mascaramento 500
│       ├── test_security_sql_injection.py     # Testes de estresse contra SQLi
│       └── test_security_static_blocking.py   # Bloqueio de arquivos sensíveis
│
└── frontend/
    ├── src/
    │   ├── services/
    │   │   ├── markdown.ts           # Validação estrita de protocolos de link
    │   │   └── sanitizer.ts          # Sanitizador leve e seguro de tags HTML
    │   └── components/
    │       └── MarkdownContent.vue   # Integração da sanitização antes do v-html
    └── tests/
        └── security_xss_sanitization.test.mjs # Testes unitários de neutralização XSS
```

---

## Phase 0: Outline & Research

- Todas as decisões técnicas foram consolidadas em [research.md](./research.md):
  - D1: Sanitização em duas camadas (parser + DOM) preservando leitura ativa.
  - D2: CSP em modo *Enforce* com diretivas compatíveis com Vue, Google Identity e fontes.
  - D3: CORS restrito por ambiente (same-origin padrão, parametrizável via `CADERNO_CORS_ORIGINS`).
  - D4: Exception handler global 500 com correlação de logs via `error_id` UUID.
  - D5: Auditoria e parametrização estrita em todas as consultas SQL.
  - D6: Bloqueio estrito de arquivos estáticos ocultos/sensíveis e verificação da chave de sessão.

---

## Phase 1: Design & Contracts

- Modelos e contratos especificados em [data-model.md](./data-model.md) e [contracts/security-headers-api.yaml](./contracts/security-headers-api.yaml).
- Cenários de validação rápida documentados em [quickstart.md](./quickstart.md).
- Re-avaliação da Constituição: **100% CONFORME**. Pronto para geração de tarefas (`/speckit-tasks`).
