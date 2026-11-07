# HANDOFF — Leitorum (leia primeiro)

**Atualizado em:** 2026-11-07, na conversa CDL-Main.
**Para quem:** cada conversa nova de lote (0.10, 0.11, 1.0). Leia este arquivo, `AGENTS.md` e o roadmap do lote antes
de mexer em código. Ao encerrar, atualize este arquivo e `caderno-leitura-0.1/docs/contexto/RETOMADA.md`.

---

## 1. Onde estamos

- **Plano mestre** de 2026-11-01, renumerado para **0.10, 0.11 e 1.0** (os números 0.8 e 0.9 já eram roadmaps
  entregues). **Prazo combinado:** terminar os três até **15/11/2026**, cerca de 2 features por dia.
- **`main`** está em dia com o trabalho até 2026-11-07, inclusive as duas features que tinham ficado só em branches
  de conversas laterais (ver §4).

### Roadmap 0.10 (redesenho, segurança e ergonomia)

| Feature | Situação | Commit | Spec |
|---|---|---|---|
| F0.10.01 Header leve e variante neutra de botão (`.quiet`) | Concluída | `4a6759a` | `specs/092-header-leve-botao-neutro/` |
| F0.10.02 Endurecimento de segurança (CSP, origem, noindex, security.txt, `secure_delete`) | Concluída | `e06b925` | `specs/093-endurecimento-seguranca/` |
| F0.10.02.5 Capa, contraste e gerenciamento de capítulos (emergência) | Concluída | `2b69b80`, `9477f80` | `specs/094-correcoes-capa-capitulos/` |
| F0.10.03 Painel de Sistema (commit, revisão do banco, integridade, backups) | Concluída | `fdad9c4` | `specs/095-painel-sistema-soberania/` |
| F0.10.04 Revisão: baldes, sessões 5/10/15, gaveta de contexto | Concluída | `d410760` | `specs/096-revisao-baldes-sessao/` |
| **F0.10.05 Destaques** (cópia ABNT, tipografia citação × anotação) | **Próxima** | — | — |
| F0.10.06 Importar (faixa de metadados, ganchos para referências em 3 escopos) | Pendente | — | — |
| F0.10.07 Amigos (leituras e estudos em comum) | Pendente | — | — |
| F0.10.08 Landing: seção de confiança e "Desafio F12" (TCO só com fontes e datas) | Pendente | — | — |
| F0.10.10 Correções reservadas (lista do usuário; inclui talvez unificar os 3 botões de sessão da Revisão) | Pendente | — | — |

Inbox e Lixeira do plano já estavam atendidas pelo código (auditoria de 2026-11-01); só conferir se surgir dúvida.
O **lote 1** (F0.10.01 a .04) fechou com as suítes completas em 2026-11-03. O **lote 2** começa na F0.10.05.

### Roadmap 0.11 (motores) — nada iniciado

Estados de leitura do livro (exige migração) · bandeja de triagem por capítulo · parsers Kindle/Kobo · ISBN (BrasilAPI
e Open Library, só sob demanda) · referências em 3 escopos (CSL-JSON, BibTeX, ABNT/APA) · léxico de conceitos e `[[ ]]`
· validador de paráfrase (Jaccard) · evolução da revisão (`difficulty_weight`, conceitos frágeis, cartões de conceito,
Memória do Dia) · receptor KOReader/Readest · recorte de foto para a digitalização · cadernos de síntese com transclusão.

### Roadmap 1.0 (comunidade e ecossistema) — nada iniciado

Cadernos públicos indexáveis (inclui criar a rota `/compartilhado/:id`, ver §5) · importadores (Readwise, Goodreads,
StoryGraph, Omnivore, BookWyrm) · feeds RSS/Atom/JSON · quadro espacial com exportação JSON Canvas (o backend do canvas
existe) · oclusão de imagem em SVG · círculos de leitura com trava anti-spoiler (depende de ISBN e estados de leitura).

---

## 2. Como trabalhamos (decisões do usuário em vigor)

- **Spec Kit:** spec, plano e tarefas **juntos** em `specs/NNN-*/`, uma aprovação por feature; depois, executar até o
  fim sem parar em checkpoints. Próximo número livre de spec: **098**.
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
- **Nunca rodar `npm run build` junto com o `pytest`.**
- **`pytest`:** desde 2026-11-07 o `conftest.py` aponta para um banco temporário e recusa o banco ativo (spec 097).
  Mesmo assim, rodar com `CADERNO_DATABASE_PATH` para um arquivo descartável, `LEITORUM_SECONDARY_BACKUP_DIR=""` e
  `LEITORUM_STORAGE_ROOT=""`. Suíte completa: ~7 min; em 2026-11-07, 778 aprovados e 1 pulado.
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
  real depois da correção de memória (088). Fatia futura possível: a mensagem "Não foi possível ler esta foto" aparece
  também em recusas passageiras (`low_memory`, `busy`).
- **Responsividade:** validação em aparelho real nunca foi registrada.
- **Login com Google** com `Referrer-Policy: same-origin`: conferido só até o botão carregar; falta um login real.
- **Celular via Tailscale:** se salvar der "Origem do pedido não autorizada", acrescentar a origem em
  `LEITORUM_TRUSTED_ORIGINS` (o log do serviço mostra qual foi recusada).
- **Imagens externas** em estudos deixaram de carregar (CSP); caminho: enviar pela área de imagens.
- **`/compartilhado/{id}`** está no sitemap e no `robots.txt`, mas a rota não existe no frontend (404): fica para os
  cadernos públicos do 1.0.
- **Licença:** o repositório não tem arquivo de licença; textos públicos dizem "código-fonte público", não "software
  livre". O rodapé global do App ainda diz "Software Livre".
- **`ROADMAP-0.10.md`, `ROADMAP-0.11.md`, `ROADMAP-1.0.md`:** ainda não escritos; este arquivo faz as vezes deles até lá.
