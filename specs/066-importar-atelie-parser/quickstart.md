# Quickstart: 066-importar-atelie-parser

## Execução Local

```bash
# Executar a suíte de testes do frontend
cd caderno-leitura-0.1/frontend
npm test

# Compilação e checagem de tipos
npm run build

# Validação do backend
cd ../backend
python -m pytest
```

## Cenários de Teste Manual

1. **Acesso à Rota**: Navegar até `/importar` pelo menu retrátil "Mais ▾" no Header ou diretamente pela URL.
2. **Faixa Compacta**: Selecionar Livro e Capítulo na barra superior.
3. **Colagem de Texto e Preview**: Colar texto formatado com seções (ex.: `# Resumo... # Explicação...`) no editor e verificar preenchimento das 4 seções no painel direito.
4. **Barra Flutuante**: Selecionar uma palavra com o mouse ou cursor e testar a aplicação de formatação (`Ctrl+B`, `Ctrl+I`).
5. **Modos de Foco**: Alternar entre `Dividido`, `Apenas Fonte` e `Apenas Prévia`.
6. **Responsividade**: Redimensionar a janela para menos de 1024px e testar a navegação por abas segmentadas.
