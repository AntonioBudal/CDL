# Validação técnica — Alpha 0.1 / Tarefa 8

Data: 9 de setembro de 2026. Versão da aplicação: `0.1.0-alpha.1`.

O pacote completo foi preparado para uma instalação independente das Tarefas 1 a 7. A validação técnica abaixo foi executada em Linux x86_64, com uma cópia extraída do ZIP em uma pasta com espaço no nome. A conferência visual e a execução dos atalhos `.cmd` no Windows permanecem pendentes; use `ACEITE-0.1.md` no seu PC.

## Resultados

| Verificação | Resultado observado |
| --- | --- |
| Instalação inicial com `instalar.py` | Ambiente virtual criado, dependências fixadas instaladas e migração `0001_initial` aplicada ao banco vazio |
| Inicialização com `iniciar.py` | Interface compilada e API atendidas pelo mesmo processo Python em `127.0.0.1:8000`, sem servidor Vite |
| Dependências para uso | Inicializador verificado antes de instalar `pytest` e `httpx`; o frontend pronto não exige executar Node.js |
| Caminhos da instalação | Instalador e inicializador executados a partir de outro diretório, apontando para um projeto cujo caminho contém espaço |
| Preservação na reinstalação | Um estudo sintético foi importado e editado; após encerrar o servidor, repetir a instalação e reiniciar, seu conteúdo permaneceu igual |
| Backend — `python -m pytest -q` | **68 testes passaram**, sem testes pulados; 2 avisos de descontinuação das bibliotecas de teste |
| Frontend — `npm ci` | Dependências instaladas a partir do `package-lock.json` em uma pasta extraída do pacote |
| Frontend — `npm test` | **35 testes passaram**, sem falhas nem testes pulados |
| Frontend — `npm run build` | Verificação TypeScript e compilação Vite concluídas; os 5 arquivos gerados são idênticos aos incluídos em `frontend/dist` |

Os testes de persistência usam arquivos SQLite temporários. A instalação de conferência utilizou apenas dados sintéticos. Nenhum banco pessoal ou banco de teste acompanha a entrega.

## O que os testes cobrem

- **Banco:** migrações compatíveis com os modelos, conservação dos registros ao reaplicar migrações e reabrir em outro processo, chaves estrangeiras, rejeição de relacionamentos inválidos e reversão de transações que falham.
- **API:** organização por livro e capítulo, validação dos campos, preparação da prévia sem gravação, importação das correções, edição parcial e conservação da resposta original e das notas. Uma edição inválida não aplica apenas parte das alterações.
- **Importador:** as quatro seções, acentos, diferentes quebras de linha, títulos ausentes ou repetidos, texto não associado e blocos de código. O texto original permanece disponível para revisão.
- **Interface, por testes de lógica:** estado da importação e da edição, falhas de comunicação, prevenção de envios simultâneos, respostas atrasadas, formatação Markdown e confirmação ao abandonar alterações. A navegação usa o Vue Router em memória; isso não equivale a uma inspeção visual no navegador.
- **Servidor real:** entrega do HTML, JavaScript e CSS compilados, prioridade das rotas da API, leitura direta dos endereços da interface, importação, edição e persistência após encerrar e iniciar outro processo Uvicorn.
- **Pasta pública:** atendimento restrito a `frontend/dist`, erros de arquivos ausentes, bloqueio de caminhos indevidos e rejeição de um banco configurado dentro do diretório público.

## Versões usadas na conferência

| Componente | Versão |
| --- | --- |
| Python / SQLite incluído nesse Python | 3.13.15 / 3.53.1 |
| FastAPI / Starlette / Pydantic | 0.141.1 / 1.6.0 / 2.13.5 |
| Uvicorn / SQLAlchemy / Alembic | 0.52.4 / 2.0.52 / 1.19.2 |
| pytest / httpx | 9.1.1 / 0.28.1 |
| Node.js | 24.19.0 |
| Vue / Vue Router | 3.5.42 / 4.6.4 |
| TypeScript / vue-tsc / Vite | 6.0.3 / 3.3.11 / 8.2.2 |
| markdown-it | 14.3.1 |

As dependências Python, incluindo as transitivas, estão fixadas nos arquivos `requirements*.txt`. A árvore do frontend está no `package-lock.json`. A versão do SQLite pode variar conforme a distribuição de Python instalada no seu PC; não é necessário instalar um servidor SQLite separado.

Os dois avisos Python referem-se ao uso de `httpx` pelo TestClient do Starlette e a um alias do AnyIO. Eles não causaram falhas. O npm também exibiu um aviso sobre uma configuração de proxy do ambiente de conferência; a configuração não faz parte do projeto e a instalação e a compilação terminaram normalmente.

## Instalação em outro PC

O ZIP reúne código, interface compilada, migrações, dependências declaradas, exemplos e documentação. **Não é um executável portátil:** o destino precisa ter Python 3.13, e a primeira instalação baixa as dependências pela internet. Não é preciso instalar Node.js para o uso diário.

Os estudos existentes devem ser transferidos separadamente. O procedimento está em `LEIA-ME-0.1.md`: encerrar o caderno, copiar o banco para uma pasta nova e depois executar o instalador, conservando a origem até conferir o acervo. A reinstalação foi verificada com dados sintéticos; não tive acesso ao banco do seu PC.

## Conferência que falta no seu PC

Os atalhos Windows foram preparados com caminhos entre aspas e finais de linha Windows, mas não foram executados em Windows nesta sessão. Também não foram verificados visualmente o layout, a troca de abas por teclado, o foco e os diálogos do navegador. A tentativa anterior de usar o navegador de teste foi rejeitada pela revisão automática de aprovação; essa verificação não é declarada como concluída.

O roteiro `ACEITE-0.1.md` registra essas verificações locais. Os testes automáticos aprovados não substituem esse aceite visual.
