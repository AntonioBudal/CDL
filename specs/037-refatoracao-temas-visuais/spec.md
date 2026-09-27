# Feature Specification: F09.5 — Refatoração de Temas, Persistência e Correções Visuais

**Feature Branch**: `037-refatoracao-temas-visuais`

**Created**: 2026-09-26

**Status**: Draft

**Input**: User description: "Feature 9.5 - Refatoração de Temas, Persistência e Correções Visuais: simplificação de nomenclatura de temas, exclusão de 5 temas distrativos, adição de 5 novos temas minimalistas, correção de persistência no F5/navegação, restrições dimensionais de SVGs (estudos compartilhados, botão compartilhar, modal exportar) e garantia de contraste dinâmico em dropdowns, tags e cabeçalhos de agrupamento."

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Persistência Imediata e Prevenção de Reset de Tema (Priority: P1) 🎯 MVP

Como leitor do Leitorum, quero que a minha preferência de tema seja lida e aplicada de forma síncrona imediatamente na abertura da página ou ao recarregar (F5), para que a interface nunca pisque no tema errado, nunca reverta ao padrão e não sofra perda de estado durante a navegação entre rotas.

**Why this priority**: É a fundação crítica de usabilidade da interface visual. Sem persistência síncrona confiável, qualquer personalização de tema é frustrante e descartada ao menor reload ou transição de tela.

**Independent Test**: Selecionar um tema qualquer (ex.: "Nord"), recarregar a página com F5 e navegar entre as rotas (`/`, `/livro/1`, `/ajustes`); o tema selecionado deve permanecer ativo de forma ininterrupta, sem piscar e sem reverter para o tema inicial da lista.

**Acceptance Scenarios**:

1. **Given** que o leitor definiu um tema ativo no aplicativo, **When** recarrega a página no navegador (F5 ou Ctrl+R), **Then** o tema salvo no `localStorage` é aplicado antes da renderização do DOM, sem flash de tema incorreto e sem reversão para o padrão.
2. **Given** que o leitor está com o aplicativo aberto, **When** navega entre diferentes telas e rotas via Vue Router, **Then** as classes e atributos de tema (`data-theme`) no documento raiz permanecem inalterados.
3. **Given** um leitor que possuía salvo no navegador um dos temas excluídos (ex.: `porcelana` ou `breu`), **When** o aplicativo é inicializado, **Then** o sistema executa migração automática e transparente para o substituto minimalista correspondente (`papel-fosco` ou `noite-suave`), sem quebrar a tela.

---

### User Story 2 - Simplificação de Nomenclatura, Exclusão de Temas Distrativos e Novos Temas Minimalistas (Priority: P2)

Como leitor focado no estudo reflexivo, quero que a lista de temas ofereça opções limpas, discretas e de baixo contraste, com nomes diretos e sem adjetivos excessivos, para que a experiência de leitura seja confortável para os olhos durante longas sessões.

**Why this priority**: A identidade do Leitorum exige foco na leitura e sobriedade estética, eliminando opções berrantes ou distrativas e oferecendo paletas ergonômicas refinadas.

**Independent Test**: Abrir o seletor de temas nos Ajustes; constatar que os nomes estão simplificados sem prefixo, que os 5 temas excluídos não aparecem mais e que os 5 novos temas minimalistas podem ser aplicados com cores e contrastes fiéis aos requisitos.

**Acceptance Scenarios**:

1. **Given** a lista de temas nos Ajustes, **When** o leitor visualiza as opções, **Then** todos os temas exibem apenas seu nome substantivo simplificado, sem prefixos compostos com travessão.
2. **Given** o catálogo do sistema, **When** o leitor busca por `Porcelana`, `Breu`, `Vinil`, `Sequoia` ou `Véspera`, **Then** esses temas estão completamente removidos das opções e seus estilos CSS obsoletos foram expurgados.
3. **Given** os 5 novos temas cadastrados, **When** o leitor ativa qualquer um deles, **Then** as seguintes paletas de baixo contraste são aplicadas corretamente:
   - **Papel Fosco (Claro)**: Fundo `#f5f5f5`, Texto `#333333`, Destaque ardósia/cinza-azulado.
   - **Noite Suave (Escuro)**: Fundo `#1e1e24`, Texto `#d4d4d4`, Destaque azul acinzentado opaco.
   - **Cinza Neutro (Claro)**: Fundo `#e8e8e8`, Texto `#2b2b2b`, Destaque cinza médio-escuro.
   - **Grafite (Escuro)**: Fundo `#222222`, Texto `#cccccc`, Destaque marrom-acinzentado ou bege escuro discreto.
   - **Monocromático (Claro)**: Fundo `#ffffff`, Texto `#111111`, Destaque preto ou contornos pretos.

---

### User Story 3 - Correção Dimensional e Blindagem de SVGs e Ícones (Priority: P3)

Como leitor interagindo com a plataforma, quero que todos os botões, telas vazias e modais apresentem ícones com proporções harmônicas e fixas, para que nenhum elemento gráfico estoure a tela ou quebre a diagramação dos textos.

**Why this priority**: Ícones desproporcionais quebram a hierarquia visual, deformam botões essenciais e geram sensação de defeito grave na aplicação.

**Independent Test**: Acessar a aba "Estudos Compartilhados", a visualização de um estudo e abrir o modal "Exportar Estudo"; verificar que nenhum ícone excede o tamanho esperado, que o botão "Compartilhar" mantém o texto em uma linha única e que o modal de exportação flui com proporções estáveis.

**Acceptance Scenarios**:

1. **Given** a aba "Estudos Compartilhados" sem itens (estado vazio), **When** a tela é exibida, **Then** o ícone central ilustrativo possui tamanho contido e delimitado (`max-width: 120px`), sem tomar a viewport inteira.
2. **Given** o cabeçalho de ações de um estudo, **When** o botão "Compartilhar" é renderizado, **Then** o ícone possui dimensão restrita (`1.2em` ou `18px`), layout flexível alinhado ao centro com espaçamento de 8px e a palavra "Compartilhar" permanece em linha única ininterrupta (`white-space: nowrap`).
3. **Given** o diálogo modal "Exportar Estudo", **When** o modal é aberto, **Then** os ícones e caixas dos seletores de formato e opções mantêm dimensões fixas (`24px`), alinhados à esquerda sem estourar e sem deformar a grade.

---

### User Story 4 - Contraste Dinâmico e Legibilidade em Modais, Tags e Acordeões (Priority: P4)

Como leitor utilizando temas claros ou escuros, quero que todos os textos informativos, rótulos de status e cabeçalhos colapsáveis tenham contraste automático calibrado com a cor do seu fundo, para que nunca fiquem invisíveis ou difíceis de ler.

**Why this priority**: Acessibilidade visual é obrigatória. Textos escuros sobre fundos escuros ou textos claros sobre fundos claros impedem a leitura e violam os princípios do produto.

**Independent Test**: Alternar entre temas claros (ex.: "Papel Fosco") e escuros (ex.: "Noite Suave"); inspecionar o modal de exportação, os badges de status de estudo e o botão de recolher/expandir grupos (`group-toggle-btn`); constatar legibilidade nítida e contraste conforme as normas WCAG AA em todos os estados.

**Acceptance Scenarios**:

1. **Given** o modal "Exportar Estudo", **When** renderizado sob qualquer tema ativo, **Then** todos os textos descritivos e títulos herdam as variáveis semânticas do tema (`--color-text`, `--color-muted`), permanecendo plenamente legíveis sem dependência de fallbacks inadequados.
2. **Given** o componente de status de leitura (`StudyStatusBadge`), **When** o menu suspenso ou pílula é exibido, **Then** o contraste entre a cor de fundo do status e a fonte é garantido dinamicamente para fundos claros e escuros.
3. **Given** a visualização de estudos agrupados por seção (`GroupSection`), **When** o cabeçalho colapsável (`.group-toggle-btn`) é exibido sobre fundos coloridos ou de destaque, **Then** o título (`.group-title`) e a seta (`.group-chevron-wrap`) adaptam suas cores de texto/traço (forçando branco em tons escuros/saturados e cor escura em fundos claros), mantendo contraste absoluto.

---

## Edge Cases

- O que acontece se o leitor tiver um tema personalizado legado gravado no `localStorage` que foi removido? O sistema detecta o valor obsoleto na inicialização e o substitui pelo fallback sem interromper o funcionamento.
- Como o sistema se comporta sob modo de alto contraste do sistema operacional ou preferência `prefers-contrast: more`? As regras de contraste dinâmico respeitam e reforçam bordas e legibilidade.
- O que ocorre se um texto de título de agrupamento for muito longo no cabeçalho colapsável? O texto quebra naturalmente ou trunca com elipse sem sobrepor o chevron ou os badges de contagem.
- O que ocorre se a API de preferências do backend demorar a responder durante a navegação? A preferência local lida de forma síncrona prevalece no DOM e evita qualquer "pulo" de tema na tela.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE simplificar a nomenclatura de todos os temas visuais, suprimindo o prefixo composto e mantendo o identificador conciso e consagrado: os 5 temas preservados passam a se chamar `Sépia`, `E-Ink`, `Solarized`, `Nord` e `Cyber`.
- **FR-002**: O sistema DEVE remover integralmente do código (CSS, stores, catálogos e interface de Ajustes) os temas obsoletos: `Porcelana`, `Breu`, `Vinil`, `Sequoia` e `Véspera`.
- **FR-003**: O sistema DEVE implementar e calibrar os 5 novos temas minimalistas de baixo contraste: `Papel Fosco`, `Noite Suave`, `Cinza Neutro`, `Grafite` e `Monocromático`.
- **FR-004**: O sistema DEVE definir `Papel Fosco` (`papel-fosco`, claro) como o tema padrão oficial de fallback da plataforma para novos usuários ou quando o tema anterior salvo tiver sido excluído.
- **FR-005**: A aplicação DEVE ler e aplicar a preferência de tema do `localStorage` de forma síncrona no carregamento da página antes da montagem e hidratação do Vue (`app.mount`).
- **FR-006**: A store e os composables de preferências DEVEM manter o tema ativo unificado através de um ID nominal único do tema gravado em ambos (`localStorage` e store de preferências), eliminando valores genéricos (`dark`/`light`) que anteriormente sobrescreviam o tema real em navegações e recargas (F5).
- **FR-007**: O sistema DEVE aplicar contenção dimensional física (`max-width: 120px; height: auto`) ao elemento visual de estado vazio em "Estudos Compartilhados".
- **FR-008**: O botão "Compartilhar" DEVE possuir alinhamento flex centralizado, espaçamento delimitado (8px), ícone com proporção fixa (`1.2em` / `18px`) e propriedade `white-space: nowrap` para impedir divisão de palavras.
- **FR-009**: O modal "Exportar Estudo" DEVE travar o tamanho dos SVGs de seleção em 24x24px, estruturar seus itens em grade/flex alinhada sem sobreposição e herdar as variáveis semânticas de cor do tema ativo (`--color-text`, `--color-muted`, `--color-surface`, `--color-border`).
- **FR-010**: O componente `StudyStatusBadge` DEVE assegurar legibilidade em qualquer tema, aplicando cores de texto contrastantes para cada fundo de status em temas claros e escuros.
- **FR-011**: O cabeçalho de agrupamento (`GroupSection.vue`) DEVE garantir contraste visual absoluto para `.group-toggle-btn`, `.group-title` e `.group-chevron-wrap`, forçando fonte e traço claros/brancos sobre fundos escuros ou saturados e escuros sobre fundos claros.

---

### Key Entities

- **ThemeDefinition**: Representa a configuração visual de um tema, contendo identificador único (`id`), nome de exibição (`name`), esquema de cores (`light` ou `dark`) e paleta de variáveis CSS associadas.
- **VisualPreferences**: Representa o conjunto de preferências estéticas salvas pelo leitor (tema ativo, fonte, escala tipográfica, densidade, alinhamento e superclasse cinemática).

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: O tempo de aplicação do tema salvo no carregamento da página é zero perceptível (0ms de atraso visual / sem FOUC de tema errado ao pressionar F5).
- **SC-002**: 100% das transições de rotas preservam o tema selecionado sem regressão para o padrão.
- **SC-003**: 100% dos botões e áreas inspecionadas cumprem a proporção de contraste mínima de 4.5:1 (nível AA do WCAG 2.1) em todos os temas suportados.
- **SC-004**: Zero ocorrências de quebra de linha inadequada ou ícones com dimensões superiores ao seu contêiner em resoluções de desktop e mobile.
- **SC-005**: O catálogo de temas fica consolidado exatamente em 10 temas refinados (5 clássicos preservados e 5 novos minimalistas).

---

## Assumptions

- A biblioteca de ícones do projeto (`lucide-vue-next` e SVG inline) continua sendo a fonte primária de elementos gráficos vetoriais.
- A persistência local em `localStorage` sob as chaves oficiais permanece como salvaguarda primária offline e instantânea.
- Nenhuma alteração de schema de banco de dados no backend é necessária para esta feature, pois a preferência de tema no backend aceita strings correspondentes aos identificadores.

---
