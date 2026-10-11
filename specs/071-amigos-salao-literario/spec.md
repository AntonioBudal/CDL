# Feature Specification: F0.8.06 — Amigos: Salão Literário e Círculos de Estudo

**Feature Branch**: `071-amigos-salao-literario`  
**Created**: 2026-10-11  
**Status**: Draft  
**Input**: Roadmap 0.8 — Feature 06: "Amigos — Salão Literário e Círculos de Estudo" (Área: `/amigos`, Redesign social, Cartão de Identidade do Leitor / Ex-Líbris Digital, Descoberta de pares e correspondência literária).

---

## 1. Contexto & Visão de Produto

A área de Amizades (`/amigos`) do Leitorum conecta leitores, pesquisadores e estudantes em círculos de estudo mútuos e troca de anotações literárias.

Atualmente, a tela opera com limitações visuais e ergonômicas significativas:
1. **Identidade Oculta e Impessoal**: O identificador de usuário (`@identificador`) só é exibido de forma secundária no interior do estado vazio da primeira aba. Caso o leitor já possua conexões, seu próprio identificador fica oculto, dificultando o compartilhamento e a expansão do seu círculo.
2. **Estética de CRUD Genérico**: As listas de amigos, solicitações e bloqueados se assemelham a tabelas administrativas cinzentas, sem o calor, a elegância e a atmosfera de um "Salão Literário" ou clube de correspondência intelectual.
3. **Falta de Feedback Tátil**: O botão de cópia do identificador carece de feedback visual característico do Leitorum, e não há integração com compartilhamento móvel nativo (*Web Share API*).
4. **Descoberta Árida**: A aba "Descobrir Leitores" apresenta um campo de busca isolado sem orientação ou sugestões para novos usuários.

O redesenho transforma `/amigos` em um **Salão Literário e Círculos de Estudo**:
- **Cartão de Identidade do Leitor (*Bookplate Card* / Ex-Líbris Digital)** permanente no topo, exibindo o perfil literário do usuário, seu `@identificador`, contadores de afinidade e ação de compartilhamento com selo de confirmação esmaecendo em 1200ms.
- **Cartas de Conexão Literária**: Redesenho dos cartões de amigos e solicitações com hierarquia clara, badges semânticos de status e ações contextuais bem distribuídas.
- **Círculos de Estudo & Descoberta Guiada**: Estados vazios ricos, sugestões temáticas de exploração e navegação fluida pelas 4 abas sociais com contadores em tempo real.
- **Imunidade Cromática e Acessibilidade**: Adaptação perfeita aos 10 temas visuais do Leitorum, alvos móveis $\ge 44 \times 44$px e zero emojis.

---

## 2. User Scenarios & Testing *(Prioritised)*

### User Story 1 - Cartão de Identidade do Leitor (*Bookplate Card*) e Compartilhamento Ágil (Priority: P1) 🎯 MVP

**Objetivo**: Como leitor ativo, desejo visualizar meu Cartão de Identidade Literária (*Ex-Líbris*) em destaque no topo da tela com meu `@identificador` e copiá-lo com feedback imediato, para compartilhá-lo facilmente com colegas de estudo.

**Why this priority**: É a porta de entrada para qualquer conexão social no Leitorum; sem visibilidade imediata do próprio identificador, a formação de círculos literários é bloqueada.

**Independent Test**: Acessar `/amigos`, visualizar o Bookplate Card no topo contendo o `@identificador` do usuário logado, clicar em "Copiar" e validar a animação do selo de confirmação esmaecendo em 1200ms com o texto copiado para o clipboard.

**Acceptance Scenarios**:
1. **Given** um leitor autenticado na tela `/amigos`,  
   **When** a página é renderizada,  
   **Then** o Cartão de Identidade do Leitor (*Bookplate Card*) é exibido no topo, contendo avatar/iniciais, nome de exibição, bio literária (se preenchida), contador de conexões e o `@identificador`.
2. **Given** o botão de cópia do identificador no Bookplate Card,  
   **When** o leitor clica no botão,  
   **Then** o texto `@identificador` é copiado para a área de transferência e o botão exibe o selo de confirmação visual com esmaecimento suave em 1200ms.
3. **Given** um dispositivo móvel com suporte a `navigator.share` (Web Share API),  
   **When** o leitor toca em "Compartilhar Perfil",  
   **Then** o diálogo nativo do sistema operacional é acionado com link e texto de convite formatado do Leitorum.

---

### User Story 2 - Salão Literário: Cartões de Conexão e Ações Contextuais (Priority: P1) 🎯 MVP

**Objetivo**: Como leitor com conexões sociais ativas, desejo visualizar meus amigos e solicitações em cartões elegantes com tipografia editorial e acionar ações de relacionamento sem formulários confusos.

**Why this priority**: Converte a experiência social fria em um encontro estético de leitores, permitindo gerenciar pedidos de amizade e círculos com clareza.

**Independent Test**: Acessar a aba "Círculo de Leitura" e a aba "Solicitações", verificando a renderização dos cartões com data de conexão, botões acessíveis e confirmações defensivas para remoção/bloqueio.

**Acceptance Scenarios**:
1. **Given** a aba "Círculo de Leitura" com conexões existentes,  
   **When** visualizada pelo leitor,  
   **Then** cada amigo é apresentado em um cartão editorial com avatar, nome, identificador e botão contextual para visitar a estante pública do leitor (`/u/:username`).
2. **Given** a aba "Solicitações" com convites pendentes,  
   **When** o leitor recebe um novo pedido,  
   **Then** o cartão exibe opções diretas "Aceitar Conexão" e "Recusar", com atualização reativa imediata dos contadores e da lista.
3. **Given** a intenção de desfazer amizade ou bloquear um usuário,  
   **When** a ação é acionada,  
   **Then** o sistema solicita confirmação defensiva antes de efetivar a desconexão ou bloqueio.

---

### User Story 3 - Descoberta de Pares e Estados Vazios Enriquecidos (Priority: P2)

**Objetivo**: Como novo usuário sem amigos cadastrados, desejo ver um estado acolhedor ("Círculo em Formação") e explorar outros leitores por temas e interesses intelectuais na aba "Descobrir Leitores".

**Why this priority**: Elimina a sensação de "sala vazia e abandonada" quando o usuário ainda não adicionou ninguém à rede.

**Independent Test**: Acessar a aba de descoberta, digitar um termo de busca e confirmar resultados em tempo real com debounce; se a busca estiver vazia, exibir sugestões acolhedoras de temas intelectuais.

**Acceptance Scenarios**:
1. **Given** um usuário sem nenhuma amizade cadastrada,  
   **When** ele acessa a aba "Círculo de Leitura",  
   **Then** a interface apresenta o estado editorial "Círculo em Formação", explicando o propósito da correspondência literária e incentivando o compartilhamento do identificador.
2. **Given** a aba "Descobrir Leitores",  
   **When** o leitor digita no campo de busca,  
   **Then** a consulta é executada com debounce de 300ms exibindo cartões de perfil com botão "Solicitar Conexão".

---

### User Story 4 - Navegação por Abas com Contadores e Imunidade Cromática (Priority: P2)

**Objetivo**: Como leitor que navega pelo salão social, desejo alternar facilmente entre as 4 abas com contadores numéricos precisos e garantia total de contraste e conforto visual em qualquer um dos 10 temas.

**Why this priority**: Garante consistência arquitetural, acessibilidade WAI-ARIA e imunidade ao design system do Leitorum.

**Independent Test**: Percorrer as 4 abas via teclado (Tab e setas), verificar atributos `aria-selected` e `role="tab"`, e constatar adaptação homogênea nos temas claro, escuro, sépia e E-Ink.

**Acceptance Scenarios**:
1. **Given** a barra de navegação social,  
   **When** inspecionada,  
   **Then** apresenta 4 abas: `Círculo de Leitura` (amigos), `Solicitações`, `Descobrir Leitores` e `Bloqueados`, com badges dinâmicos para solicitações não lidas.
2. **Given** qualquer um dos 10 temas visuais ativos,  
   **When** a tela `/amigos` é renderizada,  
   **Then** 100% dos estilos consomem variáveis semânticas (`var(--color-surface)`, `var(--color-text)`, etc.), sem cores hexadecimais saturadas fixas e sem emojis.
3. **Given** navegação em telas móveis,  
   **When** os botões e abas são tocados,  
   **Then** todos possuem dimensão mínima de toque de $44 \times 44$px.

---

## 3. Edge Cases

- **Usuário sem Username Definido**: Caso o perfil ainda não possua username preenchido, o Bookplate Card exibe link amigável para configurá-lo em Ajustes de Perfil.
- **Falha de Clipboard no Navegador**: Se `navigator.clipboard.writeText` for bloqueado por políticas de segurança, o sistema exibe o identificador em um campo de texto selecionável manual sem travar a interface.
- **Navegador sem Suporte a Web Share API**: Em ambientes desktop ou navegadores antigos, o botão de compartilhamento oculta a chamada nativa e aciona a cópia rápida do link público do perfil.
- **Busca Rápida com Latência**: O campo de busca de leitores cancela requisições anteriores via debounce e exibe estado sutil de carregamento sem congelar a digitação.

---

## 4. Requirements *(Mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE exibir permanentemente no topo da tela `/amigos` o componente `BookplateCard.vue` (Ex-Líbris Digital do Leitor) com dados do usuário logado.
- **FR-002**: O `BookplateCard.vue` DEVE apresentar avatar/iniciais, nome de exibição, bio literária, contagem de conexões e o `@identificador` do leitor.
- **FR-003**: O botão de cópia do identificador DEVE fornecer feedback visual imediato (*Selo de Cópia*) com duração de 1200ms e esmaecimento suave.
- **FR-004**: O sistema DEVE suportar compartilhamento nativo via `navigator.share` (Web Share API) quando disponível no dispositivo, compartilhando o link do perfil.
- **FR-005**: O sistema DEVE fornecer navegação segmentada em 4 abas: `Círculo de Leitura`, `Solicitações`, `Descobrir Leitores` e `Bloqueados`, com contadores numéricos dinâmicos.
- **FR-006**: Os amigos DEVEM ser renderizados em cartões de conexão literária contendo data de amizade e link direto para a estante pública (`/u/:username`).
- **FR-007**: A aba de solicitações DEVE exibir botões evidentes para aceitar ou recusar convites pendentes e cancelar pedidos enviados.
- **FR-008**: O sistema DEVE solicitar confirmação defensiva antes de remover um amigo ou bloquear um usuário.
- **FR-009**: A aba "Descobrir Leitores" DEVE implementar campo de busca com debounce de 300ms e renderizar cartões de leitores encontrados com botão de solicitação de amizade.
- **FR-010**: A interface DEVE exibir estados vazios editoriais acolhedores ("Círculo em Formação") na ausência de amigos ou solicitações, estimulando a troca intelectual.
- **FR-011**: O sistema DEVE tratar falhas de carregamento com notificações editoriais no padrão do design system (`role="alert"`), eliminando mensagens técnicas cruas.

### Non-Functional & Quality Constraints

- **NR-001 (Imunidade Cromática)**: 100% de uso de tokens semânticos dos 10 temas (`var(--color-surface)`, `var(--color-text)`, etc.), banindo hexadecimais rígidos e classes arbitrárias de cores.
- **NR-002 (Zero Emojis)**: Uso exclusivo de ícones SVG semânticos (`<Icon name="..." />`); zero emojis em textos, badges ou botões.
- **NR-003 (Acessibilidade WAI-ARIA)**: Rótulos `aria-label`, estados `aria-selected` em abas, `role="tablist"` e anéis de foco visíveis (`:focus-visible`).
- **NR-004 (Ergonomia Tátil)**: Alvos de toque $\ge 44 \times 44$px para todos os botões no layout móvel.
- **NR-005 (Preservação de Dados e Backend)**: Nenhuma alteração no backend FastAPI (`backend/app/routers/friends.py` e `profile.py`) nem em tabelas/migrações do SQLite.

---

## 5. Success Criteria *(Mandatory)*

### Measurable Outcomes

- **SC-001**: O leitor consegue localizar e copiar seu identificador em menos de 2 segundos a partir do carregamento de `/amigos`.
- **SC-002**: A microinteração do selo de cópia conclui em exatamente 1200ms com transição fluida a 60 FPS acelerada por GPU.
- **SC-003**: 100% das ações sociais (copiar, aceitar, recusar, remover, buscar) são operáveis via teclado e leitor de tela sem barreiras.
- **SC-004**: 100% das suítes de testes (`npm test`, `npm run build`, `pytest backend/tests`) são aprovadas com zero falhas e zero erros de tipo.

---

## 6. Assumptions & Dependencies

- **Endpoints de Backend Preservados**: As APIs existentes `/api/friends` e `/api/profile` atendem plenamente às necessidades do Salão Literário.
- **Rotas Públicas de Usuário**: A rota `/u/:username` já existe no frontend e continuará servindo como destino para a visualização da estante pública de outros leitores.
- **Composables Reutilizados**: `useFriends.ts` e `useProfile.ts` continuarão sendo consumidos como fontes de verdade do estado social.
