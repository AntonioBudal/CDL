# Feature Specification: 009 — Invisível: Superclasse Silenciosa & Editorial e Limpeza de Ajustes

**Feature Branch**: `009-invisivel-editorial`  
**Created**: 2026-09-19  
**Status**: Ready  
**Input**: User description: "Implementação da Superclasse 'Invisível' (Silenciosa & Editorial), E remoção frontend dos ajustes desnecessários que a SuperClasse é responsável agora"

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Ativação da Superclasse Invisível com Desmaterialização de Caixas e Microinterações Editoriais (Priority: P1) 🎯 MVP

Como leitor e estudante focado em textos longos,  
Quero selecionar a Superclasse "Invisível" nas opções de aparência do aplicativo,  
Para que as bordas de cartões, caixas delimitadoras e sombras pesadas desapareçam, dando lugar a uma experiência editorial refinada onde a hierarquia é regida por espaço em branco, tipografia e microinterações de leitura (deslocamento horizontal sutil e sublinhado progressivo).

**Why this priority**: É o núcleo funcional da Superclasse Invisível. Transforma a sensação estética do Caderno de Leitura em uma publicação literária clássica e entrega valor imediato e independente como MVP.

**Independent Test**: Ativar "Invisível" nas configurações de aparência, navegar para o acervo de livros e para a tela de leitura de capítulos e verificar que:
1. Os cartões do acervo e blocos de conteúdo perdem bordas de caixa rígidas e sombras de levitação, integrando-se naturalmente ao fundo do tema ativo.
2. Ao passar o mouse sobre itens do acervo ou tópicos (`:hover`), o elemento sofre um deslocamento horizontal de leitura para a direita (`translateX(4px)`) com transição suave (~200ms).
3. Títulos e links interativos exibem um sublinhado progressivo fino que se desenha da esquerda para a direita no hover (`transform-origin: left`).
4. Os botões convencionais adotam aparência limpa, tipográfica e editorial, sem blocos plásticos pesados.

**Acceptance Scenarios**:
1. **Given** o usuário na tela de Ajustes, **When** seleciona a Superclasse "Invisível — Silenciosa & Funcional", **Then** a interface atualiza em tempo real, eliminando bordas duras de cartões e caixas sem exigir recarregamento da página.
2. **Given** a estante de livros sob a Superclasse Invisível, **When** em repouso, **Then** os livros são separados por ritmo tipográfico e respiro visual em vez de grades de caixas e sombras.
3. **Given** um item interativo ou título sob a Invisível, **When** o cursor do mouse passa sobre ele (*hover*), **Then** o texto desloca-se suavemente 4px para a direita acompanhado por uma linha de sublinhado progressiva da esquerda para a direita.
4. **Given** um botão de ação sob a Invisível, **When** exibido na interface, **Then** ele se apresenta como um controle editorial elegante, com borda sutil ou nula, preservando a legibilidade e contraste do tema ativo.

---

### User Story 2 - Transição de Página em Cascata Temporal (*Staggered Fade-Up*) (Priority: P2)

Como usuário navegando entre o acervo, capítulos e anotações,  
Quero que o conteúdo chegue em uma cascata temporal suave e ordenada ao abrir uma nova tela,  
Para ter uma percepção visual límpida e relaxante da estrutura do texto.

**Why this priority**: Complementa a atmosfera editorial da Superclasse Invisível, substituindo cortes secos ou deslizes genéricos por uma entrada sequencial dos elementos estruturais.

**Independent Test**: Navegar entre rotas (por exemplo, clicar em um livro para abrir seus detalhes ou abrir um capítulo de estudo) sob a Superclasse Invisível e observar a entrada sequencial: o cabeçalho/título surge primeiro, seguido dos metadados e do texto corrido em intervalos defasados de 40ms.

**Acceptance Scenarios**:
1. **Given** o usuário navegando para uma nova página sob a Invisível, **When** a rota se completa, **Then** os elementos principais entram em cascata temporal (*staggered fade-up*): título primeiro (0ms), metadados/autores em seguida (40ms), e corpo do conteúdo por último (80ms–120ms).
2. **Given** a transição de saída de página, **When** o usuário clica para navegar, **Then** o conteúdo esvanece suavemente em opacidade sem causar saltos ou tremores na viewport.

---

### User Story 3 - Simplificação do Painel de Ajustes via Remoção dos Controles Obsoletos (Priority: P3)

Como usuário personalizando minha experiência de leitura,  
Quero uma tela de Ajustes enxuta e intuitiva, sem controles redundantes que já são governados de forma superior pelas Superclasses,  
Para não ter que gerenciar configurações conflitantes ou desnecessárias.

**Why this priority**: A introdução das Superclasses (Zero-G, Mecânica, Invisível, etc.) assumiu com precisão milimétrica o controle do raio de curvatura de caixas (`style`), da elevação/sombras de cartões (`surface`) e do estilo estático de botões (`button-style`). Manter esses seletores manuais gera ruído cognitivo e potencial conflito estético.

**Independent Test**: Acessar a tela de Ajustes e constatar que:
1. Os campos legados "Formato das caixas" (`style`), "Cartões / Contraste da interface" (`surface`) e "Preenchimento de Botões" (`button-style`) não estão mais visíveis na interface de Ajustes.
2. Controles fundamentais do usuário como Tipografia (24 fontes, tamanho, alinhamento), Cores (10 temas, cores de destaque), Densidade de espaçamento, Abas e Disposição do Acervo permanecem intactos e perfeitamente funcionais.
3. A persistência local em navegadores que já continham dados gravados migra silenciosamente sem falhas ou exceções.

**Acceptance Scenarios**:
1. **Given** a tela de Ajustes (`/ajustes`), **When** renderizada para o usuário, **Then** os grupos e campos obsoletos de formato de caixas, contraste de superfície de cartões e preenchimento de botões não são renderizados.
2. **Given** uma sessão de usuário com preferências salvas anteriormente em versões passadas, **When** o aplicativo inicializa, **Then** os campos removidos são descartados ou ignorados com segurança sem quebrar o objeto de preferências ativas.
3. **Given** o catálogo de campos no frontend (`window.cadernoAppearance`), **When** consultado, **Then** expõe apenas os campos ativos oficiais, mantendo tipagem consistente em TypeScript.

---

### User Story 4 - Intensidade Paramétrica, Blindagem de Leitura e Acessibilidade Universal (Priority: P4)

Como usuário com preferências específicas de movimento ou sensibilidade visual,  
Quero que o deslocamento lateral e as transições em cascata respeitem o controle de intensidade e a redução de movimento,  
Para que a interface nunca cause desconforto visual.

**Why this priority**: Garante total acessibilidade e conformidade com os padrões estabelecidos na Constituição do projeto.

**Independent Test**: Alternar o seletor de intensidade entre Sutil (0.5x), Padrão (1.0x), Alta (1.5x) e Desativada (0.0x); verificar a escala proporcional do deslocamento lateral de 4px e das transições em cascata; verificar que com `prefers-reduced-motion: reduce` ou `data-motion="off"`, todos os deslocamentos e cascatas são neutralizados.

**Acceptance Scenarios**:
1. **Given** a intensidade configurada como "Sutil (0.5x)", **When** o cursor passa sobre um item editorial no hover, **Then** o deslocamento horizontal é escalado para 2px (`4px * 0.5`).
2. **Given** a intensidade configurada como "Alta (1.5x)", **When** o cursor passa sobre um item editorial no hover, **Then** o deslocamento horizontal é de 6px (`4px * 1.5`).
3. **Given** a intensidade configurada como "Desativada (0.0x)" ou o sistema em *prefers-reduced-motion*, **When** o usuário interage, **Then** todo deslocamento e cascata temporal são suprimidos (`0px`, sem atrasos), mantendo a diagramação editorial estática e imediata.
4. **Given** a leitura do texto corrido de capítulos e anotações (`.markdown-content`), **When** sob a Superclasse Invisível, **Then** o texto permanece rigorosamente imóvel.

---

### Edge Cases

- **Navegação Rápida entre Capítulos**: Se o usuário alternar rapidamente entre capítulos enquanto a cascata (*staggered fade-up*) estiver ocorrendo, a animação anterior é cancelada imediatamente para renderizar o novo texto sem acúmulo de atrasos.
- **Telas com Leitores de Tela / Navegação por Teclado**: O sublinhado progressivo e os deslocamentos no hover não afetam o anel de foco acessível (`:focus-visible`), que continua nítido e de acordo com o tema.
- **Temas de Alto Contraste e E-Ink**: Sob o tema E-Ink, a desmaterialização de caixas é complementada por linhas tipográficas puras, mantendo legibilidade máxima sem elementos cinzentos intermediários.
- **Migração de Dados no Navegador**: Usuários com chaves antigas de `style`, `surface` e `button-style` no `localStorage` não sofrem reset das outras preferências (como fontes e temas).

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE implementar a Superclasse "Invisível — Silenciosa & Funcional", ativada tanto pelo atributo `data-superclass="invisivel"` quanto pela classe CSS `.superclass-invisivel`.
- **FR-002**: A Superclasse Invisível NÃO DEVE alterar ou sobrescrever a escolha soberana do usuário quanto à fonte de leitura (24 fontes), tema cromático (10 temas), cor de destaque, alinhamento ou tamanho do texto.
- **FR-003**: Sob a Superclasse Invisível, os cartões do acervo (`.book-card`, `.book-list-item`) e caixas de formulário DEVEM desmaterializar bordas rígidas e sombras de relevo, estabelecendo a distinção de elementos por espaçamento e ritmo tipográfico.
- **FR-004**: No estado de sobreposição de cursor (*hover*), itens interativos editoriais e cartões de livros DEVEM apresentar deslocamento horizontal suave para a direita proporcional a `calc(4px * var(--sc-intensity))`.
- **FR-005**: Títulos de livros e links interativos sob a Invisível DEVEM exibir animação de sublinhado progressivo da esquerda para a direita no hover (`transform-origin: left`).
- **FR-006**: As transições de página sob a Invisível DEVEM aplicar uma cascata temporal suave (*staggered fade-up*) com atrasos progressivos de montagem (título: 0ms, subtítulo/autor: 40ms, metadados: 80ms, conteúdo: 120ms).
- **FR-007**: A Superclasse Invisível DEVE manter o texto corrido de leitura (`.markdown-content` e derivados) estritamente imóvel (`transform: none !important; animation: none !important;`).
- **FR-008**: O sistema DEVE remover da tela de Ajustes (`SettingsView.vue` / `AppearanceControls.vue`) os seletores de formato de caixas (`style`), contraste de cartões (`surface`) e preenchimento de botões (`button-style`).
- **FR-009**: O catálogo de campos no frontend (`window.cadernoAppearance.fields`) e os tipos TypeScript (`appearance.d.ts`) DEVEM ser atualizados para refletir a remoção dos campos obsoletos, mantendo total integridade sem avisos de tipagem.
- **FR-010**: A rotina de normalização e leitura de preferências em `appearance-bootstrap.js` DEVE aceitar objetos de preferências pré-existentes no `localStorage`, descartando os campos removidos sem corromper as preferências salvas do usuário.
- **FR-011**: O controle de multiplicador de intensidade (`--sc-intensity`) DEVE dosar proporcionalmente o deslocamento lateral e as cascatas da Invisível: Sutil (0.5x), Padrão (1.0x), Alta (1.5x) e Desativada (0.0x).
- **FR-012**: O sistema DEVE neutralizar sumariamente qualquer deslocamento ou cascata sob `prefers-reduced-motion: reduce` e `data-motion="off"`.

---

### Key Entities *(include if feature involves data)*

- **SuperclassInvisivelTokens**:
  - `--sc-border-radius`: `0px` ou herança transparente.
  - `--sc-shadow-idle`: `none` / `transparent`.
  - `--sc-shadow-hover`: `none` / `transparent`.
  - `--sc-reading-shift-x`: `calc(4px * var(--sc-intensity))`.
  - `--sc-transition-duration`: `200ms`.
  - `--sc-transition-easing`: `cubic-bezier(0.2, 0, 0, 1)`.
- **PrunedAppearanceFields**:
  - Campos removidos do frontend: `style` (formato de caixas), `surface` (contraste de cartões), `button-style` (preenchimento de botões).
  - Campos preservados no frontend: `theme`, `accent`, `density`, `align`, `font`, `highlight`, `reader-size`, `motion`, `button-width`, `tabs`, `library`, `container`, `superclass`, `superclass-intensity`.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A seleção da Superclasse Invisível remove instantaneamente contornos e sombras pesadas de cartões e blocos em tempo real sem necessidade de recarregar a página.
- **SC-002**: 100% dos cartões e itens editoriais sob a Invisível realizam o deslocamento lateral no hover no tempo estrito de 200ms e amplitude exata de `calc(4px * var(--sc-intensity))`.
- **SC-003**: 100% das 24 fontes tipográficas e dos 10 temas de cor continuam operando de forma perfeitamente preservada e sem regressões.
- **SC-004**: O painel de Ajustes exibe zero controles obsoletos de `style`, `surface` e `button-style`, reduzindo a carga visual da tela.
- **SC-005**: 100% dos usuários existentes com preferências gravadas no `localStorage` continuam com suas opções de tema, fontes e biblioteca íntegras após a limpeza dos campos obsoletos.
- **SC-006**: A suíte de testes unitários do frontend continua atingindo 100% de aprovação e o build de produção (`npm run build`) conclui com zero erros de tipo e sem referências a campos órfãos.
- **SC-007**: 100% do texto corrido de estudos e capítulos permanece rigorosamente estático em repouso e durante qualquer interação.

---

## Assumptions

- A remoção dos campos de estilo estático de caixas e superfícies no frontend não impacta o backend ou banco de dados SQLite, pois essas preferências residem exclusivamente no cliente (`localStorage`).
- O comportamento padrão de fallback para elementos globais continua elegante caso a Superclasse esteja configurada como "Nenhuma" (`none`).
- A transição em cascata (*staggered fade-up*) utiliza aceleração por hardware GPU (`transform`, `opacity`) para garantir 60fps estáveis em dispositivos móveis e desktops.
