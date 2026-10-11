# Implementation Plan: F0.8.06 — Amigos: Salão Literário e Círculos de Estudo

**Branch**: `071-amigos-salao-literario` | **Date**: 2026-10-11 | **Spec**: [spec.md](file:///c:/Users/User/caderno/specs/071-amigos-salao-literario/spec.md)

**Input**: Feature specification from `specs/071-amigos-salao-literario/spec.md`

---

## Summary

Transformar a tela `/amigos` do Leitorum em uma experiência de **Salão Literário e Círculos de Estudo**, substituindo o aspecto de CRUD genérico por um ateliê de correspondência intelectual e descoberta mútua de leitores.
A solução técnica implementa:
1. O componente permanente no topo `BookplateCard.vue` (*Ex-Líbris Digital do Leitor*), exibindo avatar, nome de exibição, bio literária, contadores de afinidade e o `@identificador` do leitor.
2. A microinteração do **Selo de Cópia Confirmada** com transição acelerada por GPU (`transform: scale(1.04)` e classe `.is-stamped`), esmaecendo suavemente em exatamente 1200ms.
3. Compartilhamento móvel nativo via **Web Share API** (`navigator.share`) com fallback para cópia rápida do link do perfil público (`/u/:username`) em navegadores de desktop.
4. Redesenho dos cartões de amizade em **Cartas de Conexão Literária**, apresentando data formatada em português, link direto para a estante do leitor e botões contextuais (`FriendActionButtons.vue`) com alvos táteis $\ge 44 \times 44$px.
5. Navegação segmentada por 4 abas com contadores dinâmicos (`Círculo de Leitura`, `Solicitações`, `Descobrir Leitores`, `Bloqueados`), com acessibilidade completa WAI-ARIA (`role="tablist"` / `role="tab"`).
6. Estados vazios acolhedores ("Círculo em Formação"), sugestões intelectuais na aba de descoberta e 100% de conformidade aos 10 temas visuais do Leitorum (imunidade cromática estrita e zero emojis).

---

## Technical Context

**Language/Version**: TypeScript 5.6+ (Strict mode), Vue 3.5 (Composition API, `<script setup>`), Vite. Backend: Python 3.13 (FastAPI, SQLAlchemy 2.0, Alembic, SQLite WAL).

**Primary Dependencies**: Vue 3, Vue Router, `@vue/test-utils` / `node:test`. Backend inalterado (`friends.py` e `profile.py`). Zero novas dependências de runtime.

**Storage**: SQLite local (`backend/data/caderno.db` em produção; efêmero/isolado em testes). Tabelas existentes `friendships`, `users`, `user_profiles`. Nenhuma alteração de schema ou migração de banco é necessária.

**Testing**: Suíte de testes do frontend com `node:test` (`frontend/tests/friends.test.mjs`, `frontend/tests/feature-071-amigos-salao-literario.test.mjs`), build de produção com verificação estrita de tipos (`npm run build`), e suíte de backend (`pytest backend/tests`).

**Target Platform**: Aplicação web local responsiva para desktop e dispositivos móveis (Windows local, Tailscale, PWA).

**Project Type**: Web application (Frontend SPA em Vue 3 + Backend API FastAPI local em processo único).

**Performance Goals**: Microinteração do selo concluída em exatamente 1200ms a 60 FPS acelerada por GPU; resposta de busca debounced de 300ms; carregamento inicial de `/amigos` < 300ms.

**Constraints**: Imunidade Cromática (consumo estrito dos tokens CSS dos 10 temas, banimento de hexadecimais fixos); Zero emojis; Acessibilidade WAI-ARIA com alvos táteis móveis $\ge 44 \times 44$px; Sem alteração no backend; Preservação absoluta da privacidade do acervo.

**Scale/Scope**: 1 componente novo (`BookplateCard.vue`), 1 view redesenhada (`FriendsView.vue`), 1 componente estilizado e reutilizado (`FriendActionButtons.vue`), 1 novo teste de contrato (`feature-071-amigos-salao-literario.test.mjs`).

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Artigo da Constituição | Descrição do Princípio | Status | Justificativa / Validação |
|---|---|---|---|
| **I. Proteção Absoluta do Acervo** | Proibição de exposição do acervo real do usuário e preservação de dados. | **PASS** | Nenhum dado real de usuários ou acervo é lido ou exposto; testes usam dados sintéticos. |
| **II. Isolamento Estrito de Testes** | Zero impacto no banco ativo; bancos efêmeros e descartáveis. | **PASS** | Testes de unidade operam em memória e mocks; testes de backend usam `tmp_path`. |
| **III. Fidelidade Arquitetural** | FastAPI, Vue 3 (`<script setup>`, TS estrito), SQLite WAL, processo único. | **PASS** | Tecnologias respeitadas rigorosamente; zero dependências externas adicionadas. |
| **IV. Governança por SDD** | Fatias delimitadas e ciclo formal Spec Kit. | **PASS** | Etapa formal `speckit.plan` em execução, sem avançar para tarefas ou código prematuramente. |
| **V. Resiliência Operacional** | Backups pré-migração e segurança de dados. | **PASS** | Nenhuma alteração de schema, DDL ou migração é realizada nesta feature. |

*Re-avaliação pós-Fase 1: Todos os artigos da Constituição permanecem 100% atendidos.*

---

## Project Structure

### Documentation (this feature)

```text
specs/071-amigos-salao-literario/
├── plan.md              # Este plano técnico consolidado
├── research.md          # Decisões técnicas da Fase 0 (Bookplate Card, Selo 1200ms, Web Share, Abas e Temas)
├── data-model.md        # Modelos de dados e estados reativos da Fase 1
├── quickstart.md        # Roteiro de testes automatizados e validação manual
└── contracts/
    └── amigos-contract.md # Contratos de UI, componentes, WAI-ARIA e imunidade cromática
```

### Source Code (repository root)

```text
caderno-leitura-0.1/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── BookplateCard.vue              # [NOVO] Ex-Líbris Digital permanente no topo com selo de 1200ms e Web Share
│   │   │   ├── FriendActionButtons.vue        # [PRESERVADO/ESTILIZADO] Botões de ação social com alvos táteis e tokens semânticos
│   │   │   └── ui/
│   │   │       └── Icon.vue                   # [PRESERVADO] Componente oficial de ícones SVG do sistema
│   │   ├── composables/
│   │   │   ├── useFriends.ts                  # [PRESERVADO] Composable com estado reativo de amizades e solicitações
│   │   │   └── useProfile.ts                  # [PRESERVADO] Composable para dados de perfil e iniciais
│   │   ├── views/
│   │   │   └── FriendsView.vue                # [REFATORADO] Salão Literário com 4 abas, cartões editoriais e estados acolhedores
│   │   ├── api/
│   │   │   ├── friends.ts                     # [PRESERVADO] Cliente API REST para /api/friends
│   │   │   └── profile.ts                     # [PRESERVADO] Cliente API REST para /api/profile
│   │   └── types.ts                           # [PRESERVADO] Tipos centrais de amizade e perfil
│   └── tests/
│       ├── friends.test.mjs                   # [PRESERVADO] Testes existentes de métodos e contratos
│       └── feature-071-amigos-salao-literario.test.mjs # [NOVO] Teste de contrato e integridade do Salão Literário
└── backend/
    ├── app/
    │   └── routers/
    │       ├── friends.py                     # [PRESERVADO] Endpoints REST inalterados (/api/friends)
    │       └── profile.py                     # [PRESERVADO] Endpoints REST inalterados (/api/profile)
    └── tests/                                 # [PRESERVADO] Suíte de testes do backend
```

**Structure Decision**: A feature concentra todas as modificações na camada de apresentação (`frontend/`), criando o componente `BookplateCard.vue` e modernizando `FriendsView.vue`, mantendo inalterados os composables e endpoints REST já consolidados.

---

## Complexity Tracking

> Nenhuma violação identificada. O design preserva a arquitetura existente e não requer padrões complexos adicionais.

| Violação | Por que é necessária | Alternativa mais simples rejeitada por que |
|---|---|---|
| *Nenhuma* | — | — |
