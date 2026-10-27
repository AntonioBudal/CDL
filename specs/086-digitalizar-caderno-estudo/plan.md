# Implementation Plan: Digitalizar Caderno — Foto de Página Manuscrita para Estudo

**Branch**: `086-digitalizar-caderno-estudo` | **Date**: 2026-10-27 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/086-digitalizar-caderno-estudo/spec.md`

## Summary

A tela `/digitalizar` deixa de ser informativa. O leitor tira ou escolhe a foto de uma página. O backend valida e
normaliza a imagem e chama o **motor de leitura** num processo separado. O motor é o pipeline do ADR-008,
promovido do `document-intelligence/`, com o leitor PP-OCRv6 de licença livre. A tela mostra o texto como
rascunho, com as linhas incertas listadas. O leitor revisa e salva como Estudo pelo `POST /api/studies` já
existente.

Esta fatia não traz migração, rede externa nem peso treinado com o BRESSAY.

Três peças:

1. **Motor** (`caderno-leitura-0.1/motor/`)
   - Pacote Python próprio, com ambiente próprio e instalação opcional.
   - Linha de comando `check` / `read`.
   - Modelos conferidos por SHA-256.
   - Leitor trocável por `config.json`.
2. **Backend**
   - Router `/api/digitize`, com `status` e `preview`.
   - Serviço que valida a imagem, controla memória, fila de um e tempo limite, cancela na desconexão, apaga os
     temporários e traduz a saída do motor.
3. **Frontend**
   - `DigitizeNotebookView.vue` reescrita.
   - Composable `useDigitizeDraft` com a máquina de estados.
   - Chamadas na `api`.
   - Card do Ateliê de Importação atualizado.

As decisões e os motivos estão em [research.md](research.md) (R1–R13).

---

## Technical Context

**Language/Version**: Python 3.13 (backend e motor, ambientes separados); TypeScript 5.6+ / Vue 3.5+
(`<script setup>`)

**Primary Dependencies**:
- **Backend** (sem dependência nova): FastAPI, Pydantic 2, Pillow, python-multipart.
- **Motor** (só no `motor/.venv`): `rapidocr==3.10.0`, `onnxruntime==1.31.0`,
  `opencv-python-headless==5.0.0.93`, `numpy==2.5.4`.

**Storage**: nenhuma mudança no SQLite. A imagem só existe numa pasta de `tempfile` durante o pedido. O Estudo é
criado pelo caminho atual.

**Testing**:
- `pytest`, com banco em `tmp_path` e motor falso por script;
- teste de fumaça do motor real, pulado se o motor estiver ausente;
- `npm test` (`node --test`) e `npm run build`.

**Target Platform**: Windows 11 local (servidor único via `iniciar.py`), com acesso por navegador no PC e no
celular pela rede local ou Tailscale.

**Project Type**: aplicação web local (SPA Vue + API FastAPI) + pacote de motor em processo separado.

**Performance Goals**: ≤ 20 s da foto ao texto numa página típica (SC-001). Referência: ~7 s de leitura mais o
carregamento dos modelos.

**Constraints**:
- pico do motor ~800 MiB;
- recusa abaixo de 2 GiB livres;
- um pedido por vez;
- tempo limite de 120 s;
- upload até 20 MB / 40 MP;
- zero rede externa;
- zero emojis e só tokens semânticos.

**Scale/Scope**: uma instância local com poucos usuários, uma página por pedido e um estudo por foto.

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **I. Proteção do acervo e privacidade: PASS.**
  - A foto fica na máquina e é apagada ao fim do pedido.
  - O texto lido não vai para logs.
  - Testes e validação só com dados fictícios.
  - A paridade (quickstart §4) roda localmente com imagens de teste fora do Git e relata só números.
  - `source_response` guarda a leitura bruta, o que preserva o texto original (I.2).
- **II. Isolamento de testes: PASS.**
  - `pytest` com banco em `tmp_path` e motor falso.
  - A validação manual usa `CADERNO_DATABASE_PATH` temporário e porta efêmera.
  - Nada toca `backend/data/caderno.db`.
- **III. Fidelidade arquitetural: PASS com observação.**
  - Backend e motor usam Python 3.13 de 64 bits. FastAPI e Vue 3 seguem sem dependência nova no backend.
  - O motor é um **segundo ambiente Python**, sem segundo servidor: é chamado sob demanda pelo processo único do
    `iniciar.py`, então III.4 continua valendo (ver Complexity Tracking).
  - Nenhuma API paga nem nuvem.
- **IV. Governança SDD: PASS.**
  - Ciclo specify → clarify → plan seguido. Tasks e analyze vêm depois, com aprovação a cada artefato.
  - Feature avulsa: não muda o estado das features do Roadmap 0.9.
- **V. Resiliência e migrações: PASS.**
  - Sem migração (NR-001), então não há backup pré-migração a fazer.
  - `instalar.py` continua aplicando `alembic upgrade head` como antes, sem revisão nova.
  - A configuração do motor segue o padrão de variáveis de ambiente do `config.py`.

**Re-check após o desenho (Phase 1)**: PASS. Contratos e modelo de dados confirmam zero tabela nova, zero acesso
a rede e o salvamento pelo caminho existente.

---

## Project Structure

### Documentation (this feature)

```text
specs/086-digitalizar-caderno-estudo/
├── spec.md                         # Especificação aprovada (2026-10-27)
├── plan.md                         # Este plano
├── research.md                     # Decisões R1–R13
├── data-model.md                   # Entidades transitórias e payload do Estudo
├── quickstart.md                   # Validação automática e manual
├── contracts/
│   ├── digitize-api.contract.md    # GET /api/digitize/status, POST /api/digitize/preview
│   └── motor-cli.contract.md       # check / read, config.json, troca de leitor
└── tasks.md                        # Próximo artefato (speckit.tasks), após aprovação deste plano
```

### Source Code

```text
caderno-leitura-0.1/
├── motor/                                  # NOVO — motor de leitura, ambiente próprio
│   ├── pyproject.toml
│   ├── requirements.txt                    # versões fixadas (R3)
│   ├── config.json                         # leitor, SHA-256, licença, alvo, fusão, limiar (R4, R10)
│   ├── leitorum_motor/
│   │   ├── __init__.py
│   │   ├── __main__.py                     # CLI check / read (contrato motor-cli)
│   │   ├── pipeline.py                     # detecção, escala, recorte, leitura CTC (de EXP-019)
│   │   ├── merge.py                        # fusão de fragmentos (de EXP-019)
│   │   └── geometry.py                     # recorte desentortado + ordem de leitura (de EXP-019 crop.py)
│   └── README.md                           # instalação, troca de leitor, licenças
├── backend/
│   ├── app/
│   │   ├── core/config.py                  # + get_motor_python(), limites de digitalização
│   │   ├── routers/digitize.py             # NOVO — /api/digitize/status, /preview
│   │   ├── schemas/digitize.py             # NOVO — DigitizePreviewRead, DigitizeStatusRead
│   │   ├── services/digitize_service.py    # NOVO — imagem, memória, fila, processo, limpeza
│   │   └── main.py                         # + include_router(digitize.router)
│   └── tests/
│       ├── test_digitize_api.py            # NOVO — motor falso, banco tmp_path
│       └── test_digitize_motor_smoke.py    # NOVO — motor real; pulado se ausente
├── frontend/
│   ├── src/
│   │   ├── types/digitize.ts               # reescrito — tipos da API; mantém DIGITIZE_EXIT_SHORTCUTS
│   │   ├── services/api.ts                 # + getDigitizeStatus, previewDigitize
│   │   ├── composables/useDigitizeDraft.ts # NOVO — estados, salvar como Estudo
│   │   ├── views/DigitizeNotebookView.vue  # reescrita — envio, leitura, revisão, salvar
│   │   └── views/ImportView.vue            # card: "Em Pesquisa" → "Rascunho a revisar"
│   └── tests/
│       ├── feature-086-digitalizar-caderno-estudo.test.mjs   # NOVO
│       └── feature-069-document-intelligence-placeholder.test.mjs  # removido (substituído, R13)
├── instalar.py                             # + flag opcional --motor (R3)
└── AVISOS-DE-TERCEIROS.txt                 # + rapidocr, PP-OCRv6, onnxruntime, OpenCV, NumPy

document-intelligence/
├── docs/adr/ADR-008-pipeline-de-referencia.md  # nota: pipeline promovido ao Leitorum (feature 086)
├── docs/roadmap-experiments.md                 # registro da promoção e da dispensa da validação com câmera
└── CLAUDE.md                                   # estado atual do projeto
```

**Structure Decision**: o motor fica em `caderno-leitura-0.1/motor/` porque precisa ser distribuído com o
Leitorum (R2). O backend só conversa com ele por linha de comando e arquivos temporários, e nunca o importa.
No frontend, a lógica fica no composable `useDigitizeDraft`, testável com `node --test` como o `useImportDraft`.
A view só desenha os estados.

---

## Implementation Phases (para o speckit.tasks)

1. **Motor**:
   - promover o código do EXP-019;
   - montar a CLI e o `config.json`;
   - criar o `motor/.venv` com Python 3.13;
   - rodar o `check`, o teste de fumaça, a paridade com o EXP-022 (quickstart §4) e a calibração do limiar (§5).

   Esta fase é o portão: se a paridade falhar, a fatia para aqui.
2. **Backend**: config, schemas, serviço e router, com testes usando o motor falso. Os testes cobrem cada linha
   da tabela de erros do contrato, a limpeza dos temporários, o pedido ocupado, a memória baixa, o tempo limite e
   o cancelamento.
3. **Frontend**: tipos, `api`, `useDigitizeDraft` com testes, a view reescrita, o card da importação, e a troca
   do teste 069 pelo 086.
4. **Instalação e avisos**: `instalar.py --motor`, `AVISOS-DE-TERCEIROS.txt` e o README do motor.
5. **Validação e registro**:
   - quickstart §1–§3 completo;
   - notas no `document-intelligence/`;
   - `docs/contexto/RETOMADA.md`;
   - um commit `feature — digitalizar caderno como estudo`, só depois de `pytest`, `npm test` e `npm run build`
     aprovados.

---

## Complexity Tracking

| Item | Por que é necessário | Alternativa mais simples descartada porque |
|------|----------------------|--------------------------------------------|
| Segundo ambiente Python (`motor/.venv`) | Isola OpenCV, ONNX Runtime e RapidOCR do backend (NR-004) e devolve ~800 MiB ao sistema após cada página | Instalar no `backend/.venv`: uma falha dessas bibliotecas quebraria a instalação e o início do Leitorum, e a memória ficaria presa no servidor |
| Processo filho por pedido | Tempo limite, cancelamento e falha contida sem derrubar o servidor | Chamar na mesma thread: um travamento do ONNX Runtime ou um estouro de memória derrubaria o Leitorum inteiro |
