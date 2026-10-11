# Implementation Plan: Ajustes — Ateliê de Preferências e Leitura Viva

**Branch**: `072-ajustes-atelie-preferencias` | **Date**: 2026-10-11 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/072-ajustes-atelie-preferencias/spec.md`

## Summary

Esta feature transforma a página `/ajustes` em um ateliê ergonômico moderno e responsivo com três pilares centrais:
1. **Galeria de Temas Estilo Windows 11**: Substituição da lista suspensa árida de seleção de temas por uma grade visual de cartões (`ThemePreviewGrid.vue` / `ThemePreviewCard.vue`), onde cada um dos 10 temas oficiais do Leitorum apresenta um box gráfico com as cores reais da paleta (`--color-page`, `--color-surface`, `--color-text` e `--color-accent`), indicador de tema ativo e acessibilidade total por teclado (`role="radiogroup"` / `role="radio"`).
2. **Navegação Vertical Contínua**: Substituição das abas horizontais empilhadas no topo por um menu lateral vertical (`.settings-nav`) integrando os 5 grupos funcionais ("Perfil & Privacidade", "Aparência", "Leitura", "Sistema", "Conta & Dispositivos") com sincronização transparente via URL (`/ajustes?tab=...`).
3. **Bancada de Leitura Viva e Sincronia Imediata**: Expansão do simulador de leitura (`AppearancePreview.vue`) como coluna permanente no desktop que reflete a 60 FPS qualquer ajuste de tipografia, tamanho, entrelinha, alinhamento e contraste, convertendo-se em gaveta inferior retrátil (*bottom sheet*) em dispositivos móveis.

---

## Technical Context

**Language/Version**: TypeScript 5.x / Vue 3.5+ (Composition API, `<script setup>`), Python 3.13 (Backend intocado).

**Primary Dependencies**: Vue Router, Pinia, Lucide Icons (`Icon.vue`), CSS Variables/Tokens semânticos.

**Storage**: Armazenamento local no navegador (`localStorage`, chave `caderno.aparencia.v2`), SQLite WAL existente via FastAPI para perfil e autenticação.

**Testing**: Testes unitários de componentes e contratos via `node --test` (`npm test`), compilação estrita `vue-tsc -b`, testes backend via `pytest`.

**Target Platform**: Navegadores modernos (Desktop Windows 11/Linux/macOS e Mobile iOS/Android via rede local/Tailscale).

**Project Type**: Aplicação Web Single-Page integrada a servidor local FastAPI.

**Performance Goals**: Troca de tema e atualização visual da bancada viva em menos de 16ms (60 FPS contínuos) sem travamento da thread de renderização.

**Constraints**: Alvos táteis $\ge 44 \times 44\text{px}$, imunidade cromática total aos 10 temas, zero emojis, conformidade com a Constituição do Caderno de Leitura.

**Scale/Scope**: 10 temas canônicos, 5 seções de ajustes, isolamento estrito de estilos do preview sem vazamento global acidental.

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Artigo Constitucional | Status | Justificativa / Conformidade |
| :--- | :--- | :--- |
| **I. Proteção Absoluta do Acervo e Privacidade** | PASS | O simulador de leitura utiliza fragmentos literários fictícios pré-compilados (Machado de Assis, Guimarães Rosa). Nenhuma anotação privada ou dado do acervo real é lido ou transmitido. |
| **II. Isolamento Estrito de Testes** | PASS | Todos os testes rodam contra arquivos mockados ou em memória sem tocar em `backend/data/caderno.db`. |
| **III. Fidelidade Arquitetural e Tecnológica** | PASS | Vue 3 com Composition API estrita, TypeScript, tokens CSS semânticos e Uvicorn/FastAPI preservados. |
| **IV. Governança por SDD** | PASS | Ciclo formal de especificação e planejamento executado com sucesso no Spec Kit. |
| **V. Resiliência Operacional e Transações** | PASS | Nenhuma alteração de schema SQLite ou migração de banco é necessária. Backend permanece 100% estável. |
| **VI. Versionamento Git** | PASS | 1 Feature = 1 Commit ao término da implementação com testes verdes. |

---

## Project Structure

### Documentation (this feature)

```text
specs/072-ajustes-atelie-preferencias/
├── plan.md              # Este arquivo
├── research.md          # Pesquisa técnica e matriz cromática dos 10 temas
├── data-model.md        # Modelos e catálogo CANONICAL_THEME_PREVIEWS
├── quickstart.md        # Guia de validação automatizada e manual
├── contracts/           # Contratos de componentes e layout
│   └── settings-contracts.md
├── checklists/
│   └── requirements.md
└── tasks.md             # Decomposição em tarefas (próxima etapa: /speckit-tasks)
```

### Source Code Impacted

```text
caderno-leitura-0.1/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ThemePreviewGrid.vue       # [NOVO] Grade de cartões de temas estilo Windows 11
│   │   │   ├── AppearanceControls.vue     # [MODIFICADO] Integração do ThemePreviewGrid no campo 'theme'
│   │   │   └── AppearancePreview.vue      # [MODIFICADO] Sincronia a 60 FPS e suporte a drawer mobile
│   │   ├── views/
│   │   │   └── SettingsView.vue           # [MODIFICADO] Layout 3 colunas, menu lateral vertical e bottom sheet mobile
│   │   └── types/
│   │       └── settings.ts                # [NOVO/MODIFICADO] Tipos de pré-visualização e seções
│   └── tests/
│       └── feature-072-ajustes-atelie-preferencias.test.mjs # [NOVO] Testes automatizados da feature
```

**Structure Decision**: A implementação concentra-se 100% no frontend do Caderno de Leitura (`caderno-leitura-0.1/frontend/`), preservando intacto o backend em Python, as tabelas SQLite e as APIs de dados.

---

## Complexity Tracking

*Nenhuma violação ou exceção arquitetural detectada.*
