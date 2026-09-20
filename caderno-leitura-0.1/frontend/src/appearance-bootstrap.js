(() => {
  'use strict';

  if (window.cadernoAppearance?.version === 72) return;

  const KEY = 'caderno.aparencia.v2';
  const LEGACY = 'caderno.aparencia.v1';

  const field = (key, group, label, options) => Object.freeze({
    key,
    group,
    label,
    options: Object.freeze(options.map(option => Object.freeze(option))),
  });

  // A primeira opção de cada campo é seu valor padrão.
  const fields = Object.freeze([
    field('theme', 'Aparência básica', 'Tema', [
      ['porcelana', 'Porcelana — Claro clássico'],
      ['breu', 'Breu — OLED'],
      ['pergaminho', 'Pergaminho — Sépia real'],
      ['e-ink', 'E-Ink — Preto e branco'],
      ['vespera', 'Véspera — Dracula'],
      ['solario', 'Solário — Solarized Light'],
      ['fiorde', 'Fiorde — Nord'],
      ['vinil', 'Vinil — Gruvbox'],
      ['sequoia', 'Sequoia — Floresta'],
      ['voltagem', 'Voltagem — Cyber'],
    ]),
    field('accent', '1. Cor de destaque', 'Cor', [
      ['theme', 'Cor original do tema'],
      ['blue', 'Azul'],
      ['green', 'Verde'],
      ['purple', 'Roxo'],
      ['orange', 'Laranja'],
    ]),
    field('density', '2. Densidade', 'Espaçamento da interface', [
      ['standard', 'Padrão'],
      ['compact', 'Compacta'],
      ['comfortable', 'Confortável'],
    ]),
    field('align', '3. Leitura', 'Alinhamento dos parágrafos', [
      ['left', 'Esquerda'],
      ['justify', 'Justificado'],
    ]),
    field(
      'font',
      '3. Leitura',
      'Fonte de leitura',
      window.cadernoFontCatalog.options
    ),
    field('highlight', '4. Marcação', 'Destaque de ==texto==', [
      ['background', 'Fundo colorido'],
      ['underline', 'Sublinhado'],
      ['bold', 'Negrito colorido'],
    ]),
    field('reader-size', '3. Leitura', 'Tamanho do texto',
      Array.from({ length: 11 }, (_, index) => {
        const size = String(100 + index * 10);
        return [size, `${size}%`];
      }),
    ),
    field('library', '5. Acervo', 'Disposição dos livros', [
      ['grid', 'Grade'],
      ['list', 'Lista com autor'],
    ]),
    field('container', '6. Largura da interface', 'Contêiner', [
      ['contained', 'Contido e centralizado'],
      ['fluid', 'Fluido'],
    ]),
    field('superclass', '7. Superclasse de Interface', 'Superclasse', [
      ['none', 'Nenhuma — Padrão'],
      ['zero-g', 'Zero-G — Flutuante & Magnética'],
      ['mecanica', 'Mecânica — Tátil & Precisa'],
      ['invisivel', 'Invisível — Silenciosa & Funcional'],
      ['dimensional', 'Dimensional — Cinemática & Profunda'],
      ['monolitica', 'Monolítica — Monumental & Lítica'],
    ]),
    field('superclass-intensity', '7. Superclasse de Interface', 'Intensidade da física', [
      ['standard', 'Padrão (1.0x)'],
      ['subtle', 'Sutil (0.5x)'],
      ['high', 'Alta (1.5x)'],
      ['off', 'Desativada (0.0x)'],
    ]),
  ]);

  const record = value =>
    value && typeof value === 'object' && !Array.isArray(value)
      ? value
      : {};

  function normalize(value) {
  const source = record(value);

  const aliases = {
    theme: {
      light: 'porcelana',
      dark: 'breu',
      sepia: 'pergaminho',
    },
    font: {
      sans: 'inter',
      serif: 'literata',
      dyslexic: 'opendyslexic',
    },
  };

  return Object.fromEntries(fields.map(item => {
    const raw = source[item.key];

    const candidate = typeof raw === 'string'
      ? (aliases[item.key]?.[raw] ?? raw)
      : undefined;

    return [
      item.key,
      item.options.some(([option]) => option === candidate)
        ? candidate
        : item.options[0][0],
    ];
  }));
}

  let current = normalize(null);

  try {
    const raw = window.localStorage.getItem(KEY)
      ?? window.localStorage.getItem(LEGACY);

    current = normalize(JSON.parse(raw || 'null'));
    window.localStorage.setItem(KEY, JSON.stringify(current));
  } catch {
    // Dados inválidos ou armazenamento bloqueado: usar os padrões.
  }

  function apply() {
    for (const [key, value] of Object.entries(current)) {
      document.documentElement.setAttribute(`data-${key}`, value);
    }

    document.documentElement.removeAttribute('data-style');
    document.documentElement.removeAttribute('data-surface');
    document.documentElement.removeAttribute('data-button-style');
    document.documentElement.removeAttribute('data-motion');
    document.documentElement.removeAttribute('data-button-width');
    document.documentElement.removeAttribute('data-tabs');

    for (const sc of ['zero-g', 'mecanica', 'invisivel', 'dimensional', 'monolitica']) {
      document.documentElement.classList.toggle(`superclass-${sc}`, current.superclass === sc);
    }

    for (const weight of [400, 700]) {
  const id = `reading-font-${weight}`;
  let link = document.getElementById(id);

  if (!link) {
    link = document.createElement('link');
    link.id = id;
    link.rel = 'preload';
    link.as = 'font';
    link.type = 'font/woff2';
    link.crossOrigin = 'anonymous';
    document.head.append(link);
  }

  link.href =
    `/fonts/${current.font}/${window.cadernoFontCatalog.version}` +
    `/latin-${weight}-normal.woff2`;
}
  }

  function factoryReset() {
    current = normalize(null);
    apply();

    try {
      window.localStorage.removeItem(LEGACY);
      window.localStorage.setItem(KEY, JSON.stringify(current));
      return true;
    } catch {
      return false;
    }
  }

  function cleanOrphanKeys() {
    let count = 0;
    try {
      if (window.localStorage.getItem(LEGACY) !== null) {
        window.localStorage.removeItem(LEGACY);
        count++;
      }
      const orphans = [
        'caderno.style',
        'caderno.surface',
        'caderno.button-style',
        'caderno.motion',
        'caderno.button-width',
        'caderno.tabs',
      ];
      for (const k of orphans) {
        if (window.localStorage.getItem(k) !== null) {
          window.localStorage.removeItem(k);
          count++;
        }
      }
    } catch {
      // Armazenamento pode estar bloqueado
    }
    return count;
  }

  // Purga de chaves obsoletas na inicialização
  cleanOrphanKeys();

  window.cadernoAppearance = Object.freeze({
    version: 72,
    fields,

    get: () => ({ ...current }),

    set(patch) {
      current = normalize({ ...current, ...record(patch) });
      apply();

      try {
        window.localStorage.setItem(KEY, JSON.stringify(current));
        return true;
      } catch {
        return false;
      }
    },

    factoryReset,
    cleanOrphanKeys,
  });

  apply();
})();