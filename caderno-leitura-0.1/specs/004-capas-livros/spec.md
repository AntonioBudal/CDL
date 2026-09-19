# Feature Specification: Capas de Livros por Upload e URL

**Feature Branch**: `004-capas-livros`  
**Created**: 2026-09-18  
**Status**: Ready for Planning  
**Input**: User description: "T03 — Capas por upload e URL: Adicionar upload pelo PC/celular e importação de uma URL direta de imagem. Armazenar capas em diretório persistente (backend/data/covers), servir por rota controlada e guardar referência no banco. Validar tamanho, formato e dimensões; proteger contra SSRF em URLs externas; exibir fallback amigável quando não houver capa."

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Upload e Visualização de Capa Local (Priority: P1) 🎯 MVP

Como leitor que organiza seu acervo pessoal no computador ou celular, desejo selecionar um arquivo de imagem do meu dispositivo para servir como capa de um livro, para que minha estante virtual fique visualmente reconhecível e atraente.

**Why this priority**: O upload direto de imagem local entrega imediatamente o valor essencial da funcionalidade de capas sem depender de rede externa, resolvendo a necessidade de personalização visual dos livros.

**Independent Test**: Pode ser testado abrindo o modal de edição de um livro, selecionando um arquivo de imagem (JPEG, PNG ou WebP) válido do disco local, salvando a alteração e verificando que a miniatura da capa passa a ser exibida no cartão do livro na página inicial e no cabeçalho da página de detalhes do livro.

**Acceptance Scenarios**:

1. **Given** um livro sem capa cadastrado no acervo, **When** o usuário abre a edição do livro, escolhe um arquivo de imagem local suportado (JPEG, PNG ou WebP) e salva, **Then** o arquivo é armazenado no servidor, a capa é associada ao livro e passa a ser exibida tanto na lista de livros quanto no detalhe do livro.
2. **Given** um livro sem capa no acervo, **When** o usuário visualiza o cartão do livro na estante ou a página de leitura, **Then** o sistema renderiza um marcador/placeholder tipográfico legível e elegante com o título da obra, sem quebras de layout.
3. **Given** uma tentativa de upload de um arquivo com formato não permitido (por exemplo, PDF, executável ou SVG com scripts) ou corrompido, **When** o formulário é enviado, **Then** o sistema rejeita o upload com mensagem clara de erro e não altera o livro.

---

### User Story 2 - Importação de Capa por URL Externa Segura (Priority: P2)

Como leitor que encontra referências de livros na internet, desejo informar a URL direta de uma imagem para ser utilizada como capa do livro, sem precisar primeiro baixar a imagem manualmente para meu dispositivo.

**Why this priority**: Permite agilidade ao cadastrar livros encontrados online, especialmente ao utilizar dispositivos móveis onde baixar e reenviar arquivos pode ser incômodo.

**Independent Test**: Pode ser testado informando uma URL direta e pública de imagem válida no campo de capa do livro, disparando a importação e comprovando que o servidor efetua o download seguro, armazena uma cópia local permanente no diretório de capas e associa a imagem ao livro.

**Acceptance Scenarios**:

1. **Given** um livro em edição, **When** o usuário insere uma URL direta terminada em imagem válida e confirma, **Then** o servidor valida a requisição, baixa a imagem, salva uma cópia local persistente e exibe a prévia da capa no formulário.
2. **Given** uma URL apontando para uma página HTML completa (por exemplo, página de pesquisa do Google Imagens ou link de site com texto), **When** o usuário submete a URL, **Then** o sistema informa com clareza que o endereço não corresponde a uma imagem direta e orienta o usuário.
3. **Given** uma URL inacessível, com falha de conexão, timeout ou apontando para endereços internos restritos (redes privadas locais), **When** a importação é processada, **Then** o sistema bloqueia a requisição com segurança (prevenção de SSRF), exibe mensagem amigável e preserva a capa anterior intacta.

---

### User Story 3 - Substituição e Remoção de Capas com Preservação de Integridade (Priority: P3)

Como leitor, desejo alterar a capa existente de um livro ou removê-la completamente (voltando ao marcador padrão) com segurança, garantindo que arquivos órfãos não acumulem indefinidamente e que a lixeira preserve o estado visual histórico.

**Why this priority**: Garante o ciclo de vida completo do recurso visual, mantendo a integridade do armazenamento e prevenindo inconsistências quando livros são editados ou movidos para a lixeira.

**Independent Test**: Pode ser testado substituindo a capa de um livro por outra, removendo a capa de um livro para retornar ao placeholder, e enviando/restaurando o livro da lixeira verificando que a capa permanece vinculada corretamente.

**Acceptance Scenarios**:

1. **Given** um livro que já possui capa cadastrada, **When** o usuário seleciona a opção "Remover capa", **Then** a associação de capa é desfeita e o livro volta a exibir o placeholder tipográfico padrão.
2. **Given** um livro com capa cadastrada, **When** o usuário faz o upload de uma nova imagem, **Then** a nova imagem passa a ser a capa ativa do livro.
3. **Given** um livro que possui capa ativa, **When** esse livro é enviado para a lixeira (soft delete) e posteriormente restaurado, **Then** a capa continua perfeitamente vinculada e visível após a restauração.
4. **Given** um livro excluído definitivamente da lixeira, **When** o expurgo permanente é concluído, **Then** o arquivo físico correspondente à capa é limpo de forma atômica se não for mais referenciado.

---

### Edge Cases

- **Dimensões extremas ou arquivos pesados**: Imagens muito compridas ou excessivamente pesadas não devem deformar os cartões da estante nem travar a renderização no navegador móvel.
- **Falha de rede durante o download por URL**: Em caso de timeout ou queda de conexão no momento em que o servidor tenta obter a imagem externa, a transação deve ser abortada sem gravar registros parciais nem alterar a capa atual.
- **Caracteres perigosos no nome de arquivo**: O nome original do arquivo de upload deve ser sanitizado ou substituído por identificador seguro no servidor para impedir ataques de travessia de diretório (*path traversal*).
- **Destinos de rede locais e privados**: O servidor deve rejeitar qualquer URL externa que resolva para `localhost`, `127.0.0.1`, endereços de broadcast ou faixas de IP privadas (RFC 1918), prevenindo varreduras internas na rede privada do usuário.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE permitir associar uma imagem de capa a cada livro através de um campo opcional de capa no modelo de dados do livro.
- **FR-002**: O sistema DEVE armazenar os arquivos de imagem de capas em um diretório persistente local do servidor dedicado (`backend/data/covers`), fora dos diretórios de build do frontend, garantindo que atualizações de interface não apaguem as capas.
- **FR-003**: O sistema DEVE servir os arquivos de capa através de uma rota de leitura controlada e segura, utilizando nomes de arquivo higienizados gerados pelo servidor.
- **FR-004**: O sistema DEVE aceitar upload direto de arquivos nos formatos rasterizados comuns: JPEG/JPG, PNG, WebP, GIF, BMP e TIFF, validando a integridade real da imagem e não apenas a extensão informada no arquivo.
- **FR-005**: O sistema DEVE limitar o tamanho de arquivos de capa a um teto máximo de 5 MB tanto no upload de arquivos locais quanto no download via URL externa.
- **FR-006**: O sistema DEVE redimensionar e otimizar as imagens no servidor para uma largura máxima padronizada de 800px (em formato WebP otimizado), garantindo carregamento ultrarrápido em redes locais e dispositivos móveis, sem consumir armazenamento desnecessário.
- **FR-007**: O sistema DEVE permitir informar uma URL direta da internet para download e armazenamento de cópia local da imagem pelo servidor.
- **FR-008**: Ao processar uma URL externa, o sistema DEVE validar protocolo (somente HTTP/HTTPS), aplicar timeout estrito de conexão, verificar o cabeçalho `Content-Type` de imagem e bloquear conexões para endereços de loopback e redes privadas locais (proteção contra SSRF).
- **FR-009**: O sistema DEVE permitir ao leitor remover a capa de um livro, restaurando o marcador visual padrão sem capa.
- **FR-010**: Ao substituir ou remover a capa de um livro, o sistema DEVE reter o arquivo físico correspondente enquanto o livro existir (mesmo na lixeira) para permitir restaurações visuais perfeitas, expurgando arquivos de capa órfãos apenas durante a exclusão definitiva do livro ou nas rotinas de purga/esvaziamento da lixeira.
- **FR-011**: Caso uma tentativa de upload ou importação por URL falhe, o sistema DEVE preservar a capa anterior inalterada e exibir um aviso inteligível no formulário de edição.
- **FR-012**: O sistema DEVE exibir um marcador visual (placeholder) padronizado, acessível e responsivo para qualquer livro que não possua capa cadastrada.
- **FR-013**: Os backups automáticos e sob demanda do sistema DEVEM incluir o catálogo de capas ou garantir consistência referencial dos arquivos com o banco de dados.

---

### Key Entities *(include if feature involves data)*

- **Capa do Livro (Cover)**: Representa o arquivo de imagem associado à obra. Identificada por caminho ou nome de arquivo seguro gravado no livro, referenciando o arquivo físico armazenado em `backend/data/covers/`.
- **Livro (Book)**: Entidade do acervo enriquecida com o campo opcional de identificação de sua capa (`cover_image`).

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: O leitor consegue enviar uma imagem de capa a partir do computador ou smartphone e visualizá-la no livro em menos de 3 segundos em rede local.
- **SC-002**: A importação de capa por URL direta válida é concluída e exibida no leitor em menos de 5 segundos para imagens de até 2 MB.
- **SC-003**: 100% das tentativas de upload com arquivos inválidos, corrompidos ou não-imagem são interceptadas com mensagem descritiva, sem corrupção de dados.
- **SC-004**: 100% das requisições a URLs de imagem que apontem para endereços de rede privada/interna são sumariamente bloqueadas.
- **SC-005**: A estante de livros mantém alinhamento visual estável e fluido (sem quebra de layout) em telas de PC e smartphones, tanto para livros com capa quanto para livros com placeholder.

---

## Assumptions

- O servidor possui permissão de escrita no diretório de dados local (`backend/data/covers`).
- Dispositivos clientes conectados na rede local ou Tailscale conseguem carregar as imagens através da rota servida pelo FastAPI.
- A biblioteca padrão do Python e dependências do ambiente são suficientes para validação e manipulação de arquivos de imagem e requisições HTTP seguras.
