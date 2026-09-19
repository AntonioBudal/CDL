# Feature Specification: Correção de Roteamento, Fonte Global e Limpeza de Ajustes

**Feature Branch**: `012-roteamento-fonte-ajustes`  
**Created**: 2026-09-19  
**Status**: Ready for Planning  
**Input**: User description:
> # Spec: Correção de Roteamento, Fonte Global e Limpeza de Ajustes
> 
> ## 1. Correção de Navegação (Bug da tela vazia)
> **Problema:** Mudar de aba deixa a tela vazia, forçando o usuário a dar F5 para renderizar o conteúdo.
> **Solução:** Corrija a reatividade de estado no Vue Router. Certifique-se de que o `<RouterView>` reage à mudança (ex: adicionando `:key="$route.fullPath"`) ou verifique se os hooks de ciclo de vida (`onMounted` vs `watch` na rota) estão buscando/atualizando os dados corretamente na navegação client-side.
> 
> ## 2. Aplicação Global da Fonte
> **Problema:** A alteração de fonte só afeta a área de texto, não dando preview imediato na interface.
> **Solução:** Eleve a variável CSS de fonte (ex: `--font-family-base` ou `--font-family-reading`) para o `<body>` ou `#app`. Toda a interface do sistema — incluindo a própria tela de Ajustes, botões, inputs e menus — deve herdar essa fonte instantaneamente.
> 
> ## 3. Limpeza do Painel de Ajustes (Redução de Escopo)
> **Problema:** O painel está poluído com 11 opções, e a introdução das Superclasses criou sobreposições de responsabilidade.
> **Solução:** Exclua as seguintes opções do painel (e limpe seus respectivos estados na store):
> * **Remover "5. Movimento (Transições)":** Essa função foi 100% absorvida pela opção "11. Superclasse" e seu controle de "Intensidade da física".
> * **Remover "7. Botões (Largura/Preenchimento)":** A geometria, o formato e o comportamento tátil dos botões agora são domínio exclusivo do CSS da Superclasse.
> * **Remover "8. Abas (Navegação do estudo)":** Simplifique a interface removendo controles de abas redundantes; deixe a Superclasse ditar a estética da navegação.
> 
> **Ação final:** Renumere as opções restantes (Cor de destaque, Densidade, Leitura, Marcação, Acervo, Largura da interface e Superclasse) de forma sequencial e limpa.

---

## Clarifications

### Session 2026-09-19
- Q: Ao aplicar a fonte selecionada a toda a interface, como devem se comportar os blocos de código e o texto técnico pré-formatado? → A: Opção B — Forçar a fonte selecionada de forma irrestrita em 100% dos elementos da página, inclusive sobrepondo blocos de código e textos pré-formatados.
- Q: Ao carregar a aplicação em navegadores que já possuem preferências salvas com as chaves obsoletas (`motion`, `button-width`, `tabs`), como o sistema deve tratar esses dados no `localStorage`? → A: Opção A — Purgar automaticamente as chaves obsoletas do `localStorage` na inicialização, persistindo apenas o objeto higienizado com as opções ativas.
- Q: Qual granularidade de chave de rota deve ser utilizada no `<component :is="Component">` dentro do `<RouterView>`? → A: Opção A — Usar `:key="$route.fullPath"`, remontando de forma reativa e atômica a cada mudança de caminho ou parâmetro de consulta (`?chapter=...`).

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Navegação Fluida e Confiável sem Telas Vazias (Priority: P1) 🎯 MVP

Como leitor navegando entre o acervo de livros, visualização de livro, leitura de estudos, importação, lixeira e configurações, quero transitar livremente pelas rotas e abas da interface sem que a tela fique em branco ou bloqueie a renderização, eliminando qualquer necessidade de atualizar manualmente a página (F5).

**Why this priority**: A navegação primária quebrada compromete a usabilidade básica de todo o aplicativo. Garantir que as rotas se renderizem de forma reativa e atômica é o alicerce indispensável para as melhorias de experiência visual.

**Independent Test**: Pode ser testado navegando sequencialmente entre Meus Livros (`/`), Detalhe de Livro (`/livros/:id`), Leitura de Estudo (`/livros/:bookId/estudos/:studyId`), Importar (`/importar`), Lixeira (`/lixeira`) e Ajustes (`/ajustes`) usando a barra de navegação superior e links internos, comprovando que cada tela renderiza seu conteúdo instantaneamente em 100% das transições client-side sem telas brancas.

**Acceptance Scenarios**:
1. **Given** o usuário em qualquer tela do sistema, **When** clica em um link de navegação ou botão de rota (ex.: "Ajustes", "Meus livros", "Importar"), **Then** a nova rota é montada e renderizada de forma previsível com animação de transição fluida, sem deixar o elemento `<main>` vazio.
2. **Given** o usuário navegando entre diferentes livros ou estudos em sequência, **When** o parâmetro de rota muda, **Then** o componente de destino é recarregado e inicializado com os dados correspondentes à rota atualizada.
3. **Given** componentes de visualização sob `<Transition mode="out-in">`, **When** ocorre a transição de rota, **Then** cada visualização possui um elemento raiz único e chave de rota unívoca (`:key="$route.fullPath"`), evitando falhas de animação ou cancelamento silencioso de montagem.

---

### User Story 2 - Herança Global e Preview Imediato da Tipografia Escolhida (Priority: P2)

Como usuário personalizando a tipografia do caderno nos Ajustes, quero que a fonte selecionada seja aplicada imediatamente a toda a interface — incluindo títulos, menus, botões, campos de entrada, cartões e o próprio painel de Ajustes —, para que eu tenha um preview fidedigno e uma experiência tipográfica coesa em todo o sistema.

**Why this priority**: O catálogo conta com 24 famílias tipográficas completas, mas o usuário não percebia o impacto da sua escolha na interface global nem obtinha feedback imediato na tela de configuração.

**Independent Test**: Pode ser testado abrindo a tela de Ajustes, selecionando diferentes famílias tipográficas no seletor de fontes e verificando que a tipografia de toda a página (cabeçalho, botões, inputs, legendas e textos) é atualizada instantaneamente sem necessidade de recarregar.

**Acceptance Scenarios**:
1. **Given** a tela de Ajustes aberta, **When** o usuário altera a fonte de leitura para qualquer família tipográfica do catálogo, **Then** a variável de fonte da interface é atualizada em tempo real no elemento raiz/aplicação (`:root`, `body`, `#app`), refletindo a escolha em todos os botões, menus e textos da tela.
2. **Given** o usuário navegando por qualquer página da aplicação (acervo, livro, leitura, lixeira), **When** a fonte foi definida nas preferências, **Then** a identidade tipográfica é consistente entre a casca da interface e as áreas de conteúdo.
3. **Given** a seleção de fontes com serifa, sem serifa ou monoespaçadas, **When** aplicada à interface, **Then** botões, campos de formulário e elementos numéricos preservam alinhamento e legibilidade sem quebras de layout.

---

### User Story 3 - Poda de Ajustes Redundantes e Renumeração Sequencial Limpa (Priority: P3)

Como usuário acessando as preferências de aparência, quero uma lista concisa e bem organizada de opções, sem controles obsoletos cujas funções já foram incorporadas pelas Superclasses de Interface, com numeração sequencial de 1 a 7.

**Why this priority**: A introdução das 5 Superclasses de Interface (Zero-G, Mecânica, Invisível, Dimensional, Monolítica) assumiu a responsabilidade sobre movimento, física, botões e abas. Manter controles paralelos gera confusão de produto e configurações conflitantes.

**Independent Test**: Pode ser testado abrindo o formulário de Ajustes e verificando que os grupos de controles contêm exatamente as 7 opções numeradas consecutivamente, sem as seções de Movimento, Largura de Botões e Abas, e que o `localStorage` armazena o estado limpo sem erros.

**Acceptance Scenarios**:
1. **Given** o painel de Ajustes, **When** inspecionado pelo usuário, **Then** as opções "5. Movimento (Transições)", "7. Botões (Largura)" e "8. Abas (Navegação do estudo)" não estão mais presentes na interface nem no catálogo de campos.
2. **Given** as opções remanescentes de aparência, **When** exibidas na tela, **Then** estão organizadas com numeração sequencial rigorosa:
   - Aparência básica: Tema
   - 1. Cor de destaque (`accent`)
   - 2. Densidade (`density`)
   - 3. Leitura (`font`, `reader-size`, `align`)
   - 4. Marcação (`highlight`)
   - 5. Acervo (`library`)
   - 6. Largura da interface (`container`)
   - 7. Superclasse de Interface (`superclass`, `superclass-intensity`)
3. **Given** um navegador com preferências salvas contendo chaves antigas (`motion`, `button-width`, `tabs`), **When** a aplicação é carregada, **Then** essas chaves são normalizadas e limpas sem corromper as demais escolhas válidas do usuário.

---

### Edge Cases

- **Navegação com Alterações Não Salvas:** Ao navegar para outra rota com formulário preenchido (ex.: cadastro de livro ou edição de estudo), a guarda `useUnsavedChanges` deve continuar interceptando e protegendo os dados sem causar estado de tela branca caso o usuário decida cancelar ou prosseguir.
- **Navegação Rápida com Múltiplos Cliques:** Cliques sucessivos e rápidos na barra de navegação principal durante uma transição `<Transition mode="out-in">` não devem travar a animação nem deixar o DOM sem nós filhos.
- **Chave de Rota com Query Strings vs Params:** A reatividade deve diferenciar navegações estruturais de rota (`fullPath`) garantindo que a troca de abas ou parâmetros desmonte e monte as visualizações apropriadas.
- **Migração de `localStorage` sem Quebra de Contrato:** Clientes existentes com chaves removidas no armazenamento local não podem lançar exceções JavaScript ou travar a inicialização do bootstrap de aparência (`appearance-bootstrap.js`).
- **Fontes com Caracteres Especiais ou Acentos:** A aplicação global da fonte no `body` deve manter renderização correta de acentos e diacríticos em português em todas as 24 fontes locais.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O componente de visualização de rotas em `App.vue` DEVE garantir a remontagem reativa de componentes em navegações client-side fornecendo a chave de rota completa (`:key="$route.fullPath"`) no `<component :is="Component" :key="$route.fullPath" />`, assegurando transições atômicas e isoladas mesmo sob alterações de parâmetros de consulta (`?chapter=...`).
- **FR-002**: Todas as visualizações associadas a rotas (`BooksView`, `BookView`, `StudyView`, `StudyEditView`, `ImportView`, `SettingsView`, `TrashView`, `ConnectionView`) DEVEM possuir um elemento raiz único e estático no `<template>`, garantindo conformidade estrita com o componente `<Transition mode="out-in">` do Vue 3.
- **FR-003**: A transição de rotas NUNCA deve resultar em tela em branco ou componente órfão não montado ao alternar entre abas do cabeçalho global.
- **FR-004**: O sistema DEVE propagar a fonte selecionada (`--font-reading`) para as variáveis de interface global (`--font-ui`), aplicando-a de forma irrestrita e imediata a 100% dos elementos da aplicação (`:root`, `body`, `#app`, botões, inputs, menus, cabeçalhos, cartões, blocos de código e textos técnicos).
- **FR-005**: A alteração de fonte na tela de Ajustes DEVE refletir imediatamente em tempo real sobre os elementos da própria tela de Ajustes (títulos, botões, selects, rótulos e cards de preview).
- **FR-006**: O catálogo de campos de aparência (`appearance-bootstrap.js` e `appearance.d.ts`) DEVE remover os campos obsoletos `motion`, `button-width` e `tabs`.
- **FR-007**: A função `normalize()` de aparência DEVE purgar automaticamente as chaves obsoletas (`motion`, `button-width`, `tabs`) do `localStorage` já na inicialização da aplicação, persistindo o objeto higienizado e removendo os atributos `data-motion`, `data-button-width` e `data-tabs` do elemento `<html>`.
- **FR-008**: O painel de Ajustes (`AppearanceControls.vue` e `appearance-bootstrap.js`) DEVE reorganizar e renumerar sequencialmente os grupos de opções de 1 a 7:
  - 1. Cor de destaque
  - 2. Densidade
  - 3. Leitura
  - 4. Marcação
  - 5. Acervo
  - 6. Largura da interface
  - 7. Superclasse de Interface
- **FR-009**: O controle de "Intensidade da física" na Superclasse DEVE permanecer como o único mecanismo de ajuste paramétrico de movimento da interface.
- **FR-010**: A suíte de testes unitários do frontend DEVE cobrir a nova estrutura de 7 opções, a herança global de tipografia e a estabilidade das chaves de rota.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Em 100% dos testes manuais e automatizados de navegação entre rotas, o conteúdo da tela de destino é renderizado sem tela branca e sem necessidade de atualização (F5).
- **SC-002**: A troca de qualquer uma das 24 fontes no seletor de Ajustes altera a tipografia visível da interface em menos de 50ms, sem recarregar a página.
- **SC-003**: O painel de Ajustes exibe exatamente 7 grupos numerados (1 a 7) além da Aparência Básica (Tema), sem referências a Movimento, Botões ou Abas.
- **SC-004**: 100% dos testes unitários do frontend (`npm test`) passam com sucesso, incluindo os testes de regressão das 5 superclasses e do catálogo de aparência.
- **SC-005**: O build de produção (`npm run build`) conclui sem erros de tipagem TypeScript ou avisos de template.

---

## Assumptions

- A aplicação continua rodando em processo único local, sem necessidade de alterações no backend Python ou banco SQLite.
- A persistência das preferências permanece no `localStorage` do navegador sob a chave `caderno.aparencia.v2`.
