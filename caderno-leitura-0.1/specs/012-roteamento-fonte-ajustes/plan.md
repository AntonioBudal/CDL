# Implementation Plan: Correção de Roteamento, Fonte Global e Limpeza de Ajustes

**Branch**: `012-roteamento-fonte-ajustes` | **Date**: 2026-09-19 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/012-roteamento-fonte-ajustes/spec.md`

---

## Summary

Esta feature resolve três débitos de experiência e usabilidade decorrentes da evolução da interface:
1. **Eliminação do bug de tela vazia** na navegação client-side do Vue Router: encapsulamento de todas as views em elementos raiz únicos e adoção de `:key="$route.fullPath"` no `<component :is="Component" />` sob `<Transition mode="out-in">`.
2. **Propagação e herança global irrestrita da fonte selecionada**: elevação de `--font-reading` para `--font-ui` e aplicação a 100% dos elementos da página (`:root, body, #app, button, input, select, textarea, code, pre`), proporcionando preview em tempo real.
3. **Higienização do painel de Ajustes**: remoção dos 3 controles tornados redundantes pelas Superclasses de Interface (`motion`, `button-width`, `tabs`), purga automática de chaves legadas no `localStorage` e renumeração sequencial limpa dos 7 grupos remanescentes (1 a 7).

---

## Technical Context

**Language/Version**: TypeScript 5.9+ (modo estrito), JavaScript ES2022, Vue 3.5+ (Composition API, `<script setup>`), CSS3.  
**Primary Dependencies**: Vue 3, Vue Router 4, Vite 8, `vue-tsc`.  
**Storage**: `window.localStorage` sob a chave `caderno.aparencia.v2`.  
**Testing**: Node Test Runner (`node --test`), `frontend/tests/superclasses.test.mjs`.  
**Target Platform**: Navegadores modernos desktop e mobile (Chrome, Edge, Firefox, Safari) no Windows local e via rede privada/Tailscale.  
**Project Type**: Single Page Application (SPA) desacoplada servida estaticamente via FastAPI em produção.  
**Performance Goals**: Remontagem e transição de rota fluida em < 100ms, propagação tipográfica em < 50ms, 60fps estáveis em transições de página.  
**Constraints**: 100% frontend; zero impacto no backend Python ou no banco SQLite `backend/data/caderno.db`; preservação total das 5 Superclasses de Interface.  
**Scale/Scope**: 5 visualizações ajustadas (`BooksView`, `BookView`, `StudyView`, `StudyEditView`, `ImportView`), casca global (`App.vue`), folhas de token/estilo (`tokens.css`, `style.css`), bootstrap de aparência (`appearance-bootstrap.js`) e contratos TypeScript (`appearance.d.ts`).

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **Artigo I — Privacidade e Acervo**: Nenhuma informação privada, nota pessoal ou texto do acervo é acessado, exibido ou transmitido. A feature opera 100% na casca visual do frontend. **(PASS)**
- [x] **Artigo II — Isolamento de Testes**: Não há interação com o banco de dados de produção `backend/data/caderno.db`. Todas as validações ocorrem em testes de unidade e build limpo do frontend. **(PASS)**
- [x] **Artigo III — Fidelidade Tecnológica**: Uso rigoroso de Vue 3, Composition API, TypeScript estrito, CSS nativo com variáveis e Vite. Processo local único. **(PASS)**
- [x] **Artigo IV — Governança por SDD**: Fluxo oficial Spec Kit cumprido com rigor (`specify` → `clarify` → `plan` → `tasks` → `analyze` → `implement`). As tarefas T01–T10 do Roadmap 0.3 continuam registradas como **NÃO INICIADAS**. **(PASS)**
- [x] **Artigo V — Resiliência Operacional**: Normalização defensiva e idempotente de `localStorage`, purga segura de atributos residuais do DOM e tolerância a dados prévios. **(PASS)**

---

## Project Structure

### Documentation (this feature)

```text
specs/012-roteamento-fonte-ajustes/
├── spec.md              # Especificação de requisitos e clarificações
├── checklists/
│   └── requirements.md  # Checklist de qualidade da especificação (100% PASS)
├── plan.md              # Este plano técnico de implementação
├── research.md          # Decisões arquiteturais D1, D2 e D3
├── data-model.md        # Entidades, preferências limpas e envoltórios de views
├── quickstart.md        # 5 cenários executáveis de validação
├── contracts/
│   └── appearance-settings.contract.md # Contratos de estado, DOM e roteamento
└── tasks.md             # (Será gerado na próxima etapa por /speckit-tasks)
```

### Source Code Modificado (Arquivos Mapeados)

```text
caderno-leitura-0.1/frontend/
├── src/
│   ├── App.vue                         # Roteador com :key="$route.fullPath"
│   ├── tokens.css                      # --font-ui: var(--font-reading)
│   ├── style.css                       # Herança irrestrita font-family em :root, body, #app, etc.
│   ├── appearance-bootstrap.js         # Poda de motion/button-width/tabs, purga localStorage e 7 grupos
│   ├── appearance.d.ts                 # Remoção de tipos obsoletos na interface AppearancePreferences
│   ├── components/
│   │   └── AppearanceControls.vue      # Atualização de rótulos e textos explicativos dos 7 grupos
│   └── views/
│       ├── BooksView.vue               # Invólucro único raiz <div class="books-view">
│       ├── BookView.vue                # Invólucro único raiz <div class="book-view">
│       ├── StudyView.vue               # Invólucro único raiz <div class="study-view">
│       ├── StudyEditView.vue           # Invólucro único raiz <div class="study-edit-view">
│       └── ImportView.vue              # Invólucro único raiz <div class="import-view">
└── tests/
    └── superclasses.test.mjs           # Testes unitários para 7 grupos, purga e herança de fontes
```

---

## Plan Workflow & Milestones

1. **Fase 1: Fundação de Roteamento e Enraizamento de Views (US1 - MVP)**
   - Adicionar `:key="$route.fullPath"` no `<component :is="Component" />` em `App.vue`.
   - Adicionar invólucros de elemento único nas 5 views que possuíam fragmentos raiz.
   - Validar que a transição `<Transition mode="out-in">` não apresenta inconsistências nem falhas de montagem.
2. **Fase 2: Propagação Global Irrestrita da Tipografia (US2)**
   - Configurar `--font-ui: var(--font-reading);` em `tokens.css`.
   - Configurar `font-family: var(--font-reading)` para `:root, body, #app, button, input, select, textarea, code, pre` em `style.css`.
   - Validar que a troca de fonte em Ajustes atualiza instantaneamente todos os botões, títulos e inputs do sistema.
3. **Fase 3: Poda de Ajustes, Purga de `localStorage` e Renumeração Limpa (US3)**
   - Remover `motion`, `button-width` e `tabs` de `fields` em `appearance-bootstrap.js`.
   - Atualizar a função `normalize()` para remover as chaves obsoletas do `localStorage` e limpar `data-motion`, `data-button-width`, `data-tabs` do `<html>`.
   - Renumerar sequencialmente os grupos restantes de 1 a 7.
   - Atualizar definições TypeScript em `appearance.d.ts`.
   - Ajustar textos e dicas em `AppearanceControls.vue`.
4. **Fase 4: Testes Automatizados e Build de Produção**
   - Atualizar e expandir `frontend/tests/superclasses.test.mjs` para validar a nova assinatura de 7 opções, a ausência de campos podados e a herança global de fontes.
   - Executar `npm test` e `npm run build` (`vue-tsc -b && vite build`) garantindo 100% de sucesso.
