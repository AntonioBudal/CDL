# Feature Specification: Digitalizar Caderno — Foto de Página Manuscrita para Estudo

**Feature Branch**: `086-digitalizar-caderno-estudo`

**Created**: 2026-10-27

**Status**: Implementada em 2026-10-27; validação manual de temas, celular e rede desligada pendente com o usuário

**Input**: Pedido do usuário (2026-10-27): levar a IA do subprojeto `document-intelligence/` para o Leitorum. Decisões
do usuário: (1) lançar com o leitor de licença livre, apresentando o texto como rascunho a revisar; (2) o resultado
vira um **Estudo**; (3) trabalho no backend e no frontend autorizado, seguindo as métricas de design estabelecidas.

---

## 1. Contexto

A rota `/digitalizar` existe hoje como tela informativa estática (feature 069), que proíbe upload, câmera e
chamadas de rede. O subprojeto `document-intelligence/` agora tem um pipeline medido de ponta a ponta (ADR-008):
foto da página → linhas detectadas → texto em ordem de leitura → documento LDF 2.0, processado inteiramente no
computador do usuário (~7 s e ~800 MB de RAM por página).

**Qualidade honesta da leitura.** O leitor que pode ir para o produto (PP-OCRv6, Apache-2.0) erra cerca de **1 em
cada 4 caracteres** em manuscrito português (24–27 % de CER de página). O leitor ajustado (~11 %) foi treinado com
o BRESSAY, de licença não comercial, e **não entra** no produto. O texto produzido é, portanto, um **rascunho**
que o leitor corrige antes de salvar; a troca futura do modelo de leitura não deve exigir mudança de interface.

**Relação com os roadmaps.** O Roadmap 0.9 proíbe funcionalidades novas; esta feature é avulsa, pedida
explicitamente pelo usuário, e não altera o estado de nenhuma feature da 0.9. Ela **substitui** a tela informativa
da 069 (as restrições NR-001 a NR-006 daquela feature deixam de valer para `/digitalizar`).

---

## Clarifications

### Session 2026-10-27

- Q: Em qual seção do Estudo entra o texto transcrito? → A: o leitor escolhe na hora, na tela de revisão, entre
  Resumo, Explicação, Conceitos e Referências.
- Q: Quantas fotos formam um Estudo? → A: uma foto por estudo.
- Q: Quem pode usar a digitalização? → A: todos os usuários autenticados, um pedido por vez.

---

## 2. User Scenarios & Testing *(mandatory)*

### User Story 1 — Fotografar uma página e receber o texto para revisar (Priority: P1) [MVP]

Como leitor com anotações em caderno de papel, quero enviar a foto de uma página (tirada na hora pelo celular ou
escolhida dos arquivos) e receber o texto transcrito, linha por linha e em ordem de leitura, para conferir e
corrigir.

**Why this priority**: É o valor central: tirar o texto do papel sem digitar tudo.

**Independent Test**: Com uma imagem fictícia de manuscrito (amostra sintética do projeto), abrir `/digitalizar`,
enviar a imagem e ver o texto aparecer num editor, com aviso de rascunho e indicação das linhas de baixa
confiança.

**Acceptance Scenarios**:

1. **Given** um usuário autenticado em `/digitalizar`, **When** escolhe ou tira uma foto (JPEG, PNG ou WebP),
   **Then** vê o progresso enquanto a página é processada e, ao final, o texto transcrito num campo editável.
2. **Given** o texto transcrito, **When** a tela o apresenta, **Then** um aviso visível diz que o texto foi lido
   automaticamente, pode conter erros e deve ser revisado antes de salvar.
3. **Given** linhas lidas com baixa confiança, **When** o texto é exibido, **Then** essas linhas ficam marcadas de
   forma discreta e acessível (não só por cor), sem impedir a edição.
4. **Given** uma foto em que nenhuma linha de texto é encontrada, **When** o processamento termina, **Then** a tela
   explica o resultado e sugere tirar outra foto (folha inteira, boa luz, sem sombra), sem criar nada.

---

### User Story 2 — Salvar o texto revisado como Estudo (Priority: P1) [MVP]

Como leitor, depois de revisar o texto, quero salvá-lo como um Estudo num livro e capítulo do meu acervo, para que
ele passe a fazer parte do meu caderno digital como qualquer outro estudo.

**Why this priority**: Sem salvar, a transcrição se perde; o destino escolhido pelo usuário é o Estudo.

**Independent Test**: Revisar um texto fictício, escolher um livro e capítulo fictícios num banco temporário, dar
título e salvar; o estudo aparece no capítulo com status "rascunho".

**Acceptance Scenarios**:

1. **Given** o texto revisado, **When** o leitor escolhe livro, capítulo, título e a seção que recebe o texto e
   confirma, **Then** um Estudo é
   criado pelo mesmo caminho de criação já usado pela importação, com status de leitura "rascunho".
2. **Given** o estudo criado, **When** o leitor o abre, **Then** encontra o texto revisado na seção definida para a
   transcrição e o texto lido automaticamente, sem correções, preservado como registro de origem.
3. **Given** que o leitor tenta sair da tela com texto revisado não salvo, **When** navega para outra rota,
   **Then** o sistema pede confirmação (proteção de alterações não salvas já existente).

---

### User Story 3 — Processamento local e transparente (Priority: P2)

Como leitor, quero ter certeza de que a foto do meu caderno não sai do meu computador e de que ela não fica
guardada sem eu saber.

**Why this priority**: Privacidade local é princípio do Leitorum e promessa já feita na tela da 069.

**Independent Test**: Processar uma imagem fictícia e verificar que nenhuma requisição sai para fora do servidor
local e que nenhum arquivo da imagem permanece em disco depois da resposta.

**Acceptance Scenarios**:

1. **Given** uma foto enviada, **When** o processamento termina (com sucesso ou erro), **Then** a imagem e
   quaisquer arquivos temporários são apagados; só o texto que o leitor salvar fica no acervo.
2. **Given** a tela de digitalização, **When** o leitor lê as informações, **Then** a tela diz que o processamento
   acontece no computador onde o Leitorum está instalado, inclusive quando a foto vem do celular pela rede local.

---

### User Story 4 — Estados, temas e celular (Priority: P3)

Como leitor usando qualquer um dos 10 temas, no computador ou no celular, quero uma tela clara em todos os estados
(vazio, enviando, processando, revisão, erro, salvo).

**Why this priority**: A tela precisa seguir o padrão visual e ergonômico do Leitorum (Roadmap 0.9).

**Independent Test**: Percorrer todos os estados em largura de 320 px e de desktop, em temas claro, escuro e E-Ink,
só com teclado.

**Acceptance Scenarios**:

1. **Given** qualquer tema, **When** a tela é exibida, **Then** ela usa apenas tokens CSS semânticos, sem cores
   fixas, com contraste WCAG AA.
2. **Given** o processamento em andamento, **When** a tela espera, **Then** usa esqueleto/progresso fiel ao
   resultado (não texto cru "Carregando…") e permite cancelar.
3. **Given** um celular, **When** o leitor toca em "Tirar foto", **Then** a câmera do aparelho abre pelo seletor de
   arquivo do navegador; alvos de toque têm pelo menos 44 × 44 px.

---

## 3. Edge Cases

- **Arquivo não suportado ou corrompido** (PDF, HEIC sem conversão do navegador, imagem truncada): erro claro em
  português, sem travar a tela.
- **Imagem grande demais** (acima do limite definido no plano): recusada antes de processar, com orientação.
- **Pouca memória livre no computador**: o pedido é recusado com mensagem para tentar de novo, em vez de derrubar
  o servidor.
- **Dois pedidos ao mesmo tempo** (PC e celular, ou dois usuários da instância): processados um de cada vez; o
  segundo espera ou recebe aviso de ocupado.
- **Motor de leitura ausente ou modelo corrompido** (verificação de integridade falha): a tela informa que a
  digitalização está indisponível e mantém os caminhos de saída para `/importar` e `/inbox`; o resto do Leitorum
  segue funcionando.
- **Foto girada** (celular na horizontal): a orientação gravada pela câmera é respeitada.
- **Texto vazio após revisão**: não é possível salvar um estudo sem conteúdo (regra já existente do Estudo).
- **Usuário sai da tela durante o processamento**: o processamento é cancelado ou o resultado descartado, e os
  arquivos temporários são apagados.

---

## 4. Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: A rota autenticada `/digitalizar` DEVE oferecer escolher um arquivo de imagem ou tirar uma foto
  (seletor de arquivo do navegador com preferência pela câmera no celular).
- **FR-002**: O sistema DEVE aceitar JPEG, PNG e WebP, respeitar a orientação gravada pela câmera e recusar outros
  formatos com mensagem clara.
- **FR-003**: O backend DEVE expor uma operação de **pré-visualização** que recebe a imagem e devolve o texto lido
  em ordem de leitura, linha a linha, com a confiança de cada linha e avisos; essa operação **não grava nada** no
  banco, como a pré-visualização da importação.
- **FR-004**: O processamento DEVE ocorrer inteiramente no computador onde o Leitorum roda, usando o motor do
  `document-intelligence/` com o leitor de licença livre; nenhuma chamada a serviço externo.
- **FR-005**: A imagem e arquivos temporários DEVEM ser apagados ao fim de cada pedido, com sucesso, erro ou
  cancelamento.
- **FR-006**: O texto DEVE ser apresentado num editor com aviso permanente de rascunho e marcação acessível das
  linhas de baixa confiança.
- **FR-007**: O leitor DEVE poder salvar o texto revisado como Estudo escolhendo livro, capítulo e título, pelo
  caminho de criação de estudo já existente; o estudo nasce com status "rascunho".
- **FR-008**: Na tela de revisão, o leitor DEVE escolher a seção do Estudo que recebe o texto revisado — Resumo,
  Explicação, Conceitos ou Referências (as quatro que satisfazem a regra de conteúdo do Estudo); a escolha vem com
  um valor inicial e cabe no mesmo passo de salvar. O texto lido automaticamente, sem correções, é guardado como
  registro de origem (`source_response`).
- **FR-009**: Cada foto DEVE gerar no máximo um estudo; várias páginas viram estudos separados (juntar páginas
  fica fora desta fatia).
- **FR-010**: A funcionalidade DEVE estar disponível para todos os usuários autenticados da instância, com os
  limites do FR-011; o estudo criado pertence a quem o salvou, com as mesmas regras de propriedade e visibilidade
  de qualquer estudo.
- **FR-011**: Pedidos de digitalização DEVEM ser processados um por vez e recusados com aviso quando a memória
  livre estiver abaixo do mínimo de segurança.
- **FR-012**: Se o motor estiver indisponível, `/digitalizar` DEVE informar isso e manter os atalhos para
  `/importar` e `/inbox`; o card do Ateliê de Importação deixa de dizer "Em Pesquisa" e passa a indicar que a
  leitura é um rascunho a revisar.
- **FR-013**: O motor de leitura DEVE ser um componente substituível: trocar o modelo de leitura por outro
  (por exemplo, um treinado com dados licenciados) não pode exigir mudança no frontend nem no contrato da API.

### Non-Functional & Governance Restrictions

- **NR-001 (Sem migração)**: Esta feature NÃO cria tabelas, colunas nem migrações Alembic; usa o modelo de Estudo
  existente.
- **NR-002 (Privacidade)**: Nenhum texto ou imagem real do acervo aparece em testes, logs versionados, artefatos
  da feature ou no chat; testes usam imagens e textos fictícios.
- **NR-003 (Licenças)**: Nenhum peso treinado com o BRESSAY ou outro dado `NEEDS VALIDATION` é empacotado ou
  carregado pelo produto.
- **NR-004 (Isolamento de dependências)**: O motor de leitura e suas dependências pesadas não podem quebrar a
  instalação nem a inicialização do Leitorum quando estiverem ausentes.
- **NR-005 (Design)**: Tokens semânticos dos 10 temas, zero emojis, ícones SVG, esqueletos de carregamento,
  `EmptyState` com ação, alvos de toque ≥ 44 × 44 px, foco visível e hierarquia `h1 → h2 → h3`
  (Roadmap 0.9 e TEMAS-E-SISTEMA-VISUAL).
- **NR-006 (Testes)**: `npm test`, `pytest` e `npm run build` aprovados; testes de backend em banco temporário e
  com o motor de leitura simulado; nenhum teste toca `backend/data/caderno.db`.

### Key Entities

- **Página digitalizada (transitória)**: a foto enviada; existe só durante o pedido.
- **Pré-visualização da leitura**: texto por linha, confiança por linha, avisos e identificação do motor e do
  modelo usados; não é persistida.
- **Estudo** (existente): recebe o texto revisado e o texto de origem; nenhum campo novo.

---

## 5. Success Criteria *(mandatory)*

- **SC-001**: Do envio da foto ao texto na tela em até 20 s numa página típica no computador de referência.
- **SC-002**: Zero arquivos de imagem remanescentes em disco após 100 % dos pedidos (sucesso, erro, cancelamento).
- **SC-003**: Zero requisições a hosts externos durante todo o fluxo.
- **SC-004**: O Leitorum inicia e todas as outras telas funcionam quando o motor de leitura não está instalado.
- **SC-005**: 100 % dos 10 temas com contraste WCAG AA na tela; fluxo completo operável só com teclado e em 320 px.
- **SC-006**: Do texto revisado ao Estudo salvo em no máximo 4 ações (destino, título, seção, salvar), com
  valores iniciais que permitem salvar sem mudar a seção.
- **SC-007**: Suítes `npm test`, `pytest` e `npm run build` 100 % aprovadas.

---

## 6. Assumptions & Dependencies

- O motor vem do `document-intelligence/` (pipeline do ADR-008 com o leitor original); a forma de integração
  (processo separado, serviço local ou biblioteca) é decisão do plano técnico.
- A qualidade de leitura medida (24–27 % de CER em páginas de redação digitalizadas) não foi validada em fotos de
  caderno cruas; o usuário decidiu seguir sem essa validação (2026-10-27). A interface trata o texto sempre como
  rascunho.
- Fotos vindas do celular chegam pelo próprio servidor local (rede local ou Tailscale), como o resto do Leitorum.
- Fora de escopo nesta fatia: diagramas, classificação semântica de blocos, notas de margem como estrutura
  própria, correções salvas como JSON Patch, várias colunas, e exibir as caixas das linhas sobre a foto.
