# Prompt de revisão crítica e ampliação do plano (executado pelo usuário fora do projeto)

Gerado em 2026-11-16 a pedido do usuário: analisar o [plano](./04-plano.md) e os [roadmaps](./05-roadmaps.md) e
produzir uma versão maior e mais robusta, sem pressa de calendário. O resultado deve ser salvo em
`docs/replanejamento-0.13/07-plano-revisado.md` e passa pela mesma regra dos outros: é dado a pesar, não
decisão; o que depender de evidência nova vira experimento antes de virar direção de trabalho.

**O que colar junto com o prompt, nesta ordem:** `04-plano.md`, `05-roadmaps.md`, a seção 1 a 5 do
`experiments/EXP-027-analise-50-paginas/report.md` e, se a ferramenta aceitar, `03-resultado-pesquisa.md`.
Nenhum desses arquivos contém texto do caderno; só números e categorias.

---

## Prompt (copiar a partir daqui)

Você é um revisor técnico sênior, cético e construtivo, com experiência em reconhecimento de manuscrito (HTR),
OCR de documentos, modelos visão-linguagem e, sobretudo, em **planejamento de projetos de aprendizado de
máquina que precisam durar meses sem perder o rumo**. Vou lhe entregar quatro documentos de um projeto: o
diagnóstico medido (relatório da Etapa 1), uma pesquisa de literatura (Etapa 2), o plano aprovado (Etapa 3) e
os roadmaps (Etapa 4). Sua tarefa é **criticar o plano e devolver um plano maior, mais robusto e mais
completo**, mantendo tudo o que estiver certo e corrigindo, acrescentando ou reordenando o que estiver fraco.
Não há pressa: o dono do projeto aceita que isso leve meses. O que ele não aceita é construir no escuro,
depender de fornecedor ou ter um plano que pareça completo e não seja.

### Contexto fixo (não questione; são restrições do projeto)

- Produto 100 % local, em CPU, sem custo por uso; nada de API paga nem nuvem no produto.
- Máquina de referência: Intel i5-8265U (4 núcleos), 7,9 GB de RAM, sem GPU útil, Windows 11, Python 3.13.
  GPU emprestada por horas só para treino, e só se o dono aceitar enviar páginas suas para fora.
- Objetivo final: **modelos próprios** (arquitetura, pesos, dados e treino sob controle do dono). Modelos de
  pesos abertos servem só como baseline e professor; cada um com cópia exata guardada (revisão, hash, licença).
- Dados: 51 páginas reais de um só autor, 20 congeladas como teste (nunca entram em treino, prompt, limiar ou
  léxico); o banco cresce com correções feitas pelo dono no produto. Não há dataset público de manuscrito em
  português com licença limpa para produto.
- Governança: todo experimento tem spec, hipóteses e métricas antes do código; experimento não é feature;
  nada entra no produto sem medição no teste congelado e um registro de decisão (ADR); contrato de dados
  (LDF 2.0) só muda por versão MINOR com change request.
- Números de partida no teste congelado: CER 56 %, WER 90 %; 28 % das palavras não aparecem na saída; fórmulas
  são 12–16 % do erro; cursiva não lê pior que letra de forma.

### O que fazer, nesta ordem

**1. Auditoria do plano.** Para cada seção do plano e de cada versão dos roadmaps, responda: o que está bem
fundamentado; o que é afirmação sem evidência; o que falta; o que está na ordem errada; onde um marco pode
ser atingido "no papel" sem resolver o problema real (métrica que não mede o que importa). Procure
explicitamente por: metas sem critério de parada; experimentos sem hipótese falseável; dependências ocultas;
passos que exigem dados que ninguém vai produzir; pontos onde um resultado negativo não tem plano B; riscos de
contaminar o teste congelado; riscos de licença; riscos de a máquina não aguentar.

**2. Plano ampliado.** Reescreva o plano inteiro, mais longo e mais completo, com estas seções obrigatórias:

a. **Estratégia e arquitetura-alvo** em linguagem simples, com um diagrama em texto do pipeline final e o
   papel de cada componente, incluindo o que fica fora do produto (professor, avaliação, treino).
b. **Infraestrutura de avaliação como primeira entrega**: conjunto de teste congelado, teste de deriva, métricas
   por origem de erro (detecção, ordem, leitura, fórmulas), métricas de custo (segundos e RAM por página),
   relatório automático reproduzível, regra de "nenhuma mudança entra sem o relatório". Proponha o que medir
   que o plano atual não mede.
c. **Estratégia de dados em profundidade**: como coletar, transcrever e anotar com o menor esforço humano por
   página; protocolo de qualidade da referência (duas passadas, concordância, amostragem para auditoria);
   versionamento de dados com hashes; curva de dados planejada (quantas páginas em cada degrau e o que se espera
   em cada um); dados sintéticos em português (como gerar, como validar que ajudam, quando param de ajudar);
   dados de outros autores no futuro; privacidade e consentimento.
d. **Roadmap por versões, mais granular**: quantas versões forem necessárias, cada uma com tema, hipótese
   central, experimentos e features (cada um com hipótese, métrica, critério de aceite, critério de abandono,
   dependências, se exige GPU, dados que ainda não existem), critério de saída no teste congelado e **plano B se
   o critério não for atingido**. Inclua versões de consolidação (refatoração, dívida técnica, reprodutibilidade)
   entre versões de ganho.
e. **Trajetória de modelos próprios, em degraus**: coleta → primeiro modelo próprio → comparação → substituição,
   por componente (detector, leitor, decodificador, fórmulas), com o custo honesto de cada degrau na máquina de
   referência e com GPU emprestada, os riscos de colapso de treino com poucos dados, e o critério objetivo de
   troca.
f. **Gestão de risco**: tabela de riscos com probabilidade, impacto, sinal de alerta mensurável e resposta.
g. **Portões de decisão**: momentos em que o dono precisa decidir algo (privacidade, GPU, licença, trocar de
   arquitetura), com a informação que ele terá em mãos para decidir.
h. **Ordem de execução sugerida para os próximos 12 meses sem datas**, só sequência e condições de passagem,
   dizendo o que pode correr em paralelo.

**3. Lista de experimentos adicionais** que o plano atual não tem e que reduziriam incerteza antes de gastar
esforço grande (por exemplo: medir quanto do erro é escala da foto; medir o efeito de uma só passada de
revisão versus duas; medir a variância entre sementes; ablações). Para cada um: pergunta, hipótese, custo,
o que decide.

**4. O que cortar ou adiar.** Diga sem rodeios o que no plano atual é desnecessário, prematuro ou ambicioso
demais para um só autor e uma máquina de 8 GB.

### Regras da resposta

- Português do Brasil. Uma parte em linguagem acessível para quem decide sem formação técnica, e detalhes
  técnicos em apêndices.
- Separe sempre **fato com fonte** (cite), **inferência sua** e **o que precisa ser medido localmente**. Não
  invente números nem fontes; quando não souber, diga.
- Nunca recomende serviço pago por uso, nem modelo externo como componente definitivo do produto.
- Não proponha trocar a forma como o dono escreve no caderno; o sistema se adapta ao autor, não o contrário.
- Respeite o conjunto de teste congelado: nada do que você propuser pode usar as 20 páginas de teste para
  treinar, ajustar ou escolher limiares.
- Seja longo onde houver substância e curto onde não houver. Prefira tabelas para listas de experimentos e
  riscos. Termine com uma lista de fontes com URL e data.
