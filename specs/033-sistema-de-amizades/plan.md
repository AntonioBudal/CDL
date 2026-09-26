# Implementation Plan: F06 — Sistema de Amizades

**Branch**: `033-sistema-de-amizades` | **Date**: 2026-09-25 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/033-sistema-de-amizades/spec.md`

## Summary

Implementar a infraestrutura de conexão social entre usuários no Caderno de Leitura, provendo ciclo de vida completo de solicitações de amizade (envio, aceite, recusa, cancelamento e desfazimento), proteção estrita contra contato indesejado (bloqueio bilateral com blindagem anti-enumeração e exclusão de buscas), contagem quantitativa de amigos no perfil público e um Hub Social dedicado com rota `/amigos` na navegação global do sistema.

## Technical Context

**Language/Version**: Python 3.13 (Backend), TypeScript 5.6+ / Node.js (Frontend).

**Primary Dependencies**: FastAPI, SQLAlchemy 2.0 (Declarative), Alembic, Pydantic v2, Uvicorn (Backend); Vue 3 (Composition API), Vite, Tailwind/CSS (Frontend).

**Storage**: SQLite local em modo Write-Ahead Logging (WAL) com chaves estrangeiras (`PRAGMA foreign_keys = ON`), transações atômicas com `commit_changes()` e commits explícitos. Nova tabela relacional `friendships`.

**Testing**: `pytest` com bancos descartáveis em `tmp_path` (Backend); `node:test` (`npm test`) e `vue-tsc` / `vite build` (Frontend).

**Target Platform**: Windows local (PowerShell, Uvicorn em processo único via `iniciar.py`) atendendo PC e dispositivos móveis (Tailscale).

**Project Type**: Aplicação Web local híbrida (FastAPI REST API + Vue 3 SPA).

**Performance Goals**: Resposta de endpoints sociais em menos de 100ms em SQLite local; transição e feedback de ações na interface em menos de 300ms.

**Constraints**: Isolamento estrito de produção (zero impacto em `backend/data/caderno.db`), blindagem anti-IDOR/anti-enumeração (HTTP 404 em usuários bloqueados), alvos táteis mínimos de 44x44px no mobile e acessibilidade WAI-ARIA para navegação por abas.

**Scale/Scope**: Multiusuário local e em rede privada com dezenas a centenas de conexões por leitor.

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

1. **Proteção Absoluta do Acervo e Privacidade de Dados**:
   - Status: **PASS**.
   - Justificativa: Nenhuma informação pessoal ou textual de estudos é compartilhada nesta feature. O e-mail continua rigorosamente protegido e nunca é exposto nas buscas ou listagens de amigos.
2. **Isolamento Estrito de Testes e Operações Locais**:
   - Status: **PASS**.
   - Justificativa: Todos os testes automatizados utilizam exclusivamente bancos SQLite efêmeros em `tmp_path`, mantendo `backend/data/caderno.db` intocado.
3. **Fidelidade Arquitetural e Tecnológica**:
   - Status: **PASS**.
   - Justificativa: Utiliza Python 3.13, FastAPI, SQLAlchemy 2.0 com ORM moderno, migração declarativa Alembic e Vue 3 com TypeScript estrito.
4. **Governança por Especificação Delimitada (Spec-Driven Development)**:
   - Status: **PASS**.
   - Justificativa: O desenvolvimento segue rigorosamente o ciclo do Spec Kit, partindo de `spec.md` validada com checklist de qualidade 100% aprovado.
5. **Resiliência Operacional, Transações e Migrações Seguras**:
   - Status: **PASS**.
   - Justificativa: Nova migração Alembic incremental (`0016_add_friendships_table.py`) com criação defensiva de índices e rollback seguro.

---

## Project Structure

### Documentation (this feature)

```text
specs/033-sistema-de-amizades/
├── spec.md              # Especificação aprovada com requisitos e critérios de aceite
├── plan.md              # Este plano de implementação
├── research.md          # Decisões técnicas consolidadas (par ordenado, bloqueio, etc.)
├── data-model.md        # Esquema relacional da tabela friendships e schemas Pydantic
├── quickstart.md        # Guia de validação executável em bancos efêmeros
├── contracts/
│   └── friends-api.md   # Contratos REST de /api/friends e endpoints sociais
├── checklists/
│   └── requirements.md  # Checklist de qualidade da especificação (100% PASS)
└── tasks.md             # Tarefas atômicas geradas pelo /speckit-tasks
```

### Source Code Layout

```text
caderno-leitura-0.1/
├── backend/
│   ├── app/
│   │   ├── models/
│   │   │   └── friendship.py         # Modelo relacional Friendship
│   │   ├── schemas/
│   │   │   └── friendship.py         # Schemas de validação e DTOs de amigos
│   │   ├── services/
│   │   │   └── friendship_service.py # Regras de negócio, transições e queries sociais
│   │   └── routers/
│   │       ├── friends.py            # Rotas REST /api/friends
│   │       └── users.py              # Ajuste em busca/perfil com status de amizade e bloqueio
│   ├── migrations/versions/
│   │   └── 0016_add_friendships.py   # Migração Alembic incremental
│   └── tests/
│       └── test_friendships.py       # Suíte hermética em tmp_path
└── frontend/
    └── src/
        ├── types.ts                  # Interfaces TypeScript para amigos e solicitações
        ├── services/
        │   └── api.ts                # Métodos HTTP para /api/friends
        ├── composables/
        │   └── useFriends.ts         # Estado reativo e ações sociais
        ├── components/
        │   └── FriendActionButtons.vue # Botões contextuais de ação social (conectar, aceitar, bloquear)
        ├── views/
        │   ├── FriendsView.vue       # Hub Social com abas (Amigos, Solicitações, Bloqueados, Descobrir)
        │   └── UserProfileView.vue   # Exibição de contagem de amigos e botão contextual
        └── App.vue                   # Item de menu /amigos com badge de pendências
```

## Complexity Tracking

> Nenhuma violação das regras constitucionais identificada. A estrutura relacional de par ordenado normalizado reduz a complexidade física do SQLite e garante transações atômicas seguras.
