# HANDOFF — Leitorum (leia primeiro)

**Atualizado em:** 2026-11-09, no fecho do lote 1 do 0.11 (conversa em worktree, levada ao `main`).
**Para quem:** cada conversa nova de lote (0.10, 0.11, 1.0). Leia este arquivo, `AGENTS.md` e o roadmap do lote antes
de mexer em código. Ao encerrar, atualize este arquivo e `caderno-leitura-0.1/docs/contexto/RETOMADA.md`.

---

## 1. Onde estamos

- **Plano mestre** de 2026-11-01, renumerado para **0.10, 0.11 e 1.0** (os números 0.8 e 0.9 já eram roadmaps
  entregues). **Prazo combinado:** terminar os três até **15/11/2026**, cerca de 2 features por dia.
- **`main`** está em dia com o trabalho até 2026-11-07: o lote 2 do 0.10 foi levado ao `main` por fast-forward a
  cada feature. **Push pendente** (o usuário faz) e, depois dele, `Restart-Service -Name Leitorum`.
- **Roadmap 0.10 concluído.** **Roadmap 0.11:** lote 1 (F0.11.01 a .05) concluído e fechado em 2026-11-09 com as
  suítes completas. O banco ativo foi migrado pelo usuário até a **0039** em 2026-11-14 (snapshot validado
  `D:\Leitorum\backups\caderno-pre-migracao-20261115-004129.db`) e o serviço voltou a funcionar com o 0.11.

### Roadmap 0.10 (redesenho, segurança e ergonomia)

| Feature | Situação | Commit | Spec |
|---|---|---|---|
| F0.10.01 Header leve e variante neutra de botão (`.quiet`) | Concluída | `4a6759a` | `specs/092-header-leve-botao-neutro/` |
| F0.10.02 Endurecimento de segurança (CSP, origem, noindex, security.txt, `secure_delete`) | Concluída | `e06b925` | `specs/093-endurecimento-seguranca/` |
| F0.10.02.5 Capa, contraste e gerenciamento de capítulos (emergência) | Concluída | `2b69b80`, `9477f80` | `specs/094-correcoes-capa-capitulos/` |
| F0.10.03 Painel de Sistema (commit, revisão do banco, integridade, backups) | Concluída | `fdad9c4` | `specs/095-painel-sistema-soberania/` |
| F0.10.04 Revisão: baldes, sessões 5/10/15, gaveta de contexto | Concluída | `d410760` | `specs/096-revisao-baldes-sessao/` |
| F0.10.05 Destaques: cópia ABNT (NBR 10520:2023 e 6023), citação literal × texto do leitor | Concluída | `e6ad68f` | `specs/098-destaques-abnt-tipografia/` |
| F0.10.06 Importar: dados da obra na faixa, prévia da referência em 3 escopos (`referenceScopes.ts`) | Concluída | `da4a675` | `specs/099-importar-metadados-referencias/` |
| F0.10.07 Amigos: leituras e estudos em comum no perfil (`/api/users/{username}/in-common`) | Concluída | `d17ee7e` | `specs/100-amigos-em-comum/` |
| F0.10.08 Landing: Desafio F12 (endereços contatados e CSP ao vivo) e custo com fontes e datas | Concluída | `1ab3ae8` | `specs/101-landing-confianca-f12/` |
| F0.10.10 Correções reservadas (6 itens aprovados em 2026-11-07) | Concluída | `f7dbc58` | `specs/102-correcoes-reservadas-010/` |

Inbox e Lixeira do plano já estavam atendidas pelo código (auditoria de 2026-11-01); só conferir se surgir dúvida.
O **lote 1** (F0.10.01 a .04) fechou com as suítes completas em 2026-11-03. O **lote 2** (F0.10.05 a .10; não há
F0.10.09) fechou em 2026-11-07: `npm test` 749/749, `pytest` completo 788 aprovados e 4 pulados, build ok; a
única falha antiga (testes sensíveis a CRLF) foi corrigida em commit próprio (`0214933`).

### Roadmap 0.11 (motores)

| Feature | Situação | Spec |
|---|---|---|
| F0.11.01 Estados de leitura do livro (Quero ler, Lendo, Lido, Abandonado, datas) | Concluída (migração `0034`) | `specs/103-estados-leitura-livro/` |
| F0.11.02 Bandeja de triagem por capítulo (captura com capítulo, bandeja na página do livro) | Concluída (migração `0035`) | `specs/104-bandeja-triagem-capitulo/` |
| F0.11.03 Importar destaques do Kindle (`My Clippings.txt`) e do Kobo (`KoboReader.sqlite`) para a Mesa | Concluída (sem migração) | `specs/105-importar-kindle-kobo/` |
| F0.11.04 ISBN sob demanda (BrasilAPI → Open Library, pelo servidor), editora e local; referência ABNT completa | Concluída (migração `0036`) | `specs/106-isbn-sob-demanda/` |
| F0.11.05 Referências em 3 escopos: ABNT, APA, BibTeX e CSL-JSON (obra, trecho, obras citadas; bibliografia do acervo) | Concluída (sem migração) | `specs/107-referencias-tres-escopos/` |
| F0.11.06 Léxico de conceitos derivado das seções Conceitos; `[[conceito:Termo]]` no editor e na leitura | Concluída (sem migração) | `specs/108-lexico-conceitos/` |
| F0.11.07 Validador de paráfrase (Jaccard de trigramas no navegador, contra capturas e citações literais do livro) | Concluída (sem migração) | `specs/109-validador-parafrase/` |
| F0.11.08 Evolução da revisão: `difficulty_weight` e fila, cartões de conceito, conceitos frágeis, Memória do Dia | Concluída (migração `0037`) | `specs/110-evolucao-revisao/` |
| F0.11.09 Receptor: Readest pela API compatível com o Readwise (token de recepção); KOReader pelo JSON do exportador | Concluída (migração `0038`) | `specs/111-receptor-koreader-readest/` |
| F0.11.10 Recorte e giro da foto antes da leitura na digitalização | Concluída (sem migração) | `specs/112-recorte-foto-digitalizacao/` |
| F0.11.11 Cadernos de síntese com transclusão (`![[…]]` de estudo, seção e destaque; exportação; pacote da conta) | Concluída (migração `0039`) | `specs/113-cadernos-sintese/` |

Lote 1 do 0.11 fechado em 2026-11-09: `npm test` 774/774, `pytest` 825 aprovados e 4 pulados, build ok; correção da
chave estrangeira da 0035 em commit próprio (`fd2c5fc`).

Lote 2 do 0.11 (F0.11.06 a .10) fechado em 2026-11-12: `npm test` 796/796, `pytest` 854 aprovados e 4 pulados,
build ok; nenhuma falha de feature anterior.

Lote 3 do 0.11 (F0.11.11) fechado em 2026-11-14: `npm test` 799/799, `pytest` 858 aprovados e 4 pulados (depois
da correção abaixo), build ok. A suíte completa acusou 1 falha intermitente de feature anterior (086):
`test_client_disconnect_kills_engine_and_cleans` simulava a desconexão pela contagem de chamadas e, com a máquina
carregada, ela chegava antes de o motor falso subir; corrigido só no teste, em commit próprio (`9a93645`), e conferido
8 vezes seguidas sem falha.

**Roadmap 0.11 concluído** (F0.11.01 a .11). Próximo: Roadmap 1.0 (abaixo), a começar pela spec 114.

### Roadmap 1.0 (comunidade e ecossistema) — nada iniciado

Cadernos públicos indexáveis (inclui criar a rota `/compartilhado/:id`, ver §5) · importadores (Readwise, Goodreads,
StoryGraph, Omnivore, BookWyrm) · feeds RSS/Atom/JSON · quadro espacial com exportação JSON Canvas (o backend do canvas
existe) · oclusão de imagem em SVG · círculos de leitura com trava anti-spoiler (depende de ISBN e estados de leitura).

---

## 2. Como trabalhamos (decisões do usuário em vigor)

- **Spec Kit:** spec, plano e tarefas **juntos** em `specs/NNN-*/`, uma aprovação por feature; depois, executar até o
  fim sem parar em checkpoints. Próximo número livre de spec: **114**.
- **Testes:** suítes completas (`npm test` e `pytest` inteiro) **a cada 5 features**; entre elas, `npm run build` e os
  testes novos da feature. Falha de feature anterior vai em **commit próprio**.
- **Commit** logo depois do build (vale mesmo contra o AGENTS.md §6, por decisão do usuário). Mensagem em português,
  curta: `feature — …`, `correção — …`, `docs — …`, com a linha `Co-Authored-By` de sempre.
- **Push** só quando o usuário pedir. Nunca commitar `query`, `stop` nem `.claude/`.
- **Migração de banco:** só com pedido explícito e backup verificado (AGENTS.md §2).
- **Dados reais:** nunca ler, nem para contar (AGENTS.md §1). Validação sempre com dados fictícios.

## 3. Armadilhas conhecidas

- **Build depois do commit.** O painel de Sistema compara o commit da interface (gravado no build) com o do servidor;
  build antes do commit gera falso aviso de divergência.
- **Depois do push, o serviço precisa reiniciar** para valer: `Restart-Service -Name Leitorum` (o usuário roda). Sem
  isso, a interface nova chama rotas que o backend antigo não tem (foi o 405 de 2026-11-02).
- **Migração no banco ativo:** o `iniciar.py` recusa subir quando a revisão do banco não é a última do código.
  Pelo AGENTS.md §2, só com pedido explícito. Procedimento:
  1. Parar o serviço (PowerShell como administrador): `Stop-Service -Name Leitorum`.
  2. Migrar, na pasta `caderno-leitura-0.1\backend` do checkout principal:
     `.\.venv\Scripts\python.exe -m alembic upgrade head`. Antes de mexer no banco, o Alembic cria e valida o
     snapshot `backups\caderno-pre-migracao-AAAAMMDD-HHMMSS.db` (hora em UTC) na pasta de backups da raiz de
     armazenamento — nesta máquina, **`D:\Leitorum\backups\`**, não `backend\backups` (com cópia na segunda pasta de
     backups, se configurada)
     e aborta a migração se o snapshot falhar.
  3. Conferir o snapshot: `.\.venv\Scripts\python.exe -m app.services.maintenance verificar-snapshot <caminho>`.
  4. Iniciar o serviço: `Start-Service -Name Leitorum` (ou `Restart-Service`).
- **Rota nova no frontend:** registrar o nome em `specs/076-estrategia-responsiva/contracts/responsive-decisions.contract.md`,
  `specs/081-regressao-responsiva/contracts/regression-coverage.contract.md` e `.../data-model.md` (guardas 076/081).
- **Saídas de rede do servidor:** login com Google, capa por endereço e busca por ISBN (desligável com
  `LEITORUM_ISBN_LOOKUP=off`). Qualquer saída nova precisa atualizar "Seus dados" e o Desafio F12 da landing.
- **Migração com chave estrangeira:** usar `batch_alter_table` com o nome da convenção (`fk_<tabela>_<coluna>_<alvo>`);
  `ALTER TABLE ... ADD COLUMN ... REFERENCES` cria a chave sem nome e o `alembic check` falha.
- **Nunca rodar `npm run build` junto com o `pytest`.**
- **Quebras de linha (CRLF × LF):** com `core.autocrlf`, o checkout principal e os worktrees ficam com arquivos
  mistos (só os tocados viram CRLF). Testes que procuram trechos de código com `\n` devem importar
  `tests/helpers/normalize-eol.mjs` (ou normalizar ao ler). Edições por script: preservar o CRLF do arquivo.
- **Conversa em worktree:** depois de cada commit, `git -C C:/Users/User/caderno merge --ff-only <branch>` e
  `npm run build` no checkout principal (o serviço serve o `dist` de lá). O worktree não tem `node_modules`: uma
  junção para o do checkout principal resolve (`New-Item -ItemType Junction`).
- **Landing no servidor de validação:** com `REQUIRE_AUTH` desligado o dono é redirecionado para `/livros`; criar
  o arquivo `auth-on` ao lado do `serve.py` para ver a landing como visitante. Banco novo pede a senha mestra
  (`POST /api/auth/setup-owner` com senha de teste gerada); POST/PUT pela API exigem o cabeçalho `Origin`.
- **`pytest`:** desde 2026-11-07 o `conftest.py` aponta para um banco temporário e recusa o banco ativo (spec 097).
  Mesmo assim, rodar com `CADERNO_DATABASE_PATH` para um arquivo descartável, `LEITORUM_SECONDARY_BACKUP_DIR=""` e
  `LEITORUM_STORAGE_ROOT=""`. Suíte completa: ~7 min; em 2026-11-09, 825 aprovados e 4 pulados.
- **Regra global de botões** (`appearance-advanced.css`, especificidade 0,4,0) pinta todo `<button>` com o destaque e
  vence o CSS dos componentes. Controles secundários usam a variante **`.quiet`** (ganchos `--quiet-bg`,
  `--quiet-border`, `--quiet-fg`, `--quiet-fg-disabled`). Elementos com cara de link dentro de texto: usar `<a>`.
- **Classes globais com nomes genéricos** já existentes (`.source-text`, `.study-tabs` etc.) colidem com classes
  novas; procurar no CSS global antes de nomear.
- **Edição de arquivos pelo Bash:** o shell converte `\\` em `\` nos heredocs e se confunde com crases. Para edições
  com barras ou template strings, escrever um script Python num arquivo e rodá-lo, ou usar a ferramenta de edição.
- **Painel do navegador oculto:** congela transições, animações e `requestAnimationFrame` (trocas de página do Vue e
  revelações ficam paradas). Para medir layout, injetar CSS que zera `transition`/`animation` e navegar direto para a
  URL em vez de trocar de rota por clique.
- **Servidor de validação:** `serve.py` sobe o backend na porta 8010 com banco temporário e dados fictícios (Alembic
  `upgrade head`, `REQUIRE_AUTH` só se existir um arquivo `auth-on` ao lado). A última cópia está no scratchpad da
  conversa antiga (`C:\Users\User\AppData\Local\Temp\claude\C--Users-User-caderno\e06556a9-7f74-4683-a750-476ded401d76\scratchpad\visual\serve.py`);
  numa conversa nova, recriar no próprio scratchpad. Reiniciar o servidor depois de mudar o backend.

## 4. Integrado ao `main` em 2026-11-07 (vindo de conversas laterais)

- **087, autorização antes de gerar backup** (`a6b520a`): `/api/backup` e `/api/backup/bundle` geravam a cópia do
  banco antes de checar o administrador. Corrigido; testes em `test_security_privileged_access.py`.
- **097, isolamento do banco nos testes** (`specs/097-isolamento-banco-testes/`, renumerada de 086): `conftest.py`
  com banco temporário e guarda em `sqlite3.connect` e `sqlite3.dbapi2.connect`; 11 testes-guarda.
- Handoffs das conversas laterais, mantidos para consulta: `docs/contexto/handoffs/`.

## 5. Pendências e pontos a conferir

- **Digitalização (086):** falta validação manual (temas, celular, 320 px, rede desligada) e o resultado de uma foto
  real depois da correção de memória (088). Desde a F0.10.10, `busy` e `low_memory` guardam a foto e oferecem
  "Tentar de novo" (conferido só por testes: o servidor de validação não tem o motor de leitura).
- **Preços da landing** (`components/landing/costSources.ts`, consultados em 07/11/2026): conferir nas fontes e
  trocar valores e `checkedAt` quando forem revistos.
- **Lote 2, conferências só por teste ou script:** cópia ABNT colada de fato no Word/Docs; conflito de versão (409)
  ao completar os dados do livro na Importar; cópia da barra flutuante do estudo.
- **Responsividade:** validação em aparelho real nunca foi registrada.
- **Login com Google** com `Referrer-Policy: same-origin`: conferido só até o botão carregar; falta um login real.
- **Celular via Tailscale:** se salvar der "Origem do pedido não autorizada", acrescentar a origem em
  `LEITORUM_TRUSTED_ORIGINS` (o log do serviço mostra qual foi recusada).
- **Imagens externas** em estudos deixaram de carregar (CSP); caminho: enviar pela área de imagens.
- **`/compartilhado/{id}`:** a rota não existe no frontend; desde a F0.10.10 o `robots.txt` e o sitemap não a
  anunciam (`seo_service.PUBLIC_STUDY_PAGES_ENABLED = False`). Ligar quando os cadernos públicos do 1.0 criarem a rota.
- **Licença:** o repositório não tem arquivo de licença. Desde a F0.10.10 nenhum texto diz "software livre"; o
  rodapé diz "Código-fonte público". Escolher uma licença é decisão do dono.
- **`ROADMAP-0.10.md`, `ROADMAP-0.11.md`, `ROADMAP-1.0.md`:** ainda não escritos; este arquivo faz as vezes deles até lá.
