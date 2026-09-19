# Research: 007 — Zero-G: Superclasse Flutuante & Magnética

**Date**: 2026-09-19  
**Feature**: 007 — Zero-G: Superclasse Flutuante & Magnética  
**Status**: Completed  

---

## Technical Unknowns & Architectural Decisions

### Decision 1: Separação Arquitetural entre Respiração de Repouso (*Idle Breathing*) e Magnetismo de Hover

- **Decision**: Delegação em duas camadas DOM distintas no grid de acervo (`BooksView.vue`):
  1. O elemento contêiner de lista (`<li>` do `.book-grid`) é responsável pela animação contínua de repouso (*idle breathing*) via keyframes CSS assíncronos (`animation-delay: calc(var(--card-index, 0) * 240ms)`).
  2. O cartão interativo (`.book-card`) é responsável pela atração magnética omnidirecional (`transform: translate(...)`) e elevação de sombra suave (`box-shadow`), com retorno amortecido por inércia elástica (`cubic-bezier(0.16, 1, 0.3, 1)`).
- **Rationale**:
  - Em CSS, aplicar simultaneamente uma `@keyframes` de repouso no `transform` e transições de `transform` no `:hover` sobre o mesmo elemento cria conflito de composição de pilha de transformações, provocando saltos ou exigindo pausar a animação bruscamente.
  - A separação hierárquica (`li` pai oscila ~1px suavemente, `.book-card` filho responde ao cursor) permite que ambas as transformações sejam compostas naturalmente pelo compositor de GPU do navegador sem qualquer interferência mútua, sem saltos e sem necessidade de loops em JavaScript (`requestAnimationFrame`).
- **Alternatives considered**:
  - *Keyframes únicos animando CSS Custom Property `@property --sc-idle-y`*: Exige suporte mais recente e pode ter inconsistências em navegadores legados ou causar reflows se o tipo registrado não for tratado como transform puro pelo compositor.
  - *Motor de física por mola em JavaScript (Spring Physics)*: Aumentaria desnecessariamente o bundle e consumiria ciclos contínuos de CPU/bateria para uma oscilação que o CSS nativo executa na GPU a 60fps com custo desprezível.

---

### Decision 2: Modelo Matemático de Parametrização via Variável Multiplicadora `--sc-intensity`

- **Decision**: Introduzir uma variável CSS centralizada `:root { --sc-intensity: 1.0; }` vinculada ao atributo raiz `[data-superclass-intensity]`:
  - `subtle`: `--sc-intensity: 0.5;`
  - `standard`: `--sc-intensity: 1.0;`
  - `high`: `--sc-intensity: 1.5;`
  - `off`: `--sc-intensity: 0.0;`
  - `@media (prefers-reduced-motion: reduce)` e `[data-motion="off"]`: forçam `--sc-intensity: 0.0 !important;`.
  - Todas as forças dinâmicas utilizam a fórmula:
    - Deslocamento magnético: `calc(var(--sc-magnetic-x, 0) * 4px * var(--sc-intensity))`
    - Oscilação vertical de repouso: `calc(-1px * var(--sc-intensity))`
- **Rationale**:
  - Permite calibração em tempo de execução 100% declarativa e instantânea.
  - Quando a intensidade é `0.0`, a multiplicação direta anula qualquer translação e oscilação (`4px * 0 = 0px`), garantindo que o modo estático e a acessibilidade de redução de movimento operem sem falhas ou efeitos colaterais.
- **Alternatives considered**:
  - *Classes utilitárias repetitivas por intensidade*: Geraria dezenas de seletores repetidos no CSS (`.zero-g--subtle`, `.zero-g--high`), dificultando a manutenção.
  - *Cálculos dinâmicos em JavaScript recalculando estilos inline no DOM*: Bypassa a folha de estilo, reduz a performance de renderização e complica a integração com o tema.

---

### Decision 3: Rastreamento Magnético Reativo ao Cursor (*Hover Magnético*)

- **Decision**: Implementar um composable / diretiva de ponteiro leve (`useMagneticHover` ou manipulador de eventos de ponteiro no `.book-card`) que calcula a posição normalizada do cursor em relação ao centro do cartão:
  - `relX = (clientX - (rect.left + rect.width / 2)) / (rect.width / 2)` (intervalo `[-1.0, 1.0]`)
  - `relY = (clientY - (rect.top + rect.height / 2)) / (rect.height / 2)` (intervalo `[-1.0, 1.0]`)
  - Atribui as variáveis locais no elemento: `--sc-magnetic-x: relX;` e `--sc-magnetic-y: relY;`.
  - No evento `pointerleave`, reseta ambas para `0`.
  - A transição CSS do `.book-card` utiliza `transition: transform 0.65s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.65s cubic-bezier(0.16, 1, 0.3, 1)`.
- **Rationale**:
  - O CSS `:hover` padrão só permite deslocamento estático pré-fixado (ex.: subir 2px). A especificação de Zero-G requer que o cartão responda suavemente à aproximação e posição do ponteiro como uma atração gravitacional sutil.
  - O cálculo é simples, assíncrono por evento e tem teto físico estrito de 4px na intensidade padrão (`4px * rel * intensity`), não causando atraso perceptível de input.
  - Dispositivos com telas touch (`@media (pointer: coarse)`) não executam o hover de cursor, preservando a usabilidade em celulares e tablets.
- **Alternatives considered**:
  - *Apenas CSS `:hover { transform: translateY(-4px); }`*: Não atenderia ao requisito de magnetismo reativo ao cursor detalhado pelo usuário.
  - *Full Pointer Follower com bounding box global*: Faria o cartão "perseguir" o cursor fora de seus limites, violando a regra de que se trata de magnetismo sutil, não perseguição.

---

### Decision 4: Integração com o Subsistema de Preferências de Aparência Existente

- **Decision**: Estender declarativamente o catálogo em `frontend/src/appearance-bootstrap.js` e a tipagem em `frontend/src/appearance.d.ts`:
  - Campo `superclass`: `'none' | 'zero-g' | 'mecanica' | 'invisivel' | 'dimensional' | 'monolitica'` (padrão `'none'`).
  - Campo `superclass-intensity`: `'standard' | 'subtle' | 'high' | 'off'` (padrão `'standard'`).
  - Agrupamento sob `'11. Superclasse de Interface'`, preservando rigorosamente os grupos `1` a `10` existentes.
  - Atributos injetados automaticamente no `<html>`: `data-superclass="..."` e `data-superclass-intensity="..."`.
  - Persistência contínua e unificada na chave existente do `localStorage` (`caderno.aparencia.v2`).
- **Rationale**:
  - Mantém a arquitetura do projeto uniforme, sem introduzir múltiplos canais de persistência.
  - O componente `AppearanceControls.vue` consome automaticamente os campos e grupos registrados em `cadernoAppearance.fields`, renderizando os seletores de forma consistente.
- **Alternatives considered**:
  - *Chave isolada no localStorage (`caderno.superclasses`)*: Criaria dessincronização potencial entre o snapshot de aparência e o estado da superclasse.
  - *Armazenar preferências no backend*: Viola o princípio de arquitetura local do cliente e adiciona latência desnecessária a uma preferência visual de interface.

---

### Decision 5: Isolamento Absoluto do Modo de Leitura e Proteção Ergonômica

- **Decision**: Escopo CSS estritamente restrito. Nenhuma regra da Superclasse Zero-G se aplicará aos contêineres `.markdown-content`, `.study-section`, `.reader-tools`, áreas de texto ou parágrafos de leitura.
- **Rationale**:
  - Conformidade estrita com o Princípio da Soberania do Leitor e requisito FR-008. O texto corrido deve permanecer imóvel e estável para leitura e estudo aprofundado sem fadiga ocular.
- **Alternatives considered**:
  - *Permitir oscilação suave no contêiner da página*: Rejeitado imediatamente; causaria vertigem, náusea e desconforto visual em leitores assíduos.
