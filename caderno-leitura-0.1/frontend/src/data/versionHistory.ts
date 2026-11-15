/**
 * F0.12.01 (spec 114): linha do tempo das versões do Leitorum, escrita à mão a partir dos documentos do projeto
 * (nada do acervo do usuário).
 *
 * Fontes: docs/HISTORICO-ROADMAPS.md (0.1–0.4), docs/contexto/ROADMAP-0.3.md … ROADMAP-0.9.md (data de emissão e lista de
 * features), docs/contexto/HANDOFF.md (0.10 e 0.11, com datas de fecho), docs/contexto/ROADMAP-0.12.md (0.12).
 * "started" é a data de emissão do roadmap (ou do commit de marco, na 0.1 e na 0.2); "closed", quando o documento a
 * registra. Ao concluir cada feature do 0.12, marcar `done: true` e subir o `alpha.N` em VERSION (HANDOFF §2).
 */

export type RoadmapStatus = 'closed' | 'in_progress'

export interface RoadmapFeature {
  id: string
  title: string
  done: boolean
}

export interface RoadmapEntry {
  version: string // SemVer da versão fechada (ou a que será, se em andamento)
  roadmap: string // "0.11"
  title: string
  started: string // AAAA-MM-DD
  closed?: string
  status: RoadmapStatus
  featureCount: number | null // null quando os documentos não dão o número
  highlights: string[]
  features?: RoadmapFeature[] // só no roadmap em andamento
}

export const VERSION_HISTORY: RoadmapEntry[] = [
  {
    version: '0.12.0',
    roadmap: '0.12',
    title: 'Comunidade, ecossistema e versões',
    started: '2026-11-14',
    status: 'in_progress',
    featureCount: 10,
    highlights: [
      'Versão no rodapé e esta linha do tempo',
      'Estudos publicados na web, em páginas que os buscadores encontram',
      'Importar de outros serviços de leitura e feeds para acompanhar publicações',
      'Livro exportável como quadro (JSON Canvas), revisão sobre imagens e círculos de leitura sem spoilers',
      'Nomes de telas mais simples e ajustes de usabilidade',
    ],
    features: [
      { id: 'F0.12.01', title: 'Versão no rodapé e evolução das versões', done: true },
      { id: 'F0.12.02', title: 'Estudos publicados na web', done: true },
      { id: 'F0.12.03', title: 'Importadores (Readwise, Goodreads, StoryGraph, Omnivore, BookWyrm)', done: true },
      { id: 'F0.12.04', title: 'Feeds RSS, Atom e JSON', done: true },
      { id: 'F0.12.05', title: 'Exportar o livro em JSON Canvas', done: true },
      { id: 'F0.12.06', title: 'Oclusão de imagem para revisão', done: true },
      { id: 'F0.12.07', title: 'Círculos de leitura com trava anti-spoiler', done: true },
      { id: 'F0.12.08', title: 'Nomes mais simples nas telas', done: true },
      { id: 'F0.12.09', title: 'Seletor de idioma (fundação)', done: false },
      { id: 'F0.12.10', title: 'Pequenas melhorias de usabilidade', done: false },
    ],
  },
  {
    version: '0.11.0',
    roadmap: '0.11',
    title: 'Motores de estudo',
    started: '2026-11-09',
    closed: '2026-11-14',
    status: 'closed',
    featureCount: 11,
    highlights: [
      'Estados de leitura (quero ler, lendo, lido) e bandeja de triagem por capítulo',
      'Destaques do Kindle, do Kobo, do KOReader e envio automático do Readest',
      'ISBN sob demanda e referências em ABNT, APA, BibTeX e CSL-JSON',
      'Léxico de conceitos, validador de paráfrase e revisão com peso de dificuldade',
      'Recorte e giro da foto na digitalização',
      'Cadernos de síntese que mostram trechos atualizados dos estudos',
    ],
  },
  {
    version: '0.10.0',
    roadmap: '0.10',
    title: 'Redesenho, segurança e ergonomia',
    started: '2026-11-01',
    closed: '2026-11-07',
    status: 'closed',
    featureCount: 10,
    highlights: [
      'Cabeçalho mais leve e botões neutros',
      'Segurança reforçada: política de conteúdo, conferência de origem, exclusão segura',
      'Painel de Sistema com integridade do banco e backups',
      'Revisão por níveis de dificuldade e sessões de 5, 10 ou 15 itens',
      'Cópia de citações em ABNT e leituras em comum com amigos',
    ],
  },
  {
    version: '0.9.0',
    roadmap: '0.9',
    title: 'Revisão geral de interface e estabilização',
    started: '2026-10-18',
    status: 'closed',
    featureCount: 5,
    highlights: [
      'Navegação global e estrutura que se adapta ao celular',
      'Página do livro mais leve no celular',
      'Leitor de estudos mais seguro e refinado',
      'Acessibilidade e cores que funcionam em todos os temas',
    ],
  },
  {
    version: '0.8.0',
    roadmap: '0.8',
    title: 'Curadoria editorial de cada área',
    started: '2026-10-10',
    status: 'closed',
    featureCount: 10,
    highlights: [
      'Biblioteca ativa e novo cabeçalho global',
      'Destaques como margens vivas e Central de Revisão redesenhada',
      'Mesa de Triagem, Ateliê de Fichamento e Lixeira com salvaguardas',
      'Página inicial pública para quem ainda não tem conta',
    ],
  },
  {
    version: '0.7.0',
    roadmap: '0.7',
    title: 'A experiência de estudos',
    started: '2026-10-03',
    status: 'closed',
    featureCount: 15,
    highlights: [
      'Visões em grade, lista, árvore, mapa e quadro livre redesenhadas',
      'Central de revisão com perguntas e lacunas',
      'Biblioteca de destaques e menções entre estudos',
      'Caixa de entrada de capturas e sessões de estudo',
      'Modelos de estudo prontos',
    ],
  },
  {
    version: '0.6.0',
    roadmap: '0.6',
    title: 'Leitura ativa e presença pública',
    started: '2026-09-27',
    status: 'closed',
    featureCount: 10,
    highlights: [
      'Importação inteligente de fichamentos',
      'Seleção de texto com ações e leitura ativa',
      'Histórico automático das versões de cada estudo',
      'Página de apoio e segurança da aplicação e da autenticação',
    ],
  },
  {
    version: '0.5.0',
    roadmap: '0.5',
    title: 'Multiusuário e social',
    started: '2026-09-20',
    status: 'closed',
    featureCount: 10,
    highlights: [
      'Várias contas na mesma instalação, com login próprio ou pelo Google',
      'Sincronização entre aparelhos',
      'Perfil, amizades e compartilhamento com permissões',
      'Administração, notificações e ciclo de vida da conta',
    ],
  },
  {
    version: '0.4.0',
    roadmap: '0.4',
    title: 'Navegação espacial e relações',
    started: '2026-09-19',
    status: 'closed',
    featureCount: 10,
    highlights: [
      'Várias formas de ver o acervo e quadro de estudos',
      'Relações entre estudos e agrupamento visual',
      'Painel 2.0 e busca global',
      'Sistema visual profissional e movimento',
    ],
  },
  {
    version: '0.3.0',
    roadmap: '0.3',
    title: 'Gestão, visualização e produtividade',
    started: '2026-09-15',
    closed: '2026-09-19',
    status: 'closed',
    featureCount: 10,
    highlights: [
      'Edição completa, lixeira e capas',
      'Busca, ordenação e categorias',
      'Painel com calendário e linha do tempo',
      'Exportação em Markdown e backups confiáveis',
    ],
  },
  {
    version: '0.2.0',
    roadmap: '0.2',
    title: 'Acesso em rede e aparência',
    started: '2026-09-15',
    status: 'closed',
    featureCount: null,
    highlights: [
      'Uso pelo celular na rede de casa',
      'Personalização da aparência',
    ],
  },
  {
    version: '0.1.0',
    roadmap: '0.1',
    title: 'Base inicial',
    started: '2026-09-10',
    status: 'closed',
    featureCount: 8,
    highlights: [
      'Livros, capítulos e estudos no próprio computador',
      'Leitura em quatro partes: resumo, explicação, conceitos e referências',
    ],
  },
]
