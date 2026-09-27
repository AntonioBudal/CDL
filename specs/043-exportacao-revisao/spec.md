# Feature Specification: F0.6.4 — Exportação com Destaques e Caderno de Revisão

**Feature Branch**: `043-exportacao-revisao`  
**Created**: 2026-09-27  
**Status**: Draft  
**Input**: User description: "F0.6.4 — Exportação com Destaques e Caderno de Revisão"

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Exportação de Estudo com Destaques e Anotações (Priority: P1) 🎯 MVP

Como leitor ou pesquisador que utiliza editores externos (como Obsidian, Typora ou leitores de e-book), quero exportar meu estudo em formato Markdown ou Texto Puro incluindo todos os destaques, anotações e perguntas cadastrados, para que meu documento exportado preserve o trabalho analítico realizado sem perda das marcações.

**Why this priority**: É o valor imediato que conecta o estudo realizado no Leitorum aos fluxos de trabalho externos do leitor, garantindo que o tempo investido em grifos e anotações seja portável.

**Independent Test**: Abrir um estudo contendo 3 trechos grifados em cores diferentes, 1 anotação e 1 pergunta; abrir o modal "Exportar estudo"; selecionar "Incluir destaques e anotações"; baixar o arquivo Markdown; validar que os trechos grifados e anotações estão representados corretamente no arquivo gerado.

**Acceptance Scenarios**:
1. **Given** um estudo aberto com destaques e anotações, **When** o usuário abre o modal de exportação e seleciona a opção "Incluir destaques e anotações", **Then** o arquivo Markdown gerado incorpora a marcação visual dos grifos e as notas associadas.
2. **Given** o modal de exportação, **When** o usuário mantém desmarcada a opção de destaques, **Then** o arquivo exportado contém o texto original limpo, preservando compatibilidade com o formato existente.
3. **Given** o formato "Texto Puro (.txt)" selecionado com destaques ativos, **When** o usuário faz o download, **Then** os destaques são demarcados com delimitadores textuais legíveis e notas numeradas no rodapé.

---

### User Story 2 - Geração do Caderno de Revisão da Obra ou Estudo (Priority: P1)

Como estudante revisando para exames ou aulas, quero gerar um documento consolidado denominado "Caderno de Revisão" (em nível de estudo ou do livro completo), compilando exclusivamente as perguntas ativas, termos ocluídos e notas marginais organizados por capítulo e seção, para que eu possa revisar os conceitos centrais rapidamente sem ler dezenas de páginas de texto integral.

**Why this priority**: Transforma as interações de retenção ativa (F0.6.2 e F0.6.3) em um artefato tangível de consulta rápida e impressão, multiplicando a utilidade pedagógica da plataforma.

**Independent Test**: No menu de exportação do estudo ou do livro, selecionar a opção "Caderno de Revisão (Digest)"; baixar o documento; verificar a presença de índice, seções organizadas de "Perguntas de Retenção", "Trechos Chave & Oclusões" e "Notas Marginais", com atribuição correta de capítulo e estudo.

**Acceptance Scenarios**:
1. **Given** um livro com 5 estudos contendo perguntas e oclusões distribuídas, **When** o usuário solicita a exportação do "Caderno de Revisão do Livro", **Then** o sistema gera um documento Markdown consolidado estruturado por capítulo e estudo.
2. **Given** um estudo individual, **When** o usuário solicita o "Caderno de Revisão do Estudo", **Then** o documento sintetiza apenas as interações daquele estudo em seções temáticas claras.
3. **Given** um estudo ou livro sem nenhum destaque ou pergunta interativa cadastrada, **When** o Caderno de Revisão é solicitado, **Then** o sistema gera um arquivo informativo indicando a ausência de notas de estudo sem erros operacionais.

---

### User Story 3 - Configuração de Formatação e Modo de Revisão (Priority: P2)

Como leitor preparando material de autoavaliação ou estudo impresso, quero poder escolher se o Caderno de Revisão deve ser exportado com gabarito no final ("Modo Exercício") ou com respostas expostas no fluxo ("Modo Estudo"), para que eu possa testar meus conhecimentos no papel sem ver as respostas antecipadamente.

**Why this priority**: Permite que o leitor utilize o Caderno de Revisão para estudo ativo em papel ou em dispositivos sem distração (ex.: e-readers e fichas impressas).

**Independent Test**: Exportar o Caderno de Revisão selecionando "Modo Exercício" e verificar que as respostas das perguntas e termos ocluídos aparecem suprimidos no corpo com linhas de preenchimento, e as respostas corretas estão reunidas em um apêndice de gabarito no final do documento.

**Acceptance Scenarios**:
1. **Given** a exportação do Caderno de Revisão configurada para "Modo Exercício", **When** o arquivo é gerado, **Then** as perguntas exibem linhas de resposta em branco e as respostas constam no Gabarito Final.
2. **Given** a exportação configurada para "Modo Estudo", **When** o arquivo é gerado, **Then** cada pergunta ou oclusão traz sua respectiva resposta logo abaixo do enunciado.

---

### User Story 4 - Exportação Confiável em Estudos Compartilhados (Priority: P3)

Como leitor convidado com permissão somente leitura em um estudo ou livro compartilhado por outro usuário, quero poder exportar o estudo com os destaques e o Caderno de Revisão autorizado, para que eu possa estudar o material compartilhado sem necessidade de privilégios administrativos.

**Why this priority**: Garante que o ecossistema colaborativo do Leitorum permita aos alunos ou membros de grupos de estudos colherem os frutos do estudo conjunto.

**Independent Test**: Acessar um estudo com conta de convidado (`canEdit = false`), abrir o modal de exportação, gerar o Caderno de Revisão e confirmar o recebimento do arquivo completo e sem vazamento de dados privados.

**Acceptance Scenarios**:
1. **Given** um usuário visualizando um estudo compartilhado em modo somente leitura, **When** ele aciona a exportação com destaques ou o Caderno de Revisão, **Then** o download é processado com sucesso.
2. **Given** a exportação de um estudo compartilhado, **When** o arquivo é baixado, **Then** os metadados do cabeçalho identificam a autoria original do proprietário da obra.

---

### Edge Cases

- **Estudo ou Livro sem destaques cadastrados**: Ao escolher a opção de exportação com destaques ou Caderno de Revisão, o sistema emite documento válido com mensagem explicativa ("Este estudo não possui destaques ou notas registradas."), evitando downloads vazios ou mensagens crípticas.
- **Destaques com quebras de linha e caracteres especiais**: Citações, perguntas ou respostas contendo aspas, símbolos matemáticos ou caracteres de controle são devidamente escapados para não corromper a sintaxe do Markdown gerado.
- **Livros com grande volume de estudos (mais de 50 estudos)**: A geração do Caderno de Revisão consolidado do livro processa a busca relacional de forma indexada sem causar lentidão ou estouro de memória no servidor.
- **Exportação em dispositivos móveis**: O modal de exportação ajusta os seletores de opções para botões táteis de no mínimo $44 \times 44\text{px}$, permitindo download direto no navegador do smartphone ou tablet.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE estender o modal de exportação (`ExportModal.vue`) com a opção de incluir ou excluir destaques e anotações nos formatos Markdown (`.md`) e Texto Puro (`.txt`).
- **FR-002**: O sistema DEVE adicionar uma nova modalidade de exportação: "Caderno de Revisão (Digest)", disponível tanto no escopo de estudo individual quanto no escopo de livro completo.
- **FR-003**: Na exportação de estudo com destaques em Markdown, o sistema DEVE representar os destaques por marcas de realce (`==texto==` ou `<mark>texto</mark>`) no fluxo textual e vincular as anotações e perguntas correspondentes através de notas de rodapé padrão Markdown (`[^1]: Nota...`) posicionadas no final de cada seção.
- **FR-004**: No Caderno de Revisão, o sistema DEVE agrupar os elementos interativos por Capítulo e Estudo, organizados nas categorias: "Perguntas de Retenção", "Trechos Ocluídos" e "Notas Marginais & Citações".
- **FR-005**: O sistema DEVE suportar a configuração de exibição de respostas no Caderno de Revisão através do Modo Exercício (onde os termos ocluídos e respostas são substituídos por linhas de preenchimento `_______` e compilados em uma seção dedicada de "Gabarito de Revisão" no final do documento) e Modo Estudo (respostas exibidas diretamente abaixo de cada pergunta).
- **FR-006**: Na exportação de livro completo, o Caderno de Revisão DEVE incluir sumário inicial com links internos para os capítulos e estudos correspondentes.
- **FR-007**: A exportação NÃO DEVE alterar o conteúdo salvo no banco de dados e deve preservar a integridade estrita do texto Markdown original do acervo.
- **FR-008**: O endpoint de exportação DEVE aceitar parâmetros de consulta (`include_highlights: bool`, `format_type: 'full' | 'digest'`, `exercise_mode: bool`) e validar autorização de leitura para o usuário requisitante.
- **FR-009**: O arquivo exportado DEVE conter metadados no topo (título da obra, capítulo, autor/proprietário, data de geração e estatísticas de destaques e perguntas).
- **FR-010**: A interface do modal de exportação DEVE manter conformidade com os 10 temas visuais do Leitorum e padrões de acessibilidade WCAG AA.

---

### Key Entities

- **Opções de Exportação de Estudo**: Parâmetros de configuração selecionados no modal pelo leitor (`scope: 'study' | 'book'`, `format: 'markdown' | 'text'`, `include_highlights: boolean`, `type: 'full' | 'digest'`, `exercise_mode: boolean`).
- **Caderno de Revisão (Digest)**: Estrutura compilada em memória contendo o sumário executivo, metadados da obra e agrupamento hierárquico de perguntas ativas, termos ocluídos, citações e notas marginais.
- **Metadados de Exportação**: Bloco YAML frontmatter ou cabeçalho textual informando título, capítulo, proprietário, data/hora e totalizadores de estudo ativo.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: O download do estudo com destaques ou do Caderno de Revisão inicia em menos de 1 segundo para estudos individuais e menos de 3 segundos para livros completos com mais de 20 estudos.
- **SC-002**: 100% dos destaques, anotações e perguntas cadastrados na base de dados do estudo são integrados com exatidão ao arquivo exportado quando a opção estiver ativada.
- **SC-003**: O arquivo Markdown exportado é 100% compatível com as especificações CommonMark / GFM, renderizando sem quebras de layout em ferramentas externas como Obsidian, VS Code e Typora.
- **SC-004**: Usuários convidados com acesso somente leitura conseguem exportar o Caderno de Revisão sem falhas de autenticação e com isolamento total dos dados privados de outros usuários.
- **SC-005**: Zero perda ou modificação acidental do Markdown original do estudo ou dos registros relacionais no SQLite em decorrência da exportação.

---

## Assumptions

- O modelo relacional de destaques (`study_highlights`) das features F0.6.1 a F0.6.3 fornece os dados estruturados de cor, tipo (`highlight`, `note`, `quote`, `hidden`, `question`), posição e anotação necessários para a exportação.
- A exportação é uma operação de leitura estrita e sob demanda, gerando respostas HTTP do tipo `Content-Disposition: attachment` para download direto no navegador do usuário.
- O editor do leitor preserva os títulos e estrutura das 4 seções de análise (`summary`, `explanation`, `concepts`, `references`).
