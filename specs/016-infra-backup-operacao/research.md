# Research & Architectural Decisions: Infraestrutura (T09-T10)

**Feature**: `016-infra-backup-operacao`  
**Date**: 2026-09-19  
**Status**: Completed  

---

## 1. Empacotamento de Backup Universal (.zip)

### Contexto
O sistema possuía apenas o download do arquivo bruto `.db` via `GET /api/backup`. No entanto, capas de livros cadastradas pelo leitor residem como arquivos estáticos no sistema de arquivos local (`backend/data/covers/`), e não dentro do SQLite. Além disso, a simples transferência de um arquivo `.db` não possui metadados sobre a versão do schema ou garantias criptográficas de integridade bit a bit.

### Decisão
Criar a rota `GET /api/backup/bundle` que gera um arquivo compactado `.zip` com compressão padrão `zipfile.ZIP_DEFLATED`.
O arquivo contém:
- `caderno.db`: Base SQLite gerada com a SQLite Online Backup API (`sqlite3.Connection.backup`), forçada em modo `PRAGMA journal_mode=DELETE` para autossuficiência de arquivo único.
- `covers/`: Pasta contendo as imagens de capas físicas existentes em `backend/data/covers/`. Se o diretório estiver vazio, a pasta é incluída ou omitida de forma graciosa.
- `manifest.json`: Arquivo contendo metadados estruturados e uma tabela com os hashes SHA-256 hexadecimais de cada arquivo contido no pacote.

### Justificativa
- A extensão universal `.zip` é nativamente compreendida pelo Windows Explorer, macOS Finder, gerenciadores de arquivos Linux e sistemas móveis (Android/iOS).
- A biblioteca padrão do Python possui o módulo `zipfile`, eliminando a necessidade de qualquer biblioteca externa ou binário do sistema.
- A rota `/api/backup` existente é preservada para compatibilidade de ferramentas de automação que buscam apenas o banco SQLite.

### Alternativas Rejeitadas
- **Arquivo `.tar.gz`**: Rejeitado porque no Windows muitos usuários não têm ferramentas nativas configuradas para abrir ou inspecionar arquivos `.tar.gz` com facilidade.
- **Armazenamento de imagens diretamente no SQLite (BLOBs)**: Rejeitado porque fragmenta o arquivo de banco, prejudica a performance de leitura de metadados e demandaria migração DDL de schema no banco de produção.

---

## 2. Manifesto de Autenticidade e Verificação Criptográfica (SHA-256)

### Contexto
Para validar se um arquivo compactado está intacto ou se sofreu corrupção durante o download/upload (ou truncamento de rede), é necessário um mecanismo de verificação rápida e inequívoca antes de abrir os arquivos.

### Decisão
Utilizar o algoritmo SHA-256 do módulo nativo `hashlib` para calcular a soma de verificação de:
1. `caderno.db`
2. Cada imagem presente em `covers/`
O manifesto é gravado como `manifest.json` na raiz do arquivo ZIP.

### Estrutura do `manifest.json`
```json
{
  "app_version": "0.3.0",
  "schema_version": "0005_trash_and_covers",
  "created_at": "2026-09-19T14:30:00Z",
  "generator": "Caderno de Leitura Backup Engine",
  "counts": {
    "books": 12,
    "chapters": 45,
    "studies": 150,
    "covers": 8
  },
  "files": {
    "caderno.db": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "covers/capa-1.jpg": "a591a6d40bf420404a011733cfb7b190d62c65bf0bcda32b57b277d9ad9f146e"
  }
}
```

### Justificativa
- O SHA-256 é imune a colisões práticas e computacionalmente muito rápido para o volume de dados do Caderno de Leitura (poucos megabytes).
- Permite verificar a integridade antes de realizar qualquer alteração estrutural no disco.

---

## 3. Prevenção Rigorosa contra Zip Slip e Path Traversal

### Contexto
Arquivos ZIP podem conter entradas com caminhos maliciosos, tais como `../../../../Windows/System32/calc.exe` ou `C:\qualquer_lugar\perigoso`. Se extraídos sem validação, podem sobrescrever arquivos do sistema operacional ou dados sensíveis fora do diretório do caderno.

### Decisão
Implementar uma função estrita de sanitização e extração segura:
```python
def validate_and_extract_zip(zip_path: Path, target_dir: Path) -> None:
    target_resolved = target_dir.resolve()
    with zipfile.ZipFile(zip_path, "r") as zf:
        for member in zf.infolist():
            # 1. Rejeita caminhos absolutos
            member_path = Path(member.filename)
            if member_path.is_absolute():
                raise ValueError(f"Caminho absoluto proibido no pacote: {member.filename}")
            
            # 2. Previne Zip Slip / Path Traversal
            destination = (target_dir / member_path).resolve()
            if not destination.is_relative_to(target_resolved):
                raise ValueError(f"Tentativa de escape de diretório detectada: {member.filename}")
            
            # 3. Permite apenas arquivos esperados
            parts = member_path.parts
            if not parts:
                continue
            first_part = parts[0]
            if first_part not in ("caderno.db", "manifest.json", "covers"):
                raise ValueError(f"Arquivo não autorizado no pacote de backup: {member.filename}")
            
            # Extração segura
            zf.extract(member, target_dir)
```

### Justificativa
- Garante conformidade total com as melhores práticas de segurança (CWE-22 / Zip Slip).
- Isola 100% da extração dentro de um diretório temporário efêmero.

---

## 4. Sandbox de Restauração, Snapshot de Salvaguarda e Rollback

### Contexto
A restauração do acervo é uma operação crítica. Se o usuário enviar um arquivo corrompido, incompleto ou incompatível, o acervo ativo não pode ser perdido sob nenhuma hipótese.

### Decisão
O processo de restauração segue 5 fases obrigatórias e atômicas:
1. **Fase 1: Sandbox de Extração**: O arquivo enviado é gravado em `tempfile.TemporaryDirectory()`. Se for `.zip`, passa pela validação de Zip Slip e checagem de hashes SHA-256 do `manifest.json`. Se for `.db` puro, é validado diretamente.
2. **Fase 2: Validação de Integridade do Banco**: O arquivo `caderno.db` restaurado é inspecionado com `PRAGMA quick_check` (integridade das árvores B-Tree do SQLite) e `PRAGMA foreign_key_check` (integridade referencial). Se houver erro, a restauração é abortada e a sandbox expurgada.
3. **Fase 3: Snapshot Pré-Restauração Compulsório**: Antes de mover ou sobrescrever qualquer arquivo ativo, o sistema gera uma cópia do banco ativo atual em `backend/data/backups/caderno-pre-restauracao-YYYYMMDD-HHMMSS.db` utilizando a SQLite Online Backup API.
4. **Fase 4: Substituição Atômica**:
   - Para o banco ativo: utiliza cópia consistente reversa ou substituição atômica de arquivo no disco.
   - Para as capas: copia as capas do pacote para `backend/data/covers/`.
5. **Fase 5: Rollback Automático em Caso de Erro**: Caso qualquer exceção de E/S ou de banco ocorra durante a Fase 4, o snapshot da Fase 3 é imediatamente restaurado para a posição ativa, garantindo zero inconsistência.

---

## 5. Concorrência Otimista (HTTP 409) e Resolução Assistida no Frontend

### Contexto
Ao acessar o caderno pelo computador e pelo smartphone simultaneamente (via rede local ou Tailscale), dois dispositivos podem abrir o mesmo estudo para leitura e anotação. Se ambos salvarem, o último salvaria sobrescrevendo o raciocínio do primeiro sem aviso.

### Decisão
- O backend já possui em `app/services/persistence.py` a função `check_optimistic_lock(current_updated_at, expected_updated_at, label="Estudo")` com tolerância de 1 segundo para relógios com skew.
- Ao detectar que `current_updated_at > expected_updated_at + 1s`, o backend lança `HTTPException(409, detail="Conflito de concorrência: ...")`.
- No frontend:
  - O composable `useStudyEdit.ts` intercepta o status 409 sem perder ou limpar o estado de edição (`state.dirty` permanece `true`, textos digitados ficam intactos no formulário).
  - É exibido o modal/diálogo `ConcurrencyConflictModal.vue` com duas opções (Clarificação Q3 - Opção A):
    1. **"Sobrescrever com minhas alterações"**: O frontend faz uma busca rápida pelo `updated_at` atual no servidor e reenvia o PATCH atualizado, gravando as alterações locais do usuário.
    2. **"Recarregar versão externa"**: O frontend descarta as alterações locais e recarrega os dados mais recentes do servidor via `load(study)`.

---

## 6. Resiliência de Inicialização e Detecção de Porta em `iniciar.py`

### Contexto
Se o usuário tentar executar `python iniciar.py` enquanto outra instância do servidor já estiver rodando na porta 8000 (ou outra aplicação estiver escutando na porta), o Uvicorn dispara uma exceção do Windows:
`[WinError 10048] Only one usage of each socket address (protocol/network address/port) is normally permitted` com traceback assustador.

### Decisão
Em `iniciar.py`:
1. Implementar verificação prévia de socket antes de disparar o Uvicorn:
   ```python
   def check_port_available(host: str, port: int) -> bool:
       with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
           s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 0)
           try:
               s.bind((host, port))
               return True
           except OSError:
               return False
   ```
2. Se a porta estiver ocupada, emitir mensagem informativa e clara em português:
   ```text
   ATENÇÃO: A porta 8000 já está em uso neste computador.
   Possíveis causas:
   - Uma outra janela do Caderno de Leitura já está aberta e rodando.
   - Outro aplicativo está ocupando a porta 8000.

   Para resolver:
   1. Encerre a outra janela do Caderno com Ctrl+C, OU
   2. Inicie em outra porta usando: python iniciar.py --port 8001
   ```
3. Capturar também o erro no bloco de execução do Uvicorn para proteção de ponta a ponta.

---

## 7. Utilitário CLI `maintenance.py`

### Contexto
Se a interface gráfica ou o servidor web estiverem inacessíveis por algum motivo de rede ou configuração, o leitor precisa ser capaz de criar backups, inspecionar pacotes e restaurar seus dados diretamente via linha de comando no terminal.

### Decisão
Expandir `backend/app/services/maintenance.py` com os seguintes subcomandos:
- `criar-backup [--destino CAMINHO_ZIP]`: Gera o pacote universal `.zip` completo com banco, capas e manifesto.
- `restaurar-backup <caminho_arquivo> [--forcar]`: Executa todo o pipeline de validação sandbox, snapshot prévio e restauração a partir de um `.zip` ou `.db`.
- `verificar-backup <caminho_arquivo>`: Inspeciona o arquivo sem restaurar, validando somas SHA-256, integridade física e contagens agregadas.
