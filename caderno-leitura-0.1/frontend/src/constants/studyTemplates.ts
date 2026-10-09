import type {
  StudyTemplateId,
  StudyTemplateDefinition,
} from '../types.ts'

export const STUDY_TEMPLATES: StudyTemplateDefinition[] = [
  {
    id: 'classico',
    name: 'Fichamento Clássico',
    badgeLabel: 'Fichamento Clássico',
    shortDescription: 'Estrutura tradicional do Leitorum em quatro seções analíticas equilibradas.',
    detailedPurpose: 'Ideal para leitura linear de livros teóricos, ensaios e obras gerais de não-ficção, combinando síntese panorâmica, desenvolvimento das ideias centrais, vocabulário essencial e passagens citadas.',
    sections: {
      summary: {
        key: 'summary',
        label: 'Resumo da Tese',
        hint: 'Síntese global e visão panorâmica da proposição do autor.',
        skeleton: '### Síntese Panorâmica\n\n- Tese central do trecho ou capítulo:\n- Questão motivadora:\n- Linha geral de desenvolvimento:\n',
      },
      explanation: {
        key: 'explanation',
        label: 'Desenvolvimento e Explicação',
        hint: 'Articulação dos passos do raciocínio e fundamentação das ideias.',
        skeleton: '### Articulação das Ideias\n\n- Passos fundamentais do raciocínio:\n- Contexto e ilustrações mobilizadas:\n- Desdobramentos conceituais:\n',
      },
      concepts: {
        key: 'concepts',
        label: 'Conceitos-Chave',
        hint: 'Vocabulário essencial, termos técnicos e definições constitutivas.',
        skeleton: '### Conceitos e Definições\n\n- Termo principal: definição e alcance.\n- Termos secundários relacionados:\n- Distinções conceituais importantes:\n',
      },
      references: {
        key: 'references',
        label: 'Citações e Referências',
        hint: 'Passagens literais, notas de apoio e diálogos bibliográficos.',
        skeleton: '### Citações e Fontes\n\n> "Trecho representativo ou citação literal"\n\n- Referências externas citadas pelo autor:\n- Conexões com outras fontes ou leituras:\n',
      },
    },
  },
  {
    id: 'conceito',
    name: 'Estudo de Conceito',
    badgeLabel: 'Estudo de Conceito',
    shortDescription: 'Dissecação analítica, etimológica e prática de uma ideia ou termo.',
    detailedPurpose: 'Desenhado para o exame aprofundado de termos técnicos, conceitos filosóficos ou categorias teóricas, delimitando sua definição essencial, genealogia, limites de aplicação e contra-exemplos.',
    sections: {
      summary: {
        key: 'summary',
        label: 'Definição Essencial',
        hint: 'Delimitação positiva e negativa do conceito: o que é e o que não é.',
        skeleton: '### Definição Essencial\n\n- O que o conceito expressa:\n- O que o conceito explicitamente NÃO é (delimitação negativa):\n- Fórmula sintética ou enunciado-núcleo:\n',
      },
      explanation: {
        key: 'explanation',
        label: 'Origem e Contexto Histórico',
        hint: 'Raiz etimológica, genealogia histórica e autores que o formularam.',
        skeleton: '### Genealogia e Contexto\n\n- Raiz etimológica ou termo original:\n- Contexto histórico e debate de surgimento:\n- Autores fundamentais associados:\n',
      },
      concepts: {
        key: 'concepts',
        label: 'Aplicações e Manifestações',
        hint: 'Casos de uso prático, manifestações concretas e exemplos operacionais.',
        skeleton: '### Aplicações Concretas\n\n- Exemplo operacional primário:\n- Situações em que o conceito é aplicável:\n- Consequências teóricas de sua adoção:\n',
      },
      references: {
        key: 'references',
        label: 'Contrapontos e Limites',
        hint: 'Críticas teóricas, fronteiras de validade e termos em tensão dialética.',
        skeleton: '### Limitações e Tensões\n\n- Objeções e críticas dirigidas ao conceito:\n- Fronteiras além das quais o conceito perde eficácia:\n- Conceitos rivais ou antíteses diretas:\n',
      },
    },
  },
  {
    id: 'argumento',
    name: 'Reconstrução de Argumento',
    badgeLabel: 'Reconstrução de Argumento',
    shortDescription: 'Exame lógico da validade, premissas, objeções e conclusões.',
    detailedPurpose: 'Voltado para textos persuasivos, teses filosóficas e ensaios opinativos, permitindo mapear formalmente a cadeia inferencial, avaliar a força das premissas e antecipar contra-argumentos.',
    sections: {
      summary: {
        key: 'summary',
        label: 'Tese Central',
        hint: 'A proposição fundamental que o autor busca provar ou sustentar.',
        skeleton: '### Proposição Principal\n\n- Tese defendida:\n- O que está em jogo caso a tese seja verdadeira:\n- Âmbito e alcance da afirmação:\n',
      },
      explanation: {
        key: 'explanation',
        label: 'Premissas e Justificativas',
        hint: 'Encadeamento de passos lógicos, dados e evidências de sustentação.',
        skeleton: '### Cadeia Argumentativa\n\n1. Premissa 1 (Ponto de partida):\n2. Premissa 2 (Dado empírico ou inferência intermediária):\n3. Premissa 3 (Condição de necessidade):\n- Vínculo lógico entre as premissas:\n',
      },
      concepts: {
        key: 'concepts',
        label: 'Objeções Possíveis',
        hint: 'Fragilidades lógicas, contra-exemplos e pontos de ataque.',
        skeleton: '### Fragilidades e Objeções\n\n- Principal objeção antecipada:\n- Contra-exemplo potencial:\n- Como o autor responde (ou poderia responder) à objeção:\n',
      },
      references: {
        key: 'references',
        label: 'Conclusão Dialética',
        hint: 'Desfecho analítico, força da inferência e síntese do leitor.',
        skeleton: '### Veredito Lógico\n\n- A inferência é válida e sólida?\n- Síntese dialética do argumento:\n- Implicações práticas da conclusão:\n',
      },
    },
  },
  {
    id: 'comparativo',
    name: 'Análise Comparativa',
    badgeLabel: 'Análise Comparativa',
    shortDescription: 'Confronto estruturado entre duas obras, autores ou perspectivas rivais.',
    detailedPurpose: 'Ideal para dialogar leituras sobre um mesmo tema, evidenciando pontos de convergência pacífica, zonas de atrito irredutível e construindo uma síntese avaliativa própria do leitor.',
    sections: {
      summary: {
        key: 'summary',
        label: 'Objeto de Comparação',
        hint: 'Definição dos dois polos comparados e o problema comum de partida.',
        skeleton: '### Polos de Comparação\n\n- Perspectiva A (Obra / Autor):\n- Perspectiva B (Obra / Autor):\n- Problema ou objeto comum compartilhado:\n',
      },
      explanation: {
        key: 'explanation',
        label: 'Pontos de Convergência',
        hint: 'Afinações, concordâncias de premissas e acordos teóricos.',
        skeleton: '### Convergências Fundamentais\n\n- Onde as duas perspectivas concordam:\n- Premissas e diagnósticos compartilhados:\n- Linguagem ou métodos em comum:\n',
      },
      concepts: {
        key: 'concepts',
        label: 'Pontos de Divergência',
        hint: 'Distinções fundamentais, disputas terminológicas e linhas de conflito.',
        skeleton: '### Linhas de Divergência\n\n- Ponto de cisão principal:\n- Onde a perspectiva A discorda da B:\n- As razões por trás do desacordo:\n',
      },
      references: {
        key: 'references',
        label: 'Síntese Crítica',
        hint: 'Avaliação do leitor: conciliação, superioridade ou superação dialética.',
        skeleton: '### Avaliação do Leitor\n\n- Qual das abordagens se sustenta com maior vigor?\n- É possível uma conciliação ou superação das duas teses?\n- Conclusão articulada do estudo:\n',
      },
    },
  },
  {
    id: 'resenha',
    name: 'Resenha Crítica',
    badgeLabel: 'Resenha Crítica',
    shortDescription: 'Apreciação crítica com contexto histórico, julgamento de valor e limites.',
    detailedPurpose: 'Estrutura para ensaios críticos, apreciação de lançamentos ou reavaliação de clássicos, integrando circunstância do autor, análise do mérito, identificação de vieses e posicionamento pessoal.',
    sections: {
      summary: {
        key: 'summary',
        label: 'Contexto e Circunstância',
        hint: 'Apresentação da obra, autor, época e motivação histórica.',
        skeleton: '### Contextualização da Obra\n\n- Dados da obra e do autor:\n- Circunstância histórica e intelectual do lançamento:\n- Objetivo declarado pelo autor:\n',
      },
      explanation: {
        key: 'explanation',
        label: 'Julgamento da Tese',
        hint: 'Avaliação do mérito, solidez, originalidade e contribuição.',
        skeleton: '### Apreciação do Mérito\n\n- Principais virtudes da tese:\n- Originalidade e estilo da exposição:\n- Contribuição teórica ou cultural relevante:\n',
      },
      concepts: {
        key: 'concepts',
        label: 'Limitações e Pontos Cegos',
        hint: 'Omissões relevantes, pressupostos não examinados e vieses.',
        skeleton: '### Fragilidades e Omissões\n\n- O que o autor deixou de considerar:\n- Premissas não examinadas ou anacrônicas:\n- Limites evidentes do escopo:\n',
      },
      references: {
        key: 'references',
        label: 'Posicionamento Pessoal',
        hint: 'Veredito fundamentado do leitor, recomendações e diálogo com outros estudos.',
        skeleton: '### Posicionamento Crítico\n\n- Veredito geral do leitor:\n- Para quem a leitura é recomendada:\n- Diálogo e ecos com meus outros estudos:\n',
      },
    },
  },
]

export const STUDY_TEMPLATE_MAP: Record<StudyTemplateId, StudyTemplateDefinition> = {
  classico: STUDY_TEMPLATES[0],
  conceito: STUDY_TEMPLATES[1],
  argumento: STUDY_TEMPLATES[2],
  comparativo: STUDY_TEMPLATES[3],
  resenha: STUDY_TEMPLATES[4],
}

export function getStudyTemplate(templateId?: string | null): StudyTemplateDefinition {
  if (!templateId || !(templateId in STUDY_TEMPLATE_MAP)) {
    return STUDY_TEMPLATE_MAP.classico
  }
  return STUDY_TEMPLATE_MAP[templateId as StudyTemplateId]
}
