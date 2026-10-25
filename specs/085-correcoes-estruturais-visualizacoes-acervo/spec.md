# Feature Specification: Correções Estruturais nas Visualizações do Acervo

**Feature Branch**: `085-correcoes-estruturais-visualizacoes-acervo`

**Created**: 2026-10-24

**Status**: Draft

**Input**: User description: "Correcoes Estruturais nas Visualizacoes do Acervo"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Abertura e Flutuação Livre do Menu de Status sem Cortes (Priority: P1)

Como uma pessoa leitora utilizando a visualização em lista de estudos, desejo clicar no badge de status de qualquer estudo (inclusive na primeira ou na última linha da tabela) para alterar seu estado de leitura, de modo que o menu suspenso de opções flutue perfeitamente sobre as linhas vizinhas e bordas do contêiner, sem sofrer qualquer corte (*clipping*) por regras de overflow oculto.

**Why this priority**: O corte visual de menus suspensos impede a seleção de opções essenciais de status (como "Revisado" ou "Concluído") em estudos posicionados nos limites da tabela, degradando a usabilidade central do fluxo de acompanhamento de leitura.

**Independent Test**: Pode ser testado abrindo a visualização em lista, clicando no badge de status do primeiro estudo e do último estudo da lista, verificando que o menu `.status-dropdown-menu` é renderizado completamente visível, sobrepondo as bordas da tabela e linhas adjacentes com índice de profundidade adequado (`z-index: 1000` ou superior).

**Acceptance Scenarios**:

1. **Given** que a tabela de estudos possui múltiplos itens e o leitor clica no status da última linha, **When** o menu suspenso for aberto, **Then** o menu deve calcular o espaço disponível e abrir para cima ou flutuar livremente sem ser cortado pela borda inferior da tabela ou da página.
2. **Given** que o leitor clica no status de uma linha intermediária ou da primeira linha, **When** o menu suspenso se expande, **Then** as opções de status devem sobrepor as linhas adjacentes sem que `overflow: hidden` nas linhas ou no contêiner mutile a caixa do menu.
3. **Given** que o menu suspenso de status está aberto, **When** o leitor clica fora do menu ou pressiona Escape, **Then** o menu se fecha imediatamente sem deixar resíduos visuais.

---

### User Story 2 - Legibilidade Universal do Ícone de Ordenação em Todos os Temas (Priority: P2)

Como uma pessoa leitora navegando no acervo sob qualquer um dos 10 temas oficiais do Leitorum (claros, escuros ou sépia), desejo identificar claramente qual coluna da tabela está ordenando a lista e qual o sentido da ordenação (crescente ou decrescente), através de um indicador visual de seta nítido e com contraste adequado.

**Why this priority**: A perda de visibilidade da seta de ordenação desorienta a navegação analítica do usuário, tornando imperceptível se a lista está em ordem cronológica ou alfabética.

**Independent Test**: Pode ser testado clicando nos cabeçalhos ordenáveis ("Título", "Status", "Data") sob cada um dos 10 temas visuais canônicos, verificando que o ícone SVG `.sort-indicator` herda a cor exata do rótulo da coluna ativa via `stroke: currentColor` e mantém contraste legível WCAG AA.

**Acceptance Scenarios**:

1. **Given** que o tema ativo é um tema escuro (`noturno`, `crepusculo`, `nordico`, `grafite` ou `voltagem`), **When** o leitor clica no cabeçalho "Data" para ordenar, **Then** o ícone SVG de ordenação deve herdar a cor do texto do cabeçalho ativo (`color: currentColor; stroke: currentColor;`), permanecendo perfeitamente visível contra o fundo do cabeçalho.
2. **Given** que o tema ativo é um tema claro ou texturizado (`sepia`, `pergaminho`, `classico`, `editorial` ou `monocromatico`), **When** a ordenação é alternada entre crescente e decrescente, **Then** a geometria do ícone SVG permanece nítida, sem distorção ou desaparecimento de traços.

---

### User Story 3 - Alinhamento Geométrico Estrito do Grid da Tabela em Telas Largas (Priority: P3)

Como uma pessoa leitora utilizando monitores de alta resolução (Full HD, 2K ou ultrawide de 1440px a 2560px), desejo que os cabeçalhos das colunas da tabela de estudos estejam rigorosamente alinhados com suas respectivas células de conteúdo ao longo de toda a largura útil da tela.

**Why this priority**: Em monitores largos, pequenas discrepâncias de fração de grid ou padding entre a linha de cabeçalho (`.list-header-row`) e as linhas de dados (`.study-row-item`) causam efeito de desalinhamento visual desagradável e sensação de falta de polimento profissional.

**Independent Test**: Pode ser testado inspecionando a tabela de estudos em larguras de viewport de 1024px, 1440px, 1920px e 2560px, confirmando que as frações de grid de cabeçalho e dados são idênticas e as bordas das colunas coincidem milimetricamente.

**Acceptance Scenarios**:

1. **Given** uma tela com resolução de 1440px ou superior, **When** a lista de estudos é renderizada com cabeçalho e linhas de dados, **Then** a malha de `grid-template-columns` deve ser idêntica em `.list-header-row`, `.study-row-item` e `.skeleton-row`.
2. **Given** as colunas de "Seções" e "Ações" na tabela, **When** renderizadas em qualquer largura de tela suportada, **Then** seus conteúdos devem manter alinhamento estrito (`justify-content: center` e `align-items: center`) tanto no cabeçalho quanto no corpo da tabela.
3. **Given** a visualização em grade (`StudyGridView.vue`), **When** visualizada em resoluções largas e médias, **Then** o alinhamento dos cartões de estudos e seus badges de status deve manter espaçamento equilibrado e ausência de overflow horizontal indesejado.

---

### Edge Cases

- **Tabela com estudo único ou vazia**: Quando a tabela contiver apenas um único estudo, a abertura do dropdown de status não deve estourar a altura mínima da tabela nem provocar rolagem indesejada.
- **Redimensionamento da janela durante menu aberto**: Se o viewport for redimensionado enquanto o dropdown de status estiver aberto, o menu deve permanecer posicionado de forma coerente ou fechar de forma graciosa.
- **Títulos de estudos extremamente longos**: Textos longos na coluna de título não devem empurrar ou achatar as colunas de status, data, localização e ações.
- **Nomes de localização ausentes ou vazios**: Quando o estudo não possuir localização, a célula deve exibir um traço suave (`—`) sem quebrar a altura da linha ou desalinhar a grade.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE garantir que o menu suspenso de status (`.status-dropdown-menu`) sobreponha qualquer elemento pai, borda de tabela ou linhas adjacentes em `StudyListView.vue` sem sofrer corte (*clipping*), assegurando `overflow: visible` nos contêineres pertinentes e camada de sobreposição com `z-index: 1000` ou superior.
- **FR-002**: O sistema DEVE calcular dinamicamente ou posicionar de forma segura o dropdown de status quando ativado na última ou na primeira linha da tabela, evitando que o menu seja cortado pelos limites da viewport ou do contêiner da tabela (`opens-upward`).
- **FR-003**: O indicador SVG de ordenação (`.sort-indicator`) nos botões de cabeçalho (`.header-sort-btn`) DEVE herdar a cor do rótulo ativo por meio de `stroke: currentColor` e `fill: none` (e propriedades SVG correspondentes), garantindo contraste mínimo de 4.5:1 em todos os 10 temas canônicos.
- **FR-004**: As colunas do cabeçalho da tabela (`.list-header-row`), as células das linhas de dados (`.study-row-item`) e as linhas de carregamento (`.skeleton-row`) DEVEM compartilhar exatamente a mesma malha geométrica de grid CSS em todas as faixas de resolução (desde 1024px até 2560px).
- **FR-005**: Todos os elementos de cabeçalho e células de dados DEVEM manter alinhamento vertical estrito (`align-items: center`), com centralização uniforme nas colunas de seções analíticas e ações operacionais.
- **FR-006**: As visualizações `StudyListView.vue` e `StudyGridView.vue` DEVEM manter comportamento responsivo estável, sem gerar barras de rolagem horizontais involuntárias nem descompassos na disposição de cartões ou badges.

### Key Entities *(include if feature involves data)*

- **Estudo (StudySummary)**: Entidade representando o estudo listado, contendo identificador (`id`), título (`title`), localização (`location`), status de leitura (`reading_status`), data de modificação/criação (`updated_at`, `created_at`), marcadores de seções analíticas (`has_summary`, `has_explanation`, `has_concepts`, `has_references`) e métricas.
- **Configuração de Ordenação e Filtros (StudyListFilters)**: Estado de controle visual contendo a coluna ativa de ordenação (`sortColumn`), direção (`sortDirection`), termo de busca textual (`searchQuery`) e filtro de status ativo (`statusFilter`).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% dos acionamentos do menu de status em qualquer linha da tabela de estudos abrem o menu de opções flutuante sem nenhum corte nas bordas superior, inferior ou laterais da tabela.
- **SC-002**: O ícone SVG de ordenação exibe contraste igual ou superior a 4.5:1 em relação ao fundo do cabeçalho da tabela em todos os 10 temas oficiais do Leitorum.
- **SC-003**: A divergência de alinhamento entre as colunas do cabeçalho e as células de dados correspondentes da tabela é de exatamente 0px nas resoluções de 1024px, 1440px, 1920px e 2560px.
- **SC-004**: Abertura e fechamento do dropdown de status ocorrem sem atraso perceptível (< 50ms) e sem causar rolagem involuntária da página.
- **SC-005**: 100% dos testes automatizados de regressão e validação (`npm test`, `npm run build`, `pytest`) passam com sucesso.

## Assumptions

- O componente `StudyStatusBadge.vue` é o único responsável pela renderização interativa do menu suspenso de status de leitura tanto na lista quanto na grade.
- O tema ativo do sistema é gerenciado via atributo `data-theme` no elemento `:root`, permitindo que `currentColor` herde as propriedades de texto definidas pelas variáveis CSS semânticas.
- Não são necessárias alterações estruturais no backend, na API REST ou no banco de dados SQLite para o cumprimento desta especificação.
- As regras de layout flex/grid respeitam a área útil delimitada pelo shell responsivo e pela barra lateral.
