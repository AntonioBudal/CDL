# Feature Specification: Conta Google e Vinculação de Identidade

**Feature Branch**: `030-conta-google-identidade`  
**Created**: 2026-09-22  
**Status**: Ready for Planning  
**Input**: User description: "F03 - Conta Google e Vinculação de Identidade"

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Autenticação Direta com Conta Google (Sign in with Google) (Priority: P1)

Como leitor que já vinculou sua conta Google ao Caderno de Leitura, desejo autenticar-me na tela de identificação com um único clique no botão oficial do Google, para que eu possa acessar rapidamente meus estudos e meu acervo pessoal sem necessidade de digitar nome de usuário ou senha local.

**Why this priority**: É a porta de entrada principal para a experiência de autenticação moderna e rápida, reduzindo atrito de digitação e esquecimento de senhas em computadores e aparelhos móveis autorizados.

**Independent Test**: Com uma conta Google previamente associada ao leitor, acionar o botão "Entrar com Google" na tela de login; constatar que a validação do token é processada no servidor e uma sessão autenticada (`caderno_session`) é emitida com sucesso, liberando acesso imediato à estante.

**Acceptance Scenarios**:
1. **Given** um leitor na tela de login com Google habilitado, **When** ele clica no botão "Entrar com Google" e autentica-se no popup oficial do Google, **Then** o sistema valida o token emitido no servidor, inicia a sessão do leitor e o redireciona para a página inicial.
2. **Given** um token Google adulterado, expirado ou emitido para outro aplicativo (Client ID incorreto), **When** a credencial é enviada para o servidor, **Then** o backend rejeita a requisição com código de erro amigável (`HTTP 401 Unauthorized`) e impede o acesso.
3. **Given** uma conta Google associada a um usuário com status inativo ou suspenso, **When** o login com Google é acionado, **Then** o sistema recusa o acesso informando que a conta está inativa.

---

### User Story 2 - Cadastro e Primeiro Acesso Automático via Google (Priority: P1)

Como novo leitor que utiliza a conta Google pela primeira vez na aplicação (com o auto-registro habilitado), desejo que meu perfil de leitor seja provisionado de maneira imediata com meus dados básicos e um identificador único exclusivo, para que eu possa começar meu caderno de leitura sem formulários manuais extensos.

**Why this priority**: Oferece experiência de integração fluida para novos membros da rede local ou doméstica, garantindo criação instantânea de contas sem atrito.

**Independent Test**: Acessar o sistema com uma conta Google ainda não cadastrada (em ambiente com auto-registro ativo); concluir o fluxo de login do Google e verificar que um novo usuário (`User`) isolado é criado no banco, com sua identidade externa Google (`ExternalIdentity`) vinculada através do identificador estável `sub`, acompanhado de sessão ativa.

**Acceptance Scenarios**:
1. **Given** um visitante com conta Google nunca antes utilizada no sistema e com auto-registro ativado, **When** ele aciona o botão "Entrar com Google", **Then** uma nova conta ativa é provisionada com nome de exibição e e-mail derivados do Google, um `@username` único gerado automaticamente e estante limpa isolada.
2. **Given** uma tentativa de primeiro acesso com o Google quando o auto-registro está desativado (`ALLOW_REGISTRATION=false`), **When** um visitante com conta Google não vinculada tenta entrar, **Then** o sistema rejeita a operação com aviso claro de que novos cadastros estão restritos.
3. **Given** uma conta recém-criada via Google, **When** o usuário consulta seu perfil nos Ajustes, **Then** ele constata que sua conta está identificada como vinculada ao Google e que ele pode opcionalmente definir uma senha local caso deseje no futuro.

---

### User Story 3 - Vinculação e Desvinculação nos Ajustes de Conta (Priority: P2)

Como leitor já cadastrado com credenciais locais (nome de usuário e senha), desejo poder vincular minha conta Google à minha conta existente através da tela de Ajustes — e também desvinculá-la caso mude de ideia — para ter total liberdade de escolher o método de acesso preferido.

**Why this priority**: Garante que usuários pré-existentes (inclusive o proprietário canônico) possam conectar sua identidade Google ao seu acervo histórico sem perder nenhum estudo ou duplicar contas.

**Independent Test**: Fazer login com credenciais locais (senha), acessar os Ajustes de Conta, acionar a opção "Vincular Conta Google"; após o consentimento no Google, comprovar que a identidade externa é associada à conta atual e que logins subsequentes com Google acessam a mesma conta; em seguida, testar a desvinculação garantindo que o usuário mantenha seu acesso por senha.

**Acceptance Scenarios**:
1. **Given** um usuário logado com senha local, **When** ele acessa a aba de Conta nos Ajustes e conclui a vinculação do Google, **Then** o sistema registra o identificador estável do Google na sua conta e exibe o estado "Conta Google vinculada".
2. **Given** um usuário com conta Google vinculada e com senha local cadastrada, **When** ele solicita a desvinculação do Google nos Ajustes, **Then** a identidade externa é desassociada e o usuário continua acessando normalmente por senha.
3. **Given** um usuário que se cadastrou exclusivamente pelo Google e ainda não possui senha local definida, **When** ele tenta desvincular o Google, **Then** o sistema bloqueia a ação orientando-o a definir previamente uma senha mestra local, prevenindo bloqueio permanente de acesso (*lockout prevention*).
4. **Given** uma tentativa de vincular uma conta Google que já está associada à conta de outro usuário do sistema, **When** a solicitação é processada, **Then** o backend recusa a vinculação com conflito (`HTTP 409 Conflict`).

---

### User Story 4 - Operação Graciosa e Degradação Elegante sem Chaves Google (Priority: P3)

Como proprietário ou operador que utiliza o Caderno de Leitura em ambiente totalmente offline ou que ainda não configurou as credenciais da API do Google, desejo que a aplicação funcione perfeitamente apenas com autenticação local, ocultando os botões do Google e sem gerar erros de console ou chamadas de rede externas com falha.

**Why this priority**: Preserva a filosofia de soberania local e independência do Caderno de Leitura, permitindo que a aplicação seja 100% utilizável mesmo sem dependências de serviços externos.

**Independent Test**: Executar o sistema sem a variável de ambiente `GOOGLE_CLIENT_ID` definida; abrir a tela de login e verificar que o botão do Google não é renderizado, nenhum script de `accounts.google.com` é requisitado e o formulário de login local opera normalmente.

**Acceptance Scenarios**:
1. **Given** o servidor operando sem `GOOGLE_CLIENT_ID` configurado, **When** a aplicação consulta a configuração de autenticação (`GET /api/auth/config`), **Then** a flag `google_auth_enabled` retorna falso e o Client ID não é divulgado.
2. **Given** `google_auth_enabled == false`, **When** o visitante acessa a tela de identificação, **Then** apenas os campos de credenciais locais (usuário/senha) são exibidos, sem qualquer aviso de erro ou espaço vazio não estilizado.
3. **Given** uma chamada direta de API para `POST /api/auth/google` quando o recurso estiver desativado, **When** a requisição é processada, **Then** o servidor responde com recusa explícita (`HTTP 400 Bad Request` ou `HTTP 404 Not Found`).

---

## Edge Cases

- **E-mail Já Existente com Senha Local (Resolução Q1: Opção A)**: Se um usuário autenticar-se pelo Google e o e-mail retornado já pertencer a um leitor cadastrado localmente (com senha) mas sem vínculo prévio de `sub`, o sistema verifica se o e-mail foi atestado como verificado pelo Google (`email_verified == true`). Em caso positivo, o sistema vincula a identidade externa Google (`sub`) à conta existente automaticamente e estabelece a sessão do usuário com máxima fluidez e sem atrito.
- **Auto-registro Desabilitado para Contas Google Inéditas (Resolução Q2: Opção A)**: Quando `ALLOW_REGISTRATION=false`, tentativas de primeiro acesso de contas Google ainda não vinculadas são bloqueadas no servidor com `HTTP 403 Forbidden`, preservando a soberania da trava de cadastros. Usuários com contas Google já vinculadas anteriormente continuam se autenticando normalmente.
- **Avatar e Foto de Perfil do Google (Resolução Q3: Opção A)**: O claim `picture` do Google não será persistido nem carregado nesta versão. A Feature 03 foca com rigor estrito em autenticação segura e vínculo estável de identidade (`sub`), preservando a privacidade local sem requisições externas para carregar imagens e mantendo os ícones acessíveis WAI-ARIA. A personalização de avatar e perfil visual fica formalmente reservada para a Feature 05 (Perfil e Privacidade).
- **Queda de Conexão com o Google no Navegador**: Se o usuário estiver offline ou com bloqueadores rígidos de scripts externos, a biblioteca GIS pode não carregar. O frontend trata o evento com fallback gracioso, mantendo a autenticação por credenciais locais plenamente funcional.
- **Rede Privada e Tailscale (HTTPS / Origens Autorizadas)**: O Google Identity Services exige origens HTTPS autorizadas no Google Cloud Console para qualquer domínio que não seja `localhost`. Conexões via Tailscale exigem certificado HTTPS nativo (ex.: `*.ts.net`) ou o uso do túnel configurado nas origens autorizadas.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE disponibilizar autenticação via Google Identity Services (GIS), permitindo que leitores entrem ou se cadastrem através de credenciais Google autorizadas.
- **FR-002**: O sistema DEVE validar criptograficamente a autenticidade, assinatura e expiração do ID Token (JWT) do Google exclusivamente no servidor backend (FastAPI), utilizando as chaves públicas oficiais do Google.
- **FR-003**: O sistema DEVE conferir estritamente se o destinatário (`aud`) do ID Token corresponde ao `GOOGLE_CLIENT_ID` configurado no ambiente, prevenindo uso de tokens emitidos para outras aplicações.
- **FR-004**: O vínculo entre uma conta Google e um usuário do sistema DEVE ser baseado única e exclusivamente no identificador estável do Google (`sub` - Subject Identifier), gravado na entidade `ExternalIdentity`. O endereço de e-mail NUNCA deve ser utilizado como chave de relacionamento estável.
- **FR-005**: Ao autenticar com sucesso via Google, o sistema DEVE emitir a sessão padrão da aplicação (`UserSession`) e definir o cookie seguro `caderno_session` com os mesmos atributos de proteção estabelecidos na Feature 02 (`HttpOnly`, `SameSite=Lax`, `Secure` dinâmico).
- **FR-006**: Quando um usuário Google nunca antes registrado fizer login e o auto-registro estiver habilitado, o sistema DEVE criar um novo registro de usuário (`User`), registrar a respectiva `ExternalIdentity` e gerar um `@username` único e legível.
- **FR-007**: Se o auto-registro de novos usuários estiver desativado (`ALLOW_REGISTRATION=false`), tentativas de login com contas Google não vinculadas DEVEM ser recusadas no backend com código `HTTP 403 Forbidden`.
- **FR-008**: O sistema DEVE permitir que um usuário autenticado por credenciais locais vincule sua conta Google à sua conta existente a partir do painel de Ajustes da conta.
- **FR-009**: O sistema DEVE impedir a vinculação de uma identidade Google já associada a outra conta ativa no sistema, respondendo com conflito `HTTP 409 Conflict`.
- **FR-010**: O sistema DEVE permitir que um leitor desvincule sua conta Google nos Ajustes, desde que o usuário possua ao menos outro método de acesso configurado (senha local ativa), impedindo bloqueio permanente da conta (*lockout*).
- **FR-011**: O endpoint público `GET /api/auth/config` DEVE expor a flag booleana `google_auth_enabled` e o `google_client_id` público quando configurado, permitindo que a interface web saiba se deve inicializar o botão do Google.
- **FR-012**: Se `GOOGLE_CLIENT_ID` não estiver definido nas configurações do ambiente, o sistema DEVE desativar silenciosamente os componentes do Google, não carregar bibliotecas externas e operar normalmente no modo de autenticação local.
- **FR-013**: As telas de login e registro DEVEM renderizar o botão oficial do Google de forma responsiva e harmonizada com o design system do Caderno de Leitura, em desktop e telas móveis.
- **FR-014**: Toda requisição de autenticação Google com token inválido, expirado ou com assinatura incorreta DEVE ser recusada com `HTTP 401 Unauthorized`.
- **FR-015**: A integridade dos dados e o isolamento entre contas multiusuário DEVEM ser rigorosamente preservados, assegurando que um leitor autenticado via Google acesse exclusivamente o acervo e anotações pertencentes ao seu `user_id`.
- **FR-016**: Se um leitor tentar autenticação via Google com e-mail já cadastrado localmente no sistema e verificado pelo Google (`email_verified == true`), o sistema DEVE associar a identidade Google (`sub`) à conta existente automaticamente, sem exigir recadastro ou gerar contas duplicadas.

---

### Key Entities *(include if feature involves data)*

- **Usuário (User)**: Entidade central de usuário já existente no sistema (`id`, `username`, `display_name`, `email`, `role`, `status`, `created_at`).
- **Identidade Externa (ExternalIdentity)**: Nova entidade de vínculo com provedores de identidade externos.
  - `id`: Identificador primário UUID (String 36).
  - `user_id`: Chave estrangeira para `User.id` com integridade referencial `CASCADE`.
  - `provider`: Provedor de identidade (ex.: `'google'`).
  - `provider_subject`: Claim estável `sub` do Google (String única por provedor, indexada).
  - `email_at_link`: E-mail informado pelo provedor no momento da vinculação (para auditoria).
  - `created_at`: Data/hora do estabelecimento do vínculo.
- **Sessão de Usuário (UserSession)**: Sessão ativa emitida pelo sistema após login Google bem-sucedido (reutiliza a infraestrutura criada na F02).

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: O fluxo de autenticação completa via Google (envio da credencial do frontend, validação criptográfica no backend e emissão da sessão) conclui-se em menos de 1,5 segundo em conexões locais normais.
- **SC-002**: 100% dos tokens do Google enviados para a API são validados criptograficamente pelo backend contra as chaves públicas oficiais do Google, com taxa zero de aceitação de tokens forjados ou expirados.
- **SC-003**: 100% dos vínculos de contas utilizam o identificador imutável `sub` do Google, sobrevivendo sem qualquer ruptura caso o usuário altere seu endereço de e-mail principal no Google.
- **SC-004**: Ao operar sem chaves do Google configuradas (`GOOGLE_CLIENT_ID` ausente), o sistema apresenta zero erros de console no navegador e 100% de disponibilidade no login local por credenciais.
- **SC-005**: 0% de ocorrência de bloqueio acidental de conta (*lockout*) ao tentar desvincular o Google sem possuir senha local cadastrada.
- **SC-006**: Isolamento absoluto de dados: nenhum estudo, livro ou anotação de outro leitor é acessível por um usuário autenticado via Google.

---

## Assumptions

- O Caderno de Leitura utiliza o Google Identity Services (GIS) através do script oficial `accounts.google.com/gsi/client`, dispensando bibliotecas legadas (Google Sign-In v1/gapi).
- O backend utilizará a biblioteca oficial recomendada pelo Google (`google-auth`) para a validação e decodificação do ID Token JWT.
- A configuração da credencial de cliente (`GOOGLE_CLIENT_ID`) será informada por meio de variável de ambiente no servidor local.
- Quando acessado via rede móvel e Tailscale fora de `localhost`, a conexão utilizará o domínio do nó Tailscale com HTTPS ativado, atendendo aos requisitos de origens autorizadas do Google GIS.
- Usuários autenticados pelo Google continuam sujeitos a todas as regras de controle de acesso, auditoria e isolamento multiusuário estabelecidas no Roadmap 0.5.
