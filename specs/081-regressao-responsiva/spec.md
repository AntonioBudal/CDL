# Feature Specification: F0.8.15 — Bateria Completa de Regressão e Consolidação do Roadmap de Responsividade

**Feature Branch**: `081-regressao-responsiva`  
**Created**: 2026-10-12  
**Status**: Draft  
**Input**: User description: "F0.8.15" (Briefing da Auditoria de Responsividade: F0.8.11 a F0.8.15 e encerramento do marco de responsividade móvel)

---

## Contexto e Propósito

Após a especificação e implementação das fatias estruturais do marco de responsividade — **Feature 076** (Estratégia e Contratos), **Feature 077** (Shell e Navegação Móvel), **Feature 078** (Conteúdo e Leitor Responsivo), **Feature 079** (Rótulos de Botões e Linhas Texto+Botão) e **Feature 080** (Visualizações Móveis e Destaques) —, a **Feature 081 (F0.8.15)** fecha o ciclo de responsividade do **Caderno de Leitura**.

O objetivo desta feature é executar uma **bateria exaustiva de regressão** cobrindo a matriz completa de rotas versus viewports, verificar e auditar o encerramento dos 19 problemas históricos (P-01 a P-19), consolidar um teste-guarda automatizado no frontend contra regressões futuras e publicar a documentação final de encerramento do roadmap de responsividade.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Validação da Matriz Completa de Rotas × Viewports sem Transbordamento (Priority: P1) - MVP

Como leitor acessando o Caderno de Leitura em qualquer dispositivo (smartphone compacto, smartphone padrão, tablet ou desktop), quero que todas as páginas e rotas do sistema se ajustem à largura da minha tela sem qualquer rolagem horizontal indesejada (`scrollWidth === clientWidth`) e sem elementos cortados ou inacessíveis, para desfrutar de uma leitura fluida e confortável.

**Why this priority**: É a garantia de que as correções individuais implementadas nas features 077 a 080 funcionam em conjunto de forma íntegra em todo o ecossistema de telas do aplicativo, prevenindo vazamentos de layout.

**Independent Test**: Executar a matriz de validação visual e estrutural em 320px, 375px, 390px, 430px, 767px, 768px, 1024px e 1440px em todas as 25 rotas mapeadas; constatar que em 100% dos casos a largura visível corresponde exatamente à largura da viewport (`scrollWidth === clientWidth`).

**Acceptance Scenarios**:
1. **Dado** um smartphone de tela ultra-estreita (320px) ou padrão (375px–390px), **quando** o usuário navega por qualquer uma das rotas principais (`/`, `/livros`, `/destaques`, `/revisao`, `/inbox`, `/amigos`, `/ajustes`, `/lixeira`), **então** não há barra de rolagem horizontal na página e nenhum card, tabela ou barra transborda a viewport.
2. **Dado** qualquer elemento flutuante (toasts de feedback, botões de ação rápida flutuantes, barra de ações em lote da lixeira), **quando** renderizado no mobile, **então** respeita a folga canônica da barra inferior móvel através do token `--mobile-nav-offset`, sem sobreposição nem corte de texto.
3. **Dado** o modo paisagem móvel (844×390px), **quando** a tela é girada, **então** o cabeçalho e os painéis respeitam as margens de segurança laterais (`env(safe-area-inset)`), preservando a legibilidade.

---

### User Story 2 - Rastreabilidade e Encerramento dos Problemas Auditados (P-01 a P-19) (Priority: P1)

Como mantenedor e auditor do produto, quero uma verificação item a item de cada um dos 19 problemas diagnosticados na auditoria estática original (P-01 a P-19), comprovando que cada defeito foi efetivamente resolvido, coberto por testes e integrado à base estável.

**Why this priority**: Garante que o roadmap de responsividade encerre sem pendências ocultas, dívidas técnicas não resolvidas ou suposições não comprovadas.

**Independent Test**: Conferir a matriz de rastreabilidade normativa de P-01 a P-19; validar que cada item possui status "Resolvido", com evidência técnica documentada, commit associado e teste automatizado correspondente.

**Acceptance Scenarios**:
1. **Dado** o problema P-01 (barra inferior e cabeçalho mobile), **quando** auditado, **então** a `MobileTabBar` possui 5 alvos acessíveis com $\ge 44 \times 44\text{ px}$ e o cabeçalho móvel opera limpo.
2. **Dado** os problemas de visualizações especializadas (P-04, P-05, P-06, P-07, P-08), **quando** auditados, **então** o Mapa responde a pan/pinch e oferece lista semântica; o Canvas desbloqueia o scroll vertical (`touch-action: pan-y`) e compacta a toolbar; e a Árvore oculta alças de arrasto em `pointer: coarse` e comprime a indentação.
3. **Dado** o problema P-03 (`ShareModal`), **quando** auditado, **então** o modal utiliza exclusivamente tokens CSS canônicos do sistema, sem nenhuma dependência residual de Tailwind.

---

### User Story 3 - Suíte de Testes-Guarda Automatizados contra Regressões (Priority: P2)

Como engenheiro de software atuando no projeto, quero uma suíte automatizada de testes no frontend que impeça a reintrodução de quebras de layout, classes ausentes, breakpoints fora do padrão canônico ou violações de alvos táteis em commits futuros.

**Why this priority**: Evita que novos desenvolvimentos ou refatorações reintroduzam defeitos de responsividade já superados.

**Independent Test**: Executar `npm test` no frontend; confirmar que os testes de guarda de responsividade validam contratos de CSS, ausência de classes proibidas, integridade de breakpoints e alvos táteis mínimos.

**Acceptance Scenarios**:
1. **Dado** a suíte de testes de regressão do frontend, **quando** executada via `npm test`, **então** valida a conformidade dos limites canônicos (`max-width: 767px` e `min-width: 768px`).
2. **Dado** qualquer novo componente ou edição no código-fonte, **quando** analisado pelo teste-guarda, **então** falha se houver alvos interativos táteis declarados com dimensões inferiores a $44 \times 44\text{ px}$ no mobile.
3. **Dado** os seletores globais e tokens de offset, **quando** inspecionados pelo teste-guarda, **então** garantem a presença e coerência de `--mobile-nav-offset` e das container queries do palco de estudos.

---

### User Story 4 - Protocolo de Homologação em Aparelho Físico e Encerramento (Priority: P2)

Como responsável técnico, quero um protocolo claro e reproduzível para validação do sistema em aparelhos celulares reais (Android e iOS via rede local ou Tailscale), acompanhado do documento consolidado de encerramento do marco de responsividade.

**Why this priority**: A emulação no navegador de desktop não reproduz com 100% de precisão o comportamento de teclado virtual, gestos táteis nativos de borda e safe areas de diferentes fabricantes.

**Independent Test**: Seguir o roteiro de homologação em dispositivo móvel físico em ambiente isolado com dados fictícios, verificando digitação com teclado virtual, gestos de pinça e comportamento da barra inferior.

**Acceptance Scenarios**:
1. **Dado** o servidor iniciado em modo de rede via `iniciar.py`, **quando** acessado por um smartphone na mesma rede local, **então** a interface é renderizada instantaneamente, os gestos táteis funcionam com fluidez e o teclado virtual não esconde botões essenciais.
2. **Dado** a conclusão da homologação, **quando** emitido o relatório de encerramento, **então** o marco de responsividade F0.8.11 a F0.8.15 é declarado formalmente concluído.

---

### Edge Cases

- **Teclado Virtual Ativo em Telas Estreitas**: Em smartphones com teclado aberto, a altura útil cai para ~300px. Formulários (como edição de estudo, notas e modais) devem usar `dvh` e rolagem vertical suave para não obstruir o botão de salvar.
- **Rotação de Tela (Orientação Paisagem Móvel - 844×390px)**: A barra inferior deve permanecer utilizável ou recolher-se graciosamente sem bloquear o conteúdo central.
- **Temas Visuais de Alto Contraste e E-Ink**: Linhas de contorno, bordas de cards e divisores de tabelas devem preservar legibilidade sem quebrar o alinhamento de 100% de largura.
- **Estudos com Títulos Excessivamente Longos**: Títulos de estudos com mais de 80 caracteres em nós da Árvore, cards de Destaques e badges de Mapa devem truncar com reticências sem forçar estouro da caixa pai.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE garantir que nenhuma das 25 rotas nomeadas de `router/index.ts` apresente transbordamento horizontal (`scrollWidth > clientWidth`) nas viewports de 320px, 375px, 390px, 430px, 767px, 768px, 1024px e 1440px.
- **FR-002**: O sistema DEVE auditar e atestar a resolução formal dos 19 problemas (P-01 a P-19) da auditoria estática original, documentando a rastreabilidade em matriz canônica.
- **FR-003**: O sistema DEVE consolidar a suíte de testes de regressão no frontend (`tests/feature-081-responsive-regression.test.mjs`), assegurando validações automatizadas de regras contratuais de responsividade.
- **FR-004**: O sistema DEVE ratificar a política de testes sem downloads pesados de navegadores de terceiros, preservando a agilidade e leveza do ambiente local.
- **FR-005**: Todos os controles interativos, botões de ação e links no mobile DEVEM possuir alvo tátil mínimo de **$44 \times 44\text{ px}$** (WCAG 2.1 Critério 2.5.5).
- **FR-006**: Todos os elementos fixos ou flutuantes no celular DEVEM utilizar a folga canônica da barra inferior através do token `--mobile-nav-offset`.
- **FR-007**: O sistema DEVE fornecer roteiro reproduzível de homologação em aparelhos físicos sob rede privada/Tailscale utilizando exclusivamente dados fictícios.
- **FR-008**: O código e a documentação DEVEM manter conformidade estrita de **zero emojis** e isolamento absoluto do banco ativo (`caderno.db`).

---

### Key Entities

- **Matriz de Regressão de Responsividade**: Conjunto bidimensional relacionando cada rota/componente às resoluções canônicas (320px, 375px, 390px, 430px, 767px, 768px, 1024px, 1440px), com verificação de overflow, alvos táteis e integridade de shell.
- **Registro de Rastreabilidade de Problemas (P-01 a P-19)**: Tabela consolidada com ID do problema, componente, gravidade, feature resolvedora, arquivo de teste e status de verificação.
- **Protocolo de Homologação em Aparelho Físico**: Roteiro operacional com passos de verificação de gestos, teclado virtual, safe-areas e orientação de tela em dispositivos reais.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: **100% das 25 rotas nomeadas** testadas e validadas sem transbordamento horizontal (`scrollWidth === clientWidth`) nas 8 viewports normativas.
- **SC-002**: **19 de 19 problemas (P-01 a P-19)** auditados e confirmados como formalmente resolvidos com evidência rastreável.
- **SC-003**: Suíte automatizada de testes de regressão de responsividade no frontend integrada com **100% de aprovação** no `npm test`.
- **SC-004**: Suítes completas de frontend (`npm test`), compilação (`npm run build`) e backend (`pytest`) **100% verdes**, com zero falhas ou quebras de tipos.
- **SC-005**: **Zero caracteres emoji** em qualquer arquivo novo ou modificado da feature.
- **SC-006**: Encerramento documentado do marco de responsividade (F0.8.11 a F0.8.15) consolidado em `RETOMADA.md`.

---

## Assumptions

- A validação de regressão utilizará dados estritamente sintéticos ou bancos descartáveis em `tmp_path`, sem qualquer leitura ou toque no banco real (`caderno.db`).
- A infraestrutura de testes automatizados continuará baseada no Node test runner nativo (`node --test`), mantendo alta velocidade de execução sem exigir a instalação de Playwright ou navegadores pesados.
- Testes em aparelhos físicos reais são guiados pelo protocolo estruturado fornecido na documentação da feature.
