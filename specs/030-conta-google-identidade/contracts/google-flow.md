# Sequence Diagrams & State Transitions: Google Auth

**Feature**: `030-conta-google-identidade`  
**Date**: 2026-09-22  
**Status**: Completed  

---

## 1. Fluxo de Autenticação e Primeiro Acesso (Sign In with Google)

```mermaid
sequenceDiagram
    autonumber
    actor Leitor as Leitor (Navegador)
    participant GIS as Google Identity Services
    participant API as Backend (FastAPI)
    participant DB as Banco SQLite (WAL)

    Leitor->>GIS: Clica em "Entrar com Google" (popup)
    GIS-->>Leitor: Retorna ID Token JWT (credential)
    Leitor->>API: POST /api/auth/google { credential }
    API->>API: Valida assinatura com chaves públicas do Google (JWKS)
    API->>API: Valida aud == GOOGLE_CLIENT_ID e exp
    API->>DB: Busca ExternalIdentity(provider='google', sub)

    alt Vínculo 'sub' já existe
        DB-->>API: Retorna ExternalIdentity e User
        API->>DB: Cria UserSession (janela deslizante de 30 dias)
        API-->>Leitor: 200 OK + Set-Cookie: caderno_session (HttpOnly)
    else Vínculo 'sub' não existe, mas e-mail verificado já existe
        API->>DB: Busca User pelo email e valida email_verified == true
        API->>DB: Cria ExternalIdentity(user_id=existing_user.id, sub)
        API->>DB: Cria UserSession
        API-->>Leitor: 200 OK + Set-Cookie: caderno_session (HttpOnly)
    else Conta inédita e ALLOW_REGISTRATION == true
        API->>DB: Cria novo User (username derivado, display_name, email)
        API->>DB: Cria ExternalIdentity(user_id=new_user.id, sub)
        API->>DB: Cria UserSession
        API-->>Leitor: 200 OK + Set-Cookie: caderno_session (HttpOnly)
    else Conta inédita e ALLOW_REGISTRATION == false
        API-->>Leitor: 403 Forbidden ("Auto-registro de novos usuários desativado")
    end
```

---

## 2. Fluxo de Vinculação nos Ajustes de Conta

```mermaid
sequenceDiagram
    autonumber
    actor Leitor as Leitor Autenticado
    participant GIS as Google Identity Services
    participant API as Backend (FastAPI)
    participant DB as Banco SQLite (WAL)

    Leitor->>Leitor: Acessa Ajustes > Conta & Dispositivos
    Leitor->>GIS: Clica em "Vincular Conta Google"
    GIS-->>Leitor: Retorna ID Token JWT (credential)
    Leitor->>API: POST /api/auth/google/link { credential } (com cookie de sessão)
    API->>API: Valida CurrentUser autenticado
    API->>API: Valida ID Token criptográfico
    API->>DB: Verifica se 'sub' já pertence a outro usuário

    alt Sub já pertence a outro usuário
        DB-->>API: Conflito encontrado
        API-->>Leitor: 409 Conflict ("Conta Google já vinculada a outro usuário")
    else Sub disponível
        API->>DB: Cria ExternalIdentity(user_id=current_user.id, sub, email)
        API-->>Leitor: 200 OK (ExternalIdentityRead)
    end
```

---

## 3. Fluxo de Desvinculação nos Ajustes e Prevenção de Lockout

```mermaid
sequenceDiagram
    autonumber
    actor Leitor as Leitor Autenticado
    participant API as Backend (FastAPI)
    participant DB as Banco SQLite (WAL)

    Leitor->>API: DELETE /api/auth/google/unlink (com cookie de sessão)
    API->>DB: Verifica se usuário possui senha cadastrada (LocalCredential)

    alt Usuário NÃO possui senha cadastrada
        DB-->>API: LocalCredential ausente
        API-->>Leitor: 400 Bad Request ("Defina uma senha local antes de desvincular o Google")
    else Usuário possui senha cadastrada
        DB-->>API: LocalCredential presente
        API->>DB: Remove ExternalIdentity correspondente
        API-->>Leitor: 200 OK { ok: true }
    end
```
