# Implementation Plan: Organizar nas 4 Seções

**Branch**: `089-organizar-quatro-secoes` | **Date**: 2026-10-27 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/089-organizar-quatro-secoes/spec.md`

## Summary

A feature leva ao Leitorum o organizador do EXP-023, como decidido no ADR-010.

- **Backend:**
  - um serviço em Python puro, cópia da implementação de referência, com o artefato de pesos `organizer-v1.json`
    conferido por SHA-256;
  - duas rotas no router de importação: `status` e `organize`;
  - um campo aditivo `bbox` nas linhas da pré-visualização da digitalização.
- **Frontend:**
  - um composable compartilhado (`useSectionOrganizer`) com organizar, mover e voltar;
  - o modo organizado da tela de digitalização, com 4 editores, "Seções para conferir" e "Voltar para texto
    único";
  - o botão "Organizar automaticamente" no painel de texto não classificado da importação, com desfazer.

**Paridade:** um fixture exportado pelo próprio EXP-023 prova que o produto reproduz o experimento em 144 de 144
casos.

Esta fatia não traz migração, dependência nova, leitura dos estudos do usuário nem calibração local. Decisões e
motivos em [research.md](research.md) (R1–R10).

---

## Technical Context

**Language/Version**: Python 3.13 (backend); TypeScript 5.6+ e Vue 3.5+ (`<script setup>`)

**Primary Dependencies**:
- **Backend:** só os já existentes (FastAPI, Pydantic 2) e a biblioteca padrão. O organizador usa `re`,
  `unicodedata`, `zlib`, `difflib`, `math` e `json`.
- **Frontend:** só os já existentes.

**Storage**:
- nenhuma mudança no SQLite;
- artefato estático `backend/app/data/organizer/organizer-v1.json` (0,22 MB, MIT);
- as 4 seções vão para o Estudo pelo `POST /api/studies` existente.

**Testing**:
- `pytest`, com banco descartável via `CADERNO_DATABASE_PATH` e textos fictícios, mais o fixture de paridade;
- `npm test` (`node --test`) e `npm run build`.

**Target Platform**: Windows 11 local (servidor único via `iniciar.py`), com acesso por navegador no PC e no
celular.

**Project Type**: aplicação web local (SPA Vue + API FastAPI).

**Performance Goals**: p95 ≤ 200 ms por página no servidor (SC-001). Referência do EXP-023: 8 ms por página
fictícia e 42 ms num estudo real longo.

**Constraints**:
- sem perda e sem reescrita;
- determinismo;
- até 50 000 caracteres e 400 trechos;
- nenhum texto em log;
- tokens semânticos, zero emojis e alvos de 44 px.

**Scale/Scope**: uma página ou um fichamento por pedido; pedidos curtos, sem fila.

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **I. Proteção do acervo e privacidade: PASS.**
  - A operação não lê nem grava estudos, e nada de texto vai para log.
  - Testes e validação só com textos fictícios.
  - O `source_response` continua sendo a leitura original (I.2).
- **II. Isolamento de testes: PASS.**
  - `pytest` sempre com `CADERNO_DATABASE_PATH` descartável. A 086 mostrou que a manutenção de inicialização abre
    o banco ativo sem isso; a correção está numa tarefa separada.
  - Banco em `tmp_path` nos testes da feature.
- **III. Fidelidade arquitetural: PASS.**
  - Python 3.13, FastAPI e Vue 3 sem dependência nova.
  - Servidor único (III.4) e nenhuma API externa.
- **IV. Governança SDD: PASS.** Ciclo specify → plan seguido, e tasks e analyze vêm depois, com aprovação a cada
  artefato. Feature avulsa: não altera o Roadmap 0.9.
- **V. Resiliência e migrações: PASS.** Sem migração. Com o artefato ausente, a função fica indisponível e o resto
  segue (FR-011).

**Re-check após o desenho (Phase 1)**: PASS. Os contratos confirmam zero escrita no banco, zero rede e mudança só
aditiva no contrato da 086.

---

## Project Structure

### Documentation (this feature)

```text
specs/089-organizar-quatro-secoes/
├── spec.md                          # aprovada (2026-10-27)
├── plan.md                          # este plano
├── research.md                      # decisões R1–R10
├── data-model.md                    # schemas e estados transitórios
├── quickstart.md                    # validação
├── contracts/
│   └── organize-api.contract.md     # status, organize e bbox aditivo na 086
└── tasks.md                         # próximo artefato, após aprovação
```

### Source Code

```text
document-intelligence/experiments/EXP-023/
├── harness/export_parity.py                 # NOVO — gera o fixture de paridade (24 páginas x 6 condições)
└── artifacts/parity-v1.json                 # NOVO — fictício, MIT

caderno-leitura-0.1/
├── backend/
│   ├── app/
│   │   ├── data/organizer/
│   │   │   ├── organizer-v1.json            # NOVO — cópia byte a byte do EXP-023
│   │   │   └── organizer-v1.sha256          # NOVO
│   │   ├── services/organizer/
│   │   │   ├── __init__.py                  # NOVO
│   │   │   ├── engine.py                    # NOVO — cópia de EXP-023/harness/organizer.py (sem mudança de lógica)
│   │   │   └── loader.py                    # NOVO — carga, SHA-256, cache, organize(), status()
│   │   ├── schemas/organize.py              # NOVO
│   │   ├── schemas/digitize.py              # + bbox em DigitizeLineRead
│   │   ├── services/digitize_service.py     # to_preview passa a bbox
│   │   └── routers/imports.py               # + GET /imports/organize/status, POST /imports/organize
│   └── tests/
│       ├── fixtures/organizer-parity-v1.json  # NOVO — cópia do fixture do EXP-023
│       ├── test_organizer_parity.py         # NOVO — 144/144 casos idênticos
│       ├── test_organize_api.py             # NOVO — contrato, limites, sem perda, cabeçalhos, artefato ausente
│       └── test_digitize_api.py             # + bbox na pré-visualização
└── frontend/
    ├── src/
    │   ├── types/organize.ts                # NOVO
    │   ├── services/api.ts                  # + getOrganizeStatus, organizeText
    │   ├── composables/useSectionOrganizer.ts   # NOVO — organizar, mover, voltar
    │   ├── composables/useDigitizeDraft.ts  # + modo organizado, save com 4 seções
    │   ├── composables/useImportDraft.ts    # + organizeUnassigned, undoOrganize
    │   ├── components/OrganizedSectionsEditor.vue  # NOVO — 4 editores, abas no celular
    │   ├── views/DigitizeNotebookView.vue   # botão, modo organizado, "Seções para conferir"
    │   └── views/ImportView.vue             # botão no painel de texto não classificado, desfazer
    └── tests/feature-089-organizar-quatro-secoes.test.mjs  # NOVO
```

**Structure Decision**:
- O organizador fica no backend, ao lado do parser de importação, porque é uma operação sobre texto e precisa
  funcionar sem o motor.
- A lógica de interface fica no composable compartilhado, testável sem navegador. As views só desenham.
- O `engine.py` é cópia literal do experimento, com cabeçalho de origem, para que a paridade seja verificável.

---

## Implementation Phases (para o speckit.tasks)

1. **Paridade e artefato** (portão):
   - `export_parity.py` no EXP-023, com commit no `document-intelligence/`;
   - cópia do artefato e do fixture para o backend;
   - `engine.py` e `loader.py`;
   - teste de paridade 144/144. Se falhar, a fatia para.
2. **Backend:** schemas, rotas, `bbox` na 086 e testes de contrato (limites, sem perda, cabeçalhos, autenticação,
   artefato ausente ou corrompido, nenhum texto em log).
3. **Frontend (digitalização):** tipos, API, `useSectionOrganizer` com testes, `OrganizedSectionsEditor.vue`,
   integração no `useDigitizeDraft` e na view.
4. **Frontend (importação):** `organizeUnassigned` e `undoOrganize` com testes, mais o botão na view.
5. **Validação e registro:**
   - quickstart §1–§4;
   - `RETOMADA.md`;
   - um commit `feature — organizar nas 4 seções`, só depois de `pytest`, `npm test` e `npm run build`
     aprovados.

---

## Complexity Tracking

*Nenhuma violação constitucional registrada.*
