# Feature Specification: F0.12.07 — Círculos de leitura com trava anti-spoiler

**Feature Branch**: `120-circulos-de-leitura`

**Created**: 2026-11-15

**Status**: Concluída

**Input**: Item "Círculos de leitura com trava anti-spoiler" do `docs/contexto/ROADMAP-0.12.md`. Sétima feature do 0.12.
**Com migração** (`0042`, só tabelas novas).

---

## 1. Contexto (auditoria de 2026-11-15)

| Ponto | Situação | Onde |
|---|---|---|
| Amizades e bloqueio | Prontos: amigos, pedidos, bloqueio bilateral | `services/friendship_service.py` |
| Leituras em comum | Casa livros de dois leitores por ISBN ou título + sobrenome do autor | `services/in_common_service.py` |
| Livros | Cada leitor tem a **própria cópia** do livro, com capítulos **com nomes próprios**; estado de leitura (F0.11.01) e ISBN (F0.11.04) | `models/book.py`, `chapter.py` |
| Notificações | Tipos fixos por restrição no banco (`friend_request`, `friend_accepted`, `study_shared`, `system_alert`) | `models/notification.py` |

**Consequência para a trava:** os capítulos de dois leitores não se comparam (cada um nomeia os seus). Então o círculo
tem **partes próprias**, iguais para todos os membros, e cada membro diz em que parte está. A trava usa essas partes.

---

## 2. User Stories

### US1 — Criar um círculo e convidar amigos (P1)

**Acceptance**:
1. Nova página **"Círculos"** (`/circulos`, no menu "Mais"). "Novo círculo" pede **um livro meu**; o círculo guarda
   título, autor e ISBN do livro e já vem com **as partes = os capítulos desse livro, na ordem** (editáveis depois).
   Também dá para começar pelo menu do livro ("Criar círculo deste livro").
2. Quem criou (dono) **convida amigos** (só amigos; nunca alguém bloqueado), até **20 membros**.
3. O convidado vê o convite **na página Círculos**, com um contador no item do menu; aceita ou recusa.
4. Ao entrar, se o convidado tem o mesmo livro (ISBN, ou título + sobrenome do autor, como em "Leituras em comum"),
   aparece o atalho **"Abrir meu exemplar"**.

### US2 — Progresso e trava anti-spoiler (P1)

**Acceptance**:
1. Cada membro marca **"Estou na parte…"** (ou "Ainda não comecei" / "Terminei"). O progresso de todos aparece em
   barras na página do círculo.
2. A conversa é **por parte**. As mensagens de uma parte **só chegam a quem já está nela ou adiante**: para os outros,
   o servidor **não manda o texto**, só "3 mensagens nesta parte — avance seu progresso para ler".
3. Só dá para escrever em partes **até a minha**. Mensagens: texto simples (até 4 000 caracteres, quebras de linha),
   editar e apagar as próprias; o dono pode apagar qualquer uma (moderação).
4. Voltar o progresso tranca de novo as partes à frente (nada é "desbloqueado para sempre").

### US3 — Manter o círculo (P2)

**Acceptance**:
1. Dono: renomear o círculo; **renomear partes e acrescentar no fim**; apagar uma parte do fim só se ela não tiver
   mensagens; tirar um membro; apagar o círculo (com confirmação).
2. Membro: sair do círculo (as mensagens dele ficam, com o nome).
3. Bloqueio: se dois membros se bloqueiam, **cada um deixa de ver as mensagens do outro**; nenhum dos dois pode
   convidar o outro.

### Edge Cases

- Convidar quem não é amigo, já é membro ou já tem convite pendente: recusado com mensagem clara.
- Quem não é membro (nem convidado) recebe 404 em tudo do círculo.
- Livro de origem apagado ou na lixeira: o círculo continua (guardou título, autor e ISBN).
- Até 100 partes por círculo; até 50 círculos por leitor.
- Dono não pode sair sem apagar o círculo (no 0.12 não há troca de dono).

---

## 3. Requirements

- **FR-001**: Migração `0042`: tabelas `reading_circles` (dono, nome, título, autor, ISBN, livro de origem
  anulável), `reading_circle_parts` (posição, nome), `reading_circle_members` (papel `owner`/`member`, situação
  `invited`/`active`, progresso = posição da parte atual, 0 = não comecei, N+1 = terminei) e `reading_circle_posts`
  (parte, autor, texto, criada/editada).
- **FR-002**: `services/reading_circle_service.py`: criar, convidar, aceitar/recusar, progresso, partes, mensagens com a
  trava aplicada **no servidor**, bloqueio, sair/remover/apagar; casamento do exemplar com as funções de
  `in_common_service`.
- **FR-003**: `routers/reading_circles.py` (`/api/circles…`), rotas registradas nos contratos de rota.
- **FR-004**: Frontend: `CirclesView.vue` (`/circulos`: meus círculos, convites, novo círculo), `CircleView.vue`
  (`/circulos/:id`: progresso, partes e conversa com a trava, membros, gestão); item no menu "Mais" com contador de
  convites; "Criar círculo deste livro" no menu do livro.
- **FR-005**: Versão `0.12.0-alpha.7` e F0.12.07 marcada na linha do tempo.

## 4. Success Criteria

- **SC-001**: Testes: só amigos são convidados; bloqueio; limites; aceitar/recusar; quem não é membro recebe 404; a
  **trava não deixa vazar texto** (resposta da API sem o corpo de mensagens à frente, só a contagem); escrever à frente
  é recusado; voltar o progresso tranca de novo; moderação do dono; partes (renomear, acrescentar, apagar só sem
  mensagens); sair/remover/apagar; casamento do exemplar; migração sobe e desce em banco descartável.
- **SC-002**: Navegador com dois leitores fictícios: criar, convidar, aceitar, escrever, conferir a trava dos dois
  lados; 375 px; contraste nos 10 temas.
- **SC-003**: Testes novos e vizinhos; build; versão `alpha.7`; commit; levar ao `main`. A migração no banco ativo fica
  para o procedimento dos 4 comandos.

## 5. Fora do escopo

- **Aviso no sininho** de notificações: os tipos estão travados por uma restrição no banco e mudar exige recriar a
  tabela de notificações (com os dados do usuário). O convite aparece na página Círculos e no contador do menu.
- Círculos públicos ou com quem não é amigo; troca de dono; reações, respostas encadeadas e menções.
- Progresso automático pelos estudos ou pelo estado de leitura; reordenar partes depois de criadas.
- Levar estudos ou destaques para dentro do círculo.
