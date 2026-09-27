# Feature Specification: F09 — Notificações e Atividade Social

**Feature Branch**: `036-notificacoes-atividade-social`

**Created**: 2026-09-26

**Status**: Draft

**Input**: User description: "F09 — Notificações e Atividade Social: Implementar um centro de eventos unificado que conecta solicitações de amizade, novos compartilhamentos e avisos administrativos à interface do leitor."

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Central de Notificações e Contador de Não Lidos (Priority: P1)

Como leitor na plataforma Leitorum, quero visualizar um indicador claro de novidades e notificações não lidas no cabeçalho da aplicação e acessar uma lista consolidada dos eventos recentes, para manter-me informado sobre interações sociais e atividades relevantes sem interromper meu fluxo de leitura.

**Why this priority**: É a fundação do centro de eventos. Sem um ponto de entrada visível e um contador de não lidas, os leitores não percebem quando recebem interações ou compartilhamentos de estudos.

**Independent Test**: Pode ser testado de forma independente disparando um evento de teste para o usuário e verificando que o badge de contagem no cabeçalho é atualizado e que ao clicar no ícone um painel dropdown/gaveta exibe a notificação formatada com data, avatar/ícone e descrição.

**Acceptance Scenarios**:

1. **Given** um leitor autenticado com 3 notificações não lidas, **When** ele acessa qualquer tela da aplicação, **Then** o ícone de notificações no cabeçalho exibe um indicador numérico destacado com o valor "3".
2. **Given** o painel de notificações aberto, **When** o usuário clica no botão "Marcar todas como lidas", **Then** todas as notificações são marcadas com timestamp de leitura e o contador do cabeçalho é zerado imediatamente.
3. **Given** uma notificação não lida na lista, **When** o usuário clica na notificação individual, **Then** a notificação é marcada como lida e o usuário é direcionado para o recurso associado (ex.: perfil do amigo ou estudo compartilhado).

---

### User Story 2 - Ações Rápidas de Amizade no Painel de Notificações (Priority: P2)

Como leitor que recebeu uma solicitação de amizade, quero poder aceitar ou recusar o pedido diretamente a partir do item na lista de notificações, sem precisar navegar até a página completa de Amizades.

**Why this priority**: Reduz o atrito de conexões sociais e proporciona fluidez operacional, permitindo que a interação seja concluída em apenas um clique.

**Independent Test**: Um usuário B envia solicitação de amizade para o usuário A; o usuário A abre o painel de notificações, clica em "Aceitar" diretamente no card da notificação e a amizade torna-se confirmada tanto na listagem social quanto no status da notificação.

**Acceptance Scenarios**:

1. **Given** uma notificação do tipo `friend_request`, **When** o usuário clica em "Aceitar", **Then** a relação de amizade transita para `accepted`, o remetente recebe notificação de aceite e a notificação exibe confirmação visual de amizade estabelecida.
2. **Given** uma notificação do tipo `friend_request`, **When** o usuário clica em "Recusar", **Then** o pedido é cancelado sem gerar notificação hostil ao solicitante e o card de notificação é atualizado para refletir o encerramento da solicitação.

---

### User Story 3 - Notificações de Estudos e Livros Compartilhados (Priority: P3)

Como leitor que colabora em estudos, quero ser notificado quando uma amizade compartilhar uma anotação, capítulo ou livro comigo, para poder consultar o novo material no meu ritmo.

**Why this priority**: Fortalece a troca intelectual entre leitores parceiros, dando visibilidade imediata ao conteúdo compartilhado via ACL.

**Independent Test**: Usuário A compartilha um estudo com Usuário B; Usuário B recebe notificação do tipo `study_shared` contendo o título da obra, o autor do compartilhamento e link direto para a tela de leitura compartilhada.

**Acceptance Scenarios**:

1. **Given** uma nova permissão de compartilhamento concedida a um leitor, **When** o sistema processa a concessão, **Then** uma notificação do tipo `study_shared` é gerada para o destinatário com o título do livro/estudo e nome do remetente.
2. **Given** o clique em uma notificação de estudo compartilhado, **When** a rota correspondente é acionada, **Then** o estudo compartilhado é aberto diretamente na visualização de leitura.

---

### User Story 4 - Avisos Administrativos e Alertas do Sistema (Priority: P4)

Como usuário do Leitorum, quero receber comunicados importantes da plataforma (ex.: manutenções programadas, comunicados de segurança ou orientações da administração) de forma visível e centralizada.

**Why this priority**: Garante que o administrador possa manter a base de leitores informada sobre manutenções, novidades de infraestrutura ou regras de convivência.

**Independent Test**: Um administrador emite um aviso do sistema; todos os leitores elegíveis recebem uma notificação de prioridade visual destacada do tipo `system_alert`.

**Acceptance Scenarios**:

1. **Given** um alerta emitido pelo sistema, **When** o leitor abre sua central de notificações, **Then** o item é exibido com ícone distintivo de alerta institucional e texto informativo claro.

---

### Edge Cases

- **Leitor sem conexões ou eventos:** Exibição elegante de estado vazio com ilustração ou mensagem motivadora de leitura quando a lista de notificações estiver vazia.
- **Solicitação de amizade já tratada em outra aba ou dispositivo:** Se o leitor aceitar a amizade na tela `/amigos` em uma janela e depois clicar em "Aceitar" no dropdown de notificações em outra janela, o sistema deve tratar graciosamente idempotência, exibindo "Esta solicitação já foi respondida".
- **Estudo compartilhado excluído posteriormente:** Se o autor revogar o compartilhamento ou mover o estudo para a lixeira após emitir a notificação, ao clicar nela o leitor deve ver aviso amigável: "Este conteúdo não está mais disponível ou o compartilhamento foi revogado".
- **Volume alto de notificações acumuladas:** A lista deve exibir paginação ou rolagem contínua com limite inicial (ex.: 20 mais recentes) e retenção automática que descarta itens lidos antigos após período determinado.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE fornecer um centro de notificações acessível através de ícone interativo na barra superior de navegação da interface.
- **FR-002**: O ícone no cabeçalho DEVE exibir um badge visual dinâmico com a quantidade de notificações pendentes de leitura (`unread_count`).
- **FR-003**: As notificações DEVEM ser atualizadas no cliente web através de polling periódico leve (intervalo configurável de 45 segundos) combinado com revalidação imediata sob demanda ao focar a aba do navegador, ao navegar entre rotas ou ao abrir o painel de notificações.
- **FR-004**: O sistema DEVE registrar automaticamente notificações quando:
  - Um leitor recebe uma solicitação de amizade (`friend_request`);
  - Uma solicitação de amizade enviada é aceita (`friend_accepted`);
  - Um estudo ou livro é compartilhado com o usuário (`study_shared`);
  - Um comunicado geral ou alerta da plataforma é emitido (`system_alert`).
- **FR-005**: Notificações do tipo solicitação de amizade DEVEM conter botões de ação rápida para "Aceitar" e "Recusar" diretamente no próprio card do painel de notificações. Ao acionar a ação, o card DEVE permanecer visível na lista com os botões substituídos por um feedback visual inline imediato (ex.: "Amizade aceita" ou "Solicitação recusada"), marcando o item como lido e decrementando o contador do cabeçalho sem remoção abrupta.
- **FR-006**: O leitor DEVE poder marcar notificações individuais como lidas através de interação com o item.
- **FR-007**: O leitor DEVE poder marcar todas as notificações acumuladas como lidas através de ação única ("Marcar todas como lidas").
- **FR-008**: O sistema DEVE suportar alertas institucionais e avisos administrativos (`system_alert`), implementados através da criação de registros individuais na entidade `Notification` para cada usuário ativo no momento do envio, garantindo rastreamento autônomo de leitura (`read_at`) por leitor.
- **FR-009**: O sistema DEVE implementar rotina de purga ou arquivamento de notificações lidas antigas para evitar crescimento ilimitado do banco de dados (retenção padrão de 60 dias para notificações já lidas).
- **FR-010**: A emissão de notificações DEVE ocorrer de maneira desacoplada, de modo que uma falha transitória na gravação de notificação não impeça a conclusão da operação principal (ex.: criação de amizade ou concessão de permissão).

---

### Key Entities

- **Notification**:
  - `id`: Identificador único (UUID).
  - `user_id`: Identificador do usuário destinatário da notificação.
  - `actor_id`: Identificador do usuário que originou o evento (opcional, nulo para alertas de sistema).
  - `event_type`: Categoria do evento (`friend_request`, `friend_accepted`, `study_shared`, `system_alert`).
  - `payload`: Metadados estruturados em formato flexível (título do estudo, identificadores, rota de destino, mensagem complementar).
  - `read_at`: Timestamp de quando o usuário visualizou/marcou a notificação (nulo se não lida).
  - `created_at`: Timestamp de geração do evento.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: O leitor visualiza o número de eventos não lidos no cabeçalho imediatamente ao carregar qualquer tela do sistema.
- **SC-002**: A abertura do painel de notificações e renderização dos itens recentes ocorre de forma instantânea (em menos de 300ms na interface).
- **SC-003**: 100% das ações rápidas de amizade (aceitar/recusar) executadas a partir da notificação surtem efeito no banco de dados sem exigir recarregamento da página.
- **SC-004**: O usuário consegue limpar todo o indicador de eventos não lidos com um único clique na ação "Marcar todas como lidas".
- **SC-005**: Notificações lidas com mais de 60 dias de existência são automaticamente purgadas sem degradação do banco de dados SQLite local.

---

## Assumptions

- A infraestrutura de autenticação multiusuário (F01/F02), sistema de amizades (F06) e compartilhamento de recursos (F07) já está estabelecida e operacional.
- O volume típico de notificações por usuário em ambiente pessoal/rede privada é moderado, dispensando sistemas pesados de mensageria externa (como RabbitMQ ou Kafka).
- A interface opera em processo único local servido por Uvicorn/FastAPI e empacotada com Vue 3.
- Notificações são puramente informativas e orientadas à experiência do usuário, nunca substituindo o controle de acesso de segurança (autorização permanece checada no servidor em cada requisição).
