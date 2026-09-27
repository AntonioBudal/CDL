# Quickstart: Validação da Feature 10 (F10) — Segurança, Auditoria, Ciclo de Vida da Conta e Google OAuth

**Feature**: [spec.md](spec.md)  
**Date**: 2026-09-26  
**Status**: Ready  

Este guia detalha os procedimentos e comandos executáveis para validar todas as capacidades introduzidas pela Feature 10 tanto no backend quanto no frontend.

---

## 1. Pré-requisitos de Ambiente

Certifique-se de estar no ambiente virtual Python do backend e com o frontend pronto:
```powershell
# Backend
cd c:\Users\User\caderno\caderno-leitura-0.1\backend
.\.venv\Scripts\Activate.ps1

# Frontend
cd c:\Users\User\caderno\caderno-leitura-0.1\frontend
```

---

## 2. Cenários de Validação Automatizados

### Cenário 1: Rate Limiting e Prevenção de Ataques de Força Bruta
- **Objetivo**: Garantir que 5 requisições incorretas consecutivas ativem o bloqueio temporário retornando `HTTP 429 Too Many Requests`.
- **Execução**:
  ```powershell
  pytest backend/tests/test_rate_limit.py -v
  ```
- **Resultado Esperado**: As primeiras 5 tentativas retornam `HTTP 401 Unauthorized` ("Credenciais inválidas"); a 6ª tentativa retorna `HTTP 429 Too Many Requests` com cabeçalho `Retry-After` e bloqueio imediato.

---

### Cenário 2: Prevenção contra Enumeração de Contas (OWASP)
- **Objetivo**: Garantir mensagens e tempos padronizados para e-mails existentes e inexistentes.
- **Execução**:
  ```powershell
  pytest backend/tests/test_auth_anti_enumeration.py -v
  ```
- **Resultado Esperado**: Requisições com e-mails inexistentes e senhas erradas recebem exatamente a mesma resposta genérica (`401` com `detail: "Credenciais inválidas."`), sem revelar se o cadastro existe no banco.

---

### Cenário 3: Autenticação, Vínculo e Provisionamento com Google OAuth 2.0
- **Objetivo**: Validar login com Google com um clique sem exigência de senha local.
- **Execução**:
  ```powershell
  pytest backend/tests/test_google_auth.py -v
  ```
- **Resultado Esperado**:
  1. Token Google verificado cria um novo `User` com perfil ativo sem senha local.
  2. Nova tentativa com o mesmo e-mail faz login imediato sem duplicar usuário.
  3. Tentativa com e-mail já cadastrado localmente auto-vincula a identidade Google.

---

### Cenário 4: Trilha de Auditoria (`AuditLog`) e Sanitização Estrita
- **Objetivo**: Verificar a gravação imutável de eventos sensíveis e a ausência absoluta de segredos.
- **Execução**:
  ```powershell
  pytest backend/tests/test_audit_log.py -v
  ```
- **Resultado Esperado**: A tabela `audit_logs` registra eventos (`login_success`, `login_google`, `password_changed`, etc.) e o campo `details` não contém palavras-chave como `password`, `token` ou `secret`.

---

### Cenário 5: Ciclo de Vida — Desativação Temporária e Reativação Explícita
- **Objetivo**: Validar a desativação da conta e a tela intermediária de reativação (Opção B).
- **Execução**:
  ```powershell
  pytest backend/tests/test_account_lifecycle.py -k "test_deactivate_and_reactivate" -v
  ```
- **Resultado Esperado**:
  1. `POST /api/account/deactivate` encerra todas as sessões ativas e altera status para `deactivated`.
  2. Tentativa de login retorna `HTTP 403` com payload `ACCOUNT_DEACTIVATED`.
  3. `POST /api/account/reactivate` restabelece a conta como `active` e emite nova sessão.

---

### Cenário 6: Exclusão Definitiva em Cascata Física (LGPD)
- **Objetivo**: Confirmar o direito ao esquecimento com eliminação física total sem registros órfãos.
- **Execução**:
  ```powershell
  pytest backend/tests/test_account_lifecycle.py -k "test_definitive_deletion_cascade" -v
  ```
- **Resultado Esperado**: `DELETE /api/account` elimina livros, capítulos, estudos, categorias e o próprio usuário. `PRAGMA foreign_key_check` retorna 0 violações.

---

### Cenário 7: Portabilidade e Exportação Completa de Dados (ZIP)
- **Objetivo**: Validar a geração do pacote ZIP com Markdown e JSON consolidado (Opção A).
- **Execução**:
  ```powershell
  pytest backend/tests/test_account_export.py -v
  ```
- **Resultado Esperado**: `GET /api/account/export` retorna um arquivo ZIP íntegro contendo as pastas `[Livro]/[Capítulo]/[Estudo].md` e o arquivo `dados_acervo.json` na raiz.

---

### Cenário 8: Frontend — Botão Google e Seção de Segurança
- **Objetivo**: Validar os componentes de interface no Vue 3.
- **Execução**:
  ```powershell
  npm test
  npm run build
  ```
- **Resultado Esperado**: 100% dos testes de interface aprovados, incluindo botão Google em `LoginView.vue`, modal de confirmação de reativação e seção de segurança em `SettingsView.vue`.
