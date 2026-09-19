# Quickstart & Validation Guide: Central de Ajustes com Preview ao Vivo

**Feature Branch**: `014-central-ajustes-preview`  
**Date**: 2026-09-19  

Este guia orienta a validação ponta a ponta dos novos recursos implementados na tela de Ajustes.

---

## 1. Pré-requisitos e Execução do Ambiente

Certifique-se de estar no diretório raiz do projeto ou em `caderno-leitura-0.1`:
```powershell
cd c:\Users\User\caderno\caderno-leitura-0.1
```

Executar os testes automatizados do frontend:
```powershell
npm test
```

Executar a verificação de compilação e tipagem:
```powershell
npm run build
```

---

## 2. Roteiro de Validação Manual

### Cenário 1: Navegação Estrutural em Três Abas
1. Abra a aplicação no navegador em `http://localhost:8000/ajustes` (ou ambiente Vite `http://localhost:5173/ajustes`).
2. Observe a barra de abas no topo da seção de Ajustes com três opções: **Aparência**, **Leitura** e **Sistema**.
3. Pressione a tecla `Tab` até focar na barra de abas e use as setas `Direita` e `Esquerda` para alternar entre as abas.
4. Verifique que a troca ocorre instantaneamente sem rolagem indesejada nem recarregamento da página.

### Cenário 2: Amostra Interativa e Preview ao Vivo (Layout 2 Colunas)
1. No computador em janela ampla (> 1024px), confirme que a página exibe duas colunas: controles à esquerda e o painel de amostra à direita.
2. Na aba **Aparência**, selecione o tema "Pergaminho", superclasse "Mecânica" e intensidade "Alta".
3. Observe que o painel de amostra à direita atualiza imediatamente (< 50ms) suas cores, bordas sólidas e estética tátil.
4. Role a página para baixo e verifique que o painel de preview acompanha a visão (*sticky*).
5. Na aba **Leitura**, troque a fonte para "EB Garamond" e aumente o tamanho para "130%".
6. Clique nas abas dentro da própria amostra (Resumo, Explicação, Conceitos, Referências) e observe o texto destacado `==marcação==`.
7. Alterne a opção "Disposição dos livros" entre Grade e Lista; verifique que o cartão na prévia se adapta entre modo capa/grade e modo lista.

### Cenário 3: Central Completa de Diagnóstico (Aba Sistema)
1. Clique na aba **Sistema**.
2. Verifique o bloco de informativo de escopo: nota esclarecendo que preferências visuais são salvas no navegador local (`localStorage`), enquanto o acervo reside no banco de dados SQLite.
3. Observe a checagem automática de conexão: status da API local (`/api/health`), versão e atalho para `/conexao`.
4. Observe as métricas de armazenamento local: quantidade de chaves salvas e tamanho estimado em KB.
5. Clique no botão "Restaurar Padrões de Aparência":
   - Um diálogo modal acessível de confirmação deve se abrir.
   - Pressione `Esc` ou clique em "Cancelar" para fechar sem alterar nada.
   - Abra novamente e confirme a restauração.
   - Verifique que o tema retorna imediatamente para "Porcelana", a fonte para "Inter" e o painel de amostra reflete o estado inicial de fábrica.
6. Na mesma aba, confira o painel de Backup do Banco (`DatabaseBackup.vue`), pronto para download do acervo em `.db`.

### Cenário 4: Precedência de E-Ink e Acessibilidade
1. Na aba **Aparência**, selecione o tema "E-Ink".
2. Observe que os seletores de cor de destaque e intensidade são bloqueados/desativados com aviso explicativo.
3. A amostra renderiza-se estritamente em escala de cinza e alto contraste.
4. Redimensione a janela do navegador para largura menor ou modo móvel (<= 768px):
   - O layout colapsa perfeitamente para 1 coluna vertical.
   - Os alvos de toque mantêm altura mínima acessível de 44px.
