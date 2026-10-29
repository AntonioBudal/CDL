# Feature Specification: Organizador v2 e Registro Silencioso do Feedback de Revisão

**Feature Branch**: `091-organizer-v2-feedback`

**Created**: 2026-10-28

**Status**: Concluída em 2026-10-28 nas três fatias: [A](plan-A.md), [B](plan-B.md) e [C](plan-C.md). Na fatia C, o
adaptador entrou com a ativação **desligada** (opção A do usuário, depois da medição do EXP-025 F05). A FR-013 vale
só com `LEITORUM_ORGANIZER_ADAPTER=on`.

**Input**: pedido do usuário de 2026-10-28, depois do EXP-024, em 3 passos:
1. trocar o organizador do Leitorum pelo `organizer-v2` (EXP-025);
2. registrar em silêncio o pacote `leitorum-feedback/1` a cada estudo salvo pela digitalização ou por "Organizar
   nas 4 seções", e preparar um adaptador online enxuto que só liga depois de N estudos revisados;
3. manter **desligada** a pós-correção automática da leitura, guardando as diferenças de leitura só para curadoria
   futura de ajuste fino.

Base técnica: [EXP-025](../../document-intelligence/experiments/EXP-025/RESULTS.md) e
[ADR-011](../../document-intelligence/docs/adr/ADR-011-organizer-v2-estatico.md) (`ACCEPTED`);
[EXP-024](../../document-intelligence/experiments/EXP-024/RESULTS.md) para o adaptador.

---

## 1. Contexto

- **Hoje (feature 089):** o botão "Organizar nas 4 seções" usa o `organizer-v1.json` (EXP-023, ADR-010). A sugestão
  existe só no navegador: ao salvar, o Leitorum guarda as 4 seções finais e esquece o que foi sugerido.
- **Digitalização (feature 086):** o estudo salvo já guarda o texto lido cru em `source_response`. O texto revisado
  pelo leitor vai para as seções. A diferença entre os dois é a correção humana da leitura, mas ninguém a calcula.
- **EXP-025:** o `organizer-v2` é o v1 congelado mais 4 pistas fixas de referência:
  - fichamentos fictícios: 0,704 → 0,751 de Macro-F1; Referências do fichamento em lista 0,00 → 0,55;
  - teste do EXP-023: idêntico ao v1;
  - custo: 0,017 ms por página;
  - **nos 4 estudos reais do usuário, ganho zero**: as pistas não disparam nos formatos que o usuário escreve.
- **EXP-024:** aprender com o uso só vale com um registro fiel do que foi sugerido e do que foi salvo. Dos
  componentes testados, os que renderam foram os pesos online sobre o diff (E1) e o contexto do livro e do leitor
  (E2). $T_{\text{user}}$ piorou e o *replay* custou 32,8 s.
- **Conclusão:** o valor desta feature está mais no registro do feedback do que na troca de artefato. É ele que
  vai mostrar os formatos reais de Referências.

**Relação com os roadmaps:** feature avulsa, pedida pelo usuário, fora do Roadmap 0.9. Não altera o estado de
nenhuma feature da 0.5 nem da 0.9.

---

## 2. User Scenarios & Testing *(mandatory)*

### User Story 1 — Organizador v2 no lugar do v1 (Priority: P1)

Como leitor que escreve referências em lista ("Título — Autor", links, URLs, "Título (Autor, ano)"), quero que
"Organizar nas 4 seções" reconheça essas linhas como Referências, sem piorar o resto.

**Independent Test**: com o v2 instalado, os 192 casos fictícios de `parity-v2.json` saem iguais aos do EXP-025;
uma página fictícia com "- A margem e o centro — Lúcia Dantas" põe a linha em Referências.

**Acceptance Scenarios**:

1. **Given** o artefato v2 íntegro, **When** o leitor organiza um texto, **Then** a resposta informa a versão `2` e
   o SHA-256 do v2, e o resultado é o do motor de referência do EXP-025.
2. **Given** um texto em que nenhuma das 4 pistas dispara, **When** o leitor organiza, **Then** o resultado é
   idêntico ao do v1.
3. **Given** o artefato v2 ausente ou com SHA-256 diferente, **When** o leitor abre a digitalização, **Then** o botão
   fica indisponível como hoje e o resto do Leitorum segue igual.

### User Story 2 — Registro silencioso do feedback (Priority: P1)

Como dono do Leitorum, quero que cada estudo salvo pela digitalização ou depois de "Organizar nas 4 seções" deixe
um registro local do que o motor sugeriu e do que o leitor salvou, para medir e, no futuro, ensinar o organizador
e o leitor com dados reais, sem pedir nada ao leitor.

**Independent Test**: salvar um estudo fictício organizado gera um registro `leitorum-feedback/1` válido, ligado ao
estudo e ao usuário. Derrubar o registro (erro forçado) não impede o estudo de ser salvo.

**Acceptance Scenarios**:

1. **Given** um texto organizado e conferido, **When** o leitor salva, **Then** fica um registro com:
   - a sugestão do organizador (trechos, seção sugerida, confiança, "conferir");
   - as 4 seções salvas;
   - a versão e o SHA-256 do artefato.
2. **Given** uma página digitalizada e corrigida (organizada ou não), **When** o leitor salva, **Then** o registro
   guarda também as correções de leitura (`human_corrections`) entre o texto lido (`source_response`) e o texto
   revisado.
3. **Given** um texto importado e organizado, **When** o leitor salva, **Then** fica um registro só com a parte do
   organizador (não há leitura).
4. **Given** qualquer falha ao gravar o registro, **When** o leitor salva, **Then** o estudo é salvo igual e nenhuma
   mensagem aparece. A falha vai para o log só como código, sem texto.
5. **Given** um estudo apagado de vez (lixeira esvaziada ou conta removida), **When** a exclusão termina,
   **Then** o registro dele também some.

### User Story 3 — Adaptador online dormente (Priority: P2)

Como leitor que já revisou muitos estudos, quero que o organizador aprenda o meu jeito de escrever, mas só depois
de haver dados suficientes e sem nunca ficar pior que o v2.

**Independent Test**: com usuários fictícios, abaixo de N registros revisados a sugestão é exatamente a do v2; a
partir de N, o estado do usuário é atualizado a cada registro novo e a sugestão passa a usar o adaptador. Um
usuário nunca altera o estado de outro.

**Acceptance Scenarios**:

1. **Given** um usuário com menos de N registros revisados, **When** organiza, **Then** a sugestão é a do v2 puro.
2. **Given** um registro novo, **When** é gravado, **Then** o estado do usuário é atualizado de forma incremental, em
   tempo limitado, sem reler os registros antigos.
3. **Given** N ou mais registros, **When** o usuário organiza, **Then** a sugestão usa o adaptador do usuário e a
   resposta informa isso (`engine.adapter`).
4. **Given** um usuário B, **When** o usuário A salva, **Then** o estado de B não muda.

### User Story 4 — Pós-correção da leitura continua desligada (Priority: P1)

Como leitor, quero que o texto lido continue chegando como o motor leu, sem correções automáticas, porque no
EXP-024 elas tiraram só 6–7 % do erro e estragaram palavras certas.

**Acceptance Scenarios**:

1. **Given** qualquer página, **When** é lida, **Then** o texto da revisão é o do motor, sem pós-correção, como hoje.
2. **Given** correções de leitura registradas, **When** o motor lê páginas novas, **Then** nada delas é aplicado.
   Ficam só para curadoria futura.

### Edge Cases

- **Leitor desfaz a organização** ("Voltar para texto único") e salva: o registro guarda a sugestão como
  **revertida**, sem as seções-alvo. O EXP-024 trata reversão como sinal, não como rótulo.
- **Texto reescrito, não corrigido:** o filtro de ruído de edição do EXP-024 separa correção de leitura de reescrita
  autoral. Só as correções entram em `human_corrections`; o resto fica marcado como reescrita, sem texto duplicado.
- **Página grande:** o registro tem teto de tamanho (ver FR-009); acima dele, grava só a parte do organizador.
- **Estudo editado depois de salvo:** fora desta feature. O registro descreve o momento do salvamento.
- **Artefato trocado depois:** cada registro guarda a versão e o SHA-256 que produziram a sugestão.

---

## 3. Requirements *(mandatory)*

### Functional Requirements

**Organizador v2**
- **FR-001**: O backend MUST carregar `organizer-v2.json` com o SHA-256 fixado
  (`9f6530a32726d593142b7a2de3bce3efc1c0095abf3a91335364db6343978aee`) e calcular as 4 pistas a partir de
  `extra_cues` do artefato.
- **FR-002**: O motor MUST recusar um artefato cujas pistas não sejam exatamente as conhecidas, e ficar indisponível
  como hoje.
- **FR-003**: O backend MUST reproduzir os 192 casos de `parity-v2.json` (SHA-256 `6726ddc4…1573`) em teste
  automatizado. Os casos do `parity-v1` continuam valendo onde nenhuma pista dispara.
- **FR-004**: O contrato de `/api/organize` não muda, salvo `engine.version = "2"` e o campo novo `engine.adapter`
  (`null` ou a contagem do usuário).

**Registro do feedback**
- **FR-005**: Ao salvar um estudo vindo da digitalização ou de uma organização, o Leitorum MUST gravar um
  registro `leitorum-feedback/1` ligado ao estudo e ao usuário, sem confirmação nem aviso ao leitor.
- **FR-006**: O registro MUST conter:
  - `schema` (`leitorum-feedback/1`), `created_at`, a origem (`digitize` ou `import`);
  - **organizador** (se houve organização): o texto organizado, os trechos sugeridos (início, fim, seção,
    confiança, "conferir"), as 4 seções salvas, o desfecho (`saved` ou `reverted`), a versão, o SHA-256 e o uso
    ou não do adaptador;
  - **leitura** (se houve digitalização): as correções `human_corrections` no formato do LDF 2.0
    (`op`, `path`, `value`, `author`, `timestamp`, `reason: "ocr-fix"`) entre `source_response` e o texto
    revisado, e a contagem de linhas reescritas.
- **FR-007**: Gravar o registro MUST NOT bloquear, atrasar perceptivelmente nem fazer falhar o salvamento do estudo.
- **FR-008**: O registro MUST NOT aparecer na interface, nos logs (só códigos e contagens) nem em exportações de
  dados para fora da máquina. Vai nos backups do banco como o resto do acervo.
- **FR-009**: Cada registro MUST ter teto de tamanho (proposta: 256 KB).
- **FR-010**: O registro MUST ser apagado quando o estudo for apagado de vez e quando a conta for removida.

**Adaptador dormente**
- **FR-011**: O Leitorum MUST manter, por usuário, um estado incremental do adaptador com só três componentes do
  EXP-024:
  - **E1:** pesos online sobre o diff de revisão, ancorados ao v2 (âncora L2 e projeção);
  - **E2:** centróides do leitor e do livro, e a forma de linha de referência aprendida (`ref_shape_user`);
  - **gating** por comportamento (reversão e retenção sem atualização positiva).
- **FR-012**: O adaptador MUST NOT usar $T_{\text{user}}$, *replay*, portão-sombra com canário nem pós-correção de
  leitura.
- **FR-013**: Abaixo de N = 30 registros revisados do usuário (§7, Q3 e Q4), a sugestão MUST ser exatamente a do v2. O
  estado continua sendo atualizado desde o primeiro registro, para estar pronto ao ligar.
- **FR-014**: A atualização do estado MUST ser incremental (sem reler registros antigos) e ficar abaixo de um teto
  de tempo por registro (proposta: p95 ≤ 150 ms; EXP-024 mediu 73–87 ms).
- **FR-015**: O estado MUST ser isolado por usuário e reconstruível a partir dos registros (comando de manutenção),
  caso fique corrompido ou o artefato mude.

**Leitura**
- **FR-016**: A pós-correção automática da leitura MUST continuar desligada. Nenhum código desta feature altera o
  texto lido.

### Key Entities

- **OrganizerFeedback** (novo): um por estudo salvo nas condições da FR-005. Campos: `id`, `user_id`, `study_id`,
  `schema`, `origin`, `payload` (JSON da FR-006), `size_bytes`, `created_at`.
- **OrganizerUserState** (novo): um por usuário. Campos: `user_id`, `artifact_sha256`, `reviewed_count`, `state`
  (JSON com pesos, centróides e contadores), `updated_at`.
- **Migração nova** (`0033`): cria as duas tabelas. No banco ativo do D:, só com o serviço parado, snapshot
  verificado e aprovação do usuário, como na 090.

---

## 4. Success Criteria *(mandatory)*

- **SC-001**: 192 de 192 casos de paridade v2 reproduzidos no backend.
- **SC-002**: 100 % dos estudos fictícios salvos nos 4 caminhos (digitalizado, digitalizado e organizado,
  importado e organizado, organização revertida) geram o registro esperado; 0 nos caminhos que não devem gerar.
- **SC-003**: com falha forçada na gravação do registro, 100 % dos estudos são salvos.
- **SC-004**: abaixo de N, 100 % das sugestões iguais às do v2; usuário B inalterado depois de saves do usuário A.
- **SC-005**: atualização do adaptador com p95 ≤ 150 ms por registro, medida com dados fictícios.
- **SC-006**: nenhum texto de estudo nos logs (teste que varre os logs da suíte).
- **SC-007**: `npm test`, `pytest` e `npm run build` verdes.

---

## 5. Fora do escopo

- Ligar qualquer aprendizado com os estudos reais **antes** de N registros.
- Capturar edições feitas depois do salvamento (StudyView).
- Pós-correção da leitura, ajuste fino do leitor e exportação dos registros para o `document-intelligence/` (será
  uma feature ou experimento próprio, com cópia via backup e regras de privacidade).
- Tela de consulta dos registros.

---

## 6. Fatias propostas

| Fatia | Entrega | Toca o banco ativo? |
| :--- | :--- | :--- |
| **A** | troca para o v2, pistas pelo artefato, paridade v2 (US1) | não |
| **B** | tabela, migração 0033, registro `leitorum-feedback/1` na digitalização e na importação (US2, US4) | sim (migração, com aprovação) |
| **C** | adaptador dormente E1 + E2 + gating, estado por usuário, comando de reconstrução (US3) | não (usa as tabelas da B) |

Cada fatia passa pelo ciclo Spec Kit (plano, tarefas, análise, implementação) com aprovação, e gera um commit.

---

## 7. Decisões (aprovadas pelo usuário em 2026-10-28, todas pela recomendação)

- **Q1 — Adotar o v2 mesmo com a H4 reprovada no pré-registro?** A medida de passagem única deu até +2,18 ms por
  ruído; o custo direto é 17 µs por página.
  **Decisão:** sim; ADR-011 aceito com essa ressalva registrada.
- **Q2 — "Em silêncio" inclui não mencionar em lugar nenhum?**
  **Decisão:** sem aviso nem confirmação no fluxo, mas com um parágrafo na página "Sobre" explicando que o
  Leitorum guarda localmente, junto do estudo, a sugestão e as correções para melhorar o organizador. Os dados não
  saem da máquina.
- **Q3 — N para ligar o adaptador: 20 ou 30 registros revisados?**
  **Decisão:** 30. No EXP-024, as quedas iniciais apareciam nas primeiras dezenas de páginas, e hoje há 4
  estudos no banco: com qualquer dos dois, o adaptador fica dormente por bastante tempo.
- **Q4 — O que conta como "revisado"?**
  **Decisão:** registro com organização salva (não revertida). Só digitalização sem organização não conta
  para o organizador.
- **Q5 — Guardar o texto no registro ou só posições?** As posições sozinhas se perdem quando o estudo é editado.
  **Decisão:** guardar o texto organizado e as seções salvas no registro, no mesmo banco local e com a mesma
  privacidade do estudo, apagado junto com ele (FR-010).
