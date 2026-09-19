# Quickstart & Validation Guide: Exportação de Anotações em TXT e Markdown

**Feature Branch**: `015-exportacao-anotacoes`  
**Date**: 2026-09-19  

Este roteiro descreve como validar a exportação de anotações e estudos tanto de forma automatizada quanto interativa.

---

## 1. Validação Automatizada

### Testes do Backend (Pytest)
Executa a validação isolada do serviço de exportação e endpoints da API contra banco descartável em `tmp_path`:
```powershell
cd c:\Users\User\caderno\caderno-leitura-0.1\backend
.venv\Scripts\python.exe -m pytest tests/test_export.py -v
```

### Testes do Frontend (Node Test Runner)
Executa os testes de componentes e cliente de download:
```powershell
cd c:\Users\User\caderno\caderno-leitura-0.1\frontend
npm test
```

### Validação de Tipos e Build (Vite)
```powershell
npm run build
```

---

## 2. Cenários Manuais de Validação

### Cenário 1: Exportação Consolidada de Livro em Markdown (.md)
1. Inicie a aplicação via `INICIAR.cmd` e acesse `http://localhost:8000/`.
2. Abra um livro com capítulos e estudos cadastrados.
3. No cabeçalho da página do livro, clique no botão **"Exportar anotações"**.
4. No modal exibido, verifique que o formato **Markdown (.md)** está selecionado e que as caixas **Minhas Anotações** e **Seções de Estudo** estão marcadas.
5. Clique em **"Baixar arquivo"**.
6. Abra o arquivo baixado em um editor de texto (VS Code, Bloco de Notas ou Obsidian):
   - Verifique que o topo contém o bloco Frontmatter YAML (`--- title: ... ---`).
   - Verifique que os capítulos e estudos estão dispostos hierarquicamente com títulos legíveis.
   - Verifique que a acentuação em português e os destaques `==marcação==` estão intactos.

### Cenário 2: Exportação Consolidada de Livro em Texto Puro (.txt)
1. Na mesma página do livro, clique novamente em **"Exportar anotações"**.
2. Alterne o formato para **Texto Puro (.txt)**.
3. Clique em **"Baixar arquivo"**.
4. Abra o arquivo `.txt` e confira a formatação com divisores ASCII (`===` e `---`), sem blocos YAML e com texto limpo e legível.

### Cenário 3: Exportação Pontual de Estudo Individual
1. Entre na tela de leitura de um estudo específico.
2. Na barra de ações superior, clique em **"Exportar estudo"**.
3. Baixe o arquivo e confirme que apenas o estudo ativo foi exportado, com nome de arquivo sugestivo contendo o título do estudo e do livro.

### Cenário 4: Exclusão Rigorosa de Itens da Lixeira
1. Mova um estudo ou capítulo para a lixeira.
2. Realize uma nova exportação do livro.
3. Confirme que o estudo ou capítulo presente na lixeira não consta em nenhuma parte do arquivo exportado.

### Cenário 5: Teste em Dispositivo Móvel / Rede Local
1. Acesse o sistema pelo navegador de um celular conectado via rede local ou Tailscale.
2. Solicite a exportação de um livro.
3. Confirme que o navegador do celular abre a janela nativa de salvamento/download sem bloqueios ou falhas.
