# Quickstart: F0.8.01 — Curadoria Editorial, Biblioteca Ativa e Novo Header Global

## Validação Rápida da Funcionalidade

Este guia orienta a verificação das entregas da Feature 01: o novo Header Global em 3 blocos e o redesign da página de Livros com Drawer acessível.

---

### 1. Novo Header Global

1. Acesse o sistema autenticado (ex.: `/livros` ou `/dashboard`).
2. Observe o topo da aplicação:
   - **Bloco Esquerdo**: Logo `Leitorum`.
   - **Bloco Central**: Apenas as 4 abas primárias (`Livros`, `Destaques`, `Revisão`, `Inbox`) + botão `Mais ▾`.
   - **Bloco Direito**: Botões de busca (`Ctrl K`), captura rápida (`Ctrl+Shift+C`), badge de sincronização, notificações e avatar do usuário.
3. Clique em **Mais ▾**:
   - O menu suspenso deve abrir suavemente, exibindo `Importar`, `Amigos`, `Ajustes`, `Lixeira` (e `Administração` se for admin).
   - O foco deve ser gerenciável pelo teclado e fechar com tecla `Esc` ou clique fora.
4. Clique no **Avatar do Usuário**:
   - O menu do usuário deve abrir, exibindo o perfil e, obrigatoriamente, o botão **Sair**.
   - Confirme que o botão solto "Sair" não existe mais no plano superior do header.

---

### 2. Biblioteca Ativa e Drawer de Cadastro

1. Acesse a rota `/livros`:
   - A biblioteca agora ocupa 100% da largura útil da tela (sem coluna lateral fixa).
   - O topo exibe o card **"Em Andamento"** com a obra mais recente e atalho para leitura.
2. Clique no botão **+ Adicionar Livro**:
   - A gaveta lateral deslizante (`Drawer`) deve surgir a partir da direita em 220ms com backdrop escuro.
   - O foco do teclado entra automaticamente no campo de título.
3. Pressione a tecla `Esc`:
   - O Drawer fecha imediatamente e o foco retorna ao botão disparador.
4. Reabra o Drawer, preencha o título e autor e clique em **Cadastrar livro**:
   - O livro é salvo via API e a navegação ocorre para os detalhes do livro cadastrado sem erros.
5. Alterne entre os modos **Grade** e **Lista**:
   - A transição visual é fluida e os cartões de livro possuem elevação sutil no hover.

---

### 3. Execução Automatizada dos Testes

No diretório `caderno-leitura-0.1/frontend`:
```bash
npm test
npm run build
```
Ambos os comandos devem concluir com 100% de sucesso.
