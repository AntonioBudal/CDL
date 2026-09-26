# Feature Specification: F06 — Sistema de Amizades

**Feature Branch**: `033-sistema-de-amizades`

**Created**: 2026-09-25

**Status**: Ready for Planning

**Input**: User description: "F06 — Sistema de Amizades: Criar a infraestrutura de conexão social entre usuários, com ciclo de vida completo de solicitações, aprovações e mecanismos de proteção."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Solicitação, Aceite e Recusa de Amizade (Priority: P1)

Como um leitor autenticado no Caderno de Leitura, desejo enviar solicitações de amizade para outros leitores da rede a partir do seu `@username` ou do seu perfil público, bem como aceitar ou recusar solicitações recebidas, para que possamos estabelecer vínculos mútuos de confiança e compartilhar o progresso dos nossos estudos.

**Why this priority**: Estabelece o núcleo indispensável (MVP) da conexão social no sistema. Sem o fluxo bilateral de solicitação e aceite, nenhuma funcionalidade subsequente de amizades ou compartilhamento seletivo entre amigos (F07) pode operar.

**Independent Test**: Pode ser testado de ponta a ponta criando dois usuários distintos (ex.: Leitor A e Leitor B). O Leitor A envia solicitação para o Leitor B; o Leitor B visualiza a solicitação pendente e a aceita; ambos passam a constar mutuamente como amigos com vínculo ativo. Em seguida, testa-se a recusa de uma solicitação, confirmando que o vínculo retorna a nulo sem erros.

**Acceptance Scenarios**:

1. **Envio com Sucesso**:
   - **Given** que o usuário A está autenticado e o usuário B existe, está ativo e não bloqueou A;
   - **When** o usuário A envia uma solicitação de amizade para `@username_b`;
   - **Then** o sistema registra a solicitação com status pendente, define A como o autor da ação (`action_user_id`), e ambos visualizam o status apropriado ("Solicitação enviada" para A e "Solicitação recebida" para B).

2. **Aceite de Solicitação**:
   - **Given** que o usuário B possui uma solicitação pendente enviada por A;
   - **When** o usuário B aciona a opção "Aceitar";
   - **Then** o estado da conexão passa para aceito/amigos, e ambos aparecem mutuamente em suas respectivas listas de amigos ativos.

3. **Recusa de Solicitação**:
   - **Given** que o usuário B possui uma solicitação pendente enviada por A;
   - **When** o usuário B aciona a opção "Recusar";
   - **Then** a pendência é removida do sistema e a relação retorna ao estado neutro ("sem vínculo"). O usuário A fica livre para reenviar solicitações futuras; caso o usuário B deseje impedir novos envios em definitivo, deve utilizar a ferramenta de bloqueio ("Bloquear").

4. **Prevenção de Auto-Amizade**:
   - **Given** que o usuário A está autenticado;
   - **When** o usuário A tenta enviar solicitação para si mesmo;
   - **Then** o sistema rejeita a operação com erro claro e nenhum vínculo é registrado.

---

### User Story 2 - Cancelamento e Desfazimento de Amizade (Priority: P2)

Como um leitor que enviou uma solicitação por engano ou que deseja encerrar um vínculo de amizade anterior, quero poder cancelar uma solicitação ainda pendente ou desfazer uma amizade ativa a qualquer momento, para manter o controle total sobre meus relacionamentos sociais.

**Why this priority**: Garante autonomia ao usuário para revogar ações enviadas e gerenciar sua lista de amigos de forma soberana e reversível.

**Independent Test**: O usuário A envia solicitação a B e a cancela antes da resposta de B; a solicitação é removida e a interface volta ao estado "sem vínculo". O usuário A e B são amigos; o usuário A clica em "Desfazer amizade"; o vínculo é desfeito imediatamente para ambos sem efeitos colaterais.

**Acceptance Scenarios**:

1. **Cancelamento de Solicitação Pendente**:
   - **Given** que o usuário A enviou uma solicitação para B e esta ainda está pendente;
   - **When** o usuário A clica em "Cancelar solicitação";
   - **Then** a pendência é removida do sistema e o usuário B não mais a visualiza na sua caixa de entrada.

2. **Desfazer Amizade Ativa**:
   - **Given** que os usuários A e B possuem amizade aceita e mútua;
   - **When** qualquer um dos dois aciona a opção "Desfazer amizade" e confirma a ação;
   - **Then** o vínculo de amizade é encerrado imediatamente, ambos deixam de ser listados como amigos e qualquer permissão restrita a amigos perde o efeito de forma instantânea.

---

### User Story 3 - Bloqueio, Desbloqueio e Blindagem contra Contato Indesejado (Priority: P3)

Como um leitor do sistema, desejo bloquear usuários específicos para impedir completamente que eles visualizem meu perfil, vejam meu dashboard, me enviem solicitações ou me encontrem na busca, garantindo segurança e tranquilidade pessoal.

**Why this priority**: Requisito crítico de privacidade e segurança pessoal em plataformas multiusuário. O bloqueio deve operar em camada profunda (servidor) e em ambas as direções para evitar assédio e exposição indevida.

**Independent Test**: O usuário A bloqueia o usuário B. Ao pesquisar por usuários descobríveis, B não encontra A e A não encontra B. Ao tentar acessar diretamente a URL do perfil público de A (`/@username_a`), B recebe erro de perfil não encontrado (404 Not Found), prevenindo enumeração. Solicitações anteriores são invalidadas imediatamente.

**Acceptance Scenarios**:

1. **Bloqueio a Partir de Qualquer Estado**:
   - **Given** que o usuário A está autenticado e deseja bloquear B (sejam estranhos, pendentes ou amigos prévios);
   - **When** o usuário A aciona "Bloquear usuário" e confirma;
   - **Then** qualquer amizade ou pendência anterior é dissolvida e o estado é convertido para bloqueado, com A como autor do bloqueio (`action_user_id`).

2. **Blindagem de Visibilidade e Busca Bilateral**:
   - **Given** que A bloqueou B;
   - **When** B realiza buscas por usuários ou tenta navegar para a página de perfil ou recursos de A;
   - **Then** o sistema age como se A não existisse para B (retorno vazio na busca e HTTP 404 em rotas diretas), protegendo totalmente o bloqueador.

3. **Desbloqueio Consciente**:
   - **Given** que o usuário A bloqueou B e acessa sua lista de usuários bloqueados;
   - **When** o usuário A aciona "Desbloquear";
   - **Then** o registro de bloqueio é removido, retornando a relação ao estado neutro ("sem vínculo"), sem recriar amizades prévias automaticamente.

---

### User Story 4 - Hub Social de Amigos e Descoberta de Leitores (Priority: P4)

Como um leitor que deseja interagir com outros membros da rede, quero acessar uma rota e visão dedicada de amizades (`/amigos`), acessível a partir da barra de navegação superior, para visualizar meus amigos atuais, solicitações pendentes (recebidas e enviadas), usuários bloqueados e encontrar novos leitores descobríveis com indicação clara do status da nossa relação.

**Why this priority**: Fornece a experiência visual, acessível e centralizada para que o usuário gerencie seus relacionamentos sociais sem atrito.

**Independent Test**: O usuário acessa a interface de Amigos; visualiza abas bem delimitadas ("Amigos", "Solicitações", "Bloqueados"); na aba de solicitações recebidas, vê o nome, avatar e data da solicitação com botões acessíveis de ação; ao buscar leitores descobríveis, cada cartão exibe o botão contextual correto ("Adicionar", "Pendente", "Amigo").

**Acceptance Scenarios**:

1. **Visualização Centralizada por Abas**:
   - **Given** que o usuário está autenticado;
   - **When** acessa a seção de Amigos;
   - **Then** visualiza a contagem consolidada de amigos, crachás numéricos com pendências não respondidas e listas organizadas por status.

2. **Indicador de Relação nos Perfis e Cartões**:
   - **Given** que o usuário navega pelo perfil público de outro leitor;
   - **When** a página é renderizada;
   - **Then** um botão de ação dinâmico reflete com precisão o estado ("Conectar", "Solicitação enviada", "Responder solicitação", "Amigos" ou "Bloqueado").

3. **Respeito à Privacidade na Exibição do Perfil**:
   - **Given** que um visitante consulta o perfil público de um usuário;
   - **Then** o perfil exibe exclusivamente o contador quantitativo de amigos mútuos ("X Amigos"), mantendo a listagem nominal confidencial e reservada ao próprio usuário titular.

---

### Edge Cases

- **Solicitações Cruzadas Simultâneas**: Se o usuário A solicita amizade a B e, quase simultaneamente, o usuário B solicita amizade a A antes de ver a solicitação de A, o sistema deve converter atomicamente a conexão para "aceito/amigos", reconhecendo a intenção mútua sem erro de duplicidade ou chave única.
- **Usuário Alvo Inativo ou Excluído**: Se uma conta for suspensa ou excluída enquanto há solicitações pendentes ou amizade ativa, o sistema deve ocultar essas conexões e rejeitar novas tentativas de solicitação com mensagem amigável.
- **Tentativa de Solicitação para Usuário Bloqueador**: Se B bloqueou A, e A tenta enviar solicitação para B via API direta, a resposta deve ser `404 Not Found` (como se B não existisse) para não confirmar nem revelar a existência do bloqueio.
- **Alteração de Username**: Se o usuário A alterar seu `@username` nas configurações de perfil, todos os relacionamentos de amizade e solicitações existentes devem permanecer intactos (pois são vinculados via identificador único imutável `user_id`).
- **Remoção de Usuário Descobrível**: Se um usuário desmarcar a opção "Tornar meu perfil descobrível na busca", ele não deve mais aparecer em buscas genéricas por novos amigos, mas continua acessível diretamente por link e pelos amigos existentes.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE fornecer um modelo de dados relacional para gerenciar relacionamentos de amizade entre pares de usuários (`user_id_a`, `user_id_b`), garantindo unicidade por par de identificadores independentemente da ordem.
- **FR-002**: O sistema DEVE suportar os estados canônicos de relacionamento: `pending` (pendente), `accepted` (amigos aceitos) e `blocked` (bloqueado), registrando qual usuário disparou a última transição (`action_user_id`).
- **FR-003**: O sistema DEVE proibir expressamente relacionamentos reflexivos (um usuário não pode solicitar amizade ou bloquear a si mesmo).
- **FR-004**: O sistema DEVE disponibilizar endpoint para enviar solicitação de amizade a partir do `@username` de destino (`POST /api/friends/request/{username}`).
- **FR-005**: O sistema DEVE disponibilizar endpoint para aceitar uma solicitação pendente recebida (`POST /api/friends/accept/{request_id}`), restrito exclusivamente ao destinatário da solicitação.
- **FR-006**: O sistema DEVE disponibilizar endpoint para recusar uma solicitação pendente recebida (`POST /api/friends/reject/{request_id}`), restrito exclusivamente ao destinatário.
- **FR-007**: O sistema DEVE disponibilizar endpoint para cancelar uma solicitação pendente enviada (`DELETE /api/friends/cancel/{request_id}`), restrito exclusivamente ao remetente original.
- **FR-008**: O sistema DEVE disponibilizar endpoint para desfazer uma amizade ativa (`DELETE /api/friends/{username}`), que pode ser acionado por qualquer um dos dois membros da amizade.
- **FR-009**: O sistema DEVE disponibilizar endpoint para bloquear um usuário (`POST /api/friends/block/{username}`), convertendo imediatamente qualquer vínculo prévio para o estado bloqueado.
- **FR-010**: O sistema DEVE disponibilizar endpoint para desbloquear um usuário (`POST /api/friends/unblock/{username}`), removendo o registro de bloqueio e restabelecendo o estado neutro.
- **FR-011**: O sistema DEVE filtrar a busca de usuários (`GET /api/users?q=...`) para excluir sumariamente usuários bloqueados (em qualquer direção) e exibir o estado da relação com o usuário autenticado.
- **FR-012**: O sistema DEVE blindar o acesso ao perfil público (`GET /api/users/{username}`) retornando `404 Not Found` caso o visualizador tenha sido bloqueado pelo titular do perfil.
- **FR-013**: O sistema DEVE disponibilizar endpoint para listar as amizades ativas do usuário conectado (`GET /api/friends`).
- **FR-014**: O sistema DEVE disponibilizar endpoint para listar as solicitações pendentes recebidas e enviadas (`GET /api/friends/requests`).
- **FR-015**: O sistema DEVE disponibilizar endpoint para listar os usuários bloqueados pelo usuário conectado (`GET /api/friends/blocked`).
- **FR-016**: Ao recusar uma solicitação pendente, o sistema DEVE remover o registro de pendência e retornar a relação ao estado neutro (sem vínculo). Para impedir novas solicitações de forma definitiva, o usuário DEVE utilizar a funcionalidade de Bloqueio.
- **FR-017**: O sistema DEVE disponibilizar uma rota e visão dedicada `/amigos` na barra de navegação global para usuários autenticados, contendo abas organizadas para "Meus Amigos", "Solicitações (Recebidas e Enviadas)", "Bloqueados" e "Descobrir Leitores".
- **FR-018**: No perfil público de um usuário (`/@username`), o sistema DEVE exibir unicamente a contagem quantitativa de amigos aceitos (quando o perfil for visível), mantendo a listagem nominal detalhada estritamente privada e visível apenas para o próprio usuário autenticado.

---

### Key Entities *(include if feature involves data)*

- **Friendship (Vínculo de Amizade / Relação Social)**:
  - `id`: Identificador único (inteiro sequencial ou UUID).
  - `user_id_a`: Primeiro usuário da relação (normalizado para ordenar alfabeticamente os UUIDs, garantindo chave única composta).
  - `user_id_b`: Segundo usuário da relação.
  - `status`: Estado canônico da relação (`pending`, `accepted`, `blocked`).
  - `action_user_id`: Identificador do usuário que realizou a última alteração (quem enviou a solicitação ou quem efetuou o bloqueio).
  - `created_at`: Data e hora em UTC de criação do relacionamento.
  - `updated_at`: Data e hora em UTC da última modificação de status.

- **FriendshipStatus (Enum)**:
  - `PENDING`: Solicitação enviada aguardando deliberação do destinatário.
  - `ACCEPTED`: Amizade mútua confirmada e ativa.
  - `BLOCKED`: Bloqueio unilateral imposto pelo `action_user_id`.

- **FriendshipSummary / UserRelationItem (Projeção de DTO / Schema)**:
  - `user`: Dados públicos do parceiro de relacionamento (id, username, display_name, avatar_url).
  - `relation_status`: Estado sob a perspectiva do usuário logado (`none`, `pending_sent`, `pending_received`, `friends`, `blocked_by_me`, `blocked_by_them`).
  - `request_id`: Identificador do registro para aceitar, recusar ou cancelar.
  - `since`: Data da última alteração de estado.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: O ciclo de vida completo de uma amizade (solicitar, aceitar, listar e desfazer) pode ser concluído com sucesso em menos de 3 segundos de tempo total de interação na interface.
- **SC-002**: 100% das tentativas de auto-solicitação ou solicitações duplicadas são interceptadas e tratadas pelo servidor sem falhas de integridade ou exceções 500.
- **SC-003**: 100% dos usuários bloqueados tornam-se imediatamente invisíveis nas pesquisas, perfis e tentativas de contato direto do usuário bloqueador, e vice-versa.
- **SC-004**: Ao desfazer uma amizade, todas as permissões e acessos restritos a amigos em recursos compartilhados (preparação para F07) cessam instantaneamente na requisição imediatamente subsequente.
- **SC-005**: Todas as ações da interface social (aceitar, recusar, cancelar, bloquear) possuem alvos táteis mínimos de 44x44px e fornecem feedback acessível (WAI-ARIA) para leitores de tela em conformidade com as diretrizes do projeto.

---

## Assumptions

- O sistema já possui a fundação multiusuário (F01), autenticação por sessões (F02) e perfis de usuário com `@username` único e chave `is_discoverable` (F05) operacionais.
- No Roadmap 0.5, a relação de amizade é simétrica e bilateral quando aceita (se A é amigo de B, B é amigo de A).
- A base de dados SQLite local opera em modo WAL com transações atômicas e commits explícitos garantidos pelos endpoints.
- As notificações em tempo real de novas solicitações serão introduzidas formalmente na Feature F09 (Notificações); nesta F06, o usuário toma ciência das solicitações através de crachás informativos e listas na tela de Amigos.
- O bloqueio prevalece sobre qualquer outro estado prévio e não pode ser sobreposto por solicitações do bloqueado.
