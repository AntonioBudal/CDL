# Feature Specification: Proteção do Acervo e Snapshot Consistente Pré-Atualização

**Feature Branch**: `001-snapshot-protecao-acervo`

**Created**: 2026-09-17

**Status**: Ready for Planning

**Input**: User description: "Delimitar a primeira entrega da versão 0.3 (vinculada a T09 e T10) em um snapshot consistente verificável, identificação correta da base ativa e proteção do fluxo de atualização sem perda de dados."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Backup Consistente Automático Antes de Atualizações (Priority: P1)

Como leitor e estudante que possui um acervo pessoal de livros, anotações e estudos, quero que o sistema crie automaticamente uma cópia de segurança consistente e verificada do meu acervo antes de executar qualquer atualização ou migração de banco, para que meus dados nunca sejam corrompidos ou perdidos em caso de falha no processo de atualização.

**Why this priority**: A proteção do acervo do usuário é o princípio mais crítico do projeto (Constituição, Artigo I e V). Sem essa garantia, nenhuma migração subsequente da versão 0.3 pode ser executada em segurança.

**Independent Test**: Pode ser testado de forma isolada executando um comando de migração/atualização simulada em um acervo com dados sintéticos: o sistema deve obrigatoriamente produzir um arquivo de snapshot íntegro antes de qualquer mutação e cancelar o processo caso a cópia não possa ser gerada ou validada.

**Acceptance Scenarios**:

1. **Given** um acervo ativo com livros, capítulos e estudos cadastrados, **When** uma atualização ou rotina de manutenção for solicitada, **Then** o sistema gera um snapshot atômico e isolado do banco antes de aplicar qualquer alteração de esquema.
2. **Given** um snapshot gerado durante o fluxo de atualização, **When** a cópia é finalizada, **Then** o sistema valida sua integridade estrutural e referencial antes de liberar o prosseguimento da atualização.
3. **Given** um cenário de erro durante a criação do snapshot (ex.: falha de permissão, disco cheio ou banco ocupado), **When** a falha é detectada, **Then** a rotina de atualização é imediatamente abortada e o acervo ativo permanece 100% inalterado.

---

### User Story 2 - Resolução Determinística da Base Ativa (Priority: P2)

Como usuário que inicia o Caderno de Leitura por atalhos, scripts ou terminais em pastas variadas, quero que o sistema identifique de forma unificada e inequívoca a localização da base de dados ativa, para que nenhuma operação de leitura, escrita ou manutenção utilize uma base incorreta ou crie arquivos duplicados silenciosamente.

**Why this priority**: Garante que servidores, ferramentas de linha de comando, scripts e rotinas de manutenção operem exatamente sobre o mesmo arquivo de dados, eliminando inconsistências entre chamadas locais.

**Independent Test**: Pode ser testado invocando rotinas de inicialização e de verificação a partir de diferentes diretórios de trabalho (working directories) e comprovando que ambas convergem para o mesmo arquivo absoluto de banco.

**Acceptance Scenarios**:

1. **Given** que o comando de inicialização ou verificação é executado de diretórios de trabalho diferentes, **When** a localização do banco é requisitada, **Then** o sistema resolve exatamente o mesmo caminho canônico absoluto do banco ativo.
2. **Given** a variável de ambiente `CADERNO_DATABASE_PATH` configurada pelo usuário com um caminho absoluto válido, **When** a aplicação ou rotinas de manutenção são executadas, **Then** o caminho customizado prevalece com precedência sobre o padrão.
3. **Given** um caminho relativo ambíguo fornecido em `CADERNO_DATABASE_PATH`, **When** a configuração é carregada, **Then** o sistema recusa a inicialização com diagnóstico explícito, exigindo caminho absoluto.

---

### User Story 3 - Inspeção e Diagnóstico de Integridade de Snapshots (Priority: P3)

Como usuário que deseja verificar o estado das minhas cópias de segurança, quero poder inspecionar qualquer snapshot gerado para conferir data/hora, versão do esquema e quantidades de registros cadastrados, sem expor o texto privado das minhas anotações na tela.

**Why this priority**: Oferece transparência e tranquilidade ao usuário sobre a eficácia dos backups realizados, respeitando rigorosamente a privacidade das suas reflexões pessoais.

**Independent Test**: Pode ser testado fornecendo um snapshot válido a uma rotina de verificação: o relatório deve conter metadados e contagens quantitativas sem emitir nenhuma linha de texto de estudos ou anotações.

**Acceptance Scenarios**:

1. **Given** um snapshot válido existente, **When** o usuário solicita sua verificação, **Then** o sistema retorna status de integridade positivo, data de criação, versão da estrutura e contagem agregada de livros, capítulos e estudos.
2. **Given** um arquivo de snapshot corrompido, incompleto ou ilegível, **When** a verificação é realizada, **Then** o sistema indica claramente que o backup é inválido, mantendo o acervo ativo totalmente protegido.

---

### Edge Cases

- **Operação de escrita concorrente durante a geração do snapshot:** O mecanismo de cópia deve capturar um estado consistente em repouso sem travar indefinidamente requisições legítimas nem gerar snapshots com dados pela metade.
- **Caminhos com caracteres especiais no Windows:** O armazenamento e a resolução de caminhos devem suportar acentuação, espaços e caracteres especiais comuns em nomes de pastas do Windows.
- **Interrupção brusca de processo:** Se o processo for encerrado (ex.: `Ctrl+C` ou falta de energia) durante a criação do snapshot, os arquivos temporários incompletos devem ser descartados ou identificados como inválidos, nunca substituindo backups anteriores.
- **Ausência ou vazio no banco de dados:** Caso o arquivo do banco ativo não exista ou possua 0 bytes, a rotina não deve gerar um snapshot enganoso, mas sim reportar a inexistência da base.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE criar um snapshot atômico e consistente do banco de dados antes de permitir a execução de qualquer migração ou alteração de esquema estrutural.
- **FR-002**: O sistema DEVE validar a integridade estrutural e referencial do snapshot imediatamente após a sua criação, antes de liberar qualquer etapa subsequente.
- **FR-003**: O sistema DEVE abortar qualquer procedimento de atualização caso o snapshot não possa ser gerado ou falhe na verificação de integridade, assegurando que o acervo ativo permaneça intocado.
- **FR-004**: O sistema DEVE centralizar a resolução do caminho do banco ativo em um contrato único compartilhado entre o servidor web e as rotinas de verificação/manutenção.
- **FR-005**: O sistema DEVE validar rigorosamente que `CADERNO_DATABASE_PATH` seja um caminho absoluto, rejeitando caminhos relativos para evitar dependência do diretório atual de execução.
- **FR-006**: O sistema DEVE armazenar os snapshots automáticos pré-migração no subdiretório dedicado `backend/data/backups/` (ou relativo ao diretório configurado da base ativa), adotando a nomenclatura com carimbo de data/hora UTC `caderno-pre-migracao-YYYYMMDD-HHMMSS.db`.
- **FR-007**: O sistema DEVE aplicar política de rotação automática mantendo os 5 snapshots pré-migração mais recentes, removendo com segurança os excedentes mais antigos e sem jamais remover backups manuais do usuário.
- **FR-008**: O sistema DEVE permitir a inspeção não destrutiva de snapshots, exibindo metadados técnicos (data, versão do esquema, contagem quantitativa de livros, capítulos e estudos) sem exibir anotações ou textos do acervo.
- **FR-009**: O sistema DEVE assegurar que chaves primárias, relacionamentos, texto original importado (`source_response`) e datas permaneçam integralmente preservados.
- **FR-010**: O sistema DEVE garantir a limpeza automática de arquivos temporários parciais em casos de interrupção ou erro.

### Key Entities *(include if feature involves data)*

- **Acervo Ativo**: O banco SQLite principal do usuário contendo suas tabelas relacionais (`books`, `chapters`, `studies`).
- **Snapshot Pré-Migração**: Arquivo isolado e autocontido contendo a cópia atômica consistente do Acervo Ativo no instante anterior a uma mutação.
- **Relatório de Inspeção de Snapshot**: Estrutura de dados contendo data/hora de geração, validação de integridade estrutural/referencial, versão do esquema e quantitativos agregados de itens.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% das tentativas de migração são precedidas por um snapshot validado; em 0% dos cenários de falha na criação do snapshot a base ativa é modificada.
- **SC-002**: Em caso de simulação de erro durante a migração, o acervo ativo mantém 100% dos seus registros, identificadores e integridade original.
- **SC-003**: A geração e verificação do snapshot em um acervo local é concluída em menos de 3 segundos em condições normais de disco.
- **SC-004**: A inspeção de um snapshot reporta a contagem de registros com 100% de exatidão sem nunca emitir conteúdo textual confidencial nos terminais ou relatórios.
- **SC-005**: O sistema opera sem falhas em caminhos de arquivos contendo espaços e acentos no ambiente Windows.

## Assumptions

- O ambiente de execução é Windows local monousuário, utilizando SQLite em disco.
- A criação de snapshots utilizará a API oficial de backup online do SQLite para garantir consistência mesmo sob arquivos WAL ou conexões abertas.
- A aplicação não exporá dados privados do acervo durante verificações ou logs de diagnóstico.
- Os testes automatizados serão executados exclusivamente em pastas temporárias descartáveis (`tmp_path`), sem tocar em arquivos de produção.
