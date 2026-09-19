# Guia Rápido de Validação: Capas de Livros

**Feature**: Capas de Livros por Upload e URL  
**Branch**: `004-capas-livros` | **Data**: 2026-09-18  
**Status**: Concluído

Este documento estabelece os procedimentos passo a passo e cenários executáveis para validar todas as capacidades da Feature 004, cobrindo backend, frontend, segurança contra SSRF e persistência atômica.

---

## 1. Pré-Requisitos e Ambiente de Testes

- **Python**: 3.13.15 com virtualenv ativo em `backend/.venv`.
- **Node.js**: v24.14.1 / npm para testes do frontend.
- **Regra Fundamental de Isolamento**: Os testes NUNCA tocam em `backend/data/caderno.db`. Todas as suítes utilizam `tmp_path` descartável para o banco SQLite e para o diretório de capas (`CADERNO_COVERS_DIR`).

```powershell
# Executar a suíte de testes de capas no backend
cd C:\Users\User\caderno\caderno-leitura-0.1\backend
.\.venv\Scripts\pytest tests/test_book_covers.py -v

# Executar a validação dos testes do frontend
cd C:\Users\User\caderno\caderno-leitura-0.1\frontend
npm test
```

---

## 2. Cenários de Validação Executáveis

### Cenário 1: Upload e Redimensionamento Local de Imagem (P1 - MVP)
**Objetivo**: Comprovar que o leitor envia uma imagem local (JPEG/PNG/WebP), o backend redimensiona para largura máxima de 800px, converte para WebP e associa ao livro.

1. **Dado** um livro cadastrado com ID `1` e sem capa.
2. **Quando** uma imagem JPEG de 1600x2400px (2 MB) é enviada via `POST /api/books/1/cover` (multipart).
3. **Então**:
   - Resposta HTTP 200 contendo `cover_image` (ex.: `f47ac10b...webp`) e `cover_url`.
   - O arquivo físico é gerado no diretório temporário de capas.
   - A largura da imagem gerada no disco é de no máximo 800px (mantendo proporção).
   - O formato real verificado do arquivo é `WEBP`.
   - `GET /api/covers/{filename}` retorna a imagem com `Content-Type: image/webp` e `Cache-Control: public, max-age=86400`.

### Cenário 2: Marcador Tipográfico Elegante / Fallback (P1)
**Objetivo**: Garantir que livros sem capa exibem um placeholder consistente e harmônico.

1. **Dado** um livro recém-criado sem capa (`cover_image = null`).
2. **Quando** o livro é renderizado na estante (`BooksView.vue`) ou na página do livro (`BookView.vue`).
3. **Então**:
   - O componente `BookCover.vue` renderiza a caixa na proporção 2:3.
   - Um gradiente harmônico de fundo é calculado deterministicamente a partir do título da obra.
   - As iniciais, o título e o autor são renderizados com tipografia legível.
   - Nenhum erro de imagem quebrada ou `404` é registrado no console do navegador.

### Cenário 3: Importação de Capa via URL Externa Pública (P2)
**Objetivo**: Comprovar o download seguro a partir de uma URL direta de imagem.

1. **Dado** um livro ativo com ID `2`.
2. **Quando** o usuário submete `POST /api/books/2/cover/url` com o corpo `{"url": "https://images.unsplash.com/photo-exemplo.jpg"}`.
3. **Então**:
   - O backend efetua a requisição segura externa com timeout de 5 segundos.
   - O arquivo baixado é validado como imagem válida, redimensionado para WebP e salvo no diretório de capas.
   - O livro tem o campo `cover_image` atualizado com o hash seguro gerado.

### Cenário 4: Proteção contra SSRF e Arquivos Corrompidos (P2)
**Objetivo**: Garantir que tentativas de ataque ou dados maliciosos sejam sumariamente neutralizados.

1. **Dado** requisições maliciosas ou inválidas para o backend:
   - **Caso 4A (Loopback)**: URL `http://127.0.0.1:8000/api/books` ou `http://localhost/segredo`.
   - **Caso 4B (Rede Privada RFC 1918)**: URL `http://192.168.1.1/admin` ou `http://10.0.0.1/`.
   - **Caso 4C (Arquivo não imagem)**: URL apontando para uma página HTML ou script `.exe`.
   - **Caso 4D (Upload com extensão falsa)**: Arquivo `.jpg` cujo conteúdo seja um script texto ou HTML.
2. **Quando** as requisições são submetidas:
   - Casos 4A e 4B são interceptados pela validação de DNS/IP e retornam HTTP 400 ("O endereço informado não é permitido por motivos de segurança"), **sem** disparar conexão HTTP de saída.
   - Casos 4C e 4D são interceptados pela validação do Pillow e retornam HTTP 400 ("Formato de imagem não suportado"), preservando a capa original do livro intacta.

### Cenário 5: Substituição, Remoção, Soft Delete e Purga Definitiva (P3)
**Objetivo**: Validar a integridade referencial do ciclo de vida físico da imagem.

1. **Substituição**:
   - Ao enviar nova capa para um livro que já possuía capa, a nova imagem passa a ser ativa.
2. **Remoção**:
   - Ao acionar `DELETE /api/books/1/cover`, o campo `cover_image` se torna `null` e o livro retorna imediatamente ao marcador tipográfico.
3. **Soft Delete (Lixeira)**:
   - Ao mover o livro para a lixeira (`POST /api/books/1/trash`), o arquivo físico de capa **continua preservado** no diretório.
   - Ao restaurar o livro (`POST /api/books/1/restore`), a capa volta a ser exibida imediatamente.
4. **Exclusão Definitiva (Purga)**:
   - Ao excluir definitivamente o livro da lixeira (`DELETE /api/books/1/permanent`), o arquivo físico correspondente é removido do disco se órfão.
