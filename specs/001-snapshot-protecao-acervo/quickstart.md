# Guia Rápido de Validação (Quickstart): Snapshot e Proteção do Acervo

**Feature**: `001-snapshot-protecao-acervo`  
**Date**: 2026-09-17  
**Status**: Ready for Validation  

---

## 1. Pré-Requisitos

1. Python 3.13 de 64 bits configurado no ambiente virtual [`backend/.venv`](file:///c:/Users/User/caderno/caderno-leitura-0.1/backend/.venv).
2. Dependências de desenvolvimento instaladas (`pytest`, `httpx`).
3. Todos os testes devem ser executados em bases temporárias descartáveis (`tmp_path`), garantindo isolamento total de `backend/data/caderno.db`.

---

## 2. Cenários de Validação de Ponta a Ponta

### Cenário 1: Criação e Validação Atômica de Snapshot em Base com Dados
**Objetivo**: Provar que o snapshot é gerado consistentemente a partir de uma base com dados sintéticos e que sua integridade é verificada com sucesso.

1. **Preparação**:
   Criar um banco SQLite temporário via fixture `tmp_path`, aplicar a migração inicial `0001_initial` e inserir 1 livro, 1 capítulo e 1 estudo com dados fictícios.
2. **Execução**:
   Chamar a função de snapshot:
   ```python
   snapshot = create_pre_upgrade_snapshot(database_path=db_temporario)
   ```
3. **Resultado Esperado**:
   - O arquivo `caderno-pre-migracao-*.db` é criado no subdiretório `backups/`.
   - O arquivo possui `journal_mode == "delete"`.
   - `inspect_snapshot(snapshot)` retorna:
     - `integrity_ok: True`
     - `counts: {"books": 1, "chapters": 1, "studies": 1}`
     - Nenhum texto privado é exposto.

---

### Cenário 2: Aborto Seguro de Migração quando Snapshot Falha
**Objetivo**: Provar que, se a criação ou validação do snapshot falhar, o processo de migração é cancelado e o acervo ativo permanece 100% inalterado.

1. **Preparação**:
   Simular um erro de gravação de snapshot (ex.: diretório de backup com permissão somente leitura ou disco simulado cheio).
2. **Execução**:
   Disparar o ciclo de migração (ou a função `ensure_pre_upgrade_snapshot`).
3. **Resultado Esperado**:
   - Uma exceção `RuntimeError` é disparada.
   - Nenhuma instrução DDL ou migração é executada.
   - O banco original preserva exatamente o mesmo timestamp, tamanho e registros anteriores.

---

### Cenário 3: Rotação Automática dos 5 Snapshots Mais Recentes
**Objetivo**: Provar que a criação de múltiplos snapshots retém apenas os 5 mais recentes, sem deletar backups manuais.

1. **Preparação**:
   Criar 6 snapshots sucessivos no diretório de backups, além de 1 arquivo de backup manual chamado `caderno-manual-importante.db`.
2. **Execução**:
   Executar a rotina `rotate_pre_upgrade_snapshots(backup_dir, keep=5)`.
3. **Resultado Esperado**:
   - Restam exatamente 5 arquivos do padrão `caderno-pre-migracao-*.db`.
   - O arquivo mais antigo da série foi removido.
   - O arquivo `caderno-manual-importante.db` permanece intocado.

---

### Cenário 4: Validação de Resolução de Caminhos no Windows
**Objetivo**: Provar que caminhos com espaços, acentos e caracteres especiais são tratados com segurança e que caminhos relativos são estritamente rejeitados.

1. **Execução**:
   - Testar `CADERNO_DATABASE_PATH="acervo/relativo.db"` -> Dispara `ValueError`.
   - Testar `CADERNO_DATABASE_PATH=tmp_path / "Pasta com Acentuação e Espaço 100%" / "caderno.db"` -> Resolve perfeitamente o caminho canônico.
2. **Resultado Esperado**:
   - Ambiguidade eliminada; segurança de caminhos comprovada no Windows.

---

## 3. Execução Automatizada dos Testes

Para executar toda a suíte de validação da feature em modo isolado:
```powershell
# A partir da raiz real da aplicação (caderno-leitura-0.1):
.\backend\.venv\Scripts\python.exe -m pytest backend/tests/test_backup_pre_upgrade.py -v
```
*(Nota: o arquivo de teste será implementado após a aprovação deste plano e a decomposição em tarefas via `/speckit-tasks`).*
