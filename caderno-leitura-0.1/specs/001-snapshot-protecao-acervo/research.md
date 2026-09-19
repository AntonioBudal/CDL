# Technical Research: Proteção do Acervo e Snapshot Consistente Pré-Atualização

**Feature**: `001-snapshot-protecao-acervo`  
**Date**: 2026-09-17  
**Status**: Completed  

---

## 1. Mecanismo de Snapshot Consistente em SQLite Local

### Decisão
Utilizar a **SQLite Online Backup API** através do módulo nativo `sqlite3` do Python (`sqlite3.Connection.backup`), com o arquivo de origem aberto em modo estritamente somente leitura via URI (`?mode=ro&uri=true`). Após a conclusão da cópia no arquivo de destino:
1. Configurar `PRAGMA journal_mode=DELETE` exclusivamente na base de destino (garantindo que o arquivo de snapshot seja autocontido em um único arquivo `.db`, sem arquivos WAL dependentes).
2. Executar validação de integridade física (`PRAGMA quick_check`).
3. Executar validação de integridade relacional (`PRAGMA foreign_key_check`).

### Justificativa
- **Atomicidade e Consistência:** A cópia de arquivos SQLite pelo sistema operacional (via `shutil.copy` ou ferramentas de arquivo do Windows) não é atômica e corre sério risco de gerar arquivos corrompidos se houver escritas simultâneas ou páginas não sincronizadas no arquivo de Write-Ahead Log (`-wal`).
- **Não Bloqueante:** A SQLite Online Backup API copia páginas em blocos configuráveis (ex.: blocos de 256 páginas com pequenos intervalos) sem travar leitores ativos.
- **Autocontenção:** Ao converter o arquivo de backup gerado para `journal_mode=DELETE`, o snapshot passa a ser um arquivo isolado e independente, eliminando o risco de ficar órfão de arquivos `-wal` ou `-shm`.

### Alternativas Consideradas
- **Cópia direta de arquivos no sistema operacional (`shutil.copy2`):** Rejeitada categoricamente devido à vulnerabilidade a inconsistências e corrupções sob modo WAL.
- **Exportação via `.dump` SQL:** Rejeitada por ser sensivelmente mais lenta, consumir mais memória e gerar arquivos de texto plano que expõem os dados e notas do usuário no disco.

---

## 2. Centralização da Resolução de Caminhos da Base Ativa

### Decisão
Toda a aplicação (servidor FastAPI, Alembic, rotinas de manutenção e inicializadores) deve resolver a base de dados ativa através de uma função centralizada única em `backend/app/core/config.py`:
```python
def get_database_path() -> Path:
    configured = os.environ.get("CADERNO_DATABASE_PATH")
    if configured:
        path = Path(configured).expanduser()
        if not path.is_absolute():
            raise ValueError("CADERNO_DATABASE_PATH deve ser um caminho absoluto.")
        return path.resolve()
    return (BACKEND_DIR / "data" / "caderno.db").resolve()
```
Adicionalmente, criar a função complementar `get_backup_dir()`:
```python
def get_backup_dir() -> Path:
    db_path = get_database_path()
    backup_dir = db_path.parent / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    return backup_dir
```

### Justificativa
- **Previsibilidade:** Elimina qualquer dependência do diretório atual de trabalho (`cwd`) do terminal. Abrir a aplicação a partir da raiz do repositório, da pasta `backend`, de atalhos da área de trabalho ou de scripts automatizados resultará sempre no mesmo caminho canônico absoluto.
- **Segurança contra Caminhos Relativos:** A exigência explícita de caminhos absolutos evita a criação acidental de bancos vazios em pastas imprevistas.

### Alternativas Consideradas
- **Permitir caminhos relativos resolvidos a partir de `Path.cwd()`:** Rejeitada por ser a principal causa de desvios e criação de bancos fantasmas no ambiente Windows.

---

## 3. Nomenclatura e Organização dos Snapshots Pré-Migração

### Decisão
Conforme selecionado pelo usuário na clarificação (Opção A):
- **Diretório:** Subdiretório `backups/` anexo ao diretório da base de dados ativa (`backend/data/backups/`).
- **Padrão de Nomenclatura:** `caderno-pre-migracao-YYYYMMDD-HHMMSS.db` (utilizando carimbo de data e hora em UTC).

### Justificativa
- **Separação Clara:** Não polui o diretório raiz de dados com múltiplos arquivos `.db`.
- **Diferenciação Semântica:** Permite distinguir perfeitamente os snapshots automáticos gerados pelo ciclo de migração (`caderno-pre-migracao-...`) dos backups sob demanda baixados pelo usuário via interface web (`caderno-YYYYMMDD-HHMMSS-fZ.db`).

---

## 4. Política de Rotação Automática dos Snapshots

### Decisão
Manter os **5 snapshots pré-migração mais recentes** (Opção A selecionada pelo usuário).
- A rotina de rotação filtra exclusivamente arquivos no diretório de backups que correspondam ao padrão `caderno-pre-migracao-*.db`.
- Ordena os arquivos pela data/hora embutida no nome ou por data de modificação.
- Remove os arquivos excedentes (mais antigos que os 5 mais recentes).
- **Inviolabilidade de Backups Manuais:** Arquivos que não correspondam exatamente ao prefixo de snapshot automático pré-migração são estritamente ignorados.

### Justificativa
- Garante retenção de segurança para múltiplas etapas de atualização e reversão sem provocar crescimento descontrolado do uso de disco.

---

## 5. Ponto de Integração Pré-Migração (Barreira de Proteção)

### Decisão
Integrar a chamada da barreira de segurança em `backend/migrations/env.py`:
Antes de invocar `context.run_migrations()`, a rotina de migração executa:
1. `ensure_pre_upgrade_snapshot()`:
   - Verifica se a base ativa existe e possui tamanho > 0 bytes (se o banco não existir, é uma base virgem inicial e o snapshot não é necessário).
   - Cria o snapshot em `backend/data/backups/caderno-pre-migracao-YYYYMMDD-HHMMSS.db`.
   - Executa a validação de integridade na cópia gerada.
   - Aplica a rotação automática dos 5 snapshots mais recentes.
2. Se qualquer etapa falhar (erro de I/O, timeout de banco ocupado ou falha na integridade), a função lança `RuntimeError` bloqueante, impedindo que o Alembic execute qualquer instrução DDL no acervo ativo.

### Justificativa
- Protege todas as vias de execução: migrações automáticas disparadas por `iniciar.py`, execuções via CLI `alembic upgrade head` ou scripts de validação.

---

## 6. Inspeção Não Destrutiva e Proteção de Dados

### Decisão
A rotina de inspeção (`inspect_snapshot(path: Path) -> dict`) abre a cópia em modo somente leitura e consulta unicamente:
- Versão do esquema (`PRAGMA user_version` ou tabela `alembic_version`).
- Contagens agregadas de itens via `SELECT COUNT(*) FROM books`, `chapters`, `studies`.
- Tamanho em bytes do arquivo e carimbo de data de criação.

### Justificativa
- Cumpre rigorosamente o Artigo I da Constituição: fornece ao usuário e às rotinas de manutenção métricas quantitativas de integridade sem exibir ou registrar anotações, reflexões ou respostas importadas do ChatGPT.
