# Feature Specification: Rótulos de Botões e Linhas Texto + Botão em Telas Estreitas

**Feature Branch**: `079-rotulos-botoes-responsivos`  
**Created**: 2026-10-12  
**Status**: Draft  
**Input**: Rascunho de especificação da Feature 0.8.13.5 ("Textos mais botões" / quebra de rótulos e linhas híbridas em viewports de 320px a 767px).

Esta feature estabelece uma regra arquitetural unificada para evitar que rótulos de botões quebrem em múltiplas linhas ou desalinhem controles e textos adjacentes em telas estreitas, substituindo remendos pontuais por uma abordagem sistemática por taxonomia de controle.

---

## 1. Problema e Causa Raiz

Em várias telas do Caderno de Leitura, botões de ação com texto quebram o rótulo entre palavras em dispositivos móveis, gerando botões verticalmente espessos e desalinhados de seus vizinhos. O mesmo ocorre em linhas que combinam um texto/título com um botão de ação lateral.

### Diagnóstico Técnico
1. **Ausência de proteção na regra-base**: Em `src/style.css:31`, a regra geral `button, .button { display: inline-flex; ... }` não define `white-space`. Por padrão, o rótulo quebra entre palavras quando submetido a compressão.
2. **Comportamento em contêineres flex**: O botão é tratado como item flexível com `flex-shrink: 1` e largura mínima determinada pela maior palavra isolada. Faltando espaço, o navegador contrai o botão até essa palavra mínima e quebra as demais para a linha seguinte, em vez de disparar quebra de linha do grupo.
3. **Ausência de componente de botão compartilhado**: Quase todos os controles (340 de 367) dependem de estilos ad-hoc ou sofrem sem proteção.
4. **Linhas híbridas "texto + botão"**: Falta de regras de quebra estruturada faz com que o texto fique comprimido ilegível ou o botão seja estrangulado.

---

## 2. Taxonomia de Controles

Os controles da interface são classificados em 5 tipos normativos:

| Tipo | Denominação | Características | Exemplos no Código | Regra Normativa |
|---|---|---|---|---|
| **A** | **Ação** | Rótulo fixo e curto, com ou sem ícone | "Importar estudo", "Excluir definitivamente" | **Nunca quebra**. Se o espaço for insuficiente, quem se reorganiza é o contêiner ou grupo (quebra de linha, wrap, ou variante curta). |
| **B** | **Rótulo com Dado** | Contém dado variável oriundo do acervo | "Voltar a {{ capítulo }}", Nome de categoria | Uma linha obrigatória com reticências (`text-overflow: ellipsis; white-space: nowrap`); texto completo exposto em `title` e `aria-label`. |
| **C** | **Botão-Cartão** | Título + descrição explicativa multilinha | `confirm-choice-card`, modais de conflito de concorrência | **Isento da regra geral**: múltiplas linhas são intencionais por design editorial. Título interno não quebra. |
| **D** | **Abas e Segmentos** | Divisão de abas de largura igual (`flex: 1`) | Abas do Importar, do Dashboard, filtros da Lixeira | **Nunca quebra**. Se não couber: faixa horizontal rolável (`.tabs-scroll-*`) ou variante de rótulo abreviado. |
| **E** | **Linha Texto + Botão** | Título ou descrição ao lado de uma ação | `.section-heading`, `.save-bar`, cabeçalho de cartões | O texto pode quebrar; o botão **não**. Quando o texto atinge largura crítica (< 12ch), o botão empilha na linha seguinte. |

---

## 3. Matriz de Candidatos Identificados (Análise Estática Preliminar)

| ID | Tela / Contexto | Controles Afetados | Tipo | Confiança | Localização no Código |
|---|---|---|---|---|---|
| **01** | Lixeira — barra de lote | "Selecionar todos" · "Restaurar selecionados" · "Excluir definitivamente" em 95vw | A | Alta | `views/TrashView.vue:650-666` |
| **02** | Lixeira — cartões | "Restaurar..." + "Excluir definitivamente" | A | Média | `views/TrashView.vue:534-543, 612-621` |
| **03** | Lixeira — filtros | "Estudos individuais (N)" | D | Média | `views/TrashView.vue:444-464` |
| **04** | Revisão — início de sessão | "Iniciar Sessão Estruturada do Livro" + "Rápida (10 itens)"; "Prática Rápida neste Hub (N)" | A | Alta | `views/ReviewHubView.vue:257-272` |
| **05** | Revisão — abas | "Prática de Revisão" · "Histórico de Sessões" | D | Média | `views/ReviewHubView.vue:202-212` |
| **06** | Revisão — estado vazio | "Explorar meus Livros e Criar Estudos" (largura excessiva para 320px) | A | Alta | `components/review/ReviewPedagogicalEmpty.vue:151-168` |
| **07** | Resumos de revisão / sessão | "Concluir e voltar ao acervo" + "Revisar mais 10"; "Retornar à Central de Revisão" + "Ir para o Livro" | A | Alta | `components/review/ReviewSummaryModal.vue:91-99`, `components/session/SessionSummaryModal.vue:107-115` |
| **08** | Importar — abas móveis | "Texto da Fonte" · "Prévia Estruturada" (`flex: 1`) | D | Média | `views/ImportView.vue:358-368`, `style.css:537` |
| **09** | Busca global | "Buscar estudos com qualquer um dos termos (Modo OR)" (50 caracteres) | A | Alta | `components/search/GlobalSearchModal.vue:333` |
| **10** | Landing e rodapé público | "Criar Conta Gratuita" + "Já possuo conta (Entrar)" com altura fixa de 48px | A | Média | `components/landing/HeroSection.vue:24-29`, `PublicFooter.vue:18-22` |
| **11** | Mapa — barra móvel | "Conectar a.../Toque no destino..." · "Novo Estudo" · "Ver Estudo" | A | Alta | `components/views/StudyMapView.vue:744-765` |
| **12** | Inbox — cartão de captura | "Promover para Estudo" · "Vincular a Estudo" · "Mover para Pendentes" | A | Baixa | `components/inbox/CaptureItemCard.vue:266-309` |
| **13** | Destaques — cartão | "Abrir no Estudo" · "Adicionar reflexão" · "Expandir contexto" | A | Baixa | `components/highlights/HighlightCard.vue:195-383` |
| **14** | Ajustes | "Restaurar padrões de aparência" · "Limpar chaves obsoletas" · "Salvar Alterações..." | A | Média | `views/SettingsView.vue:807-1057` |
| **15** | Ajustes — sessões | "Desvincular Google" · "Sair de todos os outros..." · "Revogar" | A | Média | `components/auth/SessionsManager.vue:218-308` |
| **16** | Modais de conta | "Excluir definitivamente" · "Sim, desativar conta" · "Reativar Minha Conta" + "Cancelar" | A | Média | `components/settings/*.vue` |
| **17** | Avatar | "Usar foto da conta Google" · "Remover foto atual" | A | Média | `components/profile/AvatarUploadModal.vue:305-345` |
| **18** | Backup | "Baixar pacote completo (.zip)" · "Baixar apenas banco (.db)" | A | Média | `components/DatabaseBackup.vue:147-167` |
| **19** | Livro | "Importar estudo" ao lado do seletor de visualização; "Adicionar capítulo" | A / E | Baixa | `views/BookView.vue:416-437` |
| **20** | Leitor | "Voltar a {{ capítulo }}"; "Ativar modo foco" · "Leitura Ativa" | B / A | Média | `views/StudyView.vue:485`, `components/ReaderTools.vue:80-90` |
| **21** | Dashboard | Abas "Para Conectar (N)" · "Conexões (N)"; "Exibir todas as atividades" | D / A | Baixa | `views/DashboardView.vue:278-378` |
| **22** | Edição de estudo | "Histórico de versões" · "Descartar rascunho" · "Salvar alterações" | A | Média | `views/StudyEditView.vue:145-192` |
| **23** | Apoie / Admin | "Repositório Oficial no GitHub"; "Salvar Configurações de Apoio"; Abas | A / D | Média | `views/SupportView.vue:140`, `views/AdminView.vue:382-769` |
| **24** | Linhas texto + botão genéricas | `.section-heading` (sem flex-wrap quando falta `.wrap`), `.save-bar` | E | Média | `style.css:148, 173` |

*Nota de fronteira*: O redesenho espacial da barra móvel do Mapa (item 11) pertence à Feature de Visualizações Móveis. Nesta feature, o Mapa recebe apenas a regra de proteção global para impedir quebras bizarras de rótulos.

---

## 4. Regra de Resolução quando o Rótulo Não Cabe

Quando o contêiner for estreito demais para comportar os botões em linha única, aplica-se a seguinte ordem de preferência ao grupo (nunca quebrando o texto do botão):

1. **Quebra de linha ou empilhamento do grupo**: O contêiner usa `flex-wrap: wrap` e os botões descem inteiros ou expandem para largura total (`width: 100%`).
2. **Variante de rótulo curto**: Alternância entre `.btn-text-full` e `.btn-text-short` através de media queries ou classes de visibilidade (ex.: "Exportar anotações" $\to$ "Exportar", "Restaurar selecionados" $\to$ "Restaurar").
3. **Apenas ícone com acessibilidade**: Exibição somente do ícone acompanhado de `title` e `aria-label` estritos (reservado para ações inequívocas: lixeira, fechar, copiar).
4. **Menu de ações secundárias ("...")**: Agrupamento em menu contextual suspenso conforme padrão do contrato da Feature 076.

### Restrições Absolutas
- Proibido reduzir o tamanho de fonte abaixo de `0.8125rem` (13px).
- Proibido aplicar reticências (`...`) em rótulos de ações fixas (Tipo A).
- Proibido manter altura fixa em botões cujo conteúdo possa ter variação de linha.
- Proibido causar rolagem horizontal na página (`scrollWidth > clientWidth`).

---

## 5. User Scenarios & Testing

### User Story 1 - Levantamento e Confirmação de Rótulos em Tela (Priority: P1)
Como responsável pelo produto, quero auditar a renderização real de botões e linhas híbridas em viewports de 320, 375, 390, 430 e 767px, para confirmar com precisão quais dos 24 candidatos quebram e demandam correção estrutural.

**Why this priority**: Evita intervenções desnecessárias ou baseadas em palpites, focando a implementação nas ocorrências efetivas em tela.

**Independent Test**: Executar rotina de inspeção de retângulos de clientes de texto em todas as rotas e larguras-alvo com dados sintéticos, gerando tabela definitiva de validação.

**Acceptance Scenarios**:
1. **Dado** a aplicação em execução com banco de dados descartável e dados fictícios, **quando** executada a verificação nas 5 larguras-alvo, **então** é gerado o inventário confirmado com classificação taxonômica (Tipos A a E).

---

### User Story 2 - Botões de Ação com Rótulo Íntegro em Uma Linha (Priority: P1)
Como leitor no celular (320px a 767px), quero que todo botão de ação mantenha seu texto em uma linha única e alinhado aos botões vizinhos, para que eu reconheça a ação imediatamente sem botões disformes ou cortados.

**Why this priority**: Rótulos partidos em 2 ou 3 linhas tornam botões desproporcionais, prejudicam a leitura rápida e provocam toques acidentais.

**Independent Test**: Navegar pelas rotas da Lixeira, Central de Revisão, Importação, Modais e Ajustes nas larguras de 320px e 375px; verificar que 100% dos botões dos Tipos A e D exibem seus rótulos em linha única.

**Acceptance Scenarios**:
1. **Dado** qualquer botão dos Tipos A ou D em tela de 320px a 767px, **quando** renderizado, **então** seu texto permanece obrigatoriamente em uma linha sem quebra entre palavras.
2. **Dado** um grupo de ações onde a soma dos botões excede a largura da tela, **quando** o espaço aperta, **então** o contêiner faz wrap limpo dos botões ou emprega variantes curtas de rótulo, sem deformar os botões.

---

### User Story 3 - Linhas "Texto + Botão" Legíveis e sem Estrangulamento (Priority: P2)
Como leitor no smartphone, quero que cabeçalhos e barras com texto ao lado de botões mantenham o texto legível e empilhem o botão na linha seguinte quando o espaço for exíguo, para não ler textos truncados em colunas estreitas.

**Why this priority**: Em `.section-heading` e barras de salvamento, botões laterais com largura rígida esmagam o texto do título para colunas de 2 ou 3 palavras.

**Independent Test**: Inspecionar linhas híbridas (Tipo E) em 320px; constatar que títulos e descrições mantêm largura confortável e o botão desce para baixo do título quando a largura de texto for menor que 12ch.

**Acceptance Scenarios**:
1. **Dado** uma linha híbrida do Tipo E em viewport de 320px, **quando** renderizada, **então** o texto não é estrangulado a menos de 12 caracteres por linha.
2. **Dado** o espaço lateral insuficiente para texto e botão lado a lado, **quando** ocorre a quebra, **então** o botão transita para a linha seguinte mantendo alinhamento à esquerda ou largura total.

---

### User Story 4 - Regra Arquitetural Protegida e Testada (Priority: P3)
Como desenvolvedor e mantenedor, quero que a regra-base de botões resida no CSS central e seja protegida por teste automatizado que falhe se novos botões forem introduzidos sem a conformidade da taxonomia.

**Why this priority**: Previne regressões futuras e garante que novas telas adotem o comportamento sem retrabalho.

**Independent Test**: Executar teste unitário que valida a existência de `white-space: nowrap` na regra geral e a isenção expressa dos componentes do Tipo C.

**Acceptance Scenarios**:
1. **Dado** a suíte de testes de frontend, **quando** executado `npm test`, **então** o teste-guarda verifica a proteção global de botões e a ausência de violações na lista de candidatos auditados.

---

## 6. Functional Requirements

- **RF-01**: Produzir inventário auditado dos 24 candidatos, classificando-os nos Tipos A a E.
- **RF-02**: Rótulos dos Tipos A e D DEVEM permanecer em linha única em 320, 375, 390, 430 e 767px.
- **RF-03**: Quando o rótulo de uma ação não couber em linha única, aplicar a ordem de resolução da seção 4 (wrap de grupo, rótulo curto, ícone acessível ou menu "...").
- **RF-04**: Rótulos do Tipo B DEVEM truncar com reticências em uma linha única e expor o texto completo via `title` e `aria-label`.
- **RF-05**: Controles do Tipo C (botões-cartão explicativos) ficam expressamente isentos da proibição de quebra de linha.
- **RF-06**: Linhas híbridas do Tipo E DEVEM permitir quebra do texto descritivo e empilhar a ação na linha de baixo quando o texto dispuser de menos de 12ch.
- **RF-07**: Nenhum botão com texto pode ter altura fixa que corte o rótulo (ex.: botões da landing de 48px com overflow oculto).
- **RF-08**: Alvos de toque DEVEM manter no mínimo $44 \times 44\text{ px}$ em telas móveis.
- **RF-09**: Nenhuma alteração pode criar transbordamento ou rolagem horizontal na página (`scrollWidth > clientWidth`).
- **RF-10**: O comportamento em desktop ($\ge 1024\text{px}$) NÃO deve sofrer alteração visual.
- **RF-11**: Variantes de rótulo curto (.btn-text-short) DEVEM preservar clareza semântica e nome acessível.
- **RF-12**: Não introduzir dependências externas nem componente `Button` genérico desnecessário.
- **RF-13**: Breakpoints seguem os padrões do contrato da Feature 076 (móvel $\le 767\text{px}$, intermediários em 640px/480px quando justificados).

---

## 7. Success Criteria

- **SC-01**: Zero controles dos Tipos A e D com rótulos quebrados em mais de uma linha nas larguras de 320px a 767px.
- **SC-02**: Zero rótulos cortados, sobrepostos ou ocultos indevidamente.
- **SC-03**: Zero rotas apresentando rolagem horizontal (`scrollWidth > clientWidth`) após as intervenções.
- **SC-04**: 100% dos 24 candidatos com status formalizado (corrigido, refutado ou isento).
- **SC-05**: 100% de testes e compilações (`npm test`, `pytest`, `npm run build`) verdes sem regressão visual no desktop.

---

## 8. Escopo Excluído

- Reescrita ampla de cópia do sistema além das variantes curtas.
- Redesenho da barra inferior móvel do Mapa ou do Canvas (escopo da Feature de Visualizações Móveis).
- Tipografia de títulos e parágrafos fora do escopo de linhas híbridas Tipo E.
- Criação de biblioteca de componentes de UI.
