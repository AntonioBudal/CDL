# Especificação (rascunho) — Feature 0.8.13.5: rótulos de botões e linhas "texto + botão" em telas estreitas

* **Preparado por:** Claude Code, em 2026-10-12, a partir do pedido do usuário ("Textos mais botões").
* **Destino:** insumo para o Antigravity rodar `speckit.specify`. Não altera código.
* **Base:** leitura (sem alteração) de `caderno-leitura-0.1/frontend/src/` no commit `97858a4`. Análise **estática**:
  nada foi renderizado. Os casos listados na seção 4 são **candidatos calculados**, não defeitos vistos em tela.
* **Posição no roadmap:** entra entre a 0.8.13 (`078-conteudo-responsivo`) e a 0.8.14 (visualizações móveis).
* **Numeração em `specs/`:** a próxima pasta livre é `079`, mas `.specify/feature.json` e o contrato
  `specs/076-estrategia-responsiva/contracts/breakpoints-patterns.contract.md` já tratam `079` como
  "visualizações móveis". **Decisão do usuário antes do `specify`:** (a) esta feature recebe `079` e as seguintes
  deslocam para `080`/`081`, com ajuste das referências no contrato; ou (b) outra convenção. Recomendação: (a).

---

## 1. Pedido original, reescrito

> Em várias telas há botões com texto que, em dispositivos móveis, não cabem em uma linha: o rótulo quebra em duas
> (ou mais) linhas, o botão fica alto e desalinhado dos vizinhos. O mesmo acontece em linhas que combinam um texto
> com um botão ao lado. Queremos primeiro levantar todas as ocorrências, em todas as telas, e depois corrigi-las
> com uma regra única, em vez de remendos tela a tela.

## 2. Causa raiz (confirmada no código)

1. A regra-base de todos os botões, em `src/style.css:31` (`button, .button { display: inline-flex; … }`), **não
   define `white-space`**. O rótulo pode quebrar entre palavras.
2. Dentro de um contêiner flex, o botão é um item com `flex-shrink: 1` e largura mínima igual à da **palavra mais
   longa**. Quando falta espaço, o navegador encolhe o botão até esse limite e o rótulo passa para a linha de baixo,
   em vez de o grupo se reorganizar.
3. Não existe componente de botão compartilhado (`components/ui/` não tem um). Cada tela resolve o aperto do seu
   jeito: 27 controles têm `white-space: nowrap` local; **340 de 367 controles com rótulo não têm proteção alguma**.
4. Existe um único precedente de solução deliberada: `BookView.vue` troca `.btn-text-full` por `.btn-text-short`
   em ≤ 640 px ("Exportar anotações" → "Exportar").

Consequência: a quebra aparece onde o botão divide a linha com outra coisa **sem** `flex-wrap` — grupos com
`flex: 1`, grades de colunas fixas e linhas "texto + botão". Grupos com `flex-wrap: wrap` tendem a se salvar,
porque o item inteiro desce para a linha seguinte antes de encolher.

## 3. Tipos de controle (a regra depende do tipo)

| Tipo | O que é | Exemplos no código | Regra proposta |
|---|---|---|---|
| **A — Ação** | Rótulo fixo e curto, com ou sem ícone | "Importar estudo", "Excluir definitivamente" | Nunca quebra. Se não couber, quem muda é o **grupo** (ver seção 5). |
| **B — Rótulo com dado** | Parte do texto vem do acervo | "Voltar a {{ capítulo }}", nome de categoria | Uma linha com reticências; texto completo em `title` e `aria-label`. |
| **C — Botão-cartão** | Título + descrição dentro do botão | `ConcurrencyConflictModal`, `ConflictResolutionModal`, `confirm-choice-card`, `btn-rating` | Várias linhas são intencionais. Fora da regra; só o título não quebra. |
| **D — Abas e segmentos** | Divisão igual da largura (`flex: 1`) | abas do Importar, do Dashboard, filtros da Lixeira | Nunca quebra. Se não couber: faixa rolável (padrão `.tabs-scroll-*` já existente) ou rótulo curto. |
| **E — Linha texto + botão** | Título/descrição ao lado de uma ação | `.section-heading`, `.save-bar`, cabeçalhos de cartão | O **texto** pode quebrar; o botão não. Abaixo de uma largura mínima de texto, o botão desce para a linha seguinte. |

## 4. Candidatos encontrados (estático — confirmar em tela)

Confiança: **A** = a conta de largura indica quebra em 320–375 px; **M** = provável em 320 px; **B** = só se o
contêiner apertar.

| # | Tela | Controles | Tipo | Conf. | Arquivo |
|---|---|---|---|---|---|
| 01 | Lixeira — barra de lote | "Selecionar todos" · "Restaurar selecionados" · "Excluir definitivamente" lado a lado em 95vw | A | A | `views/TrashView.vue:650-666` |
| 02 | Lixeira — cartões | "Restaurar…" + "Excluir definitivamente" | A | M | `views/TrashView.vue:534-543, 612-621` |
| 03 | Lixeira — filtros | "Estudos individuais (N)" | D | M | `views/TrashView.vue:444-464` |
| 04 | Revisão — início de sessão | "Iniciar Sessão Estruturada do Livro" + selo "Rápida (10 itens)"; "Prática Rápida neste Hub (N)" | A | A | `views/ReviewHubView.vue:257-272` |
| 05 | Revisão — abas | "Prática de Revisão" · "Histórico de Sessões" | D | M | `views/ReviewHubView.vue:202-212` |
| 06 | Revisão — estado vazio | "Explorar meus Livros e Criar Estudos" (não cabe em 320 px nem sozinho) | A | A | `components/review/ReviewPedagogicalEmpty.vue:151-168` |
| 07 | Resumo de revisão / sessão | "Concluir e voltar ao acervo" + "Revisar mais 10"; "Retornar à Central de Revisão" + "Ir para o Livro" | A | A | `components/review/ReviewSummaryModal.vue:91-99`, `components/session/SessionSummaryModal.vue:107-115` |
| 08 | Importar — abas móveis | "Texto da Fonte" · "Prévia Estruturada" (`flex: 1`) | D | M | `views/ImportView.vue:358-368`, `style.css:537` |
| 09 | Busca global | "Buscar estudos com qualquer um dos termos (Modo OR)" (50 caracteres) | A | A | `components/search/GlobalSearchModal.vue:333` |
| 10 | Landing e rodapé público | "Criar Conta Gratuita" + "Já possuo conta (Entrar)" com **altura fixa de 48 px** (quebra = texto cortado) | A | M | `components/landing/HeroSection.vue:24-29`, `PublicFooter.vue:18-22` |
| 11 | Mapa — barra móvel | "Conectar a…/Toque no destino…" · "Novo Estudo" · "Ver Estudo" (3 × `flex: 1` em ~311 px) | A | A | `components/views/StudyMapView.vue:744-765` |
| 12 | Inbox — cartão de captura | "Promover para Estudo" · "Vincular a Estudo" · "Mover para Pendentes" | A | B | `components/inbox/CaptureItemCard.vue:266-309` |
| 13 | Destaques — cartão | "Abrir no Estudo" · "Adicionar reflexão" · "Expandir contexto" · "Formato Markdown (> citação)" | A | B | `components/highlights/HighlightCard.vue:195-383` |
| 14 | Ajustes | "Restaurar padrões de aparência" · "Limpar chaves obsoletas" · "Salvar Alterações…" · "Baixar Acervo…" | A | M | `views/SettingsView.vue:807-1057` |
| 15 | Ajustes — sessões | "Desvincular Google" · "Sair de todos os outros…" · "Revogar" | A | M | `components/auth/SessionsManager.vue:218-308` |
| 16 | Modais de conta | "Excluir definitivamente" · "Sim, desativar conta" · "Reativar Minha Conta" + "Cancelar" | A | M | `components/settings/*.vue` |
| 17 | Avatar | "Usar foto da conta Google" · "Remover foto atual" | A | M | `components/profile/AvatarUploadModal.vue:305-345` |
| 18 | Backup | "Baixar pacote completo (.zip)" · "Baixar apenas banco (.db)" | A | M | `components/DatabaseBackup.vue:147-167` |
| 19 | Livro | "Importar estudo" ao lado do seletor de visualização; "Adicionar capítulo" | A / E | B | `views/BookView.vue:416-437` |
| 20 | Leitor | "Voltar a {{ capítulo }}"; "Ativar modo foco" · "Leitura Ativa" | B / A | M | `views/StudyView.vue:485`, `components/ReaderTools.vue:80-90` |
| 21 | Dashboard | abas "Para Conectar (N)" · "Conexões (N)"; "Exibir todas as atividades" | D / A | B | `views/DashboardView.vue:278-378` |
| 22 | Edição de estudo | "Histórico de versões" · "Descartar rascunho" · "Salvar alterações" | A | M | `views/StudyEditView.vue:145-192` |
| 23 | Apoie / Admin | "Repositório Oficial no GitHub"; "Salvar Configurações de Apoio"; abas "Contas e Acessos" · "Apoio e Doações" | A / D | M | `views/SupportView.vue:140`, `views/AdminView.vue:382-769` |
| 24 | Linhas texto + botão genéricas | `.section-heading` (sem `flex-wrap` quando falta a classe `.wrap`), `.save-bar` | E | M | `style.css:148, 173` |

Fora da regra (tipo C, várias linhas por projeto): `ConcurrencyConflictModal.vue:105-116`,
`ConflictResolutionModal.vue:217-228`, `StudyEditorFields.vue:561-575`, `StudySessionView.vue:133-155`.

**Sobreposição com outra feature:** o item 11 (Mapa) será refeito pela feature de visualizações móveis. Aqui ele só
recebe a regra global; o redesenho da barra fica lá.

## 5. Regra proposta — o que acontece quando o rótulo não cabe

Ordem de preferência, aplicada ao **grupo**, nunca ao texto:

1. **O grupo quebra de linha** (os botões descem inteiros) ou **empilha** em largura total.
2. **Rótulo curto** — variante menor do mesmo texto (precedente: `.btn-text-full` / `.btn-text-short`).
3. **Só ícone**, com `aria-label` e `title` — apenas quando o ícone é inequívoco (lixeira, fechar, copiar).
4. **Menu "⋯"** para ações secundárias (padrão 4.3 do contrato da 076).

Proibido: reduzir a fonte abaixo de 0,8125 rem; reticências em rótulo de ação fixo (tipo A); altura fixa em botão
cujo rótulo possa quebrar; rolagem horizontal da página como efeito colateral.

## 6. Proposta de especificação (insumo para `speckit.specify`)

### Histórias de usuário

**US1 (P1) — Inventário em tela.** Como responsável pelo produto, quero a lista real de onde os rótulos quebram,
medida no aplicativo em execução, para corrigir defeitos vistos e não suposições.
*Teste independente:* executar o roteiro de medição (seção 7) em 320, 375, 390, 430 e 767 px sobre todas as rotas
da matriz da 076 e obter uma tabela "rota · controle · tipo · largura em que quebra".

**US2 (P1) — Botões de ação em uma linha.** Como leitor no celular, quero que todo botão de ação mostre seu rótulo
em uma única linha, alinhado aos vizinhos, para reconhecer a ação de relance e tocar sem erro.
*Teste independente:* nas mesmas larguras, nenhum controle dos tipos A e D ocupa mais de uma linha de texto.

**US3 (P2) — Linhas texto + botão legíveis.** Como leitor no celular, quero que, ao lado de um botão, o texto
mantenha largura suficiente para ser lido, e que o botão desça para a linha seguinte quando não houver espaço.
*Teste independente:* em 320 px, nenhuma linha tipo E deixa o texto com menos de 12 caracteres por linha.

**US4 (P3) — Regra única e protegida.** Como mantenedor, quero que a regra more em um só lugar e que um teste
acuse botões novos fora do padrão.
*Teste independente:* remover a proteção da regra-base faz o teste falhar.

### Requisitos funcionais

* **RF-01** Produzir o inventário renderizado (US1), classificando cada controle nos tipos A a E e confirmando ou
  refutando os 24 candidatos da seção 4.
* **RF-02** Rótulos dos tipos A e D DEVEM permanecer em uma linha em 320, 375, 390, 430 e 767 px.
* **RF-03** Quando o rótulo não couber, aplicar a ordem da seção 5; a opção escolhida fica registrada por grupo.
* **RF-04** Rótulos do tipo B DEVEM truncar com reticências em uma linha e expor o texto completo.
* **RF-05** Controles do tipo C ficam explicitamente isentos, com lista nominal.
* **RF-06** Linhas do tipo E DEVEM permitir a quebra do texto, manter o botão em uma linha e empilhar quando o
  texto ficar com menos de 12 caracteres por linha.
* **RF-07** Nenhum botão com rótulo pode ter altura fixa que corte o texto (item 10).
* **RF-08** Alvos de toque continuam com no mínimo 44 × 44 px em telas móveis.
* **RF-09** Nenhuma correção pode criar rolagem horizontal na página.
* **RF-10** O comportamento em ≥ 1024 px NÃO muda; rótulos completos permanecem no desktop.
* **RF-11** Variantes de rótulo curto preservam o sentido da ação e o nome acessível completo.
* **RF-12** Sem dependência nova e sem componente de botão compartilhado nesta feature.
* **RF-13** Breakpoints seguem o contrato da 076 (móvel ≤ 767 px; ajustes internos em 640/480 px quando
  justificados).

### Critérios de sucesso

* **CS-01** Zero controles dos tipos A e D com rótulo em mais de uma linha nas cinco larguras, em todas as rotas.
* **CS-02** Zero rótulos cortados ou sobrepostos.
* **CS-03** Zero rotas com `scrollWidth > clientWidth` após as correções.
* **CS-04** 100% dos 24 candidatos com status final (corrigido, refutado ou isento com justificativa).
* **CS-05** `npm test`, `pytest` e `npm run build` verdes; capturas de 1440 px sem diferença visível.

### Escopo excluído

Reescrita de textos além das variantes curtas; redesenho da barra do Mapa e da toolbar do Canvas (feature de
visualizações móveis); tipografia de títulos e parágrafos; criação de um componente `Button`; cores e temas.

### Pontos para o `speckit.clarify`

1. Item 09 (frase de 50 caracteres na busca): reescrever para um rótulo curto ou tratá-lo como tipo C?
2. Item 06: qual o texto curto aceito para "Explorar meus Livros e Criar Estudos"?
3. A regra vale também em tablet (768–1023 px) ou só em móvel?

## 7. Notas técnicas para o `speckit.plan` (sugestões, não requisitos)

* **Correção na raiz:** `white-space: nowrap` na regra-base de `style.css:31` cobre os controles `<button>` e
  `.button`. Links com classe própria (ex.: `.btn-primary-cta`, `.btn-action-primary`) não herdam a regra e
  precisam de tratamento individual.
* **Risco da correção na raiz:** um botão que não quebra e é mais largo que o contêiner passa a **estourar** em vez
  de quebrar. Por isso cada grupo sem `flex-wrap` precisa ser revisto junto; a mudança global sozinha troca um
  defeito por outro.
* **Isenção do tipo C:** `white-space: normal` explícito nas classes listadas.
* **Tipo E por conteúdo, não por breakpoint:** `flex-wrap: wrap` com `flex: 1 1 12ch` no texto e `flex: 0 0 auto`
  no botão faz o empilhamento acontecer sozinho.
* **`.button-sm`:** é usada em `BookView`, `TrashView` e `CaptureItemCard`, mas não encontrei definição global.
  Confirmar onde está definida antes de mexer.
* **Medição em tela** (colar no console do navegador, com dados fictícios, em cada rota e largura):

  ```js
  [...document.querySelectorAll('button, .button, a[class*="btn"]')]
    .filter(el => el.offsetParent && el.textContent.trim())
    .map(el => {
      const r = document.createRange(); r.selectNodeContents(el)
      const linhas = new Set([...r.getClientRects()].filter(q => q.width > 1).map(q => Math.round(q.top)))
      return { texto: el.textContent.trim().slice(0, 40), classe: el.className, linhas: linhas.size }
    })
    .filter(x => x.linhas > 1)
  ```

  Ícones alinhados fora da linha do texto podem gerar falso positivo; conferir visualmente os resultados.
* **Teste-guarda:** asserção estática de que a regra-base contém a proteção e de que a lista de isentos (tipo C)
  é a registrada no contrato.
* **Ambiente:** banco descartável e dados fictícios, conforme `specs/076-estrategia-responsiva/quickstart.md`.
  Nenhuma captura do acervo real.
