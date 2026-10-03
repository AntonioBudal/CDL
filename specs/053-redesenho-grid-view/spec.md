# Feature Specification: F 0.7.4 — Redesenho da Grid View: Reconhecimento Visual e Cartografia de Leitura

**Feature Branch**: `053-redesenho-grid-view`

**Created**: 2026-10-03

**Status**: Draft

**Input**: User description: "/speckit-specify F0.7.4" (F 0.7.4 — Redesenho da Grid View: Reconhecimento Visual e Cartografia de Leitura: redesenhar a visualização em grade para priorizar reconhecimento estético imediato, densidade analítica e percepção do estado dos estudos nos capítulos)

## Clarifications

### Session 2026-10-03
- Q: Como a identidade cromática do status de leitura deve ser aplicada ao cartão do estudo para rápida diferenciação visual? → A: Friso fino vertical no lado esquerdo do cartão (ou borda superior) acompanhado do badge textual discreto no cabeçalho.
- Q: De qual seção do estudo deve ser extraída a prévia tipográfica de 2 a 3 linhas nos cartões da grade? → A: Priorizar o campo `summary` (Resumo Analítico); caso esteja vazio, usar fallback automático para `explanation` (Explicação Principal).
- Q: Como o clique principal de navegação e a ação secundária de exclusão (lixeira) devem interagir ergonomicamente no cartão da grade? → A: Cartão inteiro é uma superfície de clique para abrir a leitura; botão de lixeira discreto no rodapé com `@click.stop` e diálogo de confirmação.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Identidade Editorial e Reconhecimento Cromático de Status (Priority: P1) 🎯 MVP

Como uma pessoa leitora que gerencia múltiplos estudos dentro de um capítulo ou livro, quero que a visualização em grade (Grid View) apresente cartões com identidade editorial marcante e clara diferenciação cromática do status de leitura, para que eu possa identificar instantaneamente o progresso da minha leitura sem precisar abrir cada estudo individualmente.

**Why this priority**: É a promessa central da Grid View: permitir o reconhecimento visual e a visão panorâmica do capítulo em uma fração de segundo.

**Independent Test**: Pode ser testado navegando para um capítulo com estudos em diferentes estados (*Rascunho*, *Em Andamento*, *Revisado*, *Concluído*): os cartões devem exibir faixas cromáticas distintas e tipografia hierárquica clara.

**Acceptance Scenarios**:

1. **Given** que o usuário está na Grid View de um capítulo, **When** os estudos são exibidos, **Then** cada cartão apresenta uma indicação cromática vinculada ao seu status de leitura (*Rascunho*: neutro/cinza, *Em Andamento*: âmbar quente, *Revisado*: azul sereno, *Concluído*: verde esmeralda).
2. **Given** que o usuário clica em qualquer área ativa do cartão de estudo, **When** a ação é disparada, **Then** o sistema transporta diretamente o usuário para a tela de leitura do estudo selecionado.
3. **Given** que o usuário deseja alterar rapidamente o status de um estudo, **When** ele clica no seletor de status do cartão, **Then** o menu de status permite a alteração sem sair da grade e o estilo cromático do cartão atualiza imediatamente.

---

### User Story 2 - Cartografia de Densidade Analítica e Prévia do Resumo (Priority: P2)

Como uma pessoa pesquisadora ou estudante, quero ver no cartão de cada estudo mini-indicadores de densidade (quantidade de destaques/anotações e conexões semânticas) e uma prévia elegante do resumo analítico, para que eu compreenda a profundidade e maturidade daquele estudo na minha cartografia de leitura.

**Why this priority**: Diferencia substancialmente a Grid View de uma simples lista de títulos, dando peso cognitivo e contexto a cada bloco de leitura.

**Independent Test**: Criar estudos com diferentes quantidades de destaques e relações: verificar que o cartão exibe mini-badges discretos com contagens e exibe 2 a 3 linhas balanceadas de prévia do resumo.

**Acceptance Scenarios**:

1. **Given** que um estudo possui destaques no texto ou conexões com outros estudos, **When** renderizado no grid, **Then** o rodapé do cartão exibe mini-indicadores discretos com ícone e número de destaques e relações registradas.
2. **Given** que o estudo contém uma síntese ou resumo analítico preenchido, **When** exibido no card, **Then** o sistema renderiza uma prévia tipográfica de 2 a 3 linhas estilizada com corte suave por reticências (*line-clamp*).
3. **Given** que um estudo não possui resumo preenchido, **When** renderizado, **Then** o cartão trata a ausência de forma graciosa sem deixar buracos visuais desproporcionais na grade.

---

### User Story 3 - Grid Responsivo, Estados de Carregamento e Ergonomia Mobile (Priority: P3)

Como uma pessoa usuária alternando entre telas largas de computador e smartphone, quero que a grade se adapte fluidamente entre 3, 2 e 1 colunas com telas de esqueleto (*Skeleton Screens*) durante o carregamento, para que a experiência seja suave, estável e livre de saltos de layout (*layout shifts*).

**Why this priority**: Garante consistência visual, acessibilidade tátil móvel (alvos mínimos de 44px) e sensação de performance refinada.

**Independent Test**: Redimensionar a janela de visualização de 1280px para 390px e simular tempo de resposta de dados: verificar transição suave de 3 colunas para 1 coluna e presença de skeletons idênticos à geometria dos cartões.

**Acceptance Scenarios**:

1. **Given** uma tela desktop larga (> 1024px), **When** a Grid View é aberta, **Then** os cartões organizam-se em 3 colunas equilibradas com espaçamento consistente e efeito sutil de elevação sensorial ao passar o mouse (*hover*).
2. **Given** uma tela intermediária (768px a 1023px), **When** visualizada, **Then** a grade adapta-se para 2 colunas.
3. **Given** uma tela de smartphone (< 768px), **When** visualizada, **Then** a grade exibe 1 coluna com cartões confortáveis e alvos de toque mínimos de 44×44px.
4. **Given** que a lista de estudos está sendo carregada da API, **When** a tela é inicializada, **Then** esqueletos animados (*Skeleton Screens*) com a exata silhueta dos cartões são exibidos até a chegada dos dados.

---

### Edge Cases

- **Estudo com título muito longo**: O título deve quebrar em até 2 linhas com elipse balanceada, sem deformar os cartões adjacentes da mesma linha da grade.
- **Estudo sem localização e sem resumo**: O cartão deve manter seu alinhamento vertical e proporções harmoniosas mesmo com campos textuais opcionais vazios.
- **Capítulo sem estudos cadastrados**: Apresentar estado vazio acolhedor (*EmptyState*) com chamada clara para importação ou criação de estudos.
- **Nenhum estudo no filtro ou agrupamento ativo**: Quando agrupado por status ou capítulo e uma seção estiver vazia, exibir indicação compacta ou colapso limpo.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE exibir os estudos em formato de grade responsiva com cartões estilizados de rica identidade editorial.
- **FR-002**: Cada cartão de estudo DEVE indicar visualmente seu status de leitura através de um friso fino vertical no lado esquerdo do cartão combinado ao badge textual discreto no cabeçalho.
- **FR-003**: O sistema DEVE permitir alteração direta do status de leitura através do badge interativo presente no cartão sem exigir navegação prévia.
- **FR-004**: O sistema DEVE exibir no cartão uma prévia tipográfica de 2 a 3 linhas com corte suave (*line-clamp*) baseada prioritariamente no campo `summary` (Resumo Analítico) e com fallback automático para `explanation` (Explicação Principal) quando o resumo estiver ausente.
- **FR-005**: O sistema DEVE exibir mini-indicadores de densidade no rodapé do cartão informando contagem de destaques/anotações e contagem de relações quando superiores a zero.
- **FR-006**: O sistema DEVE estruturar o cartão para que a área integral seja uma superfície interativa de clique que transporta imediatamente para a leitura do estudo, acomodando a ação de lixeira de forma isolada no rodapé com supressão de propagação (`@click.stop`) e diálogo de confirmação de exclusão.
- **FR-007**: O sistema DEVE exibir *Skeleton Screens* animados que reproduzam fielmente o layout e a geometria dos cartões da grade durante o estado de carregamento.
- **FR-008**: O sistema DEVE preservar a integração com o componente de agrupamento (`GroupBySelector` / `GroupSection`) persistindo a preferência de agrupamento no `localStorage`.
- **FR-009**: O layout da grade DEVE se adaptar dinamicamente: 3 colunas em desktop amplo (> 1024px), 2 colunas em tablet/médio (768px a 1023px) e 1 coluna em telas móveis (< 768px).
- **FR-010**: A interface DEVE garantir alvos táteis mínimos de 44×44px para botões interativos e suportar navegação sequencial por teclado (`Tab`, `Enter`).

---

### Key Entities

- **StudyCard**: Componente visual do cartão de estudo, encapsulando metadados de identificação (título, localização, data), cromatismo de status, prévia textual e contagens agregadas de densidade.
- **StudySummaryRead**: Modelo de dados agregados do estudo, contendo identificadores, metadados editoriais e contagens leves de destaques e relações.
- **ReadingStatusTone**: Paleta semântica canônica de status de leitura vinculada aos temas visuais (`rascunho`, `em_andamento`, `revisado`, `concluido`).

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: O leitor consegue discernir visualmente o status e a densidade de qualquer estudo em menos de 1 segundo de inspeção visual da grade.
- **SC-002**: 100% dos cliques no corpo do cartão abrem a tela de leitura imediatamente sem cliques intermediários.
- **SC-003**: A grade se ajusta responsivamente entre 1, 2 e 3 colunas sem sobreposições de texto, quebras de proporção ou rolagem horizontal acidental.
- **SC-004**: Zero redundância visual com a List View, estabelecendo a Grid View como a cartografia visual de excelência do capítulo.
- **SC-005**: 100% de conformidade com os princípios da Constituição (isolamento do acervo, testes em bancos efêmeros, sem perda de dados).

---

## Assumptions

- Os estudos retornados pela API do capítulo podem conter contagens leves calculadas em lote ou agregadas no backend sem degradação de performance.
- O componente `StudyStatusBadge.vue` existente continua sendo a referência canônica para os rótulos e transições de status.
- A exclusão via lixeira permanece sendo um soft-delete com diálogo de confirmação.
- A Grid View é a visualização padrão inicial quando o usuário abre um capítulo, a menos que uma preferência diferente tenha sido salva.
