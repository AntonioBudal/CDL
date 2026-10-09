# Feature Specification: F0.7.15 — Templates Estruturados de Estudo

**Feature Branch**: `064-templates-estudo`

**Created**: 2026-10-10

**Status**: Draft

**Input**: User description: "F0.7.15 — Templates Estruturados de Estudo"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Seleção de Template na Criação e Prévia de Roteiro (Priority: P1) [MVP]

Ao criar um novo estudo em um livro ou capítulo, o leitor pode escolher entre 5 modelos canônicos de análise através de um seletor sutil no editor ou modal de prévia:
1. **Fichamento Clássico** (Resumo Geral, Explicação/Desenvolvimento, Conceitos-Chave, Citações e Referências).
2. **Estudo de Conceito** (Definição Essencial, Etimologia e Origem, Aplicações Práticas, Contrapontos e Limites).
3. **Reconstrução de Argumento** (Tese Central, Premissas e Evidências, Objeções Possíveis, Conclusão Dialética).
4. **Análise Comparativa** (Obra/Autor A vs Obra/Autor B, Pontos de Convergência, Pontos de Divergência, Síntese Crítica).
5. **Resenha Crítica** (Contexto Histórico e Autor, Julgamento e Mérito, Limitações da Tese, Posicionamento do Leitor).

Ao selecionar um template, o editor exibe uma prévia do roteiro explicativo e, ao confirmar, injeta o esqueleto com cabeçalhos e prompts em Markdown nas quatro seções canônicas (`summary`, `explanation`, `concepts`, `references`).

**Why this priority**: É o valor central da funcionalidade: guiar a mente do leitor em diferentes tipos de investigação intelectual, eliminando a paralisia da página em branco sem quebrar a estrutura canônica de 4 campos do Leitorum.

**Independent Test**: Criar um novo estudo selecionando "Estudo de Conceito", verificar a injeção do roteiro Markdown adequado nas seções e salvar com sucesso com o metadado `template_id = 'conceito'`.

**Acceptance Scenarios**:

1. **Given** o formulário de criação de estudo aberto, **When** o usuário escolhe um template no seletor, **Then** o sistema exibe a prévia da proposta e, ao confirmar, preenche os campos com os esqueletos correspondentes.
2. **Given** um formulário vazio com o template "Fichamento Clássico" por padrão, **When** o usuário troca para "Reconstrução de Argumento", **Then** os campos são atualizados sem erros e com a estrutura correspondente.

---

### User Story 2 - Troca Segura de Template com Proteção de Conteúdo Existente (Priority: P2)

O leitor pode alternar ou redefinir o template durante a edição de um estudo em andamento. Caso os campos já contenham anotações ou textos digitados, o sistema aciona uma salvaguarda para evitar perda acidental de dados, exigindo confirmação explícita antes de qualquer alteração destrutiva ou oferecendo preservação das anotações existentes.

**Why this priority**: Protege o trabalho intelectual do leitor, impedindo que experimentos visuais ou mudanças de rota analítica apaguem textos já escritos.

**Independent Test**: Preencher a seção "Resumo" com um parágrafo longo, tentar trocar o template para "Análise Comparativa" e verificar se a interface bloqueia a perda silenciosa com diálogo de confirmação claro.

**Acceptance Scenarios**:

1. **Given** um estudo com texto em uma ou mais seções, **When** o usuário tenta trocar o template de análise, **Then** o sistema apresenta confirmação informando os impactos antes de alterar os campos.
2. **Given** o diálogo de confirmação exibido, **When** o usuário clica em cancelar, **Then** o texto original e o template anterior permanecem intactos.

---

### User Story 3 - Visualização Contextual e Persistência Retrocompatível (Priority: P3)

O estudo salvo exibe na visualização (`StudyView`) uma indicação discreta do modelo analítico utilizado (ex.: badge ou indicador sutil "Estudo de Conceito"), auxiliando na identificação visual rápida na árvore e no leitor. Estudos criados anteriormente (versões 0.1 a 0.6) que não possuem `template_id` continuam perfeitamente funcionais com comportamento padrão "Fichamento Clássico".

**Why this priority**: Permite que o leitor reconheça imediatamente o método de análise empregado ao reler seus estudos meses depois, mantendo 100% de integridade com o acervo existente.

**Independent Test**: Abrir um estudo antigo sem `template_id` (nulo) e verificar se renderiza normalmente sem quebras; criar um novo com "Resenha Crítica" e verificar se exibe a identificação do modelo no cabeçalho do estudo.

**Acceptance Scenarios**:

1. **Given** um estudo criado com `template_id = 'resenha'`, **When** visualizado em `StudyView`, **Then** o cabeçalho do estudo identifica de forma discreta o tipo de fichamento.
2. **Given** um estudo legado com `template_id = null`, **When** aberto no editor ou no leitor, **Then** o sistema trata-o com o fallback padrão de "Fichamento Clássico" sem exigir migrações de conteúdo.

---

### Edge Cases

- O que acontece se o usuário selecionar um template, digitar anotações e tentar trocar de template? O sistema apresenta um diálogo de confirmação com opções explícitas de "Substituir Conteúdo" (sobrescreve os campos com o novo esqueleto) ou "Anexar ao Final" (concatena o novo esqueleto ao final do texto existente sem perda de dados), além da opção de cancelar.
- O que acontece quando o usuário promove uma captura do Inbox (F0.7.13) para estudo? O formulário de promoção inicia configurado por padrão com o template "Fichamento Clássico" para manter o fluxo rápido e sem atrito, permitindo a alteração livre para qualquer outro modelo através do seletor no editor.
- O que acontece se um estudo for importado ou exportado em Markdown/JSON? O `template_id` deve ser preservado como metadado opcional.
- O que acontece em dispositivos móveis com tela pequena? O seletor de template deve ser acessível via diálogo/gaveta touch com alvos de toque $\ge 44 \times 44$px e prévias legíveis.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE disponibilizar 5 templates canônicos fixos de análise: `classico` (Fichamento Clássico), `conceito` (Estudo de Conceito), `argumento` (Reconstrução de Argumento), `comparativo` (Análise Comparativa) e `resenha` (Resenha Crítica).
- **FR-002**: Cada template DEVE mapear seus tópicos e prompts analíticos exclusivamente nas 4 seções fundamentais do Leitorum (`summary`, `explanation`, `concepts`, `references`), preservando a arquitetura de dados e de indexação.
- **FR-003**: O editor de estudos DEVE fornecer um seletor visual e ergonômico de templates com descrição do objetivo de cada modelo e prévia do roteiro antes da aplicação.
- **FR-004**: Ao aplicar um template em um formulário vazio, o sistema DEVE preencher os esqueletos estruturados em Markdown nas seções correspondentes.
- **FR-005**: Ao tentar trocar de template em um estudo que já possui texto em qualquer das 4 seções, o sistema DEVE exibir diálogo de confirmação oferecendo a escolha entre "Substituir Conteúdo" e "Anexar ao Final", prevenindo perda inadvertida de anotações.
- **FR-006**: O fluxo de promoção de capturas do Inbox DEVE iniciar com o template `classico` por padrão, permitindo alteração livre do modelo no editor de estudos.
- **FR-007**: A entidade `Study` no banco de dados DEVE suportar a persistência do campo opcional `template_id` (com valor padrão `'classico'`).
- **FR-008**: As rotas de API `POST /api/studies` e `PUT /api/studies/{id}` DEVEM aceitar e retornar `template_id`.
- **FR-009**: Todos os estudos pré-existentes sem `template_id` DEVEM operar com fallback transparente para `'classico'`, sem quebras ou migrações forçadas de texto.
- **FR-010**: A interface DEVE garantir alvos táteis mínimos de $44 \times 44$px para mobile e suporte completo a navegação por teclado (`Tab`, `Enter`, `Esc`).

### Key Entities

- **StudyTemplate**: Catálogo de modelo mental composto por identificador (`id`), título amigável, descrição do propósito analítico, e esqueletos estruturados em Markdown para as 4 seções (`summary`, `explanation`, `concepts`, `references`).
- **Study**: Entidade principal de estudo, enriquecida com o metadado opcional `template_id` indicando o modelo analítico estruturador.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: O leitor consegue selecionar qualquer um dos 5 templates e ter os esqueletos analíticos carregados no formulário em menos de 2 cliques ou toques.
- **SC-002**: 100% dos estudos legados mantêm funcionamento íntegro, sem nenhuma regressão de leitura, edição ou busca após a introdução da coluna `template_id`.
- **SC-003**: 0% de perda acidental de dados relatada em trocas de templates graças à proteção de confirmação de alteração.
- **SC-004**: 100% de conformidade visual sem emojis, com suporte aos 10 temas oficiais e alvos táteis $\ge 44 \times 44$px no mobile.

---

## Assumptions

- Os 5 templates canônicos definidos no Roadmap 0.7 atendem à totalidade das necessidades de modelagem analítica da versão 0.7; a criação de templates customizados pelo usuário é expressamente fora de escopo (evitando construtores genéricos de formulários).
- Todos os roteiros injetados são redigidos em Markdown puro e editáveis livremente pelo leitor após a aplicação.
- A persistência de `template_id` utiliza coluna textual (`VARCHAR(30)`) com fallback seguro no modelo.
