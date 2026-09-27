# Feature Specification: F0.6.1 — Importação Inteligente

**Feature Branch**: `040-importacao-inteligente`

**Created**: 2026-09-27

**Status**: Ready for Planning

**Input**: User description: "F0.6.1 — Importação Inteligente: Evoluir o atual sistema de importação para que o usuário continue trabalhando com uma única entrada de texto, enquanto o Leitorum identifica e organiza sua estrutura semântica (Resumo, Explicação, Conceitos, Referências) de forma tolerante a variações razoáveis de cabeçalhos e formatos, eliminando a fragmentação obrigatória em quatro campos separados, exibindo prévia clara e garantindo a preservação absoluta do texto original."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Importação em Fluxo Contínuo e Direto (Priority: P1)

Como estudante e leitor do sistema, desejo colar o texto integral de uma resposta gerada por IA ou anotação pessoal em uma única área de texto e ter a estrutura semântica do fichamento (Resumo, Explicação, Conceitos e Referências) reconhecida e exibida de forma organizada em uma prévia antes de salvar, para que eu possa concluir o fichamento sem o atrito de preencher múltiplos formulários.

**Why this priority**: É a essência do princípio de UX da versão 0.6 ("Colar → Leitorum entende → Usuário confere → Salvar"). Reduz o esforço cognitivo e o tempo de cadastro de novos estudos, eliminando a fragmentação inicial obrigatória.

**Independent Test**: Acessar a tela de importação de estudos (`ImportView`), colar um texto único com seções canônicas de estudo em um único campo de entrada e verificar que a prévia organiza imediatamente as seções com seus respectivos conteúdos e títulos, permitindo salvar o estudo diretamente com persistência das quatro seções e do texto bruto (`source_response`).

**Acceptance Scenarios**:

1. **Given** um leitor na tela de importação de estudo com um livro e capítulo selecionados, **When** ele colar um texto único contendo títulos estruturados no campo de entrada principal, **Then** o sistema processa a estrutura e apresenta imediatamente a prévia com os blocos de Resumo, Explicação, Conceitos e Referências organizados.
2. **Given** a prévia gerada com sucesso e sem avisos impeditivos, **When** o leitor clicar no botão principal "Salvar Estudo", **Then** o estudo é criado no acervo com as quatro seções preenchidas e com o texto original íntegro armazenado em `source_response`.
3. **Given** um texto colado sem alterações adicionais requeridas, **When** o usuário realizar o fluxo completo, **Then** ele não é obrigado a navegar ou rolar por quatro campos `<textarea>` segregados para conseguir salvar.

---

### User Story 2 - Reconhecimento Tolerante a Variações Lexicais e Formatações (Priority: P1)

Como leitor que estuda com diferentes assistentes de IA e estilos de anotação, desejo que o Leitorum reconheça variações razoáveis de títulos (ex.: "Visão Geral", "Síntese", "Ideia Central", "Vocabulário", "Termos-chave", "Fontes", "Bibliografia"), prefixos numéricos e marcações tipográficas variadas, associando-as com segurança às seções corretas.

**Why this priority**: Usuários utilizam prompts diversos e recebem formatos variados de diferentes modelos de linguagem. O parser rígido anterior descartava sinônimos válidos em texto não atribuído, frustrando o fluxo de importação.

**Independent Test**: Submeter amostras de textos contendo títulos com variações conhecidas (ex.: `# 1. Visão Geral`, `**Conceitos Fundamentais:**`, `### Fontes Consultadas`), verificando que o parser associa os conteúdos respectivamente a `summary`, `concepts` e `references`, emitindo avisos informativos em vez de falhas.

**Acceptance Scenarios**:

1. **Given** um texto contendo títulos sinônimos mapeados (ex.: "Visão Geral" ou "Síntese" para Resumo; "Aprofundamento" ou "Desenvolvimento" para Explicação; "Termos-chave" ou "Glossário" para Conceitos; "Fontes" ou "Bibliografia" para Referências), **When** o texto for analisado, **Then** o sistema associa os respectivos blocos às quatro seções fundamentais da aplicação.
2. **Given** cabeçalhos com numeração ordinal ou prefixos (ex.: `1. Resumo:`, `## II - Conceitos`, `**Seção 3: Explicação**`), **When** processados pelo parser, **Then** a identificação semântica é concluída com sucesso ignorando ruídos de formatação.
3. **Given** um trecho de texto contendo blocos de código (` ``` `), **When** houver linhas dentro do bloco de código com palavras que coincidem com títulos (ex.: `# Resumo de variáveis`), **Then** o analisador preserva o bloco de código intacto sem interpretá-lo como um divisor de seção do fichamento.

---

### User Story 3 - Tratamento e Atribuição de Conteúdo Não Classificado (Priority: P2)

Como leitor do sistema, quando meu texto contiver saudações, introduções gerais ou cabeçalhos atípicos que o sistema não consiga identificar com certeza, desejo ser alertado de forma visualmente clara sobre o texto não classificado e ter controles rápidos para decidir seu destino, garantindo que nenhuma informação seja perdida.

**Why this priority**: Evita perda de conteúdo e dá autonomia ao leitor caso o assistente de IA inclua preâmbulos (ex.: "Aqui está o resumo que você pediu:") ou seções personalizadas.

**Independent Test**: Submeter texto com introdução genérica anterior ao primeiro cabeçalho e verificar que o bloco é sinalizado na interface como "Texto não classificado" com avisos claros e ações rápidas para associá-lo a uma seção ou mantê-lo registrado.

**Acceptance Scenarios**:

1. **Given** um texto contendo parágrafos antes da primeira seção reconhecida, **When** a prévia for exibida, **Then** esses parágrafos aparecem sinalizados na seção "Conteúdo Não Classificado", alertando o usuário sobre a pendência.
2. **Given** um bloco de conteúdo não classificado, **When** o leitor acionar uma ação rápida (ex.: "Mover para Resumo" ou "Mover para Explicação"), **Then** o conteúdo é incorporado à seção escolhida e a prévia é atualizada sem perda de texto.
3. **Given** qualquer situação de ambiguidade no texto importado, **When** o estudo for salvo, **Then** o texto colado na íntegra permanece intacto no campo `source_response`.

---

### User Story 4 - Conferência e Edição Rápida Pré-Salvamento (Priority: P3)

Como leitor do sistema, desejo poder fazer pequenos ajustes textuais ou correções pontuais diretamente no ambiente da prévia antes de confirmar o salvamento, com opção de modo avançado para ajustes manuais caso deseje inspecionar os campos individualmente.

**Why this priority**: Oferece flexibilidade para pequenos retoques sem quebrar a fluidez da experiência principal, mantendo a compatibilidade com usuários que preferem ajustes manuais finos.

**Independent Test**: Realizar uma edição de texto na prévia ou no texto original colado e verificar que a prévia reflete a alteração de forma consistente, permitindo salvar o resultado final sem inconsistências.

**Acceptance Scenarios**:

1. **Given** a prévia estruturada exibida na tela, **When** o leitor identificar uma palavra a corrigir, **Then** ele pode realizar o ajuste sem precisar recomeçar o processo de colagem do início.
2. **Given** um usuário que necessite de controle total de cada campo, **When** ele acionar a opção "Ajuste manual por seções", **Then** os campos individuais tornam-se acessíveis de forma não destrutiva, preservando o conteúdo já analisado.

---

### Edge Cases

- **Texto sem nenhum título identificável (bloco maciço de texto)**: O sistema não deve falhar com erro 500 nem travar a tela. O conteúdo deve ser classificado como `unassigned_text` ou atribuído à primeira seção com aviso explicativo sugerindo a inclusão de cabeçalhos ou ajuste rápido.
- **Títulos duplicados da mesma seção** (ex.: dois blocos iniciados por "Resumo"): O sistema deve concatenar os blocos com espaçamento adequado ou anexar o segundo bloco com aviso informativo, preservando o conteúdo sem sobrescrever silenciosamente o primeiro.
- **Marcações mistas de Markdown e texto puro**: O parser deve ser resiliente a misturas como `## 1. Resumo` e `Conceitos:` sem hashes no mesmo documento.
- **Preservação de caracteres especiais, emojis e tags HTML**: O parser e a renderização da prévia devem escapar adequadamente tags maliciosas contra XSS, preservando pontuações, acentos e emojis originais do usuário.
- **Volume extenso de texto**: Para textos de até 50.000 caracteres, a análise e geração de prévia não deve exceder 500ms na máquina local.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE fornecer na interface de importação uma área de texto unificada e predominante para colagem do texto completo do estudo (`source_response`).
- **FR-002**: O analisador sintático/semântico do sistema DEVE reconhecer como divisores de seção cabeçalhos canônicos e suas variações semânticas usuais em língua portuguesa:
  - **Resumo**: `resumo`, `visao geral`, `visao-geral`, `sintese`, `ideia central`, `introducao`.
  - **Explicação**: `explicacao`, `aprofundamento`, `desenvolvimento`, `analise`, `compreensao`, `detalhamento`.
  - **Conceitos**: `conceitos`, `conceitos-chave`, `termos`, `termos-chave`, `vocabulario`, `glossario`, `definicoes`.
  - **Referências**: `referencias`, `fontes`, `bibliografia`, `leituras complementares`, `obras citadas`.
- **FR-003**: O analisador DEVE reconhecer cabeçalhos independentemente da formatação textual utilizada:
  - Marcadores Markdown: `#`, `##`, `###`, `####`.
  - Formatação em negrito: `**Título**` ou `__Título__`.
  - Prefixos ordinais e numéricos: `1.`, `1 -`, `I.`, `Seção 1:`.
  - Sufixos comuns: `:` ou `-`.
  - Letras maiúsculas ou minúsculas (insensível a caixa e diacríticos acentuados).
- **FR-004**: O analisador DEVE isolar completamente blocos de código com cercas Markdown (code fences ` ``` `) para que linhas que comecem com `#` ou palavras-chave dentro do código não sejam interpretadas como delimitadores de seção.
- **FR-005**: O sistema DEVE gerar uma prévia estruturada e legível do estudo contendo as quatro seções mapeadas (`summary`, `explanation`, `concepts`, `references`) e eventuais avisos de consistência.
- **FR-006**: O sistema DEVE identificar trechos de texto não associados a nenhuma das quatro seções (ex.: parágrafos pré-resumo ou seções atípicas) como `unassigned_text` e sinalizá-los na interface com avisos claros.
- **FR-007**: O sistema DEVE permitir ao leitor, na interface de conferência da prévia, incorporar trechos não classificados a qualquer uma das seções do estudo com um clique.
- **FR-008**: O sistema DEVE garantir que a experiência primária de importação permita ir do texto colado ao estudo salvo sem a obrigatoriedade de rolar ou preencher quatro campos de texto segregados.
- **FR-009**: O sistema DEVE manter o acesso opcional e não destrutivo a campos manuais individuais para usuários que prefiram conferência granular antes de salvar.
- **FR-010**: O sistema DEVE persistir no banco de dados tanto as seções estruturadas individuais (`summary`, `explanation`, `concepts`, `references`) quanto a íntegra original do texto colado (`source_response`), cumprindo o princípio constitucional de preservação absoluta de dados.
- **FR-011**: O sistema DEVE atualizar a prévia inteligente instantaneamente após o evento de colagem (`paste`) do usuário no campo de entrada principal, disponibilizando botão visível "Atualizar prévia" para sincronizar a análise caso o usuário edite o texto bruto manualmente após a colagem.
- **FR-012**: Caso o texto colado contenha trechos não classificados (`unassigned_text`), o sistema DEVE sinalizá-los com destaque na prévia oferecendo atalhos de 1 clique ("Mover para Resumo", "Mover para Explicação", "Mover para Conceitos", "Mover para Referências"); caso o usuário decida salvar o estudo sem reatribuí-los, o sistema DEVE anexar o conteúdo residual ao final da seção de Explicação com um divisor visual suave, garantindo zero perda de informação.
- **FR-013**: O sistema DEVE agrupar os quatro campos de texto manuais segregados legados em um painel colapsável ("Ajuste manual detalhado"), recolhido por padrão, garantindo que o fluxo prioritário permaneça limpo e direto (`Colar → Conferir Prévia → Salvar`), sem obrigar o leitor a interagir com os campos isolados.

### Key Entities *(include if feature involves data)*

- **Study**:
  - `id`: Inteiro (Chave Primária)
  - `book_id`: Inteiro (Chave Estrangeira para `books.id`)
  - `chapter_id`: Inteiro (Chave Estrangeira para `chapters.id`, opcional)
  - `user_id`: Inteiro/UUID (Identificador do autor/proprietário)
  - `title`: String (Título do fichamento/estudo)
  - `summary`: Texto (Conteúdo da seção Resumo)
  - `explanation`: Texto (Conteúdo da seção Explicação)
  - `concepts`: Texto (Conteúdo da seção Conceitos)
  - `references`: Texto (Conteúdo da seção Referências)
  - `source_response`: Texto (Texto bruto integral colado pelo usuário na importação)
  - `created_at` / `updated_at`: DateTime UTC

- **ImportPreviewResult** (Estrutura de transferência/análise da prévia):
  - `sections`: Dicionário mapeando as quatro seções normalizadas
  - `unassigned_text`: Texto identificado que não pôde ser atribuído com segurança a nenhuma seção
  - `warnings`: Lista de mensagens informativas ou alertas ao usuário sobre o resultado da análise
  - `confidence_score`: Nível qualitativo de confiança na estruturação (ex.: total, parcial, com avisos)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: O tempo necessário para um leitor colar uma resposta de IA padrão e concluir o salvamento do estudo deve ser inferior a 15 segundos no fluxo usual.
- **SC-002**: A taxa de acerto do parser em associar sinônimos usuais em português (visão geral, aprofundamento, termos-chave, fontes) às quatro seções deve ser superior a 95% em casos de testes sintéticos.
- **SC-003**: 100% dos textos colados devem manter a sua integridade literal preservada no campo `source_response` do banco de dados, sem perda de caracteres, truncamento ou formatação corrompida.
- **SC-004**: O processamento da análise do texto colado e a renderização da prévia estruturada devem responder em menos de 400 milissegundos para textos de até 50.000 caracteres em ambiente local.
- **SC-005**: 100% dos blocos de código (` ``` `) contidos no texto original devem ser preservados sem cortes e sem disparar falsos divisores de seção.

## Assumptions

- O usuário continuará selecionando o livro e o capítulo previamente antes ou durante a importação do estudo, mantendo o vínculo com o acervo.
- O estudo continua estruturado em torno das 4 dimensões conceituais consolidadas do Leitorum: Resumo, Explicação, Conceitos e Referências.
- A persistência respeita a API e modelos do SQLite existentes sem demandar alterações destrutivas nas tabelas do acervo ativo.
- A aplicação opera localmente em processo único e sem envio de texto do usuário a serviços externos de processamento de linguagem natural (análise puramente local e determinística).
