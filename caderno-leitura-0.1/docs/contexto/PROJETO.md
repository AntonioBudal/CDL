# Caderno de Leitura — Arquitetura e Contexto do Produto

## 1. Visão Geral do Produto
O **Caderno de Leitura** é uma aplicação pessoal desenvolvida para organizar leituras, anotações e reflexões sobre livros e seus respectivos capítulos.

O fluxo de alimentação do caderno baseia-se na importação manual de respostas geradas por IA (como ChatGPT) por meio de um prompt padrão estruturado. A aplicação analisa a resposta e preenche automaticamente quatro seções de estudo:
1. **Resumo:** Síntese em prosa do trecho.
2. **Explicação:** Interpretação didática e aprofundamento.
3. **Conceitos:** Termos-chave e definições extraídas.
4. **Referências:** Citações bibliográficas, notas contextuais e fontes.

Adicionalmente, o usuário registra sua localização no livro (ex.: página, porcentagem ou posição Kindle), suas anotações pessoais livres e mantém a cópia literal da resposta do modelo (`source_response`).

## 2. Topologia e Arquitetura do Sistema
- **Execução:** Servidor único rodando no próprio computador via Python 3.13 (`iniciar.py`), servindo simultaneamente a API REST FastAPI e os arquivos estáticos pré-compilados do frontend Vue (`frontend/dist`).
- **Acesso Multidispositivo:** O servidor pode ser inicializado no endereço local (`127.0.0.1:8000`) ou na rede local privada / Tailscale (`0.0.0.0:8000`), exibindo no terminal o IP local e um QR Code ASCII para emparelhamento direto do celular.
- **Isolamento e Privacidade:** Todo o processamento e armazenamento ocorrem no dispositivo do usuário. Não há contas em nuvem, dependência de conexões externas ativas em tempo de execução nem telemetria.

## 3. Stack Tecnológica
- **Backend:**
  - Python 3.13 (64-bit)
  - FastAPI 0.141.1
  - SQLAlchemy 2.0.52 (ORM declarativo tipado)
  - Alembic 1.19.2 (migrações de esquema)
  - Uvicorn 0.52.4 (servidor ASGI)
  - Pydantic 2.13.5 (validação e schemas)
  - Pillow 12.3.0 (processamento, redimensionamento Lanczos e conversão WebP de capas)
  - python-multipart 0.0.32 (suporte a uploads de arquivos)
  - httpx 0.28.1 (download seguro de imagens externas com proteção anti-SSRF)
  - QRCode 8.2 (impressão de QR Code no terminal)
- **Frontend:**
  - Vue 3.5.41 (Composition API, `<script setup>`)
  - TypeScript 6.0.2
  - Vite 8.2.2 (bundler e servidor de desenvolvimento)
  - Vue Router 4.6.4 (navegação SPA com rotas por livro, capítulo e estudo)
  - markdown-it 14.3.1 + markdown-it-mark 4.0.0 (renderização segura)
  - Fontes locais empacotadas: EB Garamond, Source Sans 3, OpenDyslexic
- **Banco de Dados e Armazenamento:**
  - SQLite 3 local gerenciado pelo Python
  - Ativação obrigatória de chaves estrangeiras (`PRAGMA foreign_keys=ON`) por evento de conexão
  - Timeout de conexão e isolamento multi-thread em modo WAL
  - Caminho configurável via `CADERNO_DATABASE_PATH`, padrão: `backend/data/caderno.db`
  - Diretório persistente de capas configurável via `CADERNO_COVERS_DIR`, padrão: `backend/data/covers/`

## 4. Modelos de Dados Atuais (Esquema 0004)
- **`books` (Livros):**
  - `id` (Integer, PK)
  - `title` (Text, não vazio)
  - `author` (Text, opcional)
  - `subtitle` (Text, default '')
  - `year` (Integer, opcional, 1000 a 2100)
  - `cover_image` (Text, opcional, nome do arquivo seguro em disco)
  - `created_at` (DateTime UTC)
  - `updated_at` (DateTime UTC)
  - `deleted_at` (DateTime UTC, opcional, lixeira / soft delete)
  - Índice: `ix_books_deleted_at`
- **`chapters` (Capítulos):**
  - `id` (Integer, PK)
  - `book_id` (Integer, FK -> books.id, RESTRICT)
  - `name` (Text, não vazio)
  - `position` (Integer, >= 0, default 0)
  - Índice: `ix_chapters_book_id_position`
- **`studies` (Estudos):**
  - `id` (Integer, PK)
  - `chapter_id` (Integer, FK -> chapters.id, RESTRICT)
  - `title` (Text, não vazio)
  - `location` (Text, default '')
  - `source_response` (Text, cópia literal da IA)
  - `summary` (Text, Resumo)
  - `explanation` (Text, Explicação)
  - `concepts` (Text, Conceitos)
  - `references` (Text, Referências)
  - `notes` (Text, anotações próprias do usuário)
  - `created_at` (DateTime UTC, default CURRENT_TIMESTAMP)
  - `updated_at` (DateTime UTC, default CURRENT_TIMESTAMP)
  - `deleted_at` (DateTime UTC, opcional, lixeira / soft delete)
  - Restrição: ao menos uma das quatro seções deve conter texto.
  - Índices: `ix_studies_chapter_id`, `ix_studies_deleted_at`

## 5. Rotas de API Existentes
- `GET /api/health` — Verificação de saúde da aplicação
- `GET /api/backup` — Download de backup do banco gerado via SQLite Online Backup API
- `GET /api/books` e `POST /api/books` — Consulta e criação de livros
- `GET /api/books/{book_id}`, `PATCH /api/books/{book_id}` — Detalhes e edição com controle de concorrência otimista
- `POST /api/books/{book_id}/cover` — Upload multipart de arquivo de capa com redimensionamento WebP
- `POST /api/books/{book_id}/cover/url` — Importação segura de imagem externa por URL com validação anti-SSRF
- `DELETE /api/books/{book_id}/cover` — Remoção de capa (retorno ao marcador tipográfico padrão)
- `GET /api/covers/{filename}` — Servir arquivo estático de capa com cabeçalhos de cache HTTP
- `POST /api/books/{book_id}/trash`, `POST /api/books/{book_id}/restore`, `DELETE /api/books/{book_id}/permanent` — Ciclo de lixeira para livros
- `GET /api/books/{book_id}/chapters` e `POST /api/books/{book_id}/chapters` — Capítulos por livro
- `GET /api/chapters/{chapter_id}/studies` — Estudos por capítulo
- `GET /api/studies/{study_id}`, `PATCH /api/studies/{study_id}` — Detalhes e edição de estudos
- `POST /api/studies/{study_id}/trash`, `POST /api/studies/{study_id}/restore`, `DELETE /api/studies/{study_id}/permanent` — Ciclo de lixeira para estudos
- `GET /api/trash`, `POST /api/trash/empty`, `POST /api/trash/purge-expired` — Gestão central da lixeira e expurgo
- `POST /api/imports/preview` e `POST /api/imports` — Parsing e persistência de estudos importados
