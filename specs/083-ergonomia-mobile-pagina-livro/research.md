# Research & Architectural Decisions: F0.9.02 — Ergonomia Mobile e Descongestionamento da Página do Livro

**Feature**: `specs/083-ergonomia-mobile-pagina-livro`  
**Date**: 2026-10-21  
**Status**: Completed  

---

## 1. Contexto e Objetivos Técnicos

A página do livro ([`BookView.vue`](file:///c:/Users/User/caderno/caderno-leitura-0.1/frontend/src/views/BookView.vue)) reúne o acervo de capítulos e anotações de uma obra específica. Na versão desktop (`>= 768px`), a interface adota com sucesso uma arquitetura horizontal em 3 faixas (Cabeçalho com metadados, Faixa Superior de Capítulos, Palco Central de Estudos e Faixa Inferior do Inspetor Analítico).

Entretanto, em dispositivos móveis (`<= 767px`), a composição original sofre de empilhamento vertical excessivo:
- O cabeçalho consome até 450px de altura vertical com capa grande, título, autor, categorias e 4 botões de ação em formato de pílula expandida.
- A faixa de capítulos renderiza simultaneamente um `<select>` nativo e a esteira horizontal de pílulas roláveis (`.chapters-nav-strip`), criando redundância de controles e desorientação táctil.
- O inspetor analítico na base da tela repete dados estáticos em tela pequena, competindo por espaço com a leitura dos estudos.

O objetivo desta pesquisa é definir a abordagem arquitetural mais limpa, acessível e performática para descongestionar a página no mobile sem provocar regressões no layout desktop.

---

## 2. Decisões Técnicas Consolidadas

### Decisão 1: Cabeçalho Condensado em Formato de Linha Dupla no Mobile
- **Abordagem Escolhida:**
  - Breakpoint móvel: `@media (max-width: 767px)`.
  - **Linha 1:** Miniatura da capa em proporção condensada de 48x72px (usando o componente [`BookCover.vue`](file:///c:/Users/User/caderno/caderno-leitura-0.1/frontend/src/components/BookCover.vue) ou regra CSS restritiva), título da obra com truncamento inteligente em até 2 linhas (`-webkit-line-clamp: 2; overflow: hidden; text-overflow: ellipsis;`) e nome do autor acompanhado pelo ano.
  - **Linha 2:** Chips de categoria compactos e botão de ações agrupadas ("Ações do livro") que aciona menu suspenso ou modal/drawer contextual.
- **Justificativa:** Reduz a altura vertical do cabeçalho de mais de 450px para aproximadamente 130–150px, liberando mais de 300px na primeira dobra da tela.
- **Alternativas Consideradas:**
  - *Ocultar completamente a capa no celular:* Rejeitado porque a capa é um referencial visual afetivo e mnemônico essencial para o leitor.
  - *Manter os 4 botões de ação em grade 2x2:* Rejeitado porque ocupa área nobre com ações pouco frequentes (como "Mover para a lixeira" ou "Editar livro").

### Decisão 2: Agrupamento de Ações do Livro via `DropdownMenu.vue`
- **Abordagem Escolhida:**
  - Reaproveitar o componente acessível já existente [`DropdownMenu.vue`](file:///c:/Users/User/caderno/caderno-leitura-0.1/frontend/src/components/ui/DropdownMenu.vue) em `components/ui/DropdownMenu.vue`.
  - O gatilho móvel será um botão compacto e acessível com rótulo "Ações do livro" e ícone indicador de abertura.
  - O menu contextual abrigará as 4 ações primárias da obra:
    1. **Modo foco** (`toggleFocusMode`): com indicação de estado ativo/inativo.
    2. **Exportar anotações** (`exportModalOpen = true`).
    3. **Editar livro** (`isEditingBook = true`).
    4. **Mover para a lixeira** (`confirmTrashBookOpen = true`): estilizado com classe de perigo/alerta.
  - No desktop (`>= 768px`), o menu agrupado fica oculto (`display: none !important;`) e a barra tradicional de botões em pílula (`.header-actions`) permanece plenamente visível.
- **Justificativa:** Componente padronizado, com controle de teclado (Setas, Enter, Escape), fechamento por clique fora e foco previsível WAI-ARIA.
- **Alternativas Consideradas:**
  - *Criar um drawer móvel novo:* Rejeitado para evitar sobrecarga de código (o dropdown existente atende perfeitamente ao caso com alvos de 44px).

### Decisão 3: Unificação da Faixa de Capítulos sem Redundância
- **Abordagem Escolhida:**
  - No breakpoint móvel (`<= 767px`), a esteira horizontal de pílulas roláveis (`.chapters-nav-strip`) é suprimida via CSS (`display: none !important;`).
  - A faixa móvel exibe um cabeçalho único e coeso contendo:
    - O seletor de capítulos (`.chapters-mobile-select`) atualizado para apresentar o número, nome e contagem de estudos de cada capítulo.
    - O botão compacto de novo capítulo inline (`.add-chapter-pill-btn`), permitindo criar novos capítulos com alvos de toque de 44px.
- **Justificativa:** Elimina a duplicação onde o leitor via um dropdown e logo abaixo as mesmas opções em pílulas, reduzindo a altura da faixa de capítulos de ~150px para ~56px.
- **Alternativas Consideradas:**
  - *Remover o `<select>` e manter apenas as pílulas horizontais:* Rejeitado porque em livros com 20 ou mais capítulos a rolagem horizontal em telas touch torna a localização de capítulos finais lenta e cansativa.

### Decisão 4: Inspetor Analítico Recolhível por Padrão no Celular
- **Abordagem Escolhida:**
  - Adicionar estado reativo local em `BookView.vue`: `const isInspectorExpandedMobile = ref(false)`.
  - No mobile (`<= 767px`), a barra do inspetor (`.inspector-horizontal-bar`) inicia recolhida, apresentando apenas um botão de controle acessível:
    - Rótulo dinâmico: `isInspectorExpandedMobile.value ? 'Ocultar detalhes do livro' : 'Ver detalhes do livro'`
    - Atributo WAI-ARIA: `:aria-expanded="isInspectorExpandedMobile"`
    - Ícone de chevron para indicar direção.
  - Ao expandir, exibe a grade de métricas analíticas (Capítulo selecionado, Total de capítulos, Estudos no capítulo e Card de estudo em foco).
  - No desktop (`>= 768px`), o botão de alternância fica oculto (`display: none !important;`) e a grade de métricas permanece sempre aberta (`display: flex !important;`).
- **Justificativa:** Libera 100% da área útil do rodapé da tela no celular, permitindo que a lista ou grade de estudos tenha prioridade visual absoluta.
- **Alternativas Consideradas:**
  - *Remover completamente o inspetor no celular:* Rejeitado porque leitores podem querer conferir o resumo numérico de estudos e capítulos da obra sob demanda.

### Decisão 5: Conformidade com os 10 Temas e Acessibilidade
- **Abordagem Escolhida:**
  - Todas as classes e elementos novos (menu móvel, seletor unificado, gatilho do inspetor) utilizam estritamente variáveis de tema (`--color-surface`, `--color-text`, `--color-border`, `--color-muted`, `--color-accent`, etc.).
  - Zero uso de cores hexadecimais fixas.
  - Alvos táteis garantidos em no mínimo 44x44px (`min-height: 44px; min-width: 44px;`) para botões de toque.
  - Respeito à diretriz `prefers-reduced-motion` com transições suprimidas quando solicitadas pelo leitor.
  - Zero emojis em código, estilos e textos.

---

## 3. Resumo de Impacto Ergonômico

| Elemento | Altura Anterior (Mobile) | Nova Altura (Mobile) | Espaço Economizado |
| :--- | :--- | :--- | :--- |
| **Cabeçalho do Livro** | ~450px (capa grande + botões empilhados) | ~140px (linha dupla com capa 48x72 e menu agrupado) | **~310px** |
| **Faixa de Capítulos** | ~140px (select + pílulas roláveis duplicadas) | ~56px (seletor único unificado com botão inline) | **~84px** |
| **Inspetor Analítico** | ~180px (grade analítica sempre expandida na base) | ~44px (recolhido por padrão com botão de expansão) | **~136px** |
| **Total Liberado para Estudos** | — | — | **~530px de altura útil** |
