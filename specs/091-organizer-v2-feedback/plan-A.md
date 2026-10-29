# Plano Técnico da Fatia 091-A: Organizador v2 no Lugar do v1

**Feature**: `091-organizer-v2-feedback`, fatia A | **Date**: 2026-10-28 | **Spec**: [spec.md](spec.md)

**Base**:
- [spec.md](spec.md): US1, FR-001 a FR-004 (só `engine.version`), SC-001 e SC-007; decisão Q1;
- [ADR-011](../../document-intelligence/docs/adr/ADR-011-organizer-v2-estatico.md) `ACCEPTED`;
- referência: `document-intelligence/experiments/EXP-025/harness/organizer_v2.py` (commit `f8ab9e0`).

**Status**: Concluído em 2026-10-28 ([tasks-A.md](tasks-A.md), A001 a A015): o serviço real responde `version "2"`.

---

## Summary

- Trocar o artefato do organizador do `organizer-v1.json` pelo `organizer-v2.json` do EXP-025.
- Portar a camada fina do v2 (as 4 pistas lidas do artefato) sem tocar no `engine.py`, que segue cópia literal
  do EXP-023.
- Paridade exata nos 192 casos fictícios do `parity-v2.json`.
- **Sem banco, sem migração, sem mudança de tela.** A única mudança visível no contrato é `engine.version`, que
  passa de `"1"` a `"2"`, com o SHA-256 novo.
- O campo `engine.adapter` (FR-004) fica para a fatia C, que é quem o preenche.

## Technical Context

- **Backend:** Python 3.13, só biblioteca padrão (`re`, `json`, `hashlib`), como o organizador atual. Nenhuma
  dependência nova.
- **Arquivos tocados:** `app/services/organizer/` (módulo novo `engine_v2.py`, `loader.py`), `app/data/organizer/`,
  `tests/fixtures/`, `tests/test_organizer_parity.py`, `tests/test_organize_api.py`. Do lado de fora do código, o
  contrato da 089 e a documentação.
- **Frontend:** nada. O tipo `engine.version` já é `string`, e a tela não mostra a versão.
- **Tamanho:** artefato 220 KB (v1: ~200 KB); fixture de paridade 839 KB (v1: ~600 KB).
- **Fins de linha:** o artefato é uma linha só, sem `\n`, então o SHA-256 não muda com `core.autocrlf`. O teste de
  paridade já normaliza CRLF no fixture.

## Constitution Check

| Regra | Como a fatia cumpre |
| :--- | :--- |
| Privacidade (AGENTS §1) | só dados fictícios (páginas MIT do EXP-023 e do EXP-024); nenhum texto em log |
| Banco ativo (AGENTS §2) | não toca o banco; os testes usam o banco descartável de sempre |
| Spec Kit fatiado (§4) | este plano → tarefas → implementação, cada um com aprovação |
| Stack (§5) | Python puro no backend, sem dependência nova |
| Commit (§6) | um commit no fim da feature 091 (as três fatias), com `pytest`, `npm test` e `npm run build` verdes |
| Escopo do `document-intelligence/` | nada é alterado lá; o artefato e o fixture são copiados |

## Design

### 1. `app/services/organizer/engine_v2.py` (novo)

- **Origem:** cópia de `organizer_v2.py` do EXP-025, com um cabeçalho igual ao do `engine.py`: cópia literal, não
  editar aqui sem repetir no experimento e regenerar o fixture.
- **Únicas adaptações:**
  - `import organizer as org` vira `from app.services.organizer import engine as org`;
  - sai o `sys.path` e o `ARTIFACT` do experimento;
  - `load(path)` vira `from_artifact(data: dict)`, porque quem lê o arquivo e confere o SHA-256 é o `loader`.
- **Conteúdo, sem mudança de lógica:**
  - `EXTRA_CUES` com as 4 expressões e os modos;
  - `cue_values(text)`;
  - `OrganizerV2(engine.Organizer)`, que sobrescreve só `analyse` (acrescenta as 4 colunas ao vetor);
  - as duas checagens do artefato: `extra_cues` igual ao conhecido, e as 4 colunas novas por último em
    `feature_names`. Falhou, `ValueError` (FR-002).

### 2. `app/services/organizer/loader.py`

| Antes | Depois |
| :--- | :--- |
| `ARTIFACT = …/organizer-v1.json` | `…/organizer-v2.json` |
| `EXPECTED_SHA256 = "60d6538d…"` | `"9f6530a32726d593142b7a2de3bce3efc1c0095abf3a91335364db6343978aee"` |
| `VERSION = "1"` | `"2"` |
| `engine.Organizer(engine.Model.from_json(…))` | `engine_v2.from_artifact(…)` |

- O `ValueError` das checagens do v2 já cai no `except` atual, então o caminho de erro é `integrity_failed`, como
  hoje.
- `organize()` não muda: chama `organizer.analyse` e `organizer.decide`, e o `analyse` do v2 é o que entra.
- O docstring do módulo passa a citar o EXP-025 e o ADR-011.

### 3. Artefatos e fixtures

- **Copiar para `app/data/organizer/`:** `organizer-v2.json` e `organizer-v2.sha256` do EXP-025.
- **Remover:** `organizer-v1.json` e `organizer-v1.sha256`. Volta para o v1 = reverter o commit.
- **Copiar para `tests/fixtures/`:** `organizer-parity-v2.json`, a partir de `artifacts/parity-v2.json`
  (SHA-256 `6726ddc4ce9049ec45f393fe84ef9412d70068cbb0c49819ade91e5713b71573`).
- **Fixture do v1:** `organizer-parity-v1.json` **fica**, para o teste de não regressão (§4).
  - os 144 casos do v1 são as mesmas páginas, com o mesmo texto e as mesmas linhas, dos 144 primeiros do v2;
  - medido agora: as seções saem iguais nos 144, e 140 casos são idênticos em tudo;
  - nos 4 restantes muda só a confiança de algum trecho.

### 4. Testes

**`tests/test_organizer_parity.py`, reescrito para o v2:**
- `FIXTURE` e `FIXTURE_SHA256` do v2;
- `artifact_sha256` do fixture igual a `loader.EXPECTED_SHA256`;
- `status()` com `version: "2"`;
- **192 de 192 casos** com igualdade exata de trechos, seções e cabeçalhos explícitos (SC-001);
- **não regressão contra o v1:** nos 144 casos do fixture do v1, as seções saem iguais, e em todo caso em que
  nenhuma pista dispara em nenhum trecho o resultado é idêntico ao do v1 (US1, cenário 2).

**Testes novos (`tests/test_organizer_v2.py`):**
- as 4 expressões do `engine_v2` são exatamente as do artefato instalado;
- `cue_values` com exemplos fictícios da spec do EXP-025: cada pista dispara no seu exemplo e não dispara numa
  frase comum;
- uma página fictícia com "- A margem e o centro — Lúcia Dantas" põe essa linha em Referências (US1);
- **artefato adulterado:**
  - com `extra_cues` diferente, `integrity_failed` mesmo com SHA-256 recalculado (o teste troca o `EXPECTED_SHA256`
    por `monkeypatch`);
  - com as colunas fora de ordem, a mesma coisa.

**`tests/test_organize_api.py`:**
- `version: "1"` passa a `"2"`;
- o nome do arquivo falso passa a `organizer-v2.json`;
- os demais testes continuam valendo como estão: limites, política de referências, cabeçalhos, nenhum texto nos
  logs, nenhuma escrita no banco e a guarda de latência.

### 5. Documentação

- **`specs/089-organizar-quatro-secoes/contracts/organize-api.contract.md`:** nota de que a 091 trocou a versão
  para `"2"`. Os exemplos passam a mostrar a versão e o SHA novos.
- **`caderno-leitura-0.1/docs/contexto/RETOMADA.md`:** entrada da 091-A.
- **`AboutView`:** nada nesta fatia. O parágrafo do registro local (Q2) entra na fatia B.

## Testes e validação

- Ordem: `pytest` (com as variáveis do banco descartável), depois `npm test`, depois `npm run build`. Nunca o build
  junto com o `pytest`.
- Linha de base medida antes de começar e registrada nas tarefas.
- Nenhum `alembic`, nenhum acesso ao `D:\Leitorum`.
- **Conferência no serviço real:** a troca de artefato só vale depois de reiniciar o serviço `Leitorum`. É você
  quem reinicia, como na 090. Depois:
  - `/api/imports/organize/status` deve responder `version: "2"`;
  - um texto fictício com uma referência em lista deve sair em Referências.

## Fases (detalhadas no `tasks-A.md`)

1. Linha de base dos testes.
2. Copiar os artefatos e os fixtures, e conferir os SHA-256.
3. `engine_v2.py` e `loader.py`.
4. Testes de paridade, do v2 e da API.
5. Documentação.
6. Validação completa.
7. Conferência no serviço real, com você.

## Riscos

| Risco | Mitigação |
| :--- | :--- |
| A cópia do `engine_v2` divergir da referência | paridade exata nos 192 casos; o cabeçalho proíbe editar sem repetir no experimento |
| O P4 perde 1,5 ponto (Conceitos com travessão viram Referências) | aceito no ADR-011; a sugestão continua revisável, e o registro da fatia B vai medir isso nos dados reais |
| Serviço rodando com o v1 em memória depois do deploy | o artefato é lido uma vez por processo; a conferência só vale depois de reiniciar o serviço |
| SHA-256 alterado por fim de linha no Git | o artefato não tem quebra de linha; o teste confere o hash a cada execução |
