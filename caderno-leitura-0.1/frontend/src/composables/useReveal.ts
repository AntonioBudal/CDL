import type { Directive } from 'vue'

// Revelação ao rolar da página inicial: o elemento recebe .reveal e, ao entrar na tela, .is-revealed.
// O valor opcional é o atraso em milissegundos (para entradas em cascata). Sem IntersectionObserver ou com
// movimento reduzido, o elemento aparece de imediato.
let observer: IntersectionObserver | null = null

function prefersReducedMotion(): boolean {
  return typeof window !== 'undefined' && window.matchMedia?.('(prefers-reduced-motion: reduce)').matches === true
}

function getObserver(): IntersectionObserver {
  if (!observer) {
    observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (!entry.isIntersecting) continue
          entry.target.classList.add('is-revealed')
          observer?.unobserve(entry.target)
        }
      },
      { rootMargin: '0px 0px -8% 0px', threshold: 0.12 },
    )
  }
  return observer
}

export const vReveal: Directive<HTMLElement, number | undefined> = {
  mounted(el, binding) {
    el.classList.add('reveal')
    if (binding.value) el.style.setProperty('--reveal-delay', `${binding.value}ms`)
    if (typeof IntersectionObserver === 'undefined' || prefersReducedMotion()) {
      el.classList.add('is-revealed')
      return
    }
    getObserver().observe(el)
  },
  unmounted(el) {
    observer?.unobserve(el)
  },
}
