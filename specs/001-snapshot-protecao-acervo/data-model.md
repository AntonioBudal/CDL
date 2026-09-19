# Data Model: Proteção do Acervo e Snapshot Consistente Pré-Atualização

**Feature**: `001-snapshot-protecao-acervo`  
**Date**: 2026-09-17  
**Status**: Completed  

---

## 1. Entidades Lógicas do Domínio de Infraestrutura

Esta feature não introduz novas tabelas relacionais de negócio ao banco de dados; ela define entidades lógicas que governam a persistência, o ciclo de vida e a validação de snapshots e arquivos de banco.

### Entidade 1: `DatabaseLocation` (Localização e Resolução da Base Ativa)
Representa o contrato de identificação da base de dados ativa do sistema.

| Campo | Tipo | Descrição | Regras de Validação |
|---|---|---|---|
| `configured_path` | `Path | None` | Caminho definido explicitamente via variável de ambiente `CADERNO_DATABASE_PATH`. | Se presente, DEVE ser absoluto (`is_absolute() == True`). Caminhos relativos disparam erro bloqueante. |
| `resolved_path` | `Path` | Caminho canônico final do arquivo `caderno.db`. | Deve ser absoluto, canônico (`resolve()`) e apontar para um arquivo com extensão `.db`. |
| `backup_directory` | `Path` | Diretório dedicado ao armazenamento dos snapshots automáticos. | Sempre resolvido como `resolved_path.parent / "backups"`. Criado automaticamente se inexistente. |

---

### Entidade 2: `PreUpgradeSnapshot` (Arquivo de Snapshot Pré-Migração)
Representa um arquivo físico de snapshot gerado atomicamente a partir da base ativa antes de uma migração.

| Campo | Tipo | Descrição | Regras de Validação |
|---|---|---|---|
| `file_path` | `Path` | Caminho absoluto do arquivo `.db` do snapshot. | Deve residir dentro de `backup_directory`. |
| `filename` | `str` | Nome do arquivo. | Padrão estrito: `caderno-pre-migracao-YYYYMMDD-HHMMSS.db`. |
| `timestamp` | `datetime` | Data e hora da geração (UTC). | Extraída do sufixo do nome do arquivo ou carimbo de criação. |
| `size_bytes` | `int` | Tamanho do arquivo em disco. | Deve ser maior que zero (`size_bytes > 0`). |
| `journal_mode` | `str` | Modo de journaling do arquivo gerado. | Deve ser obrigatoriamente `delete` (sem dependência de arquivos WAL/SHM). |
| `integrity_status` | `bool` | Resultado das verificações de integridade. | `True` somente se `PRAGMA quick_check == [('ok',)]` e `PRAGMA foreign_key_check` não retornar violações. |

---

### Entidade 3: `SnapshotInspectionReport` (Relatório de Diagnóstico do Snapshot)
Representa as informações quantitativas extraídas de um snapshot sem violar a privacidade do acervo.

| Campo | Tipo | Descrição | Regras de Validação |
|---|---|---|---|
| `snapshot_path` | `str` | Caminho do arquivo inspecionado. | Deve apontar para arquivo legível. |
| `created_at` | `str` | Carimbo ISO-8601 UTC de criação do arquivo. | Formato padronizado UTC. |
| `file_size_bytes` | `int` | Tamanho do arquivo no sistema de arquivos. | Valor inteiro >= 0. |
| `schema_revision` | `str | None` | Identificador de revisão do Alembic ou versão do esquema. | Obtido da tabela `alembic_version` ou `PRAGMA user_version`. |
| `integrity_ok` | `bool` | Confirmação de integridade física e referencial. | Booleano estrito. |
| `counts` | `dict[str, int]` | Quantitativos agregados por entidade. | Dicionário com chaves: `books`, `chapters`, `studies`. Valores inteiros >= 0. |

> [!IMPORTANT]
> **Garantia de Privacidade:** O modelo `SnapshotInspectionReport` proíbe terminantemente a inclusão de campos de texto livre (`title`, `summary`, `explanation`, `concepts`, `references`, `notes` ou `source_response`).

---

## 2. Ciclo de Vida e Transições de Estado

```text
[Base Ativa Existente]
         │
         │ (Gatilho: Solicitação de Migração / Alembic Upgrade)
         ▼
[Criando Cópia via Online Backup API]
         │
         ├─► [Falha de I/O / Timeout] ──► Aborta Migração + Remove Arquivo Temporário
         │
         ▼
[Cópia Criada em Memória/Temp]
         │
         ├─► [PRAGMA quick_check != ok] ──► Aborta Migração + Descarta Arquivo Corrompido
         │
         ├─► [PRAGMA foreign_key_check falha] ──► Aborta Migração + Descarta Arquivo Inválido
         │
         ▼
[Snapshot Pré-Migração Válido e Atômico]
         │
         ▼
[Aplicação da Rotação Automática (Top 5 mantidos)]
         │
         ▼
[Execução Segura da Migração / Atualização no Acervo]
```
