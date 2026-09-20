# Feature Specification: F06 — Painéis Redimensionáveis

**Feature Branch**: `018-paineis-redimensionaveis`

**Created**: 2026-09-19

**Status**: Draft

**Input**: User description: "F06 Painéis Redimensionáveis"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Redimensionamento e Colapso de Painéis no Desktop com Persistência (Priority: P1) 🎯 MVP

O leitor em ambiente de mesa (computador/laptop com largura de tela a partir de 1024px) organiza seu espaço de estudo ajustando a largura das colunas de trabalho. A tela é estruturada em três áreas complementares: Navegador de Capítulos e Estudos (à esquerda), Palco Principal de Leitura/Visualização (ao centro) e Inspetor de Metadados e Contexto (à direita). Entre os painéis, uma barra divisora sutil permite arrasto contínuo com o ponteiro do mouse ou trackpad. O leitor pode colapsar qualquer painel lateral com um clique para focar integralmente na leitura, e dar duplo clique no divisor para restaurar a largura padrão recomendada. As dimensões personalizadas e o estado de colapso são preservados automaticamente para as próximas sessões.

**Why this priority**: É o núcleo de valor da feature. Elimina a rigidez do layout fixo, permite que monitores amplos sejam aproveitados e concede autonomia ergonômica total ao leitor durante seus estudos.

**Independent Test**: Em resolução desktop, abrir a visão de um livro, arrastar a barra divisora esquerda para alargar o navegador, colapsar o painel direito pelo botão de alternância rápida, recarregar a página e constatar que o navegador mantém a largura customizada e o painel direito permanece colapsado.

**Acceptance Scenarios**:

1. **Given** o leitor visualizando um livro em desktop, **When** clica e arrasta a barra divisora entre a navegação e o palco central para a direita, **Then** a largura da coluna de navegação aumenta em tempo real enquanto o palco central absorve a diferença, sem provocar seleção indesejada de texto ou quebra de elementos.
2. **Given** uma coluna lateral redimensionada, **When** o leitor dá um duplo clique sobre a barra divisora correspondente, **Then** a largura da coluna retorna instantaneamente ao valor padrão de fábrica.
3. **Given** qualquer um dos painéis laterais visíveis, **When** o usuário aciona o botão de colapso rápido na barra divisora ou no cabeçalho do painel, **Then** o painel se recolhe com transição visual suave, expandindo o palco principal para preencher o espaço restante.
4. **Given** um painel lateral colapsado, **When** o leitor aciona o botão de expansão, **Then** o painel reabre com a última largura personalizada memorizada.
5. **Given** dimensões personalizadas pelo leitor, **When** o leitor atualiza a página ou reinicia o navegador, **Then** as larguras e estados (aberto/colapsado) são restaurados com fidelidade segundo o modelo híbrido (larguras padrão globais do acervo herdadas inicialmente, preservando ajustes específicos por livro caso o leitor os customize naquela obra).

---

### User Story 2 - Acessibilidade e Ajuste Ergonômico por Teclado (Priority: P2)

O leitor que utiliza navegação por teclado ou tecnologia assistiva navega até as barras divisoras e controla as proporções da tela sem necessidade de mouse. As divisórias comportam-se como controles semânticos de separação, informando aos leitores de tela a orientação, a largura atual e os limites aceitáveis. Ao receber foco, as teclas direcionais (setas Esquerda e Direita) aumentam ou diminuem a largura do painel em passos discretos e estáveis.

**Why this priority**: Garante conformidade com as diretrizes de acessibilidade universal (WCAG e Constituição do projeto), permitindo que todos os usuários configurem seu espaço de leitura sem barreiras de motricidade.

**Independent Test**: Navegar exclusivamente pela tecla Tab até a divisória de painéis, observar o foco visível e acionar a tecla Seta Direita três vezes, confirmando que o painel expande em passos regulares com anúncio sonoro do novo valor.

**Acceptance Scenarios**:

1. **Given** o foco de navegação por teclado sobre a barra divisora, **When** o leitor pressiona a tecla Seta Esquerda ou Seta Direita, **Then** a coluna associada diminui ou aumenta em passos discretos de 10 pixels, respeitando os limites mínimo e máximo.
2. **Given** a barra divisora focada, **When** inspecionada por tecnologia assistiva, **Then** expõe o papel semântico de separador (`role="separator"`), com valores dinâmicos de percentual/largura atual, valor mínimo e valor máximo permitidos.
3. **Given** o leitor navegando por teclado, **When** atinge os botões de alternância rápida de colapso via Tab ou foca as barras divisoras (`role="separator"`), **Then** aciona o colapso/expansão via tecla Enter/Espaço e redimensiona em passos de 10px via setas direcionais, sem interceptação de atalhos globais de teclado para preservar a digitação limpa de notas e markdown.

---

### User Story 3 - Adaptação Responsiva e Gavetas Deslizantes em Tablets e Celulares (Priority: P3)

Em dispositivos com telas compactas (smartphones) ou intermediárias (tablets em modo retrato), a interface transmuta sua arquitetura espacial para priorizar o conforto de leitura. Em tablets, o painel direito inicia recolhido e abre-se como uma gaveta lateral sobreposta suave quando acionado. Em smartphones (larguras inferiores a 768px), o mecanismo de colunas redimensionáveis é substituído por gavetas deslizantes completas (*bottom sheets* ou gavetas laterais de tela cheia), acionadas por botões de fácil alcance tátil com área de toque mínima de 44x44px.

**Why this priority**: Evita layouts degradados ou espremidos em dispositivos móveis, permitindo leitura confortável no celular enquanto preserva acesso rápido à navegação e ao contexto.

**Independent Test**: Reduzir a viewport para largura mobile (390px), abrir a tela do livro e confirmar que apenas o palco principal é exibido, com botões para abrir a navegação e o contexto como gavetas modais táteis com fechamento por arrasto ou clique externo.

**Acceptance Scenarios**:

1. **Given** a primeira abertura de um livro em desktop (>= 1024px) ou tablet (768px a 1023px), **When** a página é carregada, **Then** o painel de navegação esquerdo é exibido e o painel de contexto direito inicia recolhido por padrão, garantindo foco direto na leitura do palco central sem distrações.
2. **Given** visualização em smartphone (< 768px), **When** a interface é renderizada, **Then** os divisores de arrasto são suprimidos e a navegação/inspetor tornam-se gavetas acionadas por botões dedicados de toque.
3. **Given** uma gaveta móvel aberta, **When** o usuário toca fora da gaveta ou pressiona o botão de fechar, **Then** a gaveta se recolhe suavemente devolvendo o foco ao elemento acionador.

---

### Edge Cases

- O que acontece quando o usuário arrasta a divisória além da largura total da janela? O sistema trava o arrasto no limite máximo estrito do painel (ex.: 600px ou 45% da largura da janela), garantindo que o palco central nunca fique com largura inferior a 360px.
- O que acontece se o usuário arrastar a divisória para menos do limite mínimo (ex.: 240px)? O painel é mantido no tamanho mínimo e, caso o usuário arraste intencionalmente até próximo de zero (menos de 60px), o painel entra automaticamente em estado colapsado (*snap to collapse*).
- O que acontece durante o arrasto rápido se o cursor passar sobre links, imagens ou textos? O sistema desativa temporariamente a seleção de texto e captura o ponteiro (`setPointerCapture`), evitando seleções azuis acidentais ou perda do foco do cursor.
- O que acontece se a tela for redimensionada enquanto o painel está aberto? O layout recalcula as porcentagens de forma fluida sem transbordamento horizontal de página.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE fornecer um layout flexível de 3 áreas de trabalho articuladas: Navegador (esquerda), Palco Principal (centro) e Inspetor de Contexto (direita).
- **FR-002**: O sistema DEVE disponibilizar barras divisoras interativas (*gutters*) entre os painéis adjacentes, sensíveis a eventos de ponteiro (mouse, trackpad e toque).
- **FR-003**: Os painéis laterais DEVEM respeitar limites rígidos de largura mínima (240px) e largura máxima (600px ou 40% da tela), impedindo proporções inviáveis de leitura.
- **FR-004**: O palco principal DEVE ter garantia de largura útil mínima (não inferior a 360px), prevalecendo sobre os painéis laterais em qualquer redimensionamento.
- **FR-005**: As barras divisoras DEVEM fornecer botões de alternância rápida de um clique para colapsar e restaurar o painel correspondente.
- **FR-006**: O acionamento de duplo clique sobre qualquer barra divisora DEVE redefinir a largura do painel para a dimensão padrão de fábrica (300px).
- **FR-007**: O sistema DEVE persistir a largura personalizada e o estado (aberto/colapsado) de cada painel em armazenamento local do navegador (`localStorage`) em modelo híbrido: largura padrão global do acervo com sobrescrita específica opcional por livro.
- **FR-008**: O sistema DEVE implementar atributos de acessibilidade WAI-ARIA nas barras divisoras (`role="separator"`, `aria-orientation="vertical"`, `aria-valuenow`, `aria-valuemin`, `aria-valuemax`).
- **FR-009**: As barras divisoras DEVEM responder a navegação por teclado via setas direcionais com passos regulares de 10px quando em foco.
- **FR-010**: O painel direito de contexto DEVE iniciar recolhido por padrão na primeira visita a um livro tanto no desktop (>= 1024px) quanto no tablet (768px a 1023px), assegurando foco imediato na leitura contínua do palco central.
- **FR-011**: O sistema DEVE detectar resoluções mobile (< 768px) e converter os painéis laterais em gavetas deslizantes completas com área de toque ergonômica mínima de 44x44px.
- **FR-012**: Durante o arrasto de divisores, o sistema DEVE neutralizar a seleção de texto do documento para evitar interferências visuais.
- **FR-013**: O sistema NÃO DEVE interceptar atalhos globais de teclado arbitrários para alternar painéis laterais, assegurando que o controle seja realizado pelo foco nativo em botões e divisores (`role="separator"`).

### Key Entities

- **SplitLayoutConfig**: Define as preferências gerais de posicionamento, incluindo estado colapsado dos painéis esquerdo e direito e modo de renderização ativo (colunas versus gavetas).
- **PaneDimensionState**: Registra a largura em pixels, o percentual correspondente, os limites mínimo/máximo aplicáveis e o valor padrão de fábrica de cada painel.
- **GutterInteractionState**: Representa o estado transitório do divisor durante o arrasto (ativo, posição inicial do ponteiro, delta acumulado e travamento de seleção de texto).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: O leitor consegue redimensionar qualquer painel lateral em menos de 2 segundos com resposta fluida a 60 frames por segundo, sem travamentos de rolagem ou arrasto.
- **SC-002**: 100% das preferências de largura e estado de colapso configuradas pelo usuário persistem íntegras entre recarregamentos de página e fechamento do navegador.
- **SC-003**: A transição para resolução móvel (< 768px) ocorre sem surgimento de barra de rolagem horizontal indesejada e sem sobreposição de textos.
- **SC-004**: Usuários que navegam exclusivamente por teclado conseguem redimensionar, colapsar e expandir os painéis sem necessitar de qualquer ação com o mouse.
- **SC-005**: A área de leitura do palco central nunca é reduzida a menos de 360px de largura útil, preservando a legibilidade dos textos sob qualquer configuração extrema de redimensionamento.

## Assumptions

- O armazenamento em `localStorage` do navegador do usuário está habilitado e possui espaço disponível para pequenas chaves de configuração geométrica de interface.
- Dispositivos móveis com largura menor que 768px priorizam o consumo sequencial e focado da leitura, tornando gavetas deslizantes preferíveis a colunas laterais permanentes.
- Nenhuma alteração no banco de dados SQLite ou em endpoints do backend FastAPI é requerida para esta funcionalidade (trata-se de uma capacidade estritamente de layout e apresentação no cliente).
- As transições animadas e estilos respeitam o tema ativo (Claro, Escuro, Sépia, E-Ink) e as diretrizes de movimento reduzido (`prefers-reduced-motion: reduce`).
