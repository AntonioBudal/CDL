# Feature Specification: Autenticação e Gestão de Sessões

**Feature Branch**: `029-autenticacao-gestao-sessoes`  
**Created**: 2026-09-21  
**Status**: Ready for Planning  
**Input**: User description: "F02 - Autenticação e Gestão de Sessões"

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Autenticação por Credenciais Locais e Acesso Protegido (Priority: P1)

Como leitor do Caderno de Leitura, desejo autenticar-me na aplicação informando meu nome de usuário (ou e-mail) e senha cadastrados, para que eu possa acessar com segurança minha estante particular, meus estudos e anotações privadas, garantindo que usuários não autenticados não visualizem nenhum conteúdo.

**Why this priority**: É a porta de entrada indispensável para um ambiente multiusuário privativo, substituindo o acesso irrestrito anterior por uma fronteira de segurança real.

**Independent Test**: Tentar acessar qualquer rota ou recurso privado da aplicação sem autenticação e verificar que o sistema redireciona o usuário para a tela de autenticação. Em seguida, fornecer credenciais válidas e constatar o acesso imediato ao acervo pessoal.

**Acceptance Scenarios**:
1. **Given** um visitante não autenticado, **When** ele tenta navegar para o acervo ou estudos, **Then** a aplicação impede o acesso e apresenta a tela de identificação (login).
2. **Given** um usuário cadastrado com credenciais válidas, **When** ele informa seu nome de usuário (ou e-mail) e sua senha correta, **Then** a autenticação é bem-sucedida, uma sessão segura é estabelecida e o usuário é direcionado ao seu destino.
3. **Given** um usuário tentando autenticar-se, **When** informa senha incorreta ou identificador inexistente, **Then** o sistema recusa a autenticação com mensagem amigável e genérica (sem revelar se o erro foi no usuário ou na senha) e impede o acesso.

---

### User Story 2 - Definição da Senha Inicial do Proprietário Canônico (Priority: P1)

Como proprietário canônico do acervo legado (migrado na F01), desejo ser conduzido a um fluxo obrigatório e transparente de primeiro acesso para definir minha primeira senha mestra local, para que meu acervo histórico fique protegido por senha sem atrito ou risco de bloqueio de acesso.

**Why this priority**: O usuário canônico soberano foi provisionado na F01 sem credenciais de senha; estabelecer sua senha inicial de forma segura é condição vital para que o usuário existente continue utilizando a plataforma.

**Independent Test**: Inicializar a aplicação sob a nova versão com o banco existente contendo o proprietário legado sem senha cadastrada e verificar que o sistema detecta a ausência de senha, redirecionando o proprietário para a criação da senha mestra antes de permitir o acesso geral.

**Acceptance Scenarios**:
1. **Given** uma conta de proprietário canônico ainda sem senha cadastrada, **When** a aplicação é aberta, **Then** o sistema direciona o usuário imediatamente para o assistente de primeiro acesso para definição da senha mestra.
2. **Given** o formulário de definição de senha inicial, **When** o proprietário digita e confirma uma senha de no mínimo 8 caracteres, **Then** a senha é registrada com algoritmo adaptativo (Argon2id) e a sessão do proprietário é ativada.
3. **Given** que a senha inicial do proprietário foi configurada com sucesso, **When** o proprietário acessa o sistema em momento posterior, **Then** a senha recém-criada é exigida regularmente na tela de login.

---

### User Story 3 - Cadastro de Novos Usuários na Rede Local (Priority: P1)

Como um novo leitor em um dispositivo autorizado na rede doméstica/privada, desejo criar minha própria conta fornecendo um nome de usuário único, e-mail e senha, para que eu possa iniciar meu próprio caderno de leitura independente no mesmo servidor local.

**Why this priority**: Permite que múltiplos membros da casa ou equipe compartilhem a mesma instância da aplicação com acervos totalmente isolados.

**Independent Test**: Acessar o formulário de cadastro com auto-registro habilitado, preencher dados válidos de um novo leitor e confirmar que a conta é criada com sucesso, iniciando uma sessão isolada para o novo usuário.

**Acceptance Scenarios**:
1. **Given** a aplicação configurada com auto-registro habilitado, **When** o visitante aciona a opção de criar conta na tela de login e preenche nome de usuário único, e-mail e senha segura, **Then** a conta é criada no estado ativo e uma sessão é iniciada automaticamente.
2. **Given** uma tentativa de cadastro com auto-registro, **When** o visitante informa um nome de usuário ou e-mail já existente no sistema, **Then** o sistema recusa a criação indicando com clareza o conflito.
3. **Given** a aplicação configurada com auto-registro desabilitado (`ALLOW_REGISTRATION=false`), **When** um visitante acessa a tela de login, **Then** a opção de cadastro não é exibida e tentativas diretas de registro via API são bloqueadas com código de recusa adequado.
4. **Given** um novo usuário recém-registrado, **When** ele acessa o sistema pela primeira vez, **Then** sua estante inicial encontra-se limpa e pronta para novos livros e estudos, sem qualquer dado herdado de outros usuários.

---

### User Story 4 - Gerenciamento e Revogação de Sessões e Dispositivos Conectados (Priority: P2)

Como leitor que acessa o Caderno tanto no computador principal quanto no celular via rede privada (Tailscale/LAN), desejo consultar a lista de todos os dispositivos com sessão ativa na minha conta e revogar o acesso de qualquer dispositivo remotamente, para manter total soberania sobre onde meus dados estão abertos.

**Why this priority**: Essencial para a mobilidade segura do usuário, permitindo desautorizar dispositivos perdidos, navegadores antigos ou acessos esquecidos.

**Independent Test**: Autenticar o mesmo usuário em dois navegadores distintos ("Dispositivo A" e "Dispositivo B"); acessar os Ajustes de Conta no "Dispositivo A", visualizar a lista de sessões ativas e revogar o "Dispositivo B"; verificar que o "Dispositivo B" tem seu acesso imediatamente revogado na próxima requisição.

**Acceptance Scenarios**:
1. **Given** um usuário com múltiplos acessos simultâneos, **When** ele abre o painel de sessões ativas nos Ajustes, **Then** ele visualiza cada sessão com identificação do dispositivo/navegador, data de início, última atividade e marcação visual clara de qual é a "Sessão Atual".
2. **Given** a lista de sessões ativas, **When** o usuário escolhe revogar uma sessão remota específica, **Then** a sessão é destruída no servidor e o respectivo dispositivo perde acesso imediato.
3. **Given** a opção de encerrar outras sessões, **When** o usuário comanda o logout de todos os outros dispositivos, **Then** todas as sessões ativas são invalidadas, preservando unicamente a sessão ativa corrente.

---

### User Story 5 - Encerramento Seguro de Sessão (Logout Pontual) (Priority: P1)

Como leitor terminando minha sessão de estudos em um dispositivo compartilhado, desejo sair da minha conta de forma definitiva através de um botão de logout, para garantir que ninguém mais que use aquele navegador consiga acessar minhas anotações.

**Why this priority**: Evita permanência indevida de dados e credenciais em terminais compartilhados, garantindo a privacidade local.

**Independent Test**: Efetuar logout a partir do menu do usuário e tentar navegar para trás ou acessar recursos privados, confirmando que a sessão foi destruída e o usuário é mantido na tela de login.

**Acceptance Scenarios**:
1. **Given** um usuário autenticado, **When** ele clica na opção de "Sair" (Logout), **Then** o identificador de sessão é destruído no servidor, o cookie de sessão é limpo no navegador e o usuário é redirecionado para a tela de login.
2. **Given** um usuário recém-desconectado, **When** ele tenta navegar para trás no histórico do navegador ou fazer nova requisição, **Then** o sistema exige nova autenticação.
3. **Given** uma sessão autenticada em uso regular, **When** o usuário utiliza a aplicação ativamente, **Then** a expiração da sessão é renovada automaticamente em janela deslizante (30 dias a partir da última atividade).

---

## Edge Cases

- **Navegador Offline ou Queda de Rede**: Se a conexão oscilar enquanto o usuário está autenticado, a sessão local deve permanecer preservada no cliente e restabelecer as operações normais assim que a conectividade com o servidor local for restaurada.
- **Revogação da Própria Sessão no Painel de Dispositivos**: Se o usuário tentar revogar a sessão atual pela lista de dispositivos, o sistema trata a operação como logout local convencional, redirecionando para a tela de autenticação.
- **Tentativas Repetidas com Senha Inválida (Proteção de Acesso)**: O mecanismo de autenticação deve mitigar tentativas sequenciais abusivas para evitar ataques de dicionário ou varreduras automatizadas na rede local.
- **Conta Suspensa ou Inativada**: Se o status da conta do usuário for alterado para inativo ou suspenso, qualquer sessão existente é instantaneamente recusada na próxima requisição do cliente.
- **Renovação de Sessão Ativa (Sliding Window)**: Usuários que utilizam a aplicação ativamente de forma frequente não devem ser desconectados no meio de uma leitura ou escrita contínua.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE exigir autenticação prévia para acesso a qualquer recurso privado (estante, estudos, anotações, capítulos, relações, buscas, dashboard e ajustes).
- **FR-002**: O sistema DEVE validar credenciais locais por meio de nome de usuário (ou e-mail) e senha, recusando senhas em branco ou abaixo do tamanho mínimo estipulado (mínimo de 8 caracteres).
- **FR-003**: As senhas de usuários DEVEM ser protegidas utilizando exclusivamente algoritmo adaptativo de derivação de chaves criptográficas de alta segurança (Argon2id) com sal aleatório e único por usuário, sendo estritamente vedado qualquer armazenamento em texto puro ou funções criptográficas fracas/reversíveis.
- **FR-004**: O sistema DEVE emitir identificadores de sessão opacos, criptograficamente imprevisíveis e de alta entropia para sessões autenticadas, associados a registros de sessão no servidor.
- **FR-005**: O identificador de sessão DEVE ser transportado no cliente exclusivamente via cookie HTTP com diretivas de segurança rígidas: `HttpOnly` (inacessível a scripts do cliente), `SameSite=Lax` (prevenção contra CSRF) e flag `Secure` ativada automaticamente sempre que o tráfego ocorrer via HTTPS ou túnel seguro (Tailscale).
- **FR-006**: O sistema DEVE emitir um novo identificador de sessão a cada login bem-sucedido, impedindo formalmente qualquer vulnerabilidade de fixação de sessão (*session fixation*).
- **FR-007**: As sessões DEVEM ter validade padrão de 30 dias de inatividade com renovação automática por janela deslizante (*sliding window*) a cada requisição autenticada ativa.
- **FR-008**: O sistema DEVE manter o registro de cada sessão ativa com metadados auditáveis: identificador da sessão, identificador do usuário, nome do dispositivo/cliente inferido do cabeçalho de navegação, endereço IP da conexão, data de criação, carimbo de última atividade e data de expiração.
- **FR-009**: O sistema DEVE disponibilizar painel de gestão de dispositivos conectados nas configurações da conta, permitindo que o usuário visualize todas as sessões ativas e identifique explicitamente qual é a sessão corrente.
- **FR-010**: O usuário DEVE ser capaz de revogar seletivamente qualquer sessão remota listada em seu painel de dispositivos, provocando a invalidação imediata da sessão no servidor.
- **FR-011**: O usuário DEVE ser capaz de acionar o comando de encerramento geral de outras sessões (*logout-all*), revogando todas as sessões associadas à sua conta exceto a sessão ativa em uso.
- **FR-012**: O comando de logout pontual DEVE destruir imediatamente o registro da sessão no banco de dados do servidor e instruir a remoção completa do cookie no navegador.
- **FR-013**: O sistema DEVE detectar na inicialização quando a conta do proprietário canônico legado não possui credenciais locais configuradas, forçando o direcionamento para um assistente de configuração da primeira senha mestra antes de liberar o acesso geral.
- **FR-014**: O sistema DEVE permitir a configuração do auto-registro de novos usuários através de parâmetro configurável (`ALLOW_REGISTRATION`), permitindo habilitar ou desabilitar a criação de novas contas na tela de identificação.
- **FR-015**: O sistema DEVE verificar a validade da sessão e o status ativo do usuário (`status == 'active'`) em todas as requisições protegidas, rejeitando sumariamente requisições de contas suspensas ou inativas.
- **FR-016**: O sistema DEVE fornecer telas de autenticação e registro responsivas e ergonômicas, compatíveis com uso em desktop e celulares, com feedback claro para o usuário.
- **FR-017**: O sistema DEVE exibir o usuário conectado no cabeçalho da aplicação e fornecer acesso direto ao botão de logout e aos ajustes de conta.

---

### Key Entities *(include if feature involves data)*

- **Usuário (User)**: Entidade central de identidade do sistema. Possui identificador único (`id`), nome de usuário (`username`), e-mail (`email`), nome de exibição (`display_name`), papel (`role`: admin ou user), status (`status`: active, suspended, deactivated) e data de criação.
- **Credencial Local (LocalCredential)**: Armazena as informações de autenticação local vinculadas ao usuário. Possui identificador do usuário (`user_id`), hash adaptativo de senha (`password_hash`) e carimbo de atualização de senha (`password_updated_at`).
- **Sessão de Usuário (UserSession)**: Registro individual de uma sessão ativa vinculada a um dispositivo/navegador. Possui identificador da sessão (`id`), identificador do usuário (`user_id`), hash do token de sessão (`session_token`), identificação legível do dispositivo (`device_name`), endereço IP (`ip_address`), agente do usuário (`user_agent`), data de criação (`created_at`), carimbo de última atividade (`last_activity`) e data limite de expiração (`expires_at`).

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% das rotas e recursos de dados privados da aplicação rejeitam acessos não autenticados, com taxa zero de vazamento de informações para visitantes anônimos.
- **SC-002**: 100% das senhas armazenadas são protegidas por derivação Argon2id com parâmetros recomendados de memória e custo de processamento, com 0% de senhas armazenadas em texto claro ou hashes obsoletos.
- **SC-003**: 100% dos identificadores de sessão emitidos são tokens opacos transportados exclusivamente em cookies com atributos de segurança (`HttpOnly`), impossibilitando furto via scripts do cliente.
- **SC-004**: Ao revogar uma sessão remota pelo painel de dispositivos ou acionar "encerrar todas as outras sessões", o dispositivo alvo perde acesso de forma imediata (na primeiríssima requisição subsequente).
- **SC-005**: O processo completo de autenticação (envio de credenciais, validação criptográfica e estabelecimento da sessão) completa-se em menos de 1 segundo em hardware convencional local.
- **SC-006**: Usuários ativos em rotina contínua de estudos mantêm sua sessão válida sem deslogamentos abruptos, respeitando a janela deslizante de 30 dias de inatividade.

---

## Assumptions

- O servidor continuará operando localmente no PC do usuário através do script de inicialização do projeto (`iniciar.py`), servindo tanto requisições de `localhost` quanto conexões via rede privada/Tailscale.
- A biblioteca `argon2-cffi` será utilizada para as operações criptográficas de hash de senhas locais.
- A camada de autenticação complementa a base estabelecida na Feature 01, substituindo o cabeçalho temporário `X-User-Id` por sessões persistentes seguras com cookies `HttpOnly`, mantendo a resolução do usuário ativo na dependência FastAPI `CurrentUser`.
- Os dados do acervo continuam armazenados exclusivamente no banco de dados SQLite local no modo WAL, mantendo a privacidade estrita do acervo do usuário.
- O auto-registro de novos usuários virá ativado por padrão (`ALLOW_REGISTRATION=true`), podendo ser desativado pelo proprietário via configuração.
