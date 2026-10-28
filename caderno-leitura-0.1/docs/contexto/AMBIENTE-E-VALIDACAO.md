# Ambiente e Validação Técnica

Este documento consolida as características do ambiente local Windows, os procedimentos de execução e a governança de testes para garantir integridade e isolamento absoluto de dados.

---

## 1. Inventário do Ambiente

| Ferramenta / Runtime | Versão Detectada | Caminho / Comando Recomendado | Função |
|---|---|---|---|
| **Python 3.13** | 3.13.15 (64-bit) | `py -3.13` | Runtime oficial da aplicação |
| **Python Venv** | 3.13.15 (64-bit) | `.\backend\.venv\Scripts\python.exe` | Ambiente virtual do backend |
| **Node.js** | v24.14.1 | `node` | Runtime para build e testes do frontend |
| **npm** | 11.11.0 | `npm` | Gerenciador de pacotes do frontend |
| **uv** | 0.11.21 | `uv` | Gerenciador de ferramentas e ambientes Python |
| **Specify CLI** | 1.0.1 | `specify` | CLI do GitHub Spec Kit |
| **Integração Spec Kit** | `agy` (Antigravity) | `specify integration status` (OK) | Skills e templates SDD |

---

## 2. Execução da Aplicação

### Modo Padrão (PC Local)
Executa na interface de loopback (`127.0.0.1:8000`):
```powershell
# Na raiz real da aplicação (caderno-leitura-0.1):
.\backend\.venv\Scripts\python.exe iniciar.py
# Ou via atalho:
.\INICIAR.cmd
```

### Modo Rede Local / Celular
Permite conexão de outros dispositivos na mesma rede Wi-Fi ou via Tailscale:
```powershell
# Na raiz real da aplicação (caderno-leitura-0.1):
.\backend\.venv\Scripts\python.exe iniciar.py --host 0.0.0.0 --ip <SEU_IP_LOCAL>
# Ou via atalho:
.\INICIAR-REDE.cmd
```
O servidor imprimirá no terminal a URL de acesso e um QR Code para leitura pela câmera do celular.

---

## 3. Build e Dependências

### Backend
As dependências estão fixadas em arquivos de lock/requisitos:
- `backend/requirements.txt`: Dependências de produção (`fastapi`, `sqlalchemy`, `alembic`, `uvicorn`, `pydantic`, `qrcode`, etc.).
- `backend/requirements-dev.txt`: Dependências de desenvolvimento e testes (`pytest`, `httpx`, etc.).

### Frontend
- O frontend compilado está versionado em `frontend/dist/`. O servidor FastAPI serve diretamente esses arquivos para que a aplicação funcione mesmo sem Node.js instalado.
- Para recompilar o frontend após modificações:
```powershell
Set-Location .\frontend
npm run build   # Executa vue-tsc -b && vite build
```

---

## 4. Governança e Execução de Testes

### Princípios de Segurança de Dados
1. **Isolamento Comprovado:** Todas as suítes de teste existentes (`backend/tests/`) utilizam a fixture `tmp_path` do pytest, criando bancos de dados temporários com caminhos isolados (inclusive testando caracteres especiais, espaços e acentos).
2. **Servidor Efêmero:** O teste `test_local_server.py` inicia um processo do Uvicorn com porta aleatória efêmera (`socket.bind(('127.0.0.1', 0))`) e direciona explicitamente `CADERNO_DATABASE_PATH` para o banco temporário daquele teste.
3. **Frontend Mockado:** Os testes do frontend (`frontend/tests/*.test.mjs`) usam o runner nativo do Node.js (`node --test`) com mocks das funções de gateway da API, sem disparar chamadas de rede reais.

### Comandos de Teste

#### Backend
```powershell
# Executar a partir de caderno-leitura-0.1:
.\backend\.venv\Scripts\python.exe -m pytest backend/tests
```

#### Frontend
```powershell
# Executar a partir de caderno-leitura-0.1\frontend:
npm test
```

> [!CAUTION]
> Nunca execute testes com a variável `CADERNO_DATABASE_PATH` configurada apontando para `backend/data/caderno.db`. Em ambientes de desenvolvimento/teste, garanta sempre que as fixtures temporárias sejam utilizadas.

---

## 5. Armazenamento no HD de 1 TB (feature 090-A)

A raiz `LEITORUM_STORAGE_ROOT` (por exemplo `D:\Leitorum`) guarda:
- `db/caderno.db`;
- `backups/`;
- as pastas legadas `covers/` e `avatars/`;
- o marcador `.leitorum-storage.json`.

O `storage_id` do marcador precisa ser igual ao gravado no banco (tabela `storage_settings`). Se o disco estiver
ausente ou for outro, o `iniciar.py` para com a mensagem `[ARMAZENAMENTO]` e **não cria nada**.

### Precedência dos caminhos

`CADERNO_DATABASE_PATH`, `CADERNO_COVERS_DIR` e `CADERNO_AVATARS_DIR`, quando definidos, vencem a raiz. Sem eles,
os caminhos derivam de `LEITORUM_STORAGE_ROOT`. Sem nenhum dos dois, vale `backend/data/` (comportamento
anterior).

### Migração assistida (servidor parado)

```powershell
# 1. Atualizar o banco (cria o snapshot pré-migração automaticamente)
py -3.13 instalar.py
# 2. Conferir sem gravar nada
backend\.venv\Scripts\python scripts\migrate_storage_to_hd.py --target D:\Leitorum --plan
# 3. Migrar (só depois de ler o relatório do passo 2)
backend\.venv\Scripts\python scripts\migrate_storage_to_hd.py --target D:\Leitorum --execute
# 4. Conferir a instalação migrada
backend\.venv\Scripts\python scripts\migrate_storage_to_hd.py --verify
```

O script:
- abre o banco de origem só para leitura e o copia pela API de backup;
- confere a cópia (`integrity_check`, `foreign_key_check`, contagens e SHA-256 lógico das linhas, revisão
  Alembic);
- copia os backups com SHA-256;
- só então grava `LEITORUM_STORAGE_ROOT` no `.env`, guardando o anterior em `.env.bak-<data>`.

Qualquer falha desfaz o que foi criado no destino e mantém o `.env`.

### Voltar atrás

O banco de origem fica intacto. Com o servidor parado, copie o `.env.bak-<data>` mais recente sobre o `.env`.
`--rollback-info` lista os arquivos. Mantenha a origem por pelo menos 30 dias antes de apagá-la manualmente.

### Recomendações para o disco

- HD interno ou sempre conectado, em NTFS; nunca unidade de rede.
- Desativar a suspensão do disco nas opções de energia do Windows.
- **Ativar o BitLocker na unidade.** O banco (textos dos estudos) e os backups no HD não são cifrados pelo
  Leitorum.
- Configurar `LEITORUM_SECONDARY_BACKUP_DIR` fora do HD. Backup só no mesmo disco não protege contra a perda do
  disco.

### Camadas extras de proteção contra perda (pedido do usuário, 2026-10-27)

Bloquear a exclusão da pasta inteira por permissão do Windows quebraria o Leitorum. O SQLite cria e apaga
`-wal` e `-shm`, a rotação apaga backups antigos e a restauração substitui o banco. A proteção real contra perda
são **cópias em outros lugares**:

1. **Segunda cópia de cada backup** em `LEITORUM_SECONDARY_BACKUP_DIR`, fora do HD.
2. **Backup automático:**
   - o servidor cria `caderno-auto-<data>.db` na partida e confere a cada hora se o último tem mais de
     `LEITORUM_AUTO_BACKUP_HOURS` (padrão 24);
   - guarda os `LEITORUM_AUTO_BACKUP_KEEP` mais recentes (padrão 14) na pasta de backups do HD **e** na segunda
     cópia;
   - nunca apaga snapshots pré-migração nem pacotes `.zip`.
3. **"Proteção do sistema" no `D:\`** (versões anteriores do Windows). É você quem ativa, por ser configuração de
   segurança do sistema. Para ativar:
   1. No menu Iniciar, digite **"Criar um ponto de restauração"** e abra.
   2. Na aba **Proteção do Sistema**, selecione a unidade **HD (D:)** e clique em **Configurar…**.
   3. Marque **"Ativar a proteção do sistema"** e ajuste o **Uso Máximo** para cerca de 5 % (~50 GB). Clique em
      **OK**.
   4. Ainda na aba, clique em **Criar…** e dê um nome como "Leitorum depois da migração". Repita sempre que fizer
      uma mudança grande.

   **Para recuperar uma pasta ou arquivo apagado:**
   1. No Explorador, clique com o botão direito em `D:\` (ou na pasta que continha o item) e escolha
      **Propriedades → Versões anteriores**.
   2. Escolha a data e use **Abrir** para conferir ou **Restaurar**.

   **Limite:** o Windows cria esses pontos sozinho só em atualizações e instalações. Para ter versões frequentes,
   crie pontos manualmente ou agende a criação no Agendador de Tarefas. A proteção também não substitui as
   camadas 1 e 2, porque fica no mesmo disco.

## 6. Cofre de imagens criptografadas (feature 090-B)

Avatares e capas (e, na fatia C, as fotos de páginas) nunca ficam em claro no disco. Cada imagem é limpa de
metadados (EXIF, GPS, ICC, XMP), otimizada em WebP e cifrada com AES-256-GCM em `<raiz>/vault/<aa>/<id>.enc`,
mais uma miniatura cifrada `<id>.thumb.enc`. Sem raiz configurada, o cofre fica em `backend/data/vault`.

### A chave mestra
- Fica **fora do HD**: `%LOCALAPPDATA%\Leitorum\media-master.key`, protegida pelo Windows (DPAPI, só abre com o
  seu usuário do Windows). Quem copiar o `D:\` leva só arquivos cifrados.
- Alternativa sem DPAPI: `LEITORUM_MEDIA_MASTER_KEY` (base64 de 32 bytes) num `.env` fora do HD.
- O banco guarda só a **impressão digital** da chave (16 hex), para detectar chave trocada. A chave nunca vai
  para backups, logs nem para o pacote `.zip`.

### Instalar a chave (uma vez)
```
py -3.13 instalar.py --media-key
```
Mostra o **código de recuperação uma única vez**. Anote e guarde fora do computador (papel, cofre de senhas).
Sem ele, reinstalar o Windows ou perder o arquivo da chave torna as imagens cifradas ilegíveis para sempre.

Para reinstalar a chave em outro Windows ou depois de formatar:
```
py -3.13 instalar.py --media-key --restore
```
O código é conferido com a impressão digital registrada no acervo; um código de outro acervo é recusado.

### Sem a chave
O Leitorum continua funcionando: livros, estudos e textos abrem normalmente. Só as imagens do cofre respondem
`503 vault_locked` ("cofre trancado"), avatares viram o fundo do círculo e capas mostram o marcador padrão.
Novos uploads de imagem também respondem `503` até a chave voltar. Uma chave diferente da registrada tranca o
cofre do mesmo jeito (`key_mismatch`), sem sobrescrever nada.

### Importar as capas e avatares antigos (servidor parado)
```
.\backend\.venv\Scripts\python.exe scripts\migrate_storage_to_hd.py --vault-import-plan
.\backend\.venv\Scripts\python.exe scripts\migrate_storage_to_hd.py --vault-import
```
- `--vault-import-plan` só lê: conta referências legadas, arquivos encontrados e ausentes, e o estado do cofre.
- `--vault-import` faz snapshot `caderno-pre-cofre-*.db` (com segunda cópia), cifra cada arquivo, confere a ida e
  volta e troca a referência no banco. **Os originais não são apagados**; o relatório lista quais podem ser
  apagados depois de você conferir. Referência sem arquivo fica como estava. Rodar de novo não duplica nada.

### Acesso e privacidade
| Tipo | Quem vê |
| :--- | :--- |
| avatar | qualquer usuário logado sem bloqueio com o dono |
| capa | quem pode ler o livro que a usa |
| página de caderno | só o dono |

Sem permissão, a resposta é `404`. As imagens são servidas com `Cache-Control: private, no-store` e nunca ficam
no cache do navegador. A exportação da conta (LGPD) traz as imagens decifradas em `imagens/`.

### Backup e restauração
O pacote `.zip` leva os `.enc` com SHA-256 no manifesto, a impressão digital da chave e o `storage_id`. A
restauração confere os SHA-256, mantém o `storage_id` da instalação atual e avisa quando o pacote foi cifrado com
outra chave (nesse caso, use `--media-key --restore` com o código daquela chave).
