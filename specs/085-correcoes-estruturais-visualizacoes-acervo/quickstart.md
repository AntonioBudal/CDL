# Guia Rápido de Validação: Correções Estruturais nas Visualizações do Acervo

**Feature**: `085-correcoes-estruturais-visualizacoes-acervo`
**Data**: 2026-10-24
**Status**: Concluído

---

## 1. Comandos de Validação Automatizada

Todos os comandos devem ser executados no terminal PowerShell dentro do diretório do projeto:

```powershell
# 1. Executar teste unitário focado da feature
cd caderno-leitura-0.1/frontend
node --test tests/feature-085-study-views-layout.test.mjs

# 2. Executar suíte completa de testes de regressão do frontend
npm test

# 3. Executar type-check e build estático do Vite
npm run build

# 4. Executar suíte de testes do backend (isolamento em tmp_path)
cd ../..
.venv/Scripts/pytest.exe -q
```

---

## 2. Roteiro de Verificação Manual no Navegador

1. **Abertura do Caderno de Leitura**:
   - Inicie o servidor via `python iniciar.py`.
   - Acesse `http://localhost:8000/livros/1` (ou qualquer livro do acervo).
2. **Visualização em Lista (`StudyListView.vue`)**:
   - Alterne para o modo de lista clicando no botão correspondente do `ViewSwitcher`.
   - **Teste de Corte no Topo**: Clique no badge de status do primeiro estudo. O menu deve abrir para baixo, sem cortes laterais ou superiores.
   - **Teste de Corte no Rodapé**: Role até o último estudo da lista e clique no badge de status. O menu deve abrir para cima (`opens-upward`), sobrepondo a linha sem ser cortado pelo rodapé ou pela janela.
   - **Teste do Ícone de Ordenação**:
     - Clique nos cabeçalhos "Título", "Status" e "Data".
     - Alterne os temas no menu de usuário (ex.: `sepia`, `pergaminho`, `noturno`, `nordico`).
     - Verifique que a seta SVG de ordenação possui contraste claro e herda a cor exata do rótulo da coluna.
   - **Teste de Alinhamento Geométrico**:
     - Redimensione a janela do navegador entre 1024px, 1440px e 1920px.
     - Confirme que as linhas de cabeçalho e dados mantêm as colunas perfeitamente alinhadas.
3. **Visualização em Grade (`StudyGridView.vue`)**:
   - Alterne para o modo grade.
   - Clique no badge de status de um cartão da primeira linha.
   - Confirme que o menu suspenso flutua sobre os cartões da linha de baixo sem ser sobreposto por eles.
