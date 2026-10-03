# Research & Decisões Arquiteturais: Hierarquia e Ergonomia de Header Actions no Leitor

**Feature**: `050-ergonomia-header-actions`  
**Data**: 2026-10-03  
**Status**: Concluído (Todas as decisões técnicas e padrões estabelecidos)

---

## 1. Decisão 1: Arquitetura do Componente de Menu Suspenso (`DropdownMenu.vue`)

- **Contexto**: Atualmente, `StudyView.vue` renderiza 5 a 6 botões lado a lado. Precisamos agrupar ações utilitárias secundárias sob um menu `•••` acessível e reutilizável.
- **Decisão**: Criar um componente genérico e modular `frontend/src/components/ui/DropdownMenu.vue` baseado em Vue 3 `<script setup lang="ts">`, com suporte a itens via prop ou slot customizado, ícones SVG inline e variantes semânticas (`default`, `danger`).
- **Rationale**:
  - Encapsula a lógica de estado aberto/fechado, foco de teclado e clique fora (`click-outside`).
  - Pode ser reaproveitado em outras views no futuro (ex.: `BookView.vue`, `ReviewHubView.vue`).
  - Mantém o leitor `StudyView.vue` limpo e focado no seu fluxo de estudo.
- **Alternativas Consideradas**:
  - *Markup inline diretamente em StudyView.vue*: Rejeitado por duplicar código de acessibilidade e sobrecarregar o template do leitor.
  - *Biblioteca de terceiros (ex.: Headless UI, Floating UI, Radix-vue)*: Rejeitado por violar o princípio de dependências mínimas e controle total sobre CSS/superclasses do Leitorum.

---

## 2. Decisão 2: Estratégia de Posicionamento, Overflow e Fechamento

- **Contexto**: Menus suspensos em layouts responsivos podem vazar para fora da tela (overflow horizontal) ou sofrer clipping se houver `overflow: hidden` nos ancestrais.
- **Decisão**:
  - Posicionamento relativo ancorado ao botão disparador (`position: absolute; right: 0; top: calc(100% + 4px);`), com `z-index: 100`.
  - Fechamento automático via diretiva/listener defensivo de `click-outside` (escutando `pointerdown` na janela) e tecla `Escape`.
  - Alinhamento à direita (`right: 0`) para garantir que o menu cresça para dentro da viewport, evitando quebras na margem direita de telas estreitas.
- **Rationale**: Não necessita de Teleport complexo já que `.page-header` em `StudyView.vue` não possui `overflow: hidden`, evitando problemas de sincronização de coordenadas de scroll.
- **Alternativas Consideradas**:
  - *Teleport para `body` com cálculo manual de getBoundingClientRect*: Complexidade desnecessária para menus de cabeçalho estático, com risco de dessincronia no resize.

---

## 3. Decisão 3: Hierarquia de Ações no Desktop (≥ 768px)

- **Contexto**: No desktop, todos os botões tinham estilo `secondary`, criando ambiguidade visual sobre o que era a ação primária de gestão do estudo.
- **Decisão**:
  - **Ação Primária:** Botão "Editar estudo" estilizado como primário (`button primary`), com destaque visual claro e atalho direto.
  - **Ação Secundária em Destaque:** Botão "Compartilhar" mantido visível (`secondary share-action`) ao lado do botão primário quando `canEdit === true`.
  - **Menu de Ações `•••`:** Agrupa utilitários:
    1. "Histórico de versões" (com ícone de relógio).
    2. "Exportar estudo" (com ícone de download/exportação).
    3. Divisor visual semântico.
    4. "Mover para a lixeira" (com ícone de lixeira, cor e destaque `danger`).
- **Rationale**: Reduz a carga cognitiva de 5 botões para 2 botões + 1 menu discreto, permitindo ao usuário identificar instantaneamente a hierarquia sem esconder funcionalidades essenciais.
- **Alternativas Consideradas**:
  - *Esconder "Editar estudo" no menu*: Rejeitado porque editar anotações é a ação mais recorrente no ciclo de estudo.
  - *Deixar "Mover para a lixeira" exposto*: Rejeitado por gerar risco de clique destrutivo e poluição visual desnecessária.

---

## 4. Decisão 4: Ergonomia no Mobile (< 768px e < 640px)

- **Contexto**: No mobile, botões quebravam em 2 ou 3 linhas e o breadcrumb consumia até 3 linhas verticais.
- **Decisão (Alinhada com o Usuário - Q1: A e Q2: A)**:
  - **Header Actions no Mobile (< 768px)**:
    - O cabeçalho exibe exatamente **2 controles interativos**:
      1. Botão "Editar" compacto (ícone de lápis + rótulo acessível `aria-label="Editar estudo"`, tamanho tátil mínimo de 44x44px).
      2. Botão acionador `•••` ("Mais opções", tamanho tátil de 44x44px).
    - As ações secundárias (*Compartilhar*, *Histórico*, *Exportar* e *Lixeira*) ficam centralizadas dentro do menu suspenso.
  - **Breadcrumb Inteligente (< 640px)**:
    - Em telas estreitas, a trilha extensa (`Meus livros / Livro / Capítulo`) colapsa em um botão elegante: `← Voltar ao capítulo`, exibindo o nome do capítulo atual com truncamento defensivo (`text-overflow: ellipsis`) e link direto para a rota do capítulo.
- **Rationale**: Reduz a altura vertical do topo móvel em mais de 40%, liberando a área nobre acima da dobra para o título do estudo e o texto das seções, cumprindo WCAG 2.1 Critério 2.5.5 (alvos ≥ 44x44px).
- **Alternativas Consideradas**:
  - *Manter botão de Compartilhar visível no mobile*: Rejeitado pelo usuário (Q1: A) para preservar largura livre para o título.
  - *Rolagem horizontal no breadcrumb*: Rejeitado pelo usuário (Q2: A) em favor de retorno rápido com 1 toque.

---

## 5. Decisão 5: Acessibilidade Semântica (WAI-ARIA) e Ciclo de Foco

- **Contexto**: Leitores de tela e usuários de teclado devem poder operar o menu sem armadilhas de foco.
- **Decisão**:
  - Botão disparador: `type="button"`, `aria-haspopup="menu"`, `:aria-expanded="isOpen"`, `aria-label="Mais opções do estudo"`.
  - Contêiner do menu: `role="menu"`, `aria-orientation="vertical"`, `tabindex="-1"`.
  - Itens de ação: `role="menuitem"`, `tabindex="0"` (item focado) ou `-1` (demais itens).
  - Teclas suportadas:
    - `Enter` / `Space` no disparador: abre o menu e foca no primeiro item.
    - `ArrowDown` / `ArrowUp`: navegação circular entre os itens disponíveis.
    - `Home` / `End`: pula para o primeiro / último item.
    - `Escape`: fecha o menu e devolve o foco imediatamente para o botão disparador.
- **Rationale**: Conformidade estrita com as diretrizes WAI-ARIA Menu Button Pattern.
- **Alternativas Consideradas**:
  - *Menu básico sem controle de foco*: Rejeitado por reprovar auditorias de acessibilidade.

---

## 6. Decisão 6: Não-Interferência com Listeners Globais (Active Recall)

- **Contexto**: `StudyView.vue` possui listener de teclado na janela para o modo de Active Recall (teclas `j`, `k`, `Escape`).
- **Decisão**:
  - O manipulador de teclado do `DropdownMenu` deve utilizar `event.stopPropagation()` e `event.preventDefault()` nas teclas tratadas (`Escape`, setas) para que o fechamento do menu não encerre acidentalmente a sessão de Active Recall subjacente.
- **Rationale**: Garante independência total entre a navegação do menu e a sessão de leitura ativa.
