# Roadmap 0.5 — Multiusuário, Backend, CRUD e Social

**Data oficial de emissão:** 2026-09-20  
**Status do Roadmap:** Planejado para desenvolvimento com o GitHub Spec Kit (`speckit`).  
**Regra Geral de Estado:** Todas as dez features (**F01 a F10**) estão estritamente **NÃO INICIADAS**.  
Nenhum rascunho anterior, arquivo de teste ou documento prévio altera o status de qualquer entrega deste roadmap. O avanço ocorre somente através de ciclos delimitados do fluxo Spec Kit (`speckit-specify` → `speckit-clarify` → `speckit-plan` → `speckit-tasks` → `speckit-analyze` → `speckit-implement`), resultando em **1 Commit Atômico por Feature Validada**.

---

## 1. Visão Geral e Princípios de Arquitetura

O **Caderno de Leitura (CDL)** consolidou em suas versões anteriores (0.1 a 0.4) um acervo de estudos com rica navegação espacial (Canvas 2D na GPU, Árvore de Estudos WAI-ARIA, Relações Semânticas, Cockpit Analítico e física cinemática das Superclasses). Contudo, o sistema nasceu conceitualmente como uma aplicação monousuário (*single-user*).

A versão **0.5** marca a transição de paradigma do Caderno de Leitura:
> **De um aplicativo pessoal de usuário único para uma plataforma com fundação multiusuário completa, segura e colaborativa**, mantendo a hospedagem no computador local do próprio usuário.

### Princípios Fundamentais da Versão 0.5

1. **Hospedagem Local com Acesso Híbrido (PC + Celular via Tailscale):**
   - O servidor permanece executando localmente no PC através de `iniciar.py` (FastAPI + Uvicorn na porta 8000).
   - O SQLite local em modo WAL continua plenamente viável como motor de dados para o protótipo, sustentando múltiplos leitores simultâneos e escritor único serializado com tempo de espera calibrado (`busy_timeout`).
   - A camada de acesso a dados (SQLAlchemy 2) e os serviços de domínio devem manter isolamento e padrões limpos (Repository / Service Pattern) para que uma eventual migração futura para banco cliente-servidor (PostgreSQL) não demande refatorações nas regras de negócio, na autenticação ou na autorização.

2. **Propriedade dos Dados Antes da UI Social (Fundação Antes da Camada Social):**
   - É terminantemente vedado iniciar a construção por telas de Perfil, Amigos ou Botão do Google de forma isolada.
   - Primeiro estabelece-se **Identidade**, **Propriedade de Recursos (`user_id`)** e **Autorização no Servidor**. Recursos privados não podem ser compartilhados ou expostos sem que sua propriedade canônica esteja registrada.

3. **Autorização Centralizada no Servidor ("Deny by Default" — OWASP):**
   - A proteção de dados e o controle de acesso ocorrem rigorosamente no backend (FastAPI), nunca delegando segurança ao frontend (Vue 3).
   - Ocultar botões na interface é apenas ergonomia; a API rejeita qualquer requisição não autorizada (`HTTP 403 Forbidden` ou `HTTP 404 Not Found` para proteção contra enumeração).

4. **Identidade Própria Desacoplada de Provedores Externos:**
   - O sistema possui sua própria entidade canônica de usuário (`User`). Provedores externos (como o Google) conectam-se como identidades externas vinculadas (`ExternalIdentity`), permitindo login local ou social sem duplicar regras de usuário.
   - O identificador estável do Google é o claim `sub`; o e-mail nunca é utilizado como identificador primário no modelo de dados.

5. **Compartilhamento Seguro em Somente-Leitura (Read-Only ACL):**
   - No Roadmap 0.5, o compartilhamento de estudos e acervos concede permissão estritamente de **leitura** aos amigos ou convidados. A edição colaborativa simultânea (CRDTs) fica reservada para versões futuras.

---

## 2. O que NÃO faz parte da Versão 0.5 (Fora de Escopo)

Para assegurar a robustez da fundação multiusuário e a entrega pontual das 10 features, os seguintes temas estão **expressamente fora de escopo**:

- **Edição Colaborativa em Tempo Real / CRDTs:** Não haverá edição simultânea no mesmo estudo (estilo Google Docs) na 0.5. Compartilhamento é estritamente *Read-Only*.
- **Migração do Banco de Dados para PostgreSQL em Produção:** A versão 0.5 opera 100% sobre FastAPI + SQLite WAL no PC. A arquitetura de código deve ser agnóstica a SGDB, mas a migração física de infraestrutura não faz parte desta versão.
- **Criptografia Reversível de Senhas:** Senhas nunca são criptografadas para posterior descriptografia; devem utilizar hash adaptativo unidirecional **Argon2id**.
- **Automação por Inteligência Artificial ou LLMs:** Nenhuma chamada a modelos externos de IA faz parte do núcleo de autenticação, amizades ou controle de sessões.
- **Monetização, Planos de Assinatura ou Pagamentos:** A aplicação permanece livre, pessoal e comunitária.

---

## 3. Quadro Oficial de Status das Features

| ID | Feature | Função Principal | Status |
| :--- | :--- | :--- | :--- |
| **F01** | **Fundação Multiusuário e CRUD Geral** | Associar todos os recursos a proprietários (`user_id`), migrar acervo legado e aplicar autorização server-side | **NÃO INICIADA** |
| **F02** | **Autenticação e Sessões** | Identidade local, login com Argon2id, sessões persistentes em cookies seguros e controle de dispositivos | **NÃO INICIADA** |
| **F03** | **Conta Google e Vinculação de Identidade** | Sign in with Google via Google Identity Services (GIS), claim `sub` estável e suporte a HTTPS Tailscale | **NÃO INICIADA** |
| **F04** | **Sincronização Multidispositivo** | PC e celular sincronizados com estado remoto como fonte da verdade e detecção explícita de conflitos (HTTP 409) | **NÃO INICIADA** |
| **F05** | **Perfil e Privacidade** | Identidade pública com `@username` sem vazar e-mails e controles granulares de exposição (Público, Amigos, Privado) | **NÃO INICIADA** |
| **F06** | **Sistema de Amizades** | Ciclo de vida social completo (solicitar, aceitar, recusar, cancelar, remover, bloquear) e busca por descobríveis | **NÃO INICIADA** |
| **F07** | **Compartilhamento e Permissões por Recurso** | Lista de Controle de Acesso (ACL) granular (Privado, Amigos, Concessão Nominal, Público) somente-leitura | **NÃO INICIADA** |
| **F08** | **Administração e RBAC** | Controle de papéis (`ADMIN` vs `USER`) no servidor, suspensão/reativação e painel administrativo central | **NÃO INICIADA** |
| **F09** | **Notificações e Atividade Social** | Feed desacoplado de eventos, solicitações e compartilhamentos com rastreamento de leitura | **NÃO INICIADA** |
| **F10** | **Segurança, Auditoria e Ciclo de Vida da Conta** | Rate limiting, logs de auditoria sem segredos, desativação/exclusão e exportação completa (LGPD/ANPD) | **NÃO INICIADA** |

---

## 4. Detalhamento Técnico das Features

---

### F01 — Fundação Multiusuário e CRUD Geral

**Status: NÃO INICIADA.**

Transformar todos os modelos de dados da aplicação em entidades formalmente vinculadas a um usuário proprietário (`user_id`), garantindo a preservação absoluta do acervo existente através de uma migração sem perdas.

#### Arquitetura de Dados
```
User (id: UUID, created_at, status)
 │
 ├── Books (user_id FK)
 │    ├── Chapters (book_id FK)
 │    └── Studies (user_id FK, book_id FK, chapter_id FK)
 │
 ├── Categories (user_id FK — categorias pessoais ou vinculadas)
 ├── StudyRelations (user_id FK)
 ├── CanvasPositions (user_id FK)
 ├── Preferences (user_id FK)
 └── Profile (user_id FK)
```

#### Requisitos e Critérios de Aceite
- [ ] **Migração Sem Perdas:** Criação do primeiro usuário canônico do sistema (Owner inicial) via migração Alembic, vinculando todos os registros existentes (`books`, `studies`, `chapters`, `relations`, `categories`) a este usuário.
- [ ] **Chave Estrangeira `user_id`:** Adição da coluna `user_id` (não anulável após migração) em todas as tabelas de conteúdo.
- [ ] **Autorização Server-Side no CRUD Geral:**
  - Create: todo novo registro recebe automaticamente o `user_id` do usuário autenticado.
  - Read: `GET /api/studies`, `GET /api/books` etc., filtram exclusivamente os recursos pertencentes ao usuário ou compartilhados com ele.
  - Update: `PATCH /api/studies/{id}` rejeita requisições se `study.user_id != current_user.id` com `HTTP 403 Forbidden`.
  - Delete / Soft Delete: `DELETE /api/studies/{id}` move à lixeira apenas recursos de propriedade do usuário.
  - Restore: Restauração da lixeira autorizada exclusivamente ao proprietário do item.
- [ ] **Prevenção contra Enumeração (IDOR):** Tentar acessar diretamente recursos de outros usuários por ID sem permissão deve retornar `HTTP 404 Not Found` (ou `HTTP 403 Forbidden` consistente).
- [ ] **Testes Automatizados Herméticos:** Suítes verificando isolamento entre dois usuários fictícios ("Usuário A" não visualiza nem altera dados do "Usuário B").

---

### F02 — Autenticação e Sessões

**Status: NÃO INICIADA.**

Implementar a fundação nativa de autenticação, controle de credenciais locais e gerenciamento seguro de sessões multi-dispositivo.

#### Arquitetura de Identidade
```
User
 ├── id: UUID (Primary Key)
 ├── username: String (único, alfanumérico + hífen/ponto)
 ├── email: String (único, normalizado)
 ├── role: Enum ('admin', 'user')
 ├── status: Enum ('active', 'suspended', 'deactivated')
 │
 ├── LocalCredential (user_id FK)
 │    ├── password_hash: String (Argon2id)
 │    └── password_updated_at: DateTime
 │
 └── UserSession (user_id FK)
      ├── session_token: String (Hash de token opaco de alta entropia)
      ├── device_name: String (ex.: 'PC Principal - Chrome', 'Samsung S24 - Mobile')
      ├── ip_address: String
      ├── user_agent: String
      ├── created_at: DateTime
      ├── last_activity: DateTime
      └── expires_at: DateTime
```

#### Requisitos e Critérios de Aceite
- [ ] **Hash Adaptativo de Senhas:** Utilização estrita da biblioteca `argon2-cffi` para hash e verificação de senhas locais. Proibido MD5, SHA-256 ou cifras reversíveis.
- [ ] **Sessões Seguras e Cookies:**
  - Emissão de identificador de sessão opaco e imprevisível.
  - Transporte via cookie HTTP com flags: `HttpOnly`, `SameSite=Lax` (ou `Strict`) e flag `Secure` configurável (ativada automaticamente em conexões HTTPS/Tailscale).
- [ ] **Ciclo de Vida de Sessões:**
  - Login bem-sucedido gera novo ID de sessão (proteção contra *session fixation*).
  - Logout pontual revoga e destrói o registro da sessão no banco de dados.
  - Expiração configurável (ex.: 30 dias de inatividade com renovação deslizante / sliding window).
- [ ] **Painel de Dispositivos Conectados:**
  - Endpoint `GET /api/auth/sessions` lista sessões ativas com dispositivo, data de criação e último acesso.
  - Endpoint `DELETE /api/auth/sessions/{id}` permite revogar uma sessão remota específica.
  - Endpoint `POST /api/auth/logout-all` permite encerrar todas as outras sessões ativas do usuário.
- [ ] **Dependência FastAPI `get_current_user`:** Middleware / dependência reutilizável que extrai a sessão, valida o status do usuário (`active`) e injeta a entidade `User` nas rotas protegidas.

---

### F03 — Conta Google e Vinculação de Identidade

**Status: NÃO INICIADA.**

Integrar o login e cadastro facilitado através do Google Identity Services (GIS), respeitando o padrão moderno do Google e a infraestrutura de rede local/Tailscale.

#### Arquitetura de Vinculação
```
User
 └── ExternalIdentity (user_id FK)
      ├── provider: 'google'
      ├── provider_subject: String (Claim 'sub' estável do Google)
      ├── email_at_link: String
      └── linked_at: DateTime
```

#### Requisitos e Critérios de Aceite
- [ ] **Adesão ao Google Identity Services (GIS):** Utilização da biblioteca cliente oficial `@react-oauth/google` ou SDK JS moderno do GIS (`accounts.google.com/gsi/client`), sem bibliotecas obsoletas de Sign-In.
- [ ] **Validação Criptográfica no Backend:** O frontend recebe o ID Token (JWT) e o envia para `POST /api/auth/google`. O backend valida o token usando as chaves públicas da API do Google (`google-auth-oauthlib` / `google.oauth2.id_token`).
- [ ] **Identificador Estável (`sub`):** O vínculo entre a conta Google e o `User` é realizado exclusivamente através do claim `sub` gravado em `ExternalIdentity.provider_subject`. O e-mail nunca é tratado como chave primária.
- [ ] **Fluxo de Primeiro Acesso:** Se o `sub` do Google não existir no sistema:
  - Cria um novo registro `User` com perfil básico derivado do nome/foto do Google.
  - Gera um `@username` padrão editável.
  - Vincula o `ExternalIdentity`.
  - Emite a sessão padrão do sistema.
- [ ] **Compatibilidade com Rede e Tailscale:**
  - O Google GIS exige origens autorizadas HTTPS para domínios que não sejam `localhost`.
  - O planejamento e a documentação preveem o uso de certificados HTTPS gerados nativamente pelo Tailscale para o nó da máquina (`*.ts.net`), viabilizando o login Google seguro pelo celular.

---

### F04 — Sincronização Multidispositivo

**Status: NÃO INICIADA.**

Garantir coerência, consistência e integridade em tempo real ou quase-real entre os múltiplos dispositivos do leitor (PC e Celular), com o backend local atuando como a única fonte da verdade.

#### Arquitetura de Sincronização
```
┌────────────┐             ┌─────────────┐             ┌────────────┐
│ PC Local   │────────────▶│  API Central │◀────────────│  Celular   │
│ (Desktop)  │             │  (FastAPI)  │             │ (Tailscale)│
└────────────┘             └──────┬──────┘             └────────────┘
                                  │
                                  ▼
                         Banco de Dados SQLite
                         (WAL + Versioning)
```

#### Requisitos e Critérios de Aceite
- [ ] **Backend como Fonte da Verdade:** Toda escrita é confirmada e persistida no banco central antes de ser refletida.
- [ ] **Versionamento Otimista e Detecção de Conflitos:**
  - Cada entidade editável (`Study`, `Book`, etc.) possui um contador incremental `version: int` e timestamp `updated_at`.
  - Requisições de atualização enviam o campo `expected_version`.
  - Se `current.version != expected_version`, o backend rejeita o salvamento com `HTTP 409 Conflict` e retorna o estado atual do registro.
- [ ] **Tratamento de Conflito na Interface:** A UI do Vue 3 exibe modal de resolução quando ocorre `409 Conflict`, permitindo ao usuário:
  - Preservar a alteração remota.
  - Sobrescrever deliberadamente com o rascunho local.
  - Comparar os dois textos lado a lado antes de decidir.
- [ ] **Sincronização de Metadados de Visualização:**
  - Coordenadas e posições 2D dos cartões no Canvas (`canvas_positions`).
  - Preferências visuais (Superclasse, tamanho de fonte, modo de exibição).
  - Estado da árvore hierárquica e agrupamentos.
- [ ] **Sincronização Pós-Reconexão:** Ao reestabelecer conexão após período offline/standby do celular, a aplicação consulta `GET /api/sync/changes?since=<timestamp>` para reconciliar o estado local.

---

### F05 — Perfil e Privacidade

**Status: NÃO INICIADA.**

Estabelecer a identidade do usuário no ambiente do Caderno de Leitura e conferir autonomia absoluta sobre o que é público, restrito ou estritamente confidencial.

#### Modelo de Perfil e Privacidade
```
UserProfile (user_id FK)
 ├── display_name: String
 ├── username: String (único, @exemplo)
 ├── avatar_url: String (anulável)
 ├── bio: String (anulável, max 280 caracteres)
 ├── profile_visibility: Enum ('public', 'friends', 'private')
 ├── dashboard_visibility: Enum ('public', 'friends', 'private')
 ├── is_discoverable: Boolean (se aparece em buscas gerais)
 └── created_at: DateTime
```

#### Requisitos e Critérios de Aceite
- [ ] **Username Público (@username):** Identificador exclusivo do usuário para interações sociais e buscas. O e-mail nunca é exposto na interface ou em endpoints públicos.
- [ ] **Controle Granular Desacoplado:**
  - Configuração independente para Perfil e Dashboard. Ter perfil público **não** implica dashboard público.
- [ ] **Modos de Visibilidade:**
  - `public`: visível para qualquer usuário autenticado no sistema.
  - `friends`: visível apenas para usuários com relacionamento de amizade `ACCEPTED`.
  - `private`: visível estritamente para o próprio usuário proprietário.
- [ ] **Avatar e Foto:** Suporte a seleção de imagem do perfil (upload de imagem processada em `backend/data/avatars` ou reaproveitamento de avatar do Google GIS).
- [ ] **Estatísticas Públicas Opcionais:** Parâmetro booleano que permite ocultar contadores de livros/estudos da exibição do perfil público.

---

### F06 — Sistema de Amizades

**Status: NÃO INICIADA.**

Criar a infraestrutura de conexão social entre usuários, com ciclo de vida completo de solicitações, aprovações e mecanismos de proteção.

#### Máquina de Estados de Amizade
```
[ Sem Vínculo ]
       │
       ▼ (solicitar)
[ PENDING_SENT ] ──(cancelar)──▶ [ Sem Vínculo ]
       │
       ▼ (destinatário)
[ PENDING_RECEIVED ] ──(recusar)──▶ [ Sem Vínculo ]
       │
       ▼ (aceitar)
  [ ACCEPTED ] ──(desfazer)──▶ [ Sem Vínculo ]
       │
       ▼ (bloquear)
   [ BLOCKED ] ──(desbloquear)──▶ [ Sem Vínculo ]
```

#### Requisitos e Critérios de Aceite
- [ ] **Estados Canônicos:** Tabela `friendships` com `user_id_a`, `user_id_b`, `status` (`pending`, `accepted`, `blocked`) e `action_user_id`.
- [ ] **Ciclo Completo de Operações:**
  - `POST /api/friends/request/{username}`: envia solicitação.
  - `POST /api/friends/accept/{request_id}`: aceita solicitação pendente.
  - `POST /api/friends/reject/{request_id}`: rejeita solicitação.
  - `DELETE /api/friends/cancel/{request_id}`: cancela solicitação enviada.
  - `DELETE /api/friends/{username}`: encerra amizade aceita.
  - `POST /api/friends/block/{username}`: bloqueia usuário.
  - `POST /api/friends/unblock/{username}`: desbloqueia usuário.
- [ ] **Pesquisa Restrita a Descobríveis:**
  - Endpoint `GET /api/users/search?q=toni` retorna apenas usuários com `is_discoverable == True`.
  - Usuários bloqueados (em qualquer direção) nunca aparecem nos resultados de busca.
- [ ] **Bloqueio Efetivo:** Um usuário bloqueado não pode enviar solicitações, visualizar perfil (mesmo que público), ver dashboard ou interagir com o bloqueador.

---

### F07 — Compartilhamento e Permissões por Recurso (ACL)

**Status: NÃO INICIADA.**

Permitir o compartilhamento granular e seletivo de livros, estudos e dashboards com amigos ou com o público, sob o princípio de estrita segurança em somente-leitura.

#### Arquitetura de Permissões
```
Resource (Study / Book / Dashboard)
    │
    ├── owner_id: UUID
    ├── visibility: Enum ('private', 'friends', 'custom', 'public')
    │
    └── ResourcePermission (ACL — para visibilidade 'custom')
         ├── resource_type: String ('study', 'book')
         ├── resource_id: Integer
         ├── granted_to_user_id: UUID
         └── can_view: Boolean (Default: True)
```

#### Requisitos e Critérios de Aceite
- [ ] **Compartilhamento Estritamente Read-Only:** Usuários com acesso concedido podem ler anotações e navegar pelo estudo compartilhado, mas não possuem permissão de editar, alterar tags, adicionar relações ou excluir o recurso.
- [ ] **Granularidade Multinível:**
  - `private`: apenas o proprietário acessa.
  - `friends`: todos os amigos aceitos (`status == accepted`) podem visualizar.
  - `custom`: concessão nominal individual para usuários específicos escolhidos pelo proprietário.
  - `public`: acessível para todos os leitores do sistema através do link direto.
- [ ] **Independência Hierárquica:** A visibilidade de um estudo pode ser configurada independentemente do livro (ex.: Livro Privado, mas Estudo X compartilhado com Amigo João).
- [ ] **Validação em Todas as Rotas:** O serviço de estudos (`study_service.py`) verifica a ACL antes de entregar o payload completo do estudo.
- [ ] **UI de Gestão de Acesso:** Modal de compartilhamento no Vue 3 com listagem de permissões ativas, adição de novos leitores por `@username` e remoção com 1 clique.

---

### F08 — Administração e RBAC

**Status: NÃO INICIADA.**

Fornecer governança e ferramentas de operação para a gestão de contas, papéis de usuário e saúde da aplicação.

#### Papéis e Permissões
- `USER`: Leitor padrão da plataforma. Possui acesso total ao seu próprio acervo e aos recursos compartilhados consigo.
- `ADMIN`: Administrador do sistema. Possui prerrogativa de gerenciar contas, inspecionar saúde da plataforma e auditar ações.

#### Requisitos e Critérios de Aceite
- [ ] **Validação de Role no Servidor:** Dependência FastAPI `require_admin` que verifica no banco se `current_user.role == 'admin'`, abortando com `HTTP 403 Forbidden` para usuários convencionais.
- [ ] **Painel Administrativo (`/admin`):**
  - Listagem completa de contas com colunas: ID, Username, E-mail (somente admin visualiza), Provedor, Data de Criação, Último Acesso, Status, Role e Total de Estudos.
  - Filtros por status (`active`, `suspended`, `deactivated`) e busca por texto.
- [ ] **Operações Administrativas:**
  - Suspender usuário temporariamente (`POST /api/admin/users/{id}/suspend`).
  - Reativar conta suspensa (`POST /api/admin/users/{id}/reactivate`).
  - Promover usuário a admin ou rebaixar a usuário normal.
  - Encerramento forçado de todas as sessões ativas de um usuário problemático.
- [ ] **Proteção de Auto-Bloqueio:** Um administrador não pode suspender a si próprio nem revogar o seu próprio privilégio de admin caso seja o único admin ativo no sistema.
- [ ] **Geração Segura da Conta Admin Inicial:** Script / comando CLI de setup que cria ou promove o primeiro admin de forma determinística e com senha forte via terminal.

---

### F09 — Notificações e Atividade Social

**Status: NÃO INICIADA.**

Implementar um centro de eventos unificado que conecta solicitações de amizade, novos compartilhamentos e avisos administrativos à interface do leitor.

#### Modelo de Notificações
```
Notification
 ├── id: UUID
 ├── user_id: UUID (destinatário)
 ├── actor_id: UUID (autor da ação, se aplicável)
 ├── event_type: Enum ('friend_request', 'friend_accepted', 'study_shared', 'system_alert')
 ├── payload: JSON (links, referências de ID, títulos)
 ├── read_at: DateTime (anulável)
 └── created_at: DateTime
```

#### Requisitos e Critérios de Aceite
- [ ] **Desacoplamento por Eventos:** Ações de amizade ou compartilhamento acionam o serviço de notificações em background de forma não bloqueante.
- [ ] **Centro de Notificações na Barra Superior:**
  - Sino de notificações no cabeçalho da aplicação com contador de eventos não lidos (`unread_count`).
  - Dropdown / painel retrátil listando as notificações mais recentes.
- [ ] **Ações Rápidas no Próprio Item:** Notificações de solicitação de amizade permitem [Aceitar] ou [Recusar] diretamente no painel de notificações, sem navegar para outra tela.
- [ ] **Marcação de Leitura:**
  - Endpoint `PATCH /api/notifications/{id}/read`: marca como lida.
  - Endpoint `POST /api/notifications/read-all`: limpa o badge marcando todas como lidas.
- [ ] **Retenção e Limpeza:** Purga automática configurável de notificações antigas já lidas após 60 dias.

---

### F10 — Segurança, Auditoria e Ciclo de Vida da Conta

**Status: NÃO INICIADA.**

Consolidar a blindagem da aplicação, atender às melhores práticas do OWASP e conformidade com diretrizes de privacidade (LGPD / ANPD), incluindo trilha de auditoria e exportação completa de dados.

#### Requisitos e Critérios de Aceite
- [ ] **Rate Limiting em Endpoints Críticos:**
  - Limite rigoroso de tentativas em `/api/auth/login`, `/api/auth/register` e `/api/auth/google` (ex.: máximo 5 tentativas por IP/usuário a cada 5 minutos, respondendo com `HTTP 429 Too Many Requests`).
- [ ] **Proteção contra Enumeração de Contas:** As mensagens de erro para falha de login ou recuperação de senha devem ser genéricas ("Credenciais inválidas"), sem revelar se o e-mail ou username existe no sistema.
- [ ] **Trilha de Auditoria Estruturada (`AuditLog`):**
  - Registro imutável de eventos sensíveis: login com sucesso/falha, alteração de senha, concessão de privilégio admin, suspensão de conta, exclusão de conta e alteração de ACL.
  - **Zero Segredos em Logs:** Tokens de autenticação, senhas e chaves privadas nunca são gravados nos logs de auditoria.
- [ ] **Ciclo de Vida da Conta (Direitos do Titular — LGPD):**
  - **Desativação Temporária:** O próprio usuário pode desativar sua conta, ocultando seu perfil e acervo até novo login.
  - **Exclusão Definitiva:** Rotina transacional que apaga ou anonimiza dados da conta e remove todas as sessões ativas após confirmação explícita de senha.
- [ ] **Portabilidade e Exportação Completa de Dados:**
  - Endpoint `GET /api/account/export` que compila um arquivo ZIP contendo todo o acervo do usuário (livros, capítulos, estudos em Markdown e JSON estruturado, histórico de leitura, categorias e relacionamentos semânticos).

---

## 5. Ordem Técnica de Execução Recomendada

A ordem das features reflete as dependências lógicas e arquiteturais da aplicação:

```
F01 (Fundação Multiusuário / CRUD)
    │
    ▼
F02 (Autenticação e Sessões Nativas)
    │
    ▼
F03 (Google Identity Services / Tailscale HTTPS)
    │
    ▼
F04 (Sincronização Multidispositivo e Conflitos)
    │
    ▼
F05 (Perfil e Privacidade Granular)
    │
    ▼
F06 (Sistema de Amizades)
    │
    ▼
F07 (Compartilhamento e ACL Read-Only)
    │
    ▼
F08 (Administração e RBAC)
    │
    ▼
F09 (Notificações e Atividade Social)
    │
    ▼
F10 (Segurança, Auditoria e Ciclo de Vida da Conta)
```

---

## 6. Governança e Regras de Versionamento Git

A partir do Roadmap 0.5, vigora a seguinte regra estrita de versionamento:

### **1 Feature Implementada e Validada = 1 Commit Atômico**

1. Cada feature deve passar obrigatoriamente pelo ciclo completo do GitHub Spec Kit:
   ```
   speckit.specify → speckit.clarify → speckit.plan → speckit.checklist → speckit.tasks → speckit.analyze → speckit.implement → speckit.converge
   ```
2. O commit no Git só é criado após aprovação unânime de:
   - `pytest` no backend (100% de testes verdes em bancos descartáveis `tmp_path`).
   - `npm test` no frontend (100% de testes verdes).
   - `npm run build` (compilação TypeScript e Vite limpa, 0 erros).
3. Mensagens de commit sempre em português, curtas e descritivas:
   - `feature — fundação multiusuário e crud geral`
   - `feature — autenticação e sessões`
   - `feature — conta google e vinculação de identidade`
   - `feature — sincronização multidispositivo`
   - `feature — perfil e privacidade`
   - `feature — sistema de amizades`
   - `feature — compartilhamento e permissões por recurso`
   - `feature — administração e rbac`
   - `feature — notificações e atividade social`
   - `feature — segurança, auditoria e ciclo de vida da conta`

Consulte [docs/contexto/CONVENCAO-GIT.md](docs/contexto/CONVENCAO-GIT.md) e [docs/HISTORICO-ROADMAPS.md](docs/HISTORICO-ROADMAPS.md) para diretrizes detalhadas.
