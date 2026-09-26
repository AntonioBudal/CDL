# Quickstart & Validation Guide: F06 — Sistema de Amizades

Este guia descreve os cenários executáveis e testes automatizados de validação de ponta a ponta para homologar a Feature 06 em ambiente hermético e seguro.

---

## Pré-requisitos e Isolamento
- Ambiente virtual Python 3.13 ativado (`backend/.venv`).
- Todos os testes utilizam bancos SQLite temporários em `tmp_path` com variáveis de ambiente isoladas (`REQUIRE_AUTH=true`).
- **Nenhum teste toca no banco ativo `backend/data/caderno.db`**.

---

## Cenário 1: Ciclo Completo de Solicitação e Aceite (P1)
**Objetivo**: Validar que dois usuários conseguem solicitar e aceitar amizade, passando a constar mutuamente como amigos.

1. **Setup**: Criar `UserA` ("alice") e `UserB` ("bob") em banco efêmero.
2. **Ação 1**: `POST /api/friends/request/bob` autenticado como `alice`.
   - **Resultado esperado**: `200 OK`, `status == 'pending'`.
3. **Ação 2**: `GET /api/friends/requests` autenticado como `bob`.
   - **Resultado esperado**: 1 item em `received` com `user.username == 'alice'`.
4. **Ação 3**: `POST /api/friends/accept/{request_id}` autenticado como `bob`.
   - **Resultado esperado**: `200 OK`, `status == 'accepted'`.
5. **Verificação**: `GET /api/friends` chamado por `alice` e por `bob`.
   - **Resultado esperado**: Ambos visualizam o parceiro na lista de amigos com data `since`.

---

## Cenário 2: Recusa de Solicitação e Retorno ao Estado Neutro (P1 & Q1: A)
**Objetivo**: Validar que a recusa encerra a pendência e permite nova solicitação posterior.

1. **Setup**: `UserA` ("alice") solicita amizade a `UserC` ("carlos").
2. **Ação**: `POST /api/friends/reject/{request_id}` autenticado como `carlos`.
   - **Resultado esperado**: `200 OK`, `status == 'none'`.
3. **Verificação 1**: `GET /api/friends/requests` para ambos retorna listas vazias.
4. **Verificação 2**: `POST /api/friends/request/carlos` enviado novamente por `alice`.
   - **Resultado esperado**: `200 OK`, nova solicitação aceita e registrada sem erro de duplicidade.

---

## Cenário 3: Cancelamento de Solicitação e Desfazimento de Amizade (P2)
**Objetivo**: Validar autonomia de revogação de solicitações e término de vínculos mútuos.

1. **Setup**: `UserA` solicita a `UserB`.
2. **Ação 1**: `DELETE /api/friends/cancel/{request_id}` autenticado como `UserA`.
   - **Resultado esperado**: `200 OK`, solicitação apagada.
3. **Setup 2**: `UserA` e `UserB` tornam-se amigos.
4. **Ação 2**: `DELETE /api/friends/bob` autenticado como `UserA`.
   - **Resultado esperado**: `200 OK`, vínculo de amizade dissolvido para ambos.
5. **Verificação**: `GET /api/friends` para ambos retorna lista vazia.

---

## Cenário 4: Bloqueio Bilateral e Blindagem Anti-Enumeração (P3)
**Objetivo**: Validar que o bloqueio isola completamente as partes em buscas e perfis diretos.

1. **Setup**: `UserA` bloqueia `UserD` ("daniel") via `POST /api/friends/block/daniel`.
   - **Resultado esperado**: `200 OK`, `status == 'blocked'`.
2. **Ação 1**: `UserD` busca por `UserA` via `GET /api/users?q=alice`.
   - **Resultado esperado**: `UserA` não consta nos resultados.
3. **Ação 2**: `UserD` tenta acessar o perfil público de `UserA` via `GET /api/users/alice`.
   - **Resultado esperado**: `HTTP 404 Not Found` (como se a conta não existisse).
4. **Ação 3**: `UserD` tenta enviar solicitação para `UserA`.
   - **Resultado esperado**: `HTTP 404 Not Found`.
5. **Ação 4**: `UserA` desbloqueia `UserD` via `POST /api/friends/unblock/daniel`.
   - **Resultado esperado**: `200 OK`. `UserD` volta a ser capaz de visualizar o perfil público de `UserA`.

---

## Cenário 5: Hub Social `/amigos` e Resumo de Pendências (P4 & Q2: A)
**Objetivo**: Validar contadores consolidados para badges e listagens por abas.

1. **Ação**: `GET /api/friends/summary` autenticado.
   - **Resultado esperado**: Objeto com `friends_count`, `pending_received_count` e `pending_sent_count`.
2. **Interface**: Navegação para a rota `/amigos` exibe o cabeçalho com abas ("Amigos", "Solicitações", "Bloqueados", "Descobrir") e crachá numérico em tempo real.

---

## Comandos de Validação Automatizada

```powershell
# Execução da suíte dedicada da Feature 06
pytest backend/tests/test_friendships.py -v

# Execução da suíte de regressão completa do backend
pytest backend/tests

# Validação do frontend e contratos visuais
npm test --prefix frontend
npm run build --prefix frontend
```
