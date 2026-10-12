import type { IconName } from '../types'

export type SimulatorDimensionId = 'resumo' | 'explicacao' | 'conceitos' | 'referencias'

export interface SimulatorDimension {
  id: SimulatorDimensionId
  title: string
  subtitle: string
  labelShort: string
  iconName: IconName
  question: string
  content: string
  keyInsights: readonly string[]
}

export interface TextHighlight {
  id: string
  dimensionId: SimulatorDimensionId
  textSnippet: string
  explanation: string
}

export interface LiteraryWorkSnippet {
  author: string
  title: string
  year: number
  sectionTitle: string
  paragraphs: readonly string[]
  marginalia: {
    label: string
    text: string
  }
}

export interface LandingSimulatorData {
  work: LiteraryWorkSnippet
  highlights: readonly TextHighlight[]
  dimensions: readonly SimulatorDimension[]
}

export const LANDING_SIMULATOR_DATA: LandingSimulatorData = Object.freeze({
  work: Object.freeze({
    author: 'Machado de Assis',
    title: 'Memórias Póstumas de Brás Cubas',
    year: 1881,
    sectionTitle: 'Ao leitor (Prólogo)',
    paragraphs: Object.freeze([
      'Que Stendhal confessasse haver escrito um de seus livros para cem leitores, coisa é que admira e consterna. O que não admira, nem provavelmente consternará é se este outro livro não tiver os cem leitores de Stendhal, nem cinquenta, nem vinte e, quando muito, dez. Dez? Talvez cinco.',
      'Trata-se, na verdade, de uma obra difusa, na qual eu, Brás Cubas, se adotei a forma livre de um Sterne ou de um Xavier de Maistre, não sei se lhe meti algumas rabugens de pessimismo. Pode ser. Obra de finado. Escrevi-a com a pena da galhofa e a tinta da melancolia, e não é difícil antever o que poderá sair de semelhante conúbio.',
      'Acresce que a gente grave achará no livro umas aparências de puro romance, ao passo que a gente frívola não achará nele o seu romance usual; ei-lo aí conchegado e desdenhado pelos sérios e pelos fúteis. Mas eu ainda espero angariar as simpatias da posteridade, deixando aos vermes que primeiro roerem as frias carnes do meu cadáver uma dedicatória expressa.',
    ]),
    marginalia: Object.freeze({
      label: 'Nota Marginal',
      text: 'A célebre dedicatória: «Ao verme que primeiro roeu as frias carnes do meu cadáver dedico como saudosa lembrança estas memórias póstumas».',
    }),
  }),
  highlights: Object.freeze<TextHighlight[]>([
    {
      id: 'h-resumo',
      dimensionId: 'resumo',
      textSnippet: 'Obra de finado. Escrevi-a com a pena da galhofa e a tinta da melancolia, e não é difícil antever o que poderá sair de semelhante conúbio.',
      explanation: 'Síntese da postura do narrador que escreve do além-túmulo unindo humor ácido e desilusão ontológica.',
    },
    {
      id: 'h-explicacao',
      dimensionId: 'explicacao',
      textSnippet: 'Trata-se, na verdade, de uma obra difusa, na qual eu, Brás Cubas, se adotei a forma livre',
      explanation: 'Machado desconstrói a cronologia linear romântica, adotando o fluxo digressivo e conversacional.',
    },
    {
      id: 'h-conceitos',
      dimensionId: 'conceitos',
      textSnippet: 'não sei se lhe meti algumas rabugens de pessimismo.',
      explanation: 'O pessimismo machadiano surge como mecanismo desmistificador das convenções da sociedade burguesa do séc. XIX.',
    },
    {
      id: 'h-referencias',
      dimensionId: 'referencias',
      textSnippet: 'se adotei a forma livre de um Sterne ou de um Xavier de Maistre',
      explanation: 'Diálogo direto com a tradição humorística ilustrada de Tristram Shandy e Viagem à Roda do Meu Quarto.',
    },
  ]),
  dimensions: Object.freeze<SimulatorDimension[]>([
    {
      id: 'resumo',
      title: 'Resumo Analítico',
      subtitle: 'O que o autor expressa essencialmente neste trecho?',
      labelShort: 'Resumo',
      iconName: 'book-open',
      question: 'O que a obra está comunicando em essência?',
      content:
        'No prólogo de Memórias Póstumas, Brás Cubas apresenta sua autobiografia não como um vivo que rememora seus dias, mas como um «defunto autor». Consciente do desinteresse de seu tempo, antecipa a incompreensão tanto dos espíritos graves quanto dos frívolos, destinando seu testemunho irônico à posteridade e aos próprios vermes da sepultura.',
      keyInsights: Object.freeze([
        'Inversão da perspectiva autobiográfica clássica (a morte precede a escrita).',
        'Fusão estilística deliberada entre o cômico («galhofa») e o trágico («melancolia»).',
        'Desdém assumido pela aprovação imediata do público contemporâneo.',
      ]),
    },
    {
      id: 'explicacao',
      title: 'Explicação Aprofundada',
      subtitle: 'Como o autor constrói seu argumento e sua atmosfera?',
      labelShort: 'Explicação',
      iconName: 'network',
      question: 'Como e por que o autor estrutura este pensamento?',
      content:
        'A condição de morto liberta Brás Cubas de toda hipocrisia e pacto social. Ele não precisa bajular patronos, nem zelar por reputação política ou moral. Essa liberdade ontológica manifesta-se formalmente no estilo fragmentado e nas interrupções constantes, subvertendo a convenção naturalista da época com uma ironia implacável que desmascara as ilusões humanas.',
      keyInsights: Object.freeze([
        'A morte opera como dispositivo retórico de franqueza e desobrigação social.',
        'A forma difusa reflete o temperamento oscilante e caprichoso da elite senhorial.',
        'A ironia machadiana atua desarmando o leitor que busca um romance edificante.',
      ]),
    },
    {
      id: 'conceitos',
      title: 'Conceitos-Chave',
      subtitle: 'Quais noções teóricas e filosóficas ancoram o texto?',
      labelShort: 'Conceitos',
      iconName: 'flame',
      question: 'Quais categorias conceituais foram mobilizadas?',
      content:
        'O texto introduz três conceitos fundamentais para a interpretação da obra machadiana: o «Defunto Autor» (narrador soberano fora da jurisdição temporal dos vivos), a «Pena da Galhofa e Tinta da Melancolia» (estética do contraste entre o riso zombeteiro e o abismo existencial) e as «Rabugens de Pessimismo» (ceticismo radical frente às ilusões de progresso).',
      keyInsights: Object.freeze([
        'Defunto Autor vs. Autor Defunto: distinção teórica central estabelecida pelo narrador.',
        'Voluptuosidade do Nada: o deleite estético na constatação do vazio e da vacuidade.',
        'Capricho e Digressão: a recusa à teleologia e ao determinismo sociológico rígido.',
      ]),
    },
    {
      id: 'referencias',
      title: 'Referências e Conexões',
      subtitle: 'Como este trecho dialoga com a tradição literária e filosófica?',
      labelShort: 'Referências',
      iconName: 'link',
      question: 'Com quais outras obras e tradições este trecho dialoga?',
      content:
        'Machado filia-se explicitamente à tradição da sátira menipeia e do romance digressivo do século XVIII. Cita Laurence Sterne (A Vida e as Opiniões de Tristram Shandy, 1759) pelo uso da quebra da ilusão ficcional, Xavier de Maistre (Viagem à Roda do Meu Quarto, 1794) pela exploração do microcosmo íntimo, e dialoga com o ceticismo de Montaigne e o pessimismo de Schopenhauer.',
      keyInsights: Object.freeze([
        'Laurence Sterne: mestre da digressão e do diálogo insolente com o leitor.',
        'Xavier de Maistre: ironia amena e exploração dos movimentos da mente confinada.',
        'Cadernos de lugares-comuns (commonplace books): método de entrecruzamento de citações e referências.',
      ]),
    },
  ]),
})
