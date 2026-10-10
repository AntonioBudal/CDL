<USER_REQUEST>
# Leitorum — Especificação Técnica de Execução: Roadmap 0.8

**Documento de Engenharia e Design System para o Antigravity**

**Versão do Documento:** 1.1.0-EXEC

**Alvo:** Repositório do Leitorum

**Classificação de Escopo:** Redesign Estrutural, Ergonomia de Interação e Arquitetura Visual

---

## 1. Contexto, Objetivos e Governança do Roadmap 0.8

### 1.1 Objetivo Central

O Roadmap 0.8 transforma as interfaces do Leitorum — atualmente estruturadas como um painel administrativo/CRUD genérico — em um ambiente imersivo, reflexivo e tátil voltado ao estudo profundo, leitura ativa e gestão duradoura de conhecimento.

O Leitorum já possui **dez temas cromáticos** plenamente funcionais. O escopo **não** abrange a criação de novas paletas de cores, alteração de temas existentes ou substituição arbitrária de cores primárias. O redesign foca exclusivamente em:

1. Composição espacial e arquitetura de layout.
2. Hierarquia visual, densidade e distribuição das ações.
3. Microinterações intencionais, estados de foco e animações funcionais com feedback tátil.
4. Identidade própria por tela, garantindo que cada ambiente do sistema reflita sua função cognitiva sem perder a coerência global do produto.

### 1.2 Regras de Marcação e Convenções Deste Documento

Para orientar a interpretação do Antigravity, todos os requisitos utilizam três marcadores canônicos:

* `[DEFINIDO NO PLANEJAMENTO]`: Decisões de arquitetura, fluxos, conceitos e restrições já deliberados e aprovados. Devem ser respeitados sem desvios.
* `[COMPLEMENTO TÉCNICO PROPOSTO]`: Recomendações de engenharia, componentização, contratos de estado e acessibilidade adicionados para estruturar a execução técnica.
* `[REQUER INSPEÇÃO NO CÓDIGO]`: Pontos onde o Antigravity deve inspecionar o código-fonte (árvore de componentes, rotas, stores de estado, design tokens) antes de implementar, adaptando a execução ao padrão real da base de código.

---

## 2. Diretrizes Técnicas Globais e Restrições de Sistema

### 2.1 Imunidade Cromática e Respeito aos 10 Temas

* `[DEFINIDO NO PLANEJAMENTO]` É proibido o uso de valores de cor hexadecimais fixos (`#fff`, `#1e293b`, etc.) ou classes utilitárias de cores arbitrárias diretamente no CSS/JSX dos componentes redesenhados.
* `[COMPLEMENTO TÉCNICO PROPOSTO]` Toda estilização deve consumir exclusivamente as variáveis semânticas do tema (design tokens como `--bg-canvas`, `--bg-surface`, `--bg-subtle`, `--text-primary`, `--text-muted`, `--border-subtle`, `--accent-primary`, `--accent-hover`, etc.).
* `[REQUER INSPEÇÃO NO CÓDIGO]` O Antigravity deve inspecionar o arquivo global de temas (ex: `theme.css`, `tokens.ts` ou equivalente no Tailwind/CSS Modules) e documentar os nomes exatos das variáveis antes de iniciar as estilizações.

### 2.2 Política Cinética e Performance de Animação

* `[DEFINIDO NO PLANEJAMENTO]` As animações não devem ser decorativas ou atrasar fluxos de trabalho recorrentes. Toda animação deve:
1. Fornecer feedback imediato de conclusão ou erro.
2. Esclarecer a relação espacial de entrada/saída de elementos (drawers, popovers, modais).
3. Respeitar estritamente a preferência do sistema por movimento reduzido (`prefers-reduced-motion`).


* `[COMPLEMENTO TÉCNICO PROPOSTO]` Propriedades animadas no CSS devem restringir-se a `transform` e `opacity` para garantir taxa estável de 60 FPS acelerada por GPU. Nenhuma transição deve exceder 250ms em ações frequentes de interface.
* `[COMPLEMENTO TÉCNICO PROPOSTO]` Fallback universal obrigatório:
```css
@media (prefers-reduced-motion: reduce) {
  *, ::before, ::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}

```



### 2.3 Acessibilidade e Navegabilidade Ergonômica

* `[DEFINIDO NO PLANEJAMENTO]` A interface deve ser plenamente operacional via teclado e compatível com leitores de tela.
* `[COMPLEMENTO TÉCNICO PROPOSTO]` Alvos de toque (*touch targets*) em telas táteis devem possuir dimensão mínima de 44x44px. Todos os botões contextuais e de ação devem incluir atributos `aria-label` descritivos, estados `:focus-visible` com anéis de foco nítidos (`--ring-focus`) e anúncios semânticos para transições assíncronas via regiões `aria-live`.

---

## 3. Arquitetura do Header Global e Componentes Compartilhados

### 3.1 Diagnóstico do Header Atual

* `[DEFINIDO NO PLANEJAMENTO]` O header atual sofre de superlotação: 15 elementos concorrentes no mesmo plano horizontal:


* Marca: Logotipo `Leitorum`.


* Navegação Direta (8 abas): `Livros`, `Destaques`, `Revisão`, `Inbox`, `Importar`, `Amigos`, `Ajustes`, `Lixeira`.


* Utilitários e Ações: `✓ Sincronizado`, `Q Buscar Ctrl K`, `✏ Capturar Ctrl+Shift+C`, `Sino de Notificação`.


* Usuário e Sessão: Pílula de Perfil `AN Antonio` e botão solto `Sair`.




* `[DEFINIDO NO PLANEJAMENTO]` Esse layout quebra em resoluções intermediárias (laptops e tablets), confunde navegação diária com ferramentas administrativas e expõe a ação destrutiva de logout (`Sair`) como elemento primário concorrendo com o foco de estudo.



### 3.2 Nova Arquitetura do Header (Alternativa A — Três Blocos Semânticos)

* `[DEFINIDO NO PLANEJAMENTO]` O Header é reestruturado em 3 zonas operacionais distintas:
```
+---------------------------------------------------------------------------------------------------+
| [Leitorum]  |  [Livros  Destaques  Revisão  Inbox] [Mais v]  |  [Busca Ctrl+K] [Capturar] [Sync] [Avatar]|
+---------------------------------------------------------------------------------------------------+

```


1. **Bloco Esquerdo (Marca):** Logotipo minimalista com link para o núcleo do acervo.
2. **Bloco Central (Navegação Primária + Menu "Mais"):**
* Abas diretas reservadas ao ciclo ativo de leitura: **Livros**, **Destaques**, **Revisão**, **Inbox**.
* Botão/Menu retrátil **"Mais ▾"**: reúne utilitários secundários e de ciclo estendido: **Importar**, **Amigos**, **Ajustes**, **Lixeira**.


3. **Bloco Direito (Centro de Ferramentas e Identidade):**
* Pílula de comando para **Busca Global** (`Ctrl K`).
* Botão de ação rápida de **Captura** (`Ctrl+Shift+C`) com ícone contextual.
* Indicador discreto de **Sincronização** (ícone com pulso sutil em sync, tooltip explicativo).
* **Menu do Usuário (Avatar/Iniciais):** O botão avulso `Sair` é **obrigatoriamente transferido** para dentro do menu suspenso do usuário, agrupado com o perfil e status da conta.







### 3.3 Tratamento do Header no Roadmap de 10 Features

* `[DEFINIDO NO PLANEJAMENTO]` A reformulação do Header Global e da moldura do sistema (*App Shell*) é implementada como fundação compartilhada dentro da **Feature 01 (Livros)**.
* `[COMPLEMENTO TÉCNICO PROPOSTO]` Essa implementação deve gerar componentes desacoplados reutilizáveis (`GlobalHeader`, `NavigationTabs`, `UserDropdown`, `QuickCaptureTrigger`), permitindo que as páginas subsequentes apenas consumam o layout compartilhado sem retrabalho.

---

## 4. Especificações Executáveis das 10 Features do Roadmap 0.8

---

### Feature 01: Livros — Curadoria Editorial, Biblioteca Ativa e Novo Header Global

#### 1. Identificação e Objetivo

* **Área Afetada:** Cabeçalho Global do Sistema (`App Shell`) e Página de Livros (`/livros` ou equivalente).


* **Resultado Esperado:** Cabeçalho em 3 blocos e biblioteca com composição de "Mesa do Leitor", eliminando o formulário estático lateral e destacando as leituras ativas e a estante visual.



#### 2. Contexto e Justificativa

* `[DEFINIDO NO PLANEJAMENTO]` O formulário de cadastro "Novo livro" ocupa cerca de 35% da tela permanentemente, reduzindo a área útil de exploração do acervo. O cartão de livro existente possui aspecto rígido de banco de dados. O header sobrecarregado compete com a leitura.



#### 3. Diagnóstico Necessário

* `[REQUER INSPEÇÃO NO CÓDIGO]` Inspecionar a estrutura do header global atual (`Header.tsx` ou similar), localizando os links de rota, status de sync e botões `Buscar`, `Capturar` e `Sair`.


* `[REQUER INSPEÇÃO NO CÓDIGO]` Inspecionar a página de Livros (`BooksPage.tsx` ou similar), identificando o componente do formulário lateral de cadastro (`BookForm.tsx` ou similar) e a query/mutation que lista e cadastra obras.



#### 4. Direção do Redesign

* `[DEFINIDO NO PLANEJAMENTO]`
1. Header unificado em 3 blocos semânticos com menu "Mais ▾" e transferência do botão "Sair" para o menu de perfil.


2. Área de topo da biblioteca com a seção "Em Andamento" (hero card da leitura atual).
3. Estante fluida de obras com proporção visual realista de livros, tipografia refinada e tags de metadados.
4. Cadastro de livros migrado para um *Drawer* lateral deslizante de foco exclusivo, acionado pelo botão "+ Adicionar Livro".



#### 5. Escopo de Implementação

* Reestruturar o componente de Header global.


* Criar componente compartilhado `Drawer` acessível (foco retido, fechamento via `Esc` e backdrop).
* Refatorar a página de Livros para layout de largura total com duas seções verticais:
1. *Hero de Leitura Ativa* (última obra aberta ou em progresso).
2. *Grade Curatorial do Acervo* com barra integrada de busca e filtros por chips.




* Migrar o formulário de cadastro (campos: Título, Autor opcional, Categorias opcional) para o *Drawer*.



#### 6. Interações e Animações

* `[COMPLEMENTO TÉCNICO PROPOSTO]` **Abertura do Drawer:** Deslizamento lateral a partir da direita (`transform: translateX(0)`, 220ms, curva `cubic-bezier(0.16, 1, 0.3, 1)`), com backdrop escurecido suave (`opacity: 1`, 200ms).
* `[COMPLEMENTO TÉCNICO PROPOSTO]` **Hover nos Livros:** Elevação sutil do cartão (`transform: translateY(-4px)`), com intensificação gradual da sombra de profundidade em 150ms.
* `[COMPLEMENTO TÉCNICO PROPOSTO]` Alternância Grade/Lista: Transição contínua entre modos de visualização sem recarga da página.



#### 7. Responsividade e Acessibilidade

* Header em telas menores (< 768px): Colapso das abas em navegação inferior (*bottom bar*) ou menu hambúrguer; preservação da busca rápida e do botão de captura.
* Drawer: Ocupa 420px no desktop e 100% da largura em dispositivos móveis.
* Navegação por teclado: O foco do teclado entra automaticamente no primeiro campo do Drawer ao abrir e retorna ao botão disparador ao fechar.

#### 8. Preservação Funcional

* Preservar abas de separação "Meu Acervo" e "Compartilhados Comigo".


* Preservar filtros por Categoria, ordenação (ex: "Recentemente modificados") e modos Grade/Lista.


* Preservar contratos de API de criação e listagem de livros.

#### 9. Critérios de Aceitação

* A coluna lateral estática de formulário foi removida do layout principal de Livros.


* O Header unificado exibe apenas as 4 abas primárias e agrupa as demais no menu "Mais ▾".


* O botão "Sair" não existe mais solto no topo do header.


* O cadastro de livro funciona integralmente via Drawer sem quebrar validações existentes.



#### 10. Testes e Validação

* Validar cadastro de novo livro preenchendo todos os campos e apenas os campos obrigatórios.


* Validar abertura/fechamento do Drawer via tecla `Esc` e clique no backdrop.
* Testar a página em resolução 1920px, 1280px, 768px e 375px.

#### 11. Dependências e Riscos

* Dependência: A implementação do Header afeta todas as páginas autenticadas do sistema.


* Risco: Vazamento de estilos globais ao alterar o contêiner mestre do *App Shell*. Mitigação: encapsular classes e variáveis.

#### 12. Condição de Conclusão (DoD)

* O novo Header está ativo e operando em todas as rotas; a página de Livros exibe o acervo em largura total com o novo fluxo de Drawer funcional e sem erros de console.

---

### Feature 02: Destaques — Códice e Margens Vivas

#### 1. Identificação e Objetivo

* **Área Afetada:** Página de Destaques e Anotações (`/destaques` ou equivalente).


* **Resultado Esperado:** Uma experiência visual de *commonplace book* (caderno de citações), com cartões editoriais legíveis, filtros de tonalidade de grifo e tratamento de estados de erro e vazio integrados aos temas.



#### 2. Contexto e Justificativa

* `[DEFINIDO NO PLANEJAMENTO]` A interface atual assemelha-se a uma listagem transacional com filtros faceta genéricos e bolinhas de cores horizontais estáticas. Estados de erro exibem banners retangulares vermelhos com texto descontextualizado.



#### 3. Diagnóstico Necessário

* `[REQUER INSPEÇÃO NO CÓDIGO]` Inspecionar os seletores de cor e os filtros da página de destaques (`HighlightsPage.tsx` ou similar).


* `[REQUER INSPEÇÃO NO CÓDIGO]` Verificar o tratamento do estado de erro e o componente de alerta atual (`Alert.tsx` ou bloco condicional).



#### 4. Direção do Redesign

* `[DEFINIDO NO PLANEJAMENTO]`
1. Apresentação em formato de Fichas Literárias: a citação recebe tipografia serifada/humanista em destaque com aspas editoriais, seguida de notas de estudo do leitor.
2. Filtros de cores convertidos em "Categorias de Grifo" semânticas (ex: Ideia Central, Dúvida, Citação-chave, Refutação).
3. Estado de erro e vazio remodelados com tom acolhedor e integrados ao tema visual ativo.



#### 5. Escopo de Implementação

* Redesenhar o cartão de destaque (`HighlightCard`):
* Citação do trecho com formatação tipográfica destacada.
* Rodapé com indicação de Livro, Capítulo e Página/Localização.
* Ação contextual de cópia de citação em múltiplos formatos (ABNT / Markdown).


* Reorganizar a barra de filtros: unificar busca por texto, agrupamento (Recentes vs Por Obra), filtro de obra, filtro de tipo e cores.


* Substituir o bloco de erro vermelho por um componente de estado de erro temático com botão "Tentar novamente" reestilizado.



#### 6. Interações e Animações

* `[COMPLEMENTO TÉCNICO PROPOSTO]` **Copiar Citação:** Ao passar o mouse no cartão, surge botão de cópia discreto. Ao clicar, feedback imediato com check animado e mensagem flutuante ("Copiado para a área de transferência", duração 1500ms).
* `[COMPLEMENTO TÉCNICO PROPOSTO]` **Expansão de Contexto:** Clique para ver trechos anterior/posterior com animação de acordeão suave (`height: auto`, 180ms).

#### 7. Responsividade e Acessibilidade

* Suporte a leitores de tela nos filtros de cores através de rótulos semânticos (`aria-label="Filtrar por destaques em amarelo (Ideia Central)"`).
* Quebra harmoniosa em coluna única centralizada no mobile com preservação de margens de leitura confortáveis.

#### 8. Preservação Funcional

* Preservar filtros: Busca textual, visualização "Recentes" vs "Por Obra", filtro por Obra, filtro por Tipo e filtro por Cor.


* Preservar chamada de repetição (*retry*) da query de busca de destaques.



#### 9. Critérios de Aceitação

* Os destaques são exibidos com tipografia editorial diferenciada entre citação e anotação pessoal.
* Os filtros por cor possuem representação acessível além da cor visual.
* O estado de falha na requisição respeita as cores do tema ativo sem apresentar faixas vermelhas desconexas.



#### 10. Testes e Validação

* Forçar erro de rede na API de destaques para validar visualmente o estado de erro e o botão "Tentar novamente".


* Testar filtro por cores combinadas e busca textual em conjunto.

#### 11. Dependências e Riscos

* Dependência: Acesso à lista de cores de grifo cadastradas no backend/store.
* Risco: Textos de citações extensas podem quebrar o layout se não houver tratamento adequado de truncamento e expansão de texto.

#### 12. Condição de Conclusão (DoD)

* Página de Destaques operando com os novos cartões de fichas literárias, filtros semânticos e estado de erro testado e aprovado.

---

### Feature 03: Revisão — Bancada de Fixação Cognitiva

#### 1. Identificação e Objetivo

* **Área Afetada:** Central de Revisão (`/revisao` ou equivalente).


* **Resultado Esperado:** Espaço focado na prática diária de *Active Recall*, eliminando a metrificação em caixas de dashboard e introduzindo uma bancada de estudo com gatilho claro de sessão.



#### 2. Contexto e Justificativa

* `[DEFINIDO NO PLANEJAMENTO]` A tela exibe 5 caixas retangulares enfileiradas com números "0" destacados em azul e verde, emulando um painel analítico de SaaS. O estado vazio é genérico e não convida o usuário a compreender ou iniciar o estudo ativo.



#### 3. Diagnóstico Necessário

* `[REQUER INSPEÇÃO NO CÓDIGO]` Inspecionar a lógica de cálculo dos contadores: Total elegível, Perguntas, Termos ocultos (clozes), Revisados hoje e Pendentes.


* `[REQUER INSPEÇÃO NO CÓDIGO]` Inspecionar como a sessão de revisão é iniciada e qual rota/modal abriga o ciclo de flashcards/perguntas.

#### 4. Direção do Redesign

* `[DEFINIDO NO PLANEJAMENTO]`
1. Fusão dos 5 blocos de números em uma barra de prontidão intelectual coesa e minimalista.


2. Disparador visual de sessão de estudo ("Iniciar Sessão de Revisão") com indicação do volume de cartões e tempo estimado.
3. Estado vazio pedagógico: guia visual demonstrando como grifar termos para transformá-los em perguntas e *clozes* nos estudos.





#### 5. Escopo de Implementação

* Redesenhar a área superior de status de revisão:
* Substituir os 5 cards isolados por uma seção de prontidão com indicador de progresso diário e distribuição de itens.


* Centralizar o botão de ação primária "Praticar Revisão Agora".


* Refatorar o estado vazio: incluir ilustração/diagrama conceitual de uma frase com termo oculto revelando-se ao clique.


* Preservar e reestilizar as abas "Prática de Revisão" e "Histórico de Sessões".



#### 6. Interações e Animações

* `[COMPLEMENTO TÉCNICO PROPOSTO]` **Microinteração de Sessão Concluída:** Ao zerar os itens pendentes do dia, transição fluida para estado de parabéns sereno com feedback de constância.
* `[COMPLEMENTO TÉCNICO PROPOSTO]` **Virada de Cartão (na sessão ativa):** Efeito de virada 3D suave (`transform: rotateY(180deg)`, 250ms) ao exibir a resposta do cartão de estudo.

#### 7. Responsividade e Acessibilidade

* Navegação rápida via teclado durante a revisão: `Espaço` para virar cartão, teclas numéricas `1-4` para classificar retenção/dificuldade.
* Modo de revisão com centralização em tela cheia no mobile, eliminando distrações periféricas.

#### 8. Preservação Funcional

* Preservar filtros por tipo (Todos, Perguntas, Termos Ocultos) e seletor por livro.


* Preservar abas "Prática de Revisão" e "Histórico de Sessões".


* Preservar integração com algoritmos de repetição espaçada existentes.

#### 9. Critérios de Aceitação

* A tela não exibe 5 caixas soltas com contadores repetitivos estilo SaaS.


* O estado sem itens para revisar explica de forma visual e intuitiva como criar perguntas e termos ocultos.


* A ação primária de iniciar sessão é evidente e descobrível em qualquer resolução.

#### 10. Testes e Validação

* Testar com zero itens pendentes (validação do novo empty state pedagógico).


* Testar com múltiplos itens pendentes (validação dos contadores consolidados e início da sessão).

#### 11. Dependências e Riscos

* Dependência: Sistema de geração de itens interativos a partir dos estudos.
* Risco: Animações de transição de cartões não devem gerar atraso para usuários que revisam em alta velocidade.

#### 12. Condição de Conclusão (DoD)

* Central de Revisão transformada com métricas consolidadas, estado vazio instrucional ativo e fluxo de prática iniciado com sucesso.

---

### Feature 04: Inbox — Mesa de Triagem e Despejo Intelectual

#### 1. Identificação e Objetivo

* **Área Afetada:** Caixa de Entrada de Capturas (`/inbox` ou equivalente).


* **Resultado Esperado:** Mesa ágil para descarrego mental rápido (*fleeting notes*) e processamento instantâneo de notas não estruturadas.



#### 2. Contexto e Justificativa

* `[DEFINIDO NO PLANEJAMENTO]` A página atual funciona como uma lista estática de tarefas administrativas. O botão de "+ Nova Captura" fica isolado à direita, as abas são frias e falhas exibem mensagens cruas de "Not Found".



#### 3. Diagnóstico Necessário

* `[REQUER INSPEÇÃO NO CÓDIGO]` Inspecionar os endpoints e estados das capturas: Pendentes, Promovidos, Vinculados, Arquivados, Todos.


* `[REQUER INSPEÇÃO NO CÓDIGO]` Verificar o funcionamento do modal ou trigger acionado pelo atalho `Ctrl+Shift+C`.



#### 4. Direção do Redesign

* `[DEFINIDO NO PLANEJAMENTO]`
1. Campo de entrada permanente no topo (*Quick Thought Drop*) com atalho `Ctrl+Enter` para salvar notas sem abrir diálogos modais bloqueantes.
2. Cartões de rascunho com ferramentas contextuais de triagem direta: Promover a Estudo, Vincular a Livro, Arquivar, Excluir.
3. Abas de status substituídas por uma barra de triagem moderna e segmentada com contadores discretos.





#### 5. Escopo de Implementação

* Implementar o bloco superior de entrada rápida de pensamento na própria página do Inbox.


* Redesenhar os cartões de captura com controles de triagem revelados ao hover/foco.
* Reestruturar as abas de filtro: Pendentes, Promovidos, Vinculados, Arquivados, Todos.


* Tratar graciosamente o estado vazio e erros de rede.



#### 6. Interações e Animações

* `[COMPLEMENTO TÉCNICO PROPOSTO]` **Triagem de Item:** Ao clicar em "Arquivar" ou "Promover", o cartão desliza suavemente para o lado com redução de opacidade (`transform: translateX(30px)`, `opacity: 0`, 180ms), e os itens inferiores sobem suavemente (*FLIP animation*).
* `[COMPLEMENTO TÉCNICO PROPOSTO]` **Expansão de Digitação:** O campo de captura rápida expande de 1 linha para 4 linhas suavemente ao receber foco (`:focus-within`).

#### 7. Responsividade e Acessibilidade

* Mobile: suporte a ações de deslizamento (*swipe gestures*) para arquivar (esquerda) ou vincular (direita).
* Acessibilidade: atalhos de teclado para navegar entre notas (`J`/`K`) e arquivar (`E`), com confirmação falada por leitor de tela.

#### 8. Preservação Funcional

* Preservar filtros: Pendentes, Promovidos, Vinculados, Arquivados, Todos.


* Preservar atalho global `Ctrl+Shift+C` e busca interna no Inbox.


* Preservar integridade dos vínculos com livros e estudos existentes.

#### 9. Critérios de Aceitação

* É possível digitar e salvar um pensamento diretamente na tela de Inbox sem abrir modal.


* Ações de triagem removem visualmente o card com transição suave sem recarregamento de tela.
* A mensagem de erro crua "Not Found" foi substituída por estado de falha tratado dentro do tema.



#### 10. Testes e Validação

* Registrar 3 pensamentos sucessivos pelo campo rápido e validar persistência imediata.
* Triar uma captura pendente para o status de arquivada e verificar a atualização do contador.



#### 11. Dependências e Riscos

* Dependência: Sincronização entre a captura rápida do Header e a listagem do Inbox.
* Risco: Conflito de atalhos de teclado com atalhos nativos do navegador. Mitigação: usar combinações seguras (`Ctrl+Enter`, `Ctrl+Shift+C`).

#### 12. Condição de Conclusão (DoD)

* Inbox operando com campo superior de captura rápida, barra segmentada de filtros e animações de triagem fluidas.

---

### Feature 05: Importar — Ateliê de Fichamento e Parser Estruturado

#### 1. Identificação e Objetivo

* **Área Afetada:** Fluxo de Importação de Fichamento (`/importar` ou equivalente).


* **Resultado Esperado:** Um ateliê de transformação textual em duas colunas sincronizadas (*Two-Pane Studio*), substituindo o formulário vertical monótono por uma área de edição com pré-visualização viva da estrutura de estudo.



#### 2. Contexto e Justificativa

* `[DEFINIDO NO PLANEJAMENTO]` O layout atual é um formulário longo e burocrático com campos isolados de livro, capítulo, página e título, acompanhado de uma barra de ferramentas Markdown simples encostada em uma caixa de texto crua. Não há retorno imediato de como a nota se tornará um fichamento de 4 dimensões.



#### 3. Diagnóstico Necessário

* `[REQUER INSPEÇÃO NO CÓDIGO]` Inspecionar a lógica de parsing que interpreta o texto da fonte colado.


* `[REQUER INSPEÇÃO NO CÓDIGO]` Verificar o componente da barra de ferramentas de formatação (negrito, itálico, H3, tabelas, código, links).



#### 4. Direção do Redesign

* `[DEFINIDO NO PLANEJAMENTO]`
1. Faixa superior compacta com metadados essenciais (Livro, Capítulo, Página e Título), liberando altura visual.


2. Área de trabalho dividida em 2 painéis:
* *Painel Esquerdo:* Editor de texto com realce visual ao colar a fonte.
* *Painel Direito:* Pré-visualização estruturada das seções e conceitos gerados pelo fichamento.


3. Barra de ferramentas flutuante contextual no estilo moderno (aparece ao selecionar texto), mantendo a área limpa.



#### 5. Escopo de Implementação

* Redesenhar o cabeçalho do formulário em uma barra horizontal compacta de seleção de obra.


* Implementar o layout em tela dividida (*Split Pane*) com redimensionamento ou alternância de foco.
* Transformar a barra de ferramentas fixa de botões cinzas em uma barra de ferramentas flutuante sobre a seleção de texto.


* Renderizar a pré-visualização estruturada em tempo real à medida que o texto é colado ou digitado.



#### 6. Interações e Animações

* `[COMPLEMENTO TÉCNICO PROPOSTO]` **Pulso de Detecção Estrutural:** Quando o parser identificar automaticamente uma quebra de seção ou título no texto colado, exibir um pulso luminoso discreto na linha divisória correspondente do painel de preview.


* `[COMPLEMENTO TÉCNICO PROPOSTO]` **Alternância de Visualização:** Transição suave entre visualização dividida (50/50) e tela cheia de escrita (100%) em 180ms.

#### 7. Responsividade e Acessibilidade

* Telas menores (< 1024px): O painel duplo converte-se em abas segmentadas ("Texto da Fonte" vs "Prévia Estruturada").
* Suporte total aos atalhos de edição de texto universais (`Ctrl+B`, `Ctrl+I`, `Ctrl+K`).

#### 8. Preservação Funcional

* Preservar seletores de Livro e Capítulo.


* Preservar campos opcionais de Página/Localização e Título do estudo.


* Preservar todos os recursos de formatação Markdown existentes (negrito, itálico, H3, tabelas, bloco de código, links).



#### 9. Critérios de Aceitação

* O texto colado gera pré-visualização estruturada sem travamentos na digitação.


* A barra flutuante de formatação posiciona-se corretamente sem obstruir o texto selecionado.
* Metadados de livro e capítulo ocupam espaço proporcional sem espremer o editor de texto.



#### 10. Testes e Validação

* Colar um trecho longo de leitura (> 2000 palavras) e validar a performance da prévia e do scroll simultâneo.
* Testar a criação do estudo a partir do texto importado e verificar a gravação no banco de dados.

#### 11. Dependências e Riscos

* Dependência: Performance do motor de renderização de Markdown existente.
* Risco: Textos muito longos com renderização em tempo real podem causar lentidão. Mitigação: aplicar debounce no parser do preview.

#### 12. Condição de Conclusão (DoD)

* Tela de importação funcionando em formato de ateliê com painel duplo, metadados condensados e barra de formatação contextual ativa.

---

### Feature 06: Amigos — Salão Literário e Círculos de Estudo

#### 1. Identificação e Objetivo

* **Área Afetada:** Página de Amizades e Leitores (`/amigos` ou equivalente).


* **Resultado Esperado:** Uma experiência de correspondência literária e descoberta de pares intelectuais, substituindo a caixa cinza por uma identidade do leitor e círculos de leitura.



#### 2. Contexto e Justificativa

* `[DEFINIDO NO PLANEJAMENTO]` A interface atual é vazia e impessoal: uma caixa cinza com identificador de usuário (`@antoniobudalarins`), um botão de cópia cru, uma contagem isolada de "0 amigos" e abas lineares tradicionais.



#### 3. Diagnóstico Necessário

* `[REQUER INSPEÇÃO NO CÓDIGO]` Inspecionar as rotas e abas sociais: "Meus Amigos", "Solicitações", "Descobrir Leitores" e "Bloqueados".


* `[REQUER INSPEÇÃO NO CÓDIGO]` Verificar a geração do identificador de usuário e os fluxos de busca de outros leitores.



#### 4. Direção do Redesign

* `[DEFINIDO NO PLANEJAMENTO]`
1. Cartão de Identidade do Leitor (*Bookplate Card* / Ex-Líbris Digital): apresentação do perfil pessoal com dados literários (leituras em andamento, interesses) e botão de compartilhamento.
2. Estado vazio enriquecido: sugestões de exploração por áreas de interesse intelectual na aba "Descobrir Leitores".


3. Navegação social simplificada com contadores discretos nas abas.





#### 5. Escopo de Implementação

* Redesenhar o bloco do identificador pessoal em um cartão de perfil elegante e compartilhável.


* Reestruturar as abas: "Meus Amigos", "Solicitações", "Descobrir Leitores", "Bloqueados".


* Criar componentes de cartões de perfil para a lista de amigos e leitores sugeridos.
* Integrar microinteração com feedback no botão de cópia do identificador.



#### 6. Interações e Animações

* `[COMPLEMENTO TÉCNICO PROPOSTO]` **Selo de Cópia Confirmada:** Ao clicar em copiar o `@identificador`, animação de confirmação com ícone de selo de lacre ou carimbo literário esmaecendo suavemente em 1200ms.


* `[COMPLEMENTO TÉCNICO PROPOSTO]` **Card Hover:** Ao passar o cursor sobre um perfil na aba de descoberta, exibição de prévia das leituras compartilhadas via popover suave.

#### 7. Responsividade e Acessibilidade

* Mobile: suporte ao compartilhamento nativo do dispositivo via *Web Share API* quando disponível no navegador.
* Rótulos acessíveis em botões de ação ("Solicitar amizade", "Desfazer conexão", "Bloquear").

#### 8. Preservação Funcional

* Preservar abas "Meus Amigos", "Solicitações", "Descobrir Leitores" e "Bloqueados".


* Preservar o identificador de usuário do leitor e a funcionalidade de cópia.


* Preservar todas as operações de gerenciamento de solicitações e bloqueios.

#### 9. Critérios de Aceitação

* O identificador do usuário é apresentado dentro do novo cartão de perfil do leitor.


* A cópia do identificador fornece feedback visual claro e imediato.


* As abas e listas sociais respeitam o design system sem elementos com aparência de formulário genérico.



#### 10. Testes e Validação

* Testar cópia do identificador em diferentes navegadores e confirmar que o texto correto vai para a área de transferência.


* Testar alternância entre as 4 abas sociais verificando a retenção de dados.



#### 11. Dependências e Riscos

* Dependência: Políticas de privacidade configuradas na Feature 07.
* Risco: Exposição excessiva de dados pessoais do leitor. Mitigação: exibir apenas o identificador e livros explicitamente marcados como públicos.

#### 12. Condição de Conclusão (DoD)

* Página de Amigos completamente revitalizada com o cartão de identidade do leitor e navegação de círculos literários ativa.

---

### Feature 07: Ajustes — Ateliê de Preferências e Leitura Viva

#### 1. Identificação e Objetivo

* **Área Afetada:** Página de Configurações e Preferências (`/ajustes` ou equivalente).


* **Resultado Esperado:** Um ateliê ergonômico onde cada ajuste de leitura, privacidade ou sistema tem seu efeito demonstrado em tempo real em um simulador de texto ativo.



#### 2. Contexto e Justificativa

* `[DEFINIDO NO PLANEJAMENTO]` As abas de ajustes são horizontais e empilhadas no topo ("Perfil & Privacidade", "Aparência", "Leitura", "Sistema", "Conta & Dispositivos"). A caixa de "Amostra ao Vivo (PREVIEW)" fica espremida à direita de forma estática, sem engajar o usuário na personalização da sua ergonomia de leitura.



#### 3. Diagnóstico Necessário

* `[REQUER INSPEÇÃO NO CÓDIGO]` Inspecionar as 5 seções existentes de Ajustes e seus formulários correspondentes.


* `[REQUER INSPEÇÃO NO CÓDIGO]` Inspecionar o componente de "Amostra ao Vivo" (`ReaderPreview.tsx` ou similar) e verificar quais propriedades de CSS ele reflete atualmente (tipografia, entrelinha, tema).



#### 4. Direção do Redesign

* `[DEFINIDO NO PLANEJAMENTO]`
1. Menu lateral vertical de navegação contínua por âncoras substituindo as abas horizontais no topo.


2. Expansão do papel da "Amostra ao Vivo": torna-se uma bancada interativa central de teste de legibilidade.


3. Área refinada de avatar com suporte simplificado a recorte visual e upload.





#### 5. Escopo de Implementação

* Reestruturar o layout para duas colunas principais:
* Coluna esquerda (navegação e controles): Perfil & Privacidade, Aparência, Leitura, Sistema, Conta & Dispositivos.


* Coluna direita: Simulador de Leitura vivo que reage aos controles de aparência e leitura em tempo real.




* Melhorar o componente de upload de avatar (suporte a corte 256x256 WebP/PNG/JPEG até 2MB).


* Preservar o botão de ação "Ver perfil público".



#### 6. Interações e Animações

* `[COMPLEMENTO TÉCNICO PROPOSTO]` **Sincronia Imediata no Preview:** Alterações em sliders de tamanho de fonte, largura de coluna ou espaçamento refletem no texto de exemplo instantaneamente a 60 FPS via variáveis CSS.
* `[COMPLEMENTO TÉCNICO PROPOSTO]` **Transição entre Seções:** Deslocamento suave de rolagem e realce do item ativo no menu lateral de navegação.

#### 7. Responsividade e Acessibilidade

* Mobile: O painel de visualização viva converte-se em um painel inferior retrátil (*bottom sheet* expansível), permitindo testar as mudanças sem perder os controles.
* Controles de formulário equipados com atributos `aria-describedby` e suporte completo a ajustes finos pelas setas do teclado.

#### 8. Preservação Funcional

* Preservar todas as 5 seções de ajustes existentes.


* Preservar fluxos de alteração de senha, sessões ativas e configuração de conta.


* Preservar integridade do upload de avatar e visualização do perfil público.



#### 9. Critérios de Aceitação

* A amostra ao vivo reage em tempo real a qualquer modificação de configurações de leitura ou aparência.


* As seções de ajustes são navegadas fluidamente pelo menu lateral sem quebra de contexto.


* O upload de avatar aceita os formatos especificados com validação clara de tamanho.



#### 10. Testes e Validação

* Realizar upload de imagem válida e imagem maior que 2MB, verificando mensagens de validação.


* Modificar preferências de leitura e inspecionar a renderização ao vivo do texto de demonstração.



#### 11. Dependências e Riscos

* Dependência: Persistência de preferências de usuário no banco de dados / localStorage.
* Risco: Alterações na visualização afetarem estilos globais sem intenção. Mitigação: isolar estilos do preview dentro de escopo restrito de contêiner.

#### 12. Condição de Conclusão (DoD)

* Tela de Ajustes operando com menu lateral vertical, simulador de leitura integrado e fluxo de avatar funcional.

---

### Feature 08: Lixeira — Arquivo de Salvaguarda e Segurança

#### 1. Identificação e Objetivo

* **Área Afetada:** Gestão de Acervo / Lixeira (`/lixeira` ou equivalente).


* **Resultado Esperado:** Um cofre de custódia temporária que transmita segurança e tranquilidade ao leitor, com contagem regressiva visível dos 30 dias de retenção e barreiras deliberadas contra perda acidental de dados.



#### 2. Contexto e Justificativa

* `[DEFINIDO NO PLANEJAMENTO]` A tela tem aspecto de tabela crua de dados. O botão crítico "Esvaziar lixeira" está exposto no topo sem hierarquia de proteção, e os estudos descartados apresentam tags amarelas simples ("Expurgo em 24 dias") com botões pequenos de texto.



#### 3. Diagnóstico Necessário

* `[REQUER INSPEÇÃO NO CÓDIGO]` Inspecionar as entidades gerenciadas na lixeira: "Todos", "Livros" e "Estudos individuais".


* `[REQUER INSPEÇÃO NO CÓDIGO]` Inspecionar as mutations de "Restaurar" e "Excluir definitivamente", bem como o acionamento de esvaziamento total.



#### 4. Direção do Redesign

* `[DEFINIDO NO PLANEJAMENTO]`
1. Indicador visual de contagem regressiva da retenção temporal dos 30 dias por item.


2. Barra flutuante de ações em lote para restauração ou expurgo múltiplo com um único comando.
3. Barreira de segurança deliberada no botão "Esvaziar lixeira" (modal com confirmação explícita).





#### 5. Escopo de Implementação

* Redesenhar os cartões de itens descartados:
* Indicação clara do tipo (Livro vs Estudo).


* Barra de progresso sutil ou badge circular mostrando os dias restantes antes do expurgo automático.


* Origem do estudo (Livro de origem > Capítulo) em hierarquia visual limpa.




* Adicionar caixas de seleção (*checkboxes*) para seleção múltipla de itens.
* Proteger a ação de esvaziar lixeira com diálogo modal de confirmação reforçada.



#### 6. Interações e Animações

* `[COMPLEMENTO TÉCNICO PROPOSTO]` **Restauração de Estudo:** Ao clicar em restaurar, o cartão desvanece suavemente para cima (`transform: translateY(-20px)`, `opacity: 0`, 180ms), com toast de confirmação na base da tela ("Estudo restaurado para o livro de origem").


* `[COMPLEMENTO TÉCNICO PROPOSTO]` **Barra Flutuante de Seleção:** Ao marcar um ou mais checkboxes, a barra de ações em massa sobe da parte inferior da tela em 200ms.

#### 7. Responsividade e Acessibilidade

* Diálogo de confirmação de esvaziamento total com foco retido, `role="alertdialog"` e tecla `Esc` para cancelamento rápido.
* Seleção por teclado via tecla `Espaço` nos checkboxes e navegação via setas.

#### 8. Preservação Funcional

* Preservar filtros por abas: "Todos", "Livros", "Estudos individuais" com seus respectivos contadores.


* Preservar a regra de negócio de expurgo automático de 30 dias.


* Preservar ações individuais: Restaurar e Excluir definitivamente.



#### 9. Critérios de Aceitação

* O botão "Esvaziar lixeira" não permite exclusão imediata acidental sem confirmação explícita do usuário.


* Itens restaurados desaparecem da lista com transição suave e atualizam os contadores imediatamente.
* A barra de ações em lote permite restaurar múltiplos itens selecionados em uma única ação.

#### 10. Testes e Validação

* Restaurar um estudo individual e confirmar seu retorno à visualização de estudos normais.


* Testar exclusão definitiva com cancelamento e confirmação no modal de segurança.



#### 11. Dependências e Riscos

* Dependência: Sistema de notificações temporárias (*Toasts*).
* Risco: Tentativa de restaurar um estudo cujo livro de origem também está na lixeira. Mitigação: o sistema deve alertar o usuário e sugerir restaurar o livro em conjunto.

#### 12. Condição de Conclusão (DoD)

* Lixeira operando com contagem regressiva visual de expurgo, seleção em lote ativa e diálogo de segurança em esvaziamento total.

---

### Feature 09: Página Inicial sem Login (SEO) — Manifesto do Leitor Reflexivo

#### 1. Identificação e Objetivo

* **Área Afetada:** Landing Page Pública (`/` quando desconectado).


* **Resultado Esperado:** Um manifesto editorial de alto valor para leitores e pesquisadores, comunicando o método do Leitorum através de um simulador interativo das 4 dimensões e garantindo excelência em SEO e performance.



#### 2. Contexto e Justificativa

* `[DEFINIDO NO PLANEJAMENTO]` A página pública atual segue uma fórmula padronizada de startup: título centralizado, botões de ação repetitivos e três cartões com ícones ("Fichamento em 4 Dimensões", "Biblioteca em Camadas", "Privacidade e Soberania"). Não transmite a atmosfera intelectual e serena que o produto propõe.



#### 3. Diagnóstico Necessário

* `[REQUER INSPEÇÃO NO CÓDIGO]` Inspecionar a página pública (`LandingPage.tsx` ou equivalente) e suas tags de SEO (`next/head`, `Helmet` ou equivalente).


* `[REQUER INSPEÇÃO NO CÓDIGO]` Verificar as rotas públicas de conversão: "Criar Conta Gratuita" e "Já possuo conta (Entrar)".



#### 4. Direção do Redesign

* `[DEFINIDO NO PLANEJAMENTO]`
1. Composição editorial assimétrica com tipografia expressiva de abertura.
2. Simulador Interativo do Fichamento em 4 Dimensões: o visitante pode clicar nas abas (Resumo, Explicação, Conceitos, Referências) e experimentar o método de leitura diretamente na landing page, sem precisar criar conta de imediato.
3. Demonstrador dos 10 Temas do Leitorum integrado à página, permitindo alternar e comprovar a calma visual das paletas antes do cadastro.



#### 5. Escopo de Implementação

* Redesenhar a seção Hero com layout editorial e chamada visual forte.


* Substituir os 3 cartões estáticos por:


* *Simulador das 4 Dimensões:* componente interativo com trecho literário pré-carregado demonstrando as camadas de estudo.
* *Seção de Soberania de Dados:* explicação clara sobre privacidade, ausência de anúncios e software livre.




* Inserir dados estruturados Schema.org (`SoftwareApplication`, `EducationalApplication`) para otimização de busca orgânica.

#### 6. Interações e Animações

* `[COMPLEMENTO TÉCNICO PROPOSTO]` **Simulador Interativo:** Ao alternar entre as 4 dimensões, transição sutil de esmaecimento do texto explicativo em 150ms.
* `[COMPLEMENTO TÉCNICO PROPOSTO]` **Demonstrador de Temas:** Ao clicar em uma amostra de tema na landing page, as variáveis de cor da página pública mudam instantaneamente, demonstrando a versatilidade visual do Leitorum.

#### 7. Responsividade e Acessibilidade

* Taxa de contraste mínima de 7:1 (WCAG AAA) nos textos principais de leitura.
* Carregamento assíncrono de fontes para evitar *Flash of Invisible Text* (FOIT).

#### 8. Preservação Funcional

* Preservar links institucionais: "Sobre", "Apoie" e rodapé de software livre.


* Preservar fluxos de conversão: "Criar Conta Gratuita" e "Entrar".


* Manter rastreabilidade completa por motores de busca (sem conteúdo vital bloqueado por JavaScript pesado).

#### 9. Critérios de Aceitação

* O simulador das 4 dimensões é utilizável sem requisições de rede ou cadastro prévio.
* A página atinge pontuação superior a 95 no Google Lighthouse nos quesitos Performance, Acessibilidade e SEO.
* A página comunica com clareza a proposta de valor do Leitorum como ferramenta de estudo profundo.



#### 10. Testes e Validação

* Executar auditoria completa com Google Lighthouse em modo mobile e desktop.
* Testar indexação de metatags via ferramenta de pré-visualização de Open Graph e Schema.org.

#### 11. Dependências e Riscos

* Dependência: Rotas de autenticação ativas e operacionais.
* Risco: Aumento do bundle JavaScript inicial. Mitigação: isolar o simulador em carregamento dinâmico se necessário.

#### 12. Condição de Conclusão (DoD)

* Landing page pública no ar com o manifesto editorial, simulador interativo operando sem login e nota Lighthouse comprovada.

---

### Feature 10: Suíte de Correções Visuais e Polimento de Precisão (Reservada)

#### 1. Identificação e Objetivo

* **Área Afetada:** Sistema global do Leitorum (Componentes compartilhados e telas das Features 01 a 09).
* **Resultado Esperado:** Resolução integral e pontual de uma lista nominal de inconsistências visuais, artefatos de renderização e desvios de layout que serão fornecidos diretamente pelo mantenedor do produto.

#### 2. Contexto e Justificativa

* `[DEFINIDO NO PLANEJAMENTO]` Esta décima feature do roadmap está **estritamente reservada**. Nenhum bug deve ser inventado, antecipado ou suposto. O Antigravity não deve preencher este escopo com melhorias extras de redesign. A feature permanece em compasso de espera até que a lista nominal seja explicitamente enviada pelo usuário.

#### 3. Diagnóstico Necessário

* `[REQUER INSPEÇÃO NO CÓDIGO]` Aguardar o envio da lista nominal de bugs. Após o recebimento, inspecionar cada arquivo e seletor CSS apontado pelo mantenedor.

#### 4. Direção do Redesign

* `[DEFINIDO NO PLANEJAMENTO]` Intervenções cirúrgicas de fidelidade estética (*pixel perfection*), focando no alinhamento fino, espaçamentos e consistência visual entre navegadores.

#### 5. Escopo de Implementação

* Executar exclusivamente as correções catalogadas na listagem futura enviada pelo usuário.
* Nenhuma nova funcionalidade ou refatoração profunda deve ocorrer dentro desta feature.

#### 6. Interações e Animações

* Ajustes pontuais de sincronismo visual, eliminação de oscilações (*flickering*) em transições de layout ou estados de carregamento conforme apontado na lista de bugs.

#### 7. Responsividade e Acessibilidade

* Garantir que as correções pontuais não introduzam regressões em resoluções móveis ou quebras de contraste em qualquer um dos 10 temas.

#### 8. Preservação Funcional

* Preservar 100% das regras de negócio e estabilidade conquistadas nas Features 01 a 09.

#### 9. Critérios de Aceitação

* Todos os itens da listagem nominal de bugs fornecida pelo usuário resolvidos e verificados.
* Nenhuma regressão visual ou funcional identificada após os ajustes.

#### 10. Testes e Validação

* Validação visual item a item com base nos cenários reproduzidos a partir do reporte do usuário.

#### 11. Dependências e Riscos

* Dependência: Entrega prévia da lista nominal de bugs visuais pelo usuário e conclusão das Features 01 a 09.
* Risco: Ajustes de CSS pontuais gerarem efeitos colaterais em cascata. Mitigação: usar seletores restritos e testar em múltiplos temas.

#### 12. Condição de Conclusão (DoD)

* 100% dos bugs informados nominalmente validados como corrigidos na interface real e aprovados pelo mantenedor.

---

## 5. Ordem de Execução e Matriz de Dependências

O desenvolvimento deve seguir rigorosamente a ordem de precedência técnica e de fluxo de dados:

| Sequência | Feature | Racional de Precedência Técnica |
| --- | --- | --- |
| **1º** | **Feature 01: Livros + Header Global**<br> | Constrói a fundação do *App Shell* e o novo Header unificado, sobre o qual todas as páginas seguintes serão montadas.

 |
| **2º** | **Feature 05: Importar**<br> | Estabelece o motor de fichamento e a linguagem visual do estudo em camadas, que alimenta o restante da aplicação.

 |
| **3º** | **Feature 04: Inbox**<br> | Integra-se à ação de captura rápida do novo Header e define o padrão de triagem do sistema.

 |
| **4º** | **Feature 02: Destaques**<br> | Consome os dados e livros estruturados, consolidando o estilo de citações literárias.

 |
| **5º** | **Feature 03: Revisão**<br> | Constrói a bancada de fixação sobre os estudos e destaques já existentes no ecossistema.

 |
| **6º** | **Feature 07: Ajustes**<br> | Permite testar as preferências ergonômicas e parâmetros visuais contra os novos componentes.

 |
| **7º** | **Feature 08: Lixeira**<br> | Cria a camada de custódia e expurgo para os livros e estudos refatorados.

 |
| **8º** | **Feature 06: Amigos**<br> | Estabelece a conexão social a partir de bibliotecas e perfis já amadurecidos.

 |
| **9º** | **Feature 09: Landing Page (SEO)**<br> | Aplica a maturidade visual e os simuladores de estudo desenvolvidos nas etapas anteriores na vitrine externa.

 |
| **10º** | **Feature 10: Suíte de Correções Visuais** | Etapa final de refinamento e lapidação baseada na lista nominal de bugs fornecida pelo usuário. |

---

## 6. Estratégia de Testes, Validação e Prevenção de Regressões

### 6.1 Protocolo de Validação Visual dos 10 Temas

1. Testar o componente modificado em pelo menos dois temas de polaridades opostas (ex: Tema Claro Padrão vs Tema Escuro Noturno) e em um tema de tom sépia/papel.
2. Confirmar que não existem textos invisíveis, bordas de alto contraste indesejadas ou seletores de cor com contraste inadequado.

### 6.2 Protocolo de Responsividade e Quebra de Viewport

* **Desktop Amplo (1440px+):** Verificar uso harmonioso do espaço e alinhamento do grid.
* **Laptop / Desktop Compacto (1024px a 1280px):** Verificar que o Header não transborda horizontalmente e mantém as 4 abas primárias e o menu "Mais ▾" intactos.


* **Tablet (768px a 1023px):** Confirmar conversão de layouts de duas colunas para abas ou colunas empilhadas.
* **Smartphone (375px a 430px):** Confirmar que o conteúdo não gera scroll horizontal involuntário e que alvos de clique possuem no mínimo 44x44px.

### 6.3 Protocolo de Prevenção de Regressão Funcional

* Toda tela que possuir formulário de envio deve ter seus fluxos de submissão com sucesso e com erro de validação testados.
* Todas as rotas de navegação anteriores devem permanecer idênticas ou redirecionadas transparentemente.
* Não descartar campos de API ou propriedades de dados existentes nos objetos retornados do backend.

---

## 7. Critérios Globais de Conclusão do Roadmap 0.8

O Roadmap 0.8 será considerado plenamente concluído somente quando todas as seguintes condições forem satisfeitas:

1. **Diferenciação Estilística Comprovada:** Cada uma das nove telas possui silhueta visual e composição próprias, não se comportando como variações de um mesmo template de CRUD genérico.


2. **Header Despoluído e Estável:** O cabeçalho funciona em três blocos, acomodando buscas, capturas e perfil sem quebra de linha em resoluções de desktop e laptop.


3. **Respeito aos 10 Temas:** Todos os dez temas nativos do Leitorum operam sem qualquer inconsistência cromática.
4. **Respeito a Movimento Reduzido:** Emulação com `prefers-reduced-motion` ativado desativa todas as animações espaciais sem quebrar o layout.
5. **Acessibilidade Universal:** Toda navegação e interação principal pode ser concluída integralmente via teclado sem armadilhas de foco (*focus traps*).
6. **Zero Erros de Console:** Navegação por todas as rotas ocorre sem alertas de erro de renderização no console de desenvolvimento.
7. **Suíte Reservada Atendida:** A Feature 10 foi executada apenas após a entrega formal da listagem nominal de bugs pelo mantenedor, com todos os seus itens verificados.
</USER_REQUEST>
<ADDITIONAL_METADATA>
The current local time is: 2026-10-10T14:48:39-03:00.
</ADDITIONAL_METADATA>