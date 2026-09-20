# Feature Specification: F09 - Sistema Visual Profissional

**Feature Branch**: `017-sistema-visual-profissional`

**Created**: 2026-09-19

**Status**: Ready for Planning

**Input**: User description: "F09 - Sistema Visual Profissional"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Iconografia Vetorial Sóbria e Erradicação de Emojis (Priority: P1)

Como leitor e pesquisador que utiliza o Caderno de Leitura para estudos intelectuais aprofundados,
quero interagir com uma interface visual sóbria, elegante e consistente, com ícones vetoriais monocromáticos ou de acento calibrado em todos os botões, cabeçalhos, barras de navegação e menus,
para que a aplicação transmita rigor editorial profissional e elimine qualquer aspecto de prototipagem informal causada por emojis dispersos.

**Why this priority**: É o pilar fundacional da versão 0.4. Estabelece a identidade estética definitiva e a linguagem de controle visual para todas as telas existentes e futuras visualizações (F01 a F10), garantindo legibilidade e harmonia com as 5 Superclasses de Interface.

**Independent Test**: Pode ser testado navegando por todas as vistas da aplicação (Acervo, Livro, Estudo, Edição, Lixeira, Ajustes e Dashboard) e verificando visualmente e no código do DOM que nenhum emoji é utilizado como ícone de controle ou elemento de navegação, sendo todos substituídos por ícones vetoriais nítidos e acessíveis.

**Acceptance Scenarios**:

1. **Given** que o usuário acessa a barra de navegação global ou a barra de ferramentas do acervo, **When** observa os botões de ação (adicionar livro, importar, alternar visualização, lixeira, ajustes, dashboard), **Then** cada ação exibe um ícone vetorial nítido com espessura de traço consistente e sem qualquer emoji.
2. **Given** que o usuário interage com botões de ação em cards e tabelas (editar, excluir, restaurar, exportar, alternar capítulo), **When** os botões são renderizados, **Then** eles utilizam ícones padronizados que se adaptam suavemente às cores do tema ativo (Claro, Escuro, Sépia).
3. **Given** que um leitor de tela inspeciona qualquer botão baseado em ícone, **When** o elemento recebe foco, **Then** um rótulo textual descritivo acessível é anunciado e o ícone decorativo permanece oculto para tecnologias assistivas.

---

### User Story 2 - Purificação Semântica e Erradicação de Rótulos de IA (Priority: P2)

Como usuário que organiza seus fichamentos e anotações pessoais,
quero visualizar e preencher campos com terminologias editoriais clássicas e rigorosas de estudo humano (ex.: Fichamento, Contexto da Leitura, Análise Estrutural, Conceitos-Chave),
para que o sistema valorize a autoria do leitor e elimine termos impessoais ou datados como "resposta da IA", "gerado por IA" ou "prompt".

**Why this priority**: A aplicação é um caderno pessoal de estudos e leitura crítica. Termos associados a robôs ou geradores automatizados distorcem o propósito da ferramenta, que visa a assimilação ativa e a curadoria intelectual do leitor.

**Independent Test**: Pode ser testado abrindo o formulário de criação/edição de estudos e a tela de leitura de anotações, confirmando que todos os rótulos de campos, títulos de abas e mensagens de ajuda adotam nomenclatura editorial e que nenhuma menção a "IA" permanece na interface.

**Acceptance Scenarios**:

1. **Given** que o leitor abre um estudo para leitura ou edição, **When** visualiza as seções de anotações e fichamento, **Then** o campo de texto original e contexto é rotulado com a nomenclatura editorial oficial "Fichamento da Fonte".
2. **Given** que o usuário importa ou cadastra novas notas, **When** lê as orientações e placeholders dos campos de entrada, **Then** os textos explicativos orientam a organização do raciocínio e da síntese conceitual sem sugerir que o conteúdo pertence a um agente externo.
3. **Given** que o usuário visualiza alertas do sistema ou mensagens de ajuda nos modais, **Then** o vocabulário utilizado mantém tom respeitoso, técnico e culto em português.

---

### User Story 3 - Padronização de Estados de Interface: Carregamento, Vazio e Feedback (Priority: P3)

Como leitor que transita entre livros e estudos de diferentes tamanhos,
quero que as áreas de conteúdo exibam esqueletos de carregamento proporcionais enquanto os dados são recuperados, estados vazios acolhedores com orientações úteis quando não houver dados, e notificações de desfecho discretas,
para que a navegação seja fluida, previsível e livre de saltos bruscos de layout (*layout shifts*).

**Why this priority**: A estabilidade percebida de um software profissional depende da previsibilidade de seus estados de transição. Telas em branco momentâneas ou mensagens de erro despadronizadas causam sensação de quebra e insegurança operacional.

**Independent Test**: Pode ser testado simulando latência na consulta de estudos (verificando os esqueletos proporcionais de carregamento), visualizando uma lixeira ou lista de categorias vazia (verificando o componente de estado vazio com ação de retorno), e disparando ações de salvamento/exclusão (verificando os toasts/banners de feedback harmonizados).

**Acceptance Scenarios**:

1. **Given** que uma visualização está aguardando os dados do servidor, **When** a tela é desenhada, **Then** blocos de esqueleto de carregamento com as proporções exatas dos cards e linhas são exibidos suavemente sem causar deslocamento na tela quando o conteúdo definitivo chega.
2. **Given** que uma seção não contém itens (ex.: acervo sem livros cadastrados, lixeira limpa, livro sem estudos, busca sem resultados), **When** o usuário visualiza a área, **Then** um estado vazio padronizado é exibido contendo ícone vetorial contextual, mensagem esclarecedora e um botão de ação primária relevante.
3. **Given** que o usuário executa uma operação (ex.: salvar alterações, mover para lixeira, restaurar backup), **When** a ação é concluída com sucesso ou erro, **Then** uma notificação visual padronizada surge com contraste adequado e desaparece sem exigir clique, respeitando as preferências de movimento do usuário.

---

### Edge Cases

- **Dispositivos com renderização limitada de fontes/ícones:** O sistema deve assegurar que os ícones vetoriais sejam desenhados via SVG renderizado nativamente pelo navegador, sem depender de webfonts de terceiros que possam falhar no carregamento offline.
- **Telas monocromáticas ou modo E-Ink:** Os ícones e esqueletos de carregamento devem preservar contraste legível em telas preto e branco ou com paleta de alto contraste, sem depender exclusivamente de gradações sutis de cinza.
- **Títulos e textos extremamente longos em botões de ação:** Quando um botão com ícone e texto for exibido em telas compactas (smartphones de 320px a 375px), o texto deve truncar elegantemente ou priorizar o ícone com área de toque mínima preservada de 44x44px.
- **Preferência de redução de movimento (`prefers-reduced-motion`):** As animações de transição de esqueleto (*shimmer*) devem ser estáticas ou instantâneas quando o usuário tiver a opção de acessibilidade ativada no sistema.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE substituir integralmente todos os emojis utilizados como elementos de interface, botões, abas e cabeçalhos por ícones vetoriais padronizados.
- **FR-002**: O sistema DEVE adotar oficialmente o conjunto de ícones Lucide Icons (pacote `lucide-vue-next`), garantindo traço geométrico sóbrio (stroke 1.5–2px, tamanho padrão 20–24px) e tree-shaking rigoroso no empacotador.
- **FR-003**: Todos os botões e elementos interativos baseados em ícones DEVEM possuir rótulos acessíveis explícitos (`aria-label` ou texto visível equivalente) e ocultar ícones decorativos de leitores de tela (`aria-hidden="true"`).
- **FR-004**: O sistema DEVE remover todas as ocorrências de termos alusivos a "IA", "resposta da IA", "gerado por IA" ou "prompt" nos textos da interface, formulários, modais e visualizadores.
- **FR-005**: O campo que armazena o texto-base de estudo original (`source_response` no modelo de dados interno) DEVE ser apresentado ao usuário sob a nomenclatura editorial canônica "Fichamento da Fonte", mantendo a coluna do banco inalterada por compatibilidade.
- **FR-006**: O sistema DEVE fornecer um componente padronizado de Estado Vazio (*Empty State*) para listas de acervo, lixeira, capítulos vazios, estudos sem anotações e resultados de busca sem correspondência.
- **FR-007**: O sistema DEVE fornecer um componente padronizado de Esqueleto de Carregamento (*Loading Skeleton*) que reflita a geometria das visualizações ativas durante requisições assíncronas.
- **FR-008**: Os esqueletos de carregamento DEVEM utilizar animação de pulso suave com gradiente shimmer por padrão, comutando automaticamente para renderização estática sem animação quando a preferência `prefers-reduced-motion` estiver ativa ou em modos de alto contraste/E-Ink.
- **FR-009**: O sistema DEVE disponibilizar badges informativos e indicadores de status padronizados para categorias, contadores e estados de estudo.
- **FR-010**: Todas as cores, bordas, sombras e contrastes dos novos componentes visuais DEVEM se harmonizar dinamicamente com os temas (Claro, Escuro, Sépia) e as 5 Superclasses de Interface (Zero-G, Mecânica, Invisível, Dimensional e Monolítica).

### Key Entities *(include if feature involves data)*

- **IconDefinition**: Representação semântica de um ícone do sistema, encapsulando nome do glifo, tamanho padrão, espessura de traço e rótulo de acessibilidade.
- **EmptyStateConfig**: Configuração de apresentação para seções vazias, contendo identificador de ícone, título explicativo, mensagem orientadora e ação recomendada opcional.
- **EditorialTermsMapping**: Mapeamento padronizado de vocabulário editorial que substitui termos informais ou legados por designações canônicas em português culto.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% dos emojis utilizados como ícones ou elementos visuais de controle são erradicados de todas as visualizações e componentes da aplicação.
- **SC-002**: 100% das referências a "IA", "resposta de IA" ou "prompt" são substituídas por terminologias editoriais nos textos visíveis ao usuário.
- **SC-003**: A área clicável de todos os botões baseados em ícones atinge no mínimo 44x44 pixels em dispositivos móveis e telas sensíveis ao toque.
- **SC-004**: O índice de deslocamento cumulativo de layout (*Cumulative Layout Shift* - CLS) durante o carregamento assíncrono de dados com esqueletos permanece inferior a 0.05.
- **SC-005**: A suíte de testes de integridade visual e acessibilidade valida que todos os controles com ícones possuem atributos de acessibilidade correspondentes sem regressões.

## Assumptions

- O modelo de dados interno e o banco de dados preservam as colunas existentes (como `source_response`) para garantir integridade e compatibilidade com backups e migrações anteriores, alterando exclusivamente a camada de apresentação ao usuário.
- Os ícones vetoriais adotados são leves, renderizados localmente via SVG no cliente, sem dependência de conexões com CDNs externas.
- A padronização visual respeita as configurações de tema e densidade já consolidadas na versão 0.3 sem anular preferências salvas pelo leitor.
