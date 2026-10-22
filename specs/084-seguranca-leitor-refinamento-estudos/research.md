# Research & Architecture Decisions: F0.9.03 — Segurança Operacional e Refinamento do Leitor de Estudos

**Feature**: `specs/084-seguranca-leitor-refinamento-estudos`  
**Parent Roadmap**: `docs/contexto/ROADMAP-0.9.md` (Feature F03)  
**Zero Emojis Policy**: Rigorosamente respeitada.

---

## 1. Decisões Arquiteturais e Mapeamento Técnico

### D01 — Encapsulamento de Ações Secundárias no Leitor (`StudyView.vue`)
- **Problema**: O cabeçalho de `StudyView.vue` renderiza botões lado a lado para Compartilhar, Exportar, Histórico, Editar e Lixeira. Em smartphones ou telas sensíveis ao toque, a proximidade espacial entre Editar e Lixeira provoca toques indesejados.
- **Decisão**: Reutilizar o componente canônico `DropdownMenu.vue` (`caderno-leitura-0.1/frontend/src/components/ui/DropdownMenu.vue`), que já implementa:
  - Gatilho acessível com `:aria-expanded`, `:aria-haspopup="true"`.
  - Controle de foco e isolamento de teclado (`Escape` fecha e devolve foco ao botão disparador).
  - Fechamento sob clique externo via ouvinte de evento global.
- **Estrutura Visual**:
  - Destaque primário: Botão "Editar estudo" (RouterLink com classe `button primary edit-action`) e pílula de status.
  - Gatilho do menu: Botão discreto `button secondary header-icon-btn` com ícone `more-horizontal` e atributo `aria-label="Mais opções do estudo"`.
  - Conteúdo do menu:
    - Se `canEdit === true`: "Compartilhar estudo", "Exportar estudo", "Histórico de versões", separador visual (`dropdown-divider`) e "Mover para a lixeira" (`.danger-item`).
    - Se `canEdit === false`: "Exportar estudo" e "Histórico de versões".
  - A confirmação de exclusão continua orquestrada por `TrashConfirmModal.vue`, com `danger: true` e foco retido no modal.

### D02 — Indicador Visual de Persistência em Tempo Real no Editor (`StudyEditView.vue`)
- **Problema**: `StudyEditView.vue` já possui salvamento local de rascunhos em `localStorage` via `useStudyDraft` e controle de estado não salvo via `useUnsavedChanges` e `useStudyEdit`. Porém, no topo do formulário, o usuário não tem feedback visual imediato de status de persistência durante a digitação.
- **Decisão**: Introduzir uma pílula de status acessível (`.draft-status-pill`) adjacente ao título do formulário `<h1>Editar estudo</h1>`.
- **Estados Reativos Mapeados**:
  1. **Salvando**: Quando `state.saving === true`:
     - Rótulo: "Salvando…"
     - Classe CSS: `.saving`
     - Estilo: Cor de destaque temática (`var(--color-primary)` ou `var(--color-accent)`) com animação discreta ou indicador circular.
  2. **Rascunho Local**: Quando `state.saving === false` e (`dirty.value === true` ou `isDraftRestored.value === true`):
     - Rótulo: "Rascunho salvo neste navegador"
     - Classe CSS: `.draft-local`
     - Estilo: Fundo suave informativo (`var(--color-surface-hover)`) com borda e texto sutis (`var(--color-muted)`).
  3. **Sincronizado / Salvo**: Quando `state.saving === false` e `dirty.value === false`:
     - Rótulo: "Alterações salvas"
     - Classe CSS: `.saved`
     - Estilo: Tom suave indicando integridade (`var(--color-success-text, #15803d)` ou `var(--color-muted)`).
- **Acessibilidade**: Elemento renderizado com `role="status"` e `aria-live="polite"` para anúncio sutil aos leitores de tela sem interromper o fluxo de entrada de texto.

### D03 — Calibragem de Alvos Táteis Ergonômicos (WCAG 2.5.5)
- **Problema**: O botão de fechar da barra de leitura ativa (`ActiveReadingBar.vue`) possui no desktop tamanho de 36x36px. Em dispositivos com ponteiro de toque (`pointer: coarse`) ou telas estreitas, isso viola o critério WCAG 2.5.5 de alvo mínimo de 44x44px. Além disso, as abas de análise (`StudyTabs.vue`) e botões de ação do cabeçalho precisam garantir alvos de 44x44px no mobile.
- **Decisão**:
  - Em `ActiveReadingBar.vue`: No bloco de CSS responsivo e em `@media (pointer: coarse)`, fixar `min-height: 44px; min-width: 44px;` para todos os botões (`.reading-bar-btn`, incluindo `.close-btn` e botões de navegação).
  - Em `StudyTabs.vue`: Garantir que os botões `[role="tab"]` tenham `min-height: 44px` sob `@media (pointer: coarse)` e no mobile, com `padding` equilibrado e alinhamento vertical centralizado.
  - Em `StudyView.vue`: Garantir que o gatilho de `DropdownMenu` e o botão de edição mantenham `min-height: 44px; min-width: 44px;` em viewports móveis (`<= 767px`) e sob `@media (pointer: coarse)`.

---

## 2. Compatibilidade e Ausência de Quebras

- **Testes Existentes**: Todos os testes que buscam elementos funcionais (ex.: `confirmTrashOpen`, `shareModalOpen`, `exportModalOpen`, `historyModalOpen`, `StudyHistoryModal`, `TrashConfirmModal`) permanecem plenamente atendidos porque os handlers de clique e os modais continuam idênticos, mudando apenas o posicionamento do gatilho para o menu suspenso.
- **Variáveis de Tema**: Utilizar estritamente variáveis de tema declaradas em `palettes.css` e `style.css` (ex.: `var(--color-surface)`, `var(--color-surface-hover)`, `var(--color-text)`, `var(--color-muted)`, `var(--color-border)`, `var(--color-danger, #b91c1c)`, `var(--color-danger-subtle, rgba(239, 68, 68, 0.1))`).
