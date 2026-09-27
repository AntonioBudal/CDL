# Quickstart: Validação e Testes da Feature 9.5

Este guia descreve os passos práticos para verificar e comprovar todas as entregas da Feature 9.5.

---

## 1. Verificação Automática (Suítes de Testes)

Execute a suíte de testes de sistema visual e componentes do frontend:

```bash
cd caderno-leitura-0.1/frontend
npm test
```

Verifique a tipagem estrita do TypeScript e build do Vite:

```bash
cd caderno-leitura-0.1/frontend
npm run build
```

Execute a suíte do backend para garantir que nenhuma regressão de endpoints de preferências ocorreu:

```bash
cd caderno-leitura-0.1
python -m pytest backend/tests/test_preferences.py
```

---

## 2. Roteiro de Validação Manual

### Cenário 1: Persistência no F5 e Troca de Rotas (US1)
1. Inicie a aplicação: `python iniciar.py`.
2. Acesse `http://localhost:8000/ajustes`.
3. Selecione o tema **"Nord"** (ou **"Noite Suave"**).
4. Verifique a aplicação imediata do tema escuro.
5. Pressione **F5** (recarregar página): a tela não deve piscar e o tema selecionado deve permanecer ativo.
6. Navegue para a página inicial (`/`), abra um livro (`/livro/1`) e volte para `/ajustes`: o tema deve continuar inalterado.

### Cenário 2: Catálogo de 10 Temas e Nomenclatura Simplificada (US2)
1. Acesse `http://localhost:8000/ajustes`.
2. Abra o seletor de Temas e conte as opções disponíveis: exatamente **10 temas**.
3. Confirme a ausência dos 5 temas excluídos: `Porcelana`, `Breu`, `Vinil`, `Sequoia` e `Véspera`.
4. Teste a ativação dos 5 novos temas minimalistas:
   - `Papel Fosco`: Fundo off-white suave (`#f5f5f5`), texto cinza chumbo (`#333333`).
   - `Noite Suave`: Fundo cinza escuro azulado (`#1e1e24`), texto cinza claro (`#d4d4d4`).
   - `Cinza Neutro`: Fundo cinza puro (`#e8e8e8`), texto cinza escuro (`#2b2b2b`).
   - `Grafite`: Fundo grafite escuro (`#222222`), texto cinza suave (`#cccccc`).
   - `Monocromático`: Fundo branco puro (`#ffffff`), texto preto (`#111111`).
5. Confirme a simplificação dos temas preservados: `Sépia`, `E-Ink`, `Solarized`, `Nord`, `Cyber`.

### Cenário 3: Ícone do Botão "Compartilhar" (US3)
1. Acesse qualquer estudo cadastrado (ex.: `/estudos/1`).
2. Localize o botão **"Compartilhar"** no cabeçalho de ações.
3. Inspecione visualmente: o ícone deve estar perfeitamente proporcional (`1.2em`) e a palavra "Compartilhar" deve estar em uma linha única e legível, sem quebras verticais.

### Cenário 4: Ícone do Estado Vazio em "Estudos Compartilhados" (US3)
1. Acesse a aba "Compartilhados Comigo" na Biblioteca (`/` ou `/livros`).
2. Se não houver itens compartilhados, observe a ilustração central: deve estar delimitada a um tamanho elegante (`max-width: 120px`), sem tomar a tela inteira.

### Cenário 5: Modal "Exportar Estudo" (US3 & US4)
1. Em qualquer tela de estudo, clique em **"Exportar estudo"**.
2. Sob tema escuro (ex.: `Noite Suave` ou `Nord`), verifique:
   - Os títulos e descrições dos formatos e conteúdos estão nítidos e perfeitamente legíveis.
   - Os seletores (rádios e checkboxes) possuem tamanho padronizado (24px) e estão alinhados sem sobrepor os textos.

### Cenário 6: Contraste do Acordeão de Agrupamento (US4)
1. Acesse a visão agrupada de estudos (por status, categoria ou capítulo).
2. Observe os cabeçalhos colapsáveis dos grupos (`.group-toggle-btn`): o título e a seta de chevron devem apresentar alto contraste em relação ao fundo em todos os temas.
