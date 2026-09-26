# Implementation Plan: F07 — Compartilhamento e Permissões por Recurso (ACL)

**Branch**: `034-compartilhamento-permissoes` | **Date**: 2026-09-26 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/034-compartilhamento-permissoes/spec.md`

---

## Summary

Implementar a infraestrutura completa de compartilhamento granular e controle de acesso (ACL) para livros e estudos no Caderno de Leitura. O leitor proprietário poderá definir a visibilidade dos seus recursos entre Privado, Amigos, Customizado (lista nominal por `@username`) e Público (para usuários autenticados com o link). A experiência de convidados é blindada sob o princípio inegociável de **somente-leitura (Read-Only)**, com resolução automática de herança livro-estudo, respeito estrito aos bloqueios mútuos/unilaterais (F06) e uma aba dedicada "Compartilhados Comigo" na Biblioteca.

---

## Technical Context

**Language/Version**: Python 3.13 (Backend) | TypeScript ~6.0 / JavaScript ES2024 (Frontend)

**Primary Dependencies**: 
- Backend: FastAPI, SQLAlchemy 2.0 (ORM moderno), Alembic, Pydantic v2, Uvicorn.
- Frontend: Vue 3 (Composition API `<script setup>`), Vite, Lucide Vue Next, `markdown-it`.

**Storage**: SQLite local em modo Write-Ahead Logging (WAL), com chaves estrangeiras ativadas (`PRAGMA foreign_keys = ON`). Isolamento estrito de testes via `tmp_path`.

**Testing**: 
- Backend: `pytest` com bancos descartáveis temporários e cliente de teste (`TestClient`).
- Frontend: `node:test` para testes unitários e de integração, `vue-tsc -b` para validação de tipos.

**Target Platform**: Windows 10/11 local com suporte a acesso remoto via rede local / Tailscale para dispositivos móveis (Android/iOS).

**Project Type**: Web Application monorepo local (`caderno-leitura-0.1`).

**Performance Goals**:
- Resolução de permissão e visibilidade de estudo em menos de 5ms por requisição no SQLite.
- Carregamento e renderização do modal de compartilhamento em menos de 100ms.
- Consulta ao feed de recursos compartilhados (`GET /api/shared/studies`) em menos de 20ms para acervos com milhares de estudos.

**Constraints**:
- **Somente-leitura Inviolável**: Convidados jamais podem modificar, renomear, comentar ou excluir estudos de terceiros.
- **Blindagem Anti-Enumeração**: Usuários não autorizados ou bloqueados recebem invariavelmente `404 Not Found`.
- **Zero Impacto no Acervo Ativo**: Nenhuma execução de teste ou ferramenta toca em `backend/data/caderno.db`.

**Scale/Scope**: Múltiplos leitores em rede doméstica/Tailscale; suporte a compartilhamentos individuais ou coletivos com amigos.

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **I. Proteção Absoluta do Acervo e Privacidade de Dados**: O banco ativo `backend/data/caderno.db` não é acessado durante o planejamento ou testes. Nenhum dado privado do usuário é exposto.
- [x] **II. Isolamento Estrito de Testes e Operações Locais**: Todos os testes unitários e de integração usam diretórios temporários (`tmp_path`) e portas efêmeras.
- [x] **III. Fidelidade Arquitetural e Tecnológica**: Mantida a stack padrão (Python 3.13, FastAPI, SQLAlchemy 2, Alembic, Vue 3, Vite, SQLite).
- [x] **IV. Governança por Especificação Delimitada (Spec-Driven Development)**: A feature segue o ciclo formal de Spec Kit (`speckit.specify` → `speckit.clarify` → `speckit.plan` → `speckit.tasks` → `speckit.implement`).
- [x] **V. Resiliência Operacional, Transações e Migrações Seguras**: A migração Alembic adiciona colunas com defaults seguros (`private` e `inherit`) e cria tabela relacional com integridade referencial completa.

---

## Project Structure

### Documentation (this feature)

```text
specs/034-compartilhamento-permissoes/
├── spec.md              # Especificação e requisitos funcionais validados
├── plan.md              # Este plano de implementação
├── research.md          # Decisões arquiteturais fundamentadas
├── data-model.md        # Esquema relacional, modelos e migração Alembic
├── quickstart.md        # Roteiro de validação end-to-end
├── contracts/
│   └── shared-resources-api.md  # Contratos REST de permissões e compartilhamento
└── checklists/
    └── requirements.md  # Checklist de conformidade e qualidade
```

### Source Code (caderno-leitura-0.1)

```text
backend/
├── app/
│   ├── models/
│   │   ├── book.py                    # Adição do campo 'visibility'
│   │   ├── study.py                   # Adição do campo 'visibility'
│   │   └── resource_permission.py     # Novo modelo relacional de ACL nominal
│   ├── schemas/
│   │   ├── sharing.py                 # Novos schemas Pydantic de ACL e recursos compartilhados
│   │   ├── book.py                    # Atualização de BookRead com visibility
│   │   └── study.py                   # Atualização de StudyRead com visibility e can_edit
│   ├── services/
│   │   ├── sharing_service.py         # Resolução de visibilidade, herança, ACL e blindagem
│   │   ├── study_service.py           # Integração com can_read_study e proteção Read-Only
│   │   └── book_service.py            # Integração com can_read_book
│   └── routers/
│       ├── sharing.py                 # Endpoints /api/shared/studies e /api/shared/books
│       ├── studies.py                 # Endpoints de gestão de permissão /api/studies/{id}/permissions
│       └── books.py                   # Endpoints de gestão de visibilidade do livro
├── alembic/versions/
│   └── 0017_add_sharing_and_permissions.py  # Migração relacional Alembic
└── tests/
    └── test_sharing_and_permissions.py      # Suíte completa de testes automatizados

frontend/src/
├── api/
│   └── sharing.ts                     # Cliente tipado para endpoints de compartilhamento
├── components/
│   ├── sharing/
│   │   └── ShareModal.vue             # Modal acessível de compartilhamento e gestão de ACL
│   └── library/
│       └── SharedStudiesList.vue      # Listagem de estudos na aba "Compartilhados Comigo"
├── views/
│   ├── LibraryView.vue                # Adição do alternador de abas [Meu Acervo | Compartilhados]
│   └── StudyView.vue                  # Banner de somente-leitura e bloqueio de mutações para convidados
└── tests/
    └── sharing.test.mjs               # Testes de componentes e contratos de frontend
```

---

## Phase 0: Research Summary

Todas as decisões arquiteturais foram consolidadas em [research.md](./research.md):
1. **Modelo Híbrido**: Colunas de visibilidade (`private`, `friends`, `public`, `inherit`) + Tabela de ACL nominal (`resource_permissions`) para modo `custom`.
2. **Resolução Determinística**: `can_read_study()` avalia propriedade, bloqueios, herança livro-estudo, amizade e ACL, retornando `404 Not Found` em falhas para blindagem anti-enumeração.
3. **Somente-Leitura Inviolável**: Camada dupla (bloqueio de verbos HTTP no backend + interface adaptativa sem botões de edição no frontend).
4. **Ergonomia e Centralização**: Aba dedicada "Compartilhados Comigo" integrada à Biblioteca (`LibraryView`), conforme escolha Q2: A do leitor.
5. **Autenticação Obrigatória**: Recursos públicos acessíveis exclusivamente para usuários cadastrados e autenticados (conforme Q3: A).

---

## Phase 1: Design Artifacts

Os artefatos técnicos da Fase 1 foram gerados e validados:
- **Modelo de Dados e Migração**: [data-model.md](./data-model.md)
- **Contratos de Interface e Endpoints**: [contracts/shared-resources-api.md](./contracts/shared-resources-api.md)
- **Guia de Validação e Execução**: [quickstart.md](./quickstart.md)

---

## Próximos Passos

1. Submeter o plano para aprovação do usuário.
2. Gerar a lista de tarefas atômicas e ordenadas com `/speckit-tasks`.
