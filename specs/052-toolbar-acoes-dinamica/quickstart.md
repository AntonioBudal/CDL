# Quickstart Validation: F 0.7.3 — Refatoração Dinâmica da Floating Actions Toolbar

**Feature**: F 0.7.3 — Refatoração Dinâmica da Floating Actions Toolbar  
**Status**: Ready for Validation  
**Artifact**: `quickstart.md`

Este guia descreve os passos práticos e comandos automatizados para verificar e homologar todas as capacidades da Feature F 0.7.3.

---

## Pré-requisitos e Ambiente

1. Frontend em execução local:
   ```powershell
   cd c:\Users\User\caderno\caderno-leitura-0.1\frontend
   npm run build
   ```
2. Suíte de testes automatizados do frontend pronta:
   ```powershell
   npm test
   ```

---

## Cenários de Validação

### Cenário 1: Aplicação de Marca-Texto em 1 Clique Direto
- **Ação:** No leitor de qualquer estudo, selecionar uma frase usando o mouse ou gesto de toque.
- **Resultado Esperado:**
  1. A barra flutuante surge com o Split Button de marca-texto exibindo a cor memorizada (amarelo como padrão).
  2. Ao clicar diretamente no ícone de marca-texto, o destaque é criado instantaneamente com **1 único clique**.
  3. A barra se fecha, a seleção é limpa e o micro-toast no topo exibe "Destaque aplicado".

---

### Cenário 2: Troca de Cor via Split Button e Persistência
- **Ação:** Selecionar um trecho de texto e clicar na pequena seta expansora ao lado do ícone de marca-texto.
- **Resultado Esperado:**
  1. A paleta rápida se expande com as 5 cores canônicas (amarelo, verde, azul, rosa, roxo).
  2. Ao clicar em "Verde", o trecho é grifado imediatamente em verde.
  3. Ao selecionar uma nova frase em seguida, o botão principal do marca-texto já exibe o verde como cor padrão.
  4. Recarregar a página (F5) e selecionar outro texto: o verde permanece como cor padrão do primeiro clique (`localStorage.getItem('caderno_last_highlight_color') === 'green'`).

---

### Cenário 3: Camada Desacoplada de Anotação com `Enter`
- **Ação:** Selecionar um trecho e clicar no botão "Anotar".
- **Resultado Esperado:**
  1. A régua de ações principal se recolhe e abre-se o popover ancorado independente (`NoteQuestionPopover.vue`).
  2. A régua não se deforma nem empurra o texto.
  3. O `<textarea>` recebe foco automático imediato (`autofocus`).
  4. Digitar o texto "Comentário importante sobre o argumento".
  5. Pressionar `Enter`: a anotação é salva imediatamente, o popover se fecha e surge o micro-toast "Anotação salva".

---

### Cenário 4: Multilinha com `Shift+Enter` e Cancelamento com `Escape`
- **Ação:** Selecionar um trecho, clicar em "Anotar", digitar uma linha e pressionar `Shift+Enter`.
- **Resultado Esperado:**
  1. O cursor quebra para uma nova linha sem disparar o salvamento.
  2. Digitar a segunda linha.
  3. Pressionar `Escape`: o popover se fecha sem salvar e a seleção é liberada.

---

### Cenário 5: Ergonomia Mobile e Proteção de Teclado Virtual
- **Ação:** Emular dispositivo móvel (largura 375px ou celular real), selecionar uma palavra com duplo toque e clicar em "Pergunta".
- **Resultado Esperado:**
  1. O formulário abre em formato de gaveta inferior (*bottom sheet*) na base da tela com botões ≥ 44×44px.
  2. Ao abrir o teclado virtual, a gaveta se reposiciona acompanhando a `window.visualViewport`.
  3. O campo de digitação e o botão "Salvar" permanecem completamente visíveis e operáveis acima do teclado virtual.

---

## Verificação Automatizada

Execute o comando de testes para validar a integridade de regressão:
```powershell
npm test
```
*Critério de Aceite:* Todos os testes passam com 0 falhas e compilação de tipos (`vue-tsc -b`) limpa.
