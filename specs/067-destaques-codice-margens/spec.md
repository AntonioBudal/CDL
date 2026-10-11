# Feature Specification: F0.8.02 — Destaques: Códice e Margens Vivas

**Feature Branch**: `067-destaques-codice-margens`

**Created**: 2026-10-11

**Status**: Ready for Planning

**Input**: User description: "Feature 02: Destaques — Códice e Margens Vivas (Roadmap 0.8 — Redesign Estrutural e Arquitetura Visual)"

---

## 1. Visão Geral e Contexto Editorial

A página de Destaques e Anotações (`/destaques`) é o coração do estudo ativo no Leitorum, funcionando como o *commonplace book* (caderno de lugares-comuns e citações) do leitor. Atualmente, a tela assemelha-se a uma listagem transacional genérica com filtros em facetas dispersos, marcadores de cor circulares desconectados de significado intelectual e banners de erro retangulares vermelhos que quebram a imersão e violam os temas visuais.

Esta especificação transforma a biblioteca de destaques em uma experiência tátil, serena e profundamente legível, inspirada em fichas literárias de estudo:
1. **Fichas Literárias (*Commonplace Index Cards*):** Cartões com tipografia humanista/serifada destacada para o trecho citado, aspas editoriais e distinção visual nítida entre a voz do autor da obra e as notas reflexivas do leitor.
2. **Categorias Semânticas de Grifo:** As cores dos marcadores deixam de ser meras bolinhas cromáticas e passam a representar intenções de estudo cognitivas (Ideia Central, Dúvida, Citação-chave, Refutação).
3. **Ergonomia e Ferramental de Citação:** Ação de cópia contextual com 1 clique em formatos padronizados (ABNT e Markdown) com feedback visual imediato.
4. **Estados de Erro e Vazio Acolhedores:** Substituição definitiva de caixas de erro vermelhas genéricas por estados de erro e busca vazia totalmente integrados à paleta semântica do tema ativo com ação de reintento acessível.

---

## 2. User Scenarios & Testing *(mandatory)*

### User Story 1 - Fichas Literárias com Tipografia Editorial Diferenciada (Priority: P1) [MVP]

O leitor acessa `/destaques` para consultar suas passagens grifadas e encontra cartões estruturados como fichas literárias elegantes:
1. **Trecho Citado em Destaque:** O texto grifado da obra recebe tipografia serifada de alta legibilidade, aspas editoriais discretas e realce tonal sutil correspondente à categoria do grifo.
2. **Separação entre Voz da Obra e Voz do Leitor:** Caso o leitor tenha adicionado uma anotação reflexiva ou comentário pessoal ao destaque, esta aparece em um bloco subordinado estilizado, claramente distinguível da citação original.
3. **Rodapé Metadados da Ficha:** Exibe de forma limpa a obra de origem, o capítulo e a página ou localização textual da marcação, servindo como referência bibliográfica imediata.

**Why this priority**: Constrói o núcleo da experiência de *commonplace book*, transformando uma lista de dados fria em um caderno vivo de citações legíveis e prazerosas de revisitar.

**Independent Test**: Navegar até `/destaques`, visualizar os cartões de citação com contraste tipográfico claro entre o trecho original do livro e anotações pessoais, confirmando metadados de obra, capítulo e data legíveis.

**Acceptance Scenarios**:
1. **Given** um destaque com texto e anotação pessoal associada, **When** renderizado na página de destaques, **Then** a citação é apresentada em tipografia editorial proeminente e a anotação pessoal surge em bloco complementar diferenciado.
2. **Given** um destaque sem anotações, **When** exibido no acervo, **Then** o cartão apresenta apenas a citação e seus metadados de localização sem espaços em branco desnecessários.
3. **Given** qualquer cartão de destaque, **When** o usuário examina o rodapé, **Then** constam o título do livro, capítulo associado e indicação temporal da criação do grifo.

---

### User Story 2 - Barra Unificada de Filtros e Categorias Semânticas de Grifo (Priority: P1) [MVP]

O leitor precisa localizar passagens específicas no seu acervo através de uma barra de filtros fluida e sem atritos:
1. **Categorias Semânticas de Cor:** Os seletores de cor são enriquecidos com significados intelectuais (ex.: Amarelo = Ideia Central, Verde = Citação-chave, Azul = Dúvida, Rosa = Refutação, Roxo = Síntese), permitindo filtrar por intenção cognitiva com rótulos acessíveis.
2. **Filtro Unificado de Busca e Tipos:** Campo de busca rápida textual integrado com filtros de tipo de marcação (Destaques puros, Anotações, Citações, Perguntas e Termos ocultos) e seletor por Obra.
3. **Alternância entre Modos de Agrupamento:** Suporte a visualização cronológica contínua ("Recentes") e visualização agrupada por livro ("Por Obra"), preservando a contagem de itens em cada grupo.

**Why this priority**: Permite que o leitor filtre rapidamente centenas de passagens sem perder a orientação espacial e cognitiva da sua pesquisa.

**Independent Test**: Aplicar filtros de categoria semântica combinados com busca textual e alternar entre visualização recente e por obra, validando a atualização dinâmica dos resultados e a preservação do estado na URL.

**Acceptance Scenarios**:
1. **Given** a barra de filtros carregada, **When** o usuário passa o mouse ou navega via teclado sobre os seletores de grifo, **Then** cada opção expressa textualmente sua categoria semântica e intenção de estudo.
2. **Given** o filtro de categoria semântica ativado, **When** combinado com busca textual, **Then** apenas os destaques que cumprem ambos os critérios são listados.
3. **Given** a alternância para o modo "Por Obra", **When** o conteúdo é reordenado, **Then** as fichas surgem agrupadas sob cabeçalhos editoriais dedicados para cada livro com contagem de passagens.

---

### User Story 3 - Cópia Contextual de Citação em Múltiplos Formatos com Microfeedback (Priority: P2)

O leitor está redigindo um ensaio, resenha ou estudo em outro aplicativo e deseja exportar uma citação rapidamente:
1. **Ação de Cópia Contextual:** Ao passar o mouse sobre o cartão (ou via botão acessível de ação rápida), surge a opção de copiar a citação.
2. **Múltiplos Formatos de Exportação:** Opção de cópia direta em formato de citação acadêmica/ABNT (com menção à obra e localização) ou formato Markdown (bloco de citação formatado `> ...` com referência).
3. **Feedback Tátil Imediato:** Ao clicar na cópia, o botão exibe um indicador sutil de confirmação (ícone de confirmação com animação suave) e uma notificação flutuante temporária informa "Copiado para a área de transferência" durante 1500ms, desaparecendo sem exigir clique de dispensa.

**Why this priority**: Acelera a ponte entre a biblioteca de estudos e a produção textual ativa do leitor em ferramentas externas sem atritos.

**Independent Test**: Clicar na ação de cópia de um cartão, validar que o texto copiado para a área de transferência inclui a citação formatada com a referência da obra, e verificar a exibição da mensagem de confirmação por 1,5 segundo.

**Acceptance Scenarios**:
1. **Given** um cartão de destaque visível, **When** o usuário aciona a cópia rápida, **Then** o texto da citação e sua referência são enviados para a área de transferência.
2. **Given** a ação de cópia executada com sucesso, **When** o feedback é disparado, **Then** uma mensagem flutuante discreta surge informando o sucesso e se dissolve automaticamente após 1500ms.
3. **Given** o usuário navegando via teclado, **When** foca a ação de cópia, **Then** a ação é disparável via tecla `Enter` ou `Espaço` com anúncio acessível para leitores de tela.

---

### User Story 4 - Expansão Suave de Contexto da Passagem e Edição Ágil (Priority: P2)

Para trechos longos ou citações cujos parágrafos ao redor enriquecem a compreensão:
1. **Visualização Compacta com Expansão de Trecho:** Citações extensas possuem truncamento elegante de leitura, com gatilho claro de "Ver mais" / "Expandir contexto" que anima a abertura em altura de forma suave sem saltos de layout (*layout shifts*).
2. **Edição Rápida da Anotação:** Possibilidade de ajustar ou enriquecer a nota pessoal diretamente na ficha sem abrir modais intrusivos ou navegar para outra tela.
3. **Confirmação Defensiva de Exclusão:** Opção de remoção de destaque com pedido de confirmação integrado e claro, prevenindo exclusões acidentais.

**Why this priority**: Mantém a densidade visual da lista sob controle ao mesmo tempo em que oferece profundidade de leitura e manutenção ágil in-card.

**Independent Test**: Localizar um destaque com texto longo, expandir o trecho e validar a animação suave; editar a anotação pessoal in-card e confirmar que o novo conteúdo é salvo e refletido instantaneamente.

**Acceptance Scenarios**:
1. **Given** uma citação com mais de 260 caracteres, **When** exibida inicialmente, **Then** apresenta truncamento defensivo com botão "Expandir contexto".
2. **Given** o clique em "Expandir contexto", **When** a ficha se expande, **Then** a transição de abertura é suave ($\le 180$ms) e revela o texto na íntegra.
3. **Given** a edição de uma anotação iniciada, **When** o usuário salva o texto editado, **Then** o cartão atualiza a nota pessoal imediatamente sem recarregar a tela.

---

### User Story 5 - Estados de Erro e Vazio Acolhedores e Integrados aos Temas (Priority: P3)

Quando ocorre uma oscilação na requisição ou quando não há destaques cadastrados:
1. **Eliminação do Banner Vermelho Genérico:** A mensagem de falha deixa de ser uma caixa retangular vermelha arbitrária, passando a usar um cartão acolhedor estilizado com os tokens do tema visual ativo.
2. **Ação Clara de Reintento (*Retry*):** O estado de erro oferece uma mensagem explicativa humanizada acompanhada de botão com foco nítido para "Tentar novamente".
3. **Estado Vazio Convidativo:** Quando não há resultados para a busca ou quando o acervo de destaques ainda está vazio, a tela exibe uma ilustração suave integrada ao tema e orientações práticas de como criar destaques na leitura ativa.

**Why this priority**: Preserva a harmonia visual em todos os 10 temas do sistema e previne frustração do usuário em cenários de falha de rede ou início de uso.

**Independent Test**: Simular falha de rede ao carregar a página de destaques, verificar que a interface renderiza o componente de erro respeitando as cores do tema ativo (sem tons vermelhos desconexos de caixas estáticas) e acionar "Tentar novamente" com sucesso.

**Acceptance Scenarios**:
1. **Given** uma falha ao consultar os destaques, **When** a mensagem de erro é exibida, **Then** ela utiliza exclusivamente as variáveis semânticas do tema ativo e fornece o botão "Tentar novamente".
2. **Given** o clique no botão "Tentar novamente", **When** acionado, **Then** a consulta é reexecutada exibindo o estado de carregamento preliminar.
3. **Given** uma busca que não retorna nenhuma passagem, **When** renderizado o estado vazio, **Then** uma mensagem amigável sugere limpar os filtros ou tentar outros termos de pesquisa.

---

### Edge Cases

- **Citações com formatação especial ou quebras de linha múltiplas:** A tipografia editorial deve preservar parágrafos e pontuação sem overflow horizontal nem deformação das margens da ficha.
- **Passagens muito curtas (apenas 1 ou 2 palavras):** O cartão deve manter proporções mínimas elegantes sem parecer desbalanceado ou esticado artificialmente.
- **Destaques em livros sem capítulos definidos:** O rodapé da ficha deve omitir de maneira graciosa a indicação de capítulo, exibindo unicamente a obra e data sem lacunas estranhas.
- **Navegadores com restrição de permissão à área de transferência:** Ao acionar a cópia, se a permissão da área de transferência for negada pelo navegador, deve haver fallback seguro exibindo o texto selecionável em modal/balão contextual.
- **Preferência de Movimento Reduzido (`prefers-reduced-motion`):** As transições de expansão de contexto e indicadores de cópia devem concluir-se instantaneamente quando a preferência do sistema estiver ativa.

---

## 3. Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE exibir as passagens grifadas em formato de fichas literárias (*commonplace index cards*), com destaque tipográfico da citação e contraste visual claro em relação a notas pessoais do leitor.
- **FR-002**: O sistema DEVE disponibilizar categorias semânticas de grifo associadas a cada tonalidade (ex.: Ideia Central, Citação-chave, Dúvida, Refutação, Síntese), permitindo a filtragem rápida por intenção cognitiva.
- **FR-003**: Cada botão de filtro por tonalidade DEVE conter atributo de acessibilidade descritivo (`aria-label`) indicando tanto a cor quanto o significado intelectual da categoria.
- **FR-004**: O sistema DEVE permitir a busca textual por palavras contidas nas citações, anotações e títulos de livros, com atualização de resultados em tempo real.
- **FR-005**: O sistema DEVE suportar a alternância entre a visualização cronológica contínua ("Recentes") e a visualização agrupada por livro ("Por Obra"), persistindo a preferência do usuário entre sessões.
- **FR-006**: O sistema DEVE disponibilizar ação de cópia rápida da citação em pelo menos dois formatos estruturados: citação com referência de estudo e formato Markdown.
- **FR-007**: Ao acionar a cópia de uma citação, o sistema DEVE fornecer microfeedback visual e tátil imediato no botão e exibir uma confirmação temporária durante 1500ms antes de fechar automaticamente.
- **FR-008**: Para citações com mais de 260 caracteres, o sistema DEVE apresentar truncamento inicial elegante com ação para expandir o contexto em transição suave ($\le 180$ms).
- **FR-009**: O leitor DEVE ser capaz de editar a anotação pessoal associada a um destaque diretamente na própria ficha literária, com salvamento assíncrono e atualização imediata em tela.
- **FR-010**: O sistema DEVE exigir confirmação explícita do leitor antes de efetivar a exclusão de um destaque.
- **FR-011**: Em caso de falha de conexão ou erro ao buscar dados, o sistema DEVE apresentar um estado de erro acolhedor integrado às variáveis semânticas do tema ativo, banindo alertas vermelhos fixos desconexos.
- **FR-012**: O componente de estado de erro DEVE fornecer um botão "Tentar novamente" com foco acessível que reexecute a busca de dados.
- **FR-013**: Em cenários sem destaques ou sem resultados para os filtros selecionados, o sistema DEVE exibir mensagens de estado vazio contextualizadas que orientem o usuário sobre os próximos passos.
- **FR-014**: Toda a interface de destaques DEVE obedecer às diretrizes de imunidade cromática, consumindo exclusivamente tokens semânticos e sem classes utilitárias de cores arbitrárias ou valores hexadecimais embutidos no código da view.
- **FR-015**: Todas as animações e transições DEVEM respeitar a diretriz de `prefers-reduced-motion: reduce`, desativando durações temporais quando solicitado pelo sistema operacional.

---

### Key Entities

- **Destaque / Ficha Literária (`StudyHighlight` / `HighlightLibraryItem`):** Entidade principal contendo o trecho textual selecionado da obra (`selected_text`), anotação pessoal opcional (`note`), categoria/cor semântica (`color`), tipo de marcação (`kind`), posição ou localização e identificadores do estudo e livro de origem.
- **Categoria Semântica de Grifo:** Classificação intelectual atribuída às cores disponíveis (Amarelo, Verde, Azul, Rosa, Roxo), mapeando a cor para uma intenção cognitiva clara de estudo.
- **Agrupamento por Obra:** Estrutura de agregação que reúne destaques sob o título e autor de um mesmo livro para leitura panorâmica consolidada.

---

## 4. Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: O leitor consegue identificar o trecho citado da obra e diferenciá-lo da sua anotação pessoal em menos de 2 segundos de varredura visual de uma ficha literária.
- **SC-002**: A ação de cópia de citação em múltiplos formatos fornece feedback de confirmação em menos de 100ms após o clique e conclui a notificação flutuante em exatamente 1500ms.
- **SC-003**: 100% dos seletores de categoria de grifo possuem descrição textual acessível para tecnologias assistivas, garantindo navegabilidade sem dependência de percepção de cor.
- **SC-004**: O estado de erro de rede e o estado vazio da biblioteca consomem 100% de variáveis semânticas de tema, eliminando ocorrências de elementos visuais vermelhos rígidos (#fef2f2 / #991b1b) em todos os 10 temas suportados.
- **SC-005**: A expansão de contexto para citações longas ocorre em transição fluida de no máximo 180ms a 60 FPS acelerada por GPU, ou instantaneamente sob preferência de movimento reduzido.
- **SC-006**: A experiência permanece plenamente utilizável em telas móveis e desktop, com alvos de toque mínimos de 44x44px em todos os controles interativos.

---

## 5. Assumptions

- **Compatibilidade com o Modelo Existente:** O modelo de dados e os endpoints de API de destaques (`/api/studies/{id}/highlights` e `/api/highlights/library`) já existentes no sistema suprem integralmente os dados necessários sem alterações no schema do banco de dados.
- **Preservação de Integrações:** As funcionalidades já existentes de link direto para o estudo original e persistência do modo de visualização em armazenamento local continuam ativas.
- **Imunidade dos 10 Temas:** As novas fichas literárias utilizam unicamente variáveis de design tokens já consolidadas no Leitorum (`--bg-surface`, `--bg-subtle`, `--text-primary`, `--text-muted`, `--border-subtle`, `--accent-primary`), adaptando-se harmonicamente a todos os temas claros, escuros, sépia e de alto contraste.
