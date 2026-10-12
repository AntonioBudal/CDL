# Implementation Plan: Leitor e Disposição de Conteúdo Responsivo

**Branch**: `078-conteudo-responsivo` | **Date**: 2026-10-12 | **Spec**: [spec.md](file:///c:/Users/User/caderno/specs/078-conteudo-responsivo/spec.md)

**Input**: Problemas P-11, P-12, P-14, P-15, P-16, P-17 e P-18 da Auditoria de Responsividade (F0.8.13).

## Summary

Otimizar a visualização de leitura e disposição de conteúdo em viewports móveis e telas estreitas (< 768px e 320px):
1. **BookView**: Gaveta de capítulos inicializada como fechada por padrão no mobile em `useSplitPanes.ts` (P-17) e ações secundárias do cabeçalho compactadas em menu contextual com alvos de toque $\ge 44 \times 44\text{ px}$.
2. **AdminUsersTable**: Conversão da tabela de 8 colunas para cartões adaptativos em telas estreitas (< 768px), mantendo a tabela convencional no desktop (P-14).
3. **Grids em 320px**: Adequação das grades em `FriendsView`, `AdminView` e `SovereigntySection` usando fórmulas fluidas com `minmax(min(100%, 280px), 1fr)` para blindagem total contra overflow em 320px (P-15).
4. **Modais em `dvh`**: Padronização dos modais principais com unidades de viewport dinâmico (`dvh`) e fallback para `vh` (P-16).
5. **Proteções de Hover**: Condicionar transformações de elevação `:hover` ao ponteiro fino via `@media (hover: hover) and (pointer: fine)` (P-18).
6. **Bateria de Testes**: Criar testes automatizados para validar a integridade dos seletores, classes e comportamento de viewport.

## Technical Context

**Language/Version**: TypeScript 5.7, Vue 3.5 (`<script setup>`), CSS3 nativo (tokens e media queries).  
**Primary Dependencies**: `vue`, `vue-router`, `lucide-vue-next`.  
**Storage**: `localStorage` (preferências de dimensões e visualização de livro).  
**Testing**: `node --test` (Frontend - 592 testes), `pytest` (Backend - 458 testes).  
**Target Platform**: Navegadores modernos (Desktop e Mobile/Tablet), Safari iOS, Chrome Android, Firefox.  
**Constraints**: Zero emojis no código e documentação; 1 Feature = 1 Commit; Sem Tailwind nem dependências externas pesadas; Alvos táteis $\ge 44 \times 44\text{ px}$.

## Constitution Check

- **Preservação de Dados e Privacidade**: Totalmente estática/visual no frontend; nenhum acesso ao banco do usuário nem exposição de dados.
- **Integridade do Banco**: Nenhuma alteração no backend nem no schema SQLite.
- **Convenção de Versionamento**: 1 Feature = 1 Commit após validação total de testes e build.
- **Zero Emojis**: Garantida conformidade nominal e estética sem ícones emoji.

## Project Structure

### Documentation (this feature)

```text
specs/078-conteudo-responsivo/
├── spec.md
├── plan.md
├── contracts/
│   └── responsive-content.contract.md
├── checklists/
│   └── requirements.md
└── tasks.md
```

### Source Code

- `caderno-leitura-0.1/frontend/src/composables/useSplitPanes.ts`
- `caderno-leitura-0.1/frontend/src/views/BookView.vue`
- `caderno-leitura-0.1/frontend/src/components/admin/AdminUsersTable.vue`
- `caderno-leitura-0.1/frontend/src/views/FriendsView.vue`
- `caderno-leitura-0.1/frontend/src/views/AdminView.vue`
- `caderno-leitura-0.1/frontend/src/components/landing/SovereigntySection.vue`
- `caderno-leitura-0.1/frontend/src/components/BookEditModal.vue`
- `caderno-leitura-0.1/frontend/src/components/ExportModal.vue`
- `caderno-leitura-0.1/frontend/src/components/StudyHistoryModal.vue`
- `caderno-leitura-0.1/frontend/src/views/SettingsView.vue`
- `caderno-leitura-0.1/frontend/src/style.css`
- `caderno-leitura-0.1/frontend/tests/feature-078-conteudo-responsivo.test.mjs`
