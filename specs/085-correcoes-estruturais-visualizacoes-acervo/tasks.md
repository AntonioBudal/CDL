# Tasks: Correções Estruturais nas Visualizações do Acervo

**Input**: Design documents from `specs/085-correcoes-estruturais-visualizacoes-acervo/`  
**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md), [data-model.md](data-model.md), [contracts/study-views-layout.contract.md](contracts/study-views-layout.contract.md)

## Organization

As tarefas estão estruturadas por fases e organizadas por histórias de usuário, viabilizando implementação e validação independentes para cada fatia.

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Tarefa executável em paralelo (arquivos distintos, sem dependência mútua)
- **[Story]**: Mapeamento para a respectiva história de usuário (US1, US2, US3)
- Caminhos completos de arquivos especificados em cada tarefa

---

## Phase 1: Setup & Validação de Ambiente

**Propósito**: Garantir a integridade da baseline antes das modificações.

- [x] T001 Executar suíte de testes de layout existente em `caderno-leitura-0.1/frontend/tests/study_layout_and_contrast_fixes.test.mjs` para verificar a estabilidade do ambiente

---

## Phase 2: Foundational (Infraestrutura de Testes da Feature)

**Propósito**: Estabelecer a suíte de testes dedicada para verificação da feature 085.

- [x] T002 Criar suíte de testes unitários automatizados em `caderno-leitura-0.1/frontend/tests/feature-085-study-views-layout.test.mjs` asserindo a ausência de corte de dropdown, elevação de z-index, regras de herança do ícone de ordenação SVG e alinhamento do grid

---

## Phase 3: User Story 1 - Abertura e Flutuação Livre do Menu de Status sem Cortes (Priority: P1)

**Objetivo**: Eliminar completamente o corte (*clipping*) do menu suspenso de status de leitura na lista e na grade de estudos.  
**Teste Independente**: Abrir o seletor de status no primeiro e no último estudo da tabela e verificar que o menu abre sem cortes de borda e sobrepõe as linhas/cartões vizinhos.

- [x] T003 [US1] Refinar o limiar de espaço vertical (210px) e a lógica de abertura ascendente (`opensUpward`) em `caderno-leitura-0.1/frontend/src/components/StudyStatusBadge.vue`
- [x] T004 [US1] Assegurar elevação de camada de sobreposição (`z-index: 1000; position: relative;`) e `overflow: visible` em `.study-row-item.has-dropdown-open` e `.study-row-item:has(.is-open)` em `caderno-leitura-0.1/frontend/src/components/views/StudyListView.vue`
- [x] T005 [US1] Integrar emissão de `@toggle-open` e aplicar elevação de camada (`z-index: 50; position: relative;`) nos cartões de estudo ativos em `caderno-leitura-0.1/frontend/src/components/views/StudyGridView.vue`

**Checkpoint US1**: O menu suspenso de status abre livremente na primeira e na última linha da tabela e sobrepõe os cartões na grade sem ser cortado.

---

## Phase 4: User Story 2 - Legibilidade Universal do Ícone de Ordenação em Todos os Temas (Priority: P2)

**Objetivo**: Assegurar que o indicador de ordenação da tabela herde a cor exata do rótulo ativo com alto contraste em todos os 10 temas oficiais.  
**Teste Independente**: Alternar a ordenação nos cabeçalhos da tabela sob temas claros, texturizados e escuros, verificando nitidez e contraste do ícone.

- [x] T006 [US2] Declarar propriedades estritas `stroke: currentColor` e `fill: none` no seletor `.sort-indicator` e em `:deep(.sort-indicator svg)` em `caderno-leitura-0.1/frontend/src/components/views/StudyListView.vue`
- [x] T007 [US2] Validar conformidade de contraste e ausência de preenchimento indevido da seta SVG em `caderno-leitura-0.1/frontend/tests/feature-085-study-views-layout.test.mjs`

**Checkpoint US2**: A seta de ordenação exibe traços nítidos e legíveis em qualquer tema ativo sem regras conflitantes de preenchimento.

---

## Phase 5: User Story 3 - Alinhamento Geométrico Estrito do Grid da Tabela em Telas Largas (Priority: P3)

**Objetivo**: Garantir alinhamento milimétrico entre colunas de cabeçalho, dados e carregamento em resoluções de 1024px até 2560px.  
**Teste Independente**: Inspecionar o grid da tabela em larguras de 1024px, 1440px e 1920px e certificar correspondência de colunas e centralização vertical.

- [x] T008 [US3] Padronizar a definição de `grid-template-columns` com as mesmas frações para `.list-header-row`, `.study-row-item` e `.skeleton-row` em `caderno-leitura-0.1/frontend/src/components/views/StudyListView.vue`
- [x] T009 [US3] Aplicar `display: flex; align-items: center;` universal nas células de cabeçalho e dados, centralizando as colunas de seções (`col-sections`) e ações (`col-actions`) em `caderno-leitura-0.1/frontend/src/components/views/StudyListView.vue`

**Checkpoint US3**: A tabela de estudos apresenta alinhamento geométrico perfeito em todas as resoluções suportadas.

---

## Phase 6: Polimento & Validação Integrada

**Propósito**: Validação ponta a ponta e conformidade com as suítes automatizadas do repositório.

- [x] T010 Executar suíte de testes dedicada via `node --test tests/feature-085-study-views-layout.test.mjs`
- [x] T011 Executar suíte completa de testes do frontend via `npm test`
- [x] T012 Executar type-check e compilação de produção via `npm run build`
- [x] T013 Executar suíte de testes de regressão do backend via `.venv/Scripts/pytest.exe -q`

---

## Dependencies & Execution Order

```
[Phase 1: Setup] ──> [Phase 2: Foundational]
                           │
                           ├──> [Phase 3: User Story 1 (P1)]
                           │
                           ├──> [Phase 4: User Story 2 (P2)]
                           │
                           └──> [Phase 5: User Story 3 (P3)]
                                       │
                                       └──> [Phase 6: Polimento & Validação]
```

### Regras de Execução
1. **Foundational**: A suíte de testes dedicada (T002) deve ser escrita antes da implementação das histórias.
2. **Histórias de Usuário**: Podem ser implementadas sequencialmente na ordem de prioridade P1 -> P2 -> P3.
3. **Polimento**: A validação integral (T010 a T013) transcorreu com 100% de sucesso.
