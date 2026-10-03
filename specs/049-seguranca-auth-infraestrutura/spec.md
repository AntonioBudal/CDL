# Feature Specification: F0.6.10 — Segurança de Autenticação, Abuso e Infraestrutura

**Feature Branch**: `049-seguranca-auth-infraestrutura`

**Created**: 2026-10-03

**Status**: Ready for Planning

**Input**: User description: "F10" (F0.6.10 — Segurança de Autenticação, Abuso e Exposição da Infraestrutura do Roadmap 0.6)

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Mitigação de Força Bruta e Proteção contra Abuso via Rate Limiting (Priority: P1) 🎯 MVP

Como visitante, leitor ou operador do Leitorum em rede pública,
quero que o sistema restrinja tentativas repetitivas e abusivas contra endpoints de autenticação e rotas de processamento pesado,
para que robôs maliciosos ou ataques de força bruta não comprometam credenciais, não sobrecarreguem o servidor local e os usuários legítimos continuem acessando o serviço sem lentidão.

**Why this priority**:
A exposição pública do Leitorum na internet torna o formulário de login e registro o alvo primário de varreduras automatizadas e ataques de força bruta de credenciais. Proteger o acesso é o primeiro requisito de sobrevivência de um serviço exposto.

**Independent Test**:
Submeter requisições sequenciais rápidas com credenciais inválidas para o endpoint de autenticação a partir de um mesmo endereço de origem. Verificar que, ao exceder o limiar de segurança, a aplicação responde com HTTP 429 Too Many Requests, fornecendo o tempo de espera no cabeçalho `Retry-After`, enquanto requisições de outros endereços e operações de leitura legítima continuam respondendo normalmente.

**Acceptance Scenarios**:

1. **Given** um cliente realizando tentativas de autenticação com senhas incorretas, **When** registrar 5 falhas consecutivas de autenticação a partir do mesmo IP dentro de uma janela de 1 minuto (ou exceder a cota global de 30 requisições por minuto nos endpoints de `/api/auth/*`), **Then** o sistema deve bloquear novas requisições daquela origem com status HTTP 429 (Too Many Requests) durante 60 segundos, emitindo cabeçalho `Retry-After: 60` e mensagem informativa em português.
2. **Given** um usuário que foi bloqueado temporariamente por excesso de tentativas, **When** o tempo indicado pelo cabeçalho `Retry-After` expirar, **Then** o sistema deve restabelecer a capacidade de submeter novas requisições de autenticação normalmente.
3. **Given** um cliente legítimo navegando pelo acervo e realizando consultas de leitura, **When** consome as páginas normais de estudo e catálogo, **Then** seu tráfego de leitura não deve ser interrompido nem penalizado pelas regras de contenção de rotas sensíveis.
4. **Given** múltiplas tentativas automatizadas de criação de contas ou solicitações de exportação em massa de dados, **When** a taxa ultrapassar a tolerância do endpoint, **Then** o servidor deve restringir as operações abusivas retornando código 429.

---

### User Story 2 - Blindagem de Sessões, Cookies Seguros e Invalidação Efetiva (Priority: P2)

Como usuário autenticado do Leitorum em computadores pessoais e dispositivos móveis,
quero que minha sessão seja gerenciada por cookies invioláveis e descartada com segurança após o logout,
para que invasores em redes compartilhadas não interceptem ou reutilizem meus identificadores de sessão.

**Why this priority**:
Mesmo com senhas fortes, falhas de gerenciamento de sessão (como cookies desprotegidos, ausência de invalidação no servidor ou reutilização de identificadores) anulam a segurança da conta e expõem os dados privados do acervo.

**Independent Test**:
Realizar login na aplicação e inspecionar os cabeçalhos de resposta `Set-Cookie`. Comprovar que o cookie de autenticação possui flags `HttpOnly`, `SameSite=Lax` e política de `Secure` apropriada ao protocolo da conexão. Ao acionar o encerramento da sessão (logout), verificar que a sessão é imediatamente revogada no servidor e que uma requisição subsequente portando o cookie antigo é terminantemente rejeitada com HTTP 401.

**Acceptance Scenarios**:

1. **Given** uma autenticação bem-sucedida, **When** o servidor emitir os cookies de sessão, **Then** os cookies devem conter os atributos `HttpOnly` (inacessíveis via scripts do cliente), `SameSite=Lax` e política adaptativa para o atributo `Secure`: ativado (`Secure=True`) quando a requisição for HTTPS direta ou apresentar o cabeçalho `X-Forwarded-Proto: https` (como em acessos via Cloudflare Tunnel/proxy reverso), e mantido desativado (`Secure=False`) em conexões HTTP locais puras (`localhost` ou rede privada sem SSL) para preservar a operabilidade sem certificados locais.
2. **Given** um usuário com sessão ativa, **When** o usuário acionar o comando de logout, **Then** o sistema deve invalidar a sessão no registro de sessões ativas do servidor e sobrescrever o cookie no cliente com expiração imediata.
3. **Given** uma requisição enviando um identificador de sessão que já foi invalidado pelo logout, **When** tentar acessar qualquer recurso privado, **Then** o servidor deve recusar a requisição com HTTP 401 (Não Autorizado).
4. **Given** uma transição de privilégio (como login bem-sucedido a partir de um estado não autenticado), **When** a sessão for iniciada, **Then** um novo identificador exclusivo de sessão deve ser gerado para impedir ataques de fixação de sessão.

---

### User Story 3 - Integridade da Fronteira com Proxy Reverso e Proteção de Recursos Privados (Priority: P3)

Como administrador do sistema,
quero que o Leitorum determine com precisão a identidade dos clientes atrás de túneis ou proxies reversos (como Cloudflare Tunnel) e proteja recursos internos e arquivos físicos,
para que cabeçalhos falsificados não burlem as proteções do sistema e nenhum arquivo confidencial ou administrativo vaze.

**Why this priority**:
Quando a aplicação roda atrás de um proxy reverso ou túnel, todos os pacotes brutos chegam com IP de loopback (`127.0.0.1`). Se o sistema não extrair confiavelmente o IP real do cliente nem proteger recursos privados (backups, banco de dados físico, capas e rotas administrativas), as políticas de rate limit e auditoria tornam-se inócuas ou burláveis.

**Independent Test**:
Submeter requisições simulando tráfego vindo através de proxy reverso com cabeçalhos como `CF-Connecting-IP` e `X-Forwarded-For`. Verificar que o Leitorum extrai o endereço IP correto para auditoria e rate limiting, sem permitir spoofing em ambientes de rede aberta. Requisitar endpoints restritos (como `/api/backups`) sem privilégios administrativos e verificar que o acesso é estritamente bloqueado com HTTP 403.

**Acceptance Scenarios**:

1. **Given** uma requisição roteada por proxy reverso ou Cloudflare Tunnel, **When** o servidor processar a requisição para fins de log, auditoria ou rate limiting, **Then** o endereço IP real do cliente deve ser extraído confiavelmente através de cabeçalhos de proxy designados.
2. **Given** um usuário comum ou visitante sem perfil de administrador, **When** tentar requisitar endpoints administrativos de gestão do sistema, downloads de backups completos (`/api/backups`) ou inspeção de logs, **Then** o sistema deve negar terminantemente o acesso com status HTTP 403 (Proibido).
3. **Given** tentativas de forjar cabeçalhos de encaminhamento vindas de redes não confiáveis, **When** a aplicação avaliar a confiabilidade do cliente, **Then** o sistema não deve permitir que clientes arbitrários burlem as restrições forjando endereços de IP fictícios.
4. **Given** arquivos de mídia privada (como capas de livros de outros usuários ou exportações temporárias), **When** requisitados por usuários sem permissão sobre o recurso, **Then** o sistema deve validar a posse e impedir o acesso não autorizado.

---

## Edge Cases

- **Flutuações de Conexão Móvel**: O que acontece quando o IP do cliente se altera rapidamente (ex.: transição de Wi-Fi para dados móveis)? A sessão permanece válida com base no cookie de sessão criptografado e não deve deslogar desnecessariamente o usuário, a menos que a sessão seja explicitamente revogada.
- **Requisições de Saúde Interna (Health Check)**: Como o sistema lida com sondagens automatizadas de monitoramento local (`/api/health`)? O tráfego de health check proveniente de `localhost` ou de ferramentas de monitoramento deve ser isento de limites restritivos de taxa para não gerar falsos positivos de indisponibilidade.
- **Falha de Comunicação com Proxy**: Como a aplicação se comporta se o proxy deixar de enviar o cabeçalho `CF-Connecting-IP`? O sistema deve recorrer de forma segura ao próximo cabeçalho da cadeia (`X-Forwarded-For` ou IP direto da conexão), garantindo que a aplicação nunca pare por ausência de um cabeçalho opcional.
- **Sessões Simultâneas Múltiplas**: O que acontece se o usuário fizer login em dois navegadores diferentes? As sessões devem ser independentes no gerenciamento de tokens, permitindo que o encerramento em um dispositivo não afete os demais, a menos que o usuário solicite o encerramento de todas as sessões.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE aplicar controle de taxa (rate limiting) baseado em janelas de tempo deslizantes ou balde de fichas para endpoints sensíveis de autenticação (login de usuário, criação de conta, autenticação Google e reativação).
- **FR-002**: O sistema DEVE emitir resposta HTTP 429 com cabeçalho padrão `Retry-After` (especificando os segundos restantes para liberação) e corpo JSON com mensagem clara em português sempre que uma taxa limite for excedida.
- **FR-003**: O sistema NÃO DEVE aplicar limites severos de taxa sobre operações regulares de leitura, consulta de estudos ou navegação no catálogo.
- **FR-004**: O sistema DEVE configurar cookies de autenticação com a diretiva `HttpOnly` ativada incondicionalmente, impedindo qualquer acesso por código JavaScript no cliente.
- **FR-005**: O sistema DEVE configurar a diretiva `SameSite=Lax` nos cookies de autenticação para proteger contra ataques de CSRF (Cross-Site Request Forgery) mantendo a usabilidade em redirecionamentos.
- **FR-006**: O sistema DEVE ajustar a diretiva `Secure` dos cookies com base no protocolo efetivo da requisição ou configuração explícita de ambiente.
- **FR-007**: O sistema DEVE invalidar de forma definitiva no servidor o registro da sessão ao receber uma solicitação de logout, rejeitando o reuso subsequente do token revogado.
- **FR-008**: O sistema DEVE regenerar identificadores de sessão em transições de autenticação para blindar a aplicação contra ataques de fixação de sessão.
- **FR-009**: O sistema DEVE ser capaz de identificar o IP real do cliente através de cabeçalhos de proxy confiáveis (`CF-Connecting-IP`, `X-Forwarded-For`) para alimentação precisa das tabelas de rate limiting e registros de auditoria.
- **FR-010**: O sistema DEVE proteger endpoints administrativos, de cópia de segurança (`/api/backups`) e de dados confidenciais através de controle estrito de permissões e papéis (RBAC).
- **FR-011**: O sistema DEVE garantir que arquivos temporários de exportação e mídias de acervo respeitem os direitos de acesso e propriedade do usuário.

---

### Key Entities *(include if feature involves data)*

- **Sessão de Usuário (`SessionRecord`)**: Representa a instância de autenticação de um usuário no sistema, contendo identificador único de sessão, identificador do usuário proprietário, data/hora de criação, data/hora da última atividade, status de revogação/validade e identificação de dispositivo/navegador.
- **Registro de Controle de Taxa (`RateLimitBucket`)**: Estrutura em memória ou armazenamento efêmero que contabiliza requisições por endereço de origem (ou chave composta IP + endpoint) dentro de uma janela temporal delimitada, registrando contagem de tentativas, carimbo de data/hora da última requisição e momento de liberação.
- **Política de Risco de Endpoint (`EndpointRiskPolicy`)**: Definição da classificação de risco das rotas da API, determinando a cota máxima de requisições permitidas por janela de tempo (ex.: alto risco para login/registro; moderado para exportações pesadas; padrão para demais rotas).

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% das tentativas abusivas que ultrapassarem o limite configurado de requisições em endpoints de autenticação são interrompidas com status HTTP 429 e cabeçalho `Retry-After`.
- **SC-002**: 100% dos cookies de sessão emitidos possuem a flag `HttpOnly` ativada e diretiva `SameSite=Lax`.
- **SC-003**: Ao acionar o encerramento da sessão, o token é invalidado no servidor em menos de 100 milissegundos e 100% das tentativas subsequentes de reuso com o mesmo token recebem HTTP 401.
- **SC-004**: O processamento de checagem de rate limit e extração de IP adiciona menos de 3 milissegundos à latência média das requisições atendidas pelo servidor.
- **SC-005**: 100% dos acessos não autorizados a rotas administrativas ou de backup são bloqueados com HTTP 401 ou 403 sem vazar informações confidenciais do acervo ou do sistema.

---

## Assumptions

- O Leitorum opera como um processo único local (FastAPI/Uvicorn), podendo ser acessado diretamente na rede local (`localhost:8000`) ou exposto através de um túnel de proteção como Cloudflare Tunnel.
- O controle de taxa em memória é adequado e suficiente para a arquitetura de processo único do servidor local, dispensando a necessidade de serviços externos pesados como Redis.
- As consultas públicas de leitura (como artigos abertos ou SEO público da F0.6.8) devem permanecer com alta disponibilidade e baixíssima fricção para visitantes legítimos.
- O banco ativo local (`backend/data/caderno.db`) permanece estritamente privado, nunca devendo ser exposto por nenhum endpoint HTTP direto.
