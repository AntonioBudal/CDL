# Feature Specification: 007 — Zero-G: Superclasse Flutuante & Magnética

**Feature Branch**: `007-zero-g-flutuante`  
**Created**: 2026-09-19  
**Status**: Ready  
**Input**: User description: "Zero-G — Flutuante & Magnética. Essa seria uma das Superclasses mais características do sistema. O princípio é criar a impressão de que os elementos têm massa muito baixa e estão suspensos no espaço. Cards com bordas discretas, sombras amplas e suaves, separação baseada em profundidade. Idle Breathing (oscilação imperceptível de repouso Y=0 -> Y=-1px com ciclo longo). Hover magnético com resposta sutil ao cursor (máximo 4px) e retorno com inércia elástica longa ao sair o cursor. Texto de leitura absolutamente estável. Respeito irrestrito a redução de movimento. Desacoplamento total dos temas de cores. Fronteira estrita entre visual estático (não tocar) e motor físico (Superclasse). Controle de intensidade multiplicador (Sutil 0.5, Padrão 1.0, Alta 1.5)."

---

## Clarifications

### Session 2026-09-19

- Q: Como delimitar a fronteira visual para garantir que a Superclasse não interfira nos ajustes pré-existentes do usuário? → A: **Fronteira Estática Intocada**: As Superclasses JAMAIS sobrescrevem ou interferem nas variáveis e controles de Tipografia (24 fontes, tamanho de leitura, alinhamento), Cores (10 temas, cores de destaque), Layout (densidade, largura de contêiner) e UI Base (estilo de preenchimento de botões, contraste de cartões). A leitura e o layout estático continuam estritamente sob controle soberano do usuário.
- Q: Qual é o escopo de atuação exclusivo da Superclasse na arquitetura CSS/TypeScript? → A: **Fronteira Dinâmica do Motor Físico**: A Superclasse atua exclusivamente no comportamento de movimento, inércia e reação dinâmica. Dita e gerencia apenas variáveis de `transform`, `box-shadow` dinâmico (no hover/active), curvas de `transition-timing-function` (easing) e keyframes de animação de estado.
- Q: Como o usuário poderá dosar o peso ou intensidade da física sem expor controles técnicos complexos? → A: **Controle de Intensidade Paramétrico**: É introduzido o controle de "Intensidade da Superclasse" com opções pré-definidas: Sutil (`0.5`), Padrão (`1.0`), Alta (`1.5`) e Desativada (`0.0`). A arquitetura CSS calcula todas as translações e oscilações dinâmicas através de variáveis multiplicadoras na forma `calc(var(--sc-base-translate) * var(--sc-intensity))`.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Ativação e Vivência da Superclasse Zero-G no Acervo (Priority: P1) 🎯 MVP

Como leitor que organiza e consulta seu acervo pessoal,  
Quero selecionar a Superclasse "Zero-G" nas configurações de aparência do sistema,  
Para que a estante de livros, capas e cartões transmitam uma sensação palpável de leveza, suspensão espacial e reatividade magnética suave ao cursor, sem alterar a paleta cromática do meu tema favorito nem o layout estático da página.

**Why this priority**: É a fundação do novo subsistema de Superclasses do Caderno de Leitura. Estabelece a física espacial, a geometria e o comportamento magnético dos cartões do acervo, entregando valor perceptível imediato já como MVP.

**Independent Test**: Acessar a tela de configurações, alternar a Superclasse para "Zero-G", retornar à estante de livros e constatar que:
1. Os cartões possuem bordas suaves, sombras profundas e amplas, separando-se pela profundidade e não por caixas rígidas.
2. Em repouso, os cartões apresentam uma oscilação vertical quase subliminar e assíncrona.
3. Ao aproximar e mover o cursor sobre um cartão, ele é sutilmente atraído pelo ponteiro (máximo de 4px na intensidade padrão) e, ao afastar o cursor, retorna ao repouso com amortecimento elástico gracioso.
4. Ao alternar entre temas como Breu, Fiorde ou Porcelana, a física Zero-G permanece ativa enquanto as cores mudam harmoniosamente.

**Acceptance Scenarios**:
1. **Given** que o usuário está na tela de Configurações, **When** ele seleciona a opção "Zero-G (Flutuante & Magnética)", **Then** o sistema armazena a preferência e atualiza imediatamente o comportamento físico de toda a aplicação sem recarregar a página.
2. **Given** a estante de livros com múltiplos cartões exibidos em Zero-G, **When** o usuário observa a tela em repouso, **Then** os cartões realizam uma oscilação vertical sutil e imperceptível (amplitude aproximada de 1 pixel em ciclo longo de 5 a 6 segundos), com defasagem de fase entre os cartões para conferir naturalidade.
3. **Given** um cartão de livro em Zero-G, **When** o cursor do mouse se move sobre o cartão, **Then** o cartão sofre um microdeslocamento em direção ao cursor limitado estritamente ao teto de `calc(4px * var(--sc-intensity))`.
4. **Given** um cartão de livro em estado de atração magnética, **When** o cursor deixa a área do cartão, **Then** o cartão retorna à sua posição de repouso através de uma desaceleração elástica contínua com inércia prolongada, sem saltos abruptos.

---

### User Story 2 - Calibração de Intensidade da Física pelo Usuário (Priority: P2)

Como usuário que deseja personalizar a sutileza das interações físicas,  
Quero ajustar o nível de intensidade da Superclasse entre "Sutil", "Padrão" e "Alta",  
Para dosar o peso sensorial da flutuação e do magnetismo conforme minha preferência de uso.

**Why this priority**: Permite que usuários com diferentes sensibilidades estéticas encontrem seu ponto de equilíbrio ideal, escalando matematicamente as amplitudes dinâmicas sem quebrar a consistência da física.

**Independent Test**: No painel de Ajustes, alternar a intensidade entre Sutil (`0.5x`), Padrão (`1.0x`) e Alta (`1.5x`), e verificar na estante que as oscilações de repouso e a atração magnética escalam instantaneamente suas amplitudes físicas de forma proporcional.

**Acceptance Scenarios**:
1. **Given** a intensidade configurada como "Sutil", **When** o usuário passa o mouse sobre um cartão, **Then** o deslocamento magnético máximo atinge no máximo 2px (`4px * 0.5`) e a oscilação de repouso reduz para aproximadamente 0.5px.
2. **Given** a intensidade configurada como "Alta", **When** o usuário passa o mouse sobre um cartão, **Then** o deslocamento magnético máximo alcança até 6px (`4px * 1.5`) e a oscilação de repouso atinge aproximadamente 1.5px.
3. **Given** a intensidade configurada como "Desativada", **When** qualquer elemento for exibido, **Then** todo movimento e magnetismo cessa (`0px`), preservando apenas as sombras e o formato visual estático.

---

### User Story 3 - Estabilidade e Quietude Absoluta no Modo de Leitura (Priority: P3)

Como leitor focado no estudo de capítulos e anotações,  
Quero que o texto de leitura e as áreas de anotação permaneçam 100% estáticos e confortáveis,  
Para que nenhuma animação flutuante ou física magnética cause distração visual ou fadiga ocular durante a leitura prolongada.

**Why this priority**: Garante que o propósito principal do Caderno de Leitura (estudo e reflexão aprofundada) seja preservado intacto, subordinando os efeitos visuais ao conforto ergonômico da leitura.

**Independent Test**: Abrir um capítulo ou anotação de leitura com a Superclasse Zero-G ativada e verificar que parágrafos, cabeçalhos, citações e campos de edição permanecem rigorosamente firmes, sem qualquer oscilação ou deslocamento reativo ao ponteiro do mouse.

**Acceptance Scenarios**:
1. **Given** a tela de leitura de um capítulo ou estudo com Zero-G ativo, **When** o usuário movimenta o cursor do mouse sobre o texto corrido ou rola a página, **Then** o texto e os parágrafos permanecem completamente fixos, sem qualquer translação, oscilação ou rotação.
2. **Given** a interface de leitura, **When** o usuário passa o mouse sobre botões auxiliares ou indicadores de progresso, **Then** esses elementos pontuais podem exibir a leveza da Superclasse sem mover o bloco textual adjacente.

---

### User Story 4 - Acessibilidade Universal e Neutralização sob Redução de Movimento (Priority: P4)

Como usuário com sensibilidade a movimentos (vestibulopatia, cinetose ou preferência por interfaces estáticas),  
Quero que a física de movimento seja automaticamente neutralizada quando eu configurar meu dispositivo para reduzir movimentos,  
Para que eu possa utilizar a interface com total segurança, mantendo a geometria limpa e as sombras suaves sem qualquer estímulo oscilatório.

**Why this priority**: Conformidade inegociável com diretrizes de acessibilidade e bem-estar do leitor.

**Independent Test**: Habilitar a configuração de sistema "Reduzir movimento" (*prefers-reduced-motion*) ou definir o controle de movimento da aplicação como desativado e verificar que todas as oscilações de repouso e atrações magnéticas são instantaneamente desabilitadas, preservando apenas os atributos visuais estáticos.

**Acceptance Scenarios**:
1. **Given** um sistema operacional com a diretiva de redução de movimento habilitada, **When** o Caderno de Leitura for executado com Zero-G selecionado, **Then** a oscilação de repouso (*idle breathing*) e a atração magnética de hover permanecem desativadas, mantendo os cartões em posição fixa.
2. **Given** o controle de "Movimento / Transições" na tela de Configurações do Caderno, **When** o usuário seleciona a opção "Desativadas", **Then** todas as animações dinâmicas de Zero-G cessam imediatamente em toda a aplicação.

---

### Edge Cases

- **Dispositivos Móveis e Touchscreens**: Em telas táteis onde não há ponteiro contínuo (*hover*), a atração magnética é silenciosamente suprimida; o feedback visual de toque e a elevação estática suave de Zero-G continuam operacionais.
- **Transição Rápida entre Múltiplos Cartões**: Quando o cursor se move rapidamente através de uma grade de cartões, cada cartão amortece seu retorno de forma independente, sem travamentos, sem acumulação de atrasos (*lag*) e sem artefatos visuais de corte.
- **Janela em Segundo Plano ou Aba Inativa**: Ao perder o foco da janela ou aba, as oscilações de repouso suspendem seus ciclos de atualização para não consumir ciclos desnecessários de CPU ou bateria do computador portátil.
- **Alternância Dinâmica de Temas**: Ao trocar entre um tema claro (ex.: Porcelana) e um tema escuro (ex.: Breu), as variáveis de sombra difusa adaptam automaticamente sua densidade e opacidade para manter a separação de profundidade perceptível em qualquer contraste de fundo.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE fornecer o seletor de "Superclasse de Interface" nas opções de aparência da aplicação, permitindo escolher entre os arquétipos comportamentais disponíveis, iniciando por "Zero-G (Flutuante & Magnética)".
- **FR-002**: A seleção da Superclasse DEVE ser estritamente ortogonal ao Tema de cores, garantindo que qualquer um dos temas existentes funcione harmoniosamente com a física e geometria de Zero-G sem alterar suas paletas de cores.
- **FR-003**: Os cartões de livros e superfícies destacadas na Superclasse Zero-G DEVEM apresentar bordas discretas, cantos com raio suave e separação visual fundamentada em elevação e sombras amplas e difusas em vez de linhas demarcatórias duras.
- **FR-004**: Os cartões do acervo em repouso DEVEM apresentar um movimento de respiração (*idle breathing*) quase imperceptível, com ciclo de transição suave prolongado (entre 5 e 6 segundos) e amplitude calculada via `--sc-intensity`.
- **FR-005**: O movimento de repouso dos cartões DEVE possuir defasagem temporal de fase entre elementos vizinhos, impedindo que múltiplos itens oscilem simultaneamente em bloco rígido.
- **FR-006**: Ao interagir com o cursor do mouse sobre ou nas imediações de um cartão em Zero-G, o cartão DEVE responder com atração magnética em direção ao cursor, com deslocamento máximo delimitado por `calc(4px * var(--sc-intensity))`.
- **FR-007**: Ao sair o cursor da área de um cartão, o elemento DEVE retornar à sua posição original com desaceleração física elástica prolongada (inércia amortecida), transmitindo a sensação de um objeto leve retido por tensão elástica.
- **FR-008**: O corpo de texto de capítulos, anotações e conteúdos de leitura DEVE permanecer 100% estável e imóvel em todas as circunstâncias, sendo terminantemente vedada a aplicação de oscilações ou deslocamentos magnéticos ao texto contínuo.
- **FR-009**: O sistema DEVE desativar imediatamente qualquer oscilação dinâmica ou efeito magnético quando a preferência do usuário ou do sistema operacional indicar redução de movimento (`prefers-reduced-motion` ou opção de movimento desativada).
- **FR-010**: A escolha da Superclasse e de sua intensidade DEVE ser persistida de forma duradoura no armazenamento local do navegador, sendo restaurada automaticamente em sessões futuras.
- **FR-011**: O sistema NÃO DEVE sobrescrever ou interferir em nenhuma das variáveis e controles visuais estáticos existentes do painel de Ajustes, incluindo famílias tipográficas, tamanho do texto de leitura, alinhamento de parágrafos, temas cromáticos, cores de destaque, densidade de espaçamento e formato base de botões.
- **FR-012**: O motor da Superclasse DEVE limitar sua atuação estritamente a propriedades dinâmicas de movimento, gerindo transformações espaciais (`transform`), sombras dinâmicas de elevação (`box-shadow`), curvas de aceleração/inércia (`transition-timing-function`) e animações de estado.
- **FR-013**: O sistema DEVE disponibilizar um controle de "Intensidade da Superclasse" no painel de Ajustes, permitindo escolher entre os níveis Sutil (multiplicador 0.5), Padrão (1.0), Alta (1.5) e Desativada (0.0).
- **FR-014**: Todos os cálculos de translação espacial e amplitudes oscilatórias da Superclasse DEVEM ser parametrizados no CSS através da variável multiplicadora `--sc-intensity`, calculados via `calc(var(--sc-base-translate) * var(--sc-intensity))`.

---

### Key Entities *(include if feature involves data)*

- **SuperclassPreference (Preferência de Superclasse)**:
  - Identificador estável do arquétipo físico selecionado (`zero-g`, `mecanica`, `invisivel`, `dimensional`, `monolitica`).
  - Atributo declarativo global no elemento raiz do documento (`data-superclass="zero-g"`).
- **SuperclassIntensity (Intensidade da Superclasse)**:
  - Nível de intensidade selecionado (`subtle`: 0.5, `standard`: 1.0, `high`: 1.5, `off`: 0.0).
  - Variável CSS injetada no elemento raiz (`--sc-intensity: 1`).
  - Associação com o catálogo de preferências de aparência do sistema (`AppearancePreferences`) e persistência no `localStorage`.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A ativação da Superclasse Zero-G é refletida na interface imediatamente sem necessidade de recarregar a página web.
- **SC-002**: A atração magnética de cartões no hover não ultrapassa em nenhuma hipótese o limite físico de `calc(4px * var(--sc-intensity))` de deslocamento em qualquer eixo (X ou Y).
- **SC-003**: 100% dos blocos de texto contínuo de leitura e anotações permanecem perfeitamente estáticos, sem sofrer qualquer oscilação ou deslocamento.
- **SC-004**: Sob a ativação de `prefers-reduced-motion` ou transições desativadas, 100% dos efeitos de oscilação contínua e magnetismo dinâmico são neutralizados, mantendo a geometria estática.
- **SC-005**: A alternância entre qualquer um dos 10 temas cromáticos preserva integralmente as características físicas de Zero-G sem distorção visual de contraste ou cores.
- **SC-006**: A taxa de quadros (*framerate*) durante a interação magnética e rolagem da estante mantém estabilidade visual fluida sem congelamentos perceptíveis de interface.
- **SC-007**: A alteração do nível de intensidade (Sutil 0.5x, Padrão 1.0x, Alta 1.5x) escala as amplitudes físicas de oscilação e magnetismo proporcionalmente em tempo real, sem necessidade de recarregar a página.
- **SC-008**: 100% das 24 fontes tipográficas, dos 10 temas de cor e dos ajustes de densidade do painel de Configurações mantêm seu comportamento e renderização visual estática inalterados ao alternar entre Superclasses.

---

## Assumptions

- A Superclasse Zero-G será a primeira das 5 Superclasses planejadas a ser implementada, estabelecendo a chave de configuração e a infraestrutura de tokens reutilizável pelas demais.
- Os efeitos de movimento de Zero-G utilizam exclusivamente aceleração por hardware gráfico (`transform` e `opacity`), preservando o desempenho em computadores e laptops modestos.
- Para usuários com telas sensíveis ao toque (dispositivos móveis), o sistema adapta graciosamente a experiência, suprimindo o magnetismo de cursor e conservando o acabamento visual de leveza e profundidade.
