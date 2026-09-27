# Quickstart & Guia de Validação: F0.6.4 — Exportação com Destaques e Caderno de Revisão

**Feature Branch**: `043-exportacao-revisao`  
**Date**: 2026-09-27  

Este guia detalha o procedimento de validação automatizada e manual para a funcionalidade de exportação com destaques e geração do Caderno de Revisão (Digest).

---

## 1. Pré-Requisitos e Ambiente de Execução

- PowerShell no Windows local.
- Python 3.13 com o ambiente virtual ativo (`.venv`).
- Node.js 20+ com dependências do frontend instaladas em `caderno-leitura-0.1/frontend`.
- Variável de autenticação configurada para testes isolados: `$env:REQUIRE_AUTH="false"`.

---

## 2. Validação Automatizada (Backend & Frontend)

### Backend (Pytest)
Executar os testes de exportação e validação de destaques em banco temporário (`tmp_path`):

```powershell
cd c:\Users\User\caderno\caderno-leitura-0.1\backend
$env:REQUIRE_AUTH="false"
pytest tests/test_export.py -v
```

**Resultados Esperados**:
- Formatação de estudo individual com `include_highlights=True` insere marcações `==texto==` e notas de rodapé `[^1]`.
- Exportação em texto puro (`format=text`) gera blocos `«texto» [1]` e divisor `NOTAS DA SEÇÃO:`.
- Geração de Caderno de Revisão (`export_type="digest"`) em modo exercício oculta respostas com `_______` e gera seção de `Gabarito de Revisão`.
- Caderno de Revisão no modo estudo (`exercise_mode=False`) exibe respostas diretamente no enunciado.
- Exportação de livro com estudos múltiplos consolida todos os itens sem colisão de identificadores.

### Frontend (Vitest & Build)
Validar os componentes de interface (`ExportModal.vue`) e compilação do Vite:

```powershell
cd c:\Users\User\caderno\caderno-leitura-0.1\frontend
npm test
npm run build
```

**Resultados Esperados**:
- Testes unitários do modal de exportação aprovados com 100% de sucesso.
- `npm run build` conclui com código 0 e sem erros de TypeScript (`vue-tsc --noEmit`).

---

## 3. Roteiro de Validação Manual Ponta a Ponta

### Cenário A: Exportação de Estudo com Destaques
1. Inicie a aplicação localmente:
   ```powershell
   cd c:\Users\User\caderno\caderno-leitura-0.1
   python iniciar.py
   ```
2. Abra o Leitorum em `http://localhost:8000` (ou porta indicada).
3. Navegue até um estudo existente com grifos e notas cadastrados (ou crie um destaque com pergunta via Leitura Ativa).
4. Clique no botão de exportação do estudo (ícone de download no topo).
5. No modal:
   - Mantenha selecionado "Documento Completo".
   - Certifique-se de que a opção "Incluir destaques e anotações no texto" está marcada.
   - Selecione formato "Markdown (.md)".
   - Clique em "Baixar arquivo".
6. Abra o arquivo `.md` baixado em um editor de texto ou Obsidian e confirme que os grifos aparecem com marcas `==...==` e as anotações aparecem nas notas de rodapé `[^N]` no final de cada seção.

### Cenário B: Geração do Caderno de Revisão (Modo Exercício)
1. No mesmo estudo ou na página principal do Livro, abra o diálogo de exportação.
2. Selecione a opção **"Caderno de Revisão (Digest)"**.
3. Marque a opção **"Modo Exercício (Ocultar respostas com gabarito no final)"**.
4. Clique em "Baixar arquivo".
5. Abra o documento baixado:
   - Verifique que as perguntas trazem linhas para resposta manuscrita (`Resposta: ________________________________`).
   - Verifique que os trechos ocluídos trazem `[ _______ ]`.
   - Role até o final do documento e confirme a presença da seção **"Gabarito de Revisão"** contendo as respostas originais.

### Cenário C: Caderno de Revisão (Modo Estudo)
1. Repita o Cenário B, desmarcando o "Modo Exercício".
2. Verifique que as respostas aparecem logo abaixo de cada pergunta e os termos ocluídos aparecem grifados diretamente no fluxo textual.

---

## 4. Verificação de Integridade e Isolamento

- Execute o checklist pós-validação:
  1. O arquivo `backend/data/caderno.db` não sofreu nenhuma alteração estrutural nem alteração de timestamp indevida decorrente da exportação.
  2. Nenhuma menção a dados sensíveis de teste foi versionada no repositório.
  3. Nenhum emoji informal foi inserido no código-fonte de `frontend/src`.
