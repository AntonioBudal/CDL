# Feature Specification: Infraestrutura — Integridade, Migrações, Concorrência e Operação de Backup/Restauração (T09-T10)

**Feature Branch**: `016-infra-backup-operacao`  
**Created**: 2026-09-19  
**Status**: Ready for Planning (Clarifications Resolved)  
**Input**: User description: "Vamos terminar esse roadmap com T09-T10 (T09: Integridade, migrações e concorrência; T10: Backup, restauração e operação)"  

---

## Clarifications

### Session 2026-09-19

- **Q1 (Formato do Pacote Completo de Backup — T10)**: **Opção A — Arquivo ZIP com extensão universal `.zip`** (Ex.: `caderno-backup-YYYYMMDD-HHMMSS.zip`). O pacote é um arquivo compactado padrão contendo a cópia consistente do banco SQLite (`caderno.db`), o diretório de capas físicas (`covers/`) e o manifesto de autenticidade (`manifest.json`) com somas de verificação SHA-256 de todos os arquivos.
- **Q2 (Pontos de Acionamento da Restauração — T10)**: **Opção A — Interface Gráfica (Central de Ajustes) + Linha de Comando (CLI `maintenance.py`)**. O leitor pode fazer upload do arquivo ZIP pela tela de Ajustes do navegador com modal de confirmação assistida e validação em sandbox temporária, ou o usuário pode acionar a restauração via terminal caso o servidor esteja indisponível. Em ambos os casos, um snapshot de segurança prévio do acervo ativo é gerado obrigatoriamente antes de qualquer substituição.
- **Q3 (Experiência em Caso de Conflito Concorrente 409 — T09)**: **Opção A — Alerta com opção explícita de "Sobrescrever com minhas alterações" ou "Recarregar versão externa"**. Ao detectar conflito (HTTP 409) entre edições concorrentes (ex.: PC vs celular), o frontend preserva 100% dos dados digitados pelo usuário no formulário, exibe banner/modal explicativo de concorrência e dá autonomia para decidir se grava suas alterações forçando o salvamento ou se descarta e recarrega os dados externos.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Geração de Pacote Completo de Backup com Integridade Verificável (Priority: P1) 🎯 MVP

Como leitor e mantenedor do caderno de leitura, quero baixar um pacote de backup completo e íntegro contendo meu banco de dados, pastas de mídias (capas) e manifesto com somas de verificação em arquivo `.zip`, para que todo o meu acervo possa ser preservado sem risco de corrupção ou perda de arquivos relacionados.

**Why this priority**: É a garantia de salvaguarda definitiva do acervo. Sem um pacote completo com manifesto e dados consistentes, migrações futuras e mudanças estruturais apresentam risco de perda de dados.

**Independent Test**: Solicitar a geração do backup pela interface ou linha de comando, baixar o arquivo `.zip` gerado e verificar que ele contém a base de dados consistente, o diretório de capas anexadas e um manifesto com metadados e somas de verificação (hashes SHA-256) de cada arquivo.

**Acceptance Scenarios**:

1. **Given** um acervo com livros, capítulos, anotações e capas cadastradas, **When** o usuário solicita o backup completo, **Then** o sistema gera um arquivo compactado `.zip` contendo a base de dados consistente (extraída sem ignorar dados do WAL via SQLite Backup API), as capas físicas de livros e um arquivo `manifest.json` contendo as somas criptográficas de cada item.
2. **Given** que o banco de dados está recebendo leituras no momento do backup, **When** a rotina de cópia é executada, **Then** ela conclui de forma atômica e consistente sem interrupções nem bloqueios permanentes do aplicativo.
3. **Given** a geração do pacote, **When** o manifesto é inspecionado, **Then** constam a versão da aplicação, versão do esquema, data/hora em UTC e a lista de hashes dos arquivos contidos.

---

### User Story 2 - Restauração Segura com Validação Prévia e Proteção de Rollback (Priority: P2)

Como leitor que precisa transferir o acervo para outro computador ou recuperar um estado anterior, quero restaurar um pacote de backup com validação de integridade em área intermediária e salvaguarda do acervo atual (tanto pela Central de Ajustes quanto pela linha de comando), para que um arquivo danificado ou malicioso nunca destrua meus dados existentes.

**Why this priority**: A restauração é a contrapartida essencial do backup. Sem validação rigorosa e mecanismo de reversão (rollback), qualquer falha no envio ou extração do pacote corromperia a base do usuário.

**Independent Test**: Submeter um pacote de backup para restauração em um ambiente com dados ativos, simular uma falha de validação ou integridade e verificar que o acervo original permanece 100% intacto. Em seguida, submeter um pacote íntegro e comprovar a restauração atômica bem-sucedida.

**Acceptance Scenarios**:

1. **Given** um pacote de backup válido e integro, **When** o usuário aciona a restauração (pela Central de Ajustes ou via CLI `maintenance.py`), **Then** o sistema extrai e valida os arquivos em ambiente temporário isolado, realiza um snapshot de segurança prévio do acervo ativo e substitui atomicamente o banco e as capas, disponibilizando os dados restaurados imediatamente.
2. **Given** um arquivo compactado corrompido, com somas de verificação divergentes ou que contenha caminhos com escape de diretório (ataque de path traversal/Zip Slip), **When** a restauração é solicitada, **Then** o sistema aborta a operação com diagnóstico claro, mantém o acervo atual inalterado e expurga os arquivos temporários.
3. **Given** uma falha inesperada durante a substituição dos arquivos, **When** o sistema detecta o erro, **Then** ele executa o rollback imediato para o snapshot de segurança anterior, garantindo que o acervo nunca permaneça em estado inconsistente.

---

### User Story 3 - Concorrência Otimista e Proteção contra Sobrescrita entre Dispositivos (Priority: P3)

Como usuário que acessa o caderno simultaneamente pelo PC e pelo smartphone (via rede local ou Tailscale), quero ser alertado caso um estudo ou livro tenha sido modificado em outro dispositivo enquanto eu estava editando, com opção de forçar salvamento ou recarregar a versão mais recente, para que minhas anotações locais nunca sejam perdidas ou sobrescritas silenciosamente.

**Why this priority**: Evita perda de raciocínio e anotações pessoais decorrentes de edição simultânea em abas ou dispositivos distintos.

**Independent Test**: Abrir o formulário de edição de um estudo no celular e, em seguida, salvar uma alteração do mesmo estudo no computador. Tentar salvar no celular e verificar que o sistema recusa a gravação silenciosa, exibe alerta explicativo de conflito com opções de decisão e mantém intacto o texto digitado pelo usuário.

**Acceptance Scenarios**:

1. **Given** que um estudo foi aberto para edição no dispositivo A e alterado no dispositivo B, **When** o usuário tenta salvar as alterações a partir do dispositivo A, **Then** o sistema retorna indicação de conflito de concorrência (HTTP 409), impedindo a gravação silenciosa.
2. **Given** a ocorrência de um conflito de concorrência, **When** a interface exibe o aviso, **Then** o formulário preserva integralmente as edições feitas pelo leitor sem recarregar a tela, oferecendo botões de "Sobrescrever com minhas alterações" e "Recarregar versão externa".
3. **Given** uma edição realizada de forma linear e isolada em um dispositivo, **When** o usuário salva suas anotações, **Then** o registro é atualizado normalmente e sua marca temporal é renovada para proteger futuras edições.

---

### User Story 4 - Resiliência Operacional, Inicialização e Prevenção de Conflitos de Porta (Priority: P4)

Como usuário que opera o sistema no dia a dia, quero que o inicializador verifique automaticamente a integridade do ambiente, alerte sobre migrações pendentes e diagnostique claramente conflitos de porta ou instâncias duplicadas, para que eu tenha uma inicialização segura e sem erros crípticos de sistema.

**Why this priority**: Fecha o ciclo de robustez operacional (T10), evitando tracebacks feios do Windows e bloqueios de processo quando duas janelas forem abertas acidentalmente.

**Independent Test**: Executar `iniciar.py` enquanto uma instância do Caderno já estiver ativa na mesma porta e verificar que uma mensagem informativa amigável é exibida no terminal sem quebrar a execução.

**Acceptance Scenarios**:

1. **Given** que o servidor já está ativo na porta 8000, **When** o usuário tenta executar o inicializador em outro terminal, **Then** o sistema detecta que a porta já está ocupada e exibe um diagnóstico claro em português orientando o encerramento da outra janela ou o uso de outra porta via parâmetro `--port`.
2. **Given** uma versão da aplicação que contém migrações estruturais de banco não aplicadas, **When** o inicializador é acionado, **Then** ele alerta sobre a discrepância de versões e orienta a execução da atualização de banco com snapshot obrigatório de segurança.
3. **Given** a execução de qualquer rotina operacional, **When** são gerados logs no console ou em arquivo, **Then** os registros contêm estritamente dados operacionais e de diagnóstico, sem expor anotações pessoais, títulos de livros privados ou segredos.

---

## Edge Cases

- **Zip Slip / Path Traversal**: Pacotes de restauração que contenham arquivos com nomes como `../../windows/system32` ou caminhos absolutos devem ser sumariamente rejeitados antes de qualquer extração no disco.
- **Interrupção de Restauração**: Queda de energia ou fechamento forçado durante a fase de substituição atômica de arquivos deve deixar o sistema capaz de reverter para o snapshot prévio.
- **Banco de Origem Aberto ou com WAL Ativo**: A criação do backup deve usar a API de cópia consistente do SQLite, garantindo que dados ainda em buffer WAL sejam incluídos sem exigir o encerramento forçado do servidor.
- **Divergência de Horário (Clock Skew)**: Pequenas diferenças de milissegundos entre relógios de dispositivos locais não devem provocar falsos positivos de conflito concorrente (tolerância adequada de skew de 1 segundo).
- **Tentativa de Restauração com Pacote Incompatível**: Um backup com versão de esquema mais nova do que a versão suportada pela aplicação deve ser bloqueado com mensagem informando a necessidade de atualizar o software.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE gerar pacotes completos de backup em formato universal ZIP (`.zip`) contendo a cópia consistente do banco de dados SQLite (`caderno.db`), o diretório com as capas de livros físicas (`covers/`) e um arquivo `manifest.json` com metadados do pacote e hashes SHA-256 de todos os arquivos contidos.
- **FR-002**: O sistema DEVE utilizar a SQLite Online Backup API (`sqlite3.Connection.backup`) para gerar snapshots de dados atômicos, garantindo consistência mesmo com transações concorrentes ou modo WAL habilitado.
- **FR-003**: O sistema DEVE permitir a validação de pacotes de backup através de inspeção prévia em diretório transitório descartável, verificando a assinatura dos hashes SHA-256, a integridade física do SQLite (`PRAGMA quick_check`) e a ausência de chaves estrangeiras órfãs (`PRAGMA foreign_key_check`).
- **FR-004**: O sistema DEVE disponibilizar restauração assistida tanto na interface web (aba Sistema da Central de Ajustes) quanto via linha de comando (`python -m app.services.maintenance restaurar-backup`), criando compulsoriamente um snapshot de salvaguarda do acervo ativo antes da substituição e garantindo reversão (rollback) automática caso ocorra qualquer erro.
- **FR-005**: O sistema DEVE rejeitar qualquer arquivo de pacote que tente gravar fora do diretório de destino temporário ou que utilize caminhos relativos maliciosos (prevenção contra Zip Slip).
- **FR-006**: O sistema DEVE implementar controle de concorrência otimista em todas as operações de escrita de livros, capítulos e estudos através de verificação de marca temporal (`expected_updated_at`), retornando código HTTP 409 em caso de alteração simultânea.
- **FR-007**: Ao receber um retorno de conflito de concorrência (409), a interface gráfica DEVE preservar o conteúdo editado pelo usuário na tela e exibir um diálogo oferecendo as ações de "Sobrescrever com minhas alterações" ou "Recarregar versão externa".
- **FR-008**: O sistema DEVE disponibilizar uma interface de linha de comando (`maintenance.py`) para criar backups completos, inspecionar pacotes e executar restaurações assistidas sem depender do servidor web ativo.
- **FR-009**: O inicializador `iniciar.py` DEVE verificar previamente a disponibilidade da porta de rede especificada antes de disparar o servidor Uvicorn, apresentando um diagnóstico amigável em português e orientando o encerramento da outra janela ou escolha de outra porta.
- **FR-010**: O sistema DEVE manter centralizada a resolução de caminhos (`CADERNO_DATABASE_PATH`, pasta de capas e pasta de backups) de modo que a aplicação funcione de maneira previsível independentemente do diretório de trabalho do terminal.

---

### Key Entities

- **`BackupPackage`**: Arquivo compactado `.zip` contendo:
  - `caderno.db`: Base SQLite gerada com integridade verificada.
  - `covers/`: Pasta contendo as imagens de capas ativas vinculadas aos livros.
  - `manifest.json`: Metadados contendo versão do app, versão do schema Alembic, timestamp UTC, contagens agregadas de entidades e tabela de hashes SHA-256 dos arquivos.
- **`BackupManifest`**: Objeto estruturado com os metadados de autenticidade do pacote.
- **`ConcurrencyRecord`**: Contrato de validação de versão baseado em marcação de data/hora (`updated_at` / `expected_updated_at`) com tolerância a pequenas variações de relógio.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% dos backups gerados incluem o banco de dados consistente, o manifesto com hashes SHA-256 e o acervo de capas físicas em arquivo `.zip`.
- **SC-002**: 100% das tentativas de restauração com arquivos corrompidos, adulterados ou com nomes maliciosos (Zip Slip) são bloqueadas sem afetar o acervo ativo do usuário.
- **SC-003**: A restauração completa de um acervo com até 50 livros e centenas de estudos é validada e executada em menos de 5 segundos em condições normais de disco.
- **SC-004**: 0% de perda silenciosa de edições quando múltiplos dispositivos modificam o mesmo estudo simultaneamente.
- **SC-005**: Ao tentar abrir uma segunda instância na mesma porta, o sistema emite uma mensagem clara no terminal em menos de 1 segundo sem travar ou gerar traceback não tratado.

---

## Assumptions

- O usuário executa a aplicação localmente no Windows com privilégios adequados para criar arquivos em seu diretório de usuário.
- A sincronização entre dispositivos é feita sob demanda por rede local ou rede privada virtual (Tailscale), sem necessidade de servidor em nuvem pública.
- A restauração de acervo é uma operação administrativa de baixa frequência que pode exigir recarregar a interface do navegador.
