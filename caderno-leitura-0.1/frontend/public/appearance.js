(() => {
  'use strict';

  const KEY = 'caderno.aparencia.v1';

  function normalize(value) {
    const source = value && typeof value === 'object' && !Array.isArray(value)
      ? value : {};

    return {
      theme: ['light', 'dark', 'sepia', 'e-ink'].includes(source.theme)
        ? source.theme : 'light',
      style: ['rounded', 'square'].includes(source.style)
        ? source.style : 'rounded',
      font: ['sans', 'serif'].includes(source.font)
        ? source.font : 'sans',
    };
  }

  let current = normalize(null);

  try {
    current = normalize(JSON.parse(window.localStorage.getItem(KEY) || 'null'));
  } catch {
    // O site continua funcionando se o armazenamento estiver bloqueado.
  }

  function apply() {
    const root = document.documentElement;
    root.dataset.theme = current.theme;
    root.dataset.style = current.style;
    root.dataset.font = current.font;
  }

  window.cadernoAppearance = Object.freeze({
    get() {
      return { ...current };
    },

    set(value) {
      current = normalize(value);
      apply();

      try {
        window.localStorage.setItem(KEY, JSON.stringify(current));
        return true;
      } catch {
        return false;
      }
    },
  });

  apply();
})();