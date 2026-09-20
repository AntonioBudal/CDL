# Feature Specification: Fundação Multiusuário e CRUD Geral

**Feature Branch**: `028-fundacao-multiusuario`  
**Created**: 2026-09-20  
**Status**: Ready for Planning  
**Input**: User description: "F01 - Fundação Multiusuário e CRUD Geral — transformar os dados atuais em dados pertencentes a usuários"

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Migração Transparente do Acervo Existente para o Proprietário Inicial (Priority: P1)

Como leitor que já utiliza o Caderno de Leitura, desejo que todo o meu acervo atual (livros, capítulos, estudos, anotações pessoais, relacionamentos e categorias) seja atribuído com segurança à minha conta de proprietário inicial na primeira inicialização da versão multiusuário, para que nenhum dado seja corrompido, perdido ou desvinculado.

**Why this priority**: É a garantia de preservação de dados e integridade do patrimônio intelectual construído nas versões 0.1 a 0.4, condição inegociável para qualquer evolução arquitetural.

**Independent Test**: Executar a atualização da base de dados contendo registros legados pré-existentes e verificar que 100% dos livros, capítulos, estudos e anotações permanecem acessíveis e integralmente vinculados à identidade do proprietário inicial.

**Acceptance Scenarios**:
1. **Given** uma base de dados pré-existente com registros sem identificação de proprietário, **When** o sistema inicializa sob a nova versão, **Then** um perfil de proprietário inicial é formalmente estabelecido e todos os registros são associados a ele sem perdas.
2. **Given** a migração concluída, **When** o usuário proprietário acessa sua estante e estudos, **Then** todas as contagens, textos de fichamento, relações conceituais e anotações pessoais permanecem exatamente idênticas ao estado anterior.
3. **Given** qualquer falha inesperada durante o processo de migração, **When** o procedimento é interrompido, **Then** a integridade dos dados anteriores é mantida sem corrupção parcial.

---

### User Story 2 - Criação e Propriedade de Novos Recursos no CRUD Geral (Priority: P1)

Como usuário cadastrado na plataforma, desejo que cada novo livro, capítulo, estudo ou anotação que eu registrar seja automaticamente carimbado como de minha exclusiva propriedade, para que meus conteúdos fiquem salvaguardados e associados à minha autoria.

**Why this priority**: Estabelece o princípio fundacional da versão 0.5: cada registro possui um dono canônico desde o momento da sua criação.

**Independent Test**: Criar um livro e registrar estudos através da interface ou dos serviços centrais e verificar que todos os registros recém-criados possuem o identificador de propriedade do usuário ativo.

**Acceptance Scenarios**:
1. **Given** um usuário logado na aplicação, **When** ele cadastra um novo livro na estante, **Then** o livro é registrado com o identificador de propriedade deste usuário.
2. **Given** um livro pertencente ao usuário, **When** ele importa ou cria um novo estudo, **Then** o estudo e os capítulos associados herdam rigorosamente a propriedade do autor.
3. **Given** um usuário criando categorias ou relações conceituais, **When** o registro é salvo, **Then** a entidade é vinculada ao espaço do usuário.

---

### User Story 3 - Isolamento Estrito de Consultas e Operações (Priority: P1)

Como leitor com dados privados no sistema, desejo que a minha estante, meus estudos, o cockpit analítico e a lixeira exibam exclusivamente os conteúdos que me pertencem, para que outros usuários do mesmo servidor local nunca visualizem nem acessem minhas anotações sem minha autorização expressa.

**Why this priority**: Garante o isolamento completo entre usuários (multi-tenancy local seguro) e previne vazamento acidental de anotações e leituras privadas.

**Independent Test**: Cadastrar dois usuários distintos ("Leitor A" e "Leitor B") no mesmo ambiente; criar obras e estudos para cada um; autenticar como "Leitor A" e verificar que as listagens de livros, estudos, busca global e lixeira contêm apenas os dados do "Leitor A".

**Acceptance Scenarios**:
1. **Given** dois usuários com acervos cadastrados no sistema, **When** o "Leitor A" consulta sua biblioteca, **Then** nenhum livro ou estudo do "Leitor B" é retornado na listagem ou na busca.
2. **Given** o "Leitor A" acessando o painel analítico (estatísticas, hábitos de leitura), **When** os cálculos são gerados, **Then** consideram estritamente o histórico e as métricas do "Leitor A".
3. **Given** o "Leitor A" acessando a lixeira, **When** a listagem é aberta, **Then** apenas itens excluídos pelo "Leitor A" são visíveis para restauração.

---

### User Story 4 - Autorização Rígida de Edição, Exclusão e Restauração (Priority: P1)

Como autor e proprietário dos meus estudos, desejo que apenas eu tenha permissão para editar o texto, mover para a lixeira, restaurar ou excluir permanentemente meus estudos e livros, para que nenhum outro leitor possa adulterar ou apagar minhas pesquisas.

**Why this priority**: Impede que requisições maliciosas ou manipuladas alterem ou destruam dados alheios, garantindo o princípio "Deny by Default".

**Independent Test**: Tentar enviar uma instrução de alteração ou exclusão de um estudo do "Leitor A" a partir de uma sessão do "Leitor B" e confirmar que a ação é terminantemente bloqueada pelo servidor.

**Acceptance Scenarios**:
1. **Given** um estudo pertencente ao "Leitor A", **When** o "Leitor B" tenta modificar o título, localização ou notas desse estudo, **Then** o servidor rejeita sumariamente a operação e nenhuma alteração é gravada.
2. **Given** um livro pertencente ao "Leitor A", **When** o "Leitor B" tenta mover o livro para a lixeira ou restaurá-lo, **Then** o servidor rejeita a ação mantendo o estado original.
3. **Given** um estudo na lixeira do "Leitor A", **When** o "Leitor A" comanda a restauração, **Then** o estudo é restaurado com sucesso para a árvore de leitura do proprietário.

---

### User Story 5 - Proteção Contra Enumeração e Acesso Direto Não Autorizado (IDOR) (Priority: P2)

Como usuário com preocupação sobre a privacidade dos meus estudos, desejo que o sistema não revele se um determinado identificador de estudo ou livro de outro leitor existe quando acessado diretamente, para evitar ataques de varredura ou adivinhação de conteúdos alheios.

**Why this priority**: Aplica as diretrizes internacionais da OWASP contra Insecure Direct Object References (IDOR), protegendo a privacidade dos metadados.

**Independent Test**: Tentar acessar via identificador direto um livro ou estudo pertencente a outro usuário e verificar se o sistema emite resposta segura de "Não Encontrado", idêntica à de um registro que jamais existiu.

**Acceptance Scenarios**:
1. **Given** um estudo privado do "Leitor A", **When** o "Leitor B" tenta acessar diretamente o recurso pelo seu identificador, **Then** o sistema responde com código de recurso não encontrado (HTTP 404), sem confirmar a existência do estudo.
2. **Given** um identificador inexistente no sistema, **When** qualquer usuário tenta acessá-lo, **Then** a resposta é uniforme em relação à tentativa de acesso não autorizado a recurso de terceiro.

---

## Edge Cases

- **Registro com Dependência em Cascata**: O que acontece quando um usuário tenta mover um capítulo para a lixeira contendo estudos vinculados? Todos os estudos descendentes acompanham a exclusão lógica mantendo rigorosamente o vínculo de propriedade.
- **Categorias Compartilhadas vs Pessoais**: O sistema opera em modelo híbrido: categorias fundamentais do sistema são compartilhadas globalmente entre todos os leitores, enquanto novas categorias criadas pelos usuários ficam estritamente restritas ao seu acervo pessoal (`user_id`).
- **Acesso a Recursos Desconhecidos na Migração**: Se houver relacionamentos conceituais entre estudos legados durante a migração, o sistema associa ambos ao proprietário inicial preservando intacta a rede semântica.
- **Tentativas Concorrentes de Atualização**: O mecanismo de controle de concorrência e integridade transacional preserva o estado consistente sem corromper a titularidade do dado.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE atribuir formalmente todos os registros existentes no banco de dados (livros, capítulos, estudos, anotações, relacionamentos, histórico e configurações) a um usuário proprietário inicial durante a migração para o modelo multiusuário.
- **FR-002**: Cada entidade de conteúdo no sistema (livro, estudo, anotação, relação entre estudos, posição espacial e preferência) DEVE possuir obrigatoriamente um identificador de proprietário associado.
- **FR-003**: Todo novo recurso criado no sistema DEVE receber automaticamente o identificador do usuário autenticado como seu proprietário legítimo.
- **FR-004**: Todas as consultas de listagem (acervo de livros, lista de estudos, timeline, dashboard analítico e busca global) DEVEM filtrar estritamente os dados que pertencem ao usuário autenticado.
- **FR-005**: O sistema DEVE bloquear qualquer tentativa de alteração (edição de texto, troca de capítulo, mudança de status de leitura) em recursos cujo proprietário seja diferente do usuário autenticado na requisição.
- **FR-006**: O sistema DEVE restringir o envio para a lixeira (exclusão lógica) e a restauração de itens exclusivamente ao usuário proprietário do recurso.
- **FR-007**: A exclusão definitiva (purga da lixeira) DEVE ser permitida apenas ao usuário proprietário do respectivo item.
- **FR-008**: O sistema DEVE adotar comportamento uniforme de proteção contra enumeração (IDOR), respondendo invariavelmente com status de recurso não encontrado (HTTP 404 Not Found) sempre que um usuário tentar consultar, alterar ou excluir diretamente um identificador pertencente a outro leitor sem permissão expressa.
- **FR-009**: O mecanismo de busca global DEVE indexar e retornar correspondências textuais unicamente dentro do universo de estudos e anotações pertencentes ao usuário que pesquisa.
- **FR-010**: As categorias taxonômicas DEVEM seguir modelo híbrido de visibilidade: o sistema disponibiliza categorias padronizadas globais acessíveis a todos os usuários, permitindo concomitantemente a criação de categorias taxonômicas personalizadas vinculadas com exclusividade ao `user_id` do autor.
- **FR-011**: O primeiro usuário proprietário DEVE ser provisionado de forma automática e determinística durante a migração com identidade canônica soberana (`username: "proprietario"`, nome: "Proprietário do Caderno"), assumindo a posse integral do acervo legado sem exigir intervenção ou configuração manual prévia do usuário.
- **FR-012**: O sistema DEVE garantir que nenhuma migração ou alteração de schema destrua ou desestruture dados do acervo pré-existente.

---

### Key Entities *(include if feature involves data)*

- **Usuário (User)**: Representa a identidade soberana no sistema. Atributos conceituais incluem identificador único, identificador público/nome de exibição, estado da conta e data de registro.
- **Livro (Book)**: Obra pertencente à biblioteca do usuário. Possui identificador, título, autor, metadados e o identificador do seu proprietário legítimo.
- **Estudo (Study)**: Unidade central de fichamento e pesquisa. Contém texto-base, análise em seções, anotações pessoais, localização, status de leitura e o identificador do usuário proprietário.
- **Relação entre Estudos (StudyRelation)**: Elo semântico entre dois estudos. Possui estudo de origem, estudo de destino, tipo de conexão e o identificador do proprietário da relação.
- **Posição Espacial / Canvas (SpatialMapPosition)**: Coordenadas cartesianas dos nós orbitais no mapa radial e no canvas, vinculadas ao usuário proprietário.
- **Registro de Lixeira (TrashEntry)**: Controle de exclusão reversível contendo o recurso original, data de descarte, contagem regressiva para expiração e o identificador do proprietário.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% dos registros do acervo pré-existente são preservados e associados com sucesso ao proprietário inicial após a migração, com taxa de perda de dados de 0%.
- **SC-002**: 100% das operações de criação, leitura, atualização e exclusão (CRUD) validam o identificador de propriedade no servidor, sem exceções de acesso indevido.
- **SC-003**: 0% de vazamento de dados entre usuários distintos: nenhuma consulta de usuário retorna estudos, livros, estatísticas ou notas de outro usuário em testes de isolamento.
- **SC-004**: 100% das tentativas de acesso direto por identificador a recursos de terceiros resultam em bloqueio de acesso padronizado sem vazamento de existência do dado.
- **SC-005**: 100% das suítes de testes automatizados do sistema executam em bancos descartáveis mantendo total compatibilidade e tempo de resposta estável.

---

## Assumptions

- O servidor continuará operando localmente no PC do usuário através do executável ou script de inicialização do projeto.
- Na ausência imediata da tela de login social da Feature 02, a camada de fundação da Feature 01 utiliza um mecanismo de sessão ou identidade local para estabelecer o usuário ativo em cada operação.
- O banco de dados SQLite local no modo WAL é o motor de persistência desta versão, e os modelos de dados são estruturados para permitir futura compatibilidade com bancos cliente-servidor.
- Os dados do usuário ativo permanecem estritamente no dispositivo do proprietário, respeitando a privacidade absoluta exigida pela Constituição do projeto.
