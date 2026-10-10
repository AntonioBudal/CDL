# Research: F0.8.01 — Curadoria Editorial, Biblioteca Ativa e Novo Header Global

## Contexto e Objetivos Técnicos

A feature F0.8.01 inaugura o Roadmap 0.8 (v1.1.0-EXEC), executando duas grandes transformações fundacionais na arquitetura visual e na ergonomia de interação do Leitorum:
1. **Reestruturação do Header Global (App Shell)**: Transição do cabeçalho monolítico e superlotado (15 elementos em linha) para uma arquitetura em 3 zonas operacionais semanticamente delimitadas (Alternativa A), com menu retrátil "Mais ▾" para utilitários secundários e transferência obrigatória da ação de logout ("Sair") para o menu suspenso do usuário.
2. **Curadoria Editorial e Biblioteca Ativa (`/livros`)**: Eliminação definitiva da coluna estática lateral de cadastro (que ocupava ~35% da tela permanentemente), expansão do acervo para largura total, introdução da seção "Em Andamento" (Hero Card da leitura ativa) e migração do cadastro de novas obras para um componente compartilhado de gaveta lateral deslizante acessível (`Drawer.vue`).

---

## Decisões Técnicas e Arquitetura

### 1. Novo Header Global em 3 Zonas Operacionais (Alternativa A)

- **Decisão**: Dividir o cabeçalho global autenticado em 3 blocos visuais e semânticos claros:
  1. **Bloco Esquerdo (Marca)**: Logotipo minimalista `Leitorum` com link para a raiz do acervo.
  2. **Bloco Central (Navegação Primária + Menu "Mais")**:
     - 4 abas diretas reservadas ao ciclo ativo de leitura diária: **Livros**, **Destaques**, **Revisão** e **Inbox**.
     - Menu suspenso retrátil **"Mais ▾"**: reúne utilitários secundários e de ciclo estendido: **Importar**, **Amigos**, **Ajustes**, **Lixeira** e **Administração** (exclusivo para administradores).
     - Badges de notificação/pendências em `Amigos` e `Inbox` continuam plenamente visíveis e reativos.
  3. **Bloco Direito (Centro de Ferramentas e Identidade)**:
     - Pílula minimalista de **Busca Global**: sem o badge textual `Ctrl K`, apenas ícone e texto suave 'Buscar' para manter o cabeçalho leve.
     - Botão de ação primária de **Captura**: contendo **apenas o `+`** com destaque intencional arredondado/circular e tooltip contextual (`Ctrl+Shift+C`).
     - Indicador discreto de **Sincronização** (`SyncStatusBadge`): **estritamente um ícone pequeno** com cor semântica e tooltip explicativo, sem caixas escuras, bordas duras ou textos.
     - Centro de **Notificações** (sino sobre superfície transparente com badge).
     - **Menu do Usuário (Avatar/Iniciais)**: Dropdown suspenso unificado (`UserDropdown.vue`) contendo identificação do usuário, link de perfil e botão de encerramento seguro de sessão ("Sair").
- **Racional de Centralização e Hierarquia**:
  - Centralização horizontal matemática via CSS Grid (`1fr auto 1fr`): resolve a assimetria entre o bloco esquerdo (marca ~100px) e o bloco direito (~350px), garantindo que as abas fiquem matematicamente centradas na viewport.
  - Eliminação do badge `Ctrl K` e textos compridos no botão de captura: limpa a densidade cognitiva, reservando destaque de botão real exclusivamente para a captura (`+`).
  - Redução de `SyncStatusBadge` a apenas um ícone: trata telemetria passiva com a sutileza que lhe cabe, sem disputar atenção com as ações primárias.
  - Trata o logout como ação administrativa/de conta, removendo uma ação destrutiva solta concorrendo com o foco de estudo.
- **Alternativas consideradas**:
  - *Manter abas em rolagem horizontal (overflow-x)*: Rejeitada porque oculta itens vitais e degrada a usabilidade no desktop.
  - *Menu lateral permanente (Sidebar)*: Rejeitada porque consumiria espaço horizontal contínuo de leitura e desvirtuaria a identidade do Leitorum.

### 2. Componentização Desacoplada do App Shell

- **Decisão**: Extrair a lógica monolítica do `<header>` de `App.vue` em componentes coesos e reutilizáveis:
  - `GlobalHeader.vue`: Contêiner mestre com a marcação semântica e disposição dos 3 blocos.
  - `NavigationTabs.vue`: Abas principais de leitura + dropdown retrátil "Mais ▾" com gerenciamento de foco e atributos ARIA (`aria-haspopup="true"`, `aria-expanded`).
  - `UserDropdown.vue`: Gatilho com avatar/iniciais, nome do usuário, dropdown acessível com perfil e botão `Sair` com confirmação.
- **Racional**:
  - Simplifica a manutenção do `App.vue`.
  - Permite testes unitários isolados da navegação e do menu do usuário.

### 3. Componente `Drawer.vue` Compartilhado e Acessível

- **Decisão**: Implementar `frontend/src/components/ui/Drawer.vue` como componente estrutural reutilizável:
  - Largura de 420px no desktop e 100% da viewport em telas móveis (< 768px).
  - Animação acelerada por GPU: `transform: translateX(0)` (aberto) e `transform: translateX(100%)` (fechado) em 220ms com curva `cubic-bezier(0.16, 1, 0.3, 1)`.
  - Backdrop suave semi-transparente com transição de opacidade em 200ms.
  - Acessibilidade:
    - Diálogo modal nativo com `role="dialog"`, `aria-modal="true"`.
    - Foco automático no primeiro campo ou elemento focável ao abrir.
    - Retorno do foco para o elemento disparador ao fechar.
    - Fechamento imediato ao pressionar `Esc` ou clicar no backdrop.
  - Suporte estrito a `prefers-reduced-motion`: duração de 0.01ms instantânea quando ativado.
- **Racional**:
  - Fornece um padrão consistente de edição e foco sem distrações que poderá ser reutilizado em outras partes do sistema.

### 4. Redesign da Biblioteca (`BooksView.vue`)

- **Decisão**:
  - Remover a coluna lateral estática `aside.panel.form-panel` do layout da biblioteca, permitindo que a área de acervo ocupe 100% da largura útil.
  - Criar seção de topo **"Em Andamento"** com um **Hero Card** da leitura ativa destacando a obra mais recente, seu progresso/estudos e link "Continuar Leitura".
  - Integrar o botão proeminente `+ Adicionar Livro` na barra de ações da biblioteca (`LibraryToolbar.vue` ou cabeçalho do acervo).
  - No clique de `+ Adicionar Livro`, disparar o `Drawer.vue` contendo o formulário de cadastro (Título, Autor opcional, Categorias opcionais via `CategoryInput.vue`).
  - Preservar integralmente as abas "Meu Acervo" e "Compartilhados Comigo", os modos Grade e Lista, a busca rápida e a filtragem por chips de categoria.
  - Refinar o cartão de livro na grade com proporções editoriais realistas e microinteração tátil de hover (`transform: translateY(-4px)` em 150ms).
- **Racional**:
  - Transforma a biblioteca em uma verdadeira "Mesa do Leitor", devolvendo mais de 35% de área útil para visualização das capas e metadados.

### 5. Imunidade Cromática e Respeito aos 10 Temas Nativos

- **Decisão**:
  - Todos os estilos do novo Header, do Drawer e da página de Livros devem consumir exclusivamente as variáveis semânticas CSS já auditadas em `palettes.css` e `tokens.css`:
    - `--color-surface`, `--color-page`, `--color-surface-soft`, `--color-surface-hover`, `--color-card-hover`.
    - `--color-text`, `--color-muted`, `--color-subtle`, `--color-meta`, `--color-hover-text`.
    - `--color-border`, `--color-border-strong`, `--color-border-hover`, `--color-border-divider`.
    - `--color-accent`, `--color-accent-hover`, `--color-on-accent`, `--color-selected-text`, `--color-selected-bg`.
    - `--radius-panel`, `--radius-card`, `--radius-button`, `--radius-control`.
  - Proibição absoluta de cores hexadecimais literais arbitrárias.

### 6. Conformidade Visual: ZERO EMOJIS

- **Decisão**: Uso exclusivo de tipografia editorial limpa e ícones SVG semânticos do componente `Icon.vue` (`book-open`, `pencil`, `rotate-ccw`, `inbox`, `more-horizontal`, `search`, `bell`, `sliders`, `trash`, `users`, `plus`, `x`, `log-out`). Ausência total de emojis.
