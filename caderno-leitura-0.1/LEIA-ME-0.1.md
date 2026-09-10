# Caderno de Leitura — Alpha 0.1 completa

Este pacote reúne o projeto das Tarefas 1 a 8: backend, banco por migrações, importador, frontend, interface já compilada, dependências fixadas e testes. Ele não depende dos ZIPs anteriores.

**Em outro PC, o ZIP é suficiente como pacote do projeto, mas não é um executável portátil.** É necessário extrair os arquivos, ter Python 3.13 instalado e executar a instalação das dependências. A primeira instalação usa internet. O Node.js só é necessário para desenvolver, recompilar ou testar o frontend; o build para uso já está incluído.

Seus livros e estudos não estão neste ZIP. Eles ficam no arquivo SQLite do PC em que você usa o caderno. Veja “Trazer os estudos existentes” antes da instalação se quiser conservar o mesmo acervo.

## O que a versão faz

- Cadastro de livros e capítulos; estudos organizados por livro, capítulo e trecho.
- Importação manual de uma resposta do ChatGPT, usando o prompt incluído.
- Prévia editável dividida em Resumo, Explicação, Conceitos e Referências; avisos para respostas incompletas ou títulos repetidos.
- Página/localização e anotações próprias; resposta original preservada.
- Leitura nas quatro abas, com Markdown e navegação por teclado.
- Edição de título, localização, seções e notas; aviso para alterações não salvas.
- Persistência em SQLite e uso com apenas um servidor Python, no próprio PC.

Favoritos, busca global, exportação/importação do acervo, autenticação, acesso remoto por celular e backup automatizado não fazem parte desta Alpha. O layout estreito existe para preparar a interface, mas o servidor desta versão atende somente o PC local. Não há conexão automática com a conta do ChatGPT nem cobrança de API de IA pelo aplicativo.

## Instalação nova no Windows

### 1. Instalar o Python

Use **Python 3.13 de 64 bits** e mantenha o comando `py` disponível pelo instalador/gerenciador do Python. Consulte a [página oficial para Windows](https://www.python.org/downloads/windows/).

No PowerShell, confirme:

```powershell
py -3.13 --version
```

Se o comando informar que não encontrou essa versão, instale o Python 3.13 antes de continuar. Se você usa Python sem o comando `py`, execute `instalar.py` com o caminho completo do `python.exe` dessa versão. Não é necessário instalar SQLite separadamente.

### 2. Extrair o pacote em uma pasta nova

Salve `caderno-leitura-tarefa8-completo.zip` em Downloads. O ZIP contém uma pasta superior chamada `caderno-leitura-0.1`.

```powershell
New-Item -ItemType Directory -Path "$env:USERPROFILE\source" -Force | Out-Null
Set-Location "$env:USERPROFILE\source"
if (Test-Path ".\caderno-leitura-0.1") { throw "A pasta caderno-leitura-0.1 já existe. Use outra pasta vazia para a nova instalação." }
Expand-Archive -LiteralPath "$env:USERPROFILE\Downloads\caderno-leitura-tarefa8-completo.zip" -DestinationPath .
Set-Location ".\caderno-leitura-0.1"
```

Se já usa as Tarefas 1 a 7, mantenha a pasta antiga intacta e use esta pasta nova para a versão consolidada. Isso evita misturar ambientes e arquivos de dependências das duas instalações.

### 3. Trazer os estudos existentes — opcional, antes de instalar

Para começar com um acervo vazio, pule para a etapa 4.

Para manter o acervo atual, encerre o servidor do caderno e qualquer ferramenta que esteja usando o banco. Copie `backend\data\caderno.db` da instalação antiga para o mesmo caminho relativo da pasta nova. Faça isso com o caderno encerrado nos dois locais.

Exemplo para trazer os dados do projeto anterior neste mesmo PC, ainda na raiz da pasta nova:

```powershell
$bancoOrigemCaderno = "$env:USERPROFILE\source\caderno-leitura\backend\data\caderno.db"
$bancoDestinoCaderno = Join-Path (Get-Location) "backend\data\caderno.db"
if (!(Test-Path -LiteralPath $bancoOrigemCaderno)) { throw "Banco original não encontrado. Confira o caminho." }
if (Test-Path -LiteralPath $bancoDestinoCaderno) { throw "Já existe um banco no destino. Não substitua um acervo existente; use uma pasta nova." }
New-Item -ItemType Directory -Path ".\backend\data" -Force | Out-Null
Copy-Item -LiteralPath $bancoOrigemCaderno -Destination $bancoDestinoCaderno
```

Em outro PC, transporte uma cópia desse banco feita após encerrar o caderno e use-a como origem. Mantenha a cópia original até conferir os dados na nova instalação. Se o arquivo estiver acompanhado de `caderno.db-wal` ou `caderno.db-journal`, não faça uma cópia isolada do `.db` enquanto houver uma operação ativa; encerre normalmente todas as conexões antes da transferência.

O instalador aplica migrações pendentes ao arquivo existente; ele não zera o acervo. Não há sincronização entre PCs: depois da cópia, cada instalação tem seus próprios dados.

Se você configurou `CADERNO_DATABASE_PATH`, essa variável tem prioridade sobre o caminho padrão. Confira o arquivo configurado antes de transferir dados. Esta versão conserva esse recurso avançado, mas não precisa dele para a instalação normal.

### 4. Instalar as dependências e preparar o banco

Na raiz de `caderno-leitura-0.1`:

```powershell
py -3.13 instalar.py
```

Ou abra **INSTALAR.cmd** com duplo clique. Ele executa a mesma instalação e mantém a janela aberta para exibir eventuais erros.

A instalação cria `backend\.venv`, instala as versões fixadas em `backend\requirements.txt` e aplica `alembic upgrade head`. Quando não existe acervo, cria um banco vazio. Nenhum exemplo é importado automaticamente.

Não copie a `.venv` de outro PC e não mova a pasta instalada para outro local sem refazer o ambiente. Ambientes virtuais guardam referências à instalação de Python e precisam ser recriados no destino. [Documentação do Python sobre ambientes virtuais](https://docs.python.org/3.13/library/venv.html).

### 5. Iniciar

Abra **INICIAR.cmd** ou execute:

```powershell
.\backend\.venv\Scripts\python.exe iniciar.py
```

Depois, abra o [caderno local](http://127.0.0.1:8000). Mantenha o terminal aberto. Para encerrar, pressione `Ctrl+C`.

Nas próximas vezes, basta usar **INICIAR.cmd**. A instalação não precisa ser repetida a cada abertura. Se a porta 8000 estiver ocupada, encerre o processo anterior deste projeto antes de iniciar outro. Não é necessário abrir o Vite.

## Primeiro estudo

1. Cadastre um livro e adicione um capítulo.
2. Use `PROMPT-PADRAO.md` na conversa do ChatGPT escolhida. Para testar sem uma resposta real, copie `exemplos/resposta-para-colar.txt`.
3. Em **Importar estudo**, escolha o destino, informe a localização e cole a resposta inteira.
4. Clique em **Preparar prévia**, confira os avisos e corrija as seções. Registre suas anotações.
5. Salve e clique em **Ler estudo**. Use as quatro abas para estudar e **Editar estudo** para fazer alterações.

O acervo salvo permanece no disco depois de encerrar o servidor. Rascunhos ainda não salvos ficam em memória. O roteiro de conferência da versão está em `ACEITE-0.1.md`.

## Desenvolvimento e testes

Para executar os testes Python, instale também as dependências de desenvolvimento:

```powershell
py -3.13 instalar.py --dev
Set-Location .\backend
.\.venv\Scripts\python.exe -m pytest -q
Set-Location ..
```

O teste de servidor real usa uma porta temporária em loopback e um banco temporário. O teste de link simbólico pode ser pulado no Windows quando o sistema não permite criá-lo; não altere permissões do sistema apenas para esse teste.

Para modificar, testar ou recompilar o frontend, use Node.js 24:

```powershell
Set-Location .\frontend
npm.cmd ci
npm.cmd test
npm.cmd run build
Set-Location ..
```

`npm ci` instala a árvore registrada em `package-lock.json`. Após editar a interface, gere um novo build e atualize a página. Aguarde a compilação terminar antes de usar o caderno. Alterações no Python exigem reiniciar o servidor.

Os arquivos `requirements.in` e `requirements-dev.in` registram as dependências diretas. Os correspondentes `.txt` fixam também as dependências transitivas e incluem as condições de plataforma. O Uvicorn básico é suficiente para esta aplicação; o uso diário não exige as extensões opcionais de `uvicorn[standard]`.

## Organização do pacote

| Caminho | Conteúdo |
| --- | --- |
| `INSTALAR.cmd` / `instalar.py` | Preparação da instalação local |
| `INICIAR.cmd` / `iniciar.py` | Início do servidor em `127.0.0.1:8000` |
| `backend/app` | API, modelos, importador e atendimento da interface |
| `backend/migrations` | Estrutura e evolução do SQLite |
| `backend/requirements*.txt` | Dependências fixadas para uso e testes |
| `backend/tests` | Testes de API, persistência e atendimento do frontend |
| `frontend/src` | Código Vue e TypeScript |
| `frontend/dist` | Interface compilada, já incluída e única pasta pública |
| `frontend/package.json` / `package-lock.json` | Comandos e dependências do frontend |
| `frontend/tests` | Testes de importação, edição, Markdown e navegação |
| `PROMPT-PADRAO.md` / `exemplos` | Material para preparar e testar importações |
| `VALIDACAO-0.1.md` / `ACEITE-0.1.md` | Resultado técnico e roteiro de conferência local |

O ZIP não inclui Python, `.venv`, `node_modules`, banco pessoal ou dados de testes. Não há necessidade de reunir arquivos das entregas anteriores. A versão técnica da Alpha é `0.1.0-alpha.1`.
