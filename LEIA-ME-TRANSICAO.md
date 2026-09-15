# Caderno de Leitura — transição para Antigravity + Spec Kit

Preparado em 15/09/2026. **As dez tarefas da versão 0.3 estão NÃO INICIADAS.**

Este pacote reúne contexto, regras, roadmap e prompts. A pasta de código que está no seu PC continua sendo a base do trabalho. Os documentos não comprovam que atualizações anteriores foram instaladas.

## Como usar agora

1. Extraia o ZIP na raiz da aplicação, onde ficam `iniciar.py`, `backend` e `frontend`. O ZIP cria somente a pasta `contexto-antigravity-0.3`.
2. Abra **a raiz da aplicação** no Antigravity. Último caminho informado: `C:\Users\User\caderno\caderno-leitura-0.1`. Use o caminho real caso tenha mudado.
3. Copie o conteúdo de [PRIMEIRO-PROMPT-ANTIGRAVITY.md](PRIMEIRO-PROMPT-ANTIGRAVITY.md) e envie no chat do agente.
4. O agente deve ler o contexto, comparar os arquivos de instruções existentes e integrar os documentos nos destinos abaixo. Em seguida, deve produzir uma auditoria inicial.
5. Depois de receber a auditoria, use o fluxo em [FLUXO-SPECKIT.md](docs/contexto/FLUXO-SPECKIT.md) para iniciar uma entrega delimitada. A ordem recomendada começa pelo planejamento conjunto de T09 e T10.

**Não execute os patches antigos para preparar essa transição.** O último comando informado parou em `git apply --check` com “corrupt patch …:1957”. Aquela execução não chegou à aplicação do patch, build ou migração.

## Arquivos e destinos

Todos os destinos são relativos à raiz real do projeto. Havendo arquivo no destino, o agente deve comparar e mesclar as instruções compatíveis, preservando as personalizações.

| Arquivo no pacote | Destino | Função |
| --- | --- | --- |
| `AGENTS.md` | `AGENTS.md` | Regras curtas para qualquer agente |
| `.agents/rules/caderno-leitura.md` | Mesmo caminho | Âncora de contexto do Antigravity |
| `.specify/memory/constitution.md` | Mesmo caminho | Constituição proposta para o Spec Kit |
| `docs/contexto/PROJETO.md` | Mesmo caminho | Produto, arquitetura e base de referência |
| `docs/contexto/ESTADO-E-DIAGNOSTICO.md` | Mesmo caminho | Limites das evidências e auditoria inicial |
| `docs/contexto/ROADMAP-0.3.md` | Mesmo caminho | Dez tarefas, dependências e critérios de aceite |
| `docs/contexto/AMBIENTE-E-VALIDACAO.md` | Mesmo caminho | Windows, build, testes e preservação dos dados |
| `docs/contexto/FLUXO-SPECKIT.md` | Mesmo caminho | Preparação da ferramenta e sequência de trabalho |
| `docs/contexto/RETOMADA.md` | Mesmo caminho | Registro para continuar em novas sessões |
| `PRIMEIRO-PROMPT-ANTIGRAVITY.md` | Pode permanecer no pacote | Primeiro pedido ao agente |

Este pacote contém uma constituição, mas não contém a instalação completa do Spec Kit. O agente deve conferir se o ambiente já está configurado antes de gerar templates ou skills.

## O que esperar da primeira resposta

- Raiz real do projeto e do Git identificadas.
- Python, Node.js, Spec Kit e integração disponíveis inventariados.
- Diferenças entre a base esperada e os arquivos locais registradas.
- Banco e testes localizados sem alterar o acervo.
- Relatório `docs/contexto/AUDITORIA-INICIAL.md` criado.
- Todas as linhas de T01 a T10 mantidas como **NÃO INICIADA**.

A auditoria pode encontrar código relacionado à 0.3. Isso deve ser descrito como “código encontrado, ainda não validado”; não muda o estado do roadmap.

## Ferramentas de desenvolvimento e dados pessoais

Os textos do acervo, o banco, backups, capas pessoais e credenciais não precisam ser enviados ao agente ou ao GitHub. Use exemplos fictícios em testes. O Spec Kit pode organizar especificações em um repositório local; publicar o projeto no GitHub não é requisito desta transição.
