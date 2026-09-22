# Quickstart: Validação da Autenticação e Gestão de Sessões (F02)

**Feature**: `029-autenticacao-gestao-sessoes`  
**Date**: 2026-09-21  

Este guia detalha os procedimentos para validar a camada de autenticação nativa, proteção de credenciais com Argon2id, gerenciamento de sessões com cookies seguros e revogação remota de dispositivos.

---

## 1. Pré-Requisitos e Ambiente

- Python 3.13 / 3.14 (64 bits) no Windows com dependências instaladas (`fastapi`, `sqlalchemy`, `alembic`, `pydantic`, `argon2-cffi`, `pytest`, `httpx`).
- Node.js 24 com dependências do frontend instaladas (`npm test` funcional).
- Diretório de trabalho do backend: `caderno-leitura-0.1/backend`.
- Diretório de trabalho do frontend: `caderno-leitura-0.1/frontend`.

---

## 2. Cenário 1: Primeiro Acesso do Proprietário e Definição de Senha Mestra

**Objetivo**: Confirmar que o sistema identifica a ausência de senha na conta canônica legada e força a configuração no primeiro acesso.

### Procedimento
1. Consultar a rota pública de configuração:
   ```http
   GET /api/auth/config
   ```
   **Resultado Esperado**: `HTTP 200` com `{ "owner_setup_required": true, "allow_registration": true }`.
2. Tentar cadastrar a senha mestra enviando menos de 8 caracteres:
   ```http
   POST /api/auth/setup-owner
   Content-Type: application/json

   { "password": "123" }
   ```
   **Resultado Esperado**: `HTTP 400 Bad Request` indicando que a senha deve ter pelo menos 8 caracteres.
3. Cadastrar a senha mestra válida:
   ```http
   POST /api/auth/setup-owner
   Content-Type: application/json

   { "password": "SenhaForteSegura123!" }
   ```
   **Resultado Esperado**: `HTTP 200 OK`, cabeçalho `Set-Cookie: caderno_session=...; HttpOnly; SameSite=Lax`, e corpo confirmando a identidade do proprietário canônico.
4. Tentar submeter novamente `POST /api/auth/setup-owner`:
   **Resultado Esperado**: `HTTP 403 Forbidden` (operação permanentemente bloqueada após o primeiro setup).

---

## 3. Cenário 2: Cadastro de Novo Usuário (Auto-registro)

**Objetivo**: Confirmar a criação de novo perfil isolado com credencial Argon2id e sessão imediata.

### Procedimento
1. Enviar requisição de cadastro:
   ```http
   POST /api/auth/register
   Content-Type: application/json

   {
     "username": "leitor_novo",
     "display_name": "Novo Leitor",
     "email": "leitor@exemplo.com",
     "password": "MinhaSenhaSecreta987"
   }
   ```
   **Resultado Esperado**: `HTTP 201 Created`, cabeçalho `Set-Cookie: caderno_session=...` e `UserRead` correspondente ao novo usuário.
2. Tentar cadastrar novamente com o mesmo `username`:
   **Resultado Esperado**: `HTTP 409 Conflict`.
3. Consultar `GET /api/auth/me` utilizando o cookie recebido:
   **Resultado Esperado**: `HTTP 200 OK` exibindo o perfil do novo usuário.

---

## 4. Cenário 3: Autenticação, Senha Incorreta e Renovação de Sessão

**Objetivo**: Validar login com credenciais locais, proteção contra força bruta e anti-fixação de sessão.

### Procedimento
1. Tentar login com senha errada:
   ```http
   POST /api/auth/login
   Content-Type: application/json

   { "username_or_email": "leitor_novo", "password": "SenhaErradaTotal" }
   ```
   **Resultado Esperado**: `HTTP 401 Unauthorized` com mensagem amigável sem revelar detalhes.
2. Efetuar login com credenciais corretas:
   ```http
   POST /api/auth/login
   Content-Type: application/json

   { "username_or_email": "leitor_novo", "password": "MinhaSenhaSecreta987" }
   ```
   **Resultado Esperado**: `HTTP 200 OK` com novo cookie `caderno_session` (geração de novo token contra fixação de sessão).

---

## 5. Cenário 4: Listagem de Sessões Ativas e Revogação Remota

**Objetivo**: Verificar que o usuário inspeciona todos os seus acessos e revoga dispositivos alheios com efeito imediato.

### Procedimento
1. Simular dois dispositivos distintos fazendo login com o mesmo usuário:
   - Dispositivo 1: `User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64)...`
   - Dispositivo 2: `User-Agent: Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)...`
2. Consultar `GET /api/auth/sessions` a partir do Dispositivo 1:
   **Resultado Esperado**: Lista com 2 sessões. A do Dispositivo 1 possui `is_current: true` e a do Dispositivo 2 possui `is_current: false`.
3. A partir do Dispositivo 1, revogar a sessão do Dispositivo 2:
   ```http
   DELETE /api/auth/sessions/{id_sessao_dispositivo_2}
   ```
   **Resultado Esperado**: `HTTP 200 OK`.
4. Enviar requisição protegida a partir do Dispositivo 2 com seu cookie antigo:
   **Resultado Esperado**: `HTTP 401 Unauthorized` imediato.

---

## 6. Cenário 5: Logout Pontual e Logout-All

**Objetivo**: Confirmar que o logout destrói a sessão no banco e limpa o cookie no navegador.

### Procedimento
1. Enviar comando de encerramento:
   ```http
   POST /api/auth/logout
   ```
   **Resultado Esperado**: `HTTP 200 OK` e cabeçalho `Set-Cookie` com `Max-Age=0` (remoção do cookie).
2. Tentar acessar `GET /api/auth/me`:
   **Resultado Esperado**: `HTTP 401 Unauthorized`.

---

## 7. Comandos de Validação Automatizada

### Testes do Backend (Pytest)
```powershell
python -m pytest backend/tests/test_password_security.py backend/tests/test_session_lifecycle.py backend/tests/test_device_management.py -v
```

### Testes Gerais de Regressão do Backend
```powershell
python -m pytest backend/tests
```

### Testes e Build do Frontend
```powershell
cd frontend
npm test
npm run build
```
