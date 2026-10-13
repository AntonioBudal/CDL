# Tarefas: Fechamento do contrato LDF (LDF 2.0)

* **Feature:** `001-contrato-ldf`
* **Entradas:** [`spec.md`](./spec.md) e [`plan.md`](./plan.md), ambos `APPROVED` em 2026-10-12
* **Status:** `EXECUTADO` em 2026-10-12 — aguardando aceite da feature e do ADR-004
* **Execução:** contínua, sem parar a cada fase; parada só no aceite final ou em bloqueio real

Convenções: `[P]` = pode ser feita em paralelo com as vizinhas (arquivos diferentes). Cada fase termina com
`uv run pytest` e `uv run ruff check .` limpos e um commit `FNN(document-inteligence) [contrato-ldf] <fase>`.
Testes são escritos antes do código que verificam. Só dados fictícios.

---

## Fase 0 — Preparação

- [x] **T001** Registrar os hashes de referência antes de qualquer mudança: SHA-256 de
  `docs/schemas/ldf-1.0.schema.json` e `git rev-parse HEAD:document-intelligence/experiments/EXP-00{1,2,3}`.
- [x] **T002** Adicionar `jsonschema` às dependências de `pyproject.toml`; `uv sync`; registrar em
  `docs/models-and-licensing.md` (MIT, `LICENSE STATUS: VERIFIED`, com a fonte consultada).
- [x] **T003** Criar `tests/ldf/test_frozen.py`: hash do schema 1.0 igual ao de T001; nenhum arquivo rastreado
  alterado em `experiments/EXP-001`, `EXP-002` e `EXP-003` em relação ao commit de T001 (SC-004, FR-014).

## Fase 1 — Schema e prosa (História 2, FR-004 a FR-010, FR-013 a FR-017)

- [x] **T004** Converter `src/leitorum_di/contracts/ldf.py` no pacote `contracts/ldf/` (mesmo caminho de
  importação); ajustar `contracts/__init__.py`. O modelo antigo é removido.
- [x] **T005** Escrever `contracts/ldf/schemas/ldf-2.0.schema.json` conforme o plano §4: `coordinate_space`,
  `pipeline.stages`, `recognition.lines`, `structure.regions`, `reading_order`, `diagrams` com `region_id`,
  `semantics` provisória, `human_corrections` com `target` e `ops`. Só `$defs`, `enum`, `required`,
  `additionalProperties: false`.
- [x] **T006** Garantir que o arquivo do schema entra no pacote instalado (configuração do `hatch`) e testar a
  carga por `importlib.resources`.
- [x] **T007** [P] Exemplos em `docs/ldf-examples/`: `ldf-2.0-minimal.json`, `ldf-2.0-layout-only.json`,
  `ldf-2.0-rectified.json`, `ldf-2.0-with-corrections.json`.
- [x] **T008** [P] Mover o texto atual para `docs/ldf-1.0.md` (marcado como congelado) e reescrever `docs/ldf.md`
  para o 2.0: estrutura, vocabulário, coordenadas, regras R1–R9 com código, regra de versão, correções.
- [x] **T009** [P] `docs/schemas/README.md` apontando para a fonte normativa do 2.0 e explicando o congelamento
  do 1.0.
- [x] **T010** Atualizar `tests/test_structure.py` apenas para **acrescentar** os caminhos novos; os existentes
  permanecem exigidos.

**Verificação:** exemplos válidos pelo schema; `test_frozen.py` verde.

## Fase 2 — Validação (História 1, FR-001 a FR-003; SC-003)

- [x] **T011** Casos de conformidade em `tests/ldf/conformance/`: `valid/` (ao menos os quatro exemplos, página
  vazia, linha sem região, região fora da ordem, diagrama sem nós) e `invalid/` (ao menos dois por regra R1–R9,
  mais campo desconhecido, tipo de região inexistente, versão não suportada). Cada inválido declara o código
  esperado num índice `conformance/index.json`.
- [x] **T012** `tests/ldf/test_schema.py` e `tests/ldf/test_rules.py`, dirigidos pelo índice (falham antes do código).
- [x] **T013** `contracts/ldf/schema.py`: carga em cache e validação de forma, com caminho e mensagem.
- [x] **T014** `contracts/ldf/geometry.py`: envelope de polígono, sentido dos vértices, caixa dentro da imagem,
  aplicação de homografia nos dois sentidos; `tests/ldf/test_geometry.py`.
- [x] **T015** `contracts/ldf/rules.py`: R1–R8 (R9 entra na Fase 4).
- [x] **T016** `contracts/ldf/validate.py`: `validate(doc)` devolve a lista de problemas (código, caminho,
  mensagem); verificação de versão antes do schema; as regras só rodam se a forma estiver válida.

**Verificação:** 100 % dos inválidos rejeitados com o código declarado; 100 % dos válidos aceitos.

## Fase 3 — Modelo Python (História 1; SC-001)

- [x] **T017** `tests/ldf/test_models_parity.py`: paridade de estrutura (campos, obrigatoriedade, enumerados,
  objeto a objeto) e de veredicto (todo caso de conformidade pelas duas vias); ida e volta sem perda.
- [x] **T018** `contracts/ldf/models.py`: modelo Pydantic com `extra="forbid"`, espelhando o schema.
- [x] **T019** Teste de cópia única: nenhum outro `ldf-2.0.schema.json` no repositório.

## Fase 4 — Correções humanas (História 4, FR-011, FR-012)

- [x] **T020** `tests/ldf/test_corrections.py`: correção sobrevive à remoção de linha anterior; inserção e
  remoção de elemento; alvo inexistente (R9); original intacto após aplicar; ordem de aplicação; conversão para
  JSON Patch absoluto equivalente.
- [x] **T021** `contracts/ldf/corrections.py`: `apply_corrections(doc)` (devolve cópia corrigida),
  `to_json_patch(doc)` e as seis operações RFC 6902, sem dependência nova.
- [x] **T022** Incluir R9 em `rules.py` e nos casos de conformidade.

## Fase 5 — Conversor de referência (História 2, FR-018; SC-002)

- [x] **T023** `tests/ldf/test_build.py`: página com caixa gráfica (região presente e na ordem), página só com
  layout (etapas `not_run`, linha sem texto), página retificada (ida e volta de coordenadas dentro de 1 px),
  linha inclinada (polígono preservado), componente com licença.
- [x] **T024** `contracts/ldf/build.py`: `build_document(...)` a partir de linhas, regiões, ordem, imagem,
  cantos da folha e componentes; saída sempre validada.
- [x] **T025** Teste sobre `dataset/fixtures/exp-003/test-manifest.json` (180 páginas, layout verdadeiro, sem o
  texto das linhas): zero problemas de validação, zero regiões descartadas, todas as caixas gráficas na ordem.
- [x] **T026** Verificação adicional, só se `dataset/processed/exp-003/detected-test.json` existir no disco:
  converter o layout detectado e registrar o resultado. Não recarregar modelos.

## Fase 6 — Fechamento (FR-020; SC-004 a SC-006)

- [x] **T027** `docs/adr/ADR-004-contrato-ldf-2.0.md` (`PROPOSED`) com alternativas consideradas e a situação de
  cada lacuna L1–L10 (resolvida ou adiada com justificativa); atualizar `docs/adr/README.md`.
- [x] **T028** [P] Nota em `docs/api-local.md` (segue `DRAFT`) e em `docs/handoff/PROMPT-ANTIGRAVITY-tela-placeholder.md`
  de que o contrato de referência passou a ser o LDF 2.0.
- [x] **T029** `specs/001-contrato-ldf/quickstart.md`: como validar um documento, aplicar correções e converter
  um layout; inclui a tabela de critérios de sucesso com o resultado medido.
- [x] **T030** Verificação final: `uv run pytest`, `uv run ruff check .`, testes dos harness dos EXP-002 e
  EXP-003 nos ambientes deles, `git status` sem nada fora de `document-intelligence/`.
- [x] **T031** Atualizar `CLAUDE.md` §3 e submeter ao usuário para aceite da feature e do ADR-004.

---

## Dependências

```text
Fase 0 → Fase 1 → Fase 2 → Fase 3
                        └→ Fase 4 → Fase 5 → Fase 6
```

A Fase 3 e a Fase 4 dependem só da Fase 2. A Fase 5 usa a validação (Fase 2) e a geometria (T014).

## Rastreabilidade

| Critério | Tarefas |
| :--- | :--- |
| SC-001 mesmo veredicto pelas duas vias | T017, T018 |
| SC-002 180 páginas sem lacunas | T025 |
| SC-003 inválidos rejeitados com o código certo | T011, T012, T015, T016, T022 |
| SC-004 experimentos aceitos intactos | T001, T003, T030 |
| SC-005 lacunas resolvidas ou adiadas no ADR | T027 |
| SC-006 nada fora da pasta | T030 |
