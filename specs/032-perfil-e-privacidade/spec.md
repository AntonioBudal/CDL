# Feature Specification: Perfil e Privacidade

**Feature Branch**: `032-perfil-e-privacidade`  
**Created**: 2026-09-24  
**Status**: Ready for Planning  
**Input**: User description: "F05 - Perfil e Privacidade"

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Gestão da Identidade Pública e Handle Exclusivo (Priority: P1)

Como leitor autenticado, desejo definir e gerenciar meu identificador público (@username), nome de exibição e biografia, garantindo que meu e-mail pessoal permaneça estritamente protegido e nunca seja exposto para outros usuários do sistema.

**Why this priority**: Estabelece o alicerce fundamental de identidade social do sistema. Sem um identificador público seguro e desvinculado de dados de login (e-mail), interações sociais, conexões e compartilhamento entre leitores são impossíveis.

**Independent Test**: Um leitor acessa a área de perfil nos Ajustes, escolhe um `@username` único e um nome de exibição, salva as alterações e consulta seu perfil público através de outra conta, verificando que o nome e `@username` estão visíveis e seu e-mail não aparece em nenhum elemento da tela ou resposta.

**Acceptance Scenarios**:
1. **Given** um usuário recém-cadastrado no sistema, **When** ele acessa as configurações de perfil pela primeira vez, **Then** ele pode escolher um handle `@username` único de 3 a 30 caracteres alfanuméricos e um nome de exibição amigável.
2. **Given** um usuário tentando alterar seu `@username`, **When** ele digita um handle já utilizado por outro leitor, **Then** o sistema avisa imediatamente sobre a indisponibilidade e impede a gravação duplicada.
3. **Given** um perfil público acessado por outro leitor, **When** a página do perfil é renderizada, **Then** o nome de exibição, `@username` e biografia são exibidos, sem qualquer exposição do endereço de e-mail da conta.

---

### User Story 2 - Controles Granulares de Privacidade Desacoplados (Priority: P1)

Como leitor, desejo configurar níveis de visibilidade independentes para meu perfil e para meu painel de estudos (Dashboard), escolhendo entre visibilidade Pública, Apenas Amigos ou Estritamente Privada.

**Why this priority**: Autonomia e consentimento são valores centrais do Caderno de Leitura. Leitores devem poder ter um perfil visível para interações sociais sem serem forçados a expor seu ritmo e hábitos de estudo (Dashboard).

**Independent Test**: Um leitor configura seu Perfil como "Público" e seu Dashboard como "Privado". Ao acessar o perfil desse leitor com uma conta sem vínculo de amizade, o visitante consegue visualizar o perfil, mas o acesso ao painel de estudos e métricas permanece bloqueado com indicação clara de restrição.

**Acceptance Scenarios**:
1. **Given** um leitor ajustando suas preferências de privacidade, **When** ele altera a visibilidade do Perfil para "Público" e do Dashboard para "Privado", **Then** essas escolhas são salvas independentemente e passam a vigorar de imediato.
2. **Given** um leitor com Perfil configurado como "Apenas Amigos", **When** um usuário que não está em sua lista de amizades tenta visualizar o perfil, **Then** o sistema oculta as informações detalhadas e exibe o estado restrito configurado pela política de privacidade.
3. **Given** um leitor com Perfil configurado como "Privado", **When** qualquer outro usuário tenta acessar a página correspondente, **Then** o sistema aplica a política de privacidade restrita sem vazar dados pessoais.

---

### User Story 3 - Personalização Visual do Perfil e Imagem de Avatar (Priority: P2)

Como leitor, desejo personalizar a imagem do meu avatar no perfil, podendo fazer upload de uma imagem própria do dispositivo ou reaproveitar a foto já vinculada de uma conta Google conectada.

**Why this priority**: A imagem de avatar enriquece a identidade visual e o acolhimento do leitor no ambiente do sistema, além de facilitar a identificação rápida em futuras interações e comentários.

**Independent Test**: O leitor seleciona um arquivo de imagem em seu computador ou celular, pré-visualiza o enquadramento quadrado e salva; em seguida, a imagem do avatar é renderizada no cabeçalho e na página pública de perfil.

**Acceptance Scenarios**:
1. **Given** um leitor nos ajustes de perfil, **When** ele envia um arquivo de imagem válido (PNG, JPEG ou WebP de até 2MB), **Then** a imagem é aceita, ajustada para formato quadrado e definida como seu avatar ativo.
2. **Given** um leitor que autenticou sua conta via Google, **When** ele visualiza as opções de avatar, **Then** ele tem a opção de utilizar a foto de sua conta Google como avatar ativo ou substituí-la por um upload personalizado.
3. **Given** um leitor sem foto cadastrada, **When** seu perfil ou card é exibido, **Then** o sistema apresenta um avatar gerado com as iniciais estilizadas do seu nome de exibição com base no sistema visual do caderno.

---

### User Story 4 - Blindagem de Estatísticas de Leitura e Descobrimento (Priority: P3)

Como leitor reflexivo, desejo a opção de ocultar minhas estatísticas quantitativas de leitura (total de livros lidos, estudos concluídos, sequência de dias) e controlar se meu perfil pode ser encontrado em buscas públicas no sistema.

**Why this priority**: Nem todos os leitores desejam expor métricas numéricas ou serem localizados em mecanismos gerais de busca, reforçando o caráter introspectivo e seguro do caderno de estudos.

**Independent Test**: Um leitor marca a opção "Ocultar estatísticas no perfil público" e "Não permitir que meu perfil apareça em buscas gerais". Ao pesquisar por seu nome na busca de usuários, o perfil não aparece nos resultados, e o perfil público renderizado não exibe contadores de livros ou estudos.

**Acceptance Scenarios**:
1. **Given** a opção "Ocultar estatísticas no perfil público" habilitada, **When** qualquer visitante visualiza a página pública do perfil, **Then** contadores de acervo, livros e estudos concluídos não são exibidos.
2. **Given** a opção "Perfil descobrível em buscas" desmarcada, **When** outro usuário pesquisa pelo nome de exibição no campo de busca de leitores, **Then** esse perfil não é listado nos resultados.

---

### Edge Cases

- **Caracteres especiais no handle**: Usuário tenta cadastrar um handle com espaços, acentos, pontuação inválida ou emojis (ex.: `@leitor esperto!` ou `@ana📚`); o sistema deve sanitizar e aceitar estritamente caracteres alfanuméricos minúsculos, hífens e pontos.
- **Tamanho excessivo de biografia**: O leitor tenta inserir uma biografia com mais de 280 caracteres; a interface deve exibir um contador regressivo claro e bloquear o envio além do limite.
- **Upload de arquivo inválido ou corrompido**: O usuário tenta enviar um arquivo PDF, executável ou imagem truncada; o sistema deve validar o formato real e tamanho do arquivo, rejeitando com mensagem clara em português sem falha de sistema.
- **Perfil inacessível ou inexistente**: Visitante tenta acessar a URL de um perfil que foi desativado ou cujo handle não existe; a interface deve apresentar tela de estado vazio explicativa sem alertar sobre falhas técnicas internas.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE permitir a cada leitor cadastrar e manter um identificador público exclusivo no formato `@username`, composto por 3 a 30 caracteres alfanuméricos, hífens ou pontos.
- **FR-002**: O sistema DEVE validar a unicidade do `@username`, impedindo colisões e normalizando maiúsculas/minúsculas para prevenir duplicidade de identidade.
- **FR-003**: O sistema NUNCA DEVE expor o endereço de e-mail do usuário em páginas de perfil, respostas públicas ou metadados de compartilhamento.
- **FR-004**: O sistema DEVE permitir configurar um nome de exibição (`display_name`) de até 60 caracteres e uma biografia textual de até 280 caracteres.
- **FR-005**: O sistema DEVE fornecer controles independentes de visibilidade para **Perfil** e **Dashboard**, suportando os níveis: `Público`, `Amigos` e `Privado`.
- **FR-006**: A visibilidade do Dashboard NÃO DEVE ser acoplada à visibilidade do Perfil (um perfil público pode manter seu painel de estudos como estritamente privado).
- **FR-007**: O sistema DEVE suportar avatar customizado via upload local de arquivo de imagem (PNG, JPEG ou WebP de até 2MB) processado e armazenado localmente no servidor (`backend/data/avatars/`), bem como permitir opcionalmente a seleção da foto de perfil vinculada da conta Google do usuário.
- **FR-008**: O sistema DEVE disponibilizar opção booleana para ocultar contadores quantitativos de leitura (livros e estudos) no perfil público.
- **FR-009**: O sistema DEVE fornecer controle booleano para definir se o leitor é descobrível em buscas do sistema (`is_discoverable`).
- **FR-010**: O sistema DEVE apresentar um cartão discreto e seguro ao visitante que acessar um perfil com visibilidade restrita (`Privado` ou `Amigos` sem relacionamento ativo), exibindo exclusivamente o nome de exibição, avatar e selo de restrição ("Este perfil é privado" ou "Visível apenas para amigos"), ocultando estritamente biografia, estatísticas e acervo.
- **FR-011**: O sistema DEVE permitir a alteração livre do `@username` a qualquer momento na área de ajustes do perfil, desde que o novo handle esteja vago e atenda aos requisitos de unicidade e formatação (3 a 30 caracteres alfanuméricos, hífens ou pontos).
- **FR-012**: O sistema DEVE exibir avatares substitutos elegantes baseados nas iniciais do leitor caso nenhum avatar personalizado tenha sido configurado.

---

### Key Entities

- **Perfil do Usuário (`UserProfile`)**: Representa a identidade pública e as configurações de exposição do leitor. Atributos: nome de exibição, handle único `@username`, imagem de avatar, biografia curta, nível de visibilidade do perfil, nível de visibilidade do dashboard, flag de descobrimento em buscas, flag de exibição de estatísticas e data de criação/atualização.
- **Visibilidade de Recurso**: Classificação de privacidade (`Público`, `Amigos`, `Privado`) aplicada de forma desacoplada aos diferentes aspectos da conta.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: O leitor consegue configurar ou atualizar seus dados de perfil (nome, biografia, visibilidade) em menos de 1 minuto em dispositivo desktop ou móvel.
- **SC-002**: 100% das páginas públicas e respostas do sistema preservam o sigilo do e-mail do leitor (zero vazamento de e-mails em requisições públicas).
- **SC-003**: Alterações nos níveis de privacidade entram em vigor imediatamente para todos os visitantes do sistema, sem atraso de cache perceptível.
- **SC-004**: O processamento e apresentação do avatar ocorrem de forma fluida, com imagens redimensionadas adequadamente para exibição rápida mesmo em conexões móveis.

---

## Assumptions

- O sistema já possui infraestrutura de autenticação de usuários e controle de sessões operacionais (Features 01, 02 e 03).
- Usuários autenticados podem navegar para perfis públicos de outros membros através de link direto ou menção pelo handle.
- O sistema de amizades formal (solicitar/aceitar amizades) será enriquecido na Feature 06; nesta feature (F05), o nível `Amigos` já fica previsto na regra de privacidade e modelo de dados, comportando-se inicialmente como restrito para usuários que não sejam o próprio proprietário até a conclusão de F06.
- Toda a interface gráfica respeita o sistema visual sem emojis informais e mantém compatibilidade com os perfis cinemáticos das Superclasses.
