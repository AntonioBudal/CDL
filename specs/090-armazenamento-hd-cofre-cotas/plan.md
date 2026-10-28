# Implementation Plan: Armazenamento no HD de 1 TB, Cofre de Imagens Criptografadas e Cotas

**Branch**: `090-armazenamento-hd-cofre-cotas` | **Date**: 2026-10-27 | **Spec**: [spec.md](spec.md)

**Input**: auditoria do código ([research.md §R0](research.md)) e pedido do usuário de 2026-10-27.

## Summary

Três camadas, entregues em três fatias com commits separados:

- **090-A, raiz única no HD:**
  - `LEITORUM_STORAGE_ROOT` com marcador de identidade e falha segura;
  - script de migração que copia pela API de backup, confere integridade e SHA-256 lógico, e só então troca o
    `.env`;
  - segunda cópia de backup fora do HD.
- **090-B, cofre:**
  - imagens sanitizadas, otimizadas em WebP e cifradas com AES-256-GCM, com chave por arquivo via HKDF-SHA256 a
    partir de uma chave mestra fora do HD (DPAPI);
  - arquivos `.enc` opacos;
  - tabela `encrypted_media`;
  - rotas autenticadas com regra de acesso por tipo;
  - capas e avatares migrados para o cofre;
  - backup e restauração do cofre.
- **090-C, ciclo de vida e espaço:**
  - foto de conferência opcional na digitalização;
  - "Folha original" no estudo;
  - retenção com job periódico;
  - "Minhas Imagens e Espaço";
  - cotas de 1 GiB por usuário e 900 GiB no servidor, mais o espaço livre real.

Decisões técnicas em [research.md](research.md) (R0–R12). Formato `.enc` em R2, chave em R3, schema em
[data-model.md](data-model.md), API em [contracts/media-api.contract.md](contracts/media-api.contract.md) e
migração em [contracts/migration-script.contract.md](contracts/migration-script.contract.md).

---

## Technical Context

**Language/Version**: Python 3.13 (backend, script de migração); TypeScript 5.6+ e Vue 3.5+

**Primary Dependencies**:
- **Backend:** FastAPI, SQLAlchemy 2, Alembic, Pillow (WebP) e `cryptography` 50.0.1 (AES-GCM e HKDF; já
  instalada, passa a dependência direta). DPAPI via `ctypes`.
- **Frontend:** sem pacote novo.

**Storage**:
- SQLite (WAL) em `<raiz>/db/`;
- cofre em `<raiz>/vault/<aa>/<uuid>.enc`;
- backups em `<raiz>/backups/`, mais a segunda cópia opcional;
- chave mestra no disco do sistema.

**Testing**: `pytest` em `tmp_path`, com raiz falsa de "HD", chave de teste, relógio injetável, falhas injetadas e
`disk_usage` simulado; `npm test` e `npm run build`.

**Target Platform**: Windows 11 Pro local, servidor único (`iniciar.py`), PC e celular pela rede local ou
Tailscale.

**Performance Goals**: decifrar e servir uma página com p95 ≤ 150 ms e uma miniatura com p95 ≤ 80 ms; job de
retenção em lotes de 200, sem travar requisições.

**Constraints**:
- origem nunca escrita na migração;
- chave nunca no HD nem em logs;
- nenhuma imagem em claro em disco, salvo a pasta temporária do sistema durante a leitura do motor, apagada no
  fim (research R4);
- `404` para mídia sem permissão.

**Scale/Scope**: poucos usuários por instância; até ~3 000 páginas por usuário (1 GiB) e 900 GiB no servidor.

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **I. Privacidade: PASS, e reforça.**
  - Imagens cifradas em repouso, metadados removidos, acesso autenticado.
  - O `source_response` e os textos não mudam.
  - Apagar imagem não toca no estudo (I.2).
- **II. Isolamento de testes: PASS.**
  - Tudo em `tmp_path`, com raiz e chave falsas.
  - O script de migração é validado inteiro em ambiente descartável antes de qualquer execução real.
- **III. Arquitetura: PASS.**
  - Mesmo stack e servidor único.
  - `cryptography` já está no ambiente; nenhuma API externa.
- **IV. SDD: PASS, com fatiamento.**
  - A arquitetura vira três fatias (A, B e C), cada uma com o próprio ciclo de tarefas e commit (IV.1).
  - Feature avulsa: não altera o Roadmap 0.9.
- **V. Migrações: PASS, com atenção.**
  - Duas migrações Alembic (`storage_settings` na A, `encrypted_media` na B), cada uma precedida pelo snapshot
    verificado (V.1).
  - O script de mudança de disco usa a API de backup (V.2) e não altera a origem (V.3).
  - `iniciar.py`, `config.py`, Alembic e o script passam a respeitar o mesmo contrato de caminhos (V.4).

**Re-check após o desenho**: PASS. A única exceção declarada é a imagem em claro na pasta temporária do sistema
durante a leitura do motor, já existente desde a 086 e apagada no fim do pedido.

---

## Project Structure

### Documentation

```text
specs/090-armazenamento-hd-cofre-cotas/
├── spec.md                               # histórias, requisitos, decisões pendentes Q1–Q6
├── plan.md                               # este plano (inclui o desenho das telas)
├── research.md                           # auditoria R0 e decisões R1–R12
├── data-model.md                         # storage_settings, encrypted_media, estados, configuração
├── contracts/
│   ├── media-api.contract.md             # /api/media/*, mudanças nas rotas existentes
│   └── migration-script.contract.md      # protocolo do script de migração para o HD
└── tasks-A.md, tasks-B.md, tasks-C.md    # uma lista de tarefas por fatia, após aprovação
```

### Source Code (por fatia)

```text
caderno-leitura-0.1/
├── backend/app/core/config.py              # A: get_storage_root(), precedência, falha segura, sem mkdir silencioso
├── backend/app/core/storage.py             # A: marcador .leitorum-storage.json, verificação de identidade
├── backend/app/db/session.py               # A: não cria a pasta do banco sob raiz configurada
├── backend/app/models/storage_settings.py  # A
├── backend/migrations/versions/0030_storage_settings.py         # A
├── scripts/migrate_storage_to_hd.py        # A (+ --vault-import na B)
├── iniciar.py                              # A: trava leitorum.lock, verificação da raiz, mensagem do HD
├── backend/app/services/backups.py         # A: segunda cópia; B: cofre no pacote e no manifesto
│
├── backend/app/core/media_key.py           # B: chave mestra (DPAPI/.env), impressão digital, barreira "fora do HD"
├── backend/app/services/vault.py           # B: formato .enc v1, HKDF, AES-GCM, gravação atômica, leitura
├── backend/app/services/media_service.py   # B: sanitização/WebP, cota, estados, autorização por tipo
├── backend/app/models/encrypted_media.py   # B
├── backend/migrations/versions/0031_encrypted_media.py          # B
├── backend/app/routers/media.py            # B: content/thumbnail/list/patch/delete; C: usage/bulk/attach
├── backend/app/services/avatar_service.py, cover_service.py     # B: gravam no cofre
├── backend/app/routers/profile.py, covers.py                    # B: rotas antigas resolvem para o cofre
├── backend/app/services/restore_service.py, export_service.py, account_service.py  # B: cofre em restauração, exportação, exclusão
├── instalar.py                             # B: --media-key (gerar ou restaurar com código de recuperação)
│
├── backend/app/services/media_retention.py # C: job (partida + a cada 6 h), reconciliação do cofre
├── backend/app/main.py                     # C: tarefa periódica no lifespan (cancelada no desligamento)
├── backend/app/services/digitize_service.py, routers/digitize.py  # C: keep_photo, stored_media
├── frontend/src/views/MediaSpaceView.vue   # C: "Minhas Imagens e Espaço" (/minhas-imagens)
├── frontend/src/components/media/StorageMeter.vue, MediaCard.vue, OriginalPageViewer.vue  # C
├── frontend/src/composables/useMediaSpace.ts, useOriginalPage.ts  # C
├── frontend/src/views/StudyView.vue        # C: "Folha original" ao lado do texto
└── frontend/src/views/DigitizeNotebookView.vue  # C: caixa "Guardar a foto", aviso de cota
```

---

## Desenho das telas (fatia C)

### "Minhas Imagens e Espaço" (`/minhas-imagens`, atalho no menu do usuário e em Ajustes)

```text
┌ Minhas Imagens e Espaço (h1) ───────────────────────────────────────────────────────────┐
│ Seu espaço                                                                              │
│ [██████░░░░░░░░░░░░░░░░░░░░]  Seu espaço: 312 MB de 1 GB utilizados (874 imagens)        │
│ Capacidade geral do servidor: 21 GB de 900 GB                       Estado: Normal       │
├ Liberar espaço (h2) ────────────────────────────────────────────────────────────────────┤
│ [Apagar fotos de estudos concluídos — 46 fotos, 15 MB]  [Apagar fotos com mais de 30 dias]│
├ Imagens (h2) ───── Filtros: [Tipo ▾] [Livro ▾] [Ordenar: mais recentes ▾] ──────────────┤
│ ☐ [miniatura]  Livro de Teste · Página digitalizada de teste                             │
│                27/10/2026 · expira em 30 dias · 348 KB                                   │
│                [Ver] [Manter permanentemente] [Apagar]                                   │
│ ☐ [miniatura]  ...                                                                       │
│ [Apagar selecionadas (2)]                                                                │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

- **Medidores:** `role="meter"` com `aria-valuenow`, `aria-valuemax` e `aria-valuetext` iguais ao texto exibido.
  - O nível aparece **em texto e ícone**: "Normal", "Quase cheio" (≥ 85 %) ou "Cheio". A cor vem só de tokens
    (`--color-accent`, `--color-warning-*`, `--color-error-*`).
  - No tema E-Ink, o preenchimento usa padrão de hachura, não só cor.
- **Ações em lote:** o rótulo já mostra a prévia (`dry_run`). A confirmação abre um diálogo modal acessível com
  "Apagar 46 fotos (15 MB)? Os estudos e seus textos não serão alterados." e o foco preso no diálogo.
- **Grade:**
  - miniaturas com `loading="lazy"` e `alt` "Página digitalizada do estudo …";
  - imagem `missing` ou danificada aparece como cartão "Arquivo indisponível", com "Apagar";
  - a seleção por caixa permite apagar em lote;
  - "Manter permanentemente" é um botão alternável com `aria-pressed`.
- **Estados:**
  - `EmptyState`, com ação "Digitalizar uma página";
  - `LoadingSkeleton` no formato de cartões;
  - cofre trancado (`vault_locked`), com explicação e o caminho para restaurar a chave.
- **Celular:** uma coluna; as ações vão para um menu por cartão com alvos de 44 px; a barra de lote fica fixa no
  rodapé quando há seleção.

### "Folha original" dentro do estudo (`StudyView.vue`)

- **Botão:** "Folha original (1)" na barra do estudo, só se houver foto vinculada.
- **Desktop:** um painel dividido, com o texto do estudo à esquerda e a foto à direita. A divisória pode ser
  ajustada (reaproveita `useSplitPanes`).
- **Celular:** abas "Texto | Folha original".
- **Visualizador:**
  - zoom com `+` e `−` (botões e teclado), ajuste à largura e arraste;
  - `alt` com o título do estudo;
  - várias fotos navegam com "anterior" e "próxima".
- **Rodapé do visualizador:**
  - "Apagada automaticamente em 23 dias" ou "Mantida permanentemente";
  - os botões "Manter permanentemente" e "Apagar foto".

  A confirmação diz: "O estudo e seus textos não serão alterados."
- **Rede:** a imagem é pedida só quando o painel abre e não fica em cache (`no-store`). Ao fechar, a URL `blob:` é
  revogada.

### Digitalização (`DigitizeNotebookView.vue`)

- **Caixa nova junto do salvamento:** "Guardar a foto com o estudo para conferência (apagada automaticamente em 30
  dias)", com o uso atual "312 MB de 1 GB".
- **Cota cheia ou cofre trancado:** a caixa fica desativada, com o motivo e o link para "Minhas Imagens e Espaço".
- **Texto de transparência:** muda conforme a escolha. "A foto é apagada assim que a leitura termina" vira "A foto
  fica guardada cifrada no seu espaço até …" quando a caixa está marcada.

---

## Implementation Phases (uma lista de tarefas por fatia, após aprovação)

| Fatia | Portões |
| :--- | :--- |
| **A** | script validado em `tmp_path` com todas as falhas injetadas; `--plan` no ambiente real (só leitura) e relatório apresentado ao usuário antes de `--execute`; `--execute` **só com aprovação explícita** e servidor parado |
| **B** | testes de cripto e da matriz de autorização; `--vault-import` em `tmp_path`, depois no real com aprovação; varredura de "zero imagens em claro" |
| **C** | testes do job com relógio injetável e de cotas concorrentes; medição de tamanho, legibilidade (CER no motor) e latência; conferência visual pelo usuário |

Cada fatia termina com `pytest`, `npm test` e `npm run build` aprovados, `RETOMADA.md` atualizado e um commit
`feature — …`.

---

## Complexity Tracking

| Item | Por que é necessário | Alternativa mais simples descartada porque |
| :--- | :--- | :--- |
| Duas migrações Alembic | `storage_id` para a falha segura; `encrypted_media` para cota, retenção e autorização | Guardar metadados em arquivos ao lado dos `.enc` exigiria varrer o disco para cota e listas e perderia a consistência transacional com os estudos |
| Tarefa periódica no `lifespan` | Retenção precisa rodar sem reinício do servidor | Rodar só na partida deixaria fotos vencidas ocupando cota por dias se o servidor ficar ligado |
| Três fatias | Constituição IV.1 (fatias pequenas e verificáveis) | Uma fatia única misturaria mudança de disco, criptografia e telas novas num commit só, difícil de validar e reverter |
