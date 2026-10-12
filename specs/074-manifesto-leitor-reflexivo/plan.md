# Implementation Plan: Página Inicial sem Login (SEO) — Manifesto do Leitor Reflexivo

**Branch**: `074-manifesto-leitor-reflexivo` | **Date**: 2026-10-11 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/074-manifesto-leitor-reflexivo/spec.md`

## Summary

Reformulação completa da tela inicial pública deslogada (`LandingView.vue`) transformando-a de uma landing page genérica de startup em um manifesto editorial tipográfico assinado e calmo. A solução incorpora um Hero editorial assimétrico com Ficha de Leitura flutuante, um simulador interativo in-place das 4 dimensões do método (livro aberto com prólogo de Machado de Assis e caderno analítico sincronizado sem chamadas de rede), uma vitrine com os 10 temas canônicos repintando a página efemeramente em memória via `useVisitorTheme`, seções de soberania de dados (*local-first*, sem anúncios nem rastreadores) e tradição histórica dos *commonplace books*, dados estruturados Schema.org (`SoftwareApplication` / `WebApplication`), `font-display: swap` nas fontes locais e divisão dinâmica de código (*dynamic import*) no roteador para assegurar pontuação Lighthouse $\ge 95$.

## Technical Context

**Language/Version**: TypeScript 5.x (modo estrito) / Vue 3.5 (Composition API, `<script setup>`), Python 3.13 (backend)  
**Primary Dependencies**: Vue 3, Vue Router 4, `lucide-vue-next` (ícones oficiais), CSS Custom Properties (tokens de cor e tipografia), FastAPI / Pydantic v2 (backend)  
**Storage**: N/A (a landing page pública e o simulador utilizam estruturas de dados estáticas embutidas no cliente; sem leitura ou escrita no banco de produção)  
**Testing**: Vitest (`npm test` no frontend), Pytest (`pytest` no backend)  
**Target Platform**: Navegadores modernos desktop e dispositivos móveis (responsivo de 320px a 4K) em ambiente Windows local  
**Project Type**: Web Application (SPA Vue 3 servida por processo único local FastAPI)  
**Performance Goals**: Google Lighthouse $\ge 95$ nas quatro categorias (Performance, Acessibilidade, Melhores Práticas, SEO), LCP $< 1.5$s, CLS $= 0$, alternância de tema $< 100$ms, troca de abas do simulador em 150ms  
**Constraints**: Zero Emojis (conformidade estrita com a constituição, usando exclusivamente `<Icon />`), contraste $\ge 7:1$ (WCAG AAA) nos corpos de texto de leitura contínua em todos os 10 temas oficiais, navegação 100% por teclado, alvos de toque mínimos de 44x44px  
**Scale/Scope**: 1 view pública principal (`LandingView.vue`), 6 subcomponentes especializados em `components/landing/`, 1 composable (`useVisitorTheme.ts`), 1 módulo de dados (`landingSimulator.ts`), otimização em `router/index.ts`, `fonts.css` e `index.html`  

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Princípio I (Privacidade e Acervo)**: **PASS**. A feature é 100% pública e utiliza como insumo literário exclusivamente o prólogo em domínio público de Machado de Assis (*Memórias Póstumas de Brás Cubas*, 1881). Nenhum dado do acervo privado do usuário ou do arquivo ativo `caderno.db` é acessado ou exposto.
- **Princípio II (Isolamento de Testes)**: **PASS**. Todos os testes automatizados da feature executam em ambiente descartável ou no ambiente headless do Vitest, sem interagir com arquivos de banco de dados ativos.
- **Princípio III (Fidelidade Arquitetural)**: **PASS**. Construído com Vue 3, TypeScript estrito, `<script setup>`, CSS moderno baseado em tokens sem dependências externas adicionais, integrado ao processo único local.
- **Princípio IV (Governança SDD)**: **PASS**. Ciclo formal Spec Kit respeitado integralmente (`speckit-specify` -> `speckit-plan` -> `speckit-tasks` -> `speckit-analyze` -> `speckit-implement`).
- **Princípio V (Resiliência Operacional)**: **PASS**. Nenhuma alteração arriscada de schema ou migração no banco de produção.

## Project Structure

### Documentation (this feature)

```text
specs/074-manifesto-leitor-reflexivo/
├── spec.md              # Especificação de requisitos e critérios de aceite
├── plan.md              # Este plano técnico de implementação
├── research.md          # Decisões de arquitetura e pesquisas técnicas (Phase 0)
├── data-model.md        # Esquema de tipagem e modelos TypeScript (Phase 1)
├── contracts/           # Contratos de componentes e interfaces públicas (Phase 1)
│   └── landing-contracts.md
├── quickstart.md        # Guia de validação automatizada e interativa (Phase 1)
└── checklists/          # Checklists de qualidade
    └── requirements.md
```

### Source Code (repository root: `caderno-leitura-0.1/`)

```text
caderno-leitura-0.1/
├── frontend/
│   ├── index.html                                   # Preload de fontes e marcação semântica indexável inicial
│   ├── src/
│   │   ├── assets/ or src/
│   │   │   ├── fonts.css                            # Ajuste de font-display: swap para fontes locais
│   │   │   └── palettes.css                         # Ajuste de contraste do tema solario (--color-text)
│   │   ├── components/
│   │   │   ├── ThemePreviewGrid.vue                 # Grade canônica existente reutilizada no mostruário
│   │   │   └── landing/                             # Subcomponentes dedicados da Landing Page
│   │   │       ├── PublicHeader.vue                 # Cabeçalho com link de salto e navegação
│   │   │       ├── HeroSection.vue                  # Hero editorial com ficha de leitura e CTAs
│   │   │       ├── MethodSimulator.vue              # Bancada interativa em 4 dimensões (Machado de Assis)
│   │   │       ├── ThemeShowcase.vue                # Vitrine dos 10 temas com repintura em memória
│   │   │       ├── SovereigntySection.vue           # 4 princípios de soberania e tradição histórica
│   │   │       └── PublicFooter.vue                 # Rodapé reflexivo e links institucionais
│   │   ├── composables/
│   │   │   ├── useVisitorTheme.ts                   # Gestor de tema temporário em memória para visitantes
│   │   │   └── useSeoMeta.ts                        # Schemas e metatags estruturadas
│   │   ├── data/
│   │   │   └── landingSimulator.ts                  # Textos literários, marcas e análises em camadas
│   │   ├── router/
│   │   │   └── index.ts                             # Code-splitting com rotas protegidas sob demanda
│   │   ├── types/
│   │   │   └── settings.ts                          # Catálogo canônico de temas com contraste ajustado
│   │   └── views/
│   │       ├── LandingView.vue                      # Composição principal e landmarks
│   │       └── __tests__/
│   │           └── LandingView.spec.ts              # Suíte de testes unitários da nova landing page
│   └── vitest.config.ts
└── backend/
    ├── app/
    │   └── services/
    │       └── seo_service.py                       # Conformidade com robots.txt e sitemap.xml
    └── tests/
        └── test_seo.py                              # Testes de integridade de SEO no backend
```

**Structure Decision**: A implementação concentra-se no ecossistema de frontend do `caderno-leitura-0.1/frontend`, complementada pelos ajustes pontuais de SEO e sitemap no backend, preservando o desacoplamento de responsabilidades e garantindo velocidade de carregamento excepcional.

## Complexity Tracking

*Nenhuma violação constitucional identificada.*
