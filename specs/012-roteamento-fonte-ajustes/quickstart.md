# Quickstart: Validação da Feature 012 (Roteamento, Fonte Global e Ajustes Limpos)

**Feature**: `012-roteamento-fonte-ajustes`  
**Date**: 2026-09-19  
**Status**: Ready for Implementation  

---

## 1. Cenário 1: Navegação Client-Side entre Todas as Abas sem Tela Vazia

**Objetivo:** Comprovar que a transição entre abas ocorre de forma atômica e fluida, sem tela branca ou necessidade de recarregar (F5).

1. Abra a aplicação no navegador em `http://localhost:8000/`.
2. Clique no menu superior em **"Importar"** (`/importar`).
   - *Resultado esperado*: A tela de importação monta imediatamente com animação de transição suave. Nenhum frame de tela branca ou vazia.
3. Clique em **"Ajustes"** (`/ajustes`).
   - *Resultado esperado*: A tela de Ajustes é montada e renderizada instantaneamente.
4. Clique em **"Lixeira"** (`/lixeira`).
   - *Resultado esperado*: A tela da Lixeira carrega seus dados e exibe a lista/estado vazio imediatamente.
5. Clique em **"Meus livros"** (`/`).
   - *Resultado esperado*: A biblioteca de livros reaparece perfeitamente sem necessidade de F5.

---

## 2. Cenário 2: Alternância de Capítulos via Query String (`?chapter=...`)

**Objetivo:** Validar que a chave `:key="$route.fullPath"` remonta e reage a parâmetros de query sem travar.

1. Clique em um livro do acervo para abrir o detalhe (`/livros/1`).
2. Clique em diferentes capítulos na barra lateral ou nos controles do livro.
3. Observe a URL mudando para `/livros/1?chapter=2`, `/livros/1?chapter=3`.
   - *Resultado esperado*: Os estudos do capítulo correspondente são carregados de forma reativa e precisa, sem travar o componente ou desincronizar o estado.

---

## 3. Cenário 3: Herança Global Imediata da Fonte Selecionada

**Objetivo:** Comprovar que alterar a fonte altera 100% dos elementos da interface em tempo real.

1. Navegue até a tela de **Ajustes** (`/ajustes`).
2. No grupo **"3. Leitura"**, abra o seletor **"Fonte de leitura"**.
3. Selecione uma fonte serifada distinta (ex.: **"EB Garamond"** ou **"Literata"**).
   - *Resultado esperado*: O cabeçalho global ("Caderno de Leitura"), os botões, os selects, as legendas dos grupos e o próprio card de preview assumem imediatamente a tipografia da fonte escolhida (em < 50ms).
4. Selecione uma fonte sans-serif (ex.: **"Fira Sans"**) ou dyslexic (**"OpenDyslexic"**).
   - *Resultado esperado*: Toda a interface se adapta instantaneamente à nova fonte sem necessidade de recarregar a página.

---

## 4. Cenário 4: Inspeção das 7 Seções Numeradas no Painel de Ajustes

**Objetivo:** Verificar a poda dos 3 controles obsoletos e a numeração sequencial de 1 a 7.

1. Abra o painel de **Ajustes** (`/ajustes`).
2. Conte e inspecione as seções exibidas:
   - *Aparência básica*: Tema
   - *1. Cor de destaque*
   - *2. Densidade*
   - *3. Leitura* (Fonte, Tamanho, Alinhamento)
   - *4. Marcação*
   - *5. Acervo*
   - *6. Largura da interface*
   - *7. Superclasse de Interface* (Superclasse, Intensidade da física)
3. Confirme a **ausência total** das seções:
   - "Movimento" (removido)
   - "Botões" (removido)
   - "Abas" (removido)

---

## 5. Cenário 5: Purga Automática de Chaves Obsoletas no `localStorage`

**Objetivo:** Garantir higienização segura de dados de versões anteriores.

1. No console do desenvolvedor do navegador, force a gravação de preferências legadas:
   ```javascript
   localStorage.setItem('caderno.aparencia.v2', JSON.stringify({
     theme: 'breu',
     motion: 'on',
     'button-width': 'block',
     tabs: 'segmented',
     superclass: 'monolitica'
   }));
   ```
2. Recarregue a página ou invoque `window.cadernoAppearance.get()`.
3. Verifique o conteúdo de `localStorage.getItem('caderno.aparencia.v2')`:
   - *Resultado esperado*: O JSON gravado NÃO contém mais as chaves `motion`, `button-width` ou `tabs`. O tema permanece `breu` e a superclasse permanece `monolitica`.
   - O elemento `<html>` não possui atributos `data-motion`, `data-button-width` ou `data-tabs`.
