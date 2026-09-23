# Quickstart: Validação da Conta Google e Vinculação de Identidade (F03)

**Feature**: `030-conta-google-identidade`  
**Date**: 2026-09-22  

Este guia detalha os procedimentos para validar a integração com Google Identity Services (GIS), verificação criptográfica do token de identidade via `google-auth`, vinculação/desvinculação de identidades no banco local com prevenção de bloqueio (*lockout*), e funcionamento offline/degradação graciosa.

---

## 1. Pré-Requisitos e Ambiente

- Python 3.13 / 3.14 (64 bits) no Windows com dependências instaladas (`fastapi`, `sqlalchemy`, `alembic`, `pydantic`, `google-auth`, `pytest`, `httpx`).
- Node.js 24 com dependências do frontend instaladas (`npm test` e `npm run build` funcionais).
- Diretório de trabalho da aplicação: `caderno-leitura-0.1`.
- Configuração do Google Client ID (para testes manuais): `GOOGLE_CLIENT_ID="exemplo-client-id.apps.googleusercontent.com"`.
- Para testes automatizados: todos os testes utilizam mocks herméticos da biblioteca `google-auth` e bancos temporários SQLite (`tmp_path`), sem requisições HTTP externas.

---

## 2. Cenário 1: Degradação Graciosa (Google Desabilitado)

**Objetivo**: Confirmar que na ausência de `GOOGLE_CLIENT_ID`, a aplicação funciona em modo local puro sem carregar scripts externos.

### Procedimento
1. Iniciar a API ou consultar a rota de configuração sem a variável `GOOGLE_CLIENT_ID`:
   ```http
   GET /api/auth/config
   ```
   **Resultado Esperado**: `HTTP 200 OK` contendo:
   ```json
   {
     "allow_registration": true,
     "owner_setup_required": false,
     "google_auth_enabled": false,
     "google_client_id": null
   }
   ```
2. Carregar a página de login no frontend:
   **Resultado Esperado**: Apenas o formulário padrão de usuário e senha é exibido. Nenhum script de `https://accounts.google.com/gsi/client` é injetado no DOM.
3. Tentar submeter uma credencial Google diretamente para a API:
   ```http
   POST /api/auth/google
   Content-Type: application/json

   { "credential": "token-ficticio" }
   ```
   **Resultado Esperado**: `HTTP 400 Bad Request` informando que o login com Google não está habilitado neste servidor.

---

## 3. Cenário 2: Login com Conta Google Já Vinculada

**Objetivo**: Confirmar a emissão do cookie de sessão HTTP-Only após validação bem-sucedida do token do Google via correspondência do `sub`.

### Procedimento
1. Configurar `GOOGLE_CLIENT_ID` no ambiente e possuir um usuário com identidade cadastrada em `external_identities` (`provider="google"`, `provider_subject="google-sub-123"`).
2. Enviar a credencial retornada pelo GIS:
   ```http
   POST /api/auth/google
   Content-Type: application/json

   { "credential": "jwt-valido-google-sub-123" }
   ```
   **Resultado Esperado**:
   - `HTTP 200 OK`
   - Cabeçalho `Set-Cookie: caderno_session=...; HttpOnly; SameSite=Lax; Path=/`
   - Resposta `UserRead` contendo dados do usuário e `has_google: true`.
3. Acessar `GET /api/auth/me` com o cookie retornado:
   **Resultado Esperado**: `HTTP 200 OK` com os dados do usuário autenticado.

---

## 4. Cenário 3: Vinculação Automática por E-mail Verificado

**Objetivo**: Verificar que uma conta local existente com e-mail idêntico ao do Google é automaticamente vinculada quando `email_verified=True`.

### Procedimento
1. Usuário local existe com e-mail `leitor@exemplo.com`, mas sem registro em `external_identities`.
2. O usuário inicia login com o botão Google e o token JWT possui:
   - `sub`: `"google-sub-456"`
   - `email`: `"leitor@exemplo.com"`
   - `email_verified`: `true`
3. Submeter credencial para `POST /api/auth/google`:
   **Resultado Esperado**:
   - `HTTP 200 OK`
   - Registro criado em `external_identities` associado ao usuário.
   - Sessão criada e cookie emitido.

---

## 5. Cenário 4: Rejeição de E-mail Não Verificado

**Objetivo**: Garantir que contas do Google sem confirmação de e-mail não possam se apropriar de contas locais.

### Procedimento
1. Enviar credencial Google onde `email_verified` é `false`:
   ```http
   POST /api/auth/google
   Content-Type: application/json

   { "credential": "jwt-com-email-nao-verificado" }
   ```
   **Resultado Esperado**: `HTTP 400 Bad Request` com mensagem detalhando que o e-mail da conta Google deve estar verificado. Nenhuma conta é vinculada ou criada.

---

## 6. Cenário 5: Bloqueio de Registro quando Desabilitado

**Objetivo**: Garantir que novas contas Google sejam rejeitadas com `HTTP 403 Forbidden` quando `ALLOW_REGISTRATION=false` e a identidade não estiver pré-cadastrada.

### Procedimento
1. Definir ambiente com `ALLOW_REGISTRATION=false`.
2. Enviar credencial Google de um usuário novo (cujo `sub` e e-mail não constam no banco):
   ```http
   POST /api/auth/google
   Content-Type: application/json

   { "credential": "jwt-novo-usuario-sem-conta" }
   ```
   **Resultado Esperado**: `HTTP 403 Forbidden` com código de erro amigável informando que novos cadastros estão suspensos pelo administrador.

---

## 7. Cenário 6: Vinculação e Desvinculação Manual em Ajustes (Prevenção de Lockout)

**Objetivo**: Permitir que o usuário gerencie seu vínculo Google no painel de Ajustes, impedindo que remova seu único método de acesso.

### Procedimento
1. **Vinculação**:
   - Usuário logado via senha local acessa **Ajustes > Segurança**.
   - Clica em "Vincular Conta Google" e conclui o fluxo GIS.
   - Frontend envia `POST /api/auth/google/link` com o token.
   - **Resultado Esperado**: `HTTP 200 OK`, card atualizado exibindo conta Google vinculada (`has_google: true`).
2. **Tentativa de Desvinculação sem Senha Cadastrada**:
   - Para um usuário cadastrado exclusivamente via Google (`has_password: false`):
   - Usuário tenta desvincular: `DELETE /api/auth/google/unlink`
   - **Resultado Esperado**: `HTTP 400 Bad Request` informando que o usuário precisa definir uma senha local antes de desvincular o Google, evitando lockout.
3. **Desvinculação Bem-Sucedida**:
   - Usuário possui senha local ativa (`has_password: true`).
   - Usuário clica em "Desvincular Google": `DELETE /api/auth/google/unlink`
   - **Resultado Esperado**: `HTTP 200 OK`, registro em `external_identities` removido, `has_google: false`.

---

## 8. Comandos de Validação Automatizada

### Testes do Backend (Pytest)
```powershell
python -m pytest backend/tests/test_google_auth.py -v
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
