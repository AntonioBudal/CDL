# Feature Specification: F0.6.5 — Histórico Automático de Versões de Estudo

**Feature Branch**: `044-historico-automatico`  
**Created**: 2026-09-28  
**Status**: Draft  
**Input**: User description: "F0.6.5 — Histórico Automático"

---

## Clarifications

### Session 2026-09-28
- Q: Qual a regra e intervalo ideal para agrupar micro-salvamentos consecutivos da mesma sessão? (FR-008) → A: Janela de agrupamento de 5 minutos. Salvamentos manuais consecutivos feitos pelo mesmo autor em um intervalo de até 5 minutos atualizam o snapshot da versão mais recente; um novo registro independente é criado apenas após 5 minutos de inatividade ou na alternância de autor.
- Q: O histórico deve incluir apenas as seções textuais estruturadas ou também o estado dos destaques, anotações marginais e perguntas da Leitura Ativa? (FR-009) → A: Snapshot integral. Cada versão arquiva o título, todas as 4 seções textuais estruturadas e a coleção completa de destaques, anotações e perguntas de Leitura Ativa vinculadas naquele momento.
- Q: A restauração deve aplicar imediatamente o conteúdo no banco gerando uma nova versão, ou deve carregar o texto no editor para revisão do usuário antes de salvar? (FR-010) → A: Aplicação direta com diálogo de confirmação. Após confirmação explícita no modal, o sistema cria automaticamente um snapshot do estado presente, aplica o conteúdo histórico como o estado ativo do estudo e atualiza a interface com notificação de sucesso.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Registro Automático e Consulta da Linha do Tempo (Priority: P1) [MVP]

Como autor ou pesquisador revisando e aprofundando meus fichamentos ao longo de semanas ou meses, quero que o sistema registre automaticamente versões do meu estudo a cada edição salva, para que eu possa consultar o histórico completo de evolução do documento sem precisar me preocupar em criar backups manuais antes de reescrever seções.

**Why this priority**: É a fundação indispensável da promessa de segurança editorial ("altere seus estudos sem medo de destruir uma versão anterior"). Sem o registro confiável de versões e sua listagem, nenhuma outra capacidade de comparação ou restauração é possível.

**Independent Test**: Editar e salvar um estudo com alterações no título e em duas seções; abrir a aba ou painel "Histórico de Versões"; verificar que a versão anterior foi catalogada com data, hora, autor e resumo de alterações ou tamanho do documento.

**Acceptance Scenarios**:
1. **Given** um estudo existente aberto para leitura ou edição, **When** o usuário acessa o painel de histórico de versões, **Then** o sistema exibe uma linha do tempo cronológica decrescente com as versões registradas, indicando a versão atual e versões passadas.
2. **Given** um estudo sendo editado pelo usuário, **When** uma alteração de conteúdo é salva com sucesso, **Then** o sistema arquiva automaticamente um snapshot imutável do estado anterior sem exigir ação prévia de "Criar versão".
3. **Given** um estudo sem edições recentes ou com salvamento sem alterações reais de conteúdo, **When** o salvamento ocorre, **Then** o sistema não gera versões duplicadas vazias no histórico.

---

### User Story 2 - Visualização Comparativa e Diff entre Versões (Priority: P1)

Como estudante ou pesquisador analisando o progresso de um fichamento, quero visualizar o conteúdo de qualquer versão anterior e comparar as diferenças (adições, remoções e modificações) em relação à versão atual ou à versão imediatamente anterior, para que eu entenda com exatidão o que mudou no texto antes de decidir recuperar trechos.

**Why this priority**: A visualização de histórico só se torna útil na tomada de decisão se o usuário puder inspecionar o conteúdo passado e constatar visualmente onde o texto divergiu, em vez de depender de cópias cegas.

**Independent Test**: Selecionar uma versão anterior na linha do tempo; alternar para o modo de comparação (diff); verificar que trechos adicionados aparecem com destaque visual de inserção e trechos removidos aparecem com tachado ou destaque de exclusão por seção do estudo.

**Acceptance Scenarios**:
1. **Given** a linha do tempo de versões de um estudo, **When** o usuário clica sobre uma versão passada, **Then** o sistema exibe a visualização em modo de leitura protegida (somente leitura) daquele estado histórico.
2. **Given** uma versão passada selecionada, **When** o usuário aciona a visualização comparativa (diff), **Then** a interface apresenta lado a lado ou em modo unificado as diferenças textuais de cada seção em relação à versão atual.
3. **Given** a visualização comparativa ativa, **When** uma seção não sofreu nenhuma alteração entre as duas versões, **Then** a interface indica claramente que a seção permaneceu idêntica, recolhendo-a ou identificando a ausência de mudanças.

---

### User Story 3 - Restauração Segura de Versão Anterior (Priority: P1)

Como usuário que reescreveu um fichamento e concluiu que a estrutura anterior era superior ou que perdeu anotações críticas, quero restaurar uma versão prévia de forma segura com um clique, com garantia de que a versão vigente antes da restauração também será preservada no histórico.

**Why this priority**: É a conclusão do ciclo de valor da funcionalidade: se o usuário cometeu um engano ou deseja retroceder, a recuperação deve ser simples, segura e à prova de perda de dados.

**Independent Test**: Selecionar uma versão de 3 dias atrás; clicar em "Restaurar versão"; confirmar a solicitação no diálogo de confirmação; constatar que o estudo agora reflete os dados da versão restaurada (incluindo texto e destaques) e que o histórico ganhou uma nova entrada registrando a restauração.

**Acceptance Scenarios**:
1. **Given** a inspeção de uma versão anterior, **When** o usuário clica no botão "Restaurar esta versão", **Then** o sistema exibe um diálogo de confirmação informando que o estado atual será salvo antes de aplicar o conteúdo restaurado.
2. **Given** a confirmação da restauração pelo usuário, **When** o processo é concluído, **Then** o estudo é atualizado imediatamente no banco de dados com os dados históricos (texto e anotações/destaques) e uma nova versão de histórico é criada marcando a restauração, preservando a rastreabilidade total.
3. **Given** um usuário com permissão apenas de leitura em um estudo compartilhado, **When** visualiza o histórico, **Then** a opção de restaurar versão permanece desativada e inacessível.

---

### User Story 4 - Agrupamento e Retenção Inteligente de Histórico (Priority: P2)

Como escritor que salva edições com frequência durante uma sessão de estudo, quero que o sistema evite poluir o histórico com dezenas de micro-versões causadas por correções ortográficas seguidas, agrupando alterações contíguas dentro de uma janela de 5 minutos.

**Why this priority**: Evita sobrecarga visual na linha do tempo e consumo desnecessário de armazenamento, garantindo que o histórico reflita marcos de trabalho significativos e fáceis de navegar.

**Independent Test**: Realizar 5 salvamentos manuais consecutivos de pequenas correções em um intervalo de 3 minutos; verificar que a linha do tempo consolida as edições na versão recente do bloco de 5 minutos, e que um novo salvamento após 6 minutos gera um novo registro.

**Acceptance Scenarios**:
1. **Given** uma sequência de edições salvas em curto intervalo de tempo pelo mesmo autor, **When** o intervalo entre salvamentos é inferior a 5 minutos, **Then** o sistema atualiza o snapshot da versão mais recente em vez de criar múltiplos registros redundantes na linha do tempo.
2. **Given** um intervalo superior a 5 minutos ou uma troca de autor de edição, **When** um novo salvamento ocorre, **Then** um novo registro de versão independente é criado.

---

### Edge Cases

- **Estudo volumoso ou com muitas versões acumuladas**: O carregamento da linha do tempo deve ser paginado ou virtualizado, garantindo que estudos com dezenas de versões históricas não travem a interface.
- **Restauração concorrente**: Se dois usuários ou duas sessões tentarem restaurar versões conflitantes simultaneamente, o sistema deve aplicar controle de concorrência e alertar sobre o conflito sem sobrescrita silenciosa.
- **Exclusão de estudo**: Ao mover um estudo para a lixeira ou excluí-lo definitivamente, suas versões históricas associadas devem acompanhar o ciclo de vida da entidade pai de forma limpa.
- **Estudos importados ou antigos sem histórico prévio**: Para estudos criados antes da ativação do histórico automático, o sistema deve assumir o estado atual como "Versão inicial" assim que a primeira edição for detectada.
- **Conexão instável ou falha no salvamento**: Caso a gravação da versão falhe, a integridade do estudo principal nunca pode ser corrompida.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE capturar e arquivar automaticamente o snapshot do estudo ao persistir edições que alterem o título ou qualquer uma das seções textuais (resumo, argumentos, citações, reflexões).
- **FR-002**: O sistema DEVE registrar em cada versão histórica a data e hora do registro, o identificador do autor da alteração, o número sequencial da versão e um indicador do tamanho ou volume modificado.
- **FR-003**: O sistema DEVE disponibilizar uma interface dedicada de linha do tempo de versões integrada ao contexto do estudo, acessível tanto no modo de leitura quanto no modo de edição.
- **FR-004**: O usuário DEVE ser capaz de alternar entre as versões listadas para pré-visualizar o conteúdo integral do estudo naquele momento histórico em modo protegido (somente leitura).
- **FR-005**: O sistema DEVE fornecer visualização comparativa (diff visual) destacando acréscimos e supressões de texto entre a versão selecionada e o estado atual (ou entre duas versões selecionadas).
- **FR-006**: O usuário DEVE poder acionar a restauração de qualquer versão histórica válida mediante confirmação explícita.
- **FR-007**: A operação de restauração DEVE criar um novo registro no histórico antes de sobrescrever o estudo ativo, impedindo perda irreversível de trabalho.
- **FR-008**: O sistema DEVE aplicar uma janela temporal de agrupamento (coalescência) de 5 minutos: salvamentos manuais consecutivos realizados pelo mesmo autor dentro de um intervalo de até 5 minutos atualizam o snapshot da versão mais recente, enquanto um novo registro de versão independente só é criado após 5 minutos de inatividade ou na alternância de autor.
- **FR-009**: O snapshot de cada versão DEVE capturar o estado integral do estudo, englobando o título, todas as quatro seções textuais (resumo, argumentos, citações, reflexões) e o conjunto correspondente de destaques (grifos), notas marginais e perguntas ativas da Leitura Ativa vinculadas ao estudo naquele momento.
- **FR-010**: O fluxo de restauração de versão DEVE operar por aplicação direta no banco com diálogo prévio de confirmação explícita: ao confirmar a restauração, o sistema arquiva automaticamente um snapshot do estado presente, aplica o conteúdo histórico como o estado ativo do estudo e recarrega a visualização com confirmação de sucesso.
- **FR-011**: O sistema NÃO DEVE criar novas versões históricas se o estudo for salvo sem nenhuma modificação real em relação à versão mais recente registrada.
- **FR-012**: O sistema DEVE respeitar as permissões de acesso: usuários com permissão de visualização podem apenas consultar o histórico; apenas usuários com permissão de edição podem executar restaurações.
- **FR-013**: A interface de histórico NÃO DEVE exibir emojis em seus botões, títulos, badges ou estados.
- **FR-014**: O sistema DEVE garantir que a consulta e exibição de histórico preservem a privacidade estrita dos dados, sem envio ou exposição externa do conteúdo das versões.
- **FR-015**: A interface comparativa DEVE ser acessível por teclado, com contraste adequado e responsiva para telas de computadores e dispositivos móveis.

---

### Key Entities *(include if feature involves data)*

- **Estudo (Study)**: Entidade principal do fichamento contendo título, resumo, argumentos, citações, reflexões, metadados e carimbos de data/hora.
- **Versão de Estudo (StudyVersion)**: Registro imutável de snapshot representando o estado completo do estudo em um momento específico, vinculado ao estudo de origem, contendo:
  - Número de versão sequencial.
  - Carimbo de data/hora de criação e última atualização do lote (quando dentro da janela de 5 minutos).
  - Identificador do autor da versão.
  - Título e conteúdo textual de todas as seções (resumo, argumentos, citações, reflexões).
  - Snapshot completo das marcações de Leitura Ativa (destaques, cores, anotações e perguntas associadas).
  - Metadados de contexto (ex.: se originado de edição normal ou de restauração).
- **Registro de Comparação / Diff**: Estrutura efêmera de exibição que calcula e apresenta a divergência bloco a bloco (linhas e palavras adicionadas, removidas ou inalteradas) entre dois estados do estudo.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: O usuário consegue visualizar a lista histórica de versões de um estudo em menos de 1 segundo após acionar o comando de histórico.
- **SC-002**: O cálculo e a renderização do diff comparativo entre duas versões de um estudo típico são apresentados na tela em menos de 500 milissegundos.
- **SC-003**: 100% dos salvamentos com alterações reais de conteúdo geram ou atualizam adequadamente o registro de versão sem falhas de persistência.
- **SC-004**: A restauração de qualquer versão histórica é concluída em um clique com confirmação, sem perda de qualquer dado prévio da versão ativa.
- **SC-005**: 100% dos testes automatizados de backend e frontend passam sem regressão de cobertura ou impacto no banco de dados ativo.
- **SC-006**: A interface de histórico e comparação opera perfeitamente em telas com larguras a partir de 320px (mobile) até resoluções ultrawide em desktop.

---

## Assumptions

- O usuário já possui autenticação e controle de acesso operantes conforme o modelo multiusuário do sistema.
- A aplicação continuará operando localmente com SQLite em modo WAL, garantindo transações atômicas ao registrar versões.
- A granularidade principal de versionamento é no nível do Estudo individual (cada estudo possui sua própria linha do tempo de versões independente).
- O diff textual será baseado em comparação de texto em nível de blocos e linhas legíveis, garantindo clareza sem poluição visual por diferenças invisíveis de quebra de linha.
- As versões históricas são protegidas contra alteração (imutáveis); uma versão passada nunca pode ser editada diretamente, apenas visualizada ou restaurada como base para um novo estado presente.
- O agrupamento de 5 minutos aplica-se exclusivamente a edições do mesmo autor sobre o mesmo estudo.
