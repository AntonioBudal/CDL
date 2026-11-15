# Roadmap 0.12 — Comunidade, ecossistema e versões

**Criado em:** 2026-11-14, por decisão do usuário: o antigo "Roadmap 1.0" passou a ser o **0.12**, porque a 1.0 ainda
está longe. Os itens de comunidade e ecossistema do plano mestre de 2026-11-01 continuam aqui, na mesma ordem,
depois de uma feature nova de versionamento, que vem primeiro porque as seguintes passam a se registrar nela.

**Fluxo:** o de sempre (HANDOFF §2): spec, plano e tarefas juntos em `specs/NNN-*/`, uma aprovação por feature,
suítes completas a cada 5 features, commit em português, push só quando o usuário pedir.

---

## Convenção de versão (adotada na F0.12.01)

[Versionamento Semântico 2.0.0](https://semver.org/lang/pt-BR/) (`MAJOR.MINOR.PATCH`, com pré-lançamento):

| Situação | Versão | Exemplo |
|---|---|---|
| Roadmap fechado (todas as features + suítes completas) | `0.MINOR.0` | `0.11.0` |
| Roadmap em andamento, N features entregues | `0.MINOR.0-alpha.N` | `0.12.0-alpha.2` |
| Correção depois de fechado | `0.MINOR.PATCH` | `0.11.1` |
| Compilação (só no Painel de Sistema e na dica do rodapé, não no texto) | `+<commit curto>` | `0.12.0-alpha.2+a1b2c3d` |

- `MAJOR` fica em `0` até a 1.0. Fonte única: **`caderno-leitura-0.1/VERSION`**, lida pelo backend (`app.__version__`,
  `/api/health`, Painel de Sistema) e pelo build (`__APP_VERSION__`); o `package.json`/`package-lock.json` acompanham.
- Cada feature do 0.12, ao ser concluída, sobe o `alpha.N` em `VERSION`, `package.json` e `package-lock.json` e marca
  `done: true` em `frontend/src/data/versionHistory.ts`, no mesmo commit (um teste confere que `alpha.N` = features
  entregues). Ao fechar o roadmap: `0.12.0`, `status: 'closed'` e `closed` com a data.

---

## Features

| # | Feature | Notas |
|---|---|---|
| F0.12.01 | **Versão no rodapé e "Evolução das versões"** | **Concluída em 2026-11-14** (versão `0.12.0-alpha.1`). Spec **114**. |
| F0.12.02 | **Estudos publicados na web** (`/compartilhado/:id`, indexável) | **Concluída em 2026-11-14** (versão `0.12.0-alpha.2`, migração `0040`). Spec **115**. Fechou a pendência do HANDOFF §5 sobre `/compartilhado/{id}`. |
| F0.12.03 | **Importadores:** Readwise, Goodreads, StoryGraph, Omnivore, BookWyrm | **Concluída em 2026-11-15** (versão `0.12.0-alpha.3`, sem migração). Spec **116**. Formato do Readwise ainda **sem conferência com arquivo real** (pedir teste ao usuário). |
| F0.12.04 | **Feeds RSS, Atom e JSON** | **Concluída em 2026-11-15** (versão `0.12.0-alpha.4`, sem migração). Spec **117**. |
| F0.12.05 | **Quadro espacial com exportação JSON Canvas** | O backend do canvas já existe. |
| F0.12.06 | **Oclusão de imagem em SVG** | Cartões de revisão sobre imagens. |
| F0.12.07 | **Círculos de leitura com trava anti-spoiler** | Depende de ISBN (F0.11.04) e estados de leitura (F0.11.01), já entregues. |
| F0.12.08 | **Simplificação de nomes** | Pedido do usuário em 2026-11-14. Auditoria abaixo. |
| F0.12.09 | **Seletor de idioma — só a fundação** | Pedido do usuário em 2026-11-14. Transição grande (avaliação abaixo); o usuário escolheu **só a fundação** no 0.12. |
| F0.12.10 | **Pequenas melhorias de usabilidade** | Pedido do usuário em 2026-11-14: calendário do Painel, barra de ações fixa no estudo, menu de 3 pontos no celular, espaçamento do cabeçalho do estudo. |

### F0.12.01 — Versão no rodapé e "Evolução das versões" (pedido do usuário em 2026-11-14)

1. **Rodapé:** mostra a versão atual no padrão acima, discreta (ex.: `v0.12.0-alpha.1`), com o commit da compilação
   na dica (`title`) e no Painel de Sistema; nunca dados do usuário.
2. **Tela "Evolução das versões"**, bem escondida: sem entrada nos menus; só um botão discreto no fim da página
   **Sobre o Leitorum**. Rota própria, com `noindex`.
   - Linha do tempo de **cada roadmap** (0.1 até o 0.12 em andamento): versão, período, tema e principais avanços,
     quantas features, e a situação (fechado / em andamento).
   - Fonte: um arquivo de dados escrito à mão a partir de `docs/HISTORICO-ROADMAPS.md`, dos `ROADMAP-0.x.md` e do
     HANDOFF (texto do projeto, nada do acervo do usuário).
3. A versão do backend (`/api/health`, Painel de Sistema) passa a ser a mesma do rodapé.

### F0.12.08 — Simplificação de nomes (auditoria de 2026-11-14)

**Regra:** nomes simples, descritivos e universais; **um nome por tela**, igual no menu, no título e nos avisos; letra
maiúscula só no começo (padrão do português); subtítulo de uma frase que diga o que a tela faz. Metáforas
("Bancada", "Ateliê", "Salão", "Cockpit", "Despejo") e termos em inglês na interface ("Dashboard", "Inbox",
"Active Recall") saem. Comentários e nomes internos do código não mudam.

O problema mais comum não é só o nome rebuscado: **a mesma tela tem 2 ou 3 nomes** em lugares diferentes.

| Tela | Hoje (menu · título · rótulo acima do título · outros lugares) | Proposta |
|---|---|---|
| Painel (`/dashboard`) | "Dashboard" · "Dashboard 2.0" · "Cockpit de Estudos e Navegação" · Ajustes: "Dashboard 2.0 (Cockpit de Estudos e Retoma)" | **Painel**; subtítulo: "Seus estudos recentes, suas conexões e seu ritmo de leitura." |
| Revisão (`/revisao`) | "Revisão" · "Central de Revisão" · subtítulo "Bancada de Fixação Cognitiva: pratique Active Recall…" · vazio: "Sua Bancada de Fixação Cognitiva está Pronta" · rótulo "Bancada de Prontidão" | **Revisão**; subtítulo: "Pratique lembrando: responda às perguntas e complete os trechos escondidos." ("Active Recall" → "lembrar sem olhar") |
| Caixa de entrada (`/inbox`) | "Inbox" (barra) · "Caixa de Entrada" (celular) · "Mesa de Triagem" (título) · "Triagem e Captura" · "Área de Despejo de Pensamentos" · "Abrir na Mesa de Triagem" | **Caixa de entrada**; subtítulo: "Anote ideias rápidas e decida depois o que vira estudo." |
| Importar (`/importar`) | "Importar" · "Importar Estudo" (celular) · "Importar Fichamento" · "Ateliê de Fichamento" | **Importar**; título "Importar fichamento" |
| Digitalizar (`/digitalizar`) | "Digitalizar Caderno" · "Ateliê de Fichamento" | **Digitalizar caderno** (rótulo de cima "Importar") |
| Amigos (`/amigos`) | "Amigos" · "Salão de Amigos" (celular) · "Salão Literário & Círculos de Estudo" · "correspondência intelectual" | **Amigos**; subtítulo: "Encontre leitores, veja leituras em comum e responda aos pedidos de amizade." |
| Destaques (`/highlights`) | "Destaques" · "Destaques e Anotações" | **Destaques**; subtítulo: "Os trechos que você marcou e as notas que escreveu." |
| Lixeira | "Lixeira" · "Gerenciamento de Acervo" · "expurgo automático permanente" | **Lixeira**; subtítulo: "Itens excluídos ficam aqui por 30 dias e depois são apagados de vez." |
| Imagens | "Minhas Imagens e Espaço" | **Minhas imagens** |
| Ajustes | "Ajustes" · "Ajustes & Preferências" (menu do usuário) · "Ajustes & Conexão" (celular) | **Ajustes** |
| Perfil | "Meu Perfil" (celular) · "Perfil Público" (menu do usuário) | **Meu perfil** |
| Conceitos (`/conceitos`) | "Léxico" · "Léxico de conceitos" · "Conceitos do acervo" | **Conceitos** (mais descritivo que "léxico") |
| Sínteses | "Sínteses" · "Cadernos de síntese" | **Sínteses** |
| Sair | "Encerrar Sessão (Sair)" · "Encerrar Sessão" | **Sair** |

A spec revisa também os textos que não são títulos, mas usam os nomes antigos (avisos, botões "Voltar à Mesa de
Triagem", mensagens de vazio, o painel de Ajustes), os **títulos da aba do navegador** (`meta.title` das rotas: ex.
"Amigos e Leitores", "Central de Revisão") e os testes que conferem esses textos.

### F0.12.09 — Seletor de idioma (avaliação de 2026-11-14)

O usuário escolhe o idioma da interface, independentemente da região. **É uma transição grande** — o usuário pediu
para ser avisado nesse caso:

- Não há biblioteca de tradução no projeto; todo texto está escrito direto no código, em português.
- Medição: cerca de **2.600 textos** em 155 telas e componentes, **~280** em arquivos de código e **~270** mensagens
  de erro do servidor (que também aparecem na tela); **23** arquivos formatam datas fixas em `pt-BR`.
- Partes presas ao português por natureza: citação ABNT, validador de paráfrase, leitura da seção Conceitos, o
  organizador da digitalização (palavras-chave em português), a landing e os textos jurídicos/de apoio.

Opções para decidir antes da spec:
1. **Cortar do 0.12** e guardar para um roadmap próprio de internacionalização.
2. **Só a fundação no 0.12:** biblioteca de tradução, seletor em Ajustes, idioma salvo na conta, datas pelo idioma,
   e a tradução (inglês) do que aparece em toda tela (menus, cabeçalho, rodapé, avisos gerais); o resto da interface
   segue em português e migra aos poucos.
3. **Tradução completa no 0.12:** várias features (estimativa: 6 a 10 fatias), com revisão de texto em inglês.

**Decisão do usuário (2026-11-14): opção 2, só a fundação.** Escopo da F0.12.09: biblioteca de tradução, seletor
em Ajustes, idioma salvo na conta (e lembrado no navegador antes do login), datas pelo idioma, e inglês nos textos de
toda tela (menus, cabeçalho, rodapé, avisos gerais). O resto segue em português e migra aos poucos em roadmaps
seguintes. A F0.12.08 (nomes) vem **antes**, para traduzir já os nomes novos.

### F0.12.10 — Pequenas melhorias de usabilidade (pedido de 2026-11-14)

1. **Calendário do Painel** (`components/HeatmapCalendar.vue`, `views/DashboardView.vue`): hoje é fixo em 12 meses
   (365 dias), embora a API já aceite de 30 a 730 dias. Rework: escolher o período (ex.: 1, 3, 6 e 12 meses, e ano
   anterior); corrigir o defeito visual na coluna dos dias da semana, em que um dia muda o layout; repensar o filtro
   por dia (clicar num dia hoje filtra a linha do tempo de um jeito pouco claro).
2. **Barra de ações do estudo fixa** (`components/FloatingActionsToolbar.vue`, `views/StudyView.vue`): sai a barra
   flutuante e entra uma barra fixa logo acima das abas das seções (Resumo, Explicação…), no estilo do Word e do
   Google Docs, moderna e respeitando os 10 temas. No celular, ela deixa de aparecer na parte de baixo e fica fixa no
   alto, como nesses editores.
3. **Menu de 3 pontos do estudo no celular** (`DropdownMenu` com `align="right"` em `StudyView.vue`): abre para fora da
   tela e corta boa parte do conteúdo; deve caber na tela (ou virar uma folha que sobe de baixo).
4. **Cabeçalho do leitor de estudos** (`.reader-heading-main` em `StudyView.vue`): os elementos ficam espaçados demais
   na vertical; compactar.

A spec reproduz cada defeito no navegador (com dados fictícios) antes de corrigir e confere em 375, 768 e 1366 px.

---

## Fora deste roadmap (a decidir)

- Ideias adiadas nas specs do 0.11 (backlinks "usado nas sínteses", transclusão em estudos, bordas/perspectiva na
  digitalização, SM-2/FSRS, KOReader pela rede, editar o léxico à parte).
- Planos do usuário ainda não registrados.
- Critérios da 1.0.
