# Research & Architectural Decisions: F0.6.9 — Segurança de Aplicação e Dados

**Feature**: `048-seguranca-aplicacao-dados`  
**Date**: 2026-10-03  
**Status**: Completed  

---

## Technical Decisions

### D1: Sanitização contra XSS e Validação Estrita de URLs Markdown

- **Decision**: Implementar sanitização em duas camadas complementares:
  1. **Camada 1 (Parser Markdown-it)**: Configurar regra estrita de `validateLink` no parser `frontend/src/services/markdown.ts`, permitindo exclusivamente protocolos seguros (`http:`, `https:`, `mailto:`) e caminhos relativos/âncoras locais (`/`, `#`), rejeitando categoricamente esquemas como `javascript:`, `vbscript:`, `data:` e URLs malformadas.
  2. **Camada 2 (Sanitização do HTML de Saída)**: Incorporar sanitização do HTML gerado antes da injeção via `v-html` em `MarkdownContent.vue`, garantindo que nenhuma tag executável (`<script>`, `<object>`, `<embed>`, `<iframe>`) ou atributos manipuladores de eventos (`onload`, `onerror`, `onclick`, `onmouseover`) passem para o DOM, preservando 100% dos elementos e classes semânticas legítimas de leitura ativa (`<mark>`, `.study-occlusion`, `.study-highlight`, etc.).
- **Rationale**: Defesa em profundidade (*Defense-in-Depth*). Mesmo que uma entrada ultrapasse as regras do parser ou venha de importação maliciosa, a camada de sanitização do DOM impede a execução do script.
- **Alternatives Considered**:
  - *Apenas escapar todo o texto sem permitir Markdown*: Inviabilizaria a experiência de estudo, que exige negrito, itálico, listas, tabelas e leitura ativa.
  - *Regex artesanal no backend*: Frágil contra mutações de HTML e vetores de evasão conhecidos.

---

### D2: Cabeçalhos HTTP de Segurança e Content-Security-Policy (CSP) em Modo Enforce

- **Decision**: Injetar cabeçalhos de segurança padronizados em 100% das respostas HTTP do Leitorum através de um middleware dedicado em `backend/app/main.py`:
  - `Content-Security-Policy`:
    - `default-src 'self';`
    - `script-src 'self' 'unsafe-inline' https://accounts.google.com;`
    - `style-src 'self' 'unsafe-inline' https://fonts.googleapis.com;`
    - `font-src 'self' https://fonts.gstatic.com data:;`
    - `img-src 'self' data: https: blob:;`
    - `connect-src 'self' https://accounts.google.com;`
    - `frame-src 'self' https://accounts.google.com;`
    - `frame-ancestors 'self';`
    - `base-uri 'self';`
    - `form-action 'self';`
  - `X-Content-Type-Options: nosniff`
  - `Referrer-Policy: strict-origin-when-cross-origin`
  - `Permissions-Policy: camera=(), microphone=(), geolocation=()`
  - `X-Frame-Options: SAMEORIGIN`
- **Rationale**: O alinhamento direto em modo *Enforce* foi deliberado pelo usuário (Q1: A). As diretivas acomodam os requisitos estritos do Vue 3, fontes tipográficas locais/Google, os temas com injeção de CSS e a autenticação com Google Identity Services (`accounts.google.com`), bloqueando clickjacking e origens desconhecidas.
- **Alternatives Considered**:
  - *CSP Report-Only*: Deferiria a proteção real; rejeitado na clarificação.
  - *CSP excessivamente restrito sem `unsafe-inline` para estilos*: Quebraria a estilização dinâmica de temas e tokens da aplicação.

---

### D3: Política CORS Controlada e Segura

- **Decision**: Registrar middleware CORS explícito e restritivo em `backend/app/main.py`. Em produção (comportamento padrão), a aplicação opera em *same-origin*. Para ambientes de desenvolvimento ou redes autorizadas, o servidor aceita origens configuradas via variável de ambiente `CADERNO_CORS_ORIGINS` (lista de origens separadas por vírgula) ou fallback seguro para servidores locais de desenvolvimento (`localhost:5173`, `127.0.0.1:5173`). Nunca utilizar `allow_origins=["*"]` com `allow_credentials=True`.
- **Rationale**: Garante conformidade com as diretivas de segurança modernas e protege cookies de sessão com `SameSite=Lax/Strict`.
- **Alternatives Considered**:
  - *CORS wildcard `*`*: Proibido pelos navegadores com credenciais e severamente vulnerável a CSRF e extração de dados.

---

### D4: Tratamento de Erros 500 com Correlação por `error_id`

- **Decision**: Registrar manipulador global de exceções para `Exception` em `backend/app/errors.py`. Em qualquer erro não tratado:
  - Gera um identificador único anônimo `error_id = str(uuid.uuid4())`.
  - Registra a exceção e traceback completos no logger interno do servidor associados a esse `error_id`.
  - Retorna resposta JSON uniforme: `HTTP 500 {"detail": "Ocorreu um erro interno no servidor.", "error_id": error_id}`.
- **Rationale**: Alinhado com a decisão do usuário (Q2: A). Elimina qualquer vazamento de stack traces, nomes de arquivos locais do Windows ou detalhes de queries SQL para o cliente, fornecendo uma chave de rastreamento para o administrador localizar a causa nos logs locais.
- **Alternatives Considered**:
  - *Mensagem 500 sem identificador*: Dificulta diagnóstico e correlação nos logs do servidor.
  - *Traceback exposto em desenvolvimento*: Risco de vazamento acidental se configurado incorretamente em produção.

---

### D5: Auditoria de Queries SQL e Garantia de Parametrização

- **Decision**: A auditoria do código confirmou que todas as rotas e modelos utilizam SQLAlchemy ORM moderno (SQLAlchemy 2.0) com mapeamento tipado, filtros parametrizados e métodos de agregação. A única query que utiliza `text()` em `category_service.py` utiliza bind parameters com `:cat_id`.
  - Para consolidar essa garantia, criar suíte de testes de integração específica submetendo payloads maliciosos de injeção SQL (`' OR '1'='1`, `'; DROP TABLE...`, `UNION SELECT`) em parâmetros de busca, paginação, filtros e IDs, verificando que todos são tratados como valores literais.
- **Rationale**: Validação empírica contínua contra regressões de segurança na camada de dados.
- **Alternatives Considered**:
  - *Apenas inspeção visual de código*: Não oferece cobertura contínua nem barreira automatizada contra futuras alterações.

---

### D6: Blindagem contra Exposição de Arquivos Sensíveis e Segredos de Sessão

- **Decision**:
  1. **Arquivos Sensíveis**: No serviço de arquivos estáticos (`app/frontend.py`), validar que requisições a caminhos que comecem com `.` (ex.: `.env`, `.git`), arquivos com extensões de banco (`.db`, `.sqlite`, `.sqlite3`) ou código (`.py`) retornem imediatamente `404 Not Found`, impedindo qualquer travessia de diretório.
  2. **Validação de Segredos**: Na inicialização da aplicação (`lifespan`), verificar o valor de `CADERNO_SESSION_SECRET`. Se estiver configurado com o valor padrão de desenvolvimento e a aplicação não estiver explicitamente em modo de desenvolvimento local, emitir alerta visível nos logs orientando a configuração de uma chave segura.
- **Rationale**: Preservação inviolável do Princípio I da Constituição (Proteção do Acervo) e isolamento dos arquivos de infraestrutura.
- **Alternatives Considered**:
  - *Bloqueio via servidor proxy externo apenas*: Dependência externa; a aplicação local deve ser segura por padrão (*Secure by Default*).
