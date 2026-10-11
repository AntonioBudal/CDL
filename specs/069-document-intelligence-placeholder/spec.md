# Feature Specification: Tela Placeholder do Document Intelligence (Digitalização de Caderno Manuscrito)

**Feature Branch**: `069-document-intelligence-placeholder`  
**Created**: 2026-10-11  
**Status**: Approved (Decisões de Design Consolidadas: A;A;A;A)  
**Input**: Solicitação do usuário para reserva honesta de espaço no frontend para o subprojeto `document-intelligence/` (conversão de páginas manuscritas em estudos estruturados).

---

## 1. Contexto & Visão do Produto

O repositório mantém um subprojeto independente e exploratório denominado `document-intelligence/` (pesquisado por outro agente em ambiente isolado), cujo objetivo a longo prazo é transformar fotografias de páginas de cadernos manuscritos em estudos estruturados no Caderno de Leitura (preservando hierarquia, blocos de texto, notas marginais, diagramas e ordem de leitura).

Atualmente, essa frente encontra-se em estágio preliminar de pesquisa e validação:
- Não existem serviços em execução, processos em segundo plano, modelos de IA embarcados nem endpoints de API disponíveis.
- Modelos de transcrição para caligrafia manuscrita em língua portuguesa ainda demandam pesquisa extensa.
- O formato intermediário LDF (*Layout Description Format*) e seu rascunho de especificação ainda possuem lacunas e divergências que impedem qualquer integração técnica prematura.

Para acolher a expectativa dos leitores que mantêm cadernos físicos de anotação e comunicar de forma transparente o compromisso com a **privacidade local absoluta** (processamento estritamente local no computador do usuário, sem envio de imagens para servidores em nuvem), esta feature introduz uma **tela estática placeholder honesta** no frontend do Leitorum. A tela não realiza uploads, não aciona a câmera, não executa chamadas de rede e oferece caminhos de saída imediatos para os fluxos de trabalho já operacionais no produto ("Importar Fichamento" e "Caixa de Entrada").

---

## 2. Decisões Consolidadas pelo Usuário

As 4 diretrizes estruturais de interface e produto foram validadas e aprovadas pelo usuário (padrão `A;A;A;A`):

1. **Nome da Funcionalidade e Rota**: **Digitalizar Caderno** (`/digitalizar`). Título da página: `"Digitalizar Caderno — Caderno de Leitura"`.
2. **Ponto de Entrada na Navegação**: **Card editorial dedicado dentro do Hub de Importação (`/importar`)**, rotulado como *"Caderno Manuscrito (Em Pesquisa)"* com breve síntese e botão para navegar até `/digitalizar`.
3. **Escopo de Visibilidade**: **Todos os usuários autenticados**. Acesso amplo e transparente sobre o compromisso de privacidade local e evolução da ferramenta.
4. **Indicador de Estado**: **Matriz Didática de 4 Etapas** com status textuais fixos e notas honestas sobre a maturidade da pesquisa.

---

## 3. User Scenarios & Testing *(Prioritised)*

### User Story 1 - Acesso à Proposta e Compromisso de Privacidade Local (Priority: P1) [MVP]

**Objetivo**: Como leitor que possui anotações manuais em cadernos de papel, desejo acessar a tela informativa para compreender como funcionará a futura captura estruturada e ter a certeza inegociável de que nenhuma foto será enviada para serviços de nuvem ou empresas externas.

**Why this priority**: Estabelece a identidade da funcionalidade, acolhe o leitor e ancora o princípio de soberania e privacidade local que rege o Leitorum.

**Independent Test**: Navegar até a nova rota (ex.: `/digitalizar`), ler as explicações estáticas sobre segmentação de blocos (título, notas de margem, ordem de leitura) e conferir a mensagem expressa de processamento local no computador.

**Acceptance Scenarios**:
1. **Given** um usuário autenticado no sistema,  
   **When** ele acessa a rota da funcionalidade,  
   **Then** a interface apresenta título hierárquico, descrição do fluxo de estudo estruturado a partir de cadernos manuscritos e aviso de soberania de dados afirmando que o processamento será 100% local no próprio dispositivo.
2. **Given** que o leitor procura saber prazos de lançamento,  
   **When** lê o texto explicativo da tela,  
   **Then** o conteúdo afirma com clareza que o recurso está "em pesquisa", sem promessas de datas, cronogramas fictícios ou prazos vinculantes.

---

### User Story 2 - Consulta ao Indicador de Maturidade por Etapas (Priority: P1) [MVP]

**Objetivo**: Como usuário interessado no avanço técnico da ferramenta, desejo visualizar um painel honesto e estático que descreva o estágio real de cada camada da pesquisa, para saber exatamente quais desafios já foram superados e quais ainda estão em investigação.

**Why this priority**: Evita falsas expectativas ("em breve" genérico de marketing) e estabelece um diálogo maduro com o usuário sobre a complexidade da inteligência visual em caligrafia portuguesa.

**Independent Test**: Inspecionar os 4 marcos de maturidade na tela e verificar a exatidão textual de cada status sem dependência de APIs ou requisições dinâmicas.

**Acceptance Scenarios**:
1. **Given** a visualização da seção de maturidade técnica,  
   **When** o usuário confere os indicadores,  
   **Then** são exibidos com exatidão os 4 estados fixos:
     - *Localizar linhas e blocos na página*: Em validação (funciona em páginas sintéticas; testes em fotos reais pendentes);
     - *Ordem de leitura*: Em validação;
     - *Transcrição do texto manuscrito em português*: Em pesquisa (ainda não há modelo que leia caligrafia em português);
     - *Classificação do conteúdo e diagramas*: Não iniciado.
2. **Given** a renderização dos indicadores,  
   **When** o componente é montado na tela,  
   **Then** nenhuma chamada de rede é disparada (`network request count === 0`) e nenhum dado dinâmico é simulado.

---

### User Story 3 - Caminhos de Saída Úteis para Fluxos em Operação (Priority: P2)

**Objetivo**: Como leitor que precisa registrar suas anotações imediatamente no momento presente, desejo encontrar atalhos claros para as ferramentas de entrada já funcionais no sistema ("Importar Fichamento" e "Caixa de Entrada"), sem ficar bloqueado em um beco sem saída.

**Why this priority**: Uma tela informativa não deve ser um beco sem saída; ela deve redirecionar a energia produtiva do usuário para os recursos existentes.

**Independent Test**: Clicar nos botões/links de ação de saída e confirmar navegação imediata via `vue-router` para `/importar` e `/inbox`.

**Acceptance Scenarios**:
1. **Given** um leitor na tela informativa,  
   **When** ele clica no atalho para "Importar fichamento",  
   **Then** a rota é direcionada imediatamente para o Ateliê de Importação (`/importar`).
2. **Given** um leitor na tela informativa,  
   **When** ele clica no atalho para "Caixa de Entrada",  
   **Then** a rota é direcionada imediatamente para a triagem da Caixa de Entrada (`/inbox`).

---

### User Story 4 - Respeito aos Temas Visuais, Acessibilidade & Resiliência Offline (Priority: P3)

**Objetivo**: Como leitor utilizando qualquer um dos 10 temas visuais (claros, sépia, escuros ou E-Ink) ou navegando em dispositivos móveis sem conexão à internet, desejo visualizar a tela com tipografia editorial elegante, contraste acessível e ergonomia completa.

**Why this priority**: Garante que o placeholder se integre harmoniosamente ao padrão de excelência de design do Leitorum, sem quebras visuais ou falhas de acessibilidade.

**Independent Test**: Alternar temas visuais, redimensionar a janela para telas estreitas (< 768px), navegar exclusivamente via teclado (`Tab`, `Shift+Tab`, `Enter`) e desativar o sinal de rede.

**Acceptance Scenarios**:
1. **Given** qualquer um dos 10 temas visuais ativado no sistema,  
   **When** a tela é exibida,  
   **Then** todas as superfícies, bordas e textos consomem variáveis CSS semânticas (`--color-surface`, `--color-text`, `--color-border-subtle`, etc.), com ausência total de cores fixas saturadas e conformidade WCAG AA.
2. **Given** uma conexão offline,  
   **When** a página é recarregada pelo navegador,  
   **Then** ela renderiza instantaneamente e sem erros, por ser composta de ativos estáticos do bundle local.
3. **Given** navegação assistiva ou por teclado,  
   **When** o leitor percorre a página,  
   **Then** a estrutura de cabeçalhos segue a ordem `h1` → `h2` → `h3`, com anéis de foco visíveis (`:focus-visible`) e alvos de toque móveis $\ge 44 \times 44$px.

---

## 4. Edge Cases

- **Acesso direto via URL (Deep Linking)**: Se o usuário acessar `/digitalizar` diretamente na barra do navegador estando desautenticado, o guarda de rota do Vue Router deve redirecioná-lo para a tela de autenticação (`/login`) preservando a query `redirect=/digitalizar`.
- **Navegação com Rede Inativa**: Como a tela é puramente estática e não efetua requisições HTTP, a interface deve carregar sem mensagens de "Falha ao conectar com o servidor" ou spinners infinitos.
- **Telas Estreitas / Dispositivos Móveis (320px)**: A grade de etapas e os blocos de texto devem fluir em coluna única vertical, sem transbordamento horizontal de texto ou elementos de interface cortados.
- **Tentativa de arrastar arquivos ou soltar imagens**: A tela não deve conter áreas de *drag and drop* ativas; qualquer arquivo acidentalmente solto pelo usuário sobre a janela não deve ser capturado nem processado.

---

## 5. Requirements *(Mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE fornecer a rota autenticada `/digitalizar` no frontend (`meta: { requiresAuth: true }`, visível para todos os usuários autenticados) mapeada para uma view Vue dedicada (`DigitalizarCadernoView.vue`).
- **FR-002**: A rota DEVE definir metadados completos de título de página (`document.title`) no padrão editorial do sistema: `"Digitalizar Caderno — Caderno de Leitura"`.
- **FR-003**: A interface DEVE apresentar título editorial, subtítulo explicativo e texto conceitual descrevendo o objetivo da funcionalidade: receber fotografias de páginas de caderno e convertê-las em estudos estruturados com texto, blocos (títulos, parágrafos, notas de margem e diagramas) e ordem natural de leitura.
- **FR-004**: A interface DEVE destacar de forma proeminente o compromisso de privacidade: todo o processamento computacional será estritamente local na máquina do usuário, sem transmissão de imagens ou dados para servidores externos ou serviços de nuvem.
- **FR-005**: A interface DEVE explicitar que a ferramenta encontra-se em estágio de "pesquisa experimental", sem estipular prazos de entrega, trimestres ou datas de lançamento.
- **FR-006**: A interface DEVE exibir uma seção estruturada de maturidade técnica por etapa com os 4 itens estáticos inegociáveis:
  1. *Localizar linhas e blocos na página*: `Em validação` (com nota explicativa: "Funciona em páginas sintéticas; testes com fotografias reais em andamento");
  2. *Ordem de leitura*: `Em validação`;
  3. *Transcrição do texto manuscrito em português*: `Em pesquisa` (com nota explicativa: "Investigação de modelos capazes de reconhecer grafia manuscrita em língua portuguesa");
  4. *Classificação do conteúdo e diagramas*: `Não iniciado`.
- **FR-007**: A interface DEVE disponibilizar uma seção de caminhos de ação imediata contendo atalhos clicáveis para fluxos existentes:
  - Botão/Link para o Ateliê de Importação (`/importar`);
  - Botão/Link para a Caixa de Entrada (`/inbox`).
- **FR-008**: Se uma representação visual ou esquema gráfico for exibido para exemplificar a detecção de blocos, ele DEVE ser claramente rotulado como `"Ilustração Conceitual"` e conter exclusivamente dados e textos fictícios, sem qualquer referência a notas ou livros do acervo do usuário.
- **FR-009**: O Ateliê de Importação (`/importar`) DEVE exibir um card editorial de acesso dedicado intitulado *"Caderno Manuscrito (Em Pesquisa)"* com breve síntese explicativa, ícone SVG semântico (zero emojis) e ação de navegação para a rota `/digitalizar`.

### Non-Functional & Governance Restrictions (Restrições Inegociáveis)

- **NR-001 (Isolamento de Backend)**: Nenhuma alteração pode ser realizada em arquivos Python de backend, tabelas SQLite, migrações Alembic ou endpoints da API REST.
- **NR-002 (Ausência de Captura)**: É expressamente proibido incluir `<input type="file">`, acesso a APIs de câmera (`navigator.mediaDevices`), zonas de soltura (*drag & drop*) ou persistência temporária de imagens no navegador.
- **NR-003 (Zero Chamadas de Rede)**: A tela não deve disparar nenhuma requisição HTTP para APIs locais ou remotas do Document Intelligence.
- **NR-004 (Desacoplamento de Rascunhos)**: A implementação do frontend não deve consumir nem depender das especificações preliminares `document-intelligence/docs/ldf.md` ou `api-local.md`.
- **NR-005 (Preservação do Subprojeto)**: Nenhum arquivo dentro do diretório `document-intelligence/` deve ser criado, editado ou removido por esta feature.
- **NR-006 (Zero Dependências Novas)**: Nenhuma biblioteca externa de OCR, parser de imagens ou pacote NPM deve ser adicionado ao `package.json`.
- **NR-007 (Imunidade Cromática & Zero Emojis)**: Todo o estilo CSS deve consumir tokens semânticos dos 10 temas visuais do Leitorum, com zero uso de emojis no código-fonte ou no texto visível.

---

## 6. Success Criteria *(Mandatory)*

### Measurable Outcomes

- **SC-001**: O tempo de renderização inicial da tela a partir do clique no menu de navegação é inferior a 100ms em hardware convencional, operando 100% com recursos locais do pacote compilado.
- **SC-002**: O número de requisições HTTP disparadas pela visualização durante a montagem e permanência na tela é rigorosamente zero (`0`).
- **SC-003**: 100% dos 10 temas visuais do sistema renderizam a tela com contraste conforme as diretrizes WCAG 2.1 AA (mínimo de 4.5:1 para texto comum e 3:1 para elementos de interface).
- **SC-004**: O usuário consegue transitar da tela informativa para os fluxos produtivos em exatamente 1 clique (para `/importar` ou `/inbox`).
- **SC-005**: 100% das suítes de validação de frontend (`npm test` e `npm run build`) executam com sucesso e zero erros de tipo ou compilação.

---

## 7. Assumptions & Dependencies

- **Autenticação Existente**: A rota utiliza os guardas de autenticação habituais do Vue Router (`meta: { requiresAuth: true }`) já implementados na arquitetura do Leitorum.
- **Ausência de Backend**: O backend da aplicação não precisa registrar rotas novas; o servidor Uvicorn atua servindo o SPA no roteamento de fallback tradicional para rotas do cliente.
- **Evolução Futura Planejada**:
  - Em uma fase futura de testes laboratoriais (quando `document-intelligence/` produzir seu primeiro protótipo funcional executável localmente), esta tela placeholder será estendida para suportar um *modo de visualização de layout*.
  - Esse modo de teste será restrito a administradores da instância (`adminOnly`), permitindo carregar uma imagem estática de teste e visualizar o traçado geométrico dos blocos delimitadores em sobreposição vetorial (sem transcrição textual).
  - O contrato e os endpoints necessários para essa evolução serão especificados em ciclo próprio do Spec Kit, sem antecipações nesta entrega.

---

## 8. Verificação e Testabilidade

A spec exige a criação de testes automatizados com `node:test` cobrindo:
1. Existência e integridade da rota e componente da tela informativa (`DigitalizarView.vue` ou correspondente).
2. Validação da presença obrigatória dos 4 marcos textuais de status técnico e da mensagem de soberania de dados local.
3. Validação dos links de navegação para `/importar` e `/inbox`.
4. Validação de conformidade visual: banimento total de emojis e uso exclusivo de classes semânticas.
5. Verificação da ausência de elementos de captura de imagem (`input[type="file"]`, chamadas a APIs de mídia).
