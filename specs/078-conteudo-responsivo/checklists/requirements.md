# Checklist de Requisitos — Feature 078: Leitor e Disposição de Conteúdo Responsivo

## Requisitos Funcionais
- [x] **FR-001**: Em `useSplitPanes.ts`, painel esquerdo (`leftCollapsed`) inicia fechado (`true`) por padrão em `< 768px` quando não há preferência salva.
- [x] **FR-002**: Em `BookView.vue`, cabeçalho reorganizado em `< 768px` com menu contextual de ações secundárias e botões $\ge 44 \times 44\text{ px}$.
- [x] **FR-003**: Em `AdminUsersTable.vue`, modo cartões verticais adaptativos ativado em `< 768px`.
- [x] **FR-004**: Em `AdminUsersTable.vue`, tabela convencional preservada em telas $\ge 768\text{px}$.
- [x] **FR-005**: Grids de `FriendsView.vue`, `AdminView.vue` e `SovereigntySection.vue` adaptadas para comportar viewports de 320px sem overflow.
- [x] **FR-006**: Modais (`BookEditModal.vue`, `ExportModal.vue`, `StudyHistoryModal.vue`, etc.) adotam `dvh` com fallback para `vh`.
- [x] **FR-007**: Regras de elevação de cartões em `:hover` protegidas por `@media (hover: hover) and (pointer: fine)`.
- [x] **FR-008**: Testes automatizados cobrindo os cenários US1 a US4 e critérios de aceitação da Feature 078.

## Critérios de Sucesso
- [x] **SC-001**: Gaveta de capítulos em `BookView` inicia fechada no celular sem cobrir a leitura.
- [x] **SC-002**: Painel de administração exibe cartões verticais com alvos de toque $\ge 44 \times 44\text{ px}$ no mobile.
- [x] **SC-003**: Nenhuma tela inspecionada apresenta barra de rolagem horizontal em 320px de viewport.
- [x] **SC-004**: Modais operam com `dvh` sem truncar botões em navegadores móveis.
- [x] **SC-005**: 100% dos testes e compilações (`npm test`, `npm run build`, `pytest`) passam com sucesso.
