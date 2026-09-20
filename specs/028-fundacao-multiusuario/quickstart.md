# Quickstart: Validação da Fundação Multiusuário e CRUD Geral (F01)

**Feature**: `028-fundacao-multiusuario`  
**Date**: 2026-09-20  

Este guia detalha os procedimentos para validar a migração de dados e o isolamento multiusuário entre contas distintas.

---

## 1. Pré-Requisitos e Ambiente

- Python 3.13 de 64 bits com ambiente virtual ativo em `caderno-leitura-0.1/backend/.venv`.
- Dependências de desenvolvimento instaladas (`pytest`, `httpx`).
- Diretório de trabalho: `caderno-leitura-0.1/backend`.

---

## 2. Cenário 1: Validação de Migração do Acervo Legado

**Objetivo**: Confirmar que uma base de dados anterior (sem `user_id`) é migrada com 100% de preservação para o proprietário inicial.

### Procedimento
1. Criar um banco SQLite temporário via fixture `tmp_path`.
2. Aplicar as revisões do Alembic até a `0010_add_search_history`.
3. Inserir dados legados sintéticos (1 livro, 2 capítulos, 3 estudos e relações sem `user_id`).
4. Aplicar a nova revisão `0011_add_user_and_multiuser_foundation`.
5. Consultar a tabela `users` e verificar o registro do proprietário canônico:
   - `id = '00000000-0000-0000-0000-000000000001'`
   - `username = 'proprietario'`
6. Verificar que todos os registros anteriores possuem `user_id == '00000000-0000-0000-0000-000000000001'`.

**Comando de Teste**:
```powershell
$env:PYTHONPATH="."
.\.venv\Scripts\python.exe -m pytest tests/test_multiuser_migration.py -v
```

**Resultado Esperado**:
- Todos os testes de migração passam com 100% dos dados associados ao usuário soberano.

---

## 3. Cenário 2: Isolamento de Leitura e Escrita entre Dois Usuários

**Objetivo**: Confirmar que o "Leitor A" não consegue visualizar, listar ou editar registros criados pelo "Leitor B".

### Procedimento
1. Inicializar cliente de teste FastAPI (`TestClient`).
2. Criar "Usuário A" e "Usuário B" no banco de teste.
3. Como "Usuário A" (`headers={"X-User-Id": user_a.id}`), cadastrar o livro *"Crítica da Razão Pura"*.
4. Como "Usuário B" (`headers={"X-User-Id": user_b.id}`), solicitar `GET /api/books`.
   - **Resultado Esperado**: Lista vazia `[]`.
5. Como "Usuário B", tentar `GET /api/books/{livro_a.id}`.
   - **Resultado Esperado**: `HTTP 404 Not Found`.
6. Como "Usuário B", tentar `PATCH /api/books/{livro_a.id}` ou `DELETE /api/books/{livro_a.id}`.
   - **Resultado Esperado**: `HTTP 404 Not Found` (proteção anti-enumeração IDOR).

**Comando de Teste**:
```powershell
$env:PYTHONPATH="."
.\.venv\Scripts\python.exe -m pytest tests/test_multiuser_isolation.py -v
```

---

## 4. Cenário 3: Validação das Categorias Híbridas

**Objetivo**: Confirmar que categorias do sistema são compartilhadas e categorias pessoais são privativas.

### Procedimento
1. Como "Usuário A", cadastrar categoria pessoal *"Ontologia Particular"*.
2. Como "Usuário B", listar `GET /api/categories`.
   - **Resultado Esperado**: Vê as categorias padrão do sistema, mas NÃO vê *"Ontologia Particular"*.
3. Como "Usuário B", tentar `DELETE /api/categories/{id_ontologia_particular}`.
   - **Resultado Esperado**: `HTTP 404 Not Found`.
4. Como "Usuário A", tentar `DELETE` em uma categoria global do sistema (`user_id IS NULL`).
   - **Resultado Esperado**: `HTTP 403 Forbidden` (categorias padrão protegidas).

---

## 5. Cenário 4: Não-Regressão da Aplicação Monousuário Atual

**Objetivo**: Garantir que requisições legadas (sem cabeçalho `X-User-Id`) continuem funcionando normalmente através do fallback para o usuário soberano.

### Procedimento
Executar a suíte de testes integral do backend e do frontend:
```powershell
# Backend (200+ testes)
$env:PYTHONPATH="."
.\.venv\Scripts\python.exe -m pytest tests

# Frontend (223 testes)
cd ../frontend
npm test
npm run build
```

**Resultado Esperado**:
- 100% dos testes existentes continuam passando sem falhas.
