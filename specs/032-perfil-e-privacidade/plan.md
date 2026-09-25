# Implementation Plan: Perfil e Privacidade

**Branch**: `032-perfil-e-privacidade` | **Date**: 2026-09-24 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/032-perfil-e-privacidade/spec.md`

---

## Summary

Implementar a identidade pública do leitor e governança de privacidade no Caderno de Leitura:
- Modelo relacional `UserProfile` (1:1 com `users`) com suporte a `@username` único (case-insensitive, 3-30 caracteres alfanuméricos), nome de exibição, biografia (até 280 caracteres) e controle de visibilidade desacoplado para Perfil e Dashboard (`public`, `friends`, `private`).
- Processamento e upload seguro de avatares com validação de formato (PNG/JPEG/WebP até 2MB), normalização EXIF e recorte centralizado quadrado (256x256 WebP) salvo localmente em `backend/data/avatars/`, com suporte a reaproveitamento de foto da conta Google e fallback em iniciais estilizadas no sistema visual.
- Blindagem total contra vazamento de e-mails em requisições e páginas públicas, suporte a perfil descobrível em buscas (`is_discoverable`) e exibição de cartão seguro e discreto para perfis restritos.

---

## Technical Context

**Language/Version**: Python 3.13 (FastAPI 0.141.1, SQLAlchemy 2.0.52, Alembic 1.19.2, Pillow >= 10.0.0), TypeScript 5.9+ (Vue 3, Vite, Tailwind/CSS)  
**Primary Dependencies**: FastAPI, SQLAlchemy 2.0, Alembic, Pillow, python-multipart, Vue 3, Pinia, Lucide icons  
**Storage**: SQLite local (WAL), diretório local de mídia `backend/data/avatars/`  
**Testing**: pytest com TestClient hermético e bancos descartáveis em `tmp_path`; Node.js test runner (`npm test`) e auditoria visual (`visual_system.test.mjs`)  
**Target Platform**: Windows 11 (servidor local único via `iniciar.py`) atendendo PC e dispositivos móveis via rede local/Tailscale  
**Project Type**: Aplicação Web híbrida (API REST FastAPI + SPA Vue 3)  
**Performance Goals**: < 50ms para resolução de perfis públicos; < 200ms para upload, processamento gráfico e persistência de avatar; 0 vazamento de e-mails  
**Constraints**: Zero emojis informais (uso exclusivo de Lucide SVG); alvos de toque mínimos de 44px; isolamento absoluto do acervo de produção (`backend/data/caderno.db`)  
**Scale/Scope**: Ambiente local e multi-dispositivo; perfis individuais com suporte a busca local de leitores  

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Artigo Constitucional | Regra / Diretriz | Status | Justificativa |
|---|---|:---:|---|
| **I. Proteção do Acervo e Privacidade** | Zero vazamento de dados privados ou e-mails no chat ou na API pública | **PASS** | Schemas públicos (`UserProfilePublicRead`, `UserSearchItem`) não possuem o campo `email`. Respostas públicas mascaram bio e estudos quando restrito. |
| **II. Isolamento Estrito de Testes** | Nenhuma suíte pode tocar no banco `caderno.db` | **PASS** | Todos os testes utilizam fixtures com SQLite em `tmp_path` e diretório temporário para upload de avatares. |
| **III. Fidelidade Arquitetural** | Python 3.13, FastAPI, SQLAlchemy 2.0, Alembic, Vue 3, SQLite WAL | **PASS** | Tecnologias canônicas preservadas integralmente. Processamento gráfico via Pillow já presente nas dependências. |
| **IV. Governança por SDD** | Fatias atômicas e fluxo Spec Kit delimitado | **PASS** | Ciclo formal 032-perfil-e-privacidade seguido rigorosamente. |
| **V. Resiliência Operacional e Migrações** | Migração segura e consistente | **PASS** | Migração Alembic `0015_add_user_profile.py` inclui auto-provisionamento para contas existentes sem perda de dados. |

---

## Project Structure

### Documentation (this feature)

```text
specs/032-perfil-e-privacidade/
├── spec.md                  # Especificação funcional com decisões de clarificação
├── plan.md                  # Este documento de planejamento técnico
├── research.md              # Pesquisa técnica e decisões de arquitetura consolidadas
├── data-model.md            # Modelo de dados relacional e schemas Pydantic
├── quickstart.md            # Guia de validação e cenários executáveis
├── contracts/
│   ├── profile-api.yaml     # Contrato OpenAPI 3.0 dos endpoints de perfil
│   └── privacy-matrix.md    # Matriz detalhada de visibilidade e autorização
└── checklists/
    └── requirements.md      # Checklist de qualidade validado
```

### Source Code Layout

```text
caderno-leitura-0.1/
├── backend/
│   ├── app/
│   │   ├── core/
│   │   │   └── config.py               # get_avatars_dir()
│   │   ├── models/
│   │   │   ├── __init__.py             # Export de UserProfile
│   │   │   ├── user.py                 # Relacionamento 1:1 com UserProfile
│   │   │   └── user_profile.py         # Modelo ORM UserProfile
│   │   ├── schemas/
│   │   │   └── profile.py              # Schemas Pydantic (Public/PrivateRead, Update)
│   │   ├── services/
│   │   │   ├── profile_service.py      # Resolução de visibilidade, busca e gestão
│   │   │   └── avatar_service.py       # Validação, corte quadrado e descarte
│   │   ├── routers/
│   │   │   ├── profile.py              # GET/PUT /api/profile/me, POST/DELETE avatar
│   │   │   └── users.py                # GET /api/users/{username}, GET /api/users
│   │   └── main.py                     # Registro dos routers de perfil e avatares
│   ├── migrations/versions/
│   │   └── 0015_add_user_profile.py    # Migração Alembic com auto-provisionamento
│   └── tests/
│       └── test_profile_and_privacy.py # Suíte de testes hermética
└── frontend/
    └── src/
        ├── types/
        │   ├── profile.ts              # Tipagens TypeScript para perfil e privacidade
        │   └── index.ts / types.ts     # Re-export central
        ├── api/
        │   └── profile.ts              # Cliente HTTP para rotas de perfil e busca
        ├── composables/
        │   └── useProfile.ts           # Composable reativo de perfil e privacidade
        ├── components/
        │   └── profile/
        │       ├── AvatarUploadModal.vue # Modal acessível de upload/recorte de avatar
        │       └── UserProfileCard.vue   # Card de perfil público com selo discreto
        └── views/
            ├── SettingsView.vue        # Seção de perfil público e visibilidade
            └── UserProfileView.vue     # Página pública do leitor (/@username)
```

---

## Complexity Tracking

| Componente | Complexidade | Justificativa |
|---|---|---|
| Recorte gráfico quadrado de avatar | Média | Uso de Pillow `ImageOps.fit` já instalado no ambiente, evitando upload de imagens desproporcionais ou pesadas. |
| Desacoplamento Perfil vs Dashboard | Baixa | Dois enums independentes no banco e no schema, permitindo controle granular sem complexidade excessiva. |
| Auto-provisionamento na migração | Baixa | Comando `INSERT INTO user_profiles ... SELECT` garante que contas existentes na migração já possuam perfil imediatamente. |
