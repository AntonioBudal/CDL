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
