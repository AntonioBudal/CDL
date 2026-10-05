# Feature Specification: F0.7.11 — Biblioteca Transversal de Highlights e Anotações

**Feature Branch**: `060-biblioteca-highlights-anotacoes`

**Created**: 2026-10-05

**Status**: Ready for Planning

**Input**: User description: "F7.0.11"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Exploração Transversal e Busca Textual Instantânea (Priority: P1)

Como leitor com dezenas de livros e estudos anotados, desejo acessar uma tela centralizada que liste todas as minhas marcações e notas de leitura em um único lugar, podendo pesquisar rapidamente por palavras-chave tanto no trecho destacado quanto nos meus comentários pessoais, para que eu possa recuperar insights sem precisar adivinhar em qual capítulo ou estudo específico a marcação foi feita.

**Why this priority**: É o valor central da feature e resolve a dor primária do usuário: a fragmentação das anotações em silos isolados dentro de cada estudo individual.

**Independent Test**: Pode ser testado navegando até a tela `/highlights`, visualizando a lista de cards de destaques do usuário autenticado e digitando termos no campo de busca com retorno instantâneo (debounce de 250ms), exibindo apenas os trechos que contêm o termo procurado.

**Acceptance Scenarios**:

1. **Given** que o usuário possui destaques e anotações distribuídos em diferentes livros e capítulos, **When** ele acessa a tela de Biblioteca de Destaques (`/highlights`), **Then** o sistema exibe os cartões com o texto marcado, anotação pessoal associada, identificação visual do tipo/cor e nome do livro/capítulo de origem, ordenados inicialmente em modo feed cronológico reverso ("Recentes", mais recentes primeiro) com opção de alternar para agrupamento hierárquico "Por Obra" (Livro > Capítulo).
2. **Given** a biblioteca aberta, **When** o usuário alterna entre os modos de visualização "Recentes" e "Por Obra", **Then** a apresentação se reorganiza imediatamente e a preferência é memorizada na URL (`view_mode`) e no armazenamento local (`localStorage`).
3. **Given** a lista de destaques carregada, **When** o usuário digita um termo no campo de busca rápida, **Then** a listagem filtra em tempo real (sem recarregar a página) os itens que contêm o termo no texto selecionado ou na anotação pessoal, exibindo estado vazio acolhedor caso nenhum item coincida.
4. **Given** um usuário que ainda não possui marcações cadastradas, **When** ele acessa a tela `/highlights`, **Then** o sistema exibe uma mensagem acolhedora orientando sobre como selecionar trechos e criar marcações durante a leitura.

---

### User Story 2 - Filtragem Multidimensional e Sincronização na URL (Priority: P2)

Como leitor organizando uma pesquisa temática, desejo filtrar meus destaques por obra/livro, por tipo (destaque simples, nota de margem, citação formatada, oclusão/cloze, pergunta de estudo) e por cor cromática (amarelo, verde, azul, rosa, lilás), com os filtros refletidos na URL, para que eu possa isolar recortes analíticos precisos e retomar a mesma visão por meio do histórico do navegador ou favoritos.

**Why this priority**: Permite que o usuário refine centenas de marcações em conjuntos de alta relevância (ex.: "todas as perguntas em amarelo do Livro X").

**Independent Test**: Pode ser testado selecionando combinações de filtros de livro, tipo e cor na barra superior e verificando que a listagem é restrita aos critérios selecionados e que a barra de endereços é atualizada com os query params correspondentes (`?book=...&kind=...&color=...`).

**Acceptance Scenarios**:

1. **Given** a biblioteca aberta, **When** o usuário seleciona um livro específico no seletor de obras, **Then** o filtro de capítulos é contextualizado para aquele livro e a listagem exibe somente destaques da obra escolhida.
2. **Given** a seleção de um tipo específico (ex.: "Perguntas" ou "Citações") ou de uma cor (ex.: "Verde"), **When** o filtro é aplicado, **Then** apenas os cards correspondentes àquele tipo/cor permanecem visíveis.
3. **Given** múltiplos filtros ativos na interface, **When** o usuário recarrega a página ou navega pelo botão voltar/avançar do navegador, **Then** o estado dos filtros é restaurado integralmente a partir dos parâmetros de URL.
4. **Given** filtros aplicados que não retornam resultados, **When** o leitor clica no botão "Limpar filtros", **Then** todos os parâmetros são restaurados para o padrão e a listagem completa é reapresentada.

---

### User Story 3 - Salto Contextual com Retorno ao Estudo e Gestão Rápida In-Card (Priority: P3)

Como leitor revisando uma anotação na biblioteca, desejo saltar diretamente para a posição exata daquela marcação no texto completo do estudo de origem com destaque visual sutil e poder editar ou excluir anotações diretamente no próprio cartão da biblioteca, para que eu mantenha agilidade na curadoria e restabeleça facilmente o contexto reflexivo da passagem original.

**Why this priority**: Fecha o ciclo de navegação bidirecional entre a biblioteca transversal agregada e a leitura imersiva contextual, além de evitar atrito em manutenções rápidas.

**Independent Test**: Pode ser testado:
  1. Clicando no botão "Abrir no Estudo" em qualquer cartão de destaque e confirmando que o navegador navega para o estudo correto, rola suavemente até o elemento `#highlight-{id}` e ativa um pulso luminoso (glow de 2s).
  2. Editando a nota ou excluindo o destaque diretamente a partir das ações do cartão na biblioteca e confirmando a persistência imediata.

**Acceptance Scenarios**:

1. **Given** um cartão de destaque exibido na biblioteca, **When** o usuário clica em "Abrir no Estudo", **Then** a aplicação navega na mesma aba para o estudo com a âncora `#highlight-{id}`, rola suavemente até o trecho e aplica um pulso luminoso temporário de 2 segundos para direcionar a atenção do leitor.
2. **Given** um cartão de destaque com anotação, **When** o usuário clica na ação de editar anotação no próprio card, **Then** o campo de nota se transforma em área de edição rápida com botões Salvar e Cancelar, persistindo a alteração no backend sem recarregar a tela.
3. **Given** um cartão de destaque, **When** o leitor aciona a ação de excluir no card e confirma a ação, **Then** o destaque é removido do backend e removido da listagem da biblioteca com transição suave.
4. **Given** um destaque pertencente a um estudo que foi enviado para a lixeira ou excluído, **When** a biblioteca de destaques é carregada, **Then** esse destaque não é exibido na listagem ativa.

---

### Edge Cases

- **Estudos excluídos ou na lixeira**: O sistema deve filtrar rigorosamente marcações cujos estudos pai estejam marcados como deletados (`deleted_at IS NOT NULL` / lixeira ativa), mantendo a integridade referencial.
- **Marcações com textos extensos**: Cards que contenham trechos selecionados muito longos devem apresentar truncamento visual harmonioso com expansão sob demanda ("Ver mais"), evitando deformação do layout em grade ou coluna.
- **Volume massivo de marcações**: Para leitores com milhares de marcações, o carregamento deve ser paginado (limit/offset indexado eficiente com botões de página ou carregamento contínuo sob demanda), prevenindo travamento de renderização e garantindo resposta ágil.
- **Caracteres especiais e diacríticos na busca**: A pesquisa textual deve normalizar acentuação e ignorar diferenças de caixa alta/baixa tanto no backend SQLite (`LOWER` com compatibilidade UTF-8) quanto na filtragem reativa no frontend.
- **Acessibilidade em telas móveis**: Em dispositivos móveis (telas $\le 768$px), a barra de filtros deve colapsar de forma ergonômica em gaveta expansível e os alvos de toque em botões e seletores devem cumprir o padrão mínimo de $44 \times 44$px.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE disponibilizar uma rota e visão dedicada para a Biblioteca Transversal de Destaques (`/highlights`).
- **FR-002**: O sistema DEVE fornecer um ponto de entrada/navegação no menu principal ou cabeçalho da aplicação para acesso rápido à Biblioteca de Destaques.
- **FR-003**: A biblioteca DEVE listar exclusivamente as marcações pertencentes ao usuário autenticado atual, preservando o isolamento multiusuário.
- **FR-004**: O sistema DEVE permitir a busca textual instantânea sobre o texto selecionado (`selected_text`) e o comentário/anotação pessoal (`note`), com resposta otimizada e debounce de 250ms.
- **FR-005**: O sistema DEVE permitir filtragem simultânea por Obra/Livro (`book_id`), Capítulo (`chapter_id`), Tipo de Marcação (`kind`: destaque, anotação, citação, oclusão/cloze, pergunta) e Cor (`color`).
- **FR-006**: O sistema DEVE sincronizar os filtros ativos, termo de busca e modo de visualização nos parâmetros de consulta da URL (`?book=...&kind=...&color=...&q=...&view_mode=...`) para compartilhamento de link interno e histórico do navegador.
- **FR-007**: Cada cartão de destaque DEVE exibir com clareza o trecho selecionado, o comentário associado (se houver), o tipo de destaque, a cor semântica, o título do livro e o título do capítulo.
- **FR-008**: O sistema DEVE disponibilizar seletor de modo de visualização permitindo alternar entre o modo cronológico ("Recentes") e o modo agrupado ("Por Obra"), com o padrão inicial sendo "Recentes" e preferência persistida em `localStorage`.
- **FR-009**: O cartão de destaque DEVE disponibilizar ação direta "Abrir no Estudo", navegando na mesma aba para o estudo com âncora `#highlight-{id}`, efetuando rolagem suave e exibindo um pulso luminoso temporário de 2 segundos no trecho correspondente.
- **FR-010**: O cartão de destaque DEVE permitir edição rápida da nota pessoal e exclusão com diálogo de confirmação in-place diretamente na biblioteca, refletindo imediatamente na lista.
- **FR-011**: O backend DEVE fornecer endpoint consolidado e paginado (`GET /api/highlights/library`) com suporte a busca textual, filtros e junção com livro e capítulo.
- **FR-012**: A interface DEVE exibir estados visuais de carregamento (esqueletos/skeletons animados) e estado vazio acolhedor sem emojis residuais.

### Key Entities *(include if feature involves data)*

- **HighlightItem**: Representa o destaque retornado para a biblioteca, contendo `id`, `study_id`, `book_id`, `chapter_id`, `book_title`, `chapter_title`, `study_title`, `selected_text`, `note`, `color`, `kind`, `created_at` e `updated_at`.
- **HighlightFilterQuery**: Conjunto de parâmetros de consulta contendo termo de busca (`q`), identificador do livro (`book_id`), identificador do capítulo (`chapter_id`), tipo (`kind`), cor (`color`), modo de visão (`view_mode`), ordenação (`sort_by`, `order`) e paginação (`page`, `per_page`).
- **BookFilterOption / ChapterFilterOption**: Pares chave-valor para alimentação dos menus de seleção contextual de obras e capítulos.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: O leitor consegue localizar qualquer destaque ou anotação de seu acervo em menos de 3 segundos utilizando a busca textual ou os filtros de livro/cor/tipo.
- **SC-002**: A busca textual instantânea responde visualmente na interface em menos de 300ms a partir do término da digitação (debounce de 250ms).
- **SC-003**: 100% dos saltos de navegação a partir do botão "Abrir no Estudo" conduzem o leitor diretamente ao estudo e à posição da marcação correta com pulso luminoso de 2 segundos.
- **SC-004**: A tela e os componentes atendem plenamente às diretrizes de ergonomia móvel com alvos táteis mínimos de $44 \times 44$px e ausência de emojis informais no código de produção.

## Assumptions

- O banco de dados já possui a tabela `study_highlights` populada com as colunas de `selected_text`, `note`, `color`, `kind` e chaves estrangeiras apropriadas para os estudos.
- A biblioteca opera estritamente no âmbito dos dados do usuário logado (respeitando o isolamento multiusuário da versão 0.5+).
- A navegação utiliza o Vue Router nativo com transições suaves e preservação de histórico.
- Os estilos visuais seguem o Design System unificado (tokens CSS, superclasses e temas canônicos) da aplicação.
