# Feature Specification: F0.9.03 — Segurança Operacional e Refinamento do Leitor de Estudos

**Feature Branch / Spec Directory**: `specs/084-seguranca-leitor-refinamento-estudos`  
**Parent Roadmap**: `docs/contexto/ROADMAP-0.9.md` (Feature F03)  
**Status**: DRAFT  
**Zero Emojis Policy**: Rigorosamente aplicada em todo o ciclo de especificação, planejamento e código.

---

## 1. Contexto e Motivação

No leitor de estudos (`/livros/:bookId/estudos/:studyId` em `StudyView.vue`), os usuários frequentemente realizam leituras imersivas e anotações reflexivas. O layout atual do cabeçalho exibe lado a lado, em formato de botões de ícone com espaçamento mínimo, as ações de "Compartilhar", "Exportar", "Histórico de Versões", "Editar Estudo" e "Mover para a Lixeira". Em telas sensíveis ao toque (smartphones, tablets e notebooks touch), a proximidade física entre o botão de edição (ação mais frequente) e o de lixeira (ação destrutiva) acarreta alto risco de toques acidentais, gerando ansiedade e frustração no leitor.

Além disso, durante a edição de estudos longos em `StudyEditView.vue`, o sistema persiste rascunhos no `localStorage` e previne perdas via `useUnsavedChanges` e `useStudyDraft`. Contudo, o usuário não conta com um indicador sutil e visível em tempo real no topo do formulário que confirme se seu texto está com "Salvando…", "Rascunho salvo neste navegador" ou "Alterações salvas", gerando insegurança quanto à persistência de suas anotações.

Por fim, botões da barra de leitura ativa (`ActiveReadingBar.vue`) e das abas de análise (`StudyTabs.vue`) necessitam de calibragem estrita para assegurar alvos táteis mínimos de 44x44px sob `@media (pointer: coarse)` e no mobile, cumprindo as diretrizes WCAG 2.5.5.

---

## 2. Histórias de Usuário (User Stories)

### User Story 1 — Menu Contextual de Ações Secundárias no Leitor (Priority: P1) [MVP]
Como um leitor no computador ou no celular navegando em `/livros/:bookId/estudos/:studyId`,  
Quero que o cabeçalho do estudo destaque de forma primária e imediata apenas o botão "Editar estudo" e a pílula de status de leitura, mantendo as ações secundárias e a ação de exclusão resguardadas dentro de um menu contextual suspenso ("Mais opções"),  
Para que eu nunca clique acidentalmente no botão de exclusão e tenha uma interface de leitura limpa e focada no conteúdo.

### User Story 2 — Indicador Visual de Persistência e Rascunho no Editor (Priority: P1)
Como um leitor redigindo reflexões e fichamentos em `StudyEditView.vue`,  
Quero visualizar uma pílula sutil de status ao lado do título do estudo que informe claramente o estado da persistência ("Salvando…", "Rascunho salvo neste navegador" ou "Alterações salvas"),  
Para que eu tenha total tranquilidade de que minhas anotações estão salvas e seguras a cada caractere digitado.

### User Story 3 — Alvos de Toque Ergonômicos na Barra de Leitura e Abas (Priority: P2)
Como um leitor utilizando dispositivo móvel ou tela sensível ao toque,  
Quero que todos os botões interativos da barra de leitura ativa (`ActiveReadingBar.vue`), do cabeçalho do estudo e das abas de análise (`StudyTabs.vue`) possuam dimensão mínima de 44x44px,  
Para que eu consiga alternar trechos, seções e abas com toques precisos, sem erros de mira ou fadiga muscular.

---

## 3. Requisitos Funcionais (Functional Requirements)

- **FR-001 (StudyView - Cabeçalho Limpo)**: No cabeçalho de `StudyView.vue`, quando o usuário tiver permissão de edição (`canEdit === true`), os únicos controles em destaque direto na barra de ações devem ser o botão primário "Editar estudo" e o botão de menu contextual suspenso `DropdownMenu` ("Mais opções" com ícone `more-horizontal` e rótulo acessível).
- **FR-002 (StudyView - Menu de Opções Secundárias)**: O menu contextual de `StudyView.vue` deve abrigar as seguintes ações:
  1. "Compartilhar estudo" (somente se `canEdit === true`).
  2. "Exportar estudo" (disponível para todos os leitores).
  3. "Histórico de versões" (disponível para todos os leitores).
  4. Separador visual semântico antes da ação destrutiva.
  5. "Mover para a lixeira" (somente se `canEdit === true`), com estilo de perigo (`.danger-item` com cor e fundo sutis do tema) e confirmação obrigatória via `TrashConfirmModal.vue`.
- **FR-003 (StudyView - Modo Somente Leitura)**: Quando o estudo for visualizado em modo somente leitura (`canEdit === false`), o botão "Editar estudo" não deve ser renderizado. O botão de menu contextual deve conter apenas "Exportar estudo" e "Histórico de versões", sem o separador nem a opção de lixeira.
- **FR-004 (StudyView - Teclado e Acessibilidade do Menu)**: O menu suspenso deve implementar semântica WAI-ARIA (`aria-haspopup="menu"`, `aria-expanded`, `role="menu"`, `role="menuitem"`), suportar fechamento via tecla `Escape` e fechar automaticamente ao acionar qualquer uma de suas ações ou ao perder foco.
- **FR-005 (StudyEditView - Pílula de Status de Rascunho)**: Ao lado do título principal em `StudyEditView.vue`, renderizar uma pílula de status (`.draft-status-pill`) com as seguintes variações reativas:
  - **Estado "Salvando…"**: quando `state.saving === true`, com animação de pulso discreta ou ícone de sincronização.
  - **Estado "Rascunho salvo neste navegador"**: quando `dirty === true` ou `isDraftRestored === true` (alterações preservadas no `localStorage`), com tom neutro/informativo.
  - **Estado "Alterações salvas"**: quando `dirty === false` e `state.saving === false`, indicando integridade com o backend.
- **FR-006 (StudyEditView - Semântica de Acessibilidade)**: A pílula de status do editor deve declarar `role="status"` e `aria-live="polite"`, permitindo que leitores de tela anunciem transições de salvamento sem interromper a digitação.
- **FR-007 (ActiveReadingBar - Alvos Táteis)**: Todos os botões de ação em `ActiveReadingBar.vue` (botões de navegação sequencial, botões de ação em massa e botão de fechar `.close-btn`) devem possuir dimensões mínimas de 44x44px em viewports móveis (`<= 767px`) e quando a mídia de ponteiro indicar toque (`@media (pointer: coarse)`).
- **FR-008 (StudyTabs - Alvos Táteis)**: Os botões de aba em `StudyTabs.vue` (`role="tab"`) devem garantir altura mínima de 44px e área de toque confortável em qualquer resolução ou densidade de tela.

---

## 4. Requisitos Não Funcionais e Restrições Arquiteturais

- **NFR-001 (Zero Emojis)**: Proibição absoluta de emojis no código-fonte, nos templates Vue, nos estilos CSS, nos commits e na documentação.
- **NFR-002 (Imunidade Cromática aos 10 Temas)**: Não utilizar cores hexadecimais fixas nos novos elementos (menu, pílula de status, botões). Usar estritamente variáveis de tema (`var(--color-...)` e `var(--radius-...)`).
- **NFR-003 (Preservação de Dados e Backend Intacto)**: Nenhuma migração de banco, rota de backend ou alteração em APIs é necessária. Todo o escopo é estritamente no frontend Vue 3.
- **NFR-004 (Desempenho e Bundle)**: Reutilizar o componente existente `DropdownMenu.vue` e utilitários já disponíveis, sem adição de dependências npm externas.

---

## 5. Critérios de Aceitação

- [ ] Em `StudyView.vue`, o cabeçalho renderiza primariamente o botão "Editar estudo" e o botão de menu suspenso "Mais opções". O botão de lixeira não é visível diretamente na barra principal.
- [ ] No menu suspenso de `StudyView.vue`, a opção "Mover para a lixeira" dispara o `TrashConfirmModal.vue`, que remove o estudo e redireciona para a página do livro com segurança.
- [ ] Quando `canEdit === false`, a opção de lixeira e o botão de edição não aparecem no DOM.
- [ ] Em `StudyEditView.vue`, a pílula de status reflete dinamicamente as alterações: exibe "Rascunho salvo neste navegador" ao editar um campo, "Salvando…" ao clicar em salvar, e "Alterações salvas" após conclusão bem-sucedida.
- [ ] Em dispositivos móveis ou sob `@media (pointer: coarse)`, todos os botões de `ActiveReadingBar.vue`, `StudyView.vue` e `StudyTabs.vue` possuem alvos de toque maiores ou iguais a 44x44px.
- [ ] A suíte completa de testes (`npm test`, `pytest`, `npm run build`) passa com 100% de sucesso.
