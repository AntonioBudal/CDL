# Quickstart & Guia de Validação: 007 — Zero-G

**Feature**: 007 — Zero-G: Superclasse Flutuante & Magnética  
**Branch**: `007-zero-g-flutuante`  
**Date**: 2026-09-19  

---

## 1. Pré-requisitos & Ambiente de Testes

- Node.js >= 24
- Navegador moderno com suporte a CSS Transforms e Pointer Events.
- Repositório em `c:\Users\User\caderno\caderno-leitura-0.1`.

---

## 2. Validação Automatizada (Suíte de Testes e Tipos)

Execute os comandos a seguir a partir do diretório `frontend`:

```powershell
cd c:\Users\User\caderno\caderno-leitura-0.1\frontend

# 1. Execução da suíte de testes unitários do frontend
npm test

# 2. Verificação estrita de tipagem TypeScript e build de produção
npm run build
```

**Resultado Esperado**:
- Todos os testes passam com 0 falhas (`pass N, fail 0`).
- `vue-tsc -b` conclui sem erros de compilação de tipos.
- `vite build` gera os pacotes em `dist/` com sucesso.

---

## 3. Validação Funcional Ponta a Ponta (Manual)

Inicie o servidor local para inspeção interativa:

```powershell
cd c:\Users\User\caderno\caderno-leitura-0.1
.\backend\.venv\Scripts\python.exe iniciar.py
```
Acesse `http://127.0.0.1:8000` no navegador.

### Cenário 1: Ativação da Superclasse Zero-G no Painel de Ajustes
1. Clique no ícone de **Configurações** (Ajustes).
2. Localize a nova seção **11. Superclasse de Interface**.
3. Selecione a opção **Zero-G — Flutuante & Magnética** no campo *Superclasse*.
4. **Verificação**:
   - O elemento `<html>` recebe imediatamente o atributo `data-superclass="zero-g"`.
   - Recarregar a página (F5) preserva a seleção intacta (persistida no `localStorage`).

---

### Cenário 2: Respiração de Repouso (*Idle Breathing*) no Acervo
1. Navegue para a tela inicial / acervo (`/books`).
2. Observe os cartões de livros em repouso sem mover o mouse.
3. **Verificação**:
   - Os cartões realizam uma oscilação vertical suave e lenta (ciclo de ~5.4 segundos, subindo aproximadamente 1px).
   - Cartões vizinhos possuem defasagem temporal de fase (não sobem nem descem todos juntos no mesmo milissegundo).

---

### Cenário 3: Atração Magnética de Cursor e Retorno Elástico
1. Mova o cursor do mouse lentamente sobre a área de um cartão de livro.
2. **Verificação**:
   - O cartão é atraído sutilmente em direção à posição do ponteiro (deslocamento máximo de 4px na intensidade padrão).
   - Ao mover o cursor para fora dos limites do cartão, ele retorna suavemente à sua posição inicial com amortecimento elástico gracioso (`cubic-bezier(0.16, 1, 0.3, 1)`), sem saltos secos.

---

### Cenário 4: Escalonamento Paramétrico de Intensidade
1. Em Configurações, altere *Intensidade da física* para:
   - **Sutil (0.5x)**: Retorne ao acervo e verifique que a atração magnética e a oscilação de repouso diminuem pela metade (~2px máx de atração).
   - **Alta (1.5x)**: Verifique que o deslocamento magnético amplia proporcionalmente (~6px máx).
   - **Desativada (0.0x)**: Verifique que todo movimento e atração cessam imediatamente, mantendo apenas a geometria estática.

---

### Cenário 5: Imobilidade e Conforto no Modo de Leitura
1. Clique em um livro e abra a tela de leitura de um capítulo ou anotação de estudo.
2. Mova o cursor do mouse sobre o texto corrido, parágrafos e citações.
3. **Verificação**:
   - O texto de leitura permanece 100% estático e imóvel.
   - Nenhuma oscilação, translação ou efeito magnético atinge os blocos textuais.

---

### Cenário 6: Redução de Movimento (*Acessibilidade*)
1. Em Configurações, selecione no campo *Transições* (Grupo 5) a opção **Desativadas**.
2. **Verificação**:
   - Todas as animações e translações de Zero-G cessam imediatamente em toda a aplicação.
   - O mesmo comportamento de neutralização ocorre se o sistema operacional estiver com *prefers-reduced-motion* ativado.
