# Checklist de Requisitos — Feature 077: Shell e Navegação Móvel

## Requisitos Funcionais
- [x] **FR-001**: Barra de navegação inferior móvel (`MobileTabBar.vue`) com 5 itens (Início, Livros, Destaques, Revisão e Mais).
- [x] **FR-002**: Área de toque mínima de $44 \times 44\text{ px}$ em todos os alvos móveis.
- [x] **FR-003**: Abas superiores de navegação ocultadas em viewports `< 768px`.
- [x] **FR-004**: `MobileMoreMenu.vue` expandido com Caixa de Entrada, Amigos, Ajustes, Lixeira e Importar com badges.
- [x] **FR-005**: Token CSS `--mobile-nav-offset` exposto para elementos móveis.
- [x] **FR-006**: Toasts, barra de lote da lixeira e FAB de preview de Ajustes respeitam `--mobile-nav-offset`.
- [x] **FR-007**: `NotificationsDropdown.vue` adaptado para não estourar a margem esquerda em telas $\le 430\text{px}$.
- [x] **FR-008**: `ShareModal.vue` reescrito com tokens CSS nativos sem utilitários Tailwind.
- [x] **FR-009**: CSS scoped legado e morto purgado de `App.vue`.
- [x] **FR-010**: Testes de navegação móvel verificam a existência de seletores reais nos templates.

## Critérios de Sucesso
- [x] **SC-001**: Barra inferior móvel ativa em `< 768px` sem overflow horizontal.
- [x] **SC-002**: Alvos táteis $\ge 44 \times 44\text{ px}$ em 100% dos botões móveis.
- [x] **SC-003**: `ShareModal` renderizado com backdrop e temas nos modos claro e escuro.
- [x] **SC-004**: Zero sobreposição entre elementos flutuantes e a barra inferior.
- [x] **SC-005**: `npm test` e `npm run build` passam com 100% de sucesso.

