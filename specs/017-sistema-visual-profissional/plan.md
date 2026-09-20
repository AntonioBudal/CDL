# Implementation Plan: F09 - Sistema Visual Profissional

**Branch**: `017-sistema-visual-profissional` | **Date**: 2026-09-19 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/017-sistema-visual-profissional/spec.md`

## Summary

Esta feature institui o **Sistema Visual Profissional** no Caderno de Leitura, refinando integralmente a identidade estética, a consistência de controle e a sobriedade editorial da aplicação. A abordagem técnica compreende:
1. **Erradicação de Emojis e Adoção de Lucide Icons:** Integração da biblioteca `lucide-vue-next` e criação do componente envelope `Icon.vue` para substituir 100% dos emojis e SVGs manuais dispersos nos botões, navegações e modais.
2. **Purificação Semântica de IA:** Eliminação de referências a "IA", "prompt" e "ChatGPT", adotando a nomenclatura editorial canônica **"Fichamento da Fonte"** para o campo de texto original (`source_response`), mantendo o modelo de dados do SQLite estritamente intacto por integridade.
3. **Padronização de Estados de Interface:** Criação dos componentes `EmptyState.vue`, `LoadingSkeleton.vue` (com shimmer adaptativo que desliga sob `prefers-reduced-motion`) e `StatusBadge.vue`, harmonizados com os temas (Claro, Escuro, Sépia) e as 5 Superclasses de Interface (Zero-G, Mecânica, Invisível, Dimensional, Monolítica).

---

## Technical Context

**Language/Version**: TypeScript 5.9 (modo estrito), Vue 3 (Composition API `<script setup>`), Python 3.13 (FastAPI / SQLAlchemy 2.0).  
**Primary Dependencies**: `lucide-vue-next` (adicionado ao `package.json` do frontend), Vue 3.5, Vue Router 4.6, Vite 8.2.  
**Storage**: SQLite local existente em modo WAL (`backend/data/caderno.db`). *Zero modificações estruturais nas tabelas.*  
**Testing**: `npm run build` (`vue-tsc -b && vite build`), `node --test` (testes unitários do frontend em `frontend/tests/`), `pytest` no backend.  
**Target Platform**: Windows local (processo único via `iniciar.py`), navegadores desktop e mobile em rede privada/Tailscale.  
**Project Type**: Aplicação Web SPA (Vue 3 + Vite) servida por API REST FastAPI (Python 3.13).  
**Performance Goals**: CLS (Cumulative Layout Shift) < 0.05 com esqueletos de carregamento; tempo de inicialização do frontend sem degradação perceptível (tree-shaking estrito no empacotamento de ícones).  
**Constraints**: Zero dependência de conexões de rede externas (ícones renderizados localmente via SVG no cliente); respeito mandatória a `prefers-reduced-motion`.  
**Scale/Scope**: Todas as 8 visualizações ativas do frontend (`BooksView.vue`, `BookView.vue`, `StudyView.vue`, `StudyEditView.vue`, `ImportView.vue`, `TrashView.vue`, `SettingsView.vue`, `DashboardView.vue`) e componentes compartilhados.

---

## Constitution Check

*GATE: Avaliação contra a Constituição do Projeto Caderno de Leitura (`.specify/memory/constitution.md`).*

| Artigo Constitucional | Avaliação | Justificativa |
| :--- | :---: | :--- |
| **I. Proteção do Acervo e Privacidade** | **PASS** | O banco de produção `caderno.db` não é modificado. Nenhuma anotação ou dado privado do usuário é exposto. A coluna `source_response` é preservada integralmente no banco. |
| **II. Isolamento de Testes e Operações** | **PASS** | Testes automatizados continuam usando bancos efêmeros em `tmp_path` e mocks sem tocar no banco ativo. |
| **III. Fidelidade Tecnológica** | **PASS** | Permanece no ecossistema Vue 3 + TypeScript + Vite no frontend e FastAPI + Python 3.13 no backend. A adição de `lucide-vue-next` é leve, padrão da indústria e empacotada localmente. |
| **IV. Governança por SDD** | **PASS** | A feature segue o ciclo delimitado Spec Kit (`speckit-specify` → `speckit-plan` → `speckit-tasks` → `speckit-analyze` → `speckit-implement`). |
| **V. Resiliência Operacional e Migrações** | **PASS** | Nenhuma alteração DDL ou migração de banco é necessária para esta feature. |

---

## Project Structure

### Documentation (this feature)

```text
specs/017-sistema-visual-profissional/
├── spec.md              # Especificação funcional refinada e aprovada
├── checklists/
│   └── requirements.md  # Checklist de requisitos 100% validado
├── plan.md              # Este plano de implementação técnica
├── research.md          # Decisões de arquitetura e mapeamento exaustivo de termos/emojis
├── data-model.md        # Tipos TypeScript, interfaces de props e dicionário editorial
├── contracts/
│   └── ui-components.md # Contratos de interface dos componentes (Icon, EmptyState, Skeleton)
└── quickstart.md        # Roteiro de validação ponta a ponta e comandos de teste
```

### Source Code (repository root)

```text
caderno-leitura-0.1/
├── frontend/
│   ├── package.json                         # Adição da dependência 'lucide-vue-next'
│   └── src/
│       ├── types.ts                         # Tipos: IconName, EmptyStateProps, LoadingSkeletonProps
│       ├── constants/
│       │   └── editorial.ts                 # Dicionário canônico EDITORIAL_TERMS
│       ├── components/
│       │   ├── ui/
│       │   │   ├── Icon.vue                 # Envelope unificado de ícones Lucide
│       │   │   ├── EmptyState.vue           # Componente de estado vazio acolhedor
│       │   │   ├── LoadingSkeleton.vue      # Placeholder visual com shimmer adaptativo
│       │   │   └── StatusBadge.vue          # Pílulas informativas de status/categoria
│       │   ├── BookCover.vue                # Substituição do emoji 📖 por SVG vetorial
│       │   ├── BookEditModal.vue            # Substituição do botão ✕ por Icon name="x"
│       │   ├── TrashConfirmModal.vue        # Substituição de ⚠️ e ✕ por ícones Lucide
│       │   ├── ExportModal.vue              # Substituição de ✕ e termo "Resposta Original"
│       │   ├── RestoreModal.vue             # Substituição do ✓ por CheckCircle
│       │   └── LibraryToolbar.vue           # Substituição do botão ✕ por Icon name="x"
│       ├── views/
│       │   ├── App.vue                      # Navegação unificada com componente Icon
│       │   ├── BookView.vue                 # Substituição de ✎ e 🗑 por Pencil e Trash2; termos de IA
│       │   ├── TrashView.vue                # Adoção de EmptyState no lugar de 🗑️
│       │   ├── DashboardView.vue            # Adoção de EmptyState; troca de 🔥 e ✕
│       │   ├── ImportView.vue               # Adoção de "Fichamento da Fonte" e remoção de IA
│       │   └── StudyView.vue                # Adoção de "Consultar Fichamento da Fonte"
│       └── composables/
│           └── useImportDraft.ts            # Atualização de mensagens orientadoras sem IA
├── backend/
│   └── app/
│       └── schemas/
│           └── imports.py                   # Atualização das descrições e mensagens de erro sem "ChatGPT"
└── frontend/
    └── tests/
        └── visual_system.test.mjs           # Nova suíte de testes unitários para os componentes de UI
```

**Structure Decision**: A organização aloca os novos blocos do sistema de design na pasta `frontend/src/components/ui/`, mantendo os componentes de domínio em `frontend/src/components/` e as vistas em `views/`. A adição de `constants/editorial.ts` centraliza o vocabulário para reuso futuro nas features F01 a F10.

---

## Complexity Tracking

> **Sem violações constitucionais.** A arquitetura aproveita os recursos nativos do Vue 3 e do Vite, limitando adições externas ao pacote de ícones `lucide-vue-next`. O banco de dados e as APIs existentes permanecem intocados, garantindo risco zero para a estabilidade do sistema.
