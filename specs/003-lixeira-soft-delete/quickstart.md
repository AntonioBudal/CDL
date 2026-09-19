# Quickstart: Validação da Lixeira e Soft Delete

**Feature**: `003-lixeira-soft-delete`  
**Date**: 2026-09-18  

Este guia orienta a validação ponta a ponta da lixeira, restauração e expurgo permanente.

---

## 1. Pré-requisitos e Configuração do Ambiente

Execute os testes com banco efêmero isolado (`tmp_path`) e ambiente virtual local:

```powershell
# No diretório raiz do projeto
cd C:\Users\User\caderno\caderno-leitura-0.1

# Execução da suíte de testes automatizados de lixeira
.\backend\.venv\Scripts\python.exe -m pytest backend/tests/test_trash_soft_delete.py -v
```

---

## 2. Cenários de Validação

### Cenário 1: Descarte de Livro (Soft Delete) e Ocultação do Acervo Ativo
1. **Ação**: Criar um livro sintético com 2 capítulos e 4 estudos.
2. **Executar**: Chamar `POST /api/books/{book_id}/trash`.
3. **Verificar**:
   - Resposta HTTP 200 com campo `deleted_at` preenchido.
   - Chamada a `GET /api/books` **não** lista o livro descartado.
   - Chamada a `GET /api/books/{book_id}` retorna HTTP 404.
   - Chamada a `GET /api/trash` lista o livro na seção de livros descartados.

---

### Cenário 2: Descarte Individual de Estudo
1. **Ação**: Em um livro ativo, chamar `POST /api/studies/{study_id}/trash` em um de seus estudos.
2. **Verificar**:
   - O livro continua visível em `GET /api/books`.
   - O livro detalhado em `GET /api/books/{book_id}` omite o estudo descartado da lista do capítulo.
   - Chamada a `GET /api/trash` lista o estudo na seção de estudos descartados.

---

### Cenário 3: Restauração com Cascata Ascendente
1. **Ação**: Com um livro e seu estudo ambos na lixeira, chamar `POST /api/studies/{study_id}/restore`.
2. **Verificar**:
   - O estudo tem `deleted_at` setado como `null`.
   - O livro pai automaticamente tem `deleted_at` setado como `null`.
   - Tanto o livro quanto o estudo voltam a aparecer normalmente em `GET /api/books` e `GET /api/books/{book_id}`.

---

### Cenário 4: Exclusão Definitiva e Integridade de Chaves Estrangeiras
1. **Ação**: Chamar `DELETE /api/books/{book_id}/permanent`.
2. **Verificar**:
   - Resposta HTTP 204 No Content.
   - O livro, seus capítulos e estudos subordinados são completamente removidos do banco.
   - Não ocorre nenhuma violação de chave estrangeira (`sqlite3.IntegrityError: FOREIGN KEY constraint failed`).

---

### Cenário 5: Purga Automática após 30 Dias
1. **Ação**: Inserir um registro com `deleted_at = datetime.now(timezone.utc) - timedelta(days=31)`.
2. **Executar**: Acionar `POST /api/trash/purge-expired` (ou chamar `GET /api/trash`).
3. **Verificar**:
   - O registro com mais de 30 dias é removido permanentemente do banco.
   - Registros descartados há menos de 30 dias continuam preservados na lixeira.
