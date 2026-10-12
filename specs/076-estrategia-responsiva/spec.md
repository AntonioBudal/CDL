# Feature Specification: Estratégia Responsiva — Inventário, Validação e Decisões

**Feature Branch**: `076-estrategia-responsiva`  
**Created**: 2026-10-11  
**Status**: Draft  
**Input**: Auditoria estática de responsividade (Claude, 2026-10-11) com 19 problemas (P-01 a P-19), classificação de 25 rotas e análise individual de Map, Canvas e Tree.

Esta feature valida a auditoria no aplicativo renderizado, ratifica as decisões e produz os contratos que orientam as features 077 a 080. Não altera código de produção.

---

## User Scenarios & Testing

### User Story 1 - Decisão documentada para cada tela (Priority: P1)
Como responsável pelo produto, quero um registro único que diga, para cada rota e visualização, qual experiência o celular, o tablet e o desktop terão e por quê, para que as próximas quatro features não tomem decisões de design por suposição.

**Why this priority**: Sem isso, cada feature seguinte redecide o que adaptar, simplificar ou restringir.

**Independent Test**: Abrir `contracts/responsive-decisions.contract.md` e confirmar que cada uma das 25 rotas de `router/index.ts`, as 5 visualizações de estudos e os overlays globais têm classificação (1 a 5), justificativa e funções a preservar.

**Acceptance Scenarios**:
1. **Dado** o roteador da aplicação, **quando** comparado ao contrato de decisões, **então** nenhuma rota nomeada está ausente e nenhuma linha do contrato aponta para rota inexistente.
2. **Dado** uma tela classificada como "sem alteração" ou "desktop com alternativa móvel", **quando** lida sua linha, **então** há justificativa explícita e, no segundo caso, a alternativa móvel está descrita.
3. **Dado** Map, Canvas e Tree, **quando** lidas suas seções, **então** cada uma contém os dez itens exigidos (diagnóstico, limitações, classificação, alternativas, recomendação, funções mantidas/reorganizadas/restringidas, alternativa ao restrito, arquivos, critérios, testes).

---

### User Story 2 - Problemas confirmados ou refutados com evidência (Priority: P1)
Como implementador, quero que cada problema da auditoria estática seja reproduzido (ou refutado) no aplicativo em execução com dados fictícios, para corrigir defeitos reais e não hipóteses.

**Why this priority**: 7 dos 19 problemas dependem de renderização (confiança M ou H).

**Independent Test**: Para cada P-xx, `research.md` registra status (Confirmado / Refutado / Parcial), viewport, tema e uma captura ou medição.

**Acceptance Scenarios**:
1. **Dado** um banco descartável com dados fictícios, **quando** a aplicação é aberta em 375 px autenticada, **então** o estado real do header e da navegação (P-01) fica registrado com captura.
2. **Dado** um problema refutado, **quando** registrado, **então** ele sai do escopo das features seguintes com a evidência anexada.
3. **Dado** um problema novo encontrado na validação, **quando** registrado, **então** recebe ID (P-20 em diante), gravidade e feature de destino.

---

### User Story 3 - Regras comuns e protocolo de validação (Priority: P2)
Como implementador das features 077 a 080, quero um contrato de breakpoints e um protocolo de validação repetível, para que as correções sejam consistentes e comparáveis.

**Why this priority**: Há 15 larguras de breakpoint e nenhum teste de layout renderizado.

**Independent Test**: Seguir `quickstart.md` do zero e obter as capturas da linha de base sem tocar no banco ativo.

**Acceptance Scenarios**:
1. **Dado** o contrato de breakpoints, **quando** consultado, **então** define as faixas canônicas, a regra para a fronteira 767/768, quando usar container query e quando usar `pointer: coarse`.
2. **Dado** o protocolo, **quando** executado, **então** cobre as larguras 320, 375, 390, 430, 767, 768, 1023, 1024 e 1440 px, além de 844×390 (paisagem), em ao menos um tema claro e um escuro.

---

### Edge Cases
- Rotas com alias (`/books`, `/livros`): contam como uma tela.
- Rota `/admin`: validar com usuário fictício administrador.
- Estados vazios, de carregamento e de erro de cada tela principal entram na linha de base.
- Árvore fictícia com 5 níveis e capítulo fictício com 12 ou mais estudos relacionados para Map e Canvas.
- Largura do palco reduzida por painéis laterais abertos em 1024–1280 px (P-12).

---

## Requirements

### Functional Requirements
- **FR-001**: A feature DEVE produzir a matriz de cobertura com todas as rotas, layouts, visualizações e overlays.
- **FR-002**: A feature DEVE registrar o status de validação de P-01 a P-19 com evidência por viewport.
- **FR-003**: A feature DEVE ratificar ou revisar, com justificativa, a classificação de cada tela; mudanças em relação à auditoria exigem aprovação do usuário.
- **FR-004**: A feature DEVE publicar o contrato de breakpoints e de padrões de interação (barra inferior, gaveta, bottom sheet, menu de ações).
- **FR-005**: A feature DEVE publicar o protocolo de validação com dados exclusivamente fictícios em banco descartável.
- **FR-006**: A feature DEVE incluir um teste automatizado que falhe quando uma rota nomeada do roteador não constar da matriz de cobertura.
- **FR-007**: A feature DEVE registrar a decisão sobre infraestrutura de teste em navegador: manter testes estáticos no `node --test` acompanhados por protocolo/roteiro de validação manual nesta rodada (features 076 a 079), postergando a reavaliação de dependências de automação (como Playwright) para a Feature 080.
- **FR-008**: A feature NÃO DEVE alterar arquivos em `frontend/src` nem em `backend/app`.
- **FR-009**: A feature DEVE manter a matriz de rastreabilidade problema → feature → tarefa → teste com status "pendente".

### Key Entities
- **Problema (P-xx)**: descrição, evidência, gravidade, confiança, status de validação, feature de destino.
- **Decisão de tela**: rota/componente, classificação 1 a 5, justificativa, funções preservadas, alternativa móvel.
- **Captura de linha de base**: rota, viewport, tema, estado.

---

## Success Criteria

- **SC-001**: 100% das rotas nomeadas do roteador presentes na matriz (verificado por teste).
- **SC-002**: 19 de 19 problemas com status de validação e evidência.
- **SC-003**: Zero decisões "sem alteração" ou "desktop com alternativa" sem justificativa.
- **SC-004**: Protocolo reproduzível por outra pessoa sem acesso ao acervo real.
- **SC-005**: `npm test`, `pytest` e `npm run build` permanecem verdes; diff de `frontend/src` vazio.

---

## Assumptions
- Decisões de partida são as da auditoria: shell = 2; Tree = 2; Map = 3; Canvas = 4; admin = 3.
- A barra inferior com 4 destinos + "Mais" segue a decisão já tomada na spec 038 (FR-010).
- Simulação de viewport não equivale a aparelho real; o teste em aparelho fica como pendência declarada para a 080.
- Tailwind não será instalado; `ShareModal` será reescrito com tokens próprios na 077.
