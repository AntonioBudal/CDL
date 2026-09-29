# Data Model: F0.6.5 — Histórico Automático de Versões de Estudo

## Visão Geral

Este documento define as entidades, relacionamentos, migração de banco de dados e regras de validação para o versionamento automático de estudos.

---

## 1. Entidade: `StudyVersion` (`study_versions`)

Representa um snapshot imutável do estado de um estudo em um determinado momento histórico, incluindo suas seções textuais e o conjunto de destaques/anotações associados.

### Tabela: `study_versions`

| Coluna | Tipo | Restrições / Padrão | Descrição |
| :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | `PRIMARY KEY AUTOINCREMENT` | Identificador único do snapshot |
| `study_id` | `INTEGER` | `NOT NULL, FOREIGN KEY (studies.id) ON DELETE CASCADE` | Estudo ao qual esta versão pertence |
| `version_number` | `INTEGER` | `NOT NULL` | Número sequencial da versão no estudo (1, 2, 3...) |
| `user_id` | `VARCHAR(36)` | `NULLABLE, FOREIGN KEY (users.id) ON DELETE SET NULL` | Autor responsável por esta versão |
| `title` | `TEXT` | `NOT NULL` | Título do estudo no momento do snapshot |
| `summary` | `TEXT` | `NOT NULL, DEFAULT ''` | Conteúdo da seção Resumo |
| `explanation` | `TEXT` | `NOT NULL, DEFAULT ''` | Conteúdo da seção Argumentos/Explicação |
| `concepts` | `TEXT` | `NOT NULL, DEFAULT ''` | Conteúdo da seção Conceitos |
| `references` | `TEXT` | `NOT NULL, DEFAULT ''` | Conteúdo da seção Citações/Referências |
| `notes` | `TEXT` | `NOT NULL, DEFAULT ''` | Anotações complementares |
| `highlights_data` | `TEXT` | `NOT NULL, DEFAULT '[]'` | Serialização JSON dos destaques e notas de Leitura Ativa |
| `change_summary` | `VARCHAR(100)` | `NOT NULL, DEFAULT 'Edição'` | Descrição curta da operação (ex.: "Edição", "Restauração da versão 2") |
| `created_at` | `DATETIME` | `NOT NULL, DEFAULT CURRENT_TIMESTAMP` | Data e hora de criação do snapshot |
| `updated_at` | `DATETIME` | `NOT NULL, DEFAULT CURRENT_TIMESTAMP` | Data e hora do último agrupamento (coalescência) |

### Índices e Restrições de Tabela

```sql
INDEX ix_study_versions_study_id (study_id)
INDEX ix_study_versions_user_id (user_id)
INDEX ix_study_versions_study_created (study_id, created_at DESC)
UNIQUE INDEX uq_study_version_number (study_id, version_number)
```

---

## 2. Estrutura do Snapshot de Destaques (`highlights_data`)

O campo `highlights_data` armazena um array JSON com os registros de `study_highlights` correspondentes àquele momento:

```json
[
  {
    "section": "summary",
    "start_offset": 45,
    "end_offset": 82,
    "selected_text": "conceito central da dialética",
    "prefix": "compreender o ",
    "suffix": " exige atenção",
    "color": "yellow",
    "kind": "highlight",
    "note": ""
  },
  {
    "section": "explanation",
    "start_offset": 120,
    "end_offset": 165,
    "selected_text": "pergunta essencial sobre causalidade",
    "prefix": "isto suscita a ",
    "suffix": " que examinamos",
    "color": "blue",
    "kind": "question",
    "note": "Qual o nexo causal demonstrado pelo autor?"
  }
]
```

---

## 3. Relacionamentos SQLAlchemy

```python
# app/models/study.py
class Study(Base):
    ...
    versions: Mapped[list["StudyVersion"]] = relationship(
        "StudyVersion",
        back_populates="study",
        cascade="all, delete-orphan",
        order_by="desc(StudyVersion.version_number)",
    )

# app/models/study_version.py
class StudyVersion(Base):
    __tablename__ = "study_versions"
    ...
    study: Mapped["Study"] = relationship("Study", back_populates="versions")
    user: Mapped["User | None"] = relationship("User")
```

---

## 4. Transições de Estado e Ciclo de Vida

```text
[Estudo criado]
       │
       ▼
(Primeira edição salva) ──► Cria Versão 1 (Baseline inicial)
       │                 ──► Cria Versão 2 (Estado após alteração)
       ▼
(Nova edição em < 5 min pelo mesmo autor) ──► Atualiza Versão 2 (Coalescência)
       │
(Nova edição após > 5 min ou outro autor) ──► Cria Versão 3
       │
       ▼
(Ação "Restaurar Versão 1")
       │
       ├──► 1. Arquiva estado presente como Versão N (se modificado)
       ├──► 2. Aplica conteúdo e destaques da Versão 1 no Study
       └──► 3. Cria Versão N+1 ("Restauração da versão 1")
```

---

## 5. Migração de Banco de Dados (`Alembic`)

- **Arquivo**: `migrations/versions/0021_add_study_versions.py`
- **Revisão anterior (`down_revision`)**: `0020_add_study_highlights`
- **Operação de `upgrade`**: Criação da tabela `study_versions` com índices e chave estrangeira em cascata.
- **Operação de `downgrade`**: Remoção dos índices e da tabela `study_versions`.
