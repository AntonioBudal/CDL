# Feature Specification: F08 — Busca Global Contextual

**Feature Branch**: `025-busca-global-contextual`  
**Created**: 2026-09-19  
**Status**: Draft  
**Input**: User description: "F08 — Busca Global Contextual (indexação transversal de estudos, notas e conceitos com realce de termos e navegação direta)"

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Busca Transversal Instantânea e Navegação com Contexto (Priority: P1) [MVP]

Como leitor do Caderno, desejo acionar a busca a partir de qualquer tela da aplicação e digitar um termo ou conceito para localizar rapidamente todos os estudos e notas onde ele aparece, visualizando trechos de contexto destacados e podendo navegar com um clique para a leitura exata do estudo.

**Why this priority**: É o valor essencial da funcionalidade. Elimina a necessidade de abrir livro por livro e capítulo por capítulo para recordar onde determinado conceito ou citação foi registrado, proporcionando acesso direto ao conhecimento catalogado.

**Independent Test**:
Acessar qualquer tela da aplicação; acionar a busca global; digitar um termo presente em estudos de múltiplos livros; constatar os resultados agrupados ou identificados por obra/capítulo com trechos (*snippets*) destacando o termo; clicar em um resultado e constatar a navegação direta para a tela do estudo com o conteúdo em foco e destacado.

**Acceptance Scenarios**:
1. **Given** que o leitor possui estudos cadastrados em diferentes livros contendo o termo "dialética", **When** aciona a busca global e digita "dialética", **Then** a aplicação exibe a lista de estudos correspondentes com o título do estudo, o nome do livro, o capítulo e um trecho de contexto com o termo realçado.
2. **Given** que a lista de resultados está visível, **When** o leitor clica em um resultado, **Then** o modal de busca se fecha e a aplicação navega diretamente para a visualização do livro e capítulo correspondentes, posicionando o estudo na tela com destaque visual temporário.
3. **Given** que o leitor digita um termo com menos de 2 caracteres, **When** o campo de busca recebe entrada, **Then** a busca não dispara consultas desnecessárias e exibe uma orientação amigável solicitando no mínimo 2 caracteres.
4. **Given** que um estudo ou livro está na lixeira (marcado como excluído), **When** o leitor realiza uma busca por termos contidos nesse item, **Then** o item excluído NUNCA aparece entre os resultados da busca ativa.

---

### User Story 2 - Filtragem Contextual por Obra e Categoria Taxonômica (Priority: P2)

Como leitor com um acervo amplo e diversificado, desejo restringir os resultados da busca a um livro específico ou a uma categoria temática da taxonomia, para encontrar rapidamente referências pertinentes dentro de um domínio de estudo delimitado.

**Why this priority**: À medida que o acervo cresce, termos recorrentes (ex.: "método", "verdade", "estrutura") podem retornar dezenas de resultados. Os filtros reduzem o ruído e aceleram a localização em tópicos específicos.

**Independent Test**:
Realizar uma busca ampla que retorne estudos de múltiplos livros; aplicar o filtro de uma obra ou categoria taxonômica; constatar que a lista de resultados passa a exibir exclusivamente estudos associados ao filtro selecionado, preservando os trechos destacados.

**Acceptance Scenarios**:
1. **Given** uma busca ativa com múltiplos resultados, **When** o leitor seleciona um livro específico no seletor de filtros, **Then** a lista é imediatamente atualizada para exibir apenas os estudos daquele livro.
2. **Given** uma busca ativa, **When** o leitor seleciona uma categoria taxonômica no filtro, **Then** são exibidos apenas os estudos associados a essa categoria ou cujos livros pertençam a ela.
3. **Given** filtros aplicados, **When** o leitor clica em "Limpar filtros", **Then** a listagem volta a exibir todas as correspondências do termo pesquisado no acervo completo.

---

### User Story 3 - Histórico Recente de Pesquisas Persistido e Preparado para Sincronização (Priority: P3)

Como leitor que pesquisa temas recorrentes durante sessões de estudo em múltiplos dispositivos, desejo visualizar minhas pesquisas recentes ao abrir o campo de busca, com persistência centralizada para retomar tópicos explorados em qualquer tela ou dispositivo conectado.

**Why this priority**: Reduz o esforço cognitivo e de digitação, permitindo alternar rapidamente entre investigações paralelas e temas de estudo em andamento, mantendo o histórico pronto para sincronização em nuvem futura.

**Independent Test**:
Executar duas ou mais buscas com termos distintos; acessar a busca a partir de outra aba ou dispositivo conectado ao mesmo servidor; constatar os termos recentes sincronizados; clicar em um termo do histórico e constatar a reexecução instantânea da busca; excluir um item do histórico e constatar a remoção imediata.

**Acceptance Scenarios**:
1. **Given** que o leitor já realizou buscas anteriores, **When** abre o painel de busca com o campo de texto vazio, **Then** são exibidos os termos pesquisados mais recentemente (até 10 itens) sincronizados no backend.
2. **Given** a lista de buscas recentes visível, **When** o leitor clica em um termo do histórico, **Then** o termo é inserido no campo de busca e a pesquisa é executada imediatamente.
3. **Given** itens no histórico de busca, **When** o leitor clica no botão de remoção de um item específico ou em "Limpar histórico", **Then** o histórico é atualizado atomicamente no banco de dados e refletido na interface.

---

### User Story 4 - Ergonomia Móvel, Acessibilidade e Navegação Ágil por Teclado (Priority: P4)

Como leitor utilizando celular, tablet ou computador, desejo que a interface de busca seja ergonomicamente adaptada ao meu dispositivo, com suporte a atalhos rápidos de teclado, fechamento intuitivo e alvos táteis confortáveis.

**Why this priority**: Garante conforto de uso tanto em sessões de leitura profunda no computador quanto em consultas rápidas em dispositivos móveis, sem fricção ergonômica.

**Independent Test**:
Emular tela móvel (<768px) e verificar a abertura em tela cheia com alvos táteis ≥ 44x44px; em computador, verificar abertura rápida por atalho, foco automático no campo de digitação, navegação de resultados via setas do teclado e fechamento via tecla Esc.

**Acceptance Scenarios**:
1. **Given** que o leitor está em um computador, **When** aciona a busca, **Then** o campo de digitação recebe foco imediato, permitindo iniciar a digitação sem clique adicional do mouse.
2. **Given** que o painel de busca está aberto, **When** o leitor pressiona a tecla Esc ou clica fora da área modal, **Then** a busca é fechada e o foco retorna ao elemento que a disparou.
3. **Given** um dispositivo móvel com tela estreita, **When** a busca é acionada, **Then** ela ocupa a tela inteira com espaçamento tátil adequado (mínimo de 44x44px para botões e itens selecionáveis) e contenção rigorosa contra overflow horizontal.

---

### Edge Cases

- **Termos com caracteres acentuados ou variações ortográficas**: A busca deve encontrar correspondências com ou sem acentuação (ex.: buscar "filosofia", "lógica", "análise" deve funcionar independentemente da forma acentuada exata utilizada na consulta).
- **Consultas sem nenhum resultado**: Quando nenhum estudo corresponder ao termo pesquisado, a interface deve apresentar um estado vazio amigável, sugerindo termos alternativos, verificação da ortografia ou busca com disjunção (OR), sem mensagens técnicas.
- **Trechos longos de texto**: Quando o match ocorrer em campos com textos volumosos (ex.: explicações de múltiplos parágrafos), o fragmento (*snippet*) deve recortar aproximadamente 120 a 160 caracteres ao redor da palavra encontrada, com reticências nas extremidades para manter a leitura limpa.
- **Exclusão de registros em lixeira**: Registros com exclusão lógica (*soft delete*) em qualquer nível (estudo ou livro excluído) são estritamente excluídos dos resultados e dos cálculos de contagem.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE disponibilizar um ponto de acesso global visível e intuitivo à busca em todas as telas da aplicação.
- **FR-002**: O sistema DEVE indexar e pesquisar nos campos textuais fundamentais dos estudos: título, anotações pessoais, resumo, explicação, conceitos e referências.
- **FR-003**: O escopo dos resultados DEVE focar primariamente nos estudos (onde reside o conteúdo analítico e o fichamento), apresentando em cada card de resultado a trilha contextual completa da obra (Livro > Capítulo > Estudo) com atalho de 1 clique para navegação direta ao estudo. Correspondências que coincidam com títulos de livros e capítulos são integradas como contexto associado aos seus respectivos estudos.
- **FR-004**: O sistema DEVE gerar fragmentos de contexto legíveis (*snippets*) com a palavra ou termo pesquisado destacado visualmente de forma acessível.
- **FR-005**: Em pesquisas compostas por múltiplas palavras, o sistema DEVE adotar por padrão a conjunção estrita (operador lógico AND), exigindo que todos os termos pesquisados estejam presentes no estudo (mesmo que em campos analíticos distintos). Caso nenhum resultado seja localizado com todos os termos, o sistema DEVE oferecer uma alternativa imediata e assistida para buscar por "qualquer um dos termos" (operador lógico OR).
- **FR-006**: Ao selecionar um resultado de estudo, o sistema DEVE navegar para a respectiva obra e posicionar o leitor diretamente no estudo selecionado com sinalização visual temporária.
- **FR-007**: O sistema DEVE permitir filtrar os resultados por livro específico ou por categoria taxonômica do acervo.
- **FR-008**: O sistema DEVE ignorar e filtrar estritamente qualquer registro que se encontre na lixeira (*soft delete* ativo), tanto no livro quanto no estudo.
- **FR-009**: O histórico de buscas recentes DEVE ser persistido estruturadamente no backend (banco de dados) com timestamp e suporte a exclusão atômica (remover item individual ou limpar histórico), assegurando sincronismo entre dispositivos na rede local e prontidão de schema para futura sincronização com conta em nuvem (ex.: Google). O sistema mantém até os 10 termos mais recentes em ordem cronológica decrescente.
- **FR-010**: O sistema DEVE oferecer suporte pleno à acessibilidade, incluindo foco automático, fechamento via tecla Esc, anúncios de quantidade de resultados para tecnologias assistivas e alvos de toque de no mínimo 44x44px.

---

### Key Entities *(include if feature involves data)*

- **Consulta de Busca (Search Query)**: Termo textual digitado pelo leitor (mínimo de 2 caracteres), acompanhado de modalidade de combinação (AND padrão / OR assistido) e filtros opcionais de livro ou categoria taxonômica.
- **Item de Resultado (Search Match)**: Representação sintetizada do estudo encontrado contendo identificador do estudo, título, identificador da obra, título do livro, capítulo correspondente, campo onde ocorreu a correspondência e fragmento de texto contextual com o termo realçado.
- **Histórico de Buscas (Search History)**: Entidade persistida no banco de dados com termo pesquisado, data/hora de execução (`created_at`), retenção dos últimos 10 termos e controle para exclusão unitária ou limpeza completa.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: O leitor consegue acionar a busca, digitar um termo e visualizar os primeiros resultados em menos de 1 segundo a partir da digitação.
- **SC-002**: Ao clicar em qualquer resultado, o leitor é transportado para o conteúdo exato do estudo em foco com exatamente 1 clique.
- **SC-003**: 100% dos estudos contendo o termo pesquisado em títulos, anotações, resumos, conceitos, explicações ou referências são localizados com precisão.
- **SC-004**: 0% de itens excluídos (*soft deleted*) aparecem nos resultados de busca sob qualquer cenário.
- **SC-005**: O histórico de buscas recentes é atualizado e refletido uniformemente em qualquer dispositivo conectado ao servidor local em menos de 500ms.
- **SC-006**: A interface de busca em dispositivos móveis (< 768px) apresenta zero rolagem horizontal indesejada e todos os elementos interativos possuem área de toque de no mínimo 44x44px.

---

## Assumptions

- O leitor utiliza o Caderno como ferramenta pessoal e local de estudos, necessitando de busca rápida e precisa sem dependência de serviços ou índices externos na nuvem.
- A persistência do histórico no backend prepara estruturalmente a base de dados para futuras sincronizações com nuvem (ex.: conta Google) sem retrabalho de modelo.
- A busca é puramente textual/lexical, priorizando precisão de termos e conceitos catalogados, sem geração de texto sintético ou dependência de inteligência artificial em tempo de execução.
- O volume típico do acervo pessoal varia de centenas a dezenas de milhares de estudos, onde algoritmos de busca e indexação local devem operar com latência imperceptível.
- O acervo do leitor é estritamente confidencial; nenhuma consulta ou conteúdo de resultado é transmitido externamente.
