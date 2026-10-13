# Prompt para o Antigravity — tela placeholder do Document Intelligence

* **Preparado por:** Claude Code (subprojeto `document-intelligence/`), em 2026-10-11
* **Uso:** colar o bloco abaixo no Antigravity. Ele pede **só a especificação** (`speckit.specify`); plano, tarefas e
  implementação ficam para depois da sua revisão.
* **Estado em que foi escrito:** EXP-000 a EXP-003 concluídos; ADR-001 e ADR-002 aceitos; ADR-003 proposto.

---

```text
Contexto

O repositório tem um subprojeto separado, `document-intelligence/`, mantido por outro agente (Claude Code). Ele
pesquisa como transformar fotos de páginas de caderno manuscrito em texto estruturado para o Caderno de Leitura.
Esse subprojeto ainda está em fase de experimentos: não existe serviço rodando, nem API, nem modelo adotado.

Quero reservar desde já o lugar dessa funcionalidade no produto, com uma tela placeholder honesta.

Sua tarefa agora

Rodar apenas a etapa de especificação do Spec Kit (speckit.specify) para uma feature de frontend:
"tela placeholder do Document Intelligence". Entregue só o spec.md e pare para a minha revisão.
Não escreva plan.md, tasks.md nem código nesta rodada. Confira o próximo número livre em `specs/`
(o último que vi foi 068) e siga a convenção de nomes já usada.

O que a tela deve ser

1. Uma rota nova e autenticada no frontend (sugestão: `/digitalizar`, título "Digitalizar caderno"; proponha
   alternativas de nome e caminho na spec) com um ponto de entrada visível na navegação. Proponha onde esse ponto
   de entrada fica melhor (aba própria, item dentro de "Importar", ou cartão na Caixa de Entrada) e deixe a
   escolha como pergunta para mim.
2. Conteúdo estático que explique, em linguagem de leitor:
   - o que a funcionalidade vai fazer: fotografar uma página do caderno e recebê-la como estudo estruturado,
     com o texto, os blocos (título, parágrafos, notas de margem, diagramas) e a ordem de leitura;
   - que tudo será processado localmente, no próprio computador, sem enviar imagens a serviços externos;
   - que a funcionalidade está "em pesquisa" e ainda não está disponível. Não prometa data.
3. Um indicador de estado simples e verdadeiro, por etapa, com estes valores fixos (texto, não dados dinâmicos):
   - Localizar linhas e blocos na página: em validação (funciona em páginas sintéticas; falta testar em fotos reais)
   - Ordem de leitura: em validação
   - Transcrição do texto manuscrito em português: em pesquisa (ainda não há modelo que leia português)
   - Classificação do conteúdo e diagramas: não iniciado
4. Um caminho de saída útil: links para o que já funciona hoje e resolve a mesma necessidade ("Importar
   fichamento" e "Caixa de Entrada").

Restrições inegociáveis

- Somente frontend. Nenhuma mudança em backend, banco, migrações ou modelos SQLAlchemy.
- Nenhum upload, câmera, seletor de arquivo ou envio de imagem. A tela não coleta nem guarda nada.
- Nenhuma chamada de rede para o Document Intelligence. Não existe serviço para chamar.
- Nenhum resultado simulado que pareça real. Se houver ilustração de exemplo, ela deve ser claramente rotulada
  como ilustração e usar texto fictício (nada do acervo do usuário).
- Não implemente OCR, HTR, visão computacional nem leitura do formato LDF no frontend ou no backend. Isso é
  escopo exclusivo de `document-intelligence/`.
- Não altere nenhum arquivo dentro de `document-intelligence/`.
- Sem dependências novas.
- Não acople a tela aos rascunhos `document-intelligence/docs/ldf.md` e `document-intelligence/docs/api-local.md`:
  os dois estão em rascunho e têm lacunas conhecidas (por exemplo, o formato ainda não guarda a região de um
  diagrama, e o modelo Python diverge do JSON Schema). O contrato será fechado em decisão própria.

Requisitos de qualidade a cobrir na spec

- Mesmos padrões das telas atuais: temas e paletas existentes, tipografia, navegação móvel e de desktop,
  título e metadados da rota, acessibilidade (títulos hierárquicos, foco, contraste, leitor de tela).
- Comportamento sem JavaScript de rede: a tela renderiza igual offline.
- Critérios de aceite verificáveis e testes automatizados no padrão do projeto (`npm test`, `npm run build`).
- Pensar na evolução: a spec deve dizer como esta tela será substituída ou ampliada quando existir um primeiro
  teste real (provavelmente uma pré-visualização de layout, sem texto, restrita a quem administra a instância).
  Só descrever; não implementar.

Perguntas que quero ver na spec para eu decidir

1. Nome da funcionalidade para o leitor e caminho da rota.
2. Onde fica o ponto de entrada na navegação.
3. Visível para todos os usuários autenticados ou só para o administrador da instância nesta fase.
4. Se a tela mostra o indicador de estado por etapa (item 3) ou só a mensagem "em breve".

Lembretes de governança

- Siga `AGENTS.md` da raiz e as regras do workspace: privacidade do acervo, Spec Kit um passo de cada vez,
  mensagens de commit em português, um commit por feature, e só depois de `npm test`, `pytest` e `npm run build`.
- Esta feature não faz parte das F01 a F10 do roadmap 0.5 e não muda o estado de nenhuma delas.
```

---

## Notas para quem for revisar a spec do Antigravity

* **Atualização de 2026-10-12:** as lacunas do formato citadas no prompt (região de diagrama, modelo Python
  divergente do JSON Schema) foram fechadas no **LDF 2.0** — `document-intelligence/docs/ldf.md`, ADR-004
  (`PROPOSED`). A restrição de não acoplar a tela ao formato continua valendo: ainda não há serviço para chamar.

* Os quatro estados do indicador (item 3 do prompt) refletem os resultados aceitos até aqui: ADR-001 (nenhum
  reconhecedor pronto lê português manuscrito), ADR-002 (linhas e blocos funcionam em páginas sintéticas, sem
  validação em fotos reais) e EXP-003 (ordem de leitura boa com layout exato; de ponta a ponta ainda abaixo da
  meta). Se algum ADR mudar, o texto da tela precisa acompanhar.
* A tela não deve citar nomes de modelos nem números de experimento: são detalhes de pesquisa e mudam.
* Quando houver um primeiro teste real no site, a integração passa pelo backend do Leitorum falando com um
  serviço local do Document Intelligence; nada disso existe hoje e nada disso entra nesta feature.
