# Feature Specification: Digitalizar Caderno — Trava de Memória que Recusa Toda Leitura

**Feature Branch**: `088-memoria-digitalizacao`

**Created**: 2026-10-27

**Status**: Implementada em 2026-10-27 e validada pelo agente com página sintética. No computador de referência,
com 1 102 MB de RAM física e ~18 GB comprometíveis disponíveis, o serviço leu 3 de 3 linhas com o mínimo padrão.
O teste do motor real voltou a rodar e passou. Pendente com o usuário: enviar uma foto pela tela `/digitalizar`
depois de reiniciar o `iniciar.py`.

**Input**: Relato do usuário (2026-10-27): na tela `/digitalizar` (feature 086), anexar uma imagem devolve "Não foi
possível ler esta foto" em vez do texto lido. Decisão do usuário após o diagnóstico: medir a memória
comprometível no Windows, com mínimo calibrado pelo pico do motor mais 1 GiB de reserva, e registrar no log o
motivo e a memória medida (opção B).

---

## 1. Contexto

### Diagnóstico (feito só com páginas sintéticas e banco descartável)

- "Não foi possível ler esta foto" é o título genérico da fase de erro da tela. O motivo vem logo abaixo.
- O motor de leitura está instalado e íntegro: `check` termina com código 0, e `read` numa página fictícia
  devolveu 3 de 3 linhas.
- Pelo serviço do backend, toda leitura termina em **`503 low_memory`**, antes de o motor ser chamado. O serviço
  exige **2048 MB de memória física disponível** (research R8 da 086: pico de ~800 MiB mais 1 GiB de reserva).
  O computador de referência tem 8 GB, opera com ~82 % de uso e mostra **1,15 a 1,45 GB** disponíveis. A
  recusa é, portanto, permanente. O quickstart da 086 chegou a registrar "com 1,17 GB livres o servidor
  respondeu `503 low_memory`" como resultado esperado.
- Com a trava desligada (`LEITORUM_DIGITIZE_MIN_FREE_MB=0`), o mesmo serviço devolve o texto em ~3 s.
- Pico medido do motor em páginas sintéticas:

  | Página sintética | Memória física (pico) | Memória comprometida (pico) |
  | :--- | ---: | ---: |
  | 1200 × 800, 3 linhas | 262 MB | 460 MB |
  | 12 MP, 29 linhas | 565 MB | 765 MB |
  | 12 MP, 72 linhas, letra pequena (ampliação 2×) | 839 MB | 1 037 MB |
  | 12 MP, 133 linhas, letra minúscula (ampliação 3×) | 1 008 MB | 1 205 MB |

- No Windows, um pedido de memória só falha quando a **memória comprometível** (RAM mais arquivo de paginação)
  se esgota. No computador de referência havia **~18,5 GB** comprometíveis disponíveis, de um limite de ~32 GB.
  Com pouca RAM física, o Windows passa a usar o disco: a leitura fica mais lenta, mas não falha.
- **Falha escondida.** O motor escreve no erro padrão só o nome do tipo da exceção, mas esse arquivo é apagado
  com a pasta temporária e nunca chega ao log do servidor. A recusa por memória também não registra quanto havia
  disponível. Por isso o diagnóstico não aparecia em lugar nenhum.

### Causa

A trava de memória do FR-011 da 086 mede a grandeza errada para o Windows (RAM física disponível, em vez da
memória que ainda pode ser comprometida) e usa um mínimo acima do que a máquina de referência tem livre no uso
normal. Assim, a digitalização nunca chega a rodar.

---

## 2. User Scenarios & Testing *(mandatory)*

### User Story 1 — Ler a foto com a RAM física apertada (Priority: P1) [MVP]

Como pessoa leitora, num computador em uso normal (navegador, editor e outros programas abertos), quero que a
foto de uma página legível seja lida e o texto apareça para revisar, sem precisar fechar programas.

**Why this priority**: é a causa do relato; sem isso a feature 086 não funciona no computador de referência.

**Independent Test**: com a memória física disponível simulada abaixo de 2 GiB e a memória comprometível
simulada com folga, enviar uma página sintética legível e receber o texto (motor simulado nos testes
automatizados; motor real na validação manual com página fictícia).

**Acceptance Scenarios**:

1. **Given** 1,2 GB de RAM física disponível e vários GB de memória comprometível disponível, **When** a pessoa
   envia uma página legível, **Then** o motor é chamado e a tela mostra o texto para revisar.
2. **Given** memória comprometível disponível abaixo do mínimo, **When** a pessoa envia uma página, **Then** a
   resposta continua sendo `503 low_memory` com a mensagem atual, e o motor não é chamado.
3. **Given** o mínimo alterado por `LEITORUM_DIGITIZE_MIN_FREE_MB`, **When** a memória é medida, **Then** o valor
   configurado vale como mínimo da mesma grandeza medida.

---

### User Story 2 — Saber por que uma leitura falhou (Priority: P2)

Como pessoa que administra a instalação, quero que o log do servidor diga por que uma leitura não aconteceu, para
diagnosticar sem precisar reproduzir o erro.

**Why this priority**: a falha deste relato ficou invisível. Um próximo problema do motor também ficaria.

**Independent Test**: provocar, com motor simulado, a recusa por memória e uma falha do motor, e conferir as
linhas de log.

**Acceptance Scenarios**:

1. **Given** uma recusa por memória, **When** o pedido termina, **Then** o log registra o código `low_memory`, a
   grandeza medida, o valor disponível e o mínimo exigido, em MB.
2. **Given** que o motor termina com erro, **When** o pedido termina, **Then** o log registra o código do
   desfecho, o código de saída do motor e o nome do tipo da exceção que ele informou.
3. **Given** qualquer desfecho, **When** o log é gravado, **Then** ele não contém texto lido, conteúdo da imagem,
   nome do arquivo enviado nem caminhos temporários.

---

## 3. Edge Cases

- **Sem medida possível** (função do sistema falha): o pedido segue, como na 086.
- **RAM física muito baixa, memória comprometível com folga**: a leitura roda e pode passar dos 20 s do SC-001
  da 086 por causa da paginação. O tempo limite de 120 s continua valendo e devolve `504 timeout`.
- **Saída de erro do motor com outras linhas** (por exemplo, avisos da biblioteca de detecção com caminhos dos
  modelos): só o nome do tipo da exceção vai para o log, limitado em tamanho; se não houver um nome válido, o
  log diz que o tipo é desconhecido.
- **Linux**: a medida continua sendo a memória disponível do sistema (`MemAvailable`); a mudança de grandeza
  vale para o Windows, que é a plataforma de referência.

---

## 4. Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: No Windows, a trava de memória DEVE medir a memória comprometível disponível (RAM mais arquivo de
  paginação), e não a RAM física disponível.
- **FR-002**: O mínimo padrão DEVE ser o pico de memória comprometida medido do motor mais 1 GiB de reserva,
  arredondado para cima. Com os números da seção 1, o pico é 1 205 MB e o mínimo fica em **2 304 MB**
  (2,25 GiB).
- **FR-003**: `LEITORUM_DIGITIZE_MIN_FREE_MB` DEVE continuar mudando o mínimo, agora na grandeza do FR-001.
- **FR-004**: Abaixo do mínimo, a resposta DEVE continuar `503` com o código `low_memory` e a mensagem atual, sem
  iniciar o motor.
- **FR-005**: Toda recusa por memória DEVE registrar no log a grandeza medida, o valor disponível e o mínimo, em
  MB.
- **FR-006**: Toda falha do motor (código de saída diferente de 0) DEVE registrar no log o código de saída e o
  nome do tipo da exceção informado pelo motor, antes de a pasta temporária ser apagada.
- **FR-007**: Os registros do FR-005 e do FR-006 NÃO DEVEM conter texto lido, conteúdo ou nome da imagem, nem
  caminhos temporários.
- **FR-008**: Contrato da API, mensagens da tela e contrato de linha de comando do motor permanecem iguais.

### Non-Functional & Governance Restrictions

- **NR-001 (Sem migração)**: nenhuma tabela, coluna ou migração.
- **NR-002 (Privacidade)**: testes e validação só com páginas sintéticas e banco descartável em `tmp_path`;
  nenhuma foto real nem o banco ativo são abertos.
- **NR-003 (Escopo)**: só o backend da digitalização (`digitize_service`, `config`) e seus testes, mais a
  atualização dos documentos da 086 que citam o mínimo de 2 GiB. O frontend não muda.
- **NR-004 (Testes)**: `pytest` do backend aprovado; teste novo cobre a causa (RAM física baixa com memória
  comprometível suficiente ⇒ o motor é chamado).

### Key Entities

Nenhuma entidade nova. A pré-visualização da leitura e o Estudo da 086 não mudam.

---

## 5. Success Criteria *(mandatory)*

- **SC-001**: No computador de referência em uso normal (~1,2 GB de RAM física disponível), uma página
  sintética legível enviada pela API devolve `200` com o texto, sem fechar programas.
- **SC-002**: 100 % das recusas por memória e das falhas do motor deixam no log o motivo e os números do FR-005
  e do FR-006.
- **SC-003**: Zero ocorrências de texto lido, nome de arquivo enviado ou caminho temporário nos registros de log
  dos testes.
- **SC-004**: `pytest` do backend 100 % aprovado, exceto a falha ambiental conhecida
  `test_iniciar_rejects_relative_database_path` em worktrees sem `frontend/dist`.

---

## 6. Assumptions & Dependencies

- O pico de 1 205 MB vem de páginas sintéticas de 12 MP. Fotos maiores (até o limite de 40 MP) podem passar
  dele; a reserva de 1 GiB cobre essa diferença, e o arquivo de paginação absorve o excesso de RAM física.
- A regra de "≥ 1 GiB livre" do computador de referência é aplicada à memória comprometível, que é a que
  derruba processos quando acaba.
- Fora de escopo: mudar o título genérico "Não foi possível ler esta foto" e o botão "Tentar outra foto" para
  recusas passageiras (`low_memory`, `busy`), que não dependem da foto. Pode ser uma fatia própria.
