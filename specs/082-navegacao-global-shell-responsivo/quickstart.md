# Quickstart de Validação: F0.9.01 — Arquitetura de Navegação Global e Shell Responsivo

**Feature**: `specs/082-navegacao-global-shell-responsivo`  
**Date**: 2026-10-20  

Este guia detalha o procedimento para validar localmente as correções de navegação, offsets e trilhas (breadcrumbs).

---

## 1. Validação Automatizada de Testes

Execute a suíte completa de testes no frontend para garantir que nenhum contrato foi quebrado:

```powershell
cd c:\Users\User\caderno\caderno-leitura-0.1\frontend
npm test
```

Valide também a tipagem estrita com TypeScript e compilação do Vite:

```powershell
npm run build
```

---

## 2. Roteiro de Teste Manual: Navegação Desktop

1. Inicie a aplicação localmente (`python iniciar.py` na raiz do projeto).
2. Acesse `http://localhost:8000/ajustes` e selecione a aba **Perfil & Privacidade** ou **Aparência**.
3. Altere a preferência de tela inicial para **Dashboard**.
4. Observe a barra superior de navegação:
   - A aba **Dashboard** está presente e selecionada se você estiver em `/dashboard`.
   - A aba **Livros** está visível, com ícone de livro e link para `/livros`.
5. Altere a preferência de tela inicial para **Livros**.
   - Ambas as abas continuam visíveis.
6. Clique no logotipo textual **Leitorum** no canto superior esquerdo e confirme que ele redireciona para a preferência escolhida.

---

## 3. Roteiro de Teste Manual: Offset no Mobile

1. Abra as Ferramentas do Desenvolvedor (F12) e ative a emulação de dispositivos móveis (ex.: iPhone 14 Pro ou Pixel 7, largura 390px).
2. Acesse uma página longa, como `/livros`, `/lixeira` ou `/ajustes`.
3. Role até o final da página:
   - O rodapé `.app-footer` ("Leitorum · Sobre o Leitorum · Apoie o Leitorum · Software Livre") deve ficar completamente visível acima da barra inferior de navegação.
   - Nenhuma linha de texto ou botão fica encoberta ou cortada pela `MobileTabBar`.

---

## 4. Roteiro de Teste Manual: Breadcrumbs

1. Acesse qualquer livro existente (`/livros/:bookId`).
   - O breadcrumb no topo deve exibir: `Livros / [Título do Livro]`.
   - O clique em `Livros` deve direcionar diretamente para `/livros` (e nunca para `/` ou `/dashboard`).
2. Acesse um estudo dentro deste livro (`/livros/:bookId/estudos/:studyId`).
   - O breadcrumb deve exibir: `Livros / [Título do Livro · Nome do Capítulo] / [Título do Estudo]`.
   - O clique no segundo nível deve voltar para a página do livro selecionando o capítulo respectivo.
