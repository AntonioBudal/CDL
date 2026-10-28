# Feature Specification: Armazenamento no HD de 1 TB, Cofre de Imagens Criptografadas e Cotas

**Feature Branch**: `090-armazenamento-hd-cofre-cotas` (implementada em três fatias: 090-A, 090-B e 090-C; ver
[plan.md](plan.md))

**Created**: 2026-10-27

**Status**: Aprovada em 2026-10-27 com as recomendações Q1–Q6; fatia A em planejamento de tarefas

**Input**: pedido do usuário (2026-10-27):
- levar banco, backups e imagens para um HD de 1 TB;
- cifrar todas as imagens em repouso (AES-256-GCM, chave fora do HD);
- guardar opcionalmente a foto da página digitalizada junto do estudo, com retenção automática;
- um gerenciador "Minhas Imagens e Espaço";
- cotas de 1 GB por usuário e 900 GB no servidor.

---

## 1. Contexto

Auditoria completa em [research.md §R0](research.md). Hoje:
- o banco, os backups, as capas e os avatares ficam no disco do sistema, numa árvore derivada do banco;
- capas e avatares são WebP **em claro**, servidos **sem login** pelo nome do arquivo;
- a digitalização (feature 086) **promete** apagar a foto logo depois da leitura;
- se o disco configurado sumir, o app pode criar um banco vazio sem avisar.

**Relação com os roadmaps**: feature avulsa, pedida pelo usuário, fora do Roadmap 0.9. Ela inclui migrações de
banco, então cada migração exige o snapshot pré-migração verificado (Constituição V.1 e `AGENTS.md` §2).

---

## 2. User Scenarios & Testing *(mandatory)*

### User Story 1 — Banco e arquivos no HD de 1 TB, sem risco (Priority: P1) [fatia A]

Como dono da instalação, quero levar o banco, os backups e as imagens para o HD de 1 TB com um processo assistido
que só troca o caminho ativo depois de provar que a cópia está íntegra.

**Independent Test**: em `tmp_path`, com uma raiz falsa de "HD":
- `--plan` relata sem gravar nada;
- `--execute` copia, confere (integridade, SHA-256 lógico, contagens) e troca o caminho;
- cada falha injetada termina sem troca, com a origem intacta.

**Acceptance Scenarios**:

1. **Given** o servidor parado e um alvo vazio no HD, **When** o dono executa a migração, **Then** o banco é
   copiado pela API de backup, conferido por integridade completa, contagens e SHA-256 lógico, e só então o `.env`
   passa a apontar para o HD.
2. **Given** qualquer verificação falhando, **When** a migração termina, **Then** nada é trocado, o banco de
   origem continua intacto e o relatório diz em qual etapa parou.
3. **Given** a migração concluída, **When** o HD está desconectado ou é outro disco, **Then** o Leitorum **não**
   inicia, explica o motivo e não cria banco vazio.
4. **Given** a migração concluída, **When** o dono quer voltar atrás, **Then** restaurar o `.env` anterior volta a
   usar o banco original, que ficou intacto.

### User Story 2 — Nenhuma imagem em claro no disco (Priority: P1) [fatia B]

Como leitor, quero que nenhuma imagem minha (fotos de caderno, avatar, capas enviadas) fique legível nas pastas do
servidor ou do HD.

**Independent Test**: enviar uma imagem fictícia com metadados GPS falsos. No cofre há só um arquivo `.enc`, sem
assinatura de imagem. A imagem servida pela API não tem metadados. Com a chave errada, nada abre.

**Acceptance Scenarios**:

1. **Given** um avatar, uma capa ou uma foto enviada, **When** ela é gravada, **Then** os metadados são removidos,
   a imagem é otimizada em WebP, cifrada com AES-256-GCM e salva como `<uuid>.enc`, sem extensão de imagem.
2. **Given** a imagem cifrada, **When** alguém a pede, **Then** ela só é servida a quem pode vê-la:
   - páginas de caderno: o dono;
   - avatar: quem pode ver o perfil;
   - capa: o dono do livro e quem o recebeu compartilhado.

   Para os demais, a resposta é como se a imagem não existisse. A resposta nunca é guardada em cache.
3. **Given** o HD copiado por outra pessoa, **When** ela abre os arquivos, **Then** não consegue ver as imagens,
   porque a chave mestra não está no HD.
4. **Given** a chave ausente ou errada na partida, **When** o Leitorum inicia, **Then** textos e estudos funcionam
   normalmente e a tela de imagens explica que o cofre está trancado.

### User Story 3 — Guardar a foto da página para conferência (Priority: P1) [fatia C]

Como leitor que digitalizou uma página, quero poder guardar a foto junto do estudo e vê-la ao lado do texto
enquanto reviso, sem que apagar a foto afete o estudo.

**Independent Test**:
1. digitalizar uma página fictícia marcando "Guardar a foto", salvar o estudo e abrir a "Folha original" ao lado
   do texto;
2. apagar a foto: o estudo e as 4 seções ficam idênticos, e a cota diminui.

**Acceptance Scenarios**:

1. **Given** a revisão da digitalização, **When** o leitor marca "Guardar a foto com o estudo para conferência",
   **Then** a foto otimizada e cifrada fica vinculada ao estudo salvo, com a data de expiração exibida.
2. **Given** a opção desmarcada, **When** o leitor salva, **Then** a foto é apagada como hoje (promessa da 086
   mantida).
3. **Given** um estudo com foto, **When** o leitor o abre, **Then** pode ver a folha original ao lado do texto no
   computador, ou numa aba no celular, com zoom.
4. **Given** uma foto apagada, de forma manual, em lote ou por expiração, **When** o leitor abre o estudo, **Then**
   título, Resumo, Explicação, Conceitos, Referências e notas estão exatamente como antes.

### User Story 4 — Retenção automática (Priority: P2) [fatia C]

Como leitor, quero que as fotos de conferência sejam apagadas sozinhas depois de um tempo ou quando eu concluir o
estudo, salvo as que eu marcar para manter.

**Acceptance Scenarios**:

1. **Given** uma foto com mais de 30 dias e não marcada, **When** o job roda, **Then** ela é apagada e o espaço é
   devolvido.
2. **Given** um estudo marcado como concluído há mais de 7 dias, **When** o job roda, **Then** as fotos dele são
   apagadas, salvo as marcadas "Manter permanentemente".
3. **Given** uma foto marcada "Manter permanentemente", **When** o job roda, **Then** ela nunca expira.
4. **Given** avatares e capas, **When** o job roda, **Then** eles nunca expiram.

### User Story 5 — Minhas Imagens e Espaço (Priority: P2) [fatia C]

Como leitor, quero ver todas as imagens que ocupam minha cota e liberar espaço rapidamente.

**Acceptance Scenarios**:

1. **Given** a tela "Minhas Imagens e Espaço", **When** o leitor a abre, **Then** vê:
   - "Seu espaço: X MB de 1 GB utilizados (N imagens)" e "Capacidade geral do servidor: Y GB de 900 GB";
   - uma grade com miniatura, livro e estudo vinculados, data, dias até expirar (ou "Mantida permanentemente") e
     tamanho.
2. **Given** a tela, **When** o leitor escolhe "Apagar fotos de estudos concluídos" ou "Apagar fotos com mais de 30
   dias", **Then** vê antes quantas fotos e quantos MB serão apagados, confirma, e a cota é atualizada na hora.
3. **Given** uma imagem, **When** o leitor a apaga, marca para manter ou abre o estudo vinculado, **Then** a ação
   acontece sem sair da tela.

### User Story 6 — Cotas por usuário e do servidor (Priority: P2) [fatia C]

**Acceptance Scenarios**:

1. **Given** um usuário com 1 GB usado, **When** tenta guardar outra imagem, **Then** a gravação é recusada com a
   indicação de quanto ocupa e um atalho para "Minhas Imagens e Espaço". A digitalização ainda lê o texto; só não
   guarda a foto.
2. **Given** o servidor com 900 GB usados ou com menos espaço livre real que a margem, **When** qualquer usuário
   tenta gravar, **Then** a gravação é recusada com aviso.
3. **Given** a cota perto do fim (≥ 85 %), **When** o leitor vê a barra, **Then** o estado "Quase cheio" aparece
   com texto, não só cor.

### User Story 7 — Padrão visual (Priority: P3)

Telas novas e alteradas seguem o Roadmap 0.9:
- tokens semânticos dos 10 temas, contraste AA e imunidade cromática;
- zero emojis, alvos ≥ 44 px, foco visível;
- 320 px e uso completo por teclado.

---

## 3. Edge Cases

- **HD desconectado durante o uso:** a gravação de mídia falha com aviso e as leituras de imagem respondem
  "indisponível". O banco no HD exige o disco. Se ele cair durante o uso, o servidor para com erro claro e nenhum
  dado é gravado em outro lugar.
- **Chave mestra perdida:** imagens irrecuperáveis sem o código de recuperação. O app explica e oferece apagar as
  entradas para liberar a cota.
- **Arquivo `.enc` adulterado ou corrompido:** a tag GCM falha e a imagem aparece como "Arquivo danificado", com a
  opção de apagar.
- **Estudo apagado (lixeira) com foto:** a foto fica até a purga do estudo e é apagada 7 dias depois.
- **Exclusão de conta:** todas as imagens do usuário são apagadas antes da conta.
- **Exportação de conta:** as imagens vão decifradas no ZIP do usuário (portabilidade).
- **Backup restaurado com outra chave:** banco e cofre voltam, mas as imagens só abrem com a chave original.
- **Duas gravações simultâneas no limite da cota:** só a que cabe passa (verificação atômica).

---

## 4. Requirements *(mandatory)*

### Functional Requirements

- **FR-001** (A): `LEITORUM_STORAGE_ROOT` DEVE definir a raiz única (`db/`, `backups/`, `vault/`), com
  compatibilidade e precedência das variáveis `CADERNO_*` existentes.
- **FR-002** (A): Com a raiz configurada, o app DEVE iniciar só se a raiz tiver o marcador e o mesmo `storage_id`
  do banco. Senão, para com mensagem clara e **sem criar nada**.
- **FR-003** (A): O script `scripts/migrate_storage_to_hd.py` DEVE seguir o contrato de migração:
  - origem só para leitura;
  - API de backup;
  - integridade completa, SHA-256 lógico e de cada arquivo;
  - troca do `.env` por último;
  - rollback pela origem intacta.
- **FR-004** (B): Toda imagem de usuário DEVE ser gravada só como `.enc` (formato v1 de research R2), depois de
  remover metadados e otimizar em WebP.
- **FR-005** (B): A chave mestra DEVE ficar fora do HD (DPAPI ou `.env` do sistema). O app DEVE recusar uma chave
  dentro da raiz de armazenamento e DEVE oferecer código de recuperação.
- **FR-006** (B): As imagens DEVEM ser servidas só por endpoint autenticado, com a regra de acesso por tipo e
  `Cache-Control: private, no-store, no-cache`.
- **FR-007** (B): Backup e restauração DEVEM incluir o cofre cifrado e conferir a impressão digital da chave. A
  chave nunca vai no pacote.
- **FR-008** (C): A digitalização DEVE oferecer guardar a foto otimizada e cifrada, vinculada ao estudo salvo.
- **FR-009** (C): Apagar uma imagem NUNCA PODE alterar ou apagar o estudo ou seus textos.
- **FR-010** (C): A retenção DEVE apagar fotos de conferência:
  - por idade (padrão 30 dias);
  - depois da conclusão do estudo (com espera de 7 dias);
  - quando ficam sem vínculo.

  Fotos marcadas "Manter permanentemente" ficam de fora. O job roda na partida e a cada 6 h.
- **FR-011** (C): A tela "Minhas Imagens e Espaço" e o visualizador "Folha original" no estudo DEVEM existir, com
  apagamento individual e em lote com prévia.
- **FR-012** (C): As cotas por usuário (1 GiB) e global (900 GiB), mais o espaço livre real, DEVEM ser verificadas
  atomicamente antes de cada gravação.

### Non-Functional & Governance Restrictions

- **NR-001**: Nenhuma mudança no banco ativo sem o snapshot pré-migração verificado. O script de migração é
  validado inteiro em `tmp_path` antes de rodar no ambiente real, e roda só com o servidor parado.
- **NR-002**: Testes só com imagens e textos fictícios, bancos descartáveis e chave de teste. Nenhum teste toca
  `backend/data/caderno.db` nem o HD real.
- **NR-003**: Chave, nonces e conteúdo de imagens nunca em logs, relatórios ou respostas de erro.
- **NR-004**: Sem pacote novo além de declarar `cryptography` (já instalado) como dependência direta. DPAPI via
  `ctypes`.
- **NR-005**: Design do Roadmap 0.9 (US7).
- **NR-006**: O cofre cifra **imagens**. O banco no HD (textos dos estudos) não é cifrado por esta feature. A
  recomendação é ativar o BitLocker na unidade, o que o usuário faz no Windows, não o app.

---

## 5. Success Criteria *(mandatory)*

- **SC-001**: Em `tmp_path`, 100 % das falhas injetadas na migração terminam sem troca de caminho e com a origem
  byte a byte igual.
- **SC-002**: Zero arquivos com assinatura de imagem (JPEG, PNG, WebP) sob a raiz e nas pastas do servidor depois
  da importação para o cofre, conferido por varredura nos testes.
- **SC-003**: Zero metadados EXIF, GPS ou XMP nas imagens servidas, conferido com uma imagem fictícia com GPS
  falso.
- **SC-004**: Páginas de caderno otimizadas com mediana ≤ 450 KB para fotos de 12 MP. O texto lido pelo motor na
  imagem otimizada fica com no máximo 2 pontos de CER a mais que na original, em páginas fictícias.
- **SC-005**: Apagar imagens (uma, em lote ou por expiração) deixa 100 % dos estudos vinculados idênticos.
- **SC-006**: Nenhuma gravação ultrapassa a cota do usuário, a cota global ou a margem de espaço livre, inclusive
  com gravações concorrentes simuladas.
- **SC-007**: Decifrar e servir uma página leva p95 ≤ 150 ms; uma miniatura, p95 ≤ 80 ms.
- **SC-008**: `pytest`, `npm test` e `npm run build` aprovados em cada fatia.

---

## 6. Decisões do usuário (Clarifications, 2026-10-27: "aprovado com as recomendações")

- **Q1:** foto de conferência por escolha do leitor, com a caixa **desmarcada** por padrão.
- **Q2:** avatares e capas seguem as **regras de visibilidade atuais**, com login obrigatório. Páginas de caderno:
  só o dono.
- **Q3:** chave mestra por **DPAPI** no disco do sistema, mais o **código de recuperação** mostrado uma vez.
- **Q4:** retenção de 30 dias **e** 7 dias depois de "concluído". "Manter permanentemente" fica fora das duas.
- **Q5:** ordem das fatias **A → B → C**, cada uma com o próprio ciclo de tarefas e commit.
- **Q6:** segunda cópia de backup ativada (`LEITORUM_SECONDARY_BACKUP_DIR`) **fora do HD**.
