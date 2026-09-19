# Feature Specification: Categorias e Taxonomia de Livros

**Feature Branch**: `006-categorias-taxonomia`  
**Created**: 2026-09-18  
**Status**: Ready for Planning  
**Input**: User description: "T05 - Categorias e taxonomia"

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Atribuição e Gestão de Categorias em Livros (Priority: P1)

Como leitor e estudioso organizando meu acervo pessoal, quero associar uma ou mais categorias temáticas aos meus livros ao cadastrá-los ou editá-los, para que eu possa estruturar minha biblioteca por áreas do conhecimento e temas de estudo.

**Why this priority**: A associação direta de categorias à obra é o ponto de contato fundamental do usuário com a taxonomia do sistema, permitindo que cada livro ganhe contexto temático com relação muitos-para-muitos (N:N).

**Independent Test**: Pode ser testado abrindo o modal de edição de um livro existente ("Memórias Póstumas de Brás Cubas"), associando duas categorias ("Literatura Brasileira" e "Ficção"), salvando a edição e verificando que ambas as categorias aparecem como badges visíveis na ficha e nos cartões do livro, inclusive após recarregar a página e editar outros campos.

**Acceptance Scenarios**:

1. **Given** um livro aberto no modal de edição, **When** o usuário seleciona uma ou mais categorias do catálogo e salva a alteração, **Then** o livro é atualizado e passa a exibir todas as categorias associadas como etiquetas (badges).
2. **Given** um livro com múltiplas categorias atribuídas, **When** o usuário remove uma das categorias e salva, **Then** apenas a categoria desassociada é removida do livro, mantendo as demais e sem afetar a integridade da categoria no catálogo geral.
3. **Given** um livro com categorias atribuídas, **When** o usuário altera outros campos (título, autor, ano, capa) e salva, **Then** as categorias previamente associadas permanecem intactas.
4. **Given** um livro recém-cadastrado no acervo, **When** o usuário opta por não selecionar nenhuma categoria, **Then** o livro é salvo normalmente sem categorias obrigatórias impostas.

---

### User Story 2 - Busca Preditiva de Categorias com Caminho Hierárquico (Priority: P2)

Como usuário classificando um livro, quero digitar letras no seletor de categorias e ver sugestões instantâneas que mostram tanto o nome da categoria quanto seu caminho hierárquico completo (ex.: "Ciências Humanas / Filosofia / Ética"), para que eu encontre o termo exato sem me perder na hierarquia e sem ambiguidade entre termos parecidos.

**Why this priority**: Com mais de 100 categorias disponíveis, uma lista linear solta torna-se impraticável; a busca preditiva com trilha hierárquica é indispensável para uma seleção ágil e precisa.

**Independent Test**: Pode ser testado digitando termos como "ética", "física" ou "brasil" no campo de categorias do modal de livro e confirmando que as opções sugeridas apresentam a linhagem de categorias pai formatada com clareza.

**Acceptance Scenarios**:

1. **Given** o seletor de categorias aberto, **When** o usuário digita "historia", **Then** o sistema exibe opções como "Ciências Humanas / História / História Antiga" e "Ciências Humanas / História / História do Brasil", insensível a acentos e maiúsculas.
2. **Given** o usuário selecionando uma sugestão preditiva, **When** ele clica ou pressiona Enter sobre a opção sugerida, **Then** a categoria selecionada é adicionada ao livro como uma etiqueta (badge) visível e removível.
3. **Given** um termo de busca digitado que não encontra correspondência no catálogo, **When** a lista preditiva é consultada, **Then** é exibida mensagem amigável de que nenhuma categoria foi encontrada.

---

### User Story 3 - Catálogo Canônico com Mais de 100 Categorias e Importação Idempotente (Priority: P3)

Como mantenedor do sistema e usuário, quero contar com uma taxonomia rica e canônica com mais de 100 categorias estruturadas em português e organizadas hierarquicamente (categorias raízes e subcategorias), cuja carga inicial e atualizações futuras sejam 100% idempotentes e não dupliquem registros nem rompam vínculos com livros existentes.

**Why this priority**: Garante que o sistema ofereça imediatamente uma biblioteca taxonômica padronizada, útil e pronta para uso, sem exigir que o usuário cadastre manualmente dezenas de categorias básicas.

**Independent Test**: Pode ser testado executando a rotina de importação/sincronização do catálogo duas ou mais vezes seguidas em um banco com livros já associados a categorias, confirmando que a contagem total de categorias permanece estável, sem duplicações, sem ciclos na árvore e sem que nenhum livro perca seus vínculos.

**Acceptance Scenarios**:

1. **Given** a inicialização do sistema ou banco de dados, **When** a carga taxonômica é executada, **Then** o catálogo passa a conter mais de 100 categorias ativas em língua portuguesa com identificadores estáveis e relações de parentesco válidas.
2. **Given** um catálogo previamente importado e livros já vinculados a categorias, **When** a importação/seed é reexecutada (idempotência), **Then** os registros existentes são preservados sem duplicação de identificadores e sem perda de associações existentes.
3. **Given** as relações de hierarquia entre categorias do catálogo, **When** a árvore de parentesco é percorrida, **Then** não existe nenhum ciclo de dependência circular (ex.: A pai de B e B pai de A) e todas as categorias raízes possuem ancestral nulo.

---

### User Story 4 - Filtragem do Acervo por Categorias e Subcategorias Recursivas (Priority: P4)

Como leitor explorando seu acervo, quero filtrar os livros da estante selecionando uma categoria específica na barra de ferramentas ou clicando na etiqueta de uma categoria em um livro, para visualizar apenas as leituras correspondentes àquele assunto ou área de estudo, incluindo automaticamente livros associados a subcategorias da categoria selecionada.

**Why this priority**: Complementa a busca por texto e modos de visualização (entregues em T04), conferindo real utilidade à organização taxonômica do acervo através de agrupamento inclusivo.

**Independent Test**: Pode ser testado selecionando a categoria pai "Filosofia" na barra do acervo; a visualização (grade ou lista) deve atualizar para exibir todos os livros associados a "Filosofia" e também os livros associados a "Filosofia / Ética" ou "Filosofia / Epistemologia", atualizando a contagem dinâmica de livros encontrados.

**Acceptance Scenarios**:

1. **Given** o acervo com múltiplos livros categorizados, **When** o usuário escolhe uma categoria no filtro, **Then** todos os livros pertencentes àquela categoria ou a qualquer uma de suas subcategorias descendentes são apresentados.
2. **Given** um filtro de categoria ativo, **When** o usuário combina com uma busca textual por título/autor, **Then** o resultado exibe a interseção estrita dos dois filtros.
3. **Given** um filtro de categoria ativo, **When** o usuário limpa o filtro, **Then** a visualização completa do acervo é restabelecida.

---

### Edge Cases

- O que acontece se uma categoria tiver ciclo de referência (categoria A apontando para si mesma ou como filha de uma descendente)? O sistema deve validar a integridade da taxonomia e rejeitar ciclos hierárquicos.
- O que acontece se um livro vinculado a categorias for movido para a lixeira (soft delete)? Os vínculos com as categorias são preservados intactos para restauração futura; o livro apenas deixa de aparecer no filtro do acervo ativo.
- O que acontece se um livro for excluído definitivamente do acervo? As entradas de relacionamento associando o livro às suas categorias são excluídas transacionalmente, enquanto as categorias no catálogo permanecem intactas.
- O que acontece se o catálogo canônico for atualizado com novas subcategorias em uma versão futura? Novas categorias são inseridas e rótulos são atualizados de forma idempotente, preservando todos os vínculos já existentes com livros.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE fornecer e carregar um catálogo canônico estruturado em JSON com mais de 100 categorias de conhecimento úteis em língua portuguesa, organizadas com identificadores estáveis e relações hierárquicas de parentesco (`parent_id`).
- **FR-002**: O sistema DEVE permitir a associação de múltiplas categorias por livro (relação muitos-para-muitos / N:N), representadas como etiquetas (badges) visíveis, navegáveis e removíveis.
- **FR-003**: O seletor de categorias DEVE oferecer busca preditiva com digitação (typeahead/autocomplete) insensível a caixa e diacríticos, exibindo a trilha hierárquica completa da categoria (ex.: "Ciências Humanas / Filosofia / Ética").
- **FR-004**: O sistema DEVE preservar todas as categorias associadas a um livro durante a edição de qualquer outro campo da obra (título, autor, capa, ano, notas).
- **FR-005**: A rotina de carga e atualização do catálogo taxonômico DEVE ser estritamente idempotente, não permitindo duplicação de identificadores, nem ciclos na árvore hierárquica, nem rompimento de vínculos preexistentes com livros.
- **FR-006**: Na versão 0.3, o sistema utilizará exclusivamente o catálogo canônico padronizado de mais de 100 categorias canônicas estruturado em JSON, garantindo consistência taxonômica sem duplicações e sem necessidade de interface de CRUD de categorias pelo usuário.
- **FR-007**: O filtro de categorias no acervo DEVE ser recursivo e inclusivo: selecionar uma categoria pai (ex.: "Filosofia") exibe todos os livros vinculados a essa categoria e a qualquer uma de suas subcategorias descendentes.
- **FR-008**: O envio de um livro para a lixeira (soft delete) DEVE manter seus vínculos taxonômicos intactos para que a restauração recupere a classificação original do livro.
- **FR-009**: A exclusão definitiva de um livro DEVE expurgar os vínculos associativos sem remover nenhuma categoria do catálogo geral.
- **FR-010**: O sistema NUNCA DEVE realizar geração de categorias ou classificação automática via inteligência artificial em tempo de execução.
- **FR-011**: As categorias associadas aos livros DEVEM ser preservadas integralmente em rotinas de backup, snapshot e exportação.

---

### Key Entities *(include if feature involves data)*

- **Category (Categoria)**:
  - `id`: Identificador textual estável (slug ou código canônico padronizado, ex.: `filosofia-etica`).
  - `name`: Nome legível da categoria em língua portuguesa (ex.: "Ética").
  - `parent_id`: Identificador da categoria pai (anulável para categorias de nível superior/raízes).
  - `path`: Caminho hierárquico formatado para navegação e busca (ex.: "Ciências Humanas / Filosofia / Ética").
- **BookCategory (Associação Livro-Categoria)**:
  - `book_id`: Identificador do livro.
  - `category_id`: Identificador da categoria associada.
- **CategoryCatalogue (Catálogo Canônico)**:
  - Estrutura estática serializada em JSON contendo o conjunto completo de mais de 100 categorias canônicas hierarquizadas.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: O catálogo taxonômico deve disponibilizar mais de 100 categorias válidas em língua portuguesa sem nenhum identificador duplicado e com zero ciclos hierárquicos.
- **SC-002**: A busca preditiva de categorias deve retornar sugestões com seus caminhos hierárquicos em menos de 50ms a partir de qualquer fragmento de texto digitado.
- **SC-003**: A reexecução da carga do catálogo (idempotência) deve manter 100% dos vínculos existentes entre livros e categorias sem criar registros órfãos ou duplicados.
- **SC-004**: 100% dos livros associados a categorias devem ter suas classificações recuperadas intactas após envio para a lixeira e restauração.
- **SC-005**: 100% das operações de edição de metadados gerais do livro (título, autor, ano, capa) devem preservar inalteradas as categorias associadas.
- **SC-006**: Ao filtrar o acervo por uma categoria pai, 100% dos livros pertencentes a subcategorias descendentes devem ser exibidos no resultado.

---

## Assumptions

- O catálogo com mais de 100 categorias canônicas será versionado como um arquivo JSON no backend (`backend/app/data/categories.json` ou equivalente) e carregado no banco de dados na inicialização ou migração.
- A associação entre livros e categorias utilizará uma tabela associativa (relação muitos-para-muitos), permitindo que uma obra pertença a múltiplos temas conforme a recomendação do Roadmap 0.3.
- A exclusão de um livro da lixeira não apaga categorias do catálogo geral.
- Em conformidade estrita com o Roadmap 0.3 e as regras de governança, nenhuma categoria será inventada ou atribuída automaticamente via modelos de linguagem (IA) em tempo de execução.
