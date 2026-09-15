# Transição para GitHub Spec Kit e Antigravity

Guia consultado em 2026-09-15. As instruções locais da ferramenta instalada prevalecem sobre exemplos incompatíveis com sua versão.

A primeira rodada integra contexto e faz auditoria. As dez tarefas da 0.3 permanecem NÃO INICIADAS; não executar a operação de implementação nessa rodada.

## 1. Aproveitar o ambiente existente

No PowerShell da raiz da aplicação, verificar o que está disponível:

~~~powershell
Get-Command specify -ErrorAction SilentlyContinue
Get-Command uv -ErrorAction SilentlyContinue
Test-Path -LiteralPath '.\.specify'
~~~

Se `specify` estiver disponível, consultar um comando por vez:

~~~powershell
specify version
specify init --help
specify integration list
~~~

Dentro de projeto já inicializado, `specify integration status` inspeciona a integração. A chave atual do Antigravity é **`agy`**, com instalação de skills. Se a instalação local diferir, consultar seu help antes de escolher comandos. [Integrações oficiais](https://github.github.io/spec-kit/reference/integrations.html).

Uma pasta `.specify` contendo apenas a constituição deste pacote não comprova uma instalação completa. Conferir scripts, templates e estado da integração.

Não atualizar uma instalação funcional por rotina. Registrar versão, integração e conflitos encontrados. Não misturar comandos de tutoriais antigos com a CLI atual.

## 2. Se a ferramenta estiver ausente

Com Git instalado, instalar uv se necessário. O comando WinGet abaixo é documentado pelo projeto uv; abrir novamente o terminal se o PATH ainda não reconhecer a ferramenta. [Instalação oficial do uv](https://docs.astral.sh/uv/getting-started/installation/).

~~~powershell
winget install --id=astral-sh.uv -e
~~~

Para uma nova instalação do Spec Kit, este guia fixa a release **v1.0.6**, encontrada na consulta. A forma de instalação abaixo consta dessa release. [Spec Kit v1.0.6](https://github.com/github/spec-kit/releases/tag/v1.0.6).

~~~powershell
uv tool install specify-cli --from 'git+https://github.com/github/spec-kit.git@v1.0.6'
~~~

Verifique o resultado e então execute `specify version`. Se já existe uma instalação diferente, não adicionar `--force`: registrar a situação e planejar a compatibilidade.

Este passo instala a ferramenta de desenvolvimento; não instala a aplicação nem migra o banco.

## 3. Preparar a integração sem sobrescrever contexto

`specify init` aceita `--integration agy` e `--script ps`. A opção `--force` pode mesclar/sobrescrever arquivos; não a usar de forma automática nesta transição. Para um projeto existente, gerar primeiro uma estrutura temporária e comparar os arquivos é o procedimento escolhido para este caderno. [Comandos oficiais de inicialização](https://github.github.io/spec-kit/reference/core.html).

Se a integração ainda não existir, o agente pode gerar essa estrutura:

~~~powershell
& {
    $ErrorActionPreference = 'Stop'
    $cadernoSeedName = 'caderno-speckit-' + [guid]::NewGuid().ToString('N')
    $cadernoSeedParent = [System.IO.Path]::GetTempPath()

    Push-Location $cadernoSeedParent
    try {
        specify init $cadernoSeedName --integration agy --script ps
        if ($LASTEXITCODE -ne 0) {
            throw 'A preparação do Spec Kit falhou. Não copie arquivos parciais para o projeto.'
        }
        Write-Host ('Estrutura para comparar: ' + (Join-Path $cadernoSeedParent $cadernoSeedName))
    }
    finally {
        Pop-Location
    }
}
~~~

O agente deve comparar os arquivos oficiais gerados com os destinos e integrar somente a infraestrutura do Spec Kit e suas skills. Preservar a constituição do projeto, regras próprias e specs existentes; conferir referências de caminhos antes de mover arquivos. Não copiar caches nem manter referências absolutas ao diretório temporário.

Depois da integração, consultar novamente o estado. Alterações locais intencionais devem permanecer registradas; não forçar sobrescrita para eliminar avisos. Se a cópia não configurar corretamente a ferramenta, registrar o diagnóstico antes de tentar uma inicialização no lugar.

Se já houver outra integração, inspecionar seu estado. Quando a troca para Antigravity for necessária, a operação documentada é `specify integration switch agy --script ps`; usá-la após preservar regras customizadas, sem `--force`. [Troca de integração](https://github.github.io/spec-kit/reference/integrations.html).

Não inicializar Git nem criar branches por suposição. O comportamento de integração com Git mudou entre versões; verificar a instalação e a raiz real. A configuração inicial da ferramenta não exige publicar este projeto.

## 4. Regras do Antigravity

O pacote traz `.agents/rules/caderno-leitura.md`. Após integrar, conferir sua ativação no painel de personalizações, preferencialmente como “Always On”. A documentação atual usa `.agents/rules` e mantém compatibilidade com `.agent/rules`; aproveitar o diretório efetivamente usado no workspace. [Regras oficiais do Antigravity](https://antigravity.google/docs/rules-workflows).

A regra aponta para `AGENTS.md` e para o contexto. O primeiro prompt também pede a leitura explicitamente, evitando depender só da descoberta automática.

## 5. Fluxo de uma feature futura

Os nomes abaixo identificam operações do Spec Kit. A forma de chamar cada uma depende do agente/versão; selecionar a skill/comando que a integração expuser. A documentação geral usa a notação `/speckit.*`. Não colar esses nomes no terminal PowerShell como se fossem executáveis. [Fluxo oficial de especificação](https://github.github.io/spec-kit/reference/agentic-sdd.html).

| Operação | Resultado esperado no caderno |
| --- | --- |
| `speckit.constitution` | Consolidar a constituição existente, sem perder decisões do usuário |
| `speckit.specify` | Descrever uma entrega delimitada, comportamento e critérios de aceite |
| `speckit.clarify` | Resolver ambiguidades materiais, com perguntas objetivas |
| `speckit.plan` | Registrar desenho técnico compatível com o código auditado |
| `speckit.checklist` | Conferir a qualidade/completude dos requisitos quando necessário |
| `speckit.tasks` | Decompor o plano em alterações verificáveis |
| `speckit.analyze` | Detectar conflitos entre constituição, especificação, plano e tarefas |
| `speckit.implement` | Executar a implementação depois do pedido de início correspondente |
| `speckit.converge` | Se disponível, apoiar a verificação final do resultado |

Especificações devem separar requisito de decisão técnica ainda proposta. Registrar testes e evidências nos artefatos da feature, conforme os templates instalados.

## 6. Numeração e tamanho das entregas

`T09` e `T10` são IDs do roadmap. O identificador de uma feature em `specs/` segue a ferramenta e os diretórios existentes; não reservar `001` sem verificar.

Recomendação para a infraestrutura, quando o usuário pedir seu início:

1. Definir contratos comuns de localização de dados, snapshot e manutenção para T09/T10.
2. Especificar uma primeira fatia implementável: snapshot mínimo verificável e proteção do caminho de atualização.
3. Especificar as fatias restantes de migração/concorrência e pacote/restauração/operação.
4. Manter o vínculo de cada feature com T09/T10. Uma fatia pronta não conclui automaticamente a tarefa inteira.

Não produzir uma única tarefa vaga “implementar toda a 0.3”. Cada feature deve ter limite claro e validação própria.

## 7. Prompts para depois da auditoria

**Não executar nesta transição.** Os textos a seguir são modelos para o usuário enviar quando quiser começar o trabalho da versão.

### Consolidar governança

~~~text
Use a operação de constituição do Spec Kit disponível nesta integração para consolidar .specify/memory/constitution.md com as instruções reais do projeto e a auditoria inicial. Preserve acervo, stack, privacidade, compatibilidade e evidências. Não implemente código nem altere status do roadmap nesta operação.
~~~

### Iniciar a especificação da infraestrutura

~~~text
Agora inicie somente a especificação da primeira entrega de infraestrutura da 0.3, vinculada a T09 e T10. Leia ROADMAP-0.3.md e AUDITORIA-INICIAL.md e use a operação specify do Spec Kit.

Quero atualizar a aplicação sem perder meu acervo e conseguir recuperar os dados se algo falhar. Delimite a primeira entrega em um snapshot consistente verificável, identificação correta da base ativa e proteção do fluxo de atualização. Defina critérios que possam ser exercitados com dados fictícios, preservando IDs, notas e relacionamentos. Documente os contratos que as próximas entregas usarão.

Não implemente ainda, não execute migrações e não marque nenhuma tarefa como concluída. Mantenha as outras oito tarefas sem início. Use o próximo identificador de feature disponível no workspace.
~~~

### Elaborar o plano técnico dessa feature

~~~text
Use a operação plan do Spec Kit para a feature de infraestrutura especificada. Baseie os caminhos, contratos e versões nos arquivos auditados. Preserve FastAPI, SQLAlchemy/Alembic, SQLite e Vue/TypeScript. Reaproveite o snapshot existente somente se validado. Defina transações, isolamento dos testes, falhas, recuperação e como impedir acesso simultâneo durante operações incompatíveis. Não migre o banco real nesta etapa.
~~~

### Gerar tarefas e conferir consistência

~~~text
Use a operação tasks para decompor a feature em alterações pequenas e verificáveis. Depois use analyze para conferir consistência com a constituição e com os critérios de aceite. Inclua somente os testes necessários ao risco de dados e à compatibilidade Windows. Identifique dependências sem iniciar a implementação automaticamente.
~~~

Para implementar, o usuário deve pedir a execução da feature já delimitada. Depois desse pedido, continuar o trabalho autorizado sem solicitar confirmação a cada alteração reversível. Operações destrutivas sobre o acervo real e publicação têm escopo próprio.

## 8. Encerrar uma sessão

Atualizar `docs/contexto/RETOMADA.md` e os artefatos da feature com fatos verificados. Registrar diferenças ainda não aplicadas, testes pendentes e o próximo passo exato.

Durante a transição inicial, manter T01–T10 NÃO INICIADAS. Nos ciclos futuros, alterar estados somente conforme o trabalho realmente solicitado e realizado; não importar marcações de patches históricos.
