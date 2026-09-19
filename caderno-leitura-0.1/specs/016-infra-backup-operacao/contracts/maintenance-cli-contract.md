# CLI Contract: Utilitário de Manutenção (`maintenance.py`)

**Feature**: `016-infra-backup-operacao`  
**Module**: `app.services.maintenance`  
**Execution**: `python -m app.services.maintenance <subcomando> [argumentos]`  

---

## 1. Subcomando: `criar-backup`

Gera um pacote completo `.zip` contendo o banco consistente (`caderno.db`), a pasta de capas (`covers/`) e o manifesto criptográfico (`manifest.json`).

### Sintaxe
```bash
python -m app.services.maintenance criar-backup [--destino CAMINHO_ARQUIVO] [--json]
```

### Argumentos
- `--destino`, `-d`: Caminho opcional do arquivo `.zip` de saída. Se omitido, salva em `backend/data/backups/caderno-backup-YYYYMMDD-HHMMSS.zip`.
- `--json`: Emite o resultado em formato JSON na saída padrão (stdout).

### Saída Humana (Sucesso)
```text
Pacote de backup criado com sucesso!
Arquivo: C:\Users\...\backend\data\backups\caderno-backup-20260919-143000.zip
Tamanho: 1.450.231 bytes
Livros: 12 | Capítulos: 45 | Estudos: 150 | Capas: 2
Integridade: OK (SHA-256 verificado)
```

---

## 2. Subcomando: `verificar-backup`

Inspeciona o pacote `.zip` (ou arquivo `.db`) e confere a integridade física do SQLite e os hashes SHA-256 do manifesto sem alterar nenhum dado ativo.

### Sintaxe
```bash
python -m app.services.maintenance verificar-backup <caminho_arquivo> [--json]
```

### Argumentos
- `caminho_arquivo`: Caminho para o arquivo `.zip` ou `.db`.
- `--json`: Emite os metadados e status em JSON.

### Saída Humana (Sucesso)
```text
Pacote: caderno-backup-20260919-143000.zip
Data do Backup: 2026-09-19T14:30:00Z
Versão do App: 0.3.0
Revisão do Esquema: 0005_trash_and_covers
Integridade do Pacote: OK (todos os 3 arquivos conferem com SHA-256)
Integridade da Base SQLite: OK (PRAGMA quick_check e foreign_key_check aprovados)
Total de Livros: 12
Total de Capítulos: 45
Total de Estudos: 150
Capas Anexadas: 2
```

---

## 3. Subcomando: `restaurar-backup`

Restaura o acervo a partir de um pacote `.zip` ou arquivo `.db`. Realiza compulsoriamente a validação em sandbox, gera snapshot prévio do acervo ativo e substitui atomicamente os dados com proteção de rollback.

### Sintaxe
```bash
python -m app.services.maintenance restaurar-backup <caminho_arquivo> [--forcar] [--json]
```

### Argumentos
- `caminho_arquivo`: Caminho do arquivo `.zip` ou `.db` a ser restaurado.
- `--forcar`, `-f`: Pula a solicitação de confirmação interativa do terminal.
- `--json`: Emite o resultado em JSON.

### Confirmação Interativa
```text
ATENÇÃO: A restauração substituirá os livros, estudos e capas ativos no banco local.
Um snapshot de segurança do acervo atual será gerado automaticamente antes da substituição.
Deseja prosseguir com a restauração? (s/N): s
```

### Saída Humana (Sucesso)
```text
1. Validando pacote em ambiente temporário isolado... OK
2. Verificando integridade física e chaves estrangeiras... OK
3. Gerando snapshot de salvaguarda do acervo ativo: caderno-pre-restauracao-20260919-150210.db... OK
4. Restaurando base de dados e capas físicas... OK

Sucesso: Acervo restaurado com êxito!
Dados restaurados: 12 livros, 45 capítulos, 150 estudos e 2 capas.
```

---

## 4. Subcomandos Existentes Preservados
- `criar-snapshot`: Mantido para snapshots rápidos de banco (`.db`).
- `verificar-snapshot`: Mantido para inspeção rápida de arquivos `.db`.
