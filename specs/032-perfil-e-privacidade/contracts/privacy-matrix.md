# Regras de Autorização e Matriz de Privacidade

**Feature**: `032-perfil-e-privacidade`  
**Date**: 2026-09-24

Este documento detalha o comportamento do sistema diante das configurações de visibilidade do leitor e os dados retornados para cada categoria de requisitante.

---

## 1. Classificação dos Solicitantes

1. **Proprietário (`Owner`)**: O próprio leitor autenticado acessando seus dados (`current_user.id == target_user.id`).
2. **Amigo (`Friend`)**: Usuário autenticado com relacionamento de amizade no status `ACCEPTED` com o leitor. *(Nota: até a entrega de F06, nenhum usuário externo possui status de amigo, sendo tratado como Visitante Autenticado)*.
3. **Visitante Autenticado (`Visitor`)**: Qualquer outro usuário ativo no sistema que navega pelo perfil ou busca pelo leitor.
4. **Anônimo (`Anonymous`)**: Requisições sem sessão válida (são interceptadas com `HTTP 401 Unauthorized` por estarem sob middleware de autenticação).

---

## 2. Matriz de Exposição de Campos de Perfil

| Campo | Proprietário (`Owner`) | Visitante (`profile_visibility = public`) | Visitante (`profile_visibility = friends` ou `private`) |
|:---|:---:|:---:|:---:|
| `username` | Exibido | Exibido | Exibido |
| `display_name` | Exibido | Exibido | Exibido |
| `avatar_url` | Exibido | Exibido | Exibido |
| `bio` | Exibido | Exibido | **Oculto (`None`)** |
| `email` | **Exibido (somente em `/api/profile/me`)** | **NUNCA (`None`)** | **NUNCA (`None`)** |
| `reading_stats` | Exibido | Exibido se `show_reading_stats=True` | **Oculto (`None`)** |
| `is_private` | `False` | `False` | **`True`** |
| Selo de Restrição | Não exibe | Não exibe | **"Este perfil é privado"** |

---

## 3. Matriz de Exposição de Dashboard e Estudos

| Visibilidade do Dashboard | Acesso do Proprietário | Acesso de Amigos (F06) | Acesso de Visitantes |
|:---|:---:|:---:|:---:|
| `public` | Acesso Total | Acesso Total | Acesso Total aos estudos públicos |
| `friends` | Acesso Total | Acesso Total | Bloqueado (`HTTP 403` / Cartão restrito) |
| `private` | Acesso Total | Bloqueado | Bloqueado (`HTTP 403` / Cartão restrito) |

> **Princípio de Desacoplamento**: Um usuário com `profile_visibility: "public"` e `dashboard_visibility: "private"` permite que seu nome, avatar e bio sejam vistos por todos, mas ninguém além dele mesmo consegue ver o resumo de leitura, estudos ou livros no dashboard.

---

## 4. Regras de Busca (`GET /api/users?q=...`)

Um perfil de leitor só deve ser listado nos resultados de busca pública se:
1. `is_discoverable == True` **E**
2. `profile_visibility != 'private'` **E**
3. O status do usuário for `'ativo'`.

Se `is_discoverable == False`, o usuário não é retornado na busca geral, mas ainda pode ser acessado diretamente via link ou menção se `profile_visibility == 'public'`.
