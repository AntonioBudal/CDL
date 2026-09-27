# Roadmap 0.6 — Leitorum

**Data oficial de emissão:** 2026-09-27  
**Status do Roadmap:** Planejado para desenvolvimento com o GitHub Spec Kit (`speckit`).  
**Regra Geral de Estado:** Todas as dez features (**F0.6.1 a F0.6.10**) estão estritamente **NÃO INICIADAS**.  
Nenhum rascunho anterior, arquivo de teste ou documento prévio altera o status de qualquer entrega deste roadmap. O avanço ocorre somente através de ciclos delimitados do fluxo Spec Kit (`speckit-specify` → `speckit-clarify` → `speckit-plan` → `speckit-tasks` → `speckit-analyze` → `speckit-implement`), resultando em **1 Commit Atômico por Feature Validada**.

---

## Objetivo do Ciclo

O Roadmap 0.6 concentra-se em quatro objetivos:

1. Evoluir o fichamento de um documento estático para uma experiência de estudo mais fluida e interativa.
2. Simplificar e organizar a taxonomia interna do Leitorum.
3. Preparar a presença pública do Leitorum para descoberta, identificação e indexação na web.
4. Fortalecer a segurança do sistema agora que a aplicação está disponível publicamente.

O princípio geral do ciclo é:

> **Mais capacidade interna, menos complexidade para o usuário.**

O usuário não deve precisar aprender comandos, sintaxes ou conceitos técnicos para utilizar as novas funcionalidades do editor.

---

# F0.6.1 — Importação Inteligente

## Objetivo

Evoluir o atual sistema de importação para que o usuário continue trabalhando com **uma única entrada de texto**, enquanto o Leitorum identifica e organiza sua estrutura.

## Base existente

A auditoria confirmou que já existem:

* parser de seções;
* normalização de títulos;
* proteção de blocos de código;
* prévia antes do salvamento;
* tratamento de avisos;
* separação das quatro seções no banco.

## Evolução desejada

O sistema deverá ser mais tolerante às diferentes formas pelas quais um fichamento pode ser estruturado.

A importação deverá:

* reconhecer variações razoáveis de títulos;
* detectar estruturas equivalentes;
* informar claramente quando não conseguir determinar uma seção;
* preservar o texto original;
* permitir correções rápidas antes do salvamento;
* evitar fragmentar a experiência em quatro campos independentes como etapa obrigatória.

## Princípio de UX

```text
Colar
  ↓
Leitorum entende
  ↓
Usuário confere
  ↓
Salvar
```

---

# F0.6.2 — Seleção e Ações Contextuais

## Objetivo

Permitir que o usuário selecione qualquer trecho do estudo e encontre ações relevantes diretamente no contexto daquele trecho.

## Conceito

A interação principal será:

```text
Selecionar
    ↓
Escolher ação
    ↓
Pronto
```

Sem exigir comandos especiais ou ferramentas permanentemente visíveis.

Possíveis ações:

* destacar;
* ocultar;
* transformar em pergunta;
* criar anotação;
* transformar em citação;
* outras ações definidas durante a especificação.

## Base técnica

A auditoria confirmou que atualmente não existe:

* Selection API;
* Range API aplicada ao estudo;
* captura de seleção textual;
* ancoragem de trechos;
* floating toolbar;
* modelo persistente para trechos.

Essa feature deverá criar essa fundação.

---

# F0.6.3 — Leitura Ativa

## Objetivo

Transformar partes do próprio fichamento em pequenas interações de estudo, sem criar um sistema separado de flashcards.

## Conceito

O texto continua sendo o centro da experiência.

Alguns trechos podem assumir comportamentos como:

* revelar conteúdo;
* esconder resposta;
* expandir informação;
* destacar informação importante;
* apresentar uma pergunta simples.

Exemplo:

```text
Qual é a ideia principal do argumento?

[Revelar]
```

O usuário continua no mesmo estudo.

## Princípio

Não criar uma tela paralela de "flashcards".

A interação deverá nascer do próprio fichamento.

## Base técnica

A auditoria confirmou que o renderer atual é Markdown estático com `v-html` e `html: false`, sem componentes interativos dentro do conteúdo.

Essa feature deverá definir a nova capacidade de conteúdo interativo preservando as proteções atuais.

---

# F0.6.4 — Interface Contextual

## Objetivo

Reduzir a quantidade de controles permanentemente expostos durante leitura e edição.

## Conceito

As ações aparecem quando possuem contexto.

```text
Selecionar texto
    ↓
ações relacionadas ao texto
```

```text
Interagir com uma referência
    ↓
ações relacionadas à referência
```

```text
Entrar em edição
    ↓
ferramentas relevantes
```

## Objetivo de UX

O usuário não deve olhar para uma grande barra de ferramentas tentando descobrir qual dos vários botões precisa utilizar.

A interface deve apresentar a ação no momento em que ela se torna relevante.

## Base existente

A auditoria identificou:

* dropdowns;
* menus móveis;
* condicionamento por permissões;
* abas acessíveis;
* padrões de componentes contextuais em outras áreas.

A feature deverá reaproveitar esses padrões em vez de criar uma segunda arquitetura de menus.

---

# F0.6.5 — Histórico Automático

## Objetivo

Permitir que o usuário altere seus estudos sem medo de destruir uma versão anterior.

## Conceito

O sistema registra automaticamente versões relevantes.

O usuário poderá:

* consultar versões;
* visualizar uma versão anterior;
* restaurar uma versão.

A criação dessas versões será automática.

## UX

Não deve existir necessidade de clicar em:

> "Criar versão"

antes de editar.

Para o usuário, a promessa principal é simplesmente:

> **Suas versões anteriores podem ser recuperadas.**

## Base técnica

A auditoria confirmou que atualmente existem:

* timestamps;
* dirty state;
* proteção contra saída sem salvar;
* controle de concorrência;
* patches parciais;

mas não existem:

* snapshots;
* histórico;
* diff;
* restauração;
* autosave.

Essa feature deverá criar essa infraestrutura.

---

# F0.6.6 — Apoie o Leitorum

## Objetivo

Criar uma forma simples e opcional para que usuários possam contribuir financeiramente para manutenção do Leitorum.

## Regra de navegação

**Não criar uma aba principal para doações.**

A funcionalidade deverá ficar acessível pelo **rodapé** do site/aplicação, por exemplo:

```text
Leitorum
────────────────────────────
Sobre · Apoie o projeto · ...
```

ou equivalente visual.

A página também deverá ser acessível diretamente por uma rota pública.

## Conteúdo

A tela deverá explicar de forma simples:

* que o Leitorum é gratuito;
* que não há obrigação de contribuição;
* para que a contribuição ajuda;
* formas disponíveis para contribuir.

## Formas de contribuição

A tela deverá permitir configurar:

### PIX

* chave PIX;
* identificação;
* QR Code;
* botão para copiar a chave.

### Google Pay

* link de pagamento/doação configurável;
* botão de acesso;
* possibilidade de desativar a opção quando não configurada.

A aplicação **não deverá implementar processamento financeiro próprio**.

Ela deverá apenas apresentar/configurar os meios externos definidos pelo administrador.

## Configuração

Os dados deverão ser configuráveis sem alteração do código-fonte.

Devem existir estados claros:

```text
PIX configurado
PIX não configurado

Google Pay configurado
Google Pay não configurado
```

## UX

A tela deverá ser discreta, profissional e sem linguagem emocional ou pressionadora.

A doação é uma opção de apoio, não parte da navegação principal do produto.

---

# F0.6.7 — Normalização e Simplificação de Categorias

## Objetivo

Reorganizar a taxonomia atual do Leitorum.

A auditoria deverá partir do catálogo real existente, pois atualmente existem mais de 100 categorias e algumas possuem nomes excessivamente longos ou compostos.

## Regras para as categorias finais

As categorias canônicas deverão possuir:

* nome único;
* forma singular;
* nome curto;
* linguagem clara;
* preferência por uma única palavra;
* ausência de nomes compostos;
* ausência de duplicatas semânticas ou apenas diferenças de capitalização/acentuação;
* consistência gramatical.

Exemplo conceitual:

```text
Categorias ruins
"Ciências Sociais e Humanas"
"Histórias de Ficção"
"Teorias Políticas Modernas"

Categorias normalizadas
"Ciência"
"História"
"Política"
```

Os exemplos acima são apenas ilustrativos. **A migração real deverá ser baseada nas categorias existentes no banco.**

## Processo

A feature deverá:

1. auditar todas as categorias existentes;
2. identificar duplicidades;
3. identificar nomes compostos;
4. identificar nomes excessivamente longos;
5. identificar inconsistências entre singular/plural;
6. propor categorias canônicas;
7. mapear categorias antigas para as novas;
8. migrar as referências existentes;
9. impedir a criação de novas categorias fora das regras definidas;
10. preservar a integridade dos estudos existentes.

## Importante

Não apagar uma categoria simplesmente porque ela será substituída.

Deverá existir uma correspondência:

```text
categoria antiga
       ↓
categoria canônica
```

para que nenhum estudo perca sua classificação.

## Resultado esperado

O sistema deve sair de uma taxonomia extensa e inconsistente para uma taxonomia curta, previsível e reutilizável.

---

# F0.6.8 — Presença Pública e SEO do Leitorum

## Objetivo

Preparar o Leitorum para ser corretamente identificado, compreendido e rastreado pelos mecanismos de busca.

A funcionalidade não deverá ser apenas "colocar palavras-chave".

Deverá tratar a presença pública do produto como uma parte própria da arquitetura do site.

O Google documenta que títulos, conteúdo da página, favicons, sitemap, dados estruturados e outras informações ajudam seus sistemas a compreender e apresentar um site; dados estruturados podem ajudar a classificar o conteúdo, embora não garantam um resultado visual específico.

## Página pública "Sobre o Leitorum"

Criar uma página pública acessível pelo rodapé:

```text
Sobre
```

Ela deverá explicar claramente:

* o que é o Leitorum;
* para quem foi criado;
* como funciona;
* organização de livros;
* estudos;
* fichamentos;
* características principais;
* filosofia do produto;
* funcionamento sem anúncios, conforme definido pelo produto;
* informações básicas sobre o projeto.

Essa página deve existir principalmente para **pessoas e mecanismos de busca entenderem o produto**, não como texto artificial para SEO.

## Estrutura pública

Avaliar a necessidade de uma página inicial pública separada da aplicação autenticada:

```text
leitorum.com
      ↓
apresentação pública
      ↓
Entrar / Criar conta
```

em vez de depender exclusivamente da aplicação interna como primeira experiência pública.

## SEO técnico

A feature deverá auditar e implementar, conforme aplicável:

* títulos únicos por página pública;
* meta descriptions;
* canonical;
* Open Graph;
* Twitter/X metadata;
* favicon adequado;
* `robots.txt`;
* `sitemap.xml`;
* controle de `noindex`;
* URLs públicas coerentes;
* hierarquia semântica de headings;
* links internos;
* páginas públicas rastreáveis;
* tratamento correto das rotas SPA;
* prevenção de indexação de áreas privadas.

O Google recomenda sitemap para manter o mecanismo informado sobre mudanças e enfatiza que páginas destinadas à indexação precisam estar acessíveis ao rastreador e não bloqueadas por `robots.txt`, `noindex` ou autenticação.

## Dados estruturados

Avaliar a utilização correta de dados estruturados para identificar o Leitorum como aplicação/site.

A documentação do Google inclui `SoftwareApplication`/`WebApplication` entre os tipos utilizados para dados estruturados de software.

Não adicionar dados estruturados apenas para "encher" a página. Cada tipo deverá representar informações realmente existentes.

## Identidade do site

Avaliar também:

* nome do site;
* favicon;
* logo;
* descrição;
* identidade textual;
* consistência entre `<title>`, conteúdo visível e metadata.

O favicon atual também deverá ser revisado segundo as recomendações atuais do Google; o Google recomenda um favicon quadrado e sugere tamanho superior a 48×48 px para melhor apresentação, além de exigir que o rastreador consiga acessá-lo.

## Resultado esperado

Ao final da feature, o Leitorum deverá possuir uma presença pública coerente tanto para usuários quanto para mecanismos de busca.

A feature **não promete posicionamento específico no Google**. Ela prepara tecnicamente o site para descoberta, rastreamento e compreensão.

---

# F0.6.9 — Segurança de Aplicação e Dados

## Objetivo

Fortalecer as camadas técnicas do sistema contra vulnerabilidades de aplicação agora que o Leitorum está exposto publicamente.

Esta feature deverá concentrar as questões relacionadas ao **código, entrada de dados e exposição de informação**.

## Áreas

### XSS

Auditar e fortalecer:

* renderização Markdown;
* `v-html`;
* sanitização;
* conteúdo fornecido pelo usuário;
* conteúdo compartilhado;
* links;
* HTML incorporado;
* conteúdo exportado e reimportado.

A solução deve preservar a capacidade futura de conteúdo interativo sem abrir mão da segurança.

### SQL Injection

Auditar:

* SQLAlchemy;
* queries;
* filtros;
* buscas;
* SQL bruto;
* parâmetros;
* concatenação de SQL.

Corrigir qualquer caminho inseguro encontrado.

### CORS

Verificar:

* origens permitidas;
* necessidade real de CORS;
* comportamento em produção;
* diferença entre localhost e `leitorum.com`.

Como o sistema usa arquitetura same-origin, não adicionar permissões amplas sem necessidade.

### Security Headers

Implementar e validar os cabeçalhos de segurança realmente aplicáveis à arquitetura:

* Content-Security-Policy;
* X-Content-Type-Options;
* Referrer-Policy;
* Permissions-Policy;
* políticas relacionadas a framing;
* demais cabeçalhos relevantes.

Não adicionar headers somente por checklist; validar compatibilidade com Vue, Markdown, Google Identity e Cloudflare.

### Erros do backend

Garantir que erros de produção não exponham:

* stack traces;
* caminhos internos;
* queries;
* detalhes de implementação;
* segredos;
* informações desnecessárias do ambiente.

### Segredos

Auditar:

* chaves;
* tokens;
* credenciais;
* variáveis de ambiente;
* arquivos `.env`;
* histórico do Git;
* configurações de produção.

---

# F0.6.10 — Segurança de Autenticação, Abuso e Exposição da Infraestrutura

## Objetivo

Fortalecer a camada de acesso do Leitorum contra abuso e exposição indevida agora que existe um endereço público.

## Rate Limiting

Implementar limites apropriados para endpoints sensíveis, principalmente:

* login;
* registro;
* recuperação, quando existir;
* autenticação Google;
* operações que possam ser abusadas para gerar carga.

O rate limiting deverá ser baseado no risco do endpoint e não aplicado indiscriminadamente a toda a aplicação.

## Autenticação e Sessões

Auditar:

* cookies;
* sessão;
* expiração;
* `Secure`;
* `HttpOnly`;
* `SameSite`;
* invalidação;
* login/logout;
* proteção contra reutilização indevida de sessão;
* comportamento atrás do Cloudflare Tunnel.

## Proteção de recursos privados

Verificar se recursos como:

* banco;
* backups;
* arquivos;
* capas;
* avatares;
* exports;
* logs;
* arquivos estáticos internos;

não podem ser acessados diretamente de maneira indevida.

Especial atenção ao SQLite:

```text
backend/data/caderno.db
```

O arquivo físico nunca deve ser disponibilizado pelo servidor HTTP.

O mesmo vale para:

* ZIPs de backup;
* arquivos temporários;
* `.env`;
* código-fonte;
* diretórios internos.

## Força bruta e abuso

Avaliar:

* tentativas repetidas de autenticação;
* criação automatizada de contas;
* endpoints de alto custo;
* uploads;
* exportações;
* mecanismos de compartilhamento.

## Cloudflare

Auditar a fronteira:

```text
Internet
   ↓
Cloudflare
   ↓
Tunnel
   ↓
Windows
   ↓
Leitorum
```

Verificar se a aplicação depende corretamente da identidade dos headers encaminhados pelo proxy e se não aceita como confiáveis headers que possam ser falsificados diretamente pelo cliente.

## Resultado esperado

O Leitorum deve possuir uma separação clara entre:

```text
recursos públicos
        ↓
recursos autenticados
        ↓
recursos administrativos
        ↓
arquivos internos da infraestrutura
```

Nenhum desses níveis deve depender apenas de segurança por obscuridade.

---

# Ordem consolidada do Roadmap 0.6

| Feature    | Nome                                              | Área        |
| ---------- | ------------------------------------------------- | ----------- |
| **0.6.1**  | Importação Inteligente                            | Fichamentos |
| **0.6.2**  | Seleção e Ações Contextuais                       | Fichamentos |
| **0.6.3**  | Leitura Ativa                                     | Fichamentos |
| **0.6.4**  | Interface Contextual                              | Fichamentos |
| **0.6.5**  | Histórico Automático                              | Fichamentos |
| **0.6.6**  | Apoie o Leitorum                                  | Produto     |
| **0.6.7**  | Normalização e Simplificação de Categorias        | Dados       |
| **0.6.8**  | Presença Pública e SEO do Leitorum                | Web         |
| **0.6.9**  | Segurança de Aplicação e Dados                    | Segurança   |
| **0.6.10** | Segurança de Autenticação, Abuso e Infraestrutura | Segurança   |

---

# Dependências entre as Features

A ordem não é arbitrária.

```text
0.6.1
Importação
   ↓
0.6.2
Seleção
   ↓
0.6.3
Leitura ativa
   ↓
0.6.4
Interface contextual
   ↓
0.6.5
Histórico
```

As cinco primeiras evoluem o mesmo núcleo.

Enquanto isso:

```text
0.6.6
Doação
```

é praticamente independente.

```text
0.6.7
Categorias
```

atua principalmente sobre os dados e a organização do acervo.

```text
0.6.8
SEO / presença pública
```

transforma o Leitorum em um produto público mais bem identificado pelos mecanismos de busca.

E:

```text
0.6.9
Segurança da aplicação
       ↓
0.6.10
Segurança de autenticação e infraestrutura
```

fecha o ciclo de exposição pública.

---

# Princípio de fechamento do 0.6

Ao terminar o Roadmap 0.6, o Leitorum deverá ter evoluído em três direções simultâneas:

```text
                 LEITORUM 0.6
                      │
       ┌──────────────┼──────────────┐
       ↓              ↓              ↓
   ESTUDO          PRODUTO        CONFIANÇA
       │              │              │
 editor simples    doação         segurança
 leitura ativa     categorias     autenticação
 histórico         SEO            infraestrutura
```

A característica mais importante é que **nenhuma dessas áreas deve transformar o Leitorum em um produto inchado**.

O princípio continua sendo:

> **usuário simples, sistema sofisticado.**
