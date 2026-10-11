# Quickstart & Validation Guide: F0.8.02 — Destaques: Códice e Margens Vivas

**Feature**: `067-destaques-codice-margens` | **Date**: 2026-10-11 | **Status**: Complete

---

## 1. Pré-Requisitos e Ambiente

A validação desta funcionalidade é executada no ambiente Windows local sem afetar o banco ativo (`backend/data/caderno.db`), em estrita conformidade com a Constituição do Projeto.

### Pré-requisitos
- Node.js $\ge 20$ e npm instalados
- Python 3.13 de 64 bits com ambiente virtual ativado
- Diretório de trabalho: `caderno-leitura-0.1/`

---

## 2. Roteiro de Validação Automatizada

### Passo 1: Execução da Suíte de Testes do Frontend
Executa todos os testes unitários e de integração, incluindo os testes dedicados da Feature 02:
```powershell
cd caderno-leitura-0.1\frontend
npm test
```
**Resultado Esperado:** 100% dos testes passando sem falhas.

### Passo 2: Verificação de Tipagem e Build de Produção
Garante que os contratos TypeScript e a compilação Vite estão estritamente corretos:
```powershell
cd caderno-leitura-0.1\frontend
npm run build
```
**Resultado Esperado:** `vue-tsc -b` conclui com 0 erros e o build de produção é gerado em `dist/`.

### Passo 3: Execução da Suíte de Backend
Garante que nenhuma regressão de API foi introduzida no servidor:
```powershell
cd caderno-leitura-0.1
pytest backend/tests
```
**Resultado Esperado:** 420+ testes passando (zero falhas).

---

## 3. Roteiro de Validação Visual e Interativa (End-to-End)

Para validar a experiência de uso no navegador:

### 1. Inicialização do Servidor Local
```powershell
cd caderno-leitura-0.1
python iniciar.py
```
Acesse `http://localhost:8000/destaques` no navegador.

### 2. Cenário 1: Inspeção da Ficha Literária e Tipografia Editorial
1. Acesse a rota `/destaques`.
2. Observe que cada destaque surge como uma ficha literária com a citação do livro em tipografia serifada de alta legibilidade (`--font-serif`), acompanhada de aspas clássicas.
3. Se o destaque possuir uma nota de estudo, verifique que esta é exibida em bloco separado com fundo suave e tipografia legível.
4. Confira no rodapé da ficha o título da obra, capítulo e data da criação do grifo.

### 3. Cenário 2: Categorias Semânticas de Grifo nos Filtros
1. Na barra de filtros superior, inspecione os botões de cores.
2. Verifique que cada cor exibe seu rótulo intelectual correspondente (ex.: *Ideia Central*, *Citação-chave*, *Dúvida*, *Refutação*, *Síntese*) e a contagem de destaques associados.
3. Clique em "Ideia Central" (Amarelo): confirme que apenas os destaques correspondentes são listados e a URL é atualizada para `?color=yellow`.
4. Combine o filtro de cor com uma busca textual na barra e valide a filtragem reativa instantânea.

### 4. Cenário 3: Cópia de Citação em Múltiplos Formatos com Microfeedback
1. Passe o mouse sobre uma ficha literária e clique na ação de cópia rápida.
2. Verifique que o ícone do botão transiciona para confirmação (*check*) e um toast flutuante surge informando `"Copiado para a área de transferência"`.
3. Aguarde 1,5 segundo e confirme que a mensagem flutuante se dissolve suavemente.
4. Cole o conteúdo em um editor de texto e valide se a citação está formatada com a referência bibliográfica da obra.

### 5. Cenário 4: Expansão Suave de Contexto
1. Localize uma passagem com texto longo (> 260 caracteres).
2. Verifique o truncamento visual com botão "Expandir contexto".
3. Clique no botão e confirme a animação de abertura suave ($\le 180$ms).
4. Clique em "Ver menos" e confirme o retorno harmonioso.

### 6. Cenário 5: Estado de Erro Temático e Nova Tentativa (*Retry*)
1. Abra as ferramentas do desenvolvedor (F12) e simule desconexão na aba de rede (*Offline*).
2. Tente aplicar um filtro ou recarregar a busca.
3. Verifique que a tela renderiza o componente de erro nos tons nativos do tema ativo (sem nenhum banner vermelho rígido).
4. Reative a rede e clique em "Tentar novamente": confirme que a lista de destaques é recarregada com sucesso.
