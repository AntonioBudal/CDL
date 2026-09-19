# Guia Rápido de Validação (Quickstart): Edição de Livros, Capítulos e Estudos

**Feature**: `002-edicao-livros-estudos`  
**Date**: 2026-09-17  
**Status**: Ready for Validation  

---

## 1. Pré-Requisitos e Isolamento

1. Todos os testes devem rodar via pytest com fixture `tmp_path`, mantendo `backend/data/caderno.db` 100% isolado.
2. Ambiente virtual Python 3.13 ativo (`backend/.venv/Scripts/python.exe`).
3. Frontend com dependências prontas (`npm run build` ou `npm test`).

---

## 2. Cenários de Validação de Ponta a Ponta

### Cenário 1: Edição Completa de Livro com Novos Metadados
**Objetivo**: Comprovar que título, autor, subtítulo e ano de publicação são atualizados e persistidos sem afetar capítulos ou estudos.

1. **Preparação**: Criar banco temporário com 1 livro contendo 1 capítulo e 1 estudo.
2. **Execução**:
   - Enviar `PATCH /api/books/{id}` com `{"title": "Livro Atualizado", "author": "Novo Autor", "subtitle": "Subtítulo de Teste", "year": 2024}`.
3. **Resultado Esperado**:
   - Status `200 OK`.
   - O livro tem todos os novos campos persistidos e `updated_at` atualizado.
   - Os capítulos e estudos associados continuam exatamente com os mesmos IDs e vínculos.

---

### Cenário 2: Reordenação Atômica de Capítulos
**Objetivo**: Provar que os capítulos podem ser reordenados de forma segura e atômica.

1. **Preparação**: Criar 3 capítulos para um livro: Cap A (pos 0), Cap B (pos 1), Cap C (pos 2).
2. **Execução**:
   - Enviar `POST /api/books/{id}/chapters/{id_B}/move` com `{"direction": "up"}`.
3. **Resultado Esperado**:
   - Status `200 OK`.
   - A nova ordem de capítulos é: Cap B (pos 0), Cap A (pos 1), Cap C (pos 2).
   - Nenhum estudo perde o vínculo com seu capítulo de origem.

---

### Cenário 3: Imutabilidade Absoluta da Resposta de Origem
**Objetivo**: Comprovar que notas e seções de análise são atualizadas mantendo o texto original importado intocado.

1. **Preparação**: Estudo cadastrado com texto original na `source_response`.
2. **Execução**:
   - Enviar `PATCH /api/studies/{id}` alterando `notes` e `summary`.
3. **Resultado Esperado**:
   - As notas e o resumo são alterados com sucesso.
   - O campo `source_response` no banco permanece byte a byte idêntico ao original.

---

### Cenário 4: Prevenção de Conflito Concorrente entre PC e Celular
**Objetivo**: Comprovar que uma escrita desatualizada é rejeitada com HTTP 409.

1. **Preparação**: Obter o `updated_at` atual de um estudo.
2. **Execução**:
   - Simular que o PC alterou o estudo (avançando `updated_at`).
   - Simular envio posterior do celular com o `expected_updated_at` anterior.
3. **Resultado Esperado**:
   - O servidor retorna `409 Conflict`.
   - O estudo não é sobrescrito no banco.
   - O cliente mantém os campos digitados preservados no formulário.

---

## 3. Comandos de Teste Automatizado

```powershell
# Na raiz real da aplicação (caderno-leitura-0.1):
.\backend\.venv\Scripts\python.exe -m pytest backend/tests/test_edit_acervo.py -v
```
