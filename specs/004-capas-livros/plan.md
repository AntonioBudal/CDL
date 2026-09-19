# Implementation Plan: Capas de Livros por Upload e URL

**Branch**: `004-capas-livros` | **Date**: 2026-09-18 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/004-capas-livros/spec.md`

## Summary

Esta feature implementa o suporte a Capas de Livros por Upload local e Importação via URL no Caderno de Leitura, atendendo à entrega T03 do Roadmap 0.3. O objetivo é permitir que o leitor personalize visualmente seu acervo através do envio de imagens do computador ou smartphone e da importação de URLs diretas da internet. A solução contempla a validação estrita de integridade e formatos (JPEG, PNG, WebP), o redimensionamento e otimização no servidor para largura máxima de 800px no formato WebP (Pillow), o armazenamento seguro em diretório persistente (`backend/data/covers`), rota de entrega controlada com cache HTTP, mitigação rigorosa de SSRF (validação de resolução DNS e bloqueio de IPs locais/privados com httpx), ciclo de vida consistente na lixeira (soft delete retém capa; exclusão definitiva expurga arquivo físico órfão) e componente visual frontend com fallback tipográfico responsivo e elegante.

## Technical Context

**Language/Version**: Python 3.13.15 (64-bit Windows), TypeScript 5.9 (Node.js v24.14.1)  
**Primary Dependencies**: FastAPI 0.141.1, SQLAlchemy 2.0.52, Alembic 1.19.2, Pydantic 2.13.5, Pillow>=10.0.0, python-multipart>=0.0.18, httpx 0.28.1, Vue 3.5.13, Vite 6.2.0  
**Storage**: SQLite local em modo WAL (`backend/data/caderno.db`), coluna textual `cover_image` em `books`; diretório de arquivos binários em `backend/data/covers/` (resolvido por `get_covers_dir()`, configurável via `CADERNO_COVERS_DIR`, 100% isolado em testes via `tmp_path`)  
**Testing**: pytest 9.1.1 (`backend/tests/test_book_covers.py`), node:test (`frontend/tests/`), 100% isolados usando bases e pastas efêmeras em `tmp_path`  
**Target Platform**: Windows local (PowerShell), processo único local servindo desktop e dispositivos móveis (Tailscale/LAN)  
**Project Type**: Web Application monousuário pessoal (FastAPI backend REST + SPA Vue 3)  
**Performance Goals**: Upload e otimização < 1s; entrega de capas em rede local < 200ms com cabeçalhos de cache HTTP (`Cache-Control: public, max-age=86400`); importação de URL externa com timeout de conexão de 3s e leitura de 5s  
**Constraints**: Teto máximo de 5 MB por arquivo; formatos aceitos: JPEG, PNG, WebP; largura máxima de 800px em WebP; 100% de bloqueio de requisições SSRF para redes privadas; nomes de arquivos higienizados baseados em UUID v4; retenção física na lixeira e expurgo atômico na exclusão definitiva  
**Scale/Scope**: Monousuário, centenas de livros com capas armazenadas localmente  

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Artigo Constitucional | Exigência | Avaliação no Plano | Status |
|---|---|---|---|
| **Art. I: Privacidade do Acervo** | Jamais exibir ou logar textos do acervo no chat ou terminal | Todas as validações, uploads e testes utilizam exclusivamente dados sintéticos e imagens geradas em memória | **PASS** |
| **Art. II: Isolamento de Testes** | Testes nunca tocam em `backend/data/caderno.db` | Suíte criada exclusivamente com fixtures `tmp_path`, `CADERNO_COVERS_DIR` efêmero e banco temporário | **PASS** |
| **Art. III: Fidelidade Tecnológica** | Python 3.13, FastAPI, SQLAlchemy 2, Alembic, Vue 3, Vite | Mantida a stack oficial; adicionada biblioteca padrão de imagens `Pillow` e `python-multipart` para uploads | **PASS** |
| **Art. IV: Governança SDD** | Fatias pequenas e verificáveis; T01–T10 não iniciadas | Esta fatia desenha rigorosamente os requisitos de T03 sem alterar o status formal das tarefas do roadmap | **PASS** |
| **Art. V: Resiliência Operacional** | Contratos de configuração unificados e proteção de banco | Adicionado `get_covers_dir()` em `config.py` respeitando `CADERNO_COVERS_DIR`; migração incremental `0004_add_book_cover_image.py` | **PASS** |

## Project Structure

### Documentation (this feature)

```text
specs/004-capas-livros/
├── spec.md              # Especificação de requisitos, cenários de aceite e esclarecimentos
├── plan.md              # Este plano de implementação
├── research.md          # Decisões técnicas consolidadas (Pillow, SSRF, armazenamento, ciclo de vida, UI)
├── data-model.md        # Modelagem de dados, coluna cover_image, schemas Pydantic e máquina de estados
├── quickstart.md        # Guia passo a passo de validação executável
├── contracts/           # Contratos de API REST
│   └── covers-api.md    # Endpoints de upload, importação URL, remoção e rota de entrega estática
└── checklists/
    └── requirements.md  # Checklist de qualidade (16/16 aprovado)
```

### Source Code (repository root)

```text
caderno-leitura-0.1/
├── backend/
│   ├── app/
│   │   ├── core/
│   │   │   └── config.py              # Adiciona função canônica get_covers_dir() com suporte a CADERNO_COVERS_DIR
│   │   ├── models/
│   │   │   └── book.py                # Adiciona cover_image: Mapped[str | None]
│   │   ├── schemas/
│   │   │   ├── book.py                # Atualiza BookRead e BookPatch com cover_image
│   │   │   └── cover.py               # Novos schemas CoverUrlRequest e CoverResponse
│   │   ├── services/
│   │   │   ├── cover_service.py       # Validação de imagens, redimensionamento (Pillow), download seguro anti-SSRF e expurgo
│   │   │   └── trash_service.py       # Integra expurgo físico de capas em permanent_delete_book, empty_trash e purge
│   │   └── routers/
│   │       ├── books.py               # Rotas POST /cover, POST /cover/url, DELETE /cover
│   │       └── covers.py              # Rota GET /api/covers/{filename} para servir arquivos estáticos de forma controlada
│   ├── migrations/
│   │   └── versions/
│   │       └── 0004_add_book_cover_image.py  # Migração incremental adicionando coluna cover_image na tabela books
│   ├── requirements.in                # Adiciona Pillow>=10.0.0 e python-multipart>=0.0.18
│   ├── requirements.txt               # Atualizado com novas dependências fixadas
│   └── tests/
│       └── test_book_covers.py        # Suíte de testes isolados cobrindo os 5 cenários de capas
└── frontend/
    └── src/
        ├── types.ts                   # Atualiza Book com cover_image e exporta CoverResponse
        ├── services/api.ts            # Métodos uploadBookCover, importBookCoverFromUrl, removeBookCover
        ├── components/
        │   ├── BookCover.vue          # Novo componente reutilizável com proporção 2:3 e fallback tipográfico harmônico
        │   └── BookEditModal.vue      # Seção de gestão de capa (upload local, URL externa, preview e remoção)
        └── views/
            ├── BooksView.vue          # Integração do componente BookCover nos cartões da estante
            └── BookView.vue           # Integração do componente BookCover no cabeçalho do livro
```

## Complexity Tracking

| Componente | Justificativa | Alternativa Rejeitada |
|---|---|---|
| **Pillow (PIL)** | Validação real de integridade binária, prevenção de arquivos forjados, redimensionamento proporcional e compressão WebP de alta qualidade. | Armazenar imagens cruas (fotos de 5MB de smartphones travariam redes móveis) ou decoders incompletos sem suporte a WebP. |
| **Filtro Anti-SSRF (DNS + ipaddress)** | Prevenir que requisições HTTP do servidor alcancem endereços locais (localhost, 192.168.x.x, portas internas). | Confiar cegamente na URL informada ou tentar download pelo frontend (bloqueado por CORS). |
| **python-multipart** | Dependência padrão do Starlette/FastAPI para processamento de requisições `multipart/form-data` com `UploadFile`. | Upload via Base64 em JSON (incha o payload em 33% e consome memória excessiva). |
