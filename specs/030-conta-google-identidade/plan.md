# Implementation Plan: Conta Google e Vinculação de Identidade (F03)

**Branch**: `main` | **Date**: 2026-09-22 | **Spec**: [specs/030-conta-google-identidade/spec.md](spec.md)

**Input**: Feature specification from `/specs/030-conta-google-identidade/spec.md`

## Summary

Esta feature adiciona suporte ao fluxo de autenticação e identificação via **Google Identity Services (GIS)** utilizando tokens de identidade OpenID Connect (ID Token JWT). O backend valida os tokens criptograficamente utilizando a biblioteca oficial `google-auth` (`google.oauth2.id_token.verify_oauth2_token`) com cache de certificados públicos (JWKS).
As identidades externas vinculadas são persistidas na nova tabela `external_identities`, garantindo unicidade do identificador imutável `sub` (`provider_subject`), suporte a vinculação automática por e-mail verificado, proteção contra *lockout* (impedindo desvinculação se não houver senha local configurada), e degradação graciosa para o modo local na ausência de `GOOGLE_CLIENT_ID`. Imagens de perfil/avatares externos são estritamente postergados para a Feature 05 (Perfil e Privacidade) para salvaguardar a soberania de dados do usuário.

---

## Technical Context

**Language/Version**: Python 3.13 (64-bit) no backend; TypeScript 5.x / Vue 3.5+ no frontend (Node.js 24).  
**Primary Dependencies**:
- Backend: `fastapi`, `sqlalchemy` 2.0, `alembic`, `pydantic` v2, `argon2-cffi`, `google-auth` (para validação segura e hermética do ID Token do Google).
- Frontend: `vue`, `vue-router`, `lucide-vue-next` (ícones estritos, proibido o uso de emojis informais), `@types/google.accounts` (para tipagem TypeScript do GIS).  
**Storage**: SQLite local com modo WAL ativado, `PRAGMA foreign_keys = ON`, nova tabela `external_identities` com chave estrangeira para `users(id)` com `ON DELETE CASCADE`.  
**Testing**:
- Backend: `pytest` com fixtures herméticas (bancos efêmeros SQLite via `tmp_path`, mock de `verify_oauth2_token` sem chamadas de rede externas).
- Frontend: `npm test` e `npm run build` (validação de tipos, regras de acessibilidade e checagem do visual system).  
**Target Platform**: Servidor local em processo único no Windows 10/11 (`iniciar.py`), acessível localmente e via rede privada/Tailscale.  
**Project Type**: Aplicação Web cliente-servidor (FastAPI REST API + Vue 3 Single Page Application).  
**Performance Goals**:
- Latência de autenticação do Google < 100ms após validação de cache de chaves públicas.
- Sem bloqueio de inicialização ou latência de rede quando executado offline ou sem credenciais Google configuradas.  
**Constraints**:
- Zero dependência externa obrigatória: se `GOOGLE_CLIENT_ID` não estiver definido, o frontend não injeta o SDK do Google e a aplicação funciona 100% offline com credenciais locais.
- Isolamento absoluto: testes automatizados nunca disparam requisições HTTP para a infraestrutura do Google.
- Prevenção contra *lockout*: um usuário não pode desvincular seu único método de login (deve possuir senha local antes de desvincular a conta Google).
- Conformidade estética: conformidade total com `frontend/tests/visual_system.test.mjs` (ícones do Lucide em substituição a emojis).  
**Scale/Scope**: Sistema multiusuário local/pessoal (instância única, até centenas de usuários locais).

---

## Constitution Check

*GATE: Avaliado antes da Fase 0 e revalidado após o design da Fase 1.*

| Artigo Constitucional | Avaliação | Status | Justificativa / Conformidade |
| :--- | :---: | :---: | :--- |
| **I. Proteção do Acervo e Privacidade** | Preservação Total | **PASS** | Nenhum dado de livros, capítulos ou notas é acessado ou exposto pelo fluxo de autenticação. Avatares e fotos do Google não são importados nem salvos no banco local nesta etapa (postergados para a F05), mantendo estrita soberania e privacidade local. |
| **II. Isolamento de Testes e Operações** | Isolamento Estrito | **PASS** | Testes de integração utilizam bancos efêmeros em `tmp_path`. Chamadas de validação de token do Google são hermeticamente mockadas com `unittest.mock`, impedindo qualquer tráfego externo ou gravação no banco de produção `caderno.db`. |
| **III. Fidelidade Arquitetural** | Padrões Mantidos | **PASS** | Uso do SQLAlchemy 2.0, FastAPI DI (`get_db`, `get_current_user`), migração formal Alembic (`0013`), Vue 3 Composition API com `<script setup>`, TypeScript estrito e conformidade visual com regras de design system (Lucide icons). |
| **IV. Governança por SDD** | Ciclo Formal | **PASS** | Ciclo formal `speckit.specify` -> `speckit.clarify` -> `speckit.plan` -> `speckit.tasks` -> `speckit.analyze` -> `speckit.implement`. 1 Feature = 1 Commit. F03 isolada de features futuras. |
| **V. Resiliência Operacional e Migrações** | Migração Segura | **PASS** | Nova migração `0013_add_external_identities.py` aditiva e 100% reversível (`downgrade` limpo). Schema validado com integridade referencial `ON DELETE CASCADE`. |

---

## Project Structure

### Documentation (this feature)

```text
specs/030-conta-google-identidade/
├── spec.md                  # Especificação funcional refinada com requisitos e esclarecimentos
├── checklists/
│   └── requirements.md      # Checklist de qualidade dos requisitos (16/16 aprovados)
├── research.md              # Decisões de arquitetura e tecnologia (Phase 0)
├── data-model.md            # Modelo de dados, esquema ER e especificação da migração Alembic (Phase 1)
├── contracts/
│   ├── google-auth-api.yaml # Especificação OpenAPI 3.1 para /api/auth/google, /link e /unlink
│   └── google-flow.md       # Diagramas de sequência Mermaid dos fluxos de login e vinculação
├── quickstart.md            # Guia de validação ponta a ponta e cenários de teste (Phase 1)
├── plan.md                  # Este plano de implementação
└── tasks.md                 # Decomposição detalhada de tarefas (Phase 2 - speckit-tasks)
```

### Source Code (repository root)

```text
caderno-leitura-0.1/
├── backend/
│   ├── alembic/
│   │   └── versions/
│   │       └── 0013_add_external_identities.py    # Migração para tabela external_identities
│   ├── app/
│   │   ├── core/
│   │   │   ├── config.py                          # Configurações GOOGLE_CLIENT_ID e GOOGLE_AUTH_ENABLED
│   │   │   └── security.py                        # Helpers de sessão e segurança
│   │   ├── models/
│   │   │   ├── __init__.py                        # Export do ExternalIdentity
│   │   │   ├── user.py                            # Relacionamento users.external_identities
│   │   │   └── external_identity.py               # Novo modelo ORM ExternalIdentity
│   │   ├── schemas/
│   │   │   └── auth.py                            # Schemas Pydantic GoogleAuthRequest, AuthConfigResponse, UserRead
│   │   ├── services/
│   │   │   ├── auth_service.py                    # Lógica de login Google, link, unlink, auto-link e lockout prevention
│   │   │   └── google_auth_service.py             # Validação hermética com google.oauth2.id_token
│   │   └── routers/
│   │       └── auth.py                            # Rotas POST /google, POST /google/link, DELETE /google/unlink
│   ├── requirements.in                            # Inclusão de google-auth>=2.27.0
│   ├── requirements.txt                           # Dependências compiladas atualizadas
│   └── tests/
│       ├── conftest.py                            # Fixtures e mocks para google-auth
│       └── test_google_auth.py                    # Testes unitários e de integração herméticos da F03
│
└── frontend/
    └── src/
        ├── api/
        │   └── auth.ts                            # Funções de cliente HTTP para autenticação e vinculação Google
        ├── composables/
        │   ├── useAuth.ts                         # Estado reativo de autenticação e flag has_google
        │   └── useGoogleIdentity.ts               # Carregador assíncrono e gerenciador de eventos do SDK GIS
        ├── components/
        │   └── auth/
        │       ├── GoogleSignInButton.vue         # Renderizador do botão GIS oficial e estado de fallback
        │       └── SessionsManager.vue            # Seção de gerenciamento de vinculação Google e prevenção de lockout
        ├── views/
        │   ├── LoginView.vue                      # Inclusão do botão Google com separador visual
        │   └── RegisterView.vue                   # Inclusão de cadastro rápido via Google (quando permitido)
        └── types/
            └── auth.ts                            # Interfaces TypeScript atualizadas (has_google, ExternalIdentity)
```

**Structure Decision**: A aplicação segue a arquitetura web monorepo estabelecida (`caderno-leitura-0.1/backend` e `caderno-leitura-0.1/frontend`), mantendo total separação entre camada de persistência/API e camada cliente SPA.

---

## Complexity Tracking

| Decisão Arquitetural | Por que é necessária? | Alternativa mais simples rejeitada porque: |
| :--- | :--- | :--- |
| **Tabela separada `external_identities`** | Permite vincular identidades com seus metadados de forma extensível (`provider`, `provider_subject`, `email_at_link`) sem poluir a tabela `users`. | Adicionar colunas `google_id` e `google_email` na tabela `users` foi rejeitado por violar o princípio de extensibilidade (futuros provedores OIDC ou múltiplas identidades) e acoplar a entidade User a um provedor específico. |
| **Biblioteca oficial `google-auth`** | Valida automaticamente assinaturas RS256, rotação de chaves públicas do Google (JWKS), expiração, audiência (`aud`) e emissor (`iss`). | Validar manualmente via PyJWT exigiria reimplementar caching de chaves públicas, tratamento de rotação e requisições HTTP manuais propensas a falhas de segurança. |
| **SDK oficial do Google Identity Services (GIS) no frontend** | Proporciona experiência One Tap / botão oficial nativo com total conformidade de marca e segurança de token pelo Google. | Fluxo manual OAuth2 Authorization Code com redirecionamento de tela inteira foi rejeitado por ser excessivamente complexo para uma aplicação local (exigiria configuração de URIs de callback no console Google para múltiplos IPs locais/Tailscale). |
