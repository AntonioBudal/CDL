# Contrato CLI: Utilitário de Manutenção e Diagnóstico

**Comando**: `python -m app.services.maintenance` (ou script correspondente)  
**Objetivo**: Permitir inspeção não interativa e segura de backups e verificação de bases.

---

## 1. Comandos e Subcomandos

### `verificar-snapshot <caminho_arquivo>`
Inspeciona e valida a integridade física e referencial de um arquivo `.db` de snapshot.

- **Argumentos**:
  - `caminho_arquivo`: Caminho para o arquivo `.db` a ser inspecionado.
- **Opções**:
  - `--json`: Retorna a saída estritamente em formato JSON estruturado.
- **Saída Padrão (Texto Legível)**:
  ```text
  Snapshot: caderno-pre-migracao-20260917-210000.db
  Data de Criação: 2026-09-17 21:00:00 UTC
  Tamanho: 32.768 bytes
  Revisão do Esquema: 0001_initial
  Integridade: OK (física e chaves estrangeiras válidas)
  Total de Livros: 3
  Total de Capítulos: 12
  Total de Estudos: 45
  ```
- **Códigos de Saída (`Exit Code`)**:
  - `0`: Sucesso, snapshot íntegro e legível.
  - `1`: Erro, arquivo corrompido, chaves estrangeiras inválidas ou inacessível.

---

### `criar-snapshot [--destino <caminho>]`
Gera um snapshot manual ou pré-migração do banco ativo com validação imediata.

- **Opções**:
  - `--destino`: Caminho customizado de saída. Se omitido, grava em `backend/data/backups/caderno-pre-migracao-YYYYMMDD-HHMMSS.db`.
  - `--rotacionar`: Aplica a política de retenção mantendo os 5 mais recentes.
- **Códigos de Saída (`Exit Code`)**:
  - `0`: Snapshot criado e validado com sucesso.
  - `1`: Falha na criação, validação ou banco ocupado.
