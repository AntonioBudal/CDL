# Feature Specification: F0.10.03 — Painel de Sistema: Segurança, Backups e Soberania dos Dados

**Feature Branch**: `095-painel-sistema-soberania`

**Created**: 2026-11-03

**Status**: Concluída em 2026-11-03.

**Input**: Feature 07 do plano mestre (Ajustes → aba Sistema: "Painel de Segurança, Backups e Soberania de Dados",
com exportação `.zip`, integridade do SQLite e hash do build) e a seção 2.2 ("hash do commit na aba Sistema").
Depende da F0.10.02 (as proteções que o painel descreve já existem).

---

## 1. Contexto (auditoria de 2026-11-03)

| Item | Hoje | Onde |
|---|---|---|
| Versão do servidor | Só `__version__` (`0.x`) em `/api/health`, mostrada no card "Status da Conexão Local" | `routers/health.py`, `views/SettingsView.vue` (l. ~944) |
| Hash do build | Não existe, nem no servidor nem na interface | — |
| Revisão do banco | Não aparece em lugar nenhum | `alembic_version` |
| Integridade do SQLite | Existe `verify_sqlite_integrity()` (`quick_check` + `foreign_key_check`), usada só em backups e restauração | `services/backups.py` |
| Backups automáticos | Existem (`LEITORUM_AUTO_BACKUP_HOURS`, padrão 24 h; `..._KEEP`, padrão 14; segunda cópia opcional), mas a tela não diz quando foi o último | `services/maintenance.py` |
| Backup manual (.db/.zip) e restauração | Componente `DatabaseBackup` na aba Sistema, **visível para todos**, mas a API só aceita administrador (`AdminUser`): quem não é admin vê botões que dão 403 | `components/DatabaseBackup.vue`, `routers/backups.py` |
| Exportação do leitor (.zip) | Existe na aba Conta | `views/SettingsView.vue` (l. ~1062), `routers/account.py` |
| O que a exclusão apaga | Nenhum texto explica (`secure_delete`, checkpoint do WAL, backups antigos) | — |

**Motivação concreta:** em 2026-11-02 a interface nova chamou uma rota que o servidor antigo não tinha (405 ao
excluir capítulo), porque o serviço não tinha sido reiniciado depois do build. Mostrar o commit do servidor e o da
interface lado a lado, com aviso quando divergem, teria dito isso na hora.

---

## 2. User Stories

### US1 — Saber que versão está rodando (P1)

Como leitor, quero ver a versão e o commit do servidor e da interface, e ser avisado quando não batem.

**Acceptance**:
1. A aba Sistema mostra "Servidor: v0.x · `abc1234`" e "Interface: `abc1234`".
2. Se os commits forem diferentes, aparece um aviso: "O servidor está rodando uma versão diferente da interface.
   Reinicie o serviço Leitorum." Se algum lado não souber o commit (ex.: instalação sem `.git`), mostra
   "desconhecido" e não acusa divergência.
3. A revisão do banco aparece ("Banco: `0033_organizer_feedback`"); se for diferente da última migração do código,
   avisa: "O banco está numa revisão diferente da esperada (`X`). Faça um backup e rode as migrações."

### US2 — Conferir a saúde do banco (P1, administrador)

Como administrador, quero verificar a integridade do banco com um clique.

**Acceptance**:
1. Botão "Verificar integridade" roda `quick_check` e `foreign_key_check` (somente leitura) e mostra "Banco íntegro"
   ou a falha, com data e hora da verificação.
2. Quem não é administrador não vê o botão; a API responde 403.

### US3 — Saber se os backups estão em dia (P1, administrador)

**Acceptance**:
1. Mostra: backups automáticos ligados ou desligados, intervalo, quantos são guardados, data do último e quantos
   existem, e se a segunda cópia (fora do disco principal) está configurada. Nunca mostra caminhos de pasta.
2. Se o último backup automático tiver mais que o dobro do intervalo, aparece um aviso.
3. O componente de backup manual e restauração (`DatabaseBackup`) só aparece para administradores.

### US4 — Entender o que acontece com os meus dados (P1)

**Acceptance**: um bloco "Seus dados e a exclusão" explica, em linguagem simples e só com o que o código faz:
- os dados ficam no banco SQLite deste servidor;
- a exportação completa (`.zip` com Markdown, JSON e imagens) está na aba Conta (com link);
- excluir permanentemente zera o conteúdo no arquivo do banco (`secure_delete`) e no registro de transações (WAL);
- cópias de backup feitas antes da exclusão guardam o conteúdo até serem substituídas (com o número configurado,
  ex.: "os 14 backups automáticos mais recentes");
- proteções ativas: nenhum domínio externo na política de segurança (ou só o do login com Google, quando ativo),
  pedidos de outros sites recusados, áreas privadas fora dos buscadores, e link para `/.well-known/security.txt`.

### Edge Cases

- **Sem `.git`** (cópia do código sem repositório) ou commit não legível: "desconhecido", sem aviso.
- **`LEITORUM_BUILD_COMMIT`** definido: tem prioridade (útil para instalações sem `.git`).
- **Verificação de integridade com o banco em uso:** é somente leitura e não bloqueia escritas (`mode=ro`).
- **Backups automáticos desligados** (`LEITORUM_AUTO_BACKUP_HOURS=0`): aparece "desligados", com aviso.
- **Pasta de backups inexistente:** "nenhum backup automático ainda".

---

## 3. Requirements

- **FR-001**: `GET /api/system/status` (autenticado): versão, commit do servidor (curto, 7 caracteres), revisão do
  banco, revisão esperada (última migração do código), `google_auth_enabled`, `secure_delete` ativo; para
  administrador, também o bloco de backups (US3). Sem caminhos de arquivo nem dados do acervo.
- **FR-002**: `POST /api/system/integrity-check` (só administrador): `{ ok, detail, checked_at }`, usando
  `verify_sqlite_integrity()` sobre o banco ativo, somente leitura.
- **FR-003**: Commit do servidor lido de `LEITORUM_BUILD_COMMIT` ou do `.git` do repositório (`HEAD` → ref solta ou
  `packed-refs`), sem processo externo; resultado em cache.
- **FR-004**: Commit da interface embutido no build (`__BUILD_COMMIT__` via `define` do Vite, lido com
  `git rev-parse --short HEAD`; "desconhecido" se falhar).
- **FR-005**: Na aba Sistema, card novo "Versão, segurança e soberania" com US1 a US4; o card "Status da Conexão
  Local" passa a mostrar o commit ao lado da versão.
- **FR-006**: `DatabaseBackup` só para administradores.
- **FR-007**: Textos do painel só afirmam o que o código faz (verificado na F0.10.02); nenhuma promessa absoluta.
- **FR-008**: Só tokens de cor; contraste ≥ 4,5:1 nos 10 temas para os textos e avisos novos.
- **FR-009**: Sem migração; o banco ativo nunca é escrito pela verificação.

## 4. Success Criteria

- **SC-001**: Testes de backend: status sem e com admin (bloco de backups só para admin), commit por variável e por
  `.git` fictício em `tmp_path` (ref solta e `packed-refs`), revisão do banco e esperada, integridade ok e com banco
  corrompido fictício, 403 para não admin.
- **SC-002**: Teste de frontend: card novo, aviso de divergência, `DatabaseBackup` com `v-if` de admin, `define`
  do Vite.
- **SC-003**: Navegador (banco fictício): painel em 1366 e 375 px; aviso aparece quando o commit do servidor é
  forçado diferente (`LEITORUM_BUILD_COMMIT`); verificação de integridade funciona.
- **SC-004**: 4ª feature do lote de 5: `npm run build` e os testes novos.

## 5. Fora do escopo

- Redesenho da navegação de Ajustes (já é vertical desde a F0.8.07).
- Agendar ou disparar backups pela tela, ou restaurar backups automáticos pela tela.
- Mostrar o hash na landing ou no rodapé (vai com a seção de confiança da F0.10.08, se você quiser).
