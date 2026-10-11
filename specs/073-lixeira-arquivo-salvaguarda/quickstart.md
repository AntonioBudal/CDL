# Roteiro de Validação Rápida: Lixeira — Arquivo de Salvaguarda e Segurança

Este roteiro descreve os cenários de validação automatizada e manual para comprovar o funcionamento de ponta a ponta da Feature F0.8.8.

---

## 1. Pré-requisitos e Ambiente

- Node.js instalado e dependências do frontend instaladas (`caderno-leitura-0.1/frontend/node_modules`).
- Ambiente Python com dependências do backend instaladas para suíte de testes.
- Banco de dados de teste descartável (nunca tocar no banco ativo `caderno.db`).

---

## 2. Cenários de Validação Automatizada

### 2.1 Testes Unitários e de Componente (Frontend)
Criar e executar a suíte `frontend/tests/feature-073-lixeira-salvaguarda.test.mjs`:

```powershell
cd caderno-leitura-0.1/frontend
node --test tests/feature-073-lixeira-salvaguarda.test.mjs
```

Cenários cobertos pela suíte:
1. **Renderização de Indicador de Retenção e Badges**:
   - Valida cálculo dos dias restantes, barra de progresso proporcional e classe de urgência para `days_until_purge <= 5`.
2. **Caixas de Seleção e Barra Flutuante**:
   - Valida que ao marcar 1 item a barra flutuante é exibida com a contagem "1 item selecionado".
   - Valida alternância "Selecionar todos" / "Desmarcar todos" por aba.
3. **Segurança de Esvaziamento e Exclusão**:
   - Valida que o botão "Esvaziar lixeira" abre `TrashConfirmModal` com `role="alertdialog"` e foco no botão cancelar.
4. **Animação e Feedback de Restauração**:
   - Valida aplicação da classe `.is-restoring` durante o processo de restauração e emissão do toast informativo.
5. **Acessibilidade por Teclado e Zero Emojis**:
   - Valida suporte a Escape para fechar modal e ausência total de emojis na interface.

### 2.2 Suítes Globais de Regressão
Executar as verificações de conformidade e build:

```powershell
cd caderno-leitura-0.1/frontend
npm test
npm run build
```

E no backend:
```powershell
cd caderno-leitura-0.1
pytest backend/tests
```

---

## 3. Roteiro de Validação Manual na Interface

1. **Acesso à Lixeira**:
   - Navegue para `/lixeira` com a aplicação em execução (`python iniciar.py`).
   - Observe a divisão por abas: `Todos (X)`, `Livros (Y)` e `Estudos individuais (Z)`.
2. **Avaliação dos Cartões**:
   - Verifique os cartões de Livro e Estudo com a indicação visual de tipo.
   - Verifique o badge de retenção com o ícone de relógio e a barra de progresso sutil na base. Itens com $\le 5$ dias restantes devem ter destaque avermelhado de urgência.
3. **Seleção Múltipla e Barra Flutuante**:
   - Marque a caixa de seleção de um livro e de um estudo.
   - Observe a barra de ações em lote surgindo na base da tela com o texto "2 itens selecionados".
   - Clique em "Restaurar selecionados" e observe a saída suave de ambos os itens e a notificação de confirmação.
4. **Segurança no Esvaziamento Total**:
   - Clique no botão "Esvaziar lixeira" no topo da página.
   - Observe o modal de confirmação aberto, com o foco posicionado no botão "Cancelar".
   - Pressione `Escape` e verifique que o diálogo fecha sem alterar nenhum registro.
   - Abra novamente e confirme a ação: verifique que a lixeira esvazia e exibe o estado vazio amigável.
