# Contract: Contexto de Usuário e Autenticação (F01)

**Protocol**: HTTP / REST  
**Base Path**: `/api`  

---

## 1. Resolução do Contexto do Usuário (`CurrentUser`)

### Injeção de Dependência Server-Side
```python
CurrentUser = Annotated[User, Depends(get_current_user)]
```

### Mecanismo de Resolução
1. O servidor inspeciona o cabeçalho HTTP:
   - `X-User-Id: <UUID>`
2. **Cenário 1: Cabeçalho Ausente**
   - Resolução automática para o proprietário canônico:
     - `id`: `'00000000-0000-0000-0000-000000000001'`
     - `username`: `'proprietario'`
     - `display_name`: `'Proprietário do Caderno'`
3. **Cenário 2: Cabeçalho Presente e Válido**
   - Busca o registro correspondente em `users`.
   - Se encontrado e ativo, define o usuário como contexto de execução.
4. **Cenário 3: Cabeçalho Presente mas Inválido ou Inexistente**
   - Retorna imediatamente:
   ```json
   HTTP/1.1 401 Unauthorized
   Content-Type: application/json

   {
     "detail": "Usuário não autenticado ou inexistente."
   }
   ```

---

## 2. Endpoint de Identidade Atual

### `GET /api/auth/me`

Retorna os metadados do usuário autenticado na sessão atual.

#### Response 200 OK
```json
{
  "id": "00000000-0000-0000-0000-000000000001",
  "username": "proprietario",
  "display_name": "Proprietário do Caderno",
  "status": "ativo",
  "created_at": "2026-09-20T12:00:00Z"
}
```

#### Response 401 Unauthorized
```json
{
  "detail": "Usuário não autenticado ou inexistente."
}
```
