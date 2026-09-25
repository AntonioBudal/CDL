# Feature Specification: Sincronização Multidispositivo

**Feature Branch**: `031-sincronizacao-multidispositivo`  
**Created**: 2026-09-22  
**Status**: Ready for Planning  
**Input**: User description: "F04 - Sincronização Multidispositivo"

---

## Clarifications

### Session 2026-09-22

- Q: Como o feed incremental de alterações (`GET /api/sync/changes?since=<timestamp>`) deve identificar e entregar deleções de registros para os clientes móveis e desktop? → A: Feed unificado baseado em timestamps nas entidades existentes (`updated_at` / `deleted_at`), particionado em `{ "updated": [...], "deleted": [...] }`.
- Q: Quando ocorre `HTTP 409 Conflict` e o usuário escolhe "Sobrescrever com rascunho local", qual deve ser a mecânica exata de gravação? → A: O cliente reenvia a requisição atualizando `expected_version` para a versão atual do servidor, forçando a substituição e incrementando a versão no servidor.
- Q: Quais metadados visuais e espaciais devem ser sincronizados entre dispositivos na conta do usuário? → A: Sincronizar posições dos nós do Canvas (`x, y`), superclasse e preferências de exibição, mantendo zoom e pan do Canvas exclusivamente locais por dispositivo (para respeitar a diferença de viewport entre PC e celular).

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Detecção Otimista e Resolução de Conflitos de Concorrência (Priority: P1)

Como leitor que edita estudos e anotações alternando entre o computador (desktop) e o smartphone (celular via Tailscale), desejo que o sistema detecte automaticamente quando uma versão mais recente foi salva em outro dispositivo antes de sobrescrever meus dados locais, para que eu nunca sofra perda silenciosa de conteúdo nem sobrescreva acidentalmente minhas próprias anotações.

**Why this priority**: É o alicerce fundamental de segurança e integridade de dados (Princípio Constitucional I). Sem controle de concorrência e detecção de conflitos, edições simultâneas ou desconexões temporárias resultam em corrupção de conteúdo e frustração irrecuperável para o leitor.

**Independent Test**:
1. Abrir o mesmo estudo simultaneamente em duas abas ou dispositivos com versão inicial `v1`.
2. Salvar uma modificação na Aba A (o servidor atualiza a entidade e incrementa para `v2`).
3. Tentar salvar uma modificação conflitante na Aba B enviando `expected_version = 1`.
4. Constatar que o servidor rejeita o salvamento com `HTTP 409 Conflict`, devolvendo a versão atualizada do servidor.
5. Constatar que a interface do usuário exibe um modal de resolução permitindo: comparar os textos, manter a alteração remota ou forçar a gravação do rascunho local.

**Acceptance Scenarios**:
1. **Given** um estudo na versão `N`, **When** um cliente envia requisição de atualização informando `expected_version = N`, **Then** o servidor persiste as mudanças, incrementa a versão para `N + 1`, atualiza `updated_at` e responde `HTTP 200 OK`.
2. **Given** um estudo cuja versão no banco já é `N + 1`, **When** um segundo cliente envia atualização informando `expected_version = N`, **Then** o backend rejeita a gravação com código `HTTP 409 Conflict`, retornando o payload completo com a versão atual do servidor e os campos conflitantes.
3. **Given** a ocorrência de um conflito `HTTP 409` no cliente web/móvel, **When** a resposta de conflito é recebida, **Then** o formulário NÃO descarta o texto digitado pelo usuário, mantendo-o intacto e apresentando o diálogo de resolução de concorrência com opções claras de ação.
4. **Given** o diálogo de conflito, **When** o usuário escolhe "Manter versão do servidor", **Then** os campos locais são atualizados com a versão mais recente e o estado de pendência é limpo.
5. **Given** o diálogo de conflito, **When** o usuário escolhe "Sobrescrever com rascunho local", **Then** o cliente reenvia o salvamento informando a nova versão atual do servidor como base, persistindo o texto local com sucesso e avançando a numeração de versão.

---

### User Story 2 - Reconciliação Incremental Pós-Reconexão e Standby (Priority: P1)

Como leitor móvel que utiliza o Caderno no celular conectado via rede local ou Tailscale, desejo que ao desbloquear o aparelho ou restabelecer a conexão de rede, o aplicativo reconcilie rapidamente as alterações ocorridas no servidor sem recarregar forçadamente a página inteira, para que meu acervo esteja sempre atualizado com o que foi lido ou estudado no PC.

**Why this priority**: O uso de celulares envolve frequentes suspensões de tela (standby) e variações de conectividade de rede. Uma reconciliação leve e incremental mantém a continuidade de estudos com baixo consumo de dados e bateria.

**Independent Test**:
Realizar alterações em livros e estudos no desktop; em seguida, simular no cliente móvel a retomada de foco ou o evento `online` após um período de desconexão; constatar que o cliente consulta o endpoint de reconciliação com o carimbo temporal da última sincronização (`GET /api/sync/changes?since=<timestamp>`), aplicando as atualizações no estado reativo sem perda de contexto da tela ativa.

**Acceptance Scenarios**:
1. **Given** um cliente conectado que esteve em standby desde o instante `T`, **When** a tela é reativada ou a conexão restabelecida, **Then** o cliente dispara uma consulta de reconciliação informando o timestamp `T`.
2. **Given** que houve alterações de livros ou estudos no servidor após `T`, **When** o feed de mudanças responde com sucesso trazendo particionamento de criados/atualizados e excluídos (`deleted_at`), **Then** o cliente atualiza seus repositórios locais refletindo o novo estado.
3. **Given** um formulário aberto com alterações locais não salvas durante uma reconciliação automática, **When** o registro em edição não foi modificado remotamente, **Then** a reconciliação preserva integralmente o rascunho em digitação sem interrupção.

---

### User Story 3 - Sincronização de Metadados Visuais e Espaciais (Priority: P2)

Como leitor que organiza espacialmente estudos no Canvas 2D e personaliza a aparência de leitura, desejo que as posições dos cartões na lousa, a configuração de Superclasse e o estado de agrupamento e expansão da árvore de estudos sejam sincronizados na minha conta pelo servidor, para que eu encontre a mesma organização espacial e estética em todos os meus computadores e dispositivos.

**Why this priority**: O diferencial do Caderno de Leitura reside na navegação espacial e no design autoral (Superclasses, Canvas, Árvore). Sincronizar esses metadados eleva a experiência multiusuário para além do texto puro.

**Independent Test**:
Reposicionar nós no Canvas 2D e alterar a Superclasse no PC; carregar ou sincronizar o cliente no celular; verificar que as posições dos nós (`study_canvas_nodes`) e preferências de aparência refletem fielmente as alterações salvas no banco central, enquanto a câmera de zoom/pan do Canvas permanece ajustada para a tela do celular.

**Acceptance Scenarios**:
1. **Given** alterações nas posições de estudos no Canvas 2D (`x, y`), **When** o salvamento é efetuado, **Then** as coordenadas são persistidas com vínculo ao usuário proprietário e disponibilizadas para outros dispositivos da mesma conta.
2. **Given** alteração na preferência de visualização (Superclasse, tamanho de fonte, ordenação de árvore), **When** a preferência é atualizada, **Then** ela é persistida na conta do usuário no servidor e sincronizada nos demais terminais.
3. **Given** diferentes tamanhos de tela (desktop vs smartphone), **When** o Canvas 2D é aberto em tela móvel, **Then** as posições relativas dos cartões são respeitadas, mantendo o zoom e o deslocamento de câmera independentes e adequados à tela em uso.

---

### User Story 4 - Indicador de Conexão e Transparência do Estado de Sincronização (Priority: P3)

Como leitor em trânsito com conexão intermitente, desejo visualizar um indicador sutil e não intrusivo do estado da sincronização com o meu servidor local, para que eu tenha certeza se minhas alterações estão seguras no servidor ou salvas temporariamente no dispositivo.

**Why this priority**: Transparência operacional gera confiança psicológica para o usuário de que nenhuma leitura ou nota escrita foi perdida.

**Independent Test**:
Desconectar a rede do cliente e efetuar modificações locais; verificar que o indicador de status altera para "Offline — alterações retidas no dispositivo"; restabelecer a conexão e constatar a transição para "Sincronizando..." e, finalmente, "Sincronizado".

**Acceptance Scenarios**:
1. **Given** o cliente conectado e com todas as alterações persistidas no backend, **When** o leitor observa a barra de status ou rodapé, **Then** é exibido o estado "Sincronizado" acompanhado de ícone neutro e acessível (sem emojis).
2. **Given** a perda de comunicação com o servidor local (ex.: PC suspenso ou rede inacessível), **When** o cliente detecta a falha, **Then** o estado transiciona para "Desconectado do servidor" e orienta que as edições serão reconciliadas assim que a conexão retornar.
3. **Given** a reconexão automática bem-sucedida, **When** os dados pendentes são enviados e reconciliados, **Then** o indicador retorna suavemente ao estado de confirmação sem alertas modais obstrutivos.

---

## Edge Cases

- **Sobrescrita Concorrente em Conexão Lenta**: Se dois clientes enviarem atualizações quase simultâneas com o mesmo `expected_version`, a transação serializada do SQLite (modo WAL com lock de escrita) garante que a primeira requisição seja concluída com sucesso e a segunda receba `HTTP 409 Conflict`.
- **Restauração de Backup e Regressão de Versão**: Se o banco for restaurado a partir de um snapshot antigo e um cliente mantiver um número de versão superior em cache, o cliente detecta a discrepância na primeira reconciliação e solicita recarga dos dados do servidor central como fonte da verdade.
- **Exclusão Remota de Registro em Aberto**: Se um estudo for excluído em um dispositivo enquanto outro dispositivo o exibe na tela de edição, a tentativa de salvamento subsequente pelo segundo dispositivo detecta que o recurso foi removido (`HTTP 404 Not Found`), permitindo ao usuário copiar seu rascunho local ou salvá-lo como um novo estudo independente.
- **Operação Desconectada no Celular com Servidor Desligado**: Caso o leitor utilize o celular quando o PC onde roda o servidor estiver desligado, o aplicativo web opera em modo leitura de cache e não perde textos em edição, exibindo alerta claro de que o servidor local está inacessível.
- **Tratamento de Zoom e Pan em Dispositivos Distintos (Resolução Q3: Opção A)**: Telas ultrawide de desktop e telas compactas de celulares possuem geometrias fundamentalmente distintas. As coordenadas absolutas dos nós do Canvas (`x, y`) são compartilhadas e sincronizadas, mas o zoom e deslocamento da câmera do Canvas permanecem estritamente locais no navegador de cada dispositivo.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE adotar o backend local central como a única fonte da verdade (*single source of truth*) para todas as operações de escrita, leitura e reconciliação de estado.
- **FR-002**: Toda entidade editável do acervo (`Study`, `Book`, `Chapter`) DEVE possuir um contador incremental de controle de versão (`version: int`) e um carimbo de data/hora de última atualização em UTC (`updated_at`).
- **FR-003**: As requisições de atualização (`PUT` / `PATCH`) de estudos e livros DEVEM aceitar o parâmetro obrigatório ou cabeçalho de controle de concorrência com a versão esperada (`expected_version`).
- **FR-004**: O backend DEVE validar se `expected_version == entity.version` antes de aplicar qualquer alteração; caso os valores divirjam, o backend DEVE abortar a transação e responder imediatamente com `HTTP 409 Conflict`.
- **FR-005**: Ao responder com `HTTP 409 Conflict`, o backend DEVE incluir na resposta o estado atualizado do registro no servidor (`current_version`, `updated_at`, campos de texto vigentes), permitindo comparação no cliente.
- **FR-006**: O frontend DEVE interceptar respostas `HTTP 409 Conflict` e apresentar um diálogo modal acessível de resolução de concorrência, disponibilizando opções para: (1) adotar a versão do servidor, (2) sobrescrever deliberadamente com o rascunho local ou (3) comparar as diferenças lado a lado.
- **FR-007**: O sistema DEVE disponibilizar endpoint de feed de alterações `GET /api/sync/changes?since=<timestamp>` restrito ao usuário autenticado, retornando registros alterados ou excluídos desde o instante indicado.
- **FR-008**: O cliente web DEVE escutar eventos de reconexão de rede (`online`), visibilidade de documento (`visibilitychange`) e foco de janela (`focus`) para disparar consultas de reconciliação de forma inteligente e sem sobrecarregar o servidor.
- **FR-009**: O feed incremental de alterações `GET /api/sync/changes?since=<timestamp>` DEVE ser baseado em timestamps (`updated_at` e `deleted_at`) nas entidades existentes (`Study`, `Book`, etc.), retornando listas particionadas `{ "updated": [...], "deleted": [...] }` para reconciliação atômica no cliente.
- **FR-010**: Ao resolver um conflito com a ação "Sobrescrever com rascunho local", o cliente DEVE reenviar a atualização com `expected_version` ajustado para a versão mais recente do servidor (`server_version`), gravando o texto local com sucesso e avançando a numeração de versão.
- **FR-011**: O sistema DEVE sincronizar centralmente as posições dos nós do Canvas 2D (`study_canvas_nodes` x, y), a escolha de Superclasse e preferências de leitura entre os dispositivos do usuário, mantendo zoom e pan da câmera do Canvas como estado estritamente local em cada dispositivo para acomodar diferentes dimensões de tela.
- **FR-012**: O sistema DEVE sincronizar as preferências de leitura e visualização de cada usuário no servidor através de endpoint dedicado, persistindo escolha de Superclasse, modo de visualização preferido e tamanho padrão de tipografia.
- **FR-013**: Toda operação de sincronização e reconciliação DEVE ser estritamente isolada por `user_id`, garantindo que um usuário nunca receba ou consulte dados de sincronização pertencentes a outro usuário.
- **FR-014**: A interface do usuário DEVE exibir um indicador de sincronização minimalista e informativo, cumprindo as diretrizes de acessibilidade e ausência de emojis do Caderno de Leitura.

---

### Key Entities *(include if feature involves data)*

- **VersionedResource (Mixin / Protocol)**:
  Contém `version: int` (iniciando em 1, incrementado a cada mutação com sucesso) e `updated_at: datetime` (UTC). Aplicado às entidades editáveis como `Study`, `Book`, `Chapter` e nós espaciais.
- **UserPreference**:
  Entidade associada ao `User` que armazena configurações persistentes de leitura: `active_superclass`, `preferred_view_mode`, `tree_collapsed_state`, `font_scale` e `theme_mode`.
- **SyncChangesResponse**:
  Payload estruturado entregue por `GET /api/sync/changes`:
  ```json
  {
    "server_time": "2026-09-22T22:00:00Z",
    "updated": {
      "books": [...],
      "studies": [...],
      "canvas_nodes": [...],
      "preferences": {...}
    },
    "deleted": {
      "book_ids": [...],
      "study_ids": [...]
    }
  }
  ```

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Em caso de edições concorrentes sobre o mesmo estudo, 100% dos conflitos devem ser detectados com resposta `HTTP 409 Conflict`, sem ocorrência de sobrescrita cega ou perda silenciosa de dados.
- **SC-002**: A resolução de conflitos na interface do usuário deve permitir salvar o rascunho local ou adotar o estado do servidor em menos de 3 cliques.
- **SC-003**: A consulta de reconciliação pós-reconexão (`GET /api/sync/changes`) deve responder em menos de 100ms para acervos de até 1.000 estudos em rede local/Tailscale.
- **SC-004**: O aplicativo móvel em segundo plano (standby) deve recuperar o estado mais recente em menos de 1 segundo após o retorno do foco da janela.
- **SC-005**: 100% das preferências visuais e posições espaciais do Canvas devem ser mantidas e restauradas fidedignamente entre sessões distintas no mesmo perfil de leitor.
- **SC-006**: Cobertura de 100% dos testes unitários e de integração de detecção de concorrência e reconciliação incremental sem requisições a serviços externos de nuvem.

---

## Assumptions

- O servidor do Caderno de Leitura permanece executando no computador local do usuário, acessível por dispositivos secundários (como smartphones) através de rede local Wi-Fi ou túnel privado seguro Tailscale.
- O SQLite opera em modo WAL com timeout de escrita suficiente (`busy_timeout`), prevenindo erros de travamento de banco sob múltiplos leitores e escritor serializado.
- Conflitos de edição simultânea em estudos distintos não bloqueiam um ao outro; o controle de concorrência é granular por registro/entidade.
- A aplicação móvel funciona como Progressive Web App (PWA) ou aplicação web responsiva servida pelo backend FastAPI.
