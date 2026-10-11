# Research & Architectural Decisions: Tela Placeholder do Document Intelligence

**Feature**: F0.3.5 — Tela Placeholder do Document Intelligence  
**Branch**: `069-document-intelligence-placeholder`  
**Date**: 2026-10-11  

---

## 1. Decisão Técnica: Ponto de Entrada no Hub de Importação (`/importar`)

### Contexto
O usuário precisa de um ponto de entrada claro, elegante e não intrusivo para a funcionalidade de digitalização de cadernos, sem sobrecarregar a barra de navegação global com telas ainda não operacionais.

### Decisão
- Adicionar um card editorial no Ateliê de Importação (`ImportView.vue`), intitulado **"Caderno Manuscrito (Em Pesquisa)"**.
- O card exibe uma breve descrição do objetivo ("Transformar anotações manuscritas de cadernos físicos em estudos estruturados no computador"), badge sutil indicando `"Em Pesquisa"`, ícone SVG representativo de página manuscrita e botão de ação `"Conhecer a proposta"` direcionando para `/digitalizar`.

### Rationale
- O Hub de Importação (`/importar`) já é o lugar conceitual onde o leitor agrega anotações vindas de fora (Kindle, Kobo, textos colados). Posicionar a futura captura física ao lado dessas fontes mantém a coesão semântica.
- Não ocupa espaço fixo de menu na barra superior ou na navegação móvel para um recurso em fase exploratória.

### Alternativas Consideradas
- *Item no menu principal global*: Rejeitado por ocupar espaço nobre na barra de navegação para uma tela que não executa ações ativas.
- *Banner na Caixa de Entrada (`/inbox`)*: Rejeitado como ponto primário, pois a Caixa de Entrada tem foco em triagem de capturas imediatas, embora links cruzados permaneçam válidos.

---

## 2. Decisão Técnica: View Dedicada Estática (`DigitizeNotebookView.vue`)

### Contexto
A tela deve explicar com honestidade o escopo da pesquisa, garantir processamento estritamente local (sem nuvem) e exibir o status das 4 etapas de maturidade.

### Decisão
- Criar a view `caderno-leitura-0.1/frontend/src/views/DigitizeNotebookView.vue`.
- A view conterá:
  1. **Cabeçalho Editorial**: Título "Digitalizar Caderno", subtítulo reflexivo e manifesto de processamento estritamente local ("Soberania de Dados: Suas imagens nunca sairão do seu computador").
  2. **Estrutura de Blocos Explicativa**: Explicação didática de como a página fotografada se desdobrará em título, parágrafos, notas marginais, diagramas e ordem natural de leitura.
  3. **Matriz de Maturidade Técnica (4 Etapas)**: Componente/bloco visual exibindo os 4 estágios fixos com badges semânticos e notas sinceras.
  4. **Ilustração Conceitual Rotulada**: Mockup vetorial estático exemplificando a detecção de blocos com texto fictício (ex.: "Capítulo I — Do Hábito da Leitura"), com aviso claro `"Ilustração Conceitual"`.
  5. **Seção de Ação e Continuidade**: Botões para os fluxos produtivos existentes: "Importar fichamento digitado" (`/importar`) e "Anotar na Caixa de Entrada" (`/inbox`).

### Rationale
- Separação clara de responsabilidades: a view não possui dependências de backend, não dispara chamadas HTTP e opera de modo instantâneo mesmo sem rede ativa.
- Zero simulação enganosa: a ilustração é declarada como mock conceitual.

---

## 3. Decisão Técnica: Isolamento Total de `document-intelligence/` e Backend

### Contexto
O subprojeto `document-intelligence/` é mantido por outro agente de forma independente. Rascunhos como `docs/ldf.md` e `api-local.md` estão em evolução preliminar.

### Decisão
- Nenhum tipo TypeScript, import de código ou schema deve ser compartilhado entre `caderno-leitura-0.1/` e `document-intelligence/`.
- Nenhuma rota ou controller de backend Python deve ser criado.
- Nenhum upload de arquivo (`input[type="file"]`) ou acesso a periféricos de câmera (`navigator.mediaDevices`) deve existir.

### Rationale
- Previne acoplamento precoce e regressões decorrentes de contratos voláteis do subprojeto de pesquisa.
- Garante total conformidade com a Constituição do projeto e com as regras inegociáveis.

---

## 4. Decisão Técnica: Acessibilidade e Imunidade Cromática

### Contexto
A interface deve suportar os 10 temas visuais do Leitorum, navegação por teclado e telas móveis estreitas (< 768px).

### Decisão
- Utilizar exclusivamente tokens CSS semânticos (`--color-surface`, `--color-text`, `--color-border-subtle`, `--color-accent`, `--color-success`, `--color-warning`).
- Evitar cores fixas `#hex` saturadas.
- Touch targets com altura mínima de 44px nos botões e links de navegação.
- Sem uso de emojis em nenhum elemento textual ou visual (uso de SVGs inline com `aria-hidden="true"`).
- Testes automatizados com `node:test` verificando a presença de atributos ARIA, ausência de emojis e estabilidade offline.
