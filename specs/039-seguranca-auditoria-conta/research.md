# Research: F10 — Segurança, Auditoria, Ciclo de Vida da Conta e Google OAuth

**Feature**: [spec.md](spec.md)  
**Date**: 2026-09-26  
**Status**: Completed  

## 1. Rate Limiting e Prevenção de Ataques de Força Bruta

### Decisão
Implementar um mecanismo híbrido de controle de taxa em duas camadas:
1. **Camada em memória (FastAPI Middleware/Dependency)**: Estrutura de janela deslizante (*sliding window*) baseada em tempo (usando `collections.deque` de timestamps por chave IP/endpoint). Limita a 5 tentativas em 5 minutos para rotas `/api/auth/login`, `/api/auth/register`, `/api/auth/google`. Quando excedido, responde imediatamente com `HTTP 429 Too Many Requests`, cabeçalho `Retry-After: <segundos>` e payload JSON explicativo.
2. **Camada de conta (Lockout em banco de dados)**: Campos `failed_login_attempts` e `locked_until` na tabela `users`. Após 5 falhas consecutivas de credenciais para uma mesma conta, a conta é temporariamente travada por 15 minutos, mitigando ataques de dicionário distribuídos entre múltiplos IPs.

### Raciocínio
- A arquitetura do Caderno de Leitura roda em processo único local através de `iniciar.py`. O controle em memória é extremamente rápido (< 1ms de latência), sem overhead de I/O em disco no SQLite e sem dependência de daemons externos (como Redis ou Memcached).
- A proteção ao nível de conta impede que um atacante contorne o rate limiting por IP rotacionando endereços na rede local ou Tailscale.

### Alternativas Consideradas
- **Redis / Memcached**: Rejeitado pois violaria o Princípio III da Constituição do Projeto (aplicação autônoma local sem dependências de servidores de terceiros).
- **Tabela de requisições no SQLite**: Rejeitado para evitar contenção de escrita de disco e bloqueios desnecessários no banco WAL.

---

## 2. Autenticação e Integração com Google OAuth 2.0

### Decisão
Suportar dois fluxos integrados de autenticação com o Google:
1. **Fluxo Google Identity Services (GIS - ID Token)**: Já suportado via `POST /api/auth/google`, validando criptograficamente o ID Token JWT contra as chaves públicas (JWKS) do Google (`https://www.googleapis.com/oauth2/v3/certs`) via `google-auth` já instalado.
2. **Fluxo OAuth 2.0 Web Redirect**: Rotas `GET /api/auth/google/login` (que redireciona para `https://accounts.google.com/o/oauth2/v2/auth` com `client_id`, `redirect_uri`, `scope=openid email profile` e `state` anti-CSRF) e `GET /api/auth/google/callback` (que troca o `code` pelo token no endpoint `https://oauth2.googleapis.com/token` e inicia a sessão).
3. **Provisionamento e Vínculo Inteligente**:
   - Se `ExternalIdentity(provider='google', provider_user_id=sub)` existir: loga o usuário imediatamente.
   - Se não existir, mas existir um `User` ativo com o mesmo e-mail verificado retornado pelo Google: auto-vincula a identidade Google à conta existente.
   - Se o usuário não existir: cria automaticamente um novo `User` ativo com `username` sugerido derivado do e-mail/nome, perfil inicial, sem necessidade de senha local, e estabelece a sessão em cookie seguro.

### Raciocínio
- Atende com perfeição à exigência de praticidade ("Logar com o Google com um clique sem precisar criar senha").
- Aproveita integralmente as estruturas já criadas em `ExternalIdentity`, `google_auth_service.py` e `auth_service.py`.

### Alternativas Consideradas
- **Apenas GIS**: Embora moderno, pode ser bloqueado por extensões de privacidade estritas em iframes; a presença da rota de redirecionamento assegura robustez em qualquer navegador ou ambiente móvel.
- **Serviços de Auth de terceiros (Supabase, Auth0)**: Rejeitado por adicionar complexidade e violar a soberania de dados local.

---

## 3. Trilha de Auditoria Estruturada (`AuditLog`) e Sanitização de Segredos

### Decisão
Criar tabela dedicada `audit_logs` no SQLite gerenciada por `audit_service.py`.
- **Campos**: `id` (UUID), `created_at` (UTC), `event_type` (Enum textual), `user_id` (UUID opcional), `actor_username` (String opcional), `ip_address` (String), `user_agent` (String), `details` (JSON).
- **Sanitização Proativa**: O serviço possui lista de bloqueio de chaves (`password`, `password_hash`, `token`, `credential`, `secret`, `jwt`, `code`, `access_token`). Qualquer objeto passado em `details` tem essas chaves recursivamente descartadas ou substituídas por `[REDACTED]`.
- **Acesso Administrativo**: Endpoint `GET /api/admin/audit-logs` restrito ao papel `ADMIN`, com paginação (`limit`/`offset`) e ordenação cronológica decrescente.

### Raciocínio
- Atende ao requisito do OWASP de rastreabilidade de eventos sensíveis sem jamais registrar segredos que possam comprometer a segurança caso o banco seja inspecionado.

### Alternativas Consideradas
- **Log em arquivo texto (`logs/audit.log`)**: Rejeitado por dificultar buscas, paginação, filtros e auditoria pela UI administrativa.

---

## 4. Ciclo de Vida: Desativação Temporária e Reativação Explícita

### Decisão
- **Desativação**: `POST /api/account/deactivate` exige confirmação de credenciais (senha local ou reautenticação Google). Define `status = 'deactivated'`, grava `deactivated_at = now()` e revoga imediatamente todas as sessões ativas do usuário em `user_sessions`.
- **Reativação Explícita (Opção B)**: Quando um usuário desativado submete login correto (local ou Google), a API retorna `HTTP 403 Forbidden` com payload estruturado `{"code": "ACCOUNT_DEACTIVATED", "message": "Sua conta está desativada."}`. A interface exibe diálogo modal: *"Sua conta está desativada. Deseja reativá-la agora?"*. Ao confirmar via `POST /api/account/reactivate`, o status volta para `'active'`, o acervo volta a ser visível e a sessão é restabelecida.

### Raciocínio
- Previne reativação acidental e dá clareza total ao usuário sobre o estado de sua conta.

### Alternativas Consideradas
- **Reativação automática silenciosa (Opção A)**: Rejeitada pelo usuário na etapa de esclarecimento.

---

## 5. Exclusão Definitiva em Cascata Física Transacional (LGPD)

### Decisão
Endpoint `DELETE /api/account` requer confirmação de senha local (ou confirmação de usuário para contas Google-only).
Executa em transação atômica:
1. Registra evento em `AuditLog(event_type='account_deleted', actor_username=username, user_id=None)`.
2. Remove em cascata rigorosa todas as entidades filhas vinculadas ao `user_id`:
   - `UserSession`, `LocalCredential`, `ExternalIdentity`
   - `Notification`, `Friendship` (solicitante ou receptor)
   - `StudyShare`, `StudyRelation`, `CanvasPosition`
   - `Study`, `Chapter`, `Book`, `Category`
   - `UserProfile`, `UserPreference`
3. Remove fisicamente o registro do `User`.
4. Exclui capas associadas em disco (`uploads/covers/`).
5. Limpa os cookies de sessão.

### Raciocínio
- Cumpre o Direito ao Esquecimento da LGPD (Art. 18, VI) com eliminação total dos dados pessoais, garantindo que o banco permaneça íntegro sem registros órfãos.

### Alternativas Consideradas
- **Anonimização com manutenção de estudos**: Rejeitada pelo usuário na etapa de esclarecimento.

---

## 6. Exportação Completa de Dados (Portabilidade LGPD)

### Decisão
Endpoint `GET /api/account/export` gera sob demanda um arquivo ZIP contendo:
```
caderno-export-[username]-[data]/
├── dados_acervo.json                # JSON estruturado completo de livros, capítulos, estudos, categorias, relações e preferências
└── livros/
    └── [Nome do Livro]/
        └── [Nome do Capítulo]/
            └── [Nome do Estudo].md   # Markdown legível com Frontmatter YAML (título, status, data, tags)
```
- Gerado em streaming via `zipfile.ZipFile` em memória com `io.BytesIO` (ou arquivo temporário se acervo > 50MB) para entrega instantânea via `StreamingResponse(media_type="application/zip")`.

### Raciocínio
- Alinhado com a Opção A escolhida pelo usuário. Une legibilidade humana imediata (Markdown) com fidelidade estruturada (JSON).
