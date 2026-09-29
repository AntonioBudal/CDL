# Quickstart: F0.6.5 — Histórico Automático de Versões de Estudo

## Cenários de Validação Ponta a Ponta

Este documento orienta a execução e verificação dos fluxos de versionamento automático no ambiente de desenvolvimento local.

---

## Pré-requisitos

- Python 3.13 com virtualenv ativo.
- Node.js 24+ com dependências instaladas em `frontend/`.
- Suíte de testes isolada executando em banco temporário (`tmp_path`).

---

## Cenário 1: Registro Automático de Versão ao Editar Estudo

1. **Ação**:
   - Abrir um estudo existente em `http://localhost:8000/livros/{bookId}/estudos/{studyId}`.
   - Clicar em "Editar estudo".
   - Modificar o título e acrescentar um parágrafo na seção "Resumo".
   - Clicar em "Salvar alterações".
2. **Resultado Esperado**:
   - O estudo é salvo com sucesso.
   - O backend registra a versão anterior como snapshot base (se inexistente) e a nova versão modificada.
   - Ao abrir o painel "Histórico de versões", duas versões são listadas com seus respectivos horários e autor.

---

## Cenário 2: Janela de Coalescência de 5 Minutos

1. **Ação**:
   - Dentro de 2 minutos após o salvamento anterior, clicar novamente em "Editar estudo".
   - Fazer uma pequena correção de pontuação ou digitação.
   - Clicar em "Salvar alterações".
2. **Resultado Esperado**:
   - Nenhuma nova entrada de versão é criada na linha do tempo.
   - A versão mais recente é atualizada no mesmo registro (`updated_at` renovado), consolidando a sessão de trabalho sem poluir a lista.

---

## Cenário 3: Inspeção e Visualização de Diferenças (Diff)

1. **Ação**:
   - No estudo, clicar no botão "Histórico de versões".
   - O modal de histórico se abre exibindo a linha do tempo à esquerda.
   - Clicar na versão anterior à atual.
   - Alternar para a aba "Comparar Alterações (Diff)".
2. **Resultado Esperado**:
   - A interface exibe as seções comparadas.
   - Trechos adicionados aparecem com destaque visual de inserção.
   - Trechos removidos aparecem com destaque visual de exclusão.
   - Seções que não foram modificadas indicam "Seção inalterada" de forma compacta.

---

## Cenário 4: Restauração Segura de Versão Anterior

1. **Ação**:
   - Na versão anterior inspecionada, clicar no botão "Restaurar esta versão".
   - O sistema apresenta o diálogo de confirmação explicando que o estado atual será preservado antes de aplicar o conteúdo recuperado.
   - Confirmar a restauração.
2. **Resultado Esperado**:
   - O estudo é atualizado no banco de dados com os dados da versão restaurada (incluindo texto e destaques de Leitura Ativa).
   - Uma nova versão é registrada no histórico com a etiqueta "Restauração da versão X".
   - A interface do estudo é recarregada exibindo o conteúdo recuperado e uma notificação de sucesso.

---

## Comandos de Verificação Automatizada

### Testes de Backend (FastAPI / SQLAlchemy)

```powershell
# Executar a partir de caderno-leitura-0.1/backend
pytest tests/test_study_versions.py -v
```

### Testes de Frontend (Vue 3 / TypeScript)

```powershell
# Executar a partir de caderno-leitura-0.1/frontend
npm test
npm run build
```
