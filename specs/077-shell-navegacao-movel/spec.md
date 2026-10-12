# Feature Specification: Shell e Navegação Móvel

**Feature Branch**: `077-shell-navegacao-movel`  
**Created**: 2026-10-12  
**Status**: Draft  
**Input**: Problemas P-01, P-02, P-03, P-09, P-10, P-11 (shell), P-13 da Auditoria de Responsividade e Contratos da Feature 076.

Esta feature restaura a barra de navegação inferior no smartphone, limpa o cabeçalho superior móvel, completa a gaveta secundária "Mais", protege elementos fixos contra sobreposição, reescreve o `ShareModal` com tokens CSS nativos e ancora os testes de navegação móvel aos seletores reais do template.

---

## User Scenarios & Testing

### User Story 1 - Navegação Móvel por Barra Inferior (Priority: P1)
Como leitor acessando o caderno no smartphone (< 768px), quero ter uma barra de navegação fixa na parte inferior da tela com 5 destinos simétricos e alvos de toque confortáveis, para alternar rapidamente entre as áreas de estudo sem poluição visual no topo.

**Why this priority**: P-01 é um defeito crítico que quebrou a navegação móvel desde o commit 2a3c0f9, acumulando abas no cabeçalho e reservando espaço vazio em `#app`.

**Independent Test**: Abrir qualquer tela autenticada em 375px; verificar que a barra inferior fixa está visível com 5 itens de no mínimo 44×44px, com indicador ativo na rota atual e sem rolagem horizontal no cabeçalho superior.

**Acceptance Scenarios**:
1. **Dado** uma viewport móvel `< 768px`, **quando** o leitor está em qualquer tela autenticada, **então** a barra inferior fixa é exibida no rodapé com 5 colunas: Início (`/dashboard`), Livros (`/books`), Destaques (`/highlights`), Revisão (`/review`) e o gatilho "Mais".
2. **Dado** a barra inferior móvel, **quando** inspecionada a ergonomia, **então** cada botão possui área tátil $\ge 44 \times 44\text{ px}$ e a barra respeita `env(safe-area-inset-bottom)`.
3. **Dado** uma viewport desktop ou tablet ($\ge 768\text{px}$), **quando** o leitor navega, **então** a barra inferior fica oculta e o menu de abas superior opera normalmente no `GlobalHeader`.

---

### User Story 2 - Cabeçalho Superior Limpo e Gaveta "Mais" Completa (Priority: P1)
Como leitor no celular, quero um cabeçalho superior compacto e uma gaveta "Mais" que contenha todos os destinos secundários do sistema com seus respectivos contadores, para acessar ferramentas complementares sem perder espaço de leitura.

**Why this priority**: Evita que o topo da tela fique saturado de botões e garante que rotas como Caixa de Entrada, Amigos, Ajustes, Lixeira e Importar permaneçam acessíveis no smartphone.

**Independent Test**: Em 375px, verificar que o cabeçalho superior exibe apenas marca, busca, captura, sino e avatar. Ao tocar em "Mais" na barra inferior, a gaveta desliza exibindo todos os destinos secundários com seus badges.

**Acceptance Scenarios**:
1. **Dado** o cabeçalho superior em `< 768px`, **quando** renderizado, **então** as abas textuais de navegação ficam ocultas no topo, restando apenas o logo Leitorum, gatilho de busca global, captura rápida, notificações e avatar de perfil.
2. **Dado** o acionamento do botão "Mais" na barra inferior, **quando** aberto o `MobileMoreMenu`, **então** a gaveta lista: Caixa de Entrada (com badge de pendências), Salão de Amigos (com badge social), Ajustes, Lixeira e Importar estudo.
3. **Dado** o leitor tocando em qualquer destino da gaveta ou fora dela, **quando** a ação ocorre, **então** a gaveta fecha suavemente e direciona para a rota selecionada.

---

### User Story 3 - Offsets de Elementos Flutuantes e Notificações (Priority: P2)
Como leitor no celular, quero que mensagens flutuantes (toasts), a barra de ações em lote da Lixeira e o botão de preview dos Ajustes apareçam acima da barra inferior sem sobreposição, e que o painel de notificações não seja cortado na borda esquerda da tela.

**Why this priority**: Resolve os problemas P-09 e P-10, garantindo que botões de ação e avisos temporários não fiquem escondidos atrás da navegação móvel.

**Independent Test**: Disparar toast em `StudyView`, acessar a Lixeira com itens selecionados e abrir notificações em 375px e 320px; constatar ausência de sobreposição e alinhamento do painel.

**Acceptance Scenarios**:
1. **Dado** uma viewport móvel `< 768px`, **quando** o token `--mobile-nav-offset` é fornecido pelo shell, **então** toasts, a barra de lote da lixeira (`.trash-batch-bar`) e o botão flutuante de Ajustes (`.fab-preview`) posicionam-se elevados acima da barra de navegação.
2. **Dado** o dropdown de notificações em telas $\le 430\text{px}$, **quando** expandido, **então** ocupa a largura útil da tela com margem de segurança lateral, sem extrapolar a borda esquerda do viewport.

---

### User Story 4 - Reescrita Nativa do `ShareModal` e Purga de CSS Morto (Priority: P2)
Como leitor compartilhando um estudo, quero que a janela de compartilhamento tenha visual consistente com o tema do sistema, e como mantenedor do código, quero eliminar regras de CSS morto no shell.

**Why this priority**: P-03 quebra a exibição do modal de compartilhamento em qualquer resolução por depender de utilitários Tailwind ausentes; P-13 reduz ruído e duplicidade no shell.

**Independent Test**: Abrir o modal de compartilhar estudo em tema claro e tema escuro nos viewports 375px e 1440px; confirmar renderização de backdrop, centralização e cartões usando variáveis canônicas sem classes Tailwind.

**Acceptance Scenarios**:
1. **Dado** o componente `ShareModal.vue`, **quando** renderizado, **então** utiliza `<style scoped>` com tokens nativos (`--color-surface`, `--color-border`, `--color-text`, `--color-accent`), sem depender de Tailwind.
2. **Dado** o arquivo `App.vue`, **quando** auditado o bloco de estilos, **então** as regras obsoletas de cabeçalho que não casam com `GlobalHeader.vue` são purgadas sem qualquer alteração na aparência desktop.

---

### User Story 5 - Testes de Navegação Móvel Amarrados aos Templates Reais (Priority: P1)
Como desenvolvedor, quero que os testes automatizados de navegação móvel validem seletores presentes nos templates Vue reais, para evitar falsos positivos e regressões silenciosas.

**Why this priority**: P-02 demonstrou que os testes passavam mesmo com a barra inferior inoperante porque só verificavam strings no CSS global.

**Independent Test**: Executar `npm test`; garantir que a suíte falhe caso uma classe CSS estilizada seja removida do template Vue correspondente.

**Acceptance Scenarios**:
1. **Dado** a suíte de testes de navegação móvel, **quando** executada, **então** verifica que a classe associada à barra móvel existe no template Vue e que possui regras de fixação inferior em `< 768px`.
2. **Dado** `ShareModal.vue`, **quando** testado, **então** confirma ausência total de classes Tailwind e presença de tokens canônicos.

---

## Requirements

### Functional Requirements
- **FR-001**: A aplicação DEVE renderizar uma barra de navegação inferior fixa em telas `< 768px` com 5 alvos acessíveis: Início, Livros, Destaques, Revisão e "Mais".
- **FR-002**: Cada alvo da barra inferior DEVE respeitar a área de toque mínima de $44 \times 44\text{ px}$.
- **FR-003**: As abas de navegação no cabeçalho superior DEVEM ser ocultadas em viewports `< 768px`.
- **FR-004**: O menu `MobileMoreMenu` DEVE conter atalhos para: Caixa de Entrada, Amigos, Ajustes, Lixeira e Importar estudo, preservando badges numéricos reativos.
- **FR-005**: O shell DEVE expor o token CSS `--mobile-nav-offset: calc(56px + env(safe-area-inset-bottom, 0px))` em `< 768px`.
- **FR-006**: Os elementos fixos de rodapé (toasts, lote da Lixeira, FAB de Ajustes) DEVEM utilizar `--mobile-nav-offset` em telas móveis.
- **FR-007**: O painel `NotificationsDropdown` DEVE adaptar sua largura e ancoragem em telas $\le 430\text{px}$ para evitar transbordamento lateral esquerdo.
- **FR-008**: O componente `ShareModal.vue` DEVE ter suas classes utilitárias Tailwind substituídas por regras CSS autorais com tokens de tema.
- **FR-009**: O CSS scoped legado e morto em `App.vue` referente ao cabeçalho DEVE ser removido.
- **FR-010**: A suíte de testes de navegação móvel DEVE verificar a integridade da correspondência template $\leftrightarrow$ CSS.

---

## Success Criteria

- **SC-001**: Em 320px, 375px e 767px, a barra inferior fixa é exibida sem overflow horizontal (`scrollWidth === clientWidth`).
- **SC-002**: 100% dos botões da barra inferior e gaveta "Mais" cumprem a métrica WAI-ARIA de alvo tátil $\ge 44 \times 44\text{ px}$.
- **SC-003**: `ShareModal` renderiza com backdrop e posicionamento centralizado correto nos 10 temas.
- **SC-004**: Nenhum elemento fixo inferior sobrepõe a barra de navegação móvel.
- **SC-005**: `npm test` e `npm run build` passam com 100% de sucesso.
