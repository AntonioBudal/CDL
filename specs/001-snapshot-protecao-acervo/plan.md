# Implementation Plan: Proteção do Acervo e Snapshot Consistente Pré-Atualização

**Branch**: `001-snapshot-protecao-acervo` | **Date**: 2026-09-17 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/001-snapshot-protecao-acervo/spec.md`

## Summary

Esta feature estabelece a fundação de segurança para a versão 0.3 (vinculada a T09 e T10). O objetivo é garantir que nenhuma migração de banco de dados ou rotina de manutenção estrutural ocorra sem antes criar e validar atomicamente um snapshot consistente do acervo ativo. A solução reutiliza a SQLite Online Backup API já homologada no backend, padroniza a resolução da base ativa através de `get_database_path()`, armazena os snapshots em `backend/data/backups/caderno-pre-migracao-YYYYMMDD-HHMMSS.db`, executa rotação automática mantendo os 5 snapshots mais recentes e provê inspeção diagnóstica sem jamais expor dados confidenciais do usuário.

## Technical Context

**Language/Version**: Python 3.13.15 (64-bit Windows)  
**Primary Dependencies**: FastAPI 0.141.1, SQLAlchemy 2.0.52, Alembic 1.19.2, Uvicorn 0.52.4, sqlite3 (stdlib)  
**Storage**: SQLite local (modo WAL em execução, modo DELETE nas cópias de backup), caminhos com suporte a acentos/espaços no Windows  
**Testing**: pytest 9.1.1 (`pytest backend/tests`), fixtures com `tmp_path` e portas efêmeras, 100% isoladas de `backend/data/caderno.db`  
**Target Platform**: Windows local (PowerShell / CMD), processo único local  
**Project Type**: Web Application pessoal (FastAPI backend servindo API e assets compilados do Vue) + utilitários de manutenção  
**Performance Goals**: Geração e validação de snapshot pré-migração em < 3 segundos para acervo típico local  
**Constraints**: Zero vazamento de texto do acervo em logs/telas; zero mutação de base se snapshot falhar; tolerância a caminhos Windows com espaços/acentos  
**Scale/Scope**: Monousuário local, acervo pessoal de livros/capítulos/estudos, até dezenas de milhares de registros  

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Artigo Constitucional | Exigência | Avaliação no Plano | Status |
|---|---|---|---|
| **Art. I: Privacidade do Acervo** | Proibido ler, expor ou registrar textos do acervo em logs ou telas | A rotina de inspeção calcula apenas contagens agregadas (`SELECT COUNT(*)`) e metadados de esquema; zero leitura de campos textuais (`summary`, `notes`, etc.) | **PASS** |
| **Art. II: Isolamento de Testes** | Testes nunca tocam em `backend/data/caderno.db` | Todos os testes automatizados da feature utilizam `tmp_path` e bases sintéticas descartáveis | **PASS** |
| **Art. III: Fidelidade Tecnológica** | Python 3.13, FastAPI, SQLAlchemy 2, Alembic, SQLite | Mantida estritamente a stack oficial sem introduzir bibliotecas desnecessárias | **PASS** |
| **Art. IV: Governança SDD** | Fatias pequenas e verificáveis; T01–T10 não iniciadas | Esta fatia foca unicamente no snapshot pré-migração e isolamento de caminhos, mantendo o roadmap como NÃO INICIADO | **PASS** |
| **Art. V: Resiliência Operacional** | Backup pré-migração consistente via SQLite Backup API; atomicidade | Utilização de `sqlite3.Connection.backup` com timeout e verificações `PRAGMA quick_check` + `PRAGMA foreign_key_check` | **PASS** |

## Project Structure

### Documentation (this feature)

```text
specs/001-snapshot-protecao-acervo/
├── spec.md              # Especificação de requisitos e cenários de aceite
├── plan.md              # Este plano técnico de implementação
├── research.md          # Decisões de pesquisa técnica (Fase 0)
├── data-model.md        # Modelagem lógica dos dados e entidades (Fase 1)
├── quickstart.md        # Guia passo a passo de validação executável (Fase 1)
├── contracts/           # Contratos de interfaces e serviços (Fase 1)
│   ├── backup-service.md
│   └── cli-maintenance.md
└── checklists/
    └── requirements.md  # Checklist de qualidade dos requisitos (100% aprovado)
```

### Source Code (repository root)

```text
caderno-leitura-0.1/
├── backend/
│   ├── app/
│   │   ├── core/
│   │   │   └── config.py              # Resolução canônica de caminhos (get_database_path, get_backup_dir)
│   │   ├── services/
│   │   │   ├── backups.py             # Primitiva de snapshot atômico (SQLite Backup API)
│   │   │   └── maintenance.py         # Orquestração pré-migração, rotação e inspeção de snapshots
│   │   └── db/
│   │       └── session.py             # Conexões e garantia de PRAGMA foreign_keys
│   ├── migrations/
│   │   └── env.py                     # Hook pré-migração no Alembic
│   └── tests/
│       └── test_backup_pre_upgrade.py # Testes de validação isolados com tmp_path
└── iniciar.py                         # Verificação unificada de caminho na inicialização
```

**Structure Decision**: A implementação estende a estrutura modular existente em `backend/app/services/` e `backend/app/core/config.py`, adicionando um módulo de manutenção focado (`maintenance.py`) para encapsular o ciclo pré-migração, inspeção e rotação de snapshots.

## Complexity Tracking

> Nenhuma violação constitucional identificada. A solução não introduz frameworks adicionais, dependências externas ou camadas desnecessárias.
