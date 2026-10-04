<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'
import type { StudySummary, StudyRelationType } from '../../../types.ts'
import Icon from '../../ui/Icon.vue'
import { createStudy as apiCreateStudy, createStudyRelation as apiCreateRelation, errorMessage } from '../../../services/api.ts'

interface Props {
  isOpen: boolean
  position: { x: number; y: number }
  chapterId: number
  bookId: number
  connectedSourceId?: number | null
}

const props = withDefaults(defineProps<Props>(), {
  connectedSourceId: null,
})

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'created', payload: {
    study: StudySummary
    initialRelation?: {
      sourceId: number
      targetId: number
      relationType: StudyRelationType
    }
  }): void
}>()

const title = ref('')
const sectionKey = ref<'summary' | 'concepts' | 'explanation'>('summary')
const sectionContent = ref('')
const isSubmitting = ref(false)
const error = ref<string | null>(null)
const titleInputRef = ref<HTMLInputElement | null>(null)

const cardStyle = computed(() => {
  const maxX = typeof window !== 'undefined' ? window.innerWidth - 300 : props.position.x
  const maxY = typeof window !== 'undefined' ? window.innerHeight - 340 : props.position.y
  return {
    left: `${Math.min(maxX, Math.max(16, props.position.x))}px`,
    top: `${Math.min(maxY, Math.max(16, props.position.y))}px`,
  }
})

watch(
  () => props.isOpen,
  (open) => {
    if (open) {
      title.value = ''
      sectionContent.value = ''
      sectionKey.value = 'summary'
      error.value = null
      nextTick(() => {
        titleInputRef.value?.focus()
      })
    }
  },
  { immediate: true }
)

async function handleSubmit() {
  const trimmedTitle = title.value.trim()
  if (!trimmedTitle) {
    error.value = 'Informe um título para o estudo.'
    return
  }

  isSubmitting.value = true
  error.value = null

  try {
    const payload: any = {
      chapter_id: props.chapterId,
      title: trimmedTitle,
      location: 'Mapa Conceitual',
      source_response: '',
      notes: '',
      summary: '',
      explanation: '',
      concepts: '',
      references: '',
    }

    // Preenche a seção selecionada garantindo conformidade com require_analysis
    const initialText = sectionContent.value.trim() || `Ideia registrada no mapa: ${trimmedTitle}`
    payload[sectionKey.value] = initialText

    const createdStudy = await apiCreateStudy(payload)

    let createdRelPayload: any = undefined

    // Se iniciado a partir de uma conexão atômica
    if (props.connectedSourceId) {
      try {
        await apiCreateRelation(props.connectedSourceId, {
          target_study_id: createdStudy.id,
          relation_type: 'desdobramento_de',
          description: 'Desdobramento criado diretamente no mapa',
        })
        createdRelPayload = {
          sourceId: props.connectedSourceId,
          targetId: createdStudy.id,
          relationType: 'desdobramento_de' as StudyRelationType,
        }
      } catch (relErr) {
        console.warn('[MapQuickCreateCard] Falha ao criar relação atômica inicial:', relErr)
      }
    }

    emit('created', {
      study: createdStudy,
      initialRelation: createdRelPayload,
    })
    emit('close')
  } catch (err) {
    error.value = errorMessage(err)
  } finally {
    isSubmitting.value = false
  }
}

function handleKeydown(e: KeyboardEvent) {
  if (e.key === 'Escape') {
    e.preventDefault()
    emit('close')
  } else if (e.key === 'Enter' && (e.ctrlKey || e.metaKey || e.target === titleInputRef.value)) {
    e.preventDefault()
    handleSubmit()
  }
}
</script>

<template>
  <div
    v-if="isOpen"
    class="map-quick-create-backdrop"
    @click.self="emit('close')"
    @keydown="handleKeydown"
  >
    <div
      class="map-quick-create-card quick-create-card"
      :style="cardStyle"
      role="dialog"
      aria-label="Criar novo estudo no mapa"
    >
      <div class="card-header">
        <div class="header-title-group">
          <Icon name="plus" :size="15" class="header-icon" />
          <h4 class="card-title">Novo Estudo no Grafo</h4>
        </div>
        <button
          type="button"
          class="card-close-btn"
          title="Fechar"
          aria-label="Fechar"
          @click="emit('close')"
        >
          <Icon name="x" :size="14" />
        </button>
      </div>

      <div v-if="error" class="card-error-banner" role="alert">
        {{ error }}
      </div>

      <!-- Campo Título com autofocus -->
      <div class="form-group">
        <label for="quick-title-input" class="form-label">Título da Ideia:</label>
        <input
          id="quick-title-input"
          ref="titleInputRef"
          v-model="title"
          type="text"
          class="form-input"
          placeholder="Ex.: Síntese Dialética..."
          maxlength="150"
          :disabled="isSubmitting"
        />
      </div>

      <!-- Seletor de Seção Analítica Inicial -->
      <div class="form-group">
        <label class="form-label">Seção de Partida:</label>
        <div class="section-pills-row" role="radiogroup">
          <button
            type="button"
            class="section-pill-btn action-btn touch-target"
            :class="{ 'is-selected': sectionKey === 'summary' }"
            role="radio"
            :aria-checked="sectionKey === 'summary'"
            @click="sectionKey = 'summary'"
          >
            Resumo
          </button>
          <button
            type="button"
            class="section-pill-btn action-btn touch-target"
            :class="{ 'is-selected': sectionKey === 'concepts' }"
            role="radio"
            :aria-checked="sectionKey === 'concepts'"
            @click="sectionKey = 'concepts'"
          >
            Conceitos
          </button>
          <button
            type="button"
            class="section-pill-btn action-btn touch-target"
            :class="{ 'is-selected': sectionKey === 'explanation' }"
            role="radio"
            :aria-checked="sectionKey === 'explanation'"
            @click="sectionKey = 'explanation'"
          >
            Explicação
          </button>
        </div>
      </div>

      <!-- Texto inicial breve -->
      <div class="form-group">
        <label for="quick-content-input" class="form-label">Anotação Breve (opcional):</label>
        <textarea
          id="quick-content-input"
          v-model="sectionContent"
          rows="2"
          class="form-textarea"
          placeholder="Esboço rápido do argumento..."
          :disabled="isSubmitting"
        ></textarea>
      </div>

      <!-- Ações do Card -->
      <div class="card-footer">
        <button
          type="button"
          class="button ghost action-btn touch-target"
          :disabled="isSubmitting"
          @click="emit('close')"
        >
          Cancelar
        </button>
        <button
          type="button"
          class="button primary action-btn touch-target"
          :disabled="isSubmitting || !title.trim()"
          @click="handleSubmit"
        >
          {{ isSubmitting ? 'Salvando...' : 'Adicionar ao Grafo' }}
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.map-quick-create-backdrop {
  position: fixed;
  inset: 0;
  z-index: 1000;
  background-color: rgba(0, 0, 0, 0.2);
  display: flex;
}

.map-quick-create-card {
  position: absolute;
  width: 290px;
  background: var(--color-surface, #ffffff);
  border: 1px solid var(--color-border, #e2e8f0);
  border-radius: var(--radius-card, 8px);
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.2);
  padding: 0.9rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  animation: cardFadeIn 0.15s ease-out;
}

@keyframes cardFadeIn {
  from {
    opacity: 0;
    transform: scale(0.96) translateY(-4px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.header-title-group {
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.header-icon {
  color: var(--color-accent);
}

.card-title {
  margin: 0;
  font-size: 0.88rem;
  font-weight: 600;
  color: var(--color-inverse-bg, #0f172a);
}

.card-close-btn {
  background: transparent;
  border: none;
  color: var(--color-muted);
  cursor: pointer;
  padding: 0.2rem;
  border-radius: 4px;
}

.card-error-banner {
  padding: 0.35rem 0.5rem;
  font-size: 0.75rem;
  background-color: color-mix(in srgb, var(--color-danger, #ef4444) 12%, var(--color-surface));
  color: var(--color-danger, #ef4444);
  border-radius: 4px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}

.form-label {
  font-size: 0.73rem;
  font-weight: 600;
  color: var(--color-muted, #64748b);
}

.form-input,
.form-textarea {
  width: 100%;
  padding: 0.35rem 0.55rem;
  border: 1px solid var(--color-border, #cbd5e1);
  border-radius: 4px;
  font-size: 0.8rem;
  background: var(--color-surface);
  color: var(--color-inverse-bg);
  box-sizing: border-box;
}

.form-textarea {
  resize: none;
  font-family: inherit;
}

.form-input:focus,
.form-textarea:focus {
  outline: none;
  border-color: var(--color-accent);
  box-shadow: 0 0 0 1px var(--color-accent);
}

.section-pills-row {
  display: flex;
  gap: 0.3rem;
}

.section-pill-btn {
  flex: 1;
  padding: 0.25rem 0.4rem;
  border: 1px solid var(--color-border, #e2e8f0);
  background: var(--color-surface);
  border-radius: 4px;
  font-size: 0.72rem;
  color: var(--color-muted);
  cursor: pointer;
  text-align: center;
  transition: all 0.15s ease;
}

.section-pill-btn:hover {
  border-color: var(--color-accent);
  color: var(--color-inverse-bg);
}

.section-pill-btn.is-selected {
  background: color-mix(in srgb, var(--color-accent) 12%, var(--color-surface));
  border-color: var(--color-accent);
  color: var(--color-accent);
  font-weight: 600;
}

.card-footer {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.4rem;
  margin-top: 0.2rem;
}

.button {
  padding: 0.35rem 0.65rem;
  border-radius: 4px;
  font-size: 0.76rem;
  font-weight: 600;
  cursor: pointer;
  border: 1px solid transparent;
  transition: all 0.15s ease;
}

.button.primary {
  background: var(--color-accent, #3b82f6);
  color: #ffffff;
}

.button.primary:hover:not(:disabled) {
  filter: brightness(1.08);
}

.button.primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.button.ghost {
  background: transparent;
  color: var(--color-muted);
}

.button.ghost:hover {
  background: var(--color-surface-hover);
  color: var(--color-inverse-bg);
}

@media (max-width: 768px) {
  .map-quick-create-card {
    position: fixed !important;
    left: 1rem !important;
    right: 1rem !important;
    bottom: 1rem !important;
    top: auto !important;
    width: auto;
  }
  .touch-target,
  .action-btn {
    min-height: 44px;
  }
}
</style>
