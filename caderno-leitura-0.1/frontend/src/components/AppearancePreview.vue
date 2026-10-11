<script setup lang="ts">
import { computed } from 'vue'
import StudyTabs from './StudyTabs.vue'
import BookCover from './BookCover.vue'
import Icon from './ui/Icon.vue'
import type { AnalysisSections } from '../types'
import type { AppearancePreferences } from '../appearance'

const props = withDefaults(
  defineProps<{
    preferences?: AppearancePreferences
    isMobileDrawer?: boolean
  }>(),
  {
    isMobileDrawer: false,
  }
)

defineEmits<{
  closeDrawer: []
}>()

const isListView = computed(() => props.preferences?.library === 'list')

const studyPreviewStyle = computed(() => {
  const size = props.preferences?.['reader-size'] ? `${props.preferences['reader-size']}%` : '100%'
  const align = props.preferences?.align || 'left'
  const density = props.preferences?.density
  const lineHeight = density === 'comfortable' ? '1.8' : density === 'compact' ? '1.4' : '1.6'
  
  return {
    fontSize: size,
    textAlign: align as any,
    lineHeight: lineHeight,
    transition: 'font-size 0.15s ease, line-height 0.15s ease',
  }
})

const sections: AnalysisSections = {
  summary:
    'Ler com atenção é dar tempo às ideias. Um ==trecho marcado== ajuda a encontrar uma passagem quando você volta ao estudo. As escolhas de aparência alteram a apresentação deste texto.',
  explanation:
    'A prévia usa as mesmas abas e o mesmo leitor dos estudos. **Negrito comum** continua sendo negrito, independentemente da marcação.',
  concepts:
    '- ==Marcação==: trecho entre dois sinais de igual de cada lado.\n- Preferência: escolha de aparência salva neste navegador.',
  references:
    'Esta é uma prévia de apresentação com feedback imediato, sem alterar seus estudos reais.',
}

const books = [
  { title: 'Memórias Póstumas', author: 'Machado de Assis', year: '1881' },
  { title: 'Grande Sertão: Veredas', author: 'Guimarães Rosa', year: '1956' },
]
</script>

<template>
  <aside
    class="appearance-preview panel"
    :class="{ 'is-drawer': isMobileDrawer }"
    aria-labelledby="appearance-preview-title"
  >
    <div class="preview-header">
      <div class="preview-title-wrap">
        <h2 id="appearance-preview-title">Amostra ao Vivo</h2>
        <span class="preview-badge">Preview</span>
      </div>
      <button
        v-if="isMobileDrawer"
        type="button"
        class="preview-close-btn"
        aria-label="Fechar amostra de leitura"
        @click="$emit('closeDrawer')"
      >
        <Icon name="x" :size="18" />
      </button>
    </div>

    <div class="preview-section">
      <h3 class="preview-subtitle">Leitor de Estudo</h3>
      <div class="preview-study-container" :style="studyPreviewStyle">
        <StudyTabs
          :sections="sections"
          id-prefix="appearance-preview"
        />
      </div>
    </div>

    <div class="preview-section">
      <h3 class="preview-subtitle">Ações & Estados</h3>
      <div class="actions wrap appearance-preview-actions">
        <button type="button" class="primary" @click.prevent>
          Botão primário
        </button>
        <button type="button" class="secondary" @click.prevent>
          Secundário
        </button>
        <button type="button" disabled>
          Indisponível
        </button>
      </div>
    </div>

    <div class="preview-section">
      <h3 class="preview-subtitle">
        Acervo ({{ isListView ? 'Modo Lista' : 'Modo Grade' }})
      </h3>

      <!-- Modo Lista Compacta -->
      <ul v-if="isListView" class="book-list-compact preview-list" role="list">
        <li
          v-for="book in books"
          :key="book.title"
          class="book-list-item"
        >
          <div class="book-list-link">
            <div class="book-list-cover">
              <BookCover :title="book.title" :author="book.author" size="sm" />
            </div>
            <div class="book-list-info">
              <div class="book-list-header">
                <h4 class="book-list-title">{{ book.title }}</h4>
                <span class="book-list-year">({{ book.year }})</span>
              </div>
              <p class="book-list-author">{{ book.author }}</p>
            </div>
          </div>
        </li>
      </ul>

      <!-- Modo Grade -->
      <ul v-else class="book-grid preview-grid">
        <li v-for="(book, index) in books" :key="book.title">
          <article class="book-card has-cover">
            <div class="book-card-cover-wrapper">
              <BookCover :title="book.title" :author="book.author" size="md" />
            </div>
            <span class="book-number" aria-hidden="true">
              {{ String(index + 1).padStart(2, '0') }}
            </span>
            <h4>{{ book.title }}</h4>
            <p>{{ book.author }}</p>
            <span class="card-action">Prévia de cartão</span>
          </article>
        </li>
      </ul>
    </div>
  </aside>
</template>

<style scoped>
.preview-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-unit);
  border-bottom: var(--border-width) solid var(--color-border);
  padding-bottom: calc(var(--space-unit) * 0.5);
}

.preview-title-wrap {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.preview-close-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  min-width: 44px;
  min-height: 44px;
  padding: 0;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm, 6px);
  background: var(--color-surface);
  color: var(--color-text);
  cursor: pointer;
  transition: background-color 0.15s ease, border-color 0.15s ease;
}

.preview-close-btn:hover {
  background: var(--color-surface-hover, var(--color-border));
}

.preview-study-container {
  width: 100%;
}

.appearance-preview.is-drawer {
  border: none;
  box-shadow: none;
  background: transparent;
  padding: 0;
}

.preview-badge {
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  padding: 0.15rem 0.5rem;
  border-radius: var(--radius-sm, 4px);
  background-color: var(--color-bg-subtle, rgba(128, 128, 128, 0.15));
  color: var(--color-text-muted, inherit);
}

.preview-section + .preview-section {
  margin-top: calc(var(--space-unit) * 1.25);
  border-top: var(--border-width) solid var(--color-border);
  padding-top: var(--space-unit);
}

.preview-subtitle {
  margin: 0 0 calc(var(--space-unit) * 0.5) 0;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text-muted, inherit);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.preview-grid {
  grid-template-columns: repeat(auto-fill, minmax(130px, 1fr));
  gap: var(--space-unit);
}

.preview-grid .book-card {
  padding: calc(var(--space-unit) * 0.75);
}

.preview-grid .book-card h4 {
  margin: calc(var(--space-unit) * 0.35) 0 0.2rem 0;
  font-size: 0.95rem;
}

.preview-grid .book-card p {
  margin: 0;
  font-size: 0.8rem;
}

.preview-list {
  display: flex;
  flex-direction: column;
  gap: calc(var(--space-unit) * 0.5);
  padding: 0;
  list-style: none;
}

.preview-list .book-list-item {
  border: var(--border-width) solid var(--color-border);
  border-radius: var(--radius-md, 6px);
  padding: calc(var(--space-unit) * 0.5);
  background-color: var(--color-surface, inherit);
}

.preview-list .book-list-link {
  display: flex;
  gap: calc(var(--space-unit) * 0.75);
  align-items: center;
  text-decoration: none;
  color: inherit;
}

.preview-list .book-list-title {
  margin: 0;
  font-size: 0.9rem;
  font-weight: 600;
}

.preview-list .book-list-author {
  margin: 0.15rem 0 0 0;
  font-size: 0.8rem;
  color: var(--color-text-muted, inherit);
}

.preview-list .book-list-year {
  font-size: 0.8rem;
  color: var(--color-text-muted, inherit);
  margin-left: 0.35rem;
}
</style>