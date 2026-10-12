# Contrato Técnico: Conteúdo e Disposição Responsiva

## 1. Contrato de Inicialização de Painéis (`useSplitPanes.ts`)
- **Regra**: Em viewports com `windowWidth < 768` (modo móvel), caso não exista registro salvo em localStorage (`storedDimensions`), o valor inicial de `leftCollapsed` deve ser obrigatoriamente `true`.
- **Efeito**: Ao abrir qualquer livro em dispositivos móveis, a gaveta de capítulos inicia recolhida, exibindo imediatamente a área de leitura e o texto da obra sem obstrução.
- **Transição**: O leitor pode expandir a gaveta através do botão de capítulos a qualquer momento, momento em que ela desliza suavemente como drawer sobreposta.

## 2. Contrato de Ações do Cabeçalho do Livro (`BookView.vue`)
- **Desktop ($\ge 768\text{px}$)**:
  - Botões de alternância de painéis e botões textuais ("Exportar anotações", "Editar livro", "Mover para a lixeira") visíveis na barra superior.
- **Mobile ($< 768\text{px}$)**:
  - Preserva os botões de controle de painel (capítulos e contexto).
  - Ações secundárias agrupadas em menu de contexto/ações com ícone de reticências/menu ou botões de ícone com alvos táteis mínimos de $44 \times 44\text{ px}$.
  - Previne estouro horizontal e quebra indesejada de layout em viewports estreitas.

## 3. Contrato de Cartões Adaptativos do Admin (`AdminUsersTable.vue`)
- **Desktop ($\ge 768\text{px}$)**:
  - `table.admin-table` opera com `display: table`, `thead` visível com 8 colunas e `tr` horizontais.
- **Mobile ($< 768\text{px}$)**:
  - `table.admin-table`, `thead`, `tbody`, `tr`, `td` adaptam-se para layout de cartões (`display: block` ou `grid`).
  - `thead` oculto visualmente (`display: none` ou `sr-only`).
  - Cada `tr` renderizado como um cartão delimitado com borda, cantos arredondados, fundo de superfície (`--color-surface`) e espaçamento confortável.
  - Células exibem rótulos semânticos (ex.: `data-label` ou headers visíveis nos cartões).
  - Botões de ação em grid ou linha com altura mínima de 44px e separação tátil.

## 4. Contrato de Grades Fluidas para Telas de 320px
- Todas as grades de cartões com colunas mínimas de 280px (`FriendsView.vue`, `AdminView.vue`, `SovereigntySection.vue`):
  - Devem adotar a fórmula de contenção: `repeat(auto-fit, minmax(min(100%, 280px), 1fr))` ou `repeat(auto-fill, minmax(min(100%, 260px), 1fr))`.
  - Em telas de 320px com até 32px de somatório de paddings laterais (área útil de 288px), nenhuma grade pode forçar a viewport além de 100vw.

## 5. Contrato de Modais e Altura Dinâmica (`dvh`)
- Diálogos de modais (`BookEditModal.vue`, `ExportModal.vue`, `StudyHistoryModal.vue`, `SettingsView.vue`):
  - Devem declarar suporte a unidades dinâmicas:
    ```css
    max-height: 90vh;
    max-height: 90dvh;
    ```
  - Evita corte de botões e rodapés de confirmação quando a barra de ferramentas do navegador móvel está visível.

## 6. Contrato de Proteção Hover Tátil
- Regras CSS que aplicam transformações de elevação (`transform: translateY(-...)`) em estado `:hover`:
  - Devem ser condicionadas por `@media (hover: hover) and (pointer: fine)`.
  - Dispositivos de toque (`pointer: coarse`) mantêm feedback de clique/ativação sem reter o deslocamento flutuante permanentemente após o toque.
