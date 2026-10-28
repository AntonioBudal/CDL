# Feature Specification: Organizar nas 4 Seções — Distribuição Revisável do Texto do Estudo

**Feature Branch**: `089-organizar-quatro-secoes`

**Created**: 2026-10-27

**Status**: Implementada em 2026-10-27; conferência visual (temas, 320 px, teclado, celular) pendente com o usuário

**Input**: ADR-010 do `document-intelligence/`, aceito pelo usuário em 2026-10-27, com base no EXP-023. Leitores
escrevem no caderno de forma corrida, sem os cabeçalhos `Resumo / Explicação / Conceitos / Referências` que o
parser de importação exige. Hoje, na digitalização (feature 086), o texto inteiro vai para **uma** seção. O pedido
é um botão que **sugira** a distribuição do texto entre as 4 seções do Estudo, para o leitor conferir.

---

## 1. Contexto

- **Digitalização (`/digitalizar`, feature 086):** depois da revisão, o leitor escolhe uma única seção para o
  texto lido.
- **Importação (`/importar`, feature 066):** o parser só divide o texto quando encontra cabeçalhos. O que sobra
  fica como "texto não classificado", e o leitor o manda inteiro para uma seção com um botão.
- **EXP-023:** uma pipeline em Python puro, sem IA de terceiros, sem modelo generativo e sem rede, distribui o
  texto em trechos entre as 4 seções:
  - **páginas fictícias:** Macro-F1 de 0,93 no texto limpo e 0,82 com 25 % de erro de leitura, em menos de
    10 ms por página;
  - **estudos reais do usuário:** só 3 disponíveis, com acerto de **0,50**. A qualidade em texto real **não está
    demonstrada**.
- **Decisão do ADR-010:** a função entra como **sugestão sob demanda, sempre revisável**. Nunca distribui sozinha,
  nunca reescreve o texto e não usa os estudos do usuário para se calibrar.

**Relação com os roadmaps:** feature avulsa, pedida pelo usuário, fora do Roadmap 0.9. Não altera o estado de
nenhuma feature da 0.9.

---

## Clarifications

### Decisões já tomadas pelo usuário (EXP-023 §11 e ADR-010, 2026-10-27)

- **Q: Onde vão citações e páginas dentro de uma frase?** → A: ficam na seção da frase. Referências recebe só:
  - referências bibliográficas completas;
  - citações diretas em linha ou unidade própria;
  - remissões autônomas (`cf.`, `apud`).

  Linhas `p. 42 — comentário do leitor` contam como Explicação.
- **Q: A organização usa os estudos do próprio usuário para se ajustar?** → A: não nesta fatia (desligada até
  haver medida com N suficiente).
- **Q: A organização pode agir sozinha?** → A: não. Só quando o leitor pede, e sempre como sugestão revisável.

---

## 2. User Scenarios & Testing *(mandatory)*

### User Story 1 — Organizar o texto digitalizado nas 4 seções (Priority: P1) [MVP]

Como leitor que digitalizou uma página de anotações corridas, quero pedir que o texto seja distribuído entre
Resumo, Explicação, Conceitos e Referências, para só conferir e corrigir em vez de separar tudo à mão.

**Why this priority**: É o pedido central: hoje a página inteira cai numa seção só.

**Independent Test**: Com um texto fictício de anotações sem cabeçalhos, na tela de revisão da digitalização,
tocar em "Organizar nas 4 seções" e ver 4 editores preenchidos com os trechos originais, sem nenhuma palavra
alterada, e os trechos incertos listados para conferir.

**Acceptance Scenarios**:

1. **Given** o texto revisado em `/digitalizar`, **When** o leitor toca em "Organizar nas 4 seções", **Then** a
   escolha de uma seção única dá lugar a 4 editores rotulados, preenchidos com os trechos atribuídos a cada seção,
   na ordem em que aparecem no texto.
2. **Given** a organização feita, **When** o leitor compara os editores com o texto antes de organizar, **Then**
   todo o texto está presente exatamente uma vez, sem nenhuma palavra criada, removida ou alterada.
3. **Given** trechos com atribuição incerta, **When** a organização é exibida, **Then** eles aparecem numa lista
   "Seções para conferir", com marcação acessível (texto e ícone, não só cor), cada um com a ação "Mover para…".
4. **Given** um aviso permanente na área organizada, **When** o leitor a vê, **Then** o aviso diz que a
   distribuição é automática, pode errar e deve ser conferida antes de salvar.
5. **Given** o texto com cabeçalhos escritos pelo leitor ("Resumo:", "Conceitos"), **When** organiza, **Then** o
   que está sob cada cabeçalho vai para a seção correspondente.

---

### User Story 2 — Desfazer e salvar com segurança (Priority: P1) [MVP]

Como leitor, quero voltar ao texto único se a sugestão não ajudar, e salvar o estudo com as 4 seções quando ela
ajudar, sem perder a leitura original.

**Why this priority**: Sem desfazer e sem salvar corretamente, a sugestão vira risco de perda de texto.

**Independent Test**: Organizar um texto fictício, editar um dos editores, tocar em "Voltar para texto único",
confirmar e reencontrar exatamente o texto de antes. Organizar de novo e salvar num banco temporário: o estudo tem
as 4 seções preenchidas e o registro de origem intacto.

**Acceptance Scenarios**:

1. **Given** o texto organizado e não alterado, **When** o leitor toca em "Voltar para texto único", **Then** o
   editor único volta com o texto exatamente como estava antes de organizar.
2. **Given** um dos 4 editores alterado, **When** o leitor pede para voltar, **Then** o sistema pede confirmação
   antes de descartar as alterações.
3. **Given** o texto organizado, **When** o leitor salva, **Then** o estudo é criado pelo caminho de criação já
   existente, com as 4 seções como estão nos editores, status "rascunho" e o texto lido automaticamente
   preservado como registro de origem.
4. **Given** um trecho listado em "Seções para conferir", **When** o leitor escolhe "Mover para… Conceitos",
   **Then** o trecho sai do editor atual e entra no de Conceitos, na posição que mantém a ordem original. Se o
   trecho já foi editado, a ação fica desativada e a lista indica "já editado".
5. **Given** os 4 editores vazios, **When** o leitor tenta salvar, **Then** o salvamento é impedido, como já
   acontece com qualquer estudo.

---

### User Story 3 — Organizar o texto não classificado na importação (Priority: P2)

Como leitor que cola um fichamento sem cabeçalhos no Ateliê de Importação, quero distribuir automaticamente o
"texto não classificado" entre as 4 seções, em vez de mandá-lo inteiro para uma só.

**Why this priority**: Reaproveita a mesma função num fluxo que já sofre do mesmo problema, mas a digitalização
vem primeiro.

**Independent Test**: Colar um texto fictício sem cabeçalhos, preparar a prévia e tocar em "Organizar
automaticamente": o texto não classificado é distribuído e acrescentado às seções; "Desfazer" devolve as seções e
o texto não classificado ao estado anterior.

**Acceptance Scenarios**:

1. **Given** uma prévia com texto não classificado, **When** o leitor toca em "Organizar automaticamente",
   **Then** os trechos vão para as seções sugeridas, acrescentados ao que já estava nelas, e o painel de texto não
   classificado se esvazia.
2. **Given** a organização feita na importação, **When** o leitor toca em "Desfazer organização", **Then** as 4
   seções e o texto não classificado voltam exatamente ao estado anterior.
3. **Given** uma prévia sem texto não classificado (o parser achou todos os cabeçalhos), **When** a tela é
   exibida, **Then** o botão não aparece.

---

### User Story 4 — Estados, temas e celular (Priority: P3)

Como leitor em qualquer um dos 10 temas, no computador ou no celular, quero que a área organizada siga o padrão
visual e ergonômico do Leitorum.

**Why this priority**: Padrão obrigatório do Roadmap 0.9, depois do fluxo funcionar.

**Independent Test**: Percorrer organizar → mover → voltar → salvar em 320 px e em desktop, nos temas claro,
escuro e E-Ink, só com teclado.

**Acceptance Scenarios**:

1. **Given** uma tela estreita (< 768 px), **When** o texto é organizado, **Then** os 4 editores aparecem como
   abas acessíveis, com o número de trechos para conferir indicado em cada aba.
2. **Given** qualquer tema, **When** a área organizada é exibida, **Then** ela usa só tokens semânticos, com
   contraste WCAG AA, foco visível e alvos de toque ≥ 44 × 44 px.
3. **Given** o pedido em andamento, **When** a tela espera, **Then** mostra estado de carregamento no formato dos
   4 editores, e não texto cru.

---

## 3. Edge Cases

- **Texto vazio ou só espaços:** o botão fica desativado.
- **Texto muito longo** (acima do limite definido no plano): recusado com mensagem clara, e o texto único
  permanece.
- **Tudo atribuído a uma só seção:** a organização é exibida normalmente, com os outros editores vazios e uma nota
  de que a sugestão não encontrou outras seções.
- **Texto com muito erro de leitura:** a sugestão pode errar mais. O aviso e a lista de conferência continuam, e a
  tela sugere corrigir a leitura antes de organizar.
- **Editar o texto único e organizar de novo:** cada organização parte do texto atual. "Voltar" restaura o texto
  de antes da última organização.
- **Artefato de pesos ausente ou corrompido** (verificação de integridade falha):
  - o botão não aparece ou aparece desativado, com explicação;
  - a digitalização e a importação continuam funcionando como hoje.
- **Sair da tela com os 4 editores alterados e não salvos:** a proteção de alterações não salvas existente pede
  confirmação.
- **Texto digitalizado com linhas editadas:** a posição das linhas lidas é usada só onde o texto ainda casa com a
  leitura original.

---

## 4. Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O backend DEVE oferecer uma operação de **organização** que recebe um texto e devolve:
  - a sugestão de conteúdo de cada uma das 4 seções;
  - a lista de trechos, cada um com posição no texto recebido, seção, confiança e marcação de "conferir".

  Opcionalmente, recebe também as linhas lidas na digitalização, com posição e confiança, para usar a geometria. A
  operação **não grava nada** no banco e **não lê** os estudos do usuário.
- **FR-002**: A organização DEVE ser **sem perda e sem reescrita**:
  - todo caractere não branco do texto recebido aparece em exatamente um trecho;
  - cada seção é a junção, na ordem original, dos trechos atribuídos a ela, exatamente como estão no texto.
- **FR-003**: Cabeçalhos explícitos escritos pelo leitor, reconhecidos com a mesma lista de sinônimos do parser de
  importação, DEVEM prevalecer sobre a sugestão para o texto sob eles.
- **FR-004**: A política de referências das Clarifications DEVE ser respeitada pela pipeline.
- **FR-005**: A organização DEVE ser determinística: o mesmo texto e a mesma versão do artefato dão o mesmo
  resultado. A versão e a integridade do artefato (SHA-256) DEVEM ser conferidas ao carregar e informadas na
  resposta.
- **FR-006**: Na revisão da digitalização, o leitor DEVE poder:
  - alternar entre o modo **texto único** (o atual) e o modo **organizado** (4 editores);
  - mover trechos incertos entre seções com "Mover para…";
  - voltar ao texto único, restaurando exatamente o texto de antes de organizar, com confirmação se houve edição;
  - salvar o estudo com as 4 seções pelo caminho de criação existente, com o registro de origem intacto.
- **FR-007**: A pré-visualização da digitalização (feature 086) DEVE passar a devolver a posição de cada linha
  lida. O campo é **aditivo**: o contrato da 086 continua válido para quem não usa o campo novo.
- **FR-008**: Na importação, quando houver texto não classificado, o leitor DEVE poder distribuí-lo entre as 4
  seções e desfazer a distribuição.
- **FR-009**: Enquanto houver conteúdo organizado e não salvo, DEVE haver um aviso permanente de que a
  distribuição é automática e deve ser conferida.
- **FR-010**: A função DEVE estar disponível para todos os usuários autenticados e funcionar com ou sem o motor de
  leitura instalado. Na importação, ela não depende do motor.
- **FR-011**: Se o artefato de pesos estiver ausente ou falhar na verificação de integridade, a função DEVE ficar
  indisponível com explicação, sem afetar o restante da digitalização e da importação.

### Non-Functional & Governance Restrictions

- **NR-001 (Sem migração)**: Nenhuma tabela, coluna ou migração Alembic. Usa o modelo de Estudo existente.
- **NR-002 (Sem dependência nova)**: A organização roda no backend em Python puro (biblioteca padrão), com os pesos
  num arquivo versionado. Nenhum pacote novo no `requirements.txt` e nenhum serviço externo.
- **NR-003 (Privacidade)**:
  - nenhum texto organizado aparece em logs;
  - testes e validação usam só textos fictícios;
  - a operação não lê nem grava estudos.
- **NR-004 (Licenças)**: Artefato e código sob MIT, ajustados só com dados fictícios do projeto (ADR-010). Nenhum
  corpus, modelo ou dado de licença não verificada.
- **NR-005 (Design)**: Tokens semânticos dos 10 temas, zero emojis, ícones SVG, esqueletos de carregamento, foco
  visível, alvos ≥ 44 × 44 px e hierarquia `h1 → h2 → h3` (Roadmap 0.9 e TEMAS-E-SISTEMA-VISUAL).
- **NR-006 (Testes)**: `npm test`, `pytest` e `npm run build` aprovados. Testes de backend em banco temporário, com
  `CADERNO_DATABASE_PATH` descartável. Nenhum teste toca `backend/data/caderno.db`.
- **NR-007 (Honestidade da interface)**: Nenhum texto da interface pode prometer acerto. A função é sempre
  apresentada como sugestão, porque a qualidade em texto real não foi demonstrada (ADR-010).

### Key Entities

- **Organização (transitória):** as 4 seções sugeridas e a lista de trechos. Não é persistida.
- **Trecho:** posição no texto (início e fim), seção atribuída, confiança e marcação de conferência.
- **Artefato do organizador:** arquivo de pesos versionado, com SHA-256, produzido pelo EXP-023
  (`organizer-v1.json`).
- **Estudo** (existente): recebe as 4 seções revisadas. Nenhum campo novo.

---

## 5. Success Criteria *(mandatory)*

- **SC-001**: A organização responde em até 200 ms (p95, no servidor) para uma página típica de anotações, na
  máquina de referência.
- **SC-002**: Em 100 % dos casos de teste, o texto organizado contém todo o texto recebido exatamente uma vez,
  sem nenhuma alteração.
- **SC-003**: **Paridade com o experimento.** Nas 24 páginas de teste do EXP-023, em todas as condições, o
  organizador do produto devolve exatamente os mesmos trechos e seções que a implementação de referência do
  experimento.
- **SC-004**: Do texto revisado ao texto organizado em 1 ação, e de volta ao texto único em 1 ação (mais a
  confirmação, se houve edição).
- **SC-005**: O Leitorum inicia e a digitalização e a importação funcionam normalmente quando o artefato está
  ausente.
- **SC-006**: 100 % dos 10 temas com contraste WCAG AA na área organizada. O fluxo completo é operável só com
  teclado e em 320 px.
- **SC-007**: Suítes `npm test`, `pytest` e `npm run build` 100 % aprovadas.

---

## 6. Assumptions & Dependencies

- A pipeline e o artefato vêm do EXP-023 (commit `58dac1e`), na configuração aceita no ADR-010:
  - decodificação só por custo de troca ponderado pela coesão;
  - transição e propagação desligadas.

  Como o produto incorpora o código e o arquivo de pesos, o plano técnico decide.
- **A qualidade em texto real não está demonstrada** (0,50 em 3 estudos). A interface trata a organização sempre
  como sugestão.
- Medir de novo nos estudos do usuário quando houver pelo menos 30 é recomendação do ADR-010, **fora desta
  fatia**.
- **Fora de escopo nesta fatia:**
  - calibração com os estudos do usuário;
  - aprender com as correções do leitor;
  - organizar na tela de edição de um estudo já salvo;
  - reordenar trechos dentro de uma seção;
  - ampliar as pistas de Referências para formatos de fichamento (recomendação do ADR-010, que pede novo
    experimento).
