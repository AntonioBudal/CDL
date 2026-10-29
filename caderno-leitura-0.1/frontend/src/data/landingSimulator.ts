import type { IconName } from '../types'

export type SimulatorDimensionId = 'resumo' | 'explicacao' | 'conceitos' | 'referencias'

export interface SimulatorDimension {
  id: SimulatorDimensionId
  label: string
  iconName: IconName
  description: string
  content: string
  items: readonly string[]
}

// Trecho dividido em partes; as que têm dimensionId são destacadas quando a aba correspondente está ativa.
export interface PassageSegment {
  text: string
  dimensionId?: SimulatorDimensionId
}

export interface LiteraryWorkSnippet {
  author: string
  title: string
  year: number
  sectionTitle: string
  passage: readonly PassageSegment[]
}

export interface LandingSimulatorData {
  work: LiteraryWorkSnippet
  dimensions: readonly SimulatorDimension[]
}

// Texto do prólogo conforme a edição de 1881 (Projeto Gutenberg, ebook 54829), com ortografia atualizada.
export const LANDING_SIMULATOR_DATA: LandingSimulatorData = Object.freeze({
  work: Object.freeze({
    author: 'Machado de Assis',
    title: 'Memórias Póstumas de Brás Cubas',
    year: 1881,
    sectionTitle: 'Ao leitor',
    passage: Object.freeze<PassageSegment[]>([
      {
        text:
          'Que, no alto do principal de seus livros, confessasse Stendhal havê-lo escrito para cem leitores, coisa é que admira e consterna. O que não admira, nem provavelmente consternará é se este outro livro não tiver os cem leitores de Stendhal, nem cinquenta, nem vinte, e quando muito, dez. Dez? Talvez cinco. Trata-se, na verdade, de ',
      },
      { text: 'uma obra difusa', dimensionId: 'conceitos' },
      { text: ', na qual eu, Brás Cubas, se adotei ' },
      { text: 'a forma livre de um Sterne, de um Lamb, ou de um de Maistre', dimensionId: 'referencias' },
      { text: ', não sei se lhe meti algumas rabugens de pessimismo. Pode ser. ' },
      { text: 'Obra de finado. Escrevi-a com a pena da galhofa e a tinta da melancolia', dimensionId: 'resumo' },
      { text: '; e não é difícil antever o que poderá sair desse conúbio. Acresce que ' },
      {
        text:
          'a gente grave achará no livro umas aparências de puro romance, ao passo que a gente frívola não achará nele o seu romance usual',
        dimensionId: 'explicacao',
      },
      {
        text:
          '; e ei-lo aí fica privado da estima dos graves e do amor dos frívolos, que são as duas colunas máximas da opinião.',
      },
    ]),
  }),
  dimensions: Object.freeze<SimulatorDimension[]>([
    {
      id: 'resumo',
      label: 'Resumo',
      iconName: 'book-open',
      description: 'O que o trecho diz.',
      content:
        'Brás Cubas apresenta o livro. Se Stendhal escreveu para cem leitores, ele espera ter cinco. Diz que a obra é difusa, escrita por um morto, com humor e melancolia, e que não vai agradar nem aos leitores sérios nem aos que buscam um romance comum.',
      items: Object.freeze([]),
    },
    {
      id: 'explicacao',
      label: 'Explicação',
      iconName: 'network',
      description: 'Por que o trecho é escrito assim.',
      content:
        'O narrador escreve depois de morto e não depende da aprovação de ninguém. Por isso zomba do próprio livro e do público antes que alguém o faça. Ao dizer que o livro não serve nem aos graves nem aos frívolos, avisa que não vai seguir as convenções do romance da época.',
      items: Object.freeze([]),
    },
    {
      id: 'conceitos',
      label: 'Conceitos',
      iconName: 'flame',
      description: 'Termos e ideias para guardar.',
      content: '',
      items: Object.freeze([
        'Defunto autor: o narrador escreve depois de morrer. A expressão aparece no capítulo I: "não sou propriamente um autor defunto, mas um defunto autor".',
        'Galhofa e melancolia: a mistura de humor e desencanto que marca o livro.',
        'Obra difusa: narrativa cheia de digressões, sem ordem cronológica rígida.',
      ]),
    },
    {
      id: 'referencias',
      label: 'Referências',
      iconName: 'link',
      description: 'Autores e obras citados.',
      content: '',
      items: Object.freeze([
        'Stendhal, citado pelo número de leitores que esperava ter.',
        'Laurence Sterne, A Vida e as Opiniões de Tristram Shandy (1759-1767).',
        'Charles Lamb, ensaísta inglês.',
        'Xavier de Maistre, Viagem à Roda do Meu Quarto (1794).',
      ]),
    },
  ]),
})
