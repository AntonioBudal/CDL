# Quickstart: F0.7.11 — Biblioteca Transversal de Highlights e Anotações

**Feature**: [spec.md](spec.md) | **Branch**: `060-biblioteca-highlights-anotacoes` | **Date**: 2026-10-06

Este documento orienta a validação ponta a ponta dos fluxos da Biblioteca Transversal de Highlights e Anotações no ambiente de desenvolvimento local.

---

## 1. Pré-Requisitos e Preparação

1. **Ambiente Backend Ativo**:
   - Python 3.13 no Windows.
   - Banco de dados de teste isolado ou migrações aplicadas.
2. **Ambiente Frontend**:
   - Node.js com dependências instaladas em `caderno-leitura-0.1/frontend`.

---

## 2. Cenários de Validação Automatizada (Backend)

Executar a suíte de testes de biblioteca de destaques:
```powershell
& "caderno-leitura-0.1/backend/.venv/Scripts/pytest.exe" tests/test_highlights_library.py -v
```

### Casos de Teste Chave Cobertos:
1. **Listagem Paginada e Resposta Consolidada**:
   - Criação de múltiplos destaques em diferentes livros/capítulos para o usuário autenticado.
   - Validação de que `GET /api/highlights/library` retorna `book_title`, `chapter_title`, `study_title` e resumo numérico correto.
2. **Isolamento Multiusuário**:
   - Confirmação de que o usuário A nunca recebe destaques do usuário B.
3. **Exclusão de Registros na Lixeira**:
   - Criação de estudo com destaque e posterior deleção do estudo (`deleted_at IS NOT NULL`).
   - Confirmação de que o destaque não aparece mais na biblioteca ativa.
4. **Filtros e Busca Textual**:
   - Filtro por termo `q` em `selected_text` ou `note`.
   - Filtro por `book_id`, `kind` e `color`.
   - Teste de ordenação nos modos `recent` e `by_book`.

---

## 3. Cenários de Validação Automatizada (Frontend)

Executar a suíte de testes unitários e de integração de componentes:
```powershell
node --test tests/highlights_library_view.test.mjs
```

### Casos de Teste Chave Cobertos:
1. **Renderização dos Modos de Visualização**:
   - Alternância entre o modo "Recentes" (feed cronológico) e "Por Obra" (agrupamento hierárquico).
   - Validação da persistência de `view_mode` na URL e `localStorage`.
2. **Barra de Filtros e Busca com Debounce**:
   - Teste da digitação no campo de busca com debounce de 250ms.
   - Sincronização dos parâmetros `q`, `book`, `kind`, `color` na URL.
   - Ação do botão "Limpar filtros".
3. **Gestão In-Card**:
   - Teste da edição rápida da nota inline com botões Salvar/Cancelar.
   - Teste do acionamento de exclusão com diálogo de confirmação.
4. **Salto Contextual**:
   - Teste do botão "Abrir no Estudo" gerando navegação para rota do estudo com âncora `#highlight-{id}`.
5. **Ergonomia e Acessibilidade**:
   - Alvos táteis mínimos de $44 \times 44$px no mobile.
   - Ausência de emojis residuais em código de produção.

---

## 4. Validação Manual Ponta a Ponta

1. Iniciar o servidor local via `python iniciar.py`.
2. Acessar a aplicação no navegador em `http://localhost:8000`.
3. Navegar até um estudo e criar 3 destaques com cores e tipos diferentes (ex.: 1 destaque amarelo, 1 citação verde, 1 pergunta rosa com nota).
4. Clicar no atalho "Destaques" no menu principal para abrir `/highlights`.
5. Verificar a exibição dos 3 cartões no modo "Recentes".
6. Alternar para o modo "Por Obra" e verificar o agrupamento por livro e capítulo.
7. Testar a busca digitando uma palavra contida em uma das notas.
8. Clicar em "Abrir no Estudo" em um dos cartões e verificar:
   - Navegação direta para a tela do estudo.
   - Rolagem suave até a passagem marcada.
   - Ativação do pulso luminoso suave (glow de 2 segundos) no trecho.
