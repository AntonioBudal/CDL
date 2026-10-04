# Data Model: F 0.7.7 — Redesenho da Map View (Criação e Edição de Grafo Semântico)

**Feature**: F 0.7.7 — Redesenho da Map View  
**Created**: 2026-10-04  
**Status**: Completed  

---

## 1. Entidades de Interface e Estrutura do Grafo

### `MapNodeItem` (Nó do Grafo no Mapa)
Representa a projeção bidimensional de um estudo no plano radial do mapa conceitual.

| Campo | Tipo | Descrição |
| :--- | :--- | :--- |
| `study` | `StudySummary` | Dados fundamentais do estudo (id, título, localização, status, etc.). |
| `x` | `number` | Coordenada cartesiana horizontal calculada. |
| `y` | `number` | Coordenada cartesiana vertical calculada. |
| `angle` | `number` | Ângulo polar relativo ao centro em radianos. |
| `ring` | `'core' \| 'primary' \| 'secondary'` | Órbita ocupada pelo nó (núcleo, conexões diretas ou nós distantes). |
| `isCore` | `boolean` | Indica se o nó é o estudo focal/núcleo atual. |
| `degree` | `number` | Total de conexões ativas (inbound + outbound) deste nó. |

---

### `MapConnectionEdge` (Aresta Direcionada do Grafo)
Representa uma conexão semântica direcionada entre dois estudos renderizada em SVG com trajetória e rótulo.

| Campo | Tipo | Descrição |
| :--- | :--- | :--- |
| `id` | `number` | Identificador único da relação semântica (`study_relations.id`). |
| `sourceStudyId` | `number` | ID do estudo de origem da relação. |
| `targetStudyId` | `number` | ID do estudo de destino da relação. |
| `relationType` | `StudyRelationType` | Tipo canônico (`fundamenta`, `desdobra`, `contradiz`, `sintetiza`, `cita`, `complementa`). |
| `description` | `string \| null` | Breve nota ou justificativa do argumento. |
| `path` | `string` | Instrução SVG de curva de Bézier (`M x1 y1 Q cx cy x2 y2`). |
| `label` | `string` | Rótulo legível da relação exibido no badge central da aresta. |
| `badgeX` | `number` | Coordenada X para posicionamento do badge textual no ponto médio da curva. |
| `badgeY` | `number` | Coordenada Y para posicionamento do badge textual no ponto médio da curva. |
| `isContradiction` | `boolean` | Flag indicando estilo visual diferenciado para relações antitéticas. |

---

### `RelationPopoverState` (Estado do Popover de Relação)
Gerencia a abertura, ancoragem e preenchimento do formulário contextual `MapRelationPopover`.

| Campo | Tipo | Descrição |
| :--- | :--- | :--- |
| `isOpen` | `boolean` | Indica se o popover está aberto e visível. |
| `sourceNode` | `MapNodeItem \| null` | Estudo de origem do argumento. |
| `targetNode` | `MapNodeItem \| null` | Estudo de destino do argumento. |
| `existingRelationId` | `number \| null` | Preenchido quando o popover é aberto para editar/remover uma aresta existente. |
| `selectedType` | `StudyRelationType` | Tipo semântico selecionado no dropdown. |
| `description` | `string` | Texto da justificativa opcional. |
| `isReversed` | `boolean` | Controla a inversão da polaridade da relação (`⇄`). |
| `anchorX` | `number` | Coordenada X na viewport para ancoragem visual do popover. |
| `anchorY` | `number` | Coordenada Y na viewport para ancoragem visual do popover. |

---

### `QuickCreateState` (Estado do Mini-card de Criação Rápida)
Gerencia a captura in-place de um novo estudo criado diretamente sobre o mapa.

| Campo | Tipo | Descrição |
| :--- | :--- | :--- |
| `isOpen` | `boolean` | Indica se o mini-card está aberto. |
| `x` | `number` | Coordenada cartesiana X no mapa onde o novo nó será posicionado. |
| `y` | `number` | Coordenada cartesiana Y no mapa onde o novo nó será posicionado. |
| `sourceNodeId` | `number \| null` | Se preenchido, o novo estudo será automaticamente conectado a este estudo. |
| `title` | `string` | Título digitado pelo leitor. |
| `sectionKey` | `'summary' \| 'concepts' \| 'explanation'` | Seção analítica inicial escolhida. |
| `sectionContent` | `string` | Conteúdo inicial da seção (resumo da ideia). |

---

### `MapViewportState` (Navegação da Câmera)
Mantém o estado de pan e zoom da área gráfica.

| Campo | Tipo | Descrição |
| :--- | :--- | :--- |
| `panX` | `number` | Translação horizontal aplicada ao grupo principal do SVG. |
| `panY` | `number` | Translação vertical aplicada ao grupo principal do SVG. |
| `zoomLevel` | `number` | Escala multiplicadora (de 0.5 a 2.5, com padrão 1.0). |

---

## 2. Tipos Canônicos de Relação Semântica

A Map View utiliza o vocabulário semântico padronizado do Leitorum com correspondência ativa:

| Valor da Chave | Rótulo Ativo de Origem | Rótulo Invertido | Categoria Cognitiva |
| :--- | :--- | :--- | :--- |
| `fundamenta` | *Fundamenta* | *Fundamentado por* | Lógica / Evidência |
| `desdobra` | *Desdobra-se em* | *Desdobramento de* | Estrutura / Derivação |
| `contradiz` | *Contradiz* | *Contradito por* | Dialética / Antítese |
| `sintetiza` | *Sintetiza* | *Sintetizado por* | Conclusão / Síntese |
| `cita` | *Cita* | *Citado por* | Referência / Evidência |
| `complementa` | *Complementa* | *Complementado por* | Adição / Afinidade |
| `relacionado_com` | *Relacionado com* | *Relacionado com* | Relação Geral (Fallback) |
