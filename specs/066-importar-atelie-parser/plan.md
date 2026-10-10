# Implementation Plan: F0.8.05 — Ateliê de Fichamento e Parser Estruturado

**Branch**: `066-importar-atelie-parser` | **Date**: 2026-10-10 | **Spec**: [spec.md](file:///c:/Users/User/caderno/specs/066-importar-atelie-parser/spec.md)

**Input**: Feature specification from `specs/066-importar-atelie-parser/spec.md`

## Summary

O Roadmap 0.8 / Feature 05 transforma a tela `/importar` de um formulário transacional monolítico em um ambiente de ateliê de duas colunas sincronizadas (*Two-Pane Studio*):
- Barra superior horizontal compacta para metadados de Livro, Capítulo, Localização e Título.
- Editor da Fonte Bruta no painel esquerdo, com contadores de palavras/caracteres, botão de ação manual e tratamento térmico contra jank.
- Prévia Estruturada viva no painel direito, com cards das 4 seções (Resumo, Explicação, Conceitos, Referências), pulso luminoso de detecção e atribuição de 1 clique para texto não classificado.
- Barra de ferramentas contextual flutuante para Markdown (negrito, itálico, H3, tabela, código, link), mantendo o editor limpo.
- Alternância fluida de modos de visualização (*Split 50/50*, *Apenas Fonte 100%*, *Apenas Prévia 100%*) e adaptação responsiva com abas segmentadas para telas menores (< 1024px).

## Technical Context

**Language/Version**: TypeScript 5.x, Vue 3.x (SFC), Python 3.13 / FastAPI (Backend)
**Primary Dependencies**: Vue Router, Tailwind/CSS semântico nativo, `useImportDraft`, `markdownFormatter.ts`
**Storage**: SQLite local (WAL mode, via backend REST existente)
**Testing**: Vitest (`npm test`), Vue-tsc (`npm run build`), Pytest (`python -m pytest`)
**Target Platform**: Windows local (Chrome/Edge/Firefox), Mobile/Tablet responsivo
**Project Type**: Web Application SPA (Vue 3 + Vite)
**Performance Goals**: Latência de digitação < 50ms com debounce de 300ms na prévia; transições CSS a 60 FPS com aceleração por GPU
**Constraints**: Imunidade cromática rigorosa (10 temas nativos); zero emojis no código e templates; preservação integral dos endpoints de importação e promoção de capturas
**Scale/Scope**: 1 View refatorada (`ImportView.vue`), 2 componentes reutilizáveis (`FloatingMarkdownToolbar.vue`, `StudioViewModeToggle.vue`), 1 suíte de testes dedicada

## Constitution Check

- **Preservação de Dados e Privacidade**: Nenhuma leitura de dados reais; dados sintéticos usados em testes. **APROVADO**.
- **Isolamento de Testes**: Testes não tocam no banco de produção. **APROVADO**.
- **Imunidade Cromática**: Uso exclusivo de variáveis dos 10 temas nativos. **APROVADO**.
- **Zero Emojis**: Proibição estrita de emojis no frontend, utilizando catálogo de ícones SVG. **APROVADO**.
- **1 Feature = 1 Commit**: Commit individual dedicado ao final da implementação com mensagem em português. **APROVADO**.

## Project Structure

### Documentation (this feature)

```text
specs/066-importar-atelie-parser/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── import-studio-ui.yaml
└── checklists/
    └── requirements.md
```

### Source Code

```text
caderno-leitura-0.1/
└── frontend/
    └── src/
        ├── components/
        │   └── studies/
        │       ├── FloatingMarkdownToolbar.vue   # Nova barra contextual flutuante
        │       └── StudioViewModeToggle.vue      # Seletor de modos (Split / Fonte / Prévia)
        ├── utils/
        │   └── markdownFormatter.ts              # Suporte expandido a tabela ('table')
        ├── views/
        │   └── ImportView.vue                    # Ateliê Two-Pane Studio refatorado
        └── style.css                             # Estilos do Ateliê, pulso luminoso e split layout
```
