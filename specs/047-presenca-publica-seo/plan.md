# Implementation Plan: F0.6.8 — Presença Pública e SEO do Leitorum

**Branch**: `047-presenca-publica-seo` | **Date**: 2026-10-02 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/047-presenca-publica-seo/spec.md`

---

## Summary

Esta feature estrutura a presença pública e capacidade de descoberta orgânica do Leitorum nos mecanismos de busca, fornecendo:
1. **Páginas Institucionais Públicas**: Landing Page na raiz (`/`) para visitantes anônimos e página "Sobre o Leitorum" (`/sobre`) acessível no rodapé, explicando a metodologia em 4 partes de estudo e o compromisso sem anúncios.
2. **SEO Técnico e Blindagem de Privacidade**: Endpoint dinâmico `/sitemap.xml` para rotas institucionais e estudos públicos, `/robots.txt` com bloqueio explícito de 100% dos caminhos privados do acervo e cabeçalhos `X-Robots-Tag: noindex, nofollow` em rotas internas.
3. **Metadados Sociais e Semânticos**: Composable `useSeoMeta` no frontend para sincronização reativa de Open Graph, Twitter Cards, tags canônicas e dados estruturados Schema.org JSON-LD (`WebApplication` na home e `Article` em estudos públicos), acompanhado de favicons otimizados (SVG e PNG multi-resolução).

---

## Technical Context

**Language/Version**: Python 3.13 (Backend), TypeScript 5.8 / Node 24 (Frontend)  
**Primary Dependencies**: FastAPI, SQLAlchemy 2.0, Uvicorn, Vue 3, Vite, Tailwind/CSS  
**Storage**: SQLite 3 local (modo WAL), tabelas existentes `studies`, `books`, `support_settings`  
**Testing**: pytest (backend hermético com `TestClient`), Node test runner / Vitest (frontend)  
**Target Platform**: Windows local (PowerShell, portas locais) e produção em nuvem (`https://leitorum.com`)  
**Project Type**: Aplicação Web local-first (FastAPI + SPA Vue 3)  
**Performance Goals**: Tempo de resposta do `/sitemap.xml` e `/robots.txt` abaixo de 50ms; tempo de carregamento da página `/sobre` abaixo de 200ms  
**Constraints**: Zero vazamento de notas, livros ou dados do usuário privado; conformidade estrita com o Princípio I da Constituição  
**Scale/Scope**: 2 novas views públicas, 1 novo composable de SEO, 1 novo router FastAPI com endpoints de sitemap/robots, 1 conjunto de favicons/webmanifest e testes automatizados de ponta a ponta  

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Artigo Constitucional | Avaliação | Justificativa / Mitigação |
|---|---|---|
| **I. Proteção do Acervo e Privacidade** | ✅ APROVADO | Rotas privadas recebem `noindex, nofollow` e são bloqueadas no `robots.txt`. O `sitemap.xml` só indexa estudos com `visibility == 'public'` e `deleted_at IS NULL`. Zero dados privados expostos. |
| **II. Isolamento de Testes** | ✅ APROVADO | Testes automatizados executam sobre bancos SQLite efêmeros em `tmp_path`, sem tocar em `backend/data/caderno.db`. |
| **III. Fidelidade Arquitetural** | ✅ APROVADO | Utiliza FastAPI para servir endpoints dinâmicos de SEO e composables nativos Vue 3 no frontend, sem dependência de serviços externos ou bibliotecas desnecessárias. |
| **IV. Governança por Especificação** | ✅ APROVADO | Ciclo formal Spec Kit com branch atômica, especificação aprovada e plano técnico validado antes da geração de tarefas. |
| **V. Resiliência Operacional** | ✅ APROVADO | Nenhuma migração destrutiva de banco é necessária. Endpoints de SEO tratam exceções graciosamente com fallbacks estáticos seguros. |

---

## Project Structure

### Documentation (this feature)

```text
specs/047-presenca-publica-seo/
├── spec.md              # Especificação de requisitos e cenários
├── plan.md              # Este plano técnico de implementação
├── research.md          # Decisões de pesquisa técnica (Phase 0)
├── data-model.md        # Modelos conceituais e schemas (Phase 1)
├── quickstart.md        # Guia de validação ponta a ponta (Phase 1)
├── contracts/           # Contrato OpenAPI dos endpoints de SEO
│   └── seo-public-api.yaml
└── checklists/          # Checklists de qualidade
    └── requirements.md
```

### Source Code

```text
caderno-leitura-0.1/
├── backend/
│   ├── app/
│   │   ├── routers/
│   │   │   ├── seo.py                  # Endpoints /robots.txt e /sitemap.xml
│   │   │   └── __init__.py
│   │   ├── schemas/
│   │   │   └── seo.py                  # Schemas de metadados e sitemap
│   │   ├── services/
│   │   │   └── seo_service.py          # Lógica de agregação de URLs públicas
│   │   └── main.py                     # Inclusão do router de SEO e cabeçalhos de segurança
│   └── tests/
│       └── test_seo_and_public_presence.py # Testes de robots.txt, sitemap e X-Robots-Tag
│
├── frontend/
│   ├── public/
│   │   ├── favicon.svg                 # Ícone vetorial SVG adaptativo
│   │   ├── favicon-48x48.png           # Ícone rasterizado mínimo Google
│   │   ├── apple-touch-icon.png        # Ícone para iOS
│   │   ├── site.webmanifest            # Manifesto web PWA
│   │   └── assets/
│   │       └── og-cover.png            # Imagem de prévia social oficial 1200x630
│   ├── src/
│   │   ├── composables/
│   │   │   └── useSeoMeta.ts           # Composable reativo para title, og, twitter e ld+json
│   │   ├── views/
│   │   │   ├── LandingView.vue         # Landing page pública da raiz (/)
│   │   │   └── AboutView.vue           # Página institucional pública (/sobre)
│   │   ├── components/
│   │   │   └── layout/
│   │   │       └── AppFooter.vue       # Rodapé padronizado com links institucionais
│   │   └── router/
│   │       └── index.ts                # Definição das rotas públicas e guarda de redirecionamento
│   └── tests/
│       └── seo_metadata.test.mjs       # Testes unitários do composable e rotas
```

---

## Complexity Tracking

*Nenhuma violação constitucional ou desvio arquitetural detectado. Complexidade dentro dos padrões estabelecidos.*
