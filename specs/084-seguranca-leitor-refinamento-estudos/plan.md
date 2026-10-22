# Implementation Plan: F0.9.03 — Segurança Operacional e Refinamento do Leitor de Estudos

**Branch**: `084-seguranca-leitor-refinamento-estudos` | **Date**: 2026-10-21 | **Spec**: [specs/084-seguranca-leitor-refinamento-estudos/spec.md](spec.md)  
**Parent Roadmap**: `docs/contexto/ROADMAP-0.9.md` (Feature F03)  
**Zero Emojis Policy**: Rigorosamente respeitada em todo o planejamento e implementação.

---

## Summary

O objetivo desta feature é blindar o leitor de estudos (`/livros/:bookId/estudos/:studyId` em `StudyView.vue`) contra ações destrutivas inadvertidas, introduzir um indicador visual em tempo real de integridade e rascunho no editor (`StudyEditView.vue`), e calibrar alvos táteis mínimos de 44x44px em botões de ação e abas conforme WCAG 2.5.5.

A abordagem técnica compreende:
1. Reestruturação do cabeçalho de `StudyView.vue` para manter em destaque direto apenas "Editar estudo" e a pílula de status, agrupando "Compartilhar", "Exportar", "Histórico de versões" e "Mover para a lixeira" em um menu suspenso contextual via `DropdownMenu.vue`.
2. Criação de pílula reativa de status de persistência em `StudyEditView.vue` comunicando estados de "Salvando…", "Rascunho salvo neste navegador" e "Alterações salvas".
3. Ajuste de estilos CSS em `ActiveReadingBar.vue`, `StudyTabs.vue` e `StudyView.vue` garantindo áreas de toque táteis mínimas de 44x44px em dispositivos móveis e touch (`@media (pointer: coarse)`).

---

## Technical Context

**Language/Version**: TypeScript 5.8+, Vue 3.5+ (Composition API, `<script setup>`), CSS3 moderno  
**Primary Dependencies**: Vue 3, Vue Router 4, Lucide Icons (`lucide-vue-next`), `markdown-it`  
**Storage**: N/A para backend (schema intacto). Persistência de rascunhos em `localStorage` via `useStudyDraft.ts`  
**Testing**: Node.js Test Runner (`node --test`), `npm test`, `npm run build` (`vue-tsc -b && vite build`), `pytest` no backend  
**Target Platform**: Navegadores Web modernos em Desktop, Tablets e Smartphones (Android/iOS)  
**Project Type**: Single Page Application (SPA) em Vue 3 atendida por servidor local FastAPI  
**Constraints**:
- Zero alterações no backend e no banco de dados SQLite.
- Proibição estrita de emojis no código e na documentação.
- Imunidade cromática aos 10 temas oficiais utilizando estritamente variáveis de tema.
- Alvos táteis mínimos de 44x44px em ponteiros de toque.

---

## Constitution Check

| Artigo Constitucional | Avaliação | Justificativa / Mitigação |
| :--- | :--- | :--- |
| **I. Privacidade de Dados** | PASS | Nenhum dado de usuário ou de acervo é exposto ou transmitido. |
| **II. Isolamento de Testes** | PASS | Testes unitários com DOM sintético e validação estática de componentes, sem conexão a banco ativo. |
| **III. Fidelidade Tecnológica** | PASS | Vue 3 Composition API com TypeScript estrito, CSS scoped e variáveis canônicas de design tokens. |
| **IV. Governança por SDD** | PASS | Ciclo formal Spec Kit (specify -> plan -> tasks -> implement). |
| **V. Resiliência Operacional** | PASS | Preservação de rascunhos no `localStorage` e confirmação modal obrigatória para descarte. |
| **Convenção de Zero Emojis** | PASS | Todo o código, comentários e documentos mantêm tom formal e sem emojis. |

---

## Project Structure

### Documentation (this feature)

```text
specs/084-seguranca-leitor-refinamento-estudos/
├── spec.md                                         # Especificação funcional e User Stories
├── checklists/requirements.md                      # Checklist de aceite de requisitos
├── plan.md                                         # Este plano técnico de implementação
├── research.md                                     # Decisões de design e levantamento arquitetural
├── data-model.md                                   # Mapeamento de estados reativos e matriz de permissões
├── contracts/study-reader-safety.contract.md       # Contratos de interface WAI-ARIA e templates
├── quickstart.md                                   # Guia de validação automatizada e teste manual
└── tasks.md                                        # Tarefas de implementação (geradas no próximo passo)
```

### Source Code Modificado e Testes

```text
caderno-leitura-0.1/frontend/
├── src/
│   ├── views/
│   │   ├── StudyView.vue                           # Cabeçalho com ações agrupadas e menu contextual
│   │   └── StudyEditView.vue                       # Pílula reativa de status de persistência/rascunho
│   └── components/
│       ├── ActiveReadingBar.vue                    # Alvos táteis >= 44x44px (inclusive close-btn)
│       └── StudyTabs.vue                           # Alvos táteis >= 44px nas abas
└── tests/
    └── feature-084-study-reader-safety.test.mjs    # Suíte de testes unitários da Feature 084
```

---

## Planned Execution Phases

### Phase 1: Setup & Testes da Feature
- Criação de `caderno-leitura-0.1/frontend/tests/feature-084-study-reader-safety.test.mjs` com asserções para US1, US2 e US3.

### Phase 2: User Story 1 — Menu Contextual de Ações Secundárias no Leitor
- Importação e estruturação de `DropdownMenu.vue` no cabeçalho de `StudyView.vue`.
- Encapsulamento de Compartilhar, Exportar, Histórico e Lixeira.
- Aplicação de regras de permissão (`canEdit`) e estilização com variáveis temáticas.

### Phase 3: User Story 2 — Indicador Visual de Persistência no Editor
- Adição da pílula `.draft-status-pill` ao lado de `<h1>Editar estudo</h1>` em `StudyEditView.vue`.
- Computação reativa dos estados "Salvando…", "Rascunho salvo neste navegador" e "Alterações salvas".
- Estilização harmônica e semântica com `role="status"` e `aria-live="polite"`.

### Phase 4: User Story 3 — Alvos de Toque Ergonômicos
- Ajuste de dimensões em `ActiveReadingBar.vue` para garantir 44x44px em todos os botões sob toque e mobile.
- Ajuste em `StudyTabs.vue` e `StudyView.vue` para assegurar altura e largura tátil mínima de 44px.

### Phase 5: Polimento, Regressão e Validação Integral
- Execução de testes automatizados (`feature-084-study-reader-safety.test.mjs`, `npm test`, `npm run build`, `pytest`).
- Verificação de ausência estrita de emojis e variáveis CSS indefinidas.
- Commit atômico seguindo a convenção oficial: `feature — seguranca operacional e refinamento do leitor de estudos`.
