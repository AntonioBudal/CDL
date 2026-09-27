# Quickstart Guide: F09 — Notificações e Atividade Social

**Feature Branch**: `036-notificacoes-atividade-social`  
**Created**: 2026-09-26  
**Status**: Completed  

Este guia detalha os procedimentos para validação ponta a ponta dos recursos da feature **F09 (Notificações e Atividade Social)** no ambiente de desenvolvimento local do Leitorum, cobrindo testes automatizados de backend, frontend e verificação manual dos cenários principais.

---

## 1. Pré-Requisitos e Configuração do Ambiente

1. **Python 3.13 (64-bit)** com ambiente virtual ativo em `caderno-leitura-0.1/backend/.venv`.
2. **Node.js 20+** com dependências instaladas em `caderno-leitura-0.1/frontend/node_modules`.
3. **Isolamento Absoluto:** Todo comando de validação automatizada DEVE utilizar bancos SQLite temporários (`tmp_path`), garantindo que o banco de produção (`backend/data/caderno.db`) permaneça intocado (Artigo II da Constituição).

---

## 2. Cenários de Validação Automatizada (Backend)

Os testes de integração do backend cobrem o ciclo de vida completo: emissão de eventos sociais, contagem rápida, leitura individual, leitura em lote, ações rápidas de amizade, comunicados em massa administrativos e purga de registros expirados.

### 2.1. Execução da Suíte Pytest

No PowerShell, a partir da raiz do repositório:

```powershell
Set-Location c:\Users\User\caderno\caderno-leitura-0.1
$env:PYTHONPATH = "backend"
.\backend\.venv\Scripts\python.exe -m pytest backend/tests/test_notifications.py -v
```

### 2.2. Cenários Cobertos pelos Testes de Backend

1. **Contador Inicial Vazio:**
   - Usuário recém-criado consulta `GET /api/notifications/unread-count` e obtém `{"unread_count": 0}`.
2. **Emissão de Solicitação de Amizade (`friend_request`):**
   - Usuário A envia solicitação de amizade para Usuário B (`POST /api/friends/requests`).
   - Usuário B consulta `GET /api/notifications/unread-count` e obtém `{"unread_count": 1}`.
   - O item retornado em `GET /api/notifications` possui `event_type == 'friend_request'` com dados do remetente no payload.
3. **Aceite com Notificação Reversa (`friend_accepted`):**
   - Usuário B aceita a solicitação.
   - Usuário A passa a ter 1 notificação não lida com `event_type == 'friend_accepted'`.
4. **Compartilhamento de Recurso (`study_shared`):**
   - Usuário A concede permissão de leitura sobre um estudo para o Usuário B (`POST /api/sharing/permissions`).
   - Usuário B recebe notificação `study_shared` com o título da obra e link direto para o estudo.
5. **Marcação de Leitura Individual e em Lote:**
   - `PATCH /api/notifications/{id}/read` marca a notificação como lida (`read_at IS NOT NULL`) e decrementa o contador.
   - `POST /api/notifications/read-all` zera imediatamente qualquer contagem pendente.
6. **Aviso Administrativo em Massa (`system_alert`):**
   - Usuário com papel de administrador envia comunicado institucional via `POST /api/admin/notifications/broadcast`.
   - Todos os usuários ativos recebem uma notificação `system_alert`.
   - Usuários com papel comum recebem erro HTTP 403 Forbidden ao tentar invocar a rota.
7. **Purga Automática de Notificações Expiradas:**
   - Notificações lidas com mais de 60 dias são removidas com sucesso via `POST /api/admin/notifications/purge`.
   - Notificações não lidas permanecem estritamente preservadas no banco.

---

## 3. Cenários de Validação Automatizada (Frontend)

Os testes de frontend verificam a renderização do ícone no cabeçalho com badge, a abertura do dropdown, a exibição dos cards por tipo de evento e a transição inline das ações rápidas de amizade.

### 3.1. Execução da Suíte Vitest

No PowerShell:

```powershell
Set-Location c:\Users\User\caderno\caderno-leitura-0.1\frontend
npm test -- src/__tests__/NotificationsDropdown.spec.ts src/__tests__/useNotifications.spec.ts
```

### 3.2. Verificações de UI e Acessibilidade

- **Badge Numérico:** Quando `unread_count > 0`, o elemento exibe o número e atributo `aria-label="X notificações não lidas"`. Quando `unread_count === 0`, o badge não é exibido.
- **Ações Rápidas Inline:** Ao clicar em "Aceitar" na notificação de amizade, os botões são substituídos imediatamente por mensagem de confirmação ("✓ Amizade aceita"), sem remover abruptamente o item da lista visual.
- **Navegação por Teclado:** O botão do sino abre e fecha o menu via teclado (`Enter` ou `Space`), e `Escape` fecha o painel retornando o foco ao botão de disparo.

---

## 4. Validação Manual Ponta a Ponta no Navegador

1. **Iniciar a Aplicação Local:**
   ```powershell
   Set-Location c:\Users\User\caderno\caderno-leitura-0.1
   .\backend\.venv\Scripts\python.exe iniciar.py
   ```
2. **Fluxo Social entre Dois Leitores:**
   - Em uma aba comum, autentique-se como Usuário 1 (ex.: `leitor_a`).
   - Em uma janela anônima, autentique-se como Usuário 2 (ex.: `leitor_b`).
   - Na janela anônima, envie uma solicitação de amizade para `@leitor_a`.
   - Volte para a aba de `leitor_a`: ao focar a aba ou no intervalo do polling, o ícone de sino no cabeçalho exibe o badge numérico `1`.
   - Clique no sino: o menu suspenso abre instantaneamente exibindo a solicitação com foto/iniciais e botões "Aceitar" e "Recusar".
   - Clique em "Aceitar": o card exibe confirmação inline imediata ("✓ Amizade aceita") e o badge é zerado.
   - Retorne à janela anônima de `leitor_b`: ao focar a aba, o sino exibe `1`, e ao abrir vê-se a notificação "leitor_a aceitou sua solicitação de amizade".
