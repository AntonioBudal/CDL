# Especificação da Fatia 090-C: Fotos de Conferência, Retenção, "Minhas Imagens e Espaço" e Cotas

**Feature**: `090-armazenamento-hd-cofre-cotas`, fatia C | **Created**: 2026-10-28

**Status**: Concluída em 2026-10-28 (aprovada com as recomendações C-Q1 a C-Q4, §7); plano em
[plan-C.md](plan-C.md) e tarefas em [tasks-C.md](tasks-C.md).

**Base**:
- [spec.md](spec.md): US3 a US7, FR-008 a FR-012, SC-004 a SC-006 e decisões Q1 e Q4;
- [plan.md](plan.md): desenho das telas;
- [contracts/media-api.contract.md](contracts/media-api.contract.md).

Este documento não substitui a especificação aprovada. Ele a detalha para a fatia C, confrontando-a com o código
depois das fatias A e B, e registra o que mudou desde então.

---

## 1. Ponto de partida (auditoria do código em 2026-10-28)

### O que a fatia B já entregou e a C reaproveita
- **Cofre:** `media_service.store()`, `read()`, `read_thumbnail()` e `delete()` em duas fases.
- **Miniaturas:** a miniatura cifrada `<id>.thumb.enc` é gravada junto da imagem. Por isso não é gerada na hora,
  como previa a pesquisa R5.
- **Tabela `encrypted_media`:** já tem `study_id`, `keep_forever`, `expires_at` e `pending_until`, e os índices do
  job.
- **Rotas:**
  - `GET /api/media` (lista simples por `offset`, com filtro de tipo);
  - `GET /api/media/{id}/content` e `GET /api/media/{id}/thumbnail`;
  - `DELETE /api/media/{id}`, que limpa a referência da capa ou do avatar.
- **Preparação da página:** `prepare_page()` (2000 px, WebP, sem metadados) existe, mas ainda não é chamada por
  nenhuma rota.

### O que falta, e muda a especificação
1. **Nenhuma cota é verificada.** `store()` grava sem somar o uso, sem a cota global e sem o espaço livre real.
2. **O estudo não guarda quando foi concluído.** `studies.reading_status` vale `rascunho`, `em_estudo`, `revisado`
   ou `concluido`, mas não há data da mudança. A regra "concluído há mais de 7 dias" (Q4) precisa dessa data
   (decisão C-Q2).
3. **A digitalização decide tarde.** A caixa "Guardar a foto" fica na revisão, depois da leitura. Mas a foto só
   chega ao servidor no `POST /api/digitize/preview`, que a apaga ao terminar (promessa da 086). O contrato
   previa `keep_photo` já no envio, antes de o leitor ver o texto (decisão C-Q1).
4. **Uma foto gera um estudo.** `useDigitizeDraft` envia uma foto e salva um estudo. A "Folha original" quase
   sempre terá uma imagem. O visualizador suporta várias, mas anexar fotos a um estudo existente fica fora desta
   fatia.
5. **Lista sem contexto.** `GET /api/media` não devolve título do estudo, livro, `days_left`, ordenação nem
   filtro por livro, que a tela precisa.
6. **Não há job.** Nada apaga fotos vencidas, `pending` antigas, órfãs ou `.tmp`, nem marca `missing`.
7. **Existe papel de administrador** (`users.role = 'admin'`, `require_admin`). Isso abre a decisão C-Q4 sobre
   quem vê a capacidade do servidor.

---

## 2. Histórias (refinadas)

### US3 — Guardar a foto da página para conferência (P1)

1. **Given** a revisão da digitalização, **When** o leitor marca "Guardar a foto com o estudo para conferência
   (apagada automaticamente em 30 dias)" e salva, **Then**:
   - o estudo é criado como hoje;
   - a foto vai para o cofre otimizada, cifrada e vinculada ao estudo;
   - a tela confirma: "Foto guardada até 27/11/2026".
2. **Given** a caixa desmarcada (padrão, Q1), **When** o leitor salva, **Then** nada é guardado e a promessa da
   086 continua valendo.
3. **Given** o estudo salvo e a foto recusada (cota cheia, cofre trancado, HD indisponível), **When** a gravação
   da foto falha, **Then** o estudo **continua salvo** e o leitor vê o motivo, com o atalho para "Minhas Imagens e
   Espaço".
4. **Given** um estudo com foto, **When** o leitor o abre, **Then**:
   - aparece o botão "Folha original (1)";
   - no computador, a foto fica ao lado do texto, com divisória ajustável;
   - no celular, as abas são "Texto | Folha original";
   - há zoom e ajuste à largura.
5. **Given** uma foto apagada, de forma manual, em lote ou por expiração, **When** o estudo é aberto, **Then**:
   - título, Resumo, Explicação, Conceitos, Referências, notas e `version` estão idênticos;
   - o botão some.

### US4 — Retenção automática (P2)

1. **Expiração por idade:** a foto de página não mantida expira 30 dias depois de vinculada.
2. **Estudo concluído:** se o estudo passa a `concluido`, as fotos não mantidas são apagadas 7 dias depois.
   - Se o estudo deixar de estar concluído antes disso, a contagem é cancelada.
   - Quando o estudo voltar a `concluido`, a contagem começa de novo.
3. **Manter permanentemente:** a foto marcada não expira por nenhuma das duas regras. Desmarcar recalcula a
   validade: agora mais 30 dias.
4. **Avatares e capas** nunca expiram.
5. **Sem vínculo:**
   - foto `pending` há mais de 24 h é apagada;
   - foto com `study_id` nulo, porque o estudo foi purgado da lixeira, é apagada 7 dias depois.
6. **Estudo na lixeira:** a foto continua (o estudo pode voltar). A tela a mostra como "Estudo na lixeira". Ela
   segue sujeita à expiração por idade.

### US5 — Minhas Imagens e Espaço (P2)

1. **Abertura** (`/minhas-imagens`, pelo menu do usuário e por Ajustes): o leitor vê:
   - o medidor "Seu espaço: X MB de 1 GB utilizados (N imagens)";
   - a capacidade do servidor, conforme a decisão C-Q4;
   - a grade com miniatura, tipo, livro e estudo, data, validade ("expira em N dias", "Mantida permanentemente" ou
     "Não expira") e tamanho.
2. **Ações em lote:** "Apagar fotos de estudos concluídos" e "Apagar fotos com mais de 30 dias" mostram antes
   quantas fotos e quantos MB (`dry_run`). Pedem confirmação em diálogo e atualizam o medidor na hora.
3. **Ações por imagem**, sem sair da tela:
   - Ver;
   - Manter permanentemente, só para páginas;
   - Abrir o estudo;
   - Apagar. Para capa e avatar, avisa que o livro fica sem capa ou o perfil fica sem foto.
4. **Seleção:** caixa de seleção por cartão e "Apagar selecionadas (N)".
5. **Arquivo indisponível:** imagem `missing` ou danificada aparece como cartão "Arquivo indisponível", com
   "Apagar".
6. **Cofre trancado:** a tela explica o motivo e mostra o caminho para restaurar a chave (`instalar.py --media-key
   --restore`), sem listar nada quebrado.

### US6 — Cotas (P2)

1. **Cota do usuário:** a gravação que ultrapassaria 1 GiB é recusada com `507 user_quota`, o uso atual e o
   atalho. Vale para página, capa e avatar.
2. **Cota do servidor:** a gravação que ultrapassaria 900 GiB, ou deixaria menos de 2 GiB livres no HD, é
   recusada com `507 server_quota`.
3. **Concorrência:** duas gravações simultâneas no limite: só a que cabe passa.
4. **Quase cheio:** a partir de 85 %, o medidor mostra "Quase cheio" em texto e ícone. A 100 %, mostra "Cheio",
   e a caixa da digitalização fica desativada com o motivo.

### US7 — Padrão visual (P3)

Sem mudança: tokens dos 10 temas, contraste AA, zero emojis, alvos de 44 px, foco visível, 320 px, teclado, e
hachura no medidor do tema E-Ink.

---

## 3. Requisitos funcionais da fatia

| ID | Requisito | Origem |
| :--- | :--- | :--- |
| FR-C01 | A foto guardada DEVE ser a versão otimizada (`prepare_page`), cifrada, com miniatura, vinculada ao estudo salvo e com `expires_at = vínculo + 30 dias` | FR-008 |
| FR-C02 | Sem a escolha explícita do leitor, nenhuma foto de página DEVE ser guardada | Q1, 086 |
| FR-C03 | Falhar ao guardar a foto NUNCA PODE desfazer ou alterar o estudo salvo | FR-009 |
| FR-C04 | Apagar uma foto, em qualquer caminho, NUNCA PODE alterar uma coluna de `studies` nem as versões do estudo | FR-009, SC-005 |
| FR-C05 | O job de retenção DEVE rodar na partida e a cada 6 h, em lotes de 200, só com contagens e bytes no log, aplicando as regras da US4 | FR-010 |
| FR-C06 | O job DEVE reconciliar o cofre: `.tmp` com mais de 1 h, arquivos sem linha, linhas `deleting` pendentes e arquivos sumidos (linha `missing`) | research R6 |
| FR-C07 | Toda gravação no cofre DEVE verificar, de forma atômica no processo, a cota do usuário, a cota global e o espaço livre real antes de gravar | FR-012 |
| FR-C08 | `GET /api/media/usage` DEVE devolver o uso, a cota, o nível (`normal`, `high` ou `full`) e o estado do cofre | contrato |
| FR-C09 | `GET /api/media` DEVE devolver livro, estudo (título, estado, se está na lixeira) e `days_left`, com filtro por tipo e livro e ordenação por data, tamanho e validade | FR-011 |
| FR-C10 | `PATCH /api/media/{id}` (`keep_forever`) e `POST /api/media/bulk-delete` (filtros com `dry_run` e lista de ids) DEVEM existir, só para páginas do próprio usuário | contrato |
| FR-C11 | `GET /api/studies/{id}/media` DEVE listar as fotos do estudo, só para o dono | contrato |
| FR-C12 | As telas "Minhas Imagens e Espaço" e "Folha original", e a caixa na digitalização, DEVEM seguir o desenho do plan.md | FR-011 |
| FR-C13 | As configurações de cota e retenção DEVEM vir do `.env` (data-model §5) e ser validadas na partida; valor inválido impede a partida com mensagem clara | data-model |

---

## 4. Casos de borda

- **Duas abas salvando:** a foto é vinculada a um único estudo.
- **Estudo restaurado da lixeira:** a foto continua vinculada.
- **Estudo purgado:** `study_id` fica nulo (`ON DELETE SET NULL`), e a foto vai embora 7 dias depois.
- **HD cai durante o job:** o job interrompe o lote, registra só a contagem e tenta de novo na próxima rodada.
  Nenhuma linha é apagada sem o arquivo ter sido removido.
- **Relógio do Windows ajustado para trás:** nenhuma foto expira antes do prazo, porque as datas comparadas são do
  próprio banco, em UTC.
- **Cota reduzida no `.env` abaixo do uso atual:** nada é apagado. Só novas gravações são recusadas, e o medidor
  mostra "Cheio".
- **Exportação e exclusão de conta:** já tratam o cofre desde a fatia B; as fotos de página entram sem mudança.
- **Backup restaurado:** as datas de expiração voltam como estavam. O job apaga o que já venceu na rodada seguinte.

---

## 5. Critérios de sucesso da fatia

- **SC-004:**
  - mediana de tamanho ≤ 450 KB, em fotos fictícias de 12 MP;
  - CER do motor na imagem otimizada no máximo 2 pontos acima da original, em páginas fictícias.
- **SC-005:** apagar fotos (uma, em lote ou por expiração) deixa 100 % dos estudos vinculados idênticos,
  conferido campo a campo, inclusive `version` e `updated_at`.
- **SC-006:** nenhuma gravação passa da cota do usuário, da cota global ou da margem, com 20 gravações concorrentes
  simuladas e `disk_usage` simulado.
- **SC-009** (novo): o job, com relógio injetável, apaga exatamente o que as regras da US4 mandam em cada cenário,
  e nada mais.
- **SC-010** (novo): a tela "Minhas Imagens e Espaço" e o visualizador passam pela conferência visual do usuário
  nos 10 temas, em 320 px e no teclado.
- **SC-008:** `pytest`, `npm test` e `npm run build` aprovados.

---

## 6. Fora do escopo desta fatia

- Anexar fotos a um estudo que já existe, ou várias fotos num estudo pela digitalização.
- Cifrar o banco (NR-006: a recomendação continua sendo o BitLocker).
- Cotas diferentes por usuário. A cota é uma só, configurada no `.env`.
- Trocar a chave mestra (`key_epoch` continua 0).

---

## 7. Decisões (Clarify; 2026-10-28: "aprovado com as recomendações")

**Escolhidas:** C-Q1 A, C-Q2 A, C-Q3 "não" e C-Q4 recomendada.

### C-Q1 — Quando a foto chega ao servidor para ser guardada?

| Opção | Como funciona | Prós e contras |
| :--- | :--- | :--- |
| **A (recomendada)** | Ao salvar com a caixa marcada, o navegador reenvia a mesma foto (ainda em memória) para `POST /api/studies/{id}/media`, logo depois de criar o estudo. Sem estado `pending` para fotos de página | A caixa fica na revisão, como desenhado, e a leitura continua sem guardar nada. **Contra:** a foto sobe duas vezes (até 20 MB no celular) |
| B | A caixa fica antes do envio. Com ela marcada, a leitura já guarda uma cópia `pending` por 24 h, vinculada no salvamento | Um envio só. **Contra:** o leitor decide antes de ver o resultado, e uma foto ruim fica guardada até expirar |

### C-Q2 — Como saber há quanto tempo o estudo está concluído?

| Opção | Como funciona | Prós e contras |
| :--- | :--- | :--- |
| **A (recomendada)** | Coluna nova `encrypted_media.completed_seen_at`. O job a preenche quando vê o estudo `concluido` e a limpa se o estado mudar. A foto é apagada 7 dias depois dessa data | Não toca em `studies`. A precisão é de até 6 h, a cadência do job. Migração `0032` só na tabela do cofre |
| B | Coluna nova `studies.completed_at`, gravada em toda mudança de `reading_status` | Data exata e útil para outras telas. **Contra:** mexe na tabela de estudos e em todos os caminhos que mudam o estado |

### C-Q3 — A ação "Apagar fotos de estudos concluídos" respeita os 7 dias?

- **Recomendado: não.** É uma ação manual, com prévia e confirmação. Os 7 dias protegem só a expiração
  automática.
- **Alternativa:** só conta estudos concluídos há mais de 7 dias.

### C-Q4 — Quem vê a capacidade geral do servidor?

- **Recomendado:** o administrador vê "Y GB de 900 GB" e o espaço livre do HD. Os demais usuários veem só o
  estado ("Servidor: Normal", "Quase cheio" ou "Cheio"). Assim, ninguém deduz quanto os outros usuários guardam.
- **Alternativa:** todos veem os números, como na especificação original.
