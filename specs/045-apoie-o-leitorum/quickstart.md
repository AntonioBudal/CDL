# Quickstart & Validation Guide: F0.6.6 — Apoie o Leitorum

**Feature Branch**: `045-apoie-o-leitorum`  
**Date**: 2026-09-29  
**Status**: Ready  

Este guia descreve os cenários de validação automatizados e manuais para assegurar que a funcionalidade "Apoie o Leitorum" cumpra todos os requisitos especificados.

---

## 1. Pré-Requisitos de Validação

- Ambiente Python com dependências do backend instaladas (`pytest`).
- Ambiente Node.js com dependências do frontend instaladas (`npm test`).
- Banco de dados SQLite efêmero em diretório temporário (`tmp_path`) — **nunca tocar em `backend/data/caderno.db`**.

---

## 2. Cenários de Validação Automatizada (Backend)

Execute os testes com:
```powershell
& 'C:\Python314\python.exe' -m pytest tests/test_support_settings.py -v
```

### Cenário 1: Consulta Pública com Fallback Default e de Ambiente
1. **Ação**: Fazer requisição anônima `GET /api/support` em banco recém-criado sem registros na tabela `support_settings`.
2. **Resultado Esperado**: Retorno `200 OK` com `pix_enabled=False`, `alternative_enabled=False`, `has_any_method_active=False`.
3. **Ação Complementar**: Definir variável de ambiente `SUPPORT_PIX_KEY="pix@teste.com"` via monkeypatch e consultar novamente.
4. **Resultado Esperado**: Retorno `200 OK` refletindo a chave configurada no ambiente.

### Cenário 2: Gestão Administrativa e Mutação de Parâmetros
1. **Ação**: Autenticar como administrador e enviar `PUT /api/admin/support` com dados de PIX e Google Pay.
2. **Resultado Esperado**: Retorno `200 OK` com os dados salvos no banco e `source="database"`.
3. **Validação de Auditoria**: Verificar que uma entrada correspondente foi gerada na tabela `audit_logs`.

### Cenário 3: Controle de Acesso e Proteção Anti-IDOR
1. **Ação**: Tentar acessar `PUT /api/admin/support` sem autenticação.
2. **Resultado Esperado**: Retorno `401 Unauthorized`.
3. **Ação**: Tentar acessar `PUT /api/admin/support` autenticado como usuário comum (`role="user"`).
4. **Resultado Esperado**: Retorno `403 Forbidden`.

---

## 3. Cenários de Validação Automatizada (Frontend)

Execute os testes com:
```powershell
cd caderno-leitura-0.1/frontend
npm test
```

### Cenário 4: Renderização de `SupportView.vue` e Ação de Cópia
1. **Ação**: Montar `SupportView.vue` com dados simulados de PIX.
2. **Resultado Esperado**:
   - Exibição de chave PIX, titular e QR Code.
   - Clique no botão "Copiar Chave PIX" dispara chamada à API de clipboard e altera o texto do botão para "Copiada" temporariamente.
   - Alvos de clique possuem altura mínima de 44px.

### Cenário 5: Verificação de Ausência Total de Emojis
1. **Ação**: Executar o scanner automatizado de integridade de código em `frontend/src`.
2. **Resultado Esperado**: 0 emojis residuais em arquivos `.vue`, `.ts`, `.js` ou `.css`.

### Cenário 6: Navegação Discreta pelo Rodapé
1. **Ação**: Verificar a renderização de `App.vue` e `MobileMoreMenu.vue`.
2. **Resultado Esperado**:
   - O link "Apoie o Leitorum" está presente no rodapé `<footer class="app-footer">` e aponta para `/apoie`.
   - Nenhuma aba "Doações" ou "Apoie" existe na navegação principal de topo.
