# Feature Specification: F0.6.6 — Apoie o Leitorum

**Feature Branch**: `045-apoie-o-leitorum`

**Created**: 2026-09-29

**Status**: Ready for Planning

**Input**: User description: "F0.6.6 — Apoie o Leitorum: Criar uma forma simples e opcional para que usuários possam contribuir financeiramente para manutenção do Leitorum, acessível pelo rodapé e rota pública dedicada, com suporte a PIX, Google Pay/link configurável e sem processamento financeiro próprio."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Consulta da Página de Apoio e Contribuição via PIX (Priority: P1) [MVP]

Como usuário ou simpatizante do Leitorum, desejo acessar uma página informativa e discreta que apresente os meios para apoiar a manutenção do projeto, permitindo-me copiar a chave PIX ou ler o QR Code diretamente na tela.

**Why this priority**: É o cerne da proposta de sustentabilidade voluntária. Permite que qualquer pessoa realize uma contribuição financeira direta e opcional sem necessidade de cadastro bancário embutido ou intermediários complexos.

**Independent Test**: Navegar até a rota pública de apoio (`/apoiar`), visualizar a mensagem institucional de gratuidade e propósito, identificar os dados do PIX (chave, titular e QR Code) e acionar o botão de cópia, verificando a confirmação visual e tátil de chave copiada.

**Acceptance Scenarios**:

1. **Given** que o administrador configurou uma chave PIX e nome do titular, **When** um visitante acessa a página de apoio, **Then** a tela exibe o texto explicativo sobre a manutenção voluntária, a chave PIX textual legível, a identificação do titular, a imagem do QR Code correspondente e um botão acessível para copiar a chave.
2. **Given** que a chave PIX foi exibida na tela, **When** o usuário clica no botão "Copiar Chave PIX", **Then** o texto da chave é transferido para a área de transferência do sistema e um aviso temporário de confirmação ("Chave copiada") é apresentado de forma acessível.
3. **Given** que o usuário está navegando em dispositivo móvel com câmera apontada para uma tela externa ou usando o mesmo aparelho, **When** ele seleciona a chave, **Then** ele consegue alternar para o aplicativo do seu banco sem bloqueios ou pop-ups intrusivos.

---

### User Story 2 - Acesso Discreto e Elegante via Rodapé da Aplicação (Priority: P2)

Como leitor ou estudante que utiliza o Leitorum regularmente, desejo encontrar o link para apoiar o projeto de maneira sutil e não intrusiva no rodapé das páginas, sem que haja poluição visual no menu principal ou janelas insistentes de cobrança.

**Why this priority**: Preserva a dignidade e a atmosfera de concentração do Leitorum. A contribuição voluntária jamais deve competir com a leitura nem importunar o usuário com banners invasivos.

**Independent Test**: Navegar pelas páginas da aplicação (Dashboard, Acervo, Leituras, etc.) e verificar que a barra superior e o menu lateral não contêm abas de doação; rolar até o rodapé e constatar o link discreto "Apoie o Leitorum", que direciona com fluidez para a tela de apoio.

**Acceptance Scenarios**:

1. **Given** que o usuário está em qualquer tela pública ou autenticada que possua rodapé de encerramento, **When** ele observa as opções de rodapé, **Then** ele visualiza links institucionais neutros como "Sobre" e "Apoie o Leitorum".
2. **Given** que o usuário visualiza o link no rodapé, **When** ele clica em "Apoie o Leitorum", **Then** a navegação o encaminha imediatamente para a rota pública de apoio, sem recarregamento brusco da página.
3. **Given** que o usuário está no modo de leitura imersiva ou em tela cheia, **When** ele estuda, **Then** nenhum aviso de apoio ou banner flutuante é exibido na área de foco.

---

### User Story 3 - Suporte a Link de Pagamento Alternativo (Google Pay / Link Externo) e Gestão de Estados (Priority: P3)

Como administrador do sistema, desejo poder disponibilizar uma segunda opção de contribuição através de um link externo configurável (ex.: Google Pay, plataforma de financiamento coletivo ou link direto de pagamento), mantendo controle sobre quais meios estão ativos ou inativos.

**Why this priority**: Usuários internacionais ou pessoas que preferem pagar via carteiras digitais ou links protegidos precisam de um meio conveniente caso não utilizem o sistema PIX brasileiro.

**Independent Test**: Configurar um link de pagamento alternativo e verificar sua exibição com botão claro que abre em nova aba segura; desativar a opção e constatar que a tela se reorganiza elegantemente sem lacunas ou erros.

**Acceptance Scenarios**:

1. **Given** que o meio alternativo (Google Pay/Link externo) está configurado e ativo, **When** o usuário consulta a página de apoio, **Then** um botão seguro de redirecionamento externo ("Contribuir via Google Pay / Link") é exibido com indicação de que o destino abrirá em nova janela.
2. **Given** que um dos meios de contribuição não está configurado, **When** a página é renderizada, **Then** apenas o meio ativo é apresentado, sem deixar espaços vazios, botões desabilitados confusos ou mensagens de erro.
3. **Given** que nenhum método de pagamento financeiro está configurado, **When** o usuário visita a página de apoio, **Then** a tela exibe uma mensagem de agradecimento ao interesse e sugere formas comunitárias de apoio (compartilhamento do acervo, feedback e sugestões).

---

### Edge Cases

- **Falha de Permissão na Área de Transferência (Clipboard API)**: Quando o navegador rejeitar a cópia programática (por restrições de permissão do navegador ou contexto não seguro HTTP em rede local), a chave PIX deve ser selecionada automaticamente em campo de texto com instrução clara para cópia manual (`Ctrl+C`).
- **Nenhum Meio de Apoio Configurado**: O rodapé e a página pública não devem quebrar; a página deve exibir texto explicativo sobre o projeto ser aberto e voluntário, sem exibir blocos vazios ou botões sem ação.
- **Telas Estreitas e Dispositivos Móveis**: A imagem do QR Code deve adaptar-se responsivamente sem estourar a largura da tela (max-width de 100%), garantindo que os botões de ação possuam alvos de toque mínimos de 44x44px.
- **Navegação Offline ou Perda Temporária de Rede**: A página deve permanecer acessível a partir do cache da aplicação com os dados já carregados, sem travar o leitor.
- **Acessibilidade para Leitores de Tela**: Todos os dados do PIX e links externos devem conter rótulos semânticos (`aria-label`) descritivos e avisos audíveis para a ação de copiar chave.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE disponibilizar uma página dedicada e pública acessível pela rota canônica `/apoie`.
- **FR-002**: A página de apoio DEVE apresentar texto institucional informando que o Leitorum é um projeto gratuito, sem qualquer exigência de pagamento ou restrição de funcionalidades para usuários não contribuintes.
- **FR-003**: O sistema DEVE exibir de forma clara os objetivos e a destinação das contribuições voluntárias (custos operacionais de hospedagem, infraestrutura e desenvolvimento do ecossistema).
- **FR-004**: O sistema DEVE permitir a configuração e exibição de dados de chave PIX, incluindo chave textual, nome do titular e imagem de QR Code para leitura rápida.
- **FR-005**: A interface DEVE fornecer um botão de cópia de chave PIX de um clique, com feedback visual transitório de sucesso e mecanismo de fallback para seleção textual caso a API de clipboard do navegador falhe.
- **FR-006**: O sistema DEVE permitir a configuração opcional de um link de pagamento alternativo externo (Google Pay ou similar) que, se configurado, será exibido como um botão seguro que abre em nova aba (`rel="noopener noreferrer"`).
- **FR-007**: A aplicação NÃO DEVE realizar processamento financeiro próprio nem armazenar números de cartão de crédito, senhas bancárias ou dados cadastrais financeiros de transações no banco de dados local.
- **FR-008**: O sistema DEVE gerenciar de forma independente os estados dos meios de pagamento:
  - PIX ativo / inativo;
  - Meio alternativo (Google Pay) ativo / inativo.
- **FR-009**: O mecanismo de configuração dos dados de apoio DEVE ser gerenciado de forma híbrida pelo administrador do sistema: através de uma seção dedicada no painel de administração (`/admin`) com persistência em banco de dados, mantendo fallback automático para variáveis de ambiente (`.env`) caso nenhum registro customizado esteja cadastrado no banco.
- **FR-010**: A interface da aplicação NÃO DEVE incluir abas ou botões destacados de doação no menu principal superior ou na barra de navegação lateral.
- **FR-011**: O acesso à funcionalidade DEVE ser oferecido exclusivamente através de link sutil e discreto no rodapé das páginas da aplicação e na página Sobre.
- **FR-012**: Se nenhum meio de contribuição financeira estiver configurado pelo administrador, a página `/apoie` e o link no rodapé DEVEM permanecer ativos e visíveis, exibindo uma mensagem institucional neutra sobre a filosofia de software livre e gratuito do Leitorum e sugerindo formas comunitárias de apoio (como compartilhamento de leituras, feedback e colaboração no repositório), sem apresentar blocos vazios ou dados bancários incompletos.
- **FR-013**: Toda a interface da página e seus elementos interativos DEVEM obedecer à regra estrita de ausência total de emojis no código e na interface visual.
- **FR-014**: Todos os elementos interativos (botões de cópia e links externos) DEVEM garantir alvos táteis mínimos de 44x44px e suporte pleno à navegação por teclado (foco visível e ordem lógica).

---

### Key Entities *(include if feature involves data)*

- **SupportSettings (Configurações de Apoio)**: Representa os parâmetros vigentes para a exibição de doações, incluindo:
  - `pix_enabled`: booleano indicando se o PIX está ativo;
  - `pix_key`: chave PIX textual pública (e-mail, chave aleatória ou CPF/CNPJ);
  - `pix_recipient_name`: nome do titular/beneficiário cadastrado;
  - `pix_qr_code_url`: endereço relativo ou base64 do QR Code para leitura óptica;
  - `alternative_enabled`: booleano indicando se o meio alternativo está ativo;
  - `alternative_label`: rótulo público do meio (ex.: "Google Pay" ou "Financiamento Coletivo");
  - `alternative_url`: endereço URL externo para pagamento.
- **SupportPublicInfo**: Visualização pública e sanitizada das opções disponíveis, exposta para o frontend sem dados de auditoria interna.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: O usuário consegue visualizar os dados de contribuição e copiar a chave PIX em menos de 5 segundos após entrar na página de apoio.
- **SC-002**: 100% das páginas principais da aplicação contêm o acesso ao apoio estritamente restrito ao rodapé, com zero avisos intrusivos, pop-ups ou botões flutuantes de solicitação.
- **SC-003**: A alternância de estado de ativação de qualquer meio de apoio (ativo para inativo e vice-versa) reflete-se imediatamente na visualização pública sem exigir alterações no código da aplicação.
- **SC-004**: A página de apoio atinge 100% de conformidade com alvos de toque mínimos de 44px e conformidade WCAG AA de contraste em todos os 10 temas visuais do Leitorum.

---

## Assumptions

- O Leitorum continuará sendo um sistema pessoal e comunitário 100% livre e de código aberto; a contribuição é puramente facultativa para cobrir custos de manutenção.
- A geração da imagem do QR Code para o PIX pode ser provida como arquivo de imagem estático configurado pelo administrador ou gerada localmente a partir da chave PIX padrão BR Code.
- A aplicação não emite recibos fiscais automáticos ou certificados de doação, pois não realiza a intermediação bancária.
- A página de apoio deve ser acessível tanto para usuários autenticados quanto para visitantes anônimos se o acesso público à aplicação estiver habilitado.
