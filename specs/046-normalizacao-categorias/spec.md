# Feature Specification: F0.6.7 — Normalização e Simplificação de Categorias

**Feature Branch**: `046-normalizacao-categorias`

**Created**: 2026-10-02

**Status**: Ready for Planning

**Input**: User description: "F0.6.7 — Normalização e Simplificação de Categorias (Roadmap 0.6: Reorganizar a taxonomia atual do Leitorum para nomes canônicos no singular, curtos, sem duplicatas, mapeando categorias antigas para canônicas sem perda de dados e impedindo novas categorias fora das regras)."

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Catálogo Canônico e Navegação Limpa do Acervo (Priority: P1 - MVP)

Como leitor do Leitorum, quero visualizar meu acervo organizado por categorias curtas, canônicas e em forma singular (ex.: "Filosofia", "História", "Ciência", "Direito"), para que a navegação e a filtragem de livros e estudos sejam previsíveis, limpas e sem poluição de nomes compostos ou plurais redundantes, preservando integralmente todas as associações existentes de livros.

**Why this priority**: É o valor central da feature. A taxonomia legada possui mais de uma centena de variações, nomes compostos longos e plurais que poluem filtros e agrupamentos visuais. Entregar a navegação canônica resolve imediatamente a clareza do produto.

**Independent Test**: Pode ser testado de forma isolada ao acessar a biblioteca e os filtros de categorias: livros com categorizações anteriores refletem suas categorias canônicas normalizadas e a lista de categorias disponíveis para filtro apresenta apenas termos únicos e no singular, com 0 perda de associações de livros.

**Acceptance Scenarios**:

1. **Given** um livro anteriormente associado a categorias longas ou compostas (ex.: "Ciências Sociais e Humanas" ou "Histórias de Ficção"), **When** o leitor visualiza o acervo ou a página de detalhes do livro, **Then** as categorias exibidas são os termos canônicos curtos correspondentes (ex.: "Ciência", "História"), mantendo o livro corretamente classificado.
2. **Given** múltiplos livros associados a variações da mesma raiz (ex.: "Filosofias", "filosofia", "Filosofia"), **When** o leitor filtra por categoria na biblioteca ou no painel de agrupamento, **Then** existe exatamente uma única categoria canônica ("Filosofia") agregando todos os livros pertinentes.
3. **Given** um acervo existente, **When** a normalização taxonômica é aplicada, **Then** nenhum livro ou estudo perde sua relação de classificação e nenhum registro de conteúdo é excluído.

---

### User Story 2 - Categorização e Criação Guiada por Regras Canônicas (Priority: P2)

Como leitor cadastrando ou editando um livro, quero que o formulário de categorização me ofereça e valide termos dentro do padrão canônico (palavra única, singular, sem termos compostos ou duplicatas semânticas), para que novas categorias não reintroduzam a desorganização taxonômica no sistema.

**Why this priority**: Evita regressão taxonômica. Uma vez normalizado o catálogo existente, a interface de edição precisa orientar e manter a consistência contínua.

**Independent Test**: Pode ser testado abrindo o modal de edição/cadastro de livro: ao digitar um nome de categoria, o sistema sugere termos canônicos existentes e valida que novos termos respeitem o padrão singular e de termo único antes de confirmar.

**Acceptance Scenarios**:

1. **Given** o formulário de edição/criação de livro, **When** o usuário começa a digitar no campo de categorias, **Then** o sistema exibe sugestões baseadas no catálogo canônico aprovado.
2. **Given** a tentativa de associar uma nova categoria em forma plural ou composta (ex.: "Romances Históricos"), **When** o usuário submete a edição, **Then** o sistema orienta e aplica a forma canônica válida conforme a política adotada.
3. **Given** duas entradas com diferenças apenas de caixa alta/baixa ou acentos supérfluos, **When** o usuário tenta cadastrar, **Then** o sistema reconhece a identidade semântica e associa à categoria canônica já existente sem criar duplicatas no banco.

---

### User Story 3 - Painel e Relatório de Conformidade Taxonômica (Priority: P3)

Como administrador ou gestor do acervo, quero consultar uma visão consolidada da taxonomia (categorias canônicas, quantidade de livros vinculados e histórico de correspondências migradas), para auditar a saúde e a reutilização das classificações do Leitorum.

**Why this priority**: Garante governança e rastreabilidade para o proprietário do acervo, comprovando a migração segura e auditável da taxonomia legada.

**Independent Test**: Pode ser testado acessando a seção de categorias/administração: o sistema lista o catálogo canônico ordenado alfabeticamente com os contadores de obras associadas e o mapa de correspondência de termos legados.

**Acceptance Scenarios**:

1. **Given** o painel de categorias do sistema, **When** a listagem é consultada, **Then** cada categoria canônica informa o total de livros associados em tempo real.
2. **Given** uma categoria canônica sem nenhum livro vinculado, **When** o gestor revisa a taxonomia, **Then** é possível identificar categorias não utilizadas para limpeza segura sem afetar acervos ativos.

---

### Edge Cases

- **Convergência de múltiplas categorias no mesmo livro**: Um livro que possuía simultaneamente duas categorias antigas que mapeiam para a mesma categoria canônica (ex.: "Ficção" e "Ficção Científica" ambas convergindo para "Ficção") deve ter a associação deduplicada para manter exatamente uma única ligação canônica, sem violar restrições de chave única.
- **Variações de acentuação e diacríticos em português**: Entradas como "Historia" sem acento e "História" com acento devem colapsar de forma determinística na forma gramaticalmente correta em língua portuguesa ("História").
- **Termos compostos consagrados**: Termos como "Ficção Científica" ou "Artes Visuais" que historicamente poderiam ser compostos: definir se colapsam para termo único canônico raiz ("Ficção", "Arte") ou se termos compostos canônicos estritamente limitados são admitidos.
- **Ambiente multiusuário e visibilidade**: Livros compartilhados com outros leitores devem exibir a mesma categoria canônica normalizada sem expor identificadores privados.
- **Preservação de filtros e URLs**: Links salvos ou filtros no frontend que utilizavam nomes de categorias antigas devem redirecionar suavemente ou mapear para a categoria canônica correspondente sem quebrar a tela com estado vazio.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE fornecer um catálogo de categorias canônicas onde cada categoria possui um nome único, em forma singular e com grafia correta em língua portuguesa.
- **FR-002**: O sistema DEVE mapear todas as categorias existentes na base de dados para suas respectivas categorias canônicas através de uma tabela de correspondência auditável e não destrutiva.
- **FR-003**: A normalização DEVE preservar 100% dos vínculos de livros existentes, garantindo que nenhum livro ou estudo perca sua classificação temática.
- **FR-004**: Quando múltiplas categorias legadas de um mesmo livro convergirem para uma única categoria canônica, o sistema DEVE consolidar o vínculo sem gerar registros duplicados de junção.
- **FR-005**: A normalização DEVE adotar atribuição distributiva para categorias compostas: quando uma designação legada combinava dois ou mais ramos temáticos distintos (ex.: "Ciências Sociais e Humanas"), o livro associado recebe as respectivas categorias canônicas individuais (ex.: "Ciência" e "Humanidades"), com garantia de unicidade sem duplicar pares idênticos de livro-categoria.
- **FR-006**: A estrutura taxonômica DEVE ser estritamente plana (*flat*) de nível único, descontinuando aninhamentos hierárquicos arbitrários para garantir que todas as categorias canônicas funcionem como marcadores temáticos diretos, ágeis e coesos nos filtros do acervo.
- **FR-007**: O sistema DEVE fornecer normalização assistida transparente com sugestões: no formulário de edição/criação, o sistema sugere termos canônicos existentes em tempo real e, caso o usuário informe variações de plural (ex.: "Filosofias") ou com pontuação/espaços supérfluos, converte e sugere automaticamente a forma canônica singular correspondente ("Filosofia") antes da persistência.
- **FR-008**: O sistema DEVE impedir a criação de categorias duplicadas que difiram apenas por caixa alta/baixa (case-insensitive), acentuação gráfica supérflua ou espaços em branco nas extremidades.
- **FR-009**: Os endpoints de listagem de categorias e de filtros de livros DEVEM retornar exclusivamente as categorias canônicas ativas e normalizadas.
- **FR-010**: O sistema DEVE fornecer busca e autocompletar de categorias no formulário de edição de livros para guiar o leitor a selecionar termos canônicos pré-existentes antes de criar novos.
- **FR-011**: Nenhuma categoria canônica com livros vinculados PODE ser excluída de forma irreversível sem prévia reatribuição ou aviso explícito ao usuário.
- **FR-012**: Todas as operações de leitura e atualização de categorias DEVEM respeitar o isolamento multiusuário e as permissões de acesso do Leitorum.

---

### Key Entities *(include if feature involves data)*

- **Category (Categoria Canônica)**: Entidade que representa o tema ou classificação normalizada do acervo. Atributos conceituais: identificador único, nome canônico (singular, termo curto), rótulo normalizado para busca e data de criação.
- **CategoryMapping (Mapeamento de Normalização)**: Relação entre uma designação legada/variante e a categoria canônica oficial, utilizada para migração segura e rastreabilidade sem perda de histórico.
- **BookCategoryAssociation**: Vínculo entre uma obra do acervo e uma ou mais categorias canônicas correspondentes, com garantia de unicidade por par livro-categoria.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% dos livros atualmente existentes no acervo mantêm sua classificação temática válida após a migração, com zero livros desassociados ou órfãos.
- **SC-002**: Redução de pelo menos 60% na quantidade total de categorias distintas visíveis no catálogo, eliminando duplicatas semânticas, plurais e nomes excessivamente longos.
- **SC-003**: 100% das categorias canônicas ativas respeitam o critério de forma singular e nome conciso em português.
- **SC-004**: O tempo de carregamento da listagem de categorias e filtros de livros na biblioteca permanece abaixo de 200 milissegundos.
- **SC-005**: Usuários conseguem categorizar novos livros selecionando opções canônicas sugeridas em menos de 5 segundos no formulário de edição.

---

## Assumptions

- A migração de categorias será executada com base em uma tabela canônica bem definida e auditada antes da aplicação definitiva.
- A preservação dos dados de leitura e fichamentos é prioridade absoluta (Princípio I da Constituição).
- A aplicação local e multiusuário permanece operando sobre FastAPI e SQLite WAL sem dependências externas.
