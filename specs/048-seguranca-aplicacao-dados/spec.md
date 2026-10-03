# Feature Specification: F0.6.9 — Segurança de Aplicação e Dados

**Feature Branch**: `048-seguranca-aplicacao-dados`

**Created**: 2026-10-03

**Status**: Ready for Planning

**Input**: User description: "F0.6.9 — Segurança de Aplicação e Dados (Roadmap 0.6: Fortalecer as camadas técnicas do sistema contra vulnerabilidades de aplicação agora que o Leitorum está exposto publicamente, concentrando as questões relacionadas a código, entrada de dados, sanitização contra XSS, auditoria de queries SQL, CORS restrito, cabeçalhos de segurança HTTP, tratamento seguro de exceções sem vazamento de stack traces e auditoria de segredos e configurações de ambiente)."

---

## Clarifications

### Session 2026-10-03

- Q: Como o cabeçalho de política de segurança de conteúdo (CSP) deve ser aplicado pelo middleware do servidor? → A: Bloqueio direto (Enforce) — O servidor emite `Content-Security-Policy` bloqueando de imediato qualquer script, frame ou conexão para domínios não autorizados, calibrando com precisão os domínios essenciais (`self`, `accounts.google.com`, `fonts.googleapis.com`, `fonts.gstatic.com`).
- Q: Qual estrutura de resposta JSON deve ser devolvida pelo backend quando ocorrer uma falha não tratada em produção? → A: Mensagem genérica padronizada com `error_id` correlacionado (`{"detail": "Ocorreu um erro interno no servidor.", "error_id": "<uuid>"}`) — O traceback completo e detalhes da falha são gravados exclusivamente no log do servidor associados a esse UUID, sem expor nenhum detalhe interno ou caminho no corpo da resposta HTTP.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Imunização contra XSS e Sanitização Robusta de Conteúdo (Priority: P1 - MVP)

Como leitor, estudante ou usuário acessando estudos próprios ou compartilhados por outros membros, quero ter a garantia absoluta de que nenhum texto, nota, fichamento importado ou conteúdo formatado seja capaz de executar scripts maliciosos (`<script>`, eventos `onload`/`onerror`, links `javascript:`, esquemas `data:`) no meu navegador, ao mesmo tempo em que todos os recursos legítimos de leitura ativa (occlusões, perguntas interativas, destaques coloridos, notas marginais e formatação Markdown) permaneçam plenamente funcionais.

**Why this priority**: É a proteção primária contra comprometimento de contas e sequestro de sessões via injeção de script em uma aplicação que agora aceita estudos compartilhados e perfis públicos expostos na internet.

**Independent Test**: Pode ser testado de forma isolada submetendo estudos, anotações e fichamentos contendo vetores de ataque XSS conhecidos (ex.: `<script>alert(1)</script>`, `[clique](javascript:alert(1))`, `<img src=x onerror=alert(1)>`, `<svg/onload=alert(1)>`). O sistema deve neutralizar completamente os scripts, exibindo o texto de forma inofensiva e sem disparar nenhum código executável, mantendo intactos os componentes de leitura ativa e marcação.

**Acceptance Scenarios**:

1. **Given** um fichamento contendo links com esquemas inseguros (`javascript:...`, `vbscript:...`, `data:text/html...`), **When** o estudo é renderizado no editor ou no leitor, **Then** o sistema neutraliza o link, convertendo-o em texto seguro ou bloqueando o atributo `href` malicioso, sem executar código.
2. **Given** um payload de estudo importado contendo tags HTML maliciosas ou manipuladores de eventos (`onerror`, `onload`, `onclick`), **When** o conteúdo é processado e exibido, **Then** as tags executáveis são eliminadas ou escapadas antes da inserção no DOM, impedindo qualquer execução de script.
3. **Given** um estudo legítimo com recursos de leitura ativa (occlusão com botão "Revelar", perguntas com botão "Ver resposta", notas e marcações coloridas), **When** a sanitização é aplicada, **Then** todos os nós interativos legítimos funcionam normalmente sem quebra visual ou funcional.

---

### User Story 2 - Cabeçalhos HTTP de Segurança e Política CORS Restrita (Priority: P2)

Como administrador do sistema e leitor acessando o Leitorum via internet (web/Cloudflare Tunnel) ou rede local, quero que todas as respostas HTTP do servidor incluam cabeçalhos de proteção consagrados pela indústria (`Content-Security-Policy`, `X-Content-Type-Options: nosniff`, `Referrer-Policy`, `Permissions-Policy`, e proteção contra framing `X-Frame-Options: SAMEORIGIN` e `frame-ancestors 'self'`), acompanhados de uma política CORS restrita para a arquitetura *same-origin*, para prevenir ataques de *clickjacking*, *MIME-sniffing*, vazamento de referenciadores e requisições cruzadas não autorizadas.

**Why this priority**: Estabelece barreiras defensivas profundas no navegador do leitor (Defense-in-Depth), mitigando ataques mesmo em caso de falhas residuais de aplicação e blindando a fronteira de exposição pública do sistema.

**Independent Test**: Pode ser testado inspecionando os cabeçalhos de resposta HTTP (`curl -I` ou suíte de testes de integração) em todas as rotas públicas e da API: os cabeçalhos de segurança obrigatórios estão presentes em 100% das respostas, o CSP valida a execução apenas de scripts/estilos autorizados (permitindo Google Identity e Google Fonts sem abrir brechas gerais), e requisições CORS de origens não autorizadas são rejeitadas.

**Acceptance Scenarios**:

1. **Given** qualquer requisição enviada ao Leitorum (estática ou API), **When** a resposta é devolvida pelo backend, **Then** os cabeçalhos `X-Content-Type-Options: nosniff`, `Referrer-Policy: strict-origin-when-cross-origin`, `Permissions-Policy: camera=(), microphone=(), geolocation=()` e `X-Frame-Options: SAMEORIGIN` estão presentes.
2. **Given** a navegação na aplicação web, **When** o navegador avalia o cabeçalho `Content-Security-Policy`, **Then** recursos críticos como Google Identity (`accounts.google.com`), Google Fonts e folhas de estilo locais carregam perfeitamente, enquanto scripts externos desconhecidos ou injeções inline não autorizadas são bloqueadas pelo navegador.
3. **Given** uma requisição cruzada (CORS) vinda de um domínio malicioso ou arbitrário (`https://atacante.com`), **When** enviada à API com credenciais, **Then** o servidor não inclui cabeçalhos `Access-Control-Allow-Origin` permissivos para a origem não autorizada.

---

### User Story 3 - Mascaramento de Erros do Backend, Auditoria de Queries e Blindagem de Segredos (Priority: P3)

Como administrador da plataforma e usuário preocupado com a privacidade do acervo, quero que falhas internas inesperadas no servidor (HTTP 500) apresentem respostas genéricas e profissionais sem vazar stack traces, detalhes de arquivos do Windows ou queries do banco, que todas as consultas ao banco de dados sejam parametrizadas contra injeção SQL, e que segredos de ambiente (como segredos de sessão e credenciais) sejam validados preventivamente contra configurações inseguras padrão.

**Why this priority**: Evita que atacantes utilizem mensagens de erro detalhadas ou injeções de SQL para mapear a estrutura interna do servidor, caminhos no disco do usuário ou vulnerabilidades de banco de dados, em total alinhamento com a Constituição do Caderno de Leitura.

**Independent Test**: Pode ser testado disparando intencionalmente uma exceção não tratada em rota de teste/mock: o backend responde com código HTTP 500 e mensagem genérica padronizada com `error_id`, sem exibir linhas de código, traceback ou nomes de tabelas no corpo da resposta; e testado injetando strings maliciosas de SQL em parâmetros de busca/filtros, verificando que as consultas tratam a entrada estritamente como dado literal.

**Acceptance Scenarios**:

1. **Given** uma falha interna não tratada no backend em ambiente de produção, **When** o cliente recebe a resposta HTTP 500, **Then** o corpo da resposta contém mensagem genérica padronizada acompanhada de um `error_id` anônimo, sem nenhum stack trace, caminho de diretório local ou detalhe do SQLAlchemy.
2. **Given** uma requisição de busca ou filtro contendo caracteres e payloads de injeção SQL (`' OR '1'='1`, `UNION SELECT`, `; DROP TABLE`), **When** processada pelo backend, **Then** a consulta utiliza parametrização estrita pelo ORM, tratando os caracteres como termos literais de busca sem alterar a lógica sintática da query.
3. **Given** a inicialização da aplicação em ambiente de produção, **When** a configuração de segredo de sessão (`CADERNO_SESSION_SECRET`) estiver com o valor padrão de desenvolvimento, **Then** o sistema alerta enfaticamente ou orienta a definição de um segredo criptograficamente robusto.

---

### Edge Cases

- O que acontece se um leitor colar um trecho legítimo de código Python/HTML dentro de um bloco de código Markdown (```html ... ```)? O sistema deve preservar o código fielmente para leitura e estudo, escapando-o como texto sem executá-lo no navegador.
- Como o sistema se comporta caso o botão Google Sign-In tente carregar um iframe ou script externo sob a política CSP? O CSP deve incluir explicitamente `https://accounts.google.com` nas diretivas `script-src`, `connect-src` e `frame-src`.
- O que acontece se uma consulta de busca contiver aspas desbalanceadas, caracteres coringa do SQLite (`%`, `_`) ou caracteres nulos? As funções de busca e filtros devem escapar ou tratar os caracteres defensivamente via parâmetros tipados.
- Como o servidor lida com requisições para arquivos internos como `.env`, `.git` ou `caderno.db`? A camada de arquivos estáticos deve bloquear expressamente qualquer requisição direcionada a arquivos com extensões sensíveis ou localizados fora do diretório de assets públicos.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE sanitizar e validar todas as URLs geradas por links Markdown, permitindo exclusivamente os esquemas `http:`, `https:`, `mailto:` e caminhos relativos de âncora, neutralizando esquemas perigosos como `javascript:`, `vbscript:` e `data:`.
- **FR-002**: O sistema DEVE submeter qualquer conteúdo HTML renderizado a partir de Markdown a uma camada de sanitização estrita, eliminando tags executáveis (`<script>`, `<object>`, `<embed>`) e atributos manipuladores de eventos (`on*`).
- **FR-003**: A sanitização de conteúdo NÃO DEVE desativar, degradar ou interferir nas marcações de leitura ativa (occlusões, perguntas com botão de revelar, notas e destaques).
- **FR-004**: O backend DEVE injetar em todas as respostas HTTP os cabeçalhos de segurança: `X-Content-Type-Options: nosniff`, `Referrer-Policy: strict-origin-when-cross-origin`, `Permissions-Policy: camera=(), microphone=(), geolocation=()` e `X-Frame-Options: SAMEORIGIN`.
- **FR-005**: O backend DEVE implementar o cabeçalho `Content-Security-Policy` (CSP) em modo de bloqueio direto (*Enforce*), configurado com diretivas estritas que permitam a operação do Vue, estilos locais, Google Fonts (`fonts.googleapis.com`, `fonts.gstatic.com`) e Google Identity Services (`accounts.google.com`), bloqueando origens externas desconhecidas e prevenindo clickjacking via `frame-ancestors 'self'`.
- **FR-006**: A política CORS da API DEVE restringir origens cruzadas, operando em modo same-origin por padrão e permitindo origens explícitas apenas quando expressamente configuradas via variável de ambiente (`CADERNO_CORS_ORIGINS`).
- **FR-007**: O backend DEVE capturar exceções não tratadas através de um manipulador global de erros, retornando resposta HTTP 500 padronizada (`{"detail": "Ocorreu um erro interno no servidor.", "error_id": "<uuid>"}`) em ambiente de produção, sem expor stack traces, traceback de Python, consultas SQL ou caminhos do sistema de arquivos, gravando o traceback completo e o `error_id` correspondente exclusivamente no log do servidor para correlação e auditoria.
- **FR-008**: Todas as consultas ao banco de dados DEVEM utilizar parametrização estrita de dados através do SQLAlchemy ORM ou expressões com *bind parameters*, proibindo concatenação direta de strings do usuário em comandos SQL.
- **FR-009**: O sistema DEVE auditar e impedir o acesso direto ou exposição pública a arquivos sensíveis da infraestrutura local, incluindo o banco ativo (`backend/data/caderno.db`), backups, arquivos de ambiente (`.env`) e histórico Git.
- **FR-010**: O sistema DEVE validar a robustez da chave secreta de sessão (`CADERNO_SESSION_SECRET`) no arranque da aplicação, alertando quando executado com chaves fracas ou padrão em ambiente de produção.

---

### Key Entities *(include if feature involves data)*

- **SecurityPolicyConfiguration**: Estrutura de configuração que define as origens CORS autorizadas, as diretivas do cabeçalho Content-Security-Policy e o modo de operação (produção vs desenvolvimento local).
- **SanitizedContent**: Representação segura de texto formatado resultante do pipeline de parsing e sanitização, livre de vetores de injeção XSS e preservando metadados de leitura ativa.
- **SecurityErrorResponse**: Contrato padronizado de resposta para erros 500 da API, contendo código HTTP, mensagem amigável sem dados confidenciais e identificador `error_id` para correlação e rastreio no log interno.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% dos testes automatizados de injeção XSS com payloads clássicos e modernos (tags script, atributos de evento, URLs javascript:) são neutralizados sem execução indevida no navegador.
- **SC-002**: 100% das respostas HTTP do servidor apresentam os cabeçalhos de segurança obrigatórios (`X-Content-Type-Options`, `Referrer-Policy`, `Permissions-Policy`, `X-Frame-Options` e `Content-Security-Policy`).
- **SC-003**: 0% de vazamento de stack traces, nomes de arquivos internos, queries SQL ou caminhos do Windows em respostas de erro da API.
- **SC-004**: 100% das consultas de busca e filtros toleram caracteres especiais e sequências de injeção SQL sem falhas sintáticas ou alterações na lógica da consulta.
- **SC-005**: Tempo de renderização e parsing de Markdown e leitura ativa mantém-se instantâneo, com sobrecarga de sanitização imperceptível ao usuário (menos de 15ms adicionais por documento típico).

---

## Assumptions

- O Leitorum utiliza arquitetura same-origin em produção (atrás do Cloudflare Tunnel ou servidor web local), portanto CORS aberto para domínios arbitrários não é necessário para o fluxo principal.
- Recursos legítimos como Google Sign-In e Google Fonts requerem comunicação com `accounts.google.com`, `fonts.googleapis.com` e `fonts.gstatic.com`, devendo ser explicitamente acomodados no Content-Security-Policy.
- A sanitização de Markdown deve operar no cliente antes da injeção no DOM, servindo como defesa em profundidade juntamente com as regras do parser `markdown-it`.
- Os testes de segurança serão executados exclusivamente contra instâncias de teste e bancos descartáveis em `tmp_path`, em cumprimento irrestrito ao Princípio II da Constituição.
