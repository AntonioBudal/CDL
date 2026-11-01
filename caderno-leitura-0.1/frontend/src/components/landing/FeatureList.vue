<script setup lang="ts">
import Icon from '../ui/Icon.vue'
import { vReveal } from '../../composables/useReveal'
import type { IconName } from '../../types'

type Preview = 'livros' | 'partes' | 'marcacoes' | 'revisao' | 'importacao' | 'historico' | 'compartilhar'

interface FeatureItem {
  title: string
  text: string
  icon: IconName
  tone: 'amber' | 'blue' | 'green' | 'rose' | 'violet' | 'teal' | 'slate'
  preview: Preview
  wide: boolean
}

// Cada card corresponde a um recurso existente (routers books, studies, study_highlights, review, imports,
// study_versions, search e sharing no backend).
const features: FeatureItem[] = [
  { title: 'Livros e capítulos', text: 'Um estudo para cada trecho, com a página de referência.', icon: 'book', tone: 'amber', preview: 'livros', wide: true },
  { title: 'Quatro partes por estudo', text: 'Resumo, explicação, conceitos e referências, mais notas livres.', icon: 'grid', tone: 'blue', preview: 'partes', wide: true },
  { title: 'Marcações', text: 'Destaque, citação, nota, pergunta ou trecho oculto, em cinco cores.', icon: 'pencil', tone: 'rose', preview: 'marcacoes', wide: false },
  { title: 'Revisão', text: 'Perguntas e trechos ocultos voltam para revisar; os difíceis primeiro.', icon: 'refresh-cw', tone: 'green', preview: 'revisao', wide: false },
  { title: 'Importação', text: 'Cole um fichamento pronto e confira as quatro partes antes de salvar.', icon: 'upload', tone: 'violet', preview: 'importacao', wide: true },
  { title: 'Histórico e busca', text: 'Compare e restaure versões; encontre qualquer anotação.', icon: 'clock', tone: 'teal', preview: 'historico', wide: true },
  { title: 'Compartilhamento', text: 'Privado por padrão; abra para amigos ou publique com link.', icon: 'users', tone: 'slate', preview: 'compartilhar', wide: true },
]

// Brilho que acompanha o ponteiro dentro do card.
function onPointerMove(event: PointerEvent) {
  const card = event.currentTarget as HTMLElement
  const rect = card.getBoundingClientRect()
  card.style.setProperty('--mx', `${event.clientX - rect.left}px`)
  card.style.setProperty('--my', `${event.clientY - rect.top}px`)
}
</script>

<template>
  <section id="recursos" class="features-section" aria-labelledby="features-heading">
    <h2 v-reveal id="features-heading" class="section-title">O que dá para fazer</h2>

    <ul class="bento">
      <li
        v-for="(item, idx) in features"
        :key="item.title"
        v-reveal="idx * 70"
        class="bento-card"
        :class="[`tone-${item.tone}`, { 'is-wide': item.wide }]"
        @pointermove="onPointerMove"
      >
        <div class="card-head">
          <span class="card-icon" aria-hidden="true"><Icon :name="item.icon" :size="20" /></span>
          <h3 class="card-title">{{ item.title }}</h3>
        </div>
        <p class="card-text">{{ item.text }}</p>

        <div class="preview" aria-hidden="true">
          <template v-if="item.preview === 'livros'">
            <span class="mini-cover m1"></span><span class="mini-cover m2"></span><span class="mini-cover m3"></span>
            <span class="mini-list"><i></i><i></i><i></i></span>
          </template>
          <template v-else-if="item.preview === 'partes'">
            <span class="pill">Resumo</span><span class="pill">Explicação</span><span class="pill">Conceitos</span><span class="pill">Referências</span>
          </template>
          <template v-else-if="item.preview === 'marcacoes'">
            <span class="hl-dot yellow"></span><span class="hl-dot green"></span><span class="hl-dot blue"></span><span class="hl-dot pink"></span><span class="hl-dot purple"></span>
          </template>
          <template v-else-if="item.preview === 'revisao'">
            <span class="rate">Fácil</span><span class="rate">Médio</span><span class="rate is-hard">Difícil</span>
          </template>
          <template v-else-if="item.preview === 'importacao'">
            <span class="raw"><i></i><i></i><i></i><i></i></span>
            <Icon name="arrow-right" :size="18" class="flow-arrow" />
            <span class="split"><i>R</i><i>E</i><i>C</i><i>Ref</i></span>
          </template>
          <template v-else-if="item.preview === 'historico'">
            <span class="search-mock"><Icon name="search" :size="14" /> buscar <kbd>Ctrl K</kbd></span>
            <span class="versions"><i></i><i></i><i></i><i class="is-now"></i></span>
          </template>
          <template v-else>
            <span class="share"><Icon name="lock" :size="14" /> Privado</span>
            <span class="share"><Icon name="users" :size="14" /> Amigos</span>
            <span class="share"><Icon name="link" :size="14" /> Link</span>
          </template>
        </div>
      </li>
    </ul>
  </section>
</template>

<style scoped>
.features-section {
  padding-block: clamp(2.5rem, 6vw, 4.5rem);
  border-bottom: 1px solid var(--color-border-divider, var(--color-border));
}

.section-title {
  font-family: var(--font-reading, "Caderno EB Garamond", serif);
  font-size: clamp(1.75rem, 3vw, 2.4rem);
  font-weight: 600;
  line-height: 1.2;
  margin: 0 0 1.75rem 0;
  color: var(--color-text);
}

.bento {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 1rem;
}

.bento-card {
  --tone: var(--color-accent);
  position: relative;
  grid-column: span 1;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  padding: 1.25rem;
  min-width: 0;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 16px;
  overflow: hidden;
  transition: border-color 0.25s ease, box-shadow 0.25s ease, transform 0.25s ease;
}

.bento-card.is-wide {
  grid-column: span 2;
}

/* Brilho que segue o ponteiro e borda iluminada no hover. */
.bento-card::before {
  content: '';
  position: absolute;
  inset: 0;
  background: radial-gradient(260px circle at var(--mx, 50%) var(--my, 0%), color-mix(in srgb, var(--tone) 14%, transparent), transparent 70%);
  opacity: 0;
  transition: opacity 0.3s ease;
  pointer-events: none;
}

.bento-card:hover {
  border-color: color-mix(in srgb, var(--tone) 60%, var(--color-border));
  box-shadow: 0 0 0 1px color-mix(in srgb, var(--tone) 35%, transparent), 0 18px 36px -22px color-mix(in srgb, var(--tone) 70%, transparent);
  transform: translateY(-3px);
}

.bento-card:hover::before {
  opacity: 1;
}

.tone-amber { --tone: #d97706; }
.tone-blue { --tone: #2563eb; }
.tone-green { --tone: #16a34a; }
.tone-rose { --tone: #e11d48; }
.tone-violet { --tone: #7c3aed; }
.tone-teal { --tone: #0d9488; }
.tone-slate { --tone: #64748b; }

.card-head {
  display: flex;
  align-items: center;
  gap: 0.65rem;
}

.card-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 38px;
  height: 38px;
  flex-shrink: 0;
  border-radius: 10px;
  color: var(--tone);
  background: color-mix(in srgb, var(--tone) 14%, transparent);
  border: 1px solid color-mix(in srgb, var(--tone) 30%, transparent);
}

.card-title {
  margin: 0;
  font-size: 1.05rem;
  font-weight: 700;
  line-height: 1.3;
  color: var(--color-text);
}

.card-text {
  margin: 0;
  font-size: 0.95rem;
  line-height: 1.5;
  color: var(--color-text);
}

/* Mini-prévias */
.preview {
  margin-top: auto;
  padding-top: 0.75rem;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.4rem;
  min-height: 52px;
}

.mini-cover {
  width: 28px;
  height: 40px;
  border-radius: 2px 5px 5px 2px;
  box-shadow: inset 3px 0 0 rgba(0, 0, 0, 0.2);
  transition: transform 0.3s ease;
}

.m1 { background: linear-gradient(160deg, #3b2f2f, #6b3a2e); }
.m2 { background: linear-gradient(160deg, #1f3a4d, #2f6173); }
.m3 { background: linear-gradient(160deg, #3c4a2a, #6a7a3a); }

.bento-card:hover .m1 { transform: translateY(-4px) rotate(-4deg); }
.bento-card:hover .m3 { transform: translateY(-4px) rotate(4deg); }

.mini-list,
.raw,
.split,
.versions {
  display: inline-flex;
  gap: 4px;
}

.mini-list {
  flex-direction: column;
  margin-left: 0.5rem;
}

.mini-list i,
.raw i {
  display: block;
  width: 90px;
  height: 6px;
  border-radius: 3px;
  background: var(--color-border);
}

.raw {
  flex-direction: column;
}

.raw i {
  width: 64px;
}

.pill,
.rate,
.share,
.search-mock {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.25rem 0.6rem;
  border-radius: 999px;
  border: 1px solid var(--color-border);
  color: var(--color-text);
  background: var(--color-page);
}

/* O tom colore só bordas e fundos; o texto fica na cor do tema para manter o contraste. */
.pill:first-child {
  border-color: var(--tone);
  background: color-mix(in srgb, var(--tone) 12%, var(--color-page));
}

.hl-dot {
  width: 26px;
  height: 26px;
  border-radius: 50%;
  border: 2px solid var(--color-surface);
  box-shadow: 0 0 0 1px var(--color-border);
  transition: margin-left 0.25s ease;
}

.hl-dot + .hl-dot {
  margin-left: -10px;
}

.bento-card:hover .hl-dot + .hl-dot {
  margin-left: 2px;
}

.hl-dot.yellow { background: var(--hl-yellow, #fef08a); }
.hl-dot.green { background: var(--hl-green, #bbf7d0); }
.hl-dot.blue { background: var(--hl-blue, #bfdbfe); }
.hl-dot.pink { background: var(--hl-pink, #fbcfe8); }
.hl-dot.purple { background: var(--hl-purple, #e9d5ff); }

.rate.is-hard {
  border-color: var(--tone);
  background: color-mix(in srgb, var(--tone) 12%, var(--color-page));
}

.flow-arrow {
  color: var(--tone);
  transition: transform 0.3s ease;
}

.bento-card:hover .flow-arrow {
  transform: translateX(4px);
}

.split i {
  font-style: normal;
  font-size: 0.7rem;
  font-weight: 700;
  padding: 0.2rem 0.45rem;
  border-radius: 6px;
  color: var(--color-text);
  border: 1px solid color-mix(in srgb, var(--tone) 45%, transparent);
  background: color-mix(in srgb, var(--tone) 12%, transparent);
}

.search-mock kbd {
  font-family: inherit;
  font-size: 0.65rem;
  padding: 0 0.3rem;
  border: 1px solid var(--color-border);
  border-radius: 4px;
}

.versions {
  align-items: center;
  margin-left: 0.5rem;
}

.versions i {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: var(--color-border);
}

.versions i.is-now {
  background: var(--tone);
  box-shadow: 0 0 0 4px color-mix(in srgb, var(--tone) 20%, transparent);
}

@media (max-width: 960px) {
  .bento {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .bento-card,
  .bento-card.is-wide {
    grid-column: span 1;
  }

  .bento-card:first-child {
    grid-column: span 2;
  }
}

@media (max-width: 600px) {
  .bento {
    grid-template-columns: 1fr;
  }

  .bento-card:first-child {
    grid-column: span 1;
  }
}

@media (prefers-reduced-motion: reduce) {
  .bento-card,
  .bento-card:hover,
  .mini-cover,
  .hl-dot,
  .flow-arrow {
    transition: none;
    transform: none;
  }

  .bento-card:hover .m1,
  .bento-card:hover .m3,
  .bento-card:hover .flow-arrow {
    transform: none;
  }
}
</style>
