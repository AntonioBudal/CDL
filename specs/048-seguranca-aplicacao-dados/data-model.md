# Data Model & Security Contracts: F0.6.9 — Segurança de Aplicação e Dados

**Feature**: `048-seguranca-aplicacao-dados`  
**Date**: 2026-10-03  
**Status**: Completed  

---

## 1. Entities & Configuration Models

Como esta feature trata de segurança de aplicação, cabeçalhos HTTP e sanitização de dados, não há criação de novas tabelas relacionais no banco de dados SQLite. As entidades representam configurações de segurança, modelos de erro e estruturas de validação de dados em memória.

### SecurityPolicyConfiguration

Representa os parâmetros de segurança aplicados pelo middleware HTTP do FastAPI:

| Atributo | Tipo | Descrição | Valor Padrão |
|:---|:---|:---|:---|
| `cors_allowed_origins` | `list[str]` | Origens permitidas para requisições CORS com credenciais | `["http://localhost:5173", "http://127.0.0.1:5173"]` |
| `csp_directives` | `dict[str, str]` | Mapa de diretivas de Content-Security-Policy em modo Enforce | Diretivas calibradas para Vue, Google Fonts e Google Identity |
| `frame_options` | `str` | Política de framing HTTP | `"SAMEORIGIN"` |
| `content_type_options` | `str` | Prevenção de MIME-sniffing | `"nosniff"` |
| `referrer_policy` | `str` | Política de vazamento de referenciador | `"strict-origin-when-cross-origin"` |
| `permissions_policy` | `str` | Restrição de recursos do navegador | `"camera=(), microphone=(), geolocation=()"` |

---

### SecurityErrorResponse (Schema Pydantic)

Contrato padronizado retornado nas respostas de falha interna HTTP 500:

| Campo | Tipo | Obrigatório | Descrição |
|:---|:---|:---|:---|
| `detail` | `str` | Sim | Mensagem genérica amigável: `"Ocorreu um erro interno no servidor."` |
| `error_id` | `str` | Sim | Identificador UUID gerado aleatoriamente para correlação nos logs do servidor |

Exemplo de payload JSON:
```json
{
  "detail": "Ocorreu um erro interno no servidor.",
  "error_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d"
}
```

---

### SanitizedMarkdownContent (Frontend Contract)

Estrutura resultante do pipeline de parsing e sanitização no frontend:

| Componente | Regra de Sanitização |
|:---|:---|
| **Links (`<a>`)** | Protocolos aceitos exclusivamente: `http:`, `https:`, `mailto:`, ou caminhos relativos/âncoras (`/`, `#`). Qualquer protocolo `javascript:`, `vbscript:`, `data:` ou caracteres de escape é neutralizado. Atributos obrigatórios injetados: `target="_blank"` e `rel="noopener noreferrer"`. |
| **Tags HTML** | Tags executáveis (`<script>`, `<object>`, `<embed>`, `<iframe>`, `<applet>`, `<form>`) são eliminadas. Atributos manipuladores de eventos (`onload`, `onerror`, `onclick`, `onmouseover`, etc.) são removidos. |
| **Elementos de Leitura Ativa** | Elementos `<mark>`, spans e classes `.study-occlusion`, `.study-highlight`, `.hl-*`, `.study-note`, `.study-question-*` são preservados intactos. |

---

## 2. Validação e Ciclo de Vida de Configurações

```text
Inicialização do Servidor (lifespan)
        │
        ├──> Audita CADERNO_SESSION_SECRET
        │      └── Se for chave fraca/default em produção: emite alerta explícito no log
        │
        ├──> Carrega CADERNO_CORS_ORIGINS
        │      └── Normaliza origens em lista rigorosa (sem wildcard '*')
        │
        └──> Registra Middlewares de Segurança
               ├── CORSMiddleware restritivo
               ├── SecurityHeadersMiddleware (CSP, nosniff, Referrer, Permissions, Frame)
               └── GlobalExceptionHandler (500 com error_id)
```
