# Implementation Plan: Estratégia Responsiva

**Branch**: `076-estrategia-responsiva` | **Spec**: [spec.md](spec.md)

---

## Summary
Feature documental e de validação. Entrega `research.md` (auditoria validada), dois contratos de arquitetura (`contracts/responsive-decisions.contract.md` e `contracts/breakpoints-patterns.contract.md`), `quickstart.md` (protocolo de validação com banco descartável), evidências de linha de base e um teste-guarda automatizado de inventário (`tests/feature-076-responsive-inventory.test.mjs`). Nenhuma alteração é permitida em arquivos de produção (`frontend/src` ou `backend/app`).

---

## Technical Context
- **Stack**: Frontend Vue 3 + TypeScript + Vite 8; CSS autoral sem frameworks externos.
- **Visualizações**: Implementação interna sem dependências externas de mapas, grafos ou canvas (`StudyMapView`, `StudyCanvasView`, `StudyTreeView`).
- **Automação de navegador**: Decisão ratificada em FR-007: manter testes estáticos em `node --test` complementados por roteiro manual de validação nas features 076 a 079, adiando a introdução de ferramentas de automação (como Playwright) para reavaliação na Feature 080.
- **Breakpoints canônicos**: Faixas de trabalho consolidadas:
  - Móvel: `<768px` (`max-width: 767px`)
  - Tablet: `768px` a `1023px`
  - Desktop: `≥1024px`
- **Isolamento**: Testes e protocolos utilizam estritamente bancos temporários (`tmp_path` / descartáveis), preservando o banco de dados ativo.

---

## Constitution Check
- **I. Preservação de Dados e Privacidade**: Validação conduzida exclusivamente com banco temporário descartável e dados sintéticos fictícios. Nenhuma informação do acervo real é exposta. ✔
- **II. Integridade do Banco e Operações no Ambiente**: O banco ativo local (`backend/data/caderno.db`) não sofre leitura nem mutação. Todas as checagens usam `CADERNO_DATABASE_PATH` efêmero. ✔
- **III. Estado do Roadmap e Versão 0.5**: A conformidade das features segue rigorosamente o ciclo Spec Kit delimitado. ✔
- **IV. Fluxo de Trabalho (Spec-Driven Development)**: Respeito à ordem delimitada: specify → clarify → plan → tasks → analyze → implement. ✔
- **V. Convenção de Versionamento Git**: Feature atômica gerando commit único após validação completa da suíte de testes. ✔

---

## Project Structure

```text
specs/076-estrategia-responsiva/
├── spec.md
├── plan.md
├── tasks.md
├── research.md                         # Auditoria estática e status de validação de P-01 a P-19
├── quickstart.md                       # Protocolo de validação reproduzível com banco descartável
├── contracts/
│   ├── responsive-decisions.contract.md  # Matriz de cobertura (25 rotas) e decisões por tela
│   └── breakpoints-patterns.contract.md  # Faixas canônicas, fronteiras e padrões de interação
├── checklists/
│   └── requirements.md
└── evidence/                           # Registros e medições da linha de base (dados sintéticos)

caderno-leitura-0.1/frontend/tests/
└── feature-076-responsive-inventory.test.mjs # Teste-guarda de correspondência entre router e contrato
```

---

## Abordagem de Implementação

1. **Estruturação de Pesquisa e Diagnóstico (`research.md`)**:
   - Transcrever as Partes A, B e C da auditoria com os 19 problemas (P-01 a P-19), níveis de severidade, evidências no código e status de validação inicial.
2. **Protocolo com Banco Descartável (`quickstart.md`)**:
   - Definir script de inicialização do backend com `CADERNO_DATABASE_PATH` temporário em porta efêmera e instruções de semeadura com dados fictícios (1 livro, 3 capítulos, ≥12 estudos, árvore de 5 níveis, ≥8 relações, 2 molduras, 1 admin, 1 usuário comum).
3. **Contrato de Decisões e Matriz de Cobertura (`contracts/responsive-decisions.contract.md`)**:
   - Mapear as 25 rotas de `src/router/index.ts`, as 5 visualizações e os overlays globais, classificando cada uma nas categorias 1 a 5, justificativa e alternativas móveis.
   - Detalhar as especificações de Map View (híbrido lista/grafo), Canvas View (lista agrupada por moldura no mobile, manipulação espacial no tablet) e Tree View (redução de indentação e menu de ações).
4. **Contrato de Breakpoints e Padrões de Interação (`contracts/breakpoints-patterns.contract.md`)**:
   - Padronizar faixas de viewport, regra da fronteira 767/768px, uso de container queries dentro de `SplitPane#main`, detecção de toque com `pointer: coarse` e prevenção de hover preso com `hover: hover`.
   - Formalizar especificações da barra inferior (5 alvos ≥ 44px), gaveta "Mais", bottom sheets e menus contextuais.
5. **Teste-Guarda Automatizado (`feature-076-responsive-inventory.test.mjs`)**:
   - Teste unitário em `node --test` que inspeciona `caderno-leitura-0.1/frontend/src/router/index.ts`, extrai todas as rotas nomeadas e valida que 100% delas estão documentadas no contrato de decisões.
6. **Validação da Linha de Base**:
   - Medições de viewport (320, 375, 430, 767, 768, 1024, 1440px), confirmação dos problemas P-01 a P-19 e atualização de `research.md`.

---

## Critérios de Conclusão e Gates

- **SC-001**: 100% das rotas nomeadas de `router/index.ts` presentes no contrato e verificadas via teste automatizado.
- **SC-002**: 19 de 19 problemas com status e evidência documentados.
- **SC-003**: Zero decisões de design sem justificativa explícita.
- **SC-004**: Protocolo executável em ambiente limpo sem tocar o acervo de produção.
- **SC-005**: Suítes `npm test` e `npm run build` 100% verdes; zero alterações em `frontend/src` e `backend/app`.
