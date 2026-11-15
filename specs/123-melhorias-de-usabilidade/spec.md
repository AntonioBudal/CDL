# Feature Specification: F0.12.10 — Pequenas melhorias de usabilidade

**Feature Branch**: `123-melhorias-de-usabilidade`

**Created**: 2026-11-15

**Status**: Concluída

**Input**: Pedido do usuário em 2026-11-14 (item F0.12.10 do `docs/contexto/ROADMAP-0.12.md`). Décima e última feature
do 0.12; fecha o lote 2 com as suítes completas. **Sem migração.** Só frontend.

---

## 1. Contexto (auditoria de 2026-11-15)

| Item | Hoje | Onde |
|---|---|---|
| Calendário do Painel | Fixo em 365 dias (a API aceita de 30 a 730); rótulos dos dias da semana numa coluna separada da grade; clicar num dia filtra a linha do tempo com só um chip "Filtrando por" | `components/HeatmapCalendar.vue`, `views/DashboardView.vue` |
| Barra de ações do estudo | Aparece flutuando junto do trecho selecionado (destacar, cor, anotar, citar, ocultar, pergunta); no celular, embaixo | `components/FloatingActionsToolbar.vue`, `views/StudyView.vue` |
| Menu de 3 pontos | `DropdownMenu` alinhado à direita abre para fora da tela no celular; o mesmo componente serve a mais 2 menus (livro e capítulo) | `components/ui/DropdownMenu.vue` |
| Cabeçalho do estudo | Título, linha de metadados e ações com espaço vertical demais | `.reader-heading-main` em `StudyView.vue` |

Regra da feature: **cada defeito é reproduzido no navegador (dados fictícios) antes de corrigir** e conferido em 375,
768 e 1366 px, nos 10 temas.

---

## 2. User Stories

### US1 — Calendário do Painel (P1)

**Acceptance**:
1. Acima do calendário, um seletor de período: **1 mês, 3 meses, 6 meses, 12 meses** e **o ano passado** (ex.: 2025).
   O padrão segue 12 meses; a escolha fica lembrada no navegador. "Ano passado" usa os 730 dias que a API já devolve e
   mostra só as datas daquele ano (sem mudar o servidor).
2. **Defeito visual dos dias da semana**: reproduzir e corrigir para que a coluna dos dias (Seg, Qua, Sex) fique
   sempre alinhada às linhas da grade, em qualquer tema, fonte e largura.
3. **Filtro por dia mais claro**: clicar num dia mostra acima da linha do tempo um título "Atividades em 14 de
   novembro de 2026" com a quantidade e um botão "Ver todas"; o dia escolhido fica marcado no calendário; clicar de
   novo no mesmo dia (ou em "Ver todas") volta ao normal. No celular, a tela rola até a linha do tempo.

### US2 — Barra de ações fixa no estudo (P1)

**Acceptance**:
1. Sai a barra flutuante. Entra uma **barra fixa logo acima das abas das seções** (Resumo, Explicação…), no estilo do
   Word e do Google Docs: os mesmos botões de hoje (destacar e cor, anotar, copiar citação, ocultar trecho, pergunta),
   em grupos com separadores, ícone + dica, respeitando os 10 temas.
2. Ela **acompanha a rolagem** (fica presa no alto enquanto se lê). Sem trecho selecionado, os botões ficam
   desativados com a dica "Selecione um trecho do texto"; com trecho, ativam. Clicar num botão **não perde a seleção**.
3. **No celular** ela fica fixa no alto da tela (não mais embaixo) e rola na horizontal se não couber; alvos de 44 px.
4. Quem só pode ler (estudo compartilhado) vê apenas o que já via hoje (copiar citação).
5. Atalhos e o comportamento de cada botão não mudam (mesmos eventos para o `StudyView`).

### US3 — Menu de 3 pontos cabe na tela (P1)

**Acceptance**:
1. O `DropdownMenu` passa a **caber na tela**: depois de abrir, mede a posição e encosta dentro da tela (margem de
   8 px) na horizontal; se não couber na vertical, abre para cima ou rola por dentro. Vale para os 3 menus que usam o
   componente.

### US4 — Cabeçalho do estudo compacto (P2)

**Acceptance**:
1. Título, linha de metadados (estado, modelo, localização) e ações ficam mais próximos na vertical (medir antes e
   depois; meta: o texto da primeira seção sobe sem cortar nada).

### Edge Cases

- Período sem nenhuma atividade: calendário vazio com a mensagem de hoje.
- Seleção de texto que atravessa duas seções: a barra se comporta como a flutuante se comportava (mesma regra).
- Menu aberto perto da borda de baixo no celular com teclado aberto: rola por dentro.

---

## 3. Requirements

- **FR-001**: `HeatmapCalendar.vue` e `DashboardView.vue`: período (com `days` na API e filtro do ano passado),
  alinhamento dos dias da semana na própria grade, filtro por dia com título, contagem e "Ver todas".
- **FR-002**: `StudyActionsBar.vue` (novo, a partir da lógica do `FloatingActionsToolbar.vue`, que sai) fixo acima de
  `StudyTabs`; `StudyView.vue` passa a usá-lo.
- **FR-003**: `DropdownMenu.vue`: encaixe na tela depois de abrir.
- **FR-004**: `StudyView.vue`: espaçamento do cabeçalho.
- **FR-005**: Versão `0.12.0-alpha.10` e F0.12.10 marcada; o 0.12 fica com as 10 features concluídas na linha do
  tempo.

## 4. Success Criteria

- **SC-001**: Testes: período (dias pedidos e filtro do ano passado), alinhamento (dias da semana dentro da grade),
  filtro por dia (título, contagem, limpar), barra fixa (posição acima das abas, desativada sem seleção, mesmos
  eventos, só citar para leitura), encaixe do menu (função pura de posição), cabeçalho.
- **SC-002**: Navegador: cada defeito reproduzido antes e conferido depois em 375, 768 e 1366 px; barra e calendário
  nos 10 temas (contraste).
- **SC-003**: **Fecho do lote 2:** `npm test` e `pytest` completos (banco descartável); falha antiga em commit próprio;
  build; versão `alpha.10`; commit; levar ao `main`.

## 5. Fora do escopo

- Mudar a API do Painel; outras telas além das quatro.
- Novos botões na barra (formatação de texto como negrito/itálico).
