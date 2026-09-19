# Implementation Plan: 007 — Zero-G: Superclasse Flutuante & Magnética

**Branch**: `007-zero-g-flutuante` | **Date**: 2026-09-19 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/007-zero-g-flutuante/spec.md`

---

## Summary

Implementação da primeira das 5 Superclasses de Interface: **Zero-G (Flutuante & Magnética)**.
A solução estabelece a infraestrutura global de Superclasses no Caderno de Leitura, provendo:
1. Um seletor de Superclasse e um controle de Intensidade da Física no subsistema de aparência da aplicação (`appearance-bootstrap.js`, `appearance.d.ts` e `AppearanceControls.vue`).
2. Parametrização matemática por fator multiplicador via `--sc-intensity` (Sutil 0.5x, Padrão 1.0x, Alta 1.5x, Desativada 0.0x).
3. Separação arquitetural estrita entre o visual estático (24 fontes, 10 temas, espaçamentos e botões permanecem soberanos sob as opções do usuário) e o motor físico dinâmico.
4. Animação de repouso (*idle breathing*) nos cartões do acervo com defasagem assíncrona de fase via keyframes compostos na GPU.
5. Atração magnética sutil ao cursor (máximo 4px) com desaceleração e inércia elástica (`cubic-bezier(0.16, 1, 0.3, 1)`).
6. Imobilidade garantida (100% estática) em áreas de texto contínuo e leitura de estudos.
7. Desativação integral automática sob `prefers-reduced-motion` ou opção de movimento desligada.

---

## Technical Context

**Language/Version**: TypeScript 6.0 (Strict mode), JavaScript (ES2022+), CSS3 Modern (Custom properties, calc, cubic-bezier, transform3d).  
**Primary Dependencies**: Vue 3.5 (Composition API, `<script setup>`), Vue Router 4, Vite 8. Zero dependências externas de física ou animação (100% nativo CSS e Pointer Events).  
**Storage**: Navegador `localStorage` sob a chave `caderno.aparencia.v2` integrada ao `cadernoAppearance`.  
**Testing**: Suíte nativa de testes Node (`node --test`), verificação estrita de tipagem (`vue-tsc -b`) e validação de build (`vite build`).  
**Target Platform**: Navegadores Desktop modernos (Windows, macOS, Linux) e dispositivos táteis móveis (Android, iOS).  
**Project Type**: Aplicação Web SPA (Frontend Vue/Vite atendido por servidor FastAPI local).  
**Performance Goals**: 60fps constante durante atração magnética e rolagem; zero impacto computacional em visualização de capítulos de texto; sem loops em JavaScript na ausência de interação do mouse.  
**Constraints**: Zero modificação nas preferências de temas cromáticos, fontes e botões; neutralização completa sob preferências de acessibilidade de redução de movimento.  
**Scale/Scope**: Grade do acervo (até centenas de livros com virtualização/paginação padrão), componentes de cartões e painel de ajustes.

---

## Constitution Check

*GATE: Passed prior to Phase 0 research. Re-evaluated and fully compliant post-design.*

- [x] **Princípio I (Privacidade e Proteção do Acervo)**: A feature é 100% visual e cinemática no frontend. Nenhuma consulta ao banco de dados ou conteúdo do acervo é manipulada.
- [x] **Princípio II (Isolamento de Testes)**: O banco ativo `backend/data/caderno.db` não é acessado. Testes unitários do frontend rodam isolados com o test runner do Node.
- [x] **Princípio III (Fidelidade Arquitetural)**: Utiliza a pilha homologada (Vue 3, TypeScript estrito, CSS desacoplado, Vite).
- [x] **Princípio IV (Spec-Driven Development)**: Fase de especificação (`spec.md`) e esclarecimento concluídas; planejamento técnico formalizado.
- [x] **Princípio V (Resiliência Operacional)**: Nenhuma migração de schema backend é requerida para esta feature.

---

## Project Structure

### Documentation (this feature)

```text
specs/007-zero-g-flutuante/
├── spec.md                                     # Especificação funcional e requisitos
├── plan.md                                     # Este documento de planejamento técnico
├── research.md                                 # Decisões arquiteturais e justificativas
├── data-model.md                               # Modelagem de tipos e variáveis CSS
├── quickstart.md                               # Guia de validação automatizada e manual
└── contracts/
    ├── appearance-preferences.contract.md      # Contrato de persistência e runtime
    └── zero-g-tokens.contract.md               # Contrato de tokens CSS e restrições de física
```

### Source Code Impacted

```text
caderno-leitura-0.1/
└── frontend/
    ├── src/
    │   ├── appearance.d.ts                      # Extensão da tipagem com superclass e intensity
    │   ├── appearance-bootstrap.js              # Inclusão dos campos no catálogo de aparência
    │   ├── styles/
    │   │   └── superclasses/
    │   │       └── zero-g.css                   # [NOVO] Folha de estilos e regras dinâmicas Zero-G
    │   ├── style.css                            # Importação modular de superclasses/zero-g.css
    │   ├── views/
    │   │   └── BooksView.vue                    # Atribuição de --card-index e integração magnética
    │   ├── composables/
    │   │   └── useMagneticHover.ts              # [NOVO] Composable de rastreamento do ponteiro
    │   └── components/
    │       └── AppearanceControls.vue           # Renderização limpa do grupo 11 de Superclasses
    └── tests/
        └── superclasses.test.mjs                # [NOVO] Testes de normalização e contratos
```

**Structure Decision**: A implementação adota modularização por diretório de estilos (`styles/superclasses/`), evitando poluir `style.css` com centenas de linhas de regras de arquétipos. O comportamento de cálculo relativo de ponteiro é isolado no composable reutilizável `useMagneticHover.ts`.

---

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|---|---|---|
| *Nenhuma violação identificada* | N/A | N/A |
