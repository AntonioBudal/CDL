# Feature Specification: Acervo — Visualização, Busca e Ordenação

**Feature Branch**: `005-acervo-busca-ordenacao`  
**Created**: 2026-09-18  
**Status**: Draft  
**Input**: User description: "T04 - Acervo: visualização, busca e ordenação"

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Busca Instantânea e Filtragem de Obras (Priority: P1)

Como leitor com dezenas de livros no acervo pessoal, quero localizar rapidamente uma obra digitando termos parciais de seu título, autor ou subtítulo em um campo de busca proeminente, para que eu não precise navegar ou rolar manualmente pela lista inteira para encontrar o livro que desejo estudar.

**Why this priority**: A localização ágil de conteúdo é o requisito mais frequente e essencial de usabilidade em qualquer biblioteca pessoal à medida que o acervo cresce.

**Independent Test**: Pode ser testado cadastrando três livros fictícios ("A Arte da Guerra", "Memórias Póstumas de Brás Cubas", "Dom Casmurro"), digitando termos no campo de busca (como "guerra", "bras", "machado" ou termos sem acento como "memorias") e confirmando que a tela atualiza imediatamente para exibir apenas as obras correspondentes, indicando a contagem filtrada e oferecendo botão para limpar o filtro.

**Acceptance Scenarios**:

1. **Given** um acervo com múltiplos livros cadastrados, **When** o usuário digita "arte" no campo de busca, **Then** apenas livros contendo "arte" no título, subtítulo ou nome do autor permanecem visíveis, e a contagem exibe "1 livro encontrado".
2. **Given** um livro com caracteres acentuados ("Memórias"), **When** o usuário busca por "memorias" (sem acento) ou "MEMÓRIAS" (em maiúsculas), **Then** o sistema encontra o livro com correspondência insensível a caixa e diacríticos.
3. **Given** um termo de busca que não coincide com nenhum livro existente, **When** a pesquisa é realizada, **Then** o sistema exibe uma mensagem amigável de "Nenhum livro encontrado para esta busca" com um botão/ação clara de "Limpar busca".
4. **Given** um campo de busca preenchido, **When** o usuário clica no botão "✕" (limpar) ou apaga o texto, **Then** todas as obras do acervo voltam a ser exibidas instantaneamente.

---

### User Story 2 - Modos de Visualização: Grade de Capas vs. Lista Compacta (Priority: P2)

Como leitor, quero poder alternar a exibição do meu acervo entre o modo de "Grade com Capas" (foco visual amplo com capas em destaque) e o modo de "Lista Compacta" (foco em densidade de informação com visualização tabular/textual rápida), para adaptar o aplicativo ao meu dispositivo (celular vs. monitor widescreen) e ao tamanho atual da minha biblioteca.

**Why this priority**: Usuários com telas menores ou acervos extensos necessitam de densidade de informação, enquanto leitores que organizam capas apreciam o apelo visual da estante tradicional.

**Independent Test**: Pode ser testado clicando no alternador de visualização na barra do acervo; a exibição deve transicionar imediatamente entre grade e lista mantendo os mesmos links de acesso, os mesmos dados e as mesmas ações, persistindo a preferência escolhida após recarregar a página.

**Acceptance Scenarios**:

1. **Given** o acervo exibido em "Grade de Capas", **When** o usuário clica no botão de "Lista Compacta", **Then** os livros passam a ser exibidos em formato de linhas compactas e alinhadas, com título, autor, ano, indicador de capítulos e miniatura discreta.
2. **Given** o usuário selecionou o modo "Lista Compacta", **When** ele recarrega a página ou fecha e reabre o navegador, **Then** o sistema preserva sua escolha e renderiza diretamente o modo compacto.
3. **Given** um livro sem capa cadastrada visualizado em qualquer um dos dois modos, **When** exibido na tela, **Then** renderiza o marcador tipográfico harmônico padrão sem distorção visual nem quebra de alinhamento entre as linhas/cartões.

---

### User Story 3 - Ordenação Flexível do Acervo (Priority: P3)

Como leitor, quero poder reordenar a exibição das minhas obras por ordem alfabética (A-Z ou Z-A), por data de adição ao acervo (mais recentes primeiro ou mais antigas primeiro) e por data de última atividade/modificação, para encontrar com facilidade leituras em andamento ou localizar títulos em ordem alfabética estrita.

**Why this priority**: Facilita a gestão de acervos consolidados e a continuidade imediata das leituras mais ativas.

**Independent Test**: Pode ser testado alterando o seletor de ordenação e verificando que a sequência dos livros na tela reordena imediatamente de acordo com o critério escolhido, tanto na visualização em grade quanto na visualização em lista.

**Acceptance Scenarios**:

1. **Given** livros cadastrados em ordem aleatória, **When** o usuário escolhe a ordenação "Título (A–Z)", **Then** a lista é rearranjada alfabeticamente ignorando maiúsculas e respeitando acentos da língua portuguesa.
2. **Given** múltiplos livros no acervo, **When** o usuário seleciona a ordenação "Recentemente adicionados", **Then** as obras são exibidas em ordem decrescente pela data de cadastro (`created_at`).
3. **Given** múltiplos livros com diferentes datas de alteração, **When** o usuário escolhe a ordenação "Recentemente modificados", **Then** as obras são exibidas com base na data da última atualização (`updated_at`).
4. **Given** uma ordenação selecionada em conjunto com um termo de busca, **When** novos termos são digitados, **Then** os resultados filtrados mantêm a regra de ordenação ativa de forma previsível.

---

### Edge Cases

- **Títulos e Autores Muito Longos**: Títulos extensos ou sem espaços que poderiam estourar a grade são delimitados com quebras de linha elegantes ou reticências (`line-clamp`), sem sobrepor elementos adjacentes em telas estreitas.
- **Espaços em Branco Supérfluos na Busca**: Termos com múltiplos espaços consecutivos ou espaços no início e fim são normalizados (trimmed) para evitar buscas vazias acidentais.
- **Caracteres Especiais e Diacríticos**: Buscas contendo acentos circunflexos, agudos, til, cedilha ou pontuação (ex.: "À procura", "Conceição", "Sci-Fi") funcionam tanto se o usuário digitar os acentos quanto se digitar letras simples equivalentes.
- **Acervo Vazio vs. Busca Sem Resultados**: O sistema distingue visualmente o estado de "Nenhum livro cadastrado no sistema" (com chamada para cadastrar a primeira obra) do estado de "Nenhum livro corresponde ao filtro atual" (com botão para redefinir a pesquisa sem perder o contexto).
- **Itens na Lixeira**: Obras que foram movidas para a lixeira (soft delete) continuam estritamente ocultas do acervo ativo, da contagem total e dos resultados de busca.
- **Preservação de Foco com Teclado**: Ao usar atalhos ou botões de limpeza de busca, o foco do teclado permanece no campo de texto para permitir nova digitação sem obrigar o uso do mouse ou toque.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE disponibilizar um campo de busca textual em tempo real no cabeçalho/barra superior do acervo de livros.
- **FR-002**: A busca DEVE comparar o termo digitado com o título, autor e subtítulo do livro de maneira case-insensitive (sem distinção de maiúsculas/minúsculas) e sem sensibilidade a acentos (normalização Unicode NFKD).
- **FR-003**: O sistema DEVE exibir de forma destacada a quantidade de resultados encontrados durante uma filtragem (ex.: "Exibindo 3 de 15 livros") e permitir limpar a busca com um único clique ou toque.
- **FR-004**: O sistema DEVE permitir alternar entre pelo menos dois modos de visualização do acervo:
  - **Grade de Capas** (estante visual com capas em proporção 2:3 e destaque visual amplo).
  - **Lista Compacta** (linhas horizontais densas com miniatura discreta, metadados alinhados e ação de clique direto).
- **FR-005**: A escolha do modo de visualização DEVE persistir no armazenamento local do navegador do usuário, convivendo harmonicamente com as preferências de tema, densidade e tamanho de tela.
- **FR-006**: O sistema DEVE disponibilizar opções de ordenação explícitas:
  - Alfabética por Título (A–Z e Z–A).
  - Alfabética por Autor (A–Z).
  - Recentemente adicionados (ordem decrescente da data de cadastro `created_at`).
  - Recentemente modificados (ordem decrescente da data de última atividade `updated_at`).
  - Mais antigos adicionados (ordem crescente de `created_at`).
  - Ano de publicação (quando preenchido, do mais recente ao mais antigo).
- **FR-007**: As operações de busca e ordenação DEVEM ser combináveis entre si e funcionar de forma idêntica tanto no modo Grade quanto no modo Lista Compacta.
- **FR-008**: O sistema NUNCA DEVE exibir livros marcados como excluídos (soft delete / lixeira) nas listagens ativas, buscas ou contagens do acervo.
- **FR-009**: O layout do acervo DEVE ser totalmente responsivo, adaptando a quantidade de colunas da grade e as colunas visíveis da lista conforme a largura da janela (desktop, tablet e celular).
- **FR-010**: A interface DEVE preservar os atalhos e botões para cadastrar novos livros sem que a busca ou a alternância de layout ocultem a funcionalidade de adição.

---

### Key Entities *(include if feature involves data)*

- **Book (Livro)**: Entidade central do acervo. Atributos relevantes para visualização:
  - `id`: Identificador numérico único estável.
  - `title`: Título principal da obra (obrigatório para busca e ordenação alfabética).
  - `subtitle`: Subtítulo descritivo (usado como critério de busca).
  - `author`: Nome do autor ou organizador (usado para busca e ordenação por autor).
  - `year`: Ano de publicação (usado para ordenação cronológica e metadados).
  - `cover_image`: Referência relativa ao arquivo WebP da capa (usado na grade e miniatura da lista).
  - `created_at`: Data e hora de inclusão do livro no sistema.
  - `updated_at`: Data e hora da última modificação do livro.
  - `deleted_at`: Data e hora de envio para a lixeira (nulo para livros ativos).
- **ViewPreferences (Preferências de Visualização do Acervo)**:
  - `mode`: Modo de visualização selecionado (`grid` ou `list`).
  - `sortBy`: Critério de ordenação ativo.
  - `sortOrder`: Sentido da ordenação (`asc` ou `desc`).

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A filtragem em tempo real deve refletir na tela em menos de 100ms a cada caractere digitado para acervos de até 500 livros.
- **SC-002**: A alternância entre o modo Grade e o modo Lista deve ocorrer instantaneamente (menos de 50ms) sem necessidade de novas requisições de rede.
- **SC-003**: 100% dos livros com acentos ou caracteres especiais em títulos e autores devem ser localizáveis através de pesquisas com ou sem acentos (ex.: "Machado de Assis", "Árvore", "Poesia").
- **SC-004**: A preferência de visualização (grade vs. lista) e ordenação selecionada deve permanecer gravada e ativa mesmo após fechar a aba ou recarregar o navegador.
- **SC-005**: 100% das obras presentes na lixeira permanecem invisíveis nas buscas e contagens do acervo ativo.

---

## Assumptions

- O acervo pessoal de estudos é carregado integralmente na página inicial, permitindo busca e ordenação locais no cliente com latência imperceptível e alta reatividade.
- A persistência das preferências de visualização e ordenação pode utilizar o mecanismo existente de preferências de aparência do sistema (`cadernoAppearance` ou `localStorage`), sem exigir chamadas de rede ao backend para salvar o layout do navegador.
- Os campos `created_at` e `updated_at` já existem no modelo de dados de livros e estão disponíveis na API (`BookRead`).
