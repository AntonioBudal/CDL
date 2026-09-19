# Quickstart & Validation Guide: Infraestrutura (T09-T10)

**Feature**: `016-infra-backup-operacao`  
**Date**: 2026-09-19  
**Status**: Completed  

---

## 1. Pré-requisitos de Ambiente

- Python 3.13 de 64 bits com ambiente virtual ativo (`.venv\Scripts\Activate.ps1`).
- Node.js 22+ com dependências do frontend instaladas em `frontend/node_modules`.
- Terminal PowerShell no Windows.
- **Constituição**: Todos os comandos utilizam diretórios temporários (`tmp_path`) e portas efêmeras, sem tocar no banco ativo local `backend/data/caderno.db`.

---

## 2. Cenários de Validação Automatizada (Backend)

### Executar Toda a Bateria de Testes de Infraestrutura
```powershell
pytest backend/tests/test_backup_bundle.py backend/tests/test_restore_safety.py backend/tests/test_concurrency_409.py -v
```

### Cenário 1: Geração e Validação do Pacote ZIP Completo
- **Objetivo**: Comprovar que o pacote ZIP gerado contém a base SQLite consistente, as capas anexadas e o manifesto `manifest.json` com hashes SHA-256 válidos.
- **Passos**:
  1. Cria banco temporário com 2 livros fictícios e 1 imagem de capa física.
  2. Executa a função de criação do pacote ZIP.
  3. Descompacta o arquivo e recalcula os hashes SHA-256 de cada item.
  4. Compara com os hashes do `manifest.json`.
- **Resultado Esperado**: Todos os hashes coincidem; integridade do banco é aprovada (`quick_check == 'ok'`).

### Cenário 2: Restauração Segura com Snapshot Prévio e Substituição Atômica
- **Objetivo**: Comprovar que a restauração substitui os dados com sucesso e gera um snapshot de salvaguarda do acervo anterior.
- **Passos**:
  1. Inicializa o acervo ativo "A" com 5 livros fictícios.
  2. Prepara um pacote de backup "B" com 10 livros fictícios e 2 capas.
  3. Dispara o serviço de restauração.
  4. Verifica que um snapshot `caderno-pre-restauracao-*.db` foi criado contendo o acervo "A".
  5. Verifica que o acervo ativo agora contém os 10 livros do acervo "B".
- **Resultado Esperado**: O acervo ativo foi atualizado e o snapshot anterior preservado.

### Cenário 3: Defesa contra Zip Slip / Path Traversal
- **Objetivo**: Garantir que tentativas de gravação fora do diretório temporário sejam sumariamente bloqueadas.
- **Passos**:
  1. Cria um arquivo ZIP sintético contendo um membro com nome `../../malicious.txt`.
  2. Submete o arquivo ao serviço de restauração.
- **Resultado Esperado**: O serviço levanta `ValueError` ("Tentativa de escape de diretório detectada"), aborta a operação e o acervo ativo permanece 100% inalterado.

### Cenário 4: Rejeição de Pacote Adulterado ou Corrompido
- **Objetivo**: Garantir que adulteração de 1 único byte no banco de dados invalide a restauração.
- **Passos**:
  1. Gera um pacote ZIP legítimo.
  2. Modifica 1 byte de `caderno.db` sem atualizar o `manifest.json`.
  3. Submete o pacote para restauração.
- **Resultado Esperado**: O serviço rejeita com erro de divergência de SHA-256 e nenhum dado ativo é tocado.

### Cenário 5: Resolução de Concorrência Otimista (409)
- **Objetivo**: Validar a rejeição de salvamento simultâneo e a capacidade de sobrescrita assistida.
- **Passos**:
  1. Leitor abre estudo no momento T0 (`updated_at` = T0).
  2. Outro dispositivo altera o estudo no momento T1 (`updated_at` = T1 > T0 + 1s).
  3. O leitor tenta salvar enviando `expected_updated_at` = T0.
  4. O backend retorna HTTP 409 Conflict.
  5. O leitor confirma "Sobrescrever com minhas alterações", reenviando com `expected_updated_at` = T1.
- **Resultado Esperado**: O salvamento forçado é aceito e o estudo atualizado com os dados digitados pelo leitor.

---

## 3. Cenários de Validação Automatizada (Frontend)

### Executar Testes Unitários de Concorrência e Restauração
```powershell
cd frontend
node --test tests/backup-restore.test.mjs tests/concurrency-conflict.test.mjs
```

- **Verificação**:
  - `useStudyEdit` intercepta o status 409, mantém o formulário preenchido e disponibiliza o estado de resolução.
  - O componente de backup exibe opções de download de `.zip` e gatilho de restauração.

---

## 4. Validação Operacional do Inicializador (`iniciar.py`)

### Teste de Conflito de Porta
1. Em um terminal PowerShell, execute uma escuta simulada na porta 8000:
   ```powershell
   $listener = [System.Net.Sockets.TcpListener]8000; $listener.Start()
   ```
2. Em outro terminal, execute:
   ```powershell
   python iniciar.py --port 8000
   ```
3. **Resultado Esperado**: O inicializador imprime mensagem amigável em português explicando que a porta 8000 já está em uso e sugere usar `--port 8001` ou fechar a outra instância, encerrando sem traceback de erro do Windows.
4. Feche o listener:
   ```powershell
   $listener.Stop()
   ```
