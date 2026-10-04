<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'
import type { StudySummary, StudyRelationItem, BookCanvasRelationItem, StudyRelationType } from '../../../types.ts'
import Icon from '../../ui/Icon.vue'
import { RELATION_TYPE_LABELS } from '../../../composables/useStudyRelations.ts'

interface Props {
  isOpen: boolean
  sourceStudy: StudySummary | null
  targetStudy: StudySummary | null
  existingRelation?: StudyRelationItem | BookCanvasRelationItem | null
  position: { x: number; y: number }
}

const props = withDefaults(defineProps<Props>(), {
  existingRelation: null,
})

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'save', payload: {
    sourceId: number
    targetId: number
    relationType: StudyRelationType
    description?: string
  }): void
  (e: 'delete', relationId: number): void
}>()

const isReversed = ref(false)
const selectedType = ref<StudyRelationType>('depende_de')
const description = ref('')
const descInputRef = ref<HTMLInputElement | null>(null)

const availableTypes: Array<{ key: StudyRelationType; label: string; icon: string }> = [
  { key: 'depende_de', label: 'Fundamenta', icon: 'check-circle' },
  { key: 'desdobramento_de', label: 'Desdobra-se em', icon: 'corner-down-right' },
  { key: 'contradiz', label: 'Contradiz', icon: 'alert-triangle' },
  { key: 'complementa', label: 'Complementa', icon: 'plus' },
  { key: 'mesmo_tema', label: 'Sintetiza / Mesmo Tema', icon: 'maximize-2' },
  { key: 'relacionado_com', label: 'Relacionado com / Cita', icon: 'link' },
]

const cardStyle = computed(() => {
  const maxX = typeof window !== 'undefined' ? window.innerWidth - 320 : props.position.x
  const maxY = typeof window !== 'undefined' ? window.innerHeight - 380 : props.position.y
  return {
    left: `${Math.min(maxX, Math.max(16, props.position.x))}px`,
    top: `${Math.min(maxY, Math.max(16, props.position.y))}px`,
  }
})

watch(
  () => props.isOpen,
  (open) => {
    if (open) {
      isReversed.value = false
      if (props.existingRelation) {
        selectedType.value = props.existingRelation.relation_type
        description.value = props.existingRelation.description || ''
      } else {
        selectedType.value = 'depende_de'
        description.value = ''
      }
      nextTick(() => {
        descInputRef.value?.focus()
      })
    }
  },
  { immediate: true }
)

const effectiveSource = computed(() =>
  isReversed.value ? props.targetStudy : props.sourceStudy
)
const effectiveTarget = computed(() =>
  isReversed.value ? props.sourceStudy : props.targetStudy
)

const activeRelationLabel = computed(() => {
  const meta = RELATION_TYPE_LABELS[selectedType.value]
  return meta ? meta.outbound : selectedType.value
})

function toggleReverse() {
  isReversed.value = !isReversed.value
}

function handleSave() {
  if (!effectiveSource.value || !effectiveTarget.value) return
  emit('save', {
    sourceId: effectiveSource.value.id,
    targetId: effectiveTarget.value.id,
    relationType: selectedType.value,
    description: description.value.trim() || undefined,
  })
}

function handleDelete() {
  if (props.existingRelation) {
    emit('delete', props.existingRelation.id)
  }
}

function handleKeydown(e: KeyboardEvent) {
  if (e.key === 'Escape') {
    e.preventDefault()
    emit('close')
  } else if (e.key === 'Enter' && (e.ctrlKey || e.metaKey || e.target === descInputRef.value)) {
    e.preventDefault()
    handleSave()
  }
}
</script>

<template>
  <div
    v-if="isOpen && sourceStudy && targetStudy"
    class="map-relation-popover-backdrop"
    @click.self="emit('close')"
    @keydown="handleKeydown"
  >
    <div
      class="map-relation-popover-card"
      :style="cardStyle"
      role="dialog"
      aria-label="Definir relação semântica"
    >
      <div class="popover-header">
        <div class="header-title-group">
          <Icon name="link" :size="16" class="header-icon" />
          <h4 class="popover-title">
            {{ existingRelation ? 'Editar Relação Semântica' : 'Nova Relação Semântica' }}
          </h4>
        </div>
        <button
          type="button"
          class="popover-close-btn"
          title="Fechar"
          aria-label="Fechar"
          @click="emit('close')"
        >
          <Icon name="x" :size="15" />
        </button>
      </div>

      <!-- Oração Semântica Ativa -->
      <div class="semantic-sentence-box">
        <div class="sentence-nodes-flow">
          <span class="node-badge source-badge" :title="effectiveSource?.title">
            {{ effectiveSource?.title }}
          </span>
          <button
            type="button"
            class="reverse-direction-btn action-btn touch-target"
            title="Inverter sentido da relação (⇄)"
            aria-label="Inverter sentido da relação"
            @click="toggleReverse"
          >
            <span>⇄</span>
          </button>
          <span class="relation-verb-badge">
            {{ activeRelationLabel }}
          </span>
          <span class="node-badge target-badge" :title="effectiveTarget?.title">
            {{ effectiveTarget?.title }}
          </span>
        </div>
      </div>

      <!-- Seletor de Tipo Semântico -->
      <div class="form-group">
        <label class="form-label">Tipo de Conexão Cognitiva:</label>
        <div class="relation-type-grid" role="radiogroup">
          <button
            v-for="item in availableTypes"
            :key="item.key"
            type="button"
            class="type-pill-btn action-btn touch-target"
            :class="{ 'is-selected': selectedType === item.key }"
            role="radio"
            :aria-checked="selectedType === item.key"
            @click="selectedType = item.key"
          >
            <Icon :name="item.icon as any" :size="13" />
            <span>{{ item.label }}</span>
          </button>
        </div>
      </div>

      <!-- Justificativa Opcional -->
      <div class="form-group">
        <label for="relation-desc-input" class="form-label">
          Justificativa do Argumento (opcional):
        </label>
        <input
          id="relation-desc-input"
          ref="descInputRef"
          v-model="description"
          type="text"
          class="form-input"
          placeholder="Ex.: Este ponto deriva das premissas do capítulo..."
          maxlength="250"
        />
      </div>

      <!-- Ações do Popover -->
      <div class="popover-footer">
        <button
          v-if="existingRelation"
          type="button"
          class="button danger-ghost action-btn touch-target"
          title="Excluir esta relação"
          @click="handleDelete"
        >
          <Icon name="trash" :size="14" />
          <span>Excluir</span>
        </button>
        <div class="footer-right-actions">
          <button
            type="button"
            class="button ghost action-btn touch-target"
            @click="emit('close')"
          >
            Cancelar
          </button>
          <button
            type="button"
            class="button primary action-btn touch-target"
            @click="handleSave"
          >
            Salvar Conexão
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.map-relation-popover-backdrop {
  position: fixed;
  inset: 0;
  z-index: 1000;
  background-color: rgba(0, 0, 0, 0.25);
  display: flex;
}

.map-relation-popover-card {
  position: absolute;
  width: 320px;
  background: var(--color-surface, #ffffff);
  border: 1px solid var(--color-border, #e2e8f0);
  border-radius: var(--radius-card, 8px);
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.2), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
  animation: popoverFadeIn 0.15s ease-out;
}

@keyframes popoverFadeIn {
  from {
    opacity: 0;
    transform: scale(0.96) translateY(-4px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

.popover-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.header-title-group {
  display: flex;
  align-items: center;
  gap: 0.45rem;
}

.header-icon {
  color: var(--color-accent);
}

.popover-title {
  margin: 0;
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--color-inverse-bg, #0f172a);
}

.popover-close-btn {
  background: transparent;
  border: none;
  color: var(--color-muted);
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 4px;
}

.popover-close-btn:hover {
  background: var(--color-surface-hover);
  color: var(--color-inverse-bg);
}

.semantic-sentence-box {
  background-color: var(--color-surface-elevated, #f8fafc);
  border: 1px solid var(--color-border-divider, #e2e8f0);
  border-radius: 6px;
  padding: 0.6rem;
}

.sentence-nodes-flow {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.35rem;
  font-size: 0.78rem;
}

.node-badge {
  display: inline-block;
  max-width: 100px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-weight: 600;
  padding: 0.15rem 0.4rem;
  border-radius: 4px;
  background-color: var(--color-surface, #ffffff);
  border: 1px solid var(--color-border, #cbd5e1);
  color: var(--color-inverse-bg);
}

.reverse-direction-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 26px;
  height: 26px;
  font-size: 1rem;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 4px;
  cursor: pointer;
  color: var(--color-accent);
  transition: all 0.15s ease;
}

.reverse-direction-btn:hover {
  background: color-mix(in srgb, var(--color-accent) 15%, var(--color-surface));
  border-color: var(--color-accent);
}

.relation-verb-badge {
  font-weight: 700;
  color: var(--color-accent);
  padding: 0 0.2rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.form-label {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--color-muted, #64748b);
}

.relation-type-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.35rem;
}

.type-pill-btn {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.35rem 0.5rem;
  border: 1px solid var(--color-border, #e2e8f0);
  background: var(--color-surface, #ffffff);
  border-radius: 4px;
  font-size: 0.75rem;
  color: var(--color-inverse-bg);
  cursor: pointer;
  text-align: left;
  transition: all 0.15s ease;
}

.type-pill-btn:hover {
  border-color: var(--color-accent);
  background: var(--color-surface-hover);
}

.type-pill-btn.is-selected {
  border-color: var(--color-accent);
  background: color-mix(in srgb, var(--color-accent) 12%, var(--color-surface));
  color: var(--color-accent);
  font-weight: 600;
}

.form-input {
  width: 100%;
  padding: 0.4rem 0.6rem;
  border: 1px solid var(--color-border, #cbd5e1);
  border-radius: 4px;
  font-size: 0.8rem;
  background: var(--color-surface);
  color: var(--color-inverse-bg);
}

.form-input:focus {
  outline: none;
  border-color: var(--color-accent);
  box-shadow: 0 0 0 1px var(--color-accent);
}

.popover-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 0.25rem;
  gap: 0.5rem;
}

.footer-right-actions {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  margin-left: auto;
}

.button {
  padding: 0.35rem 0.7rem;
  border-radius: 4px;
  font-size: 0.78rem;
  font-weight: 600;
  cursor: pointer;
  border: 1px solid transparent;
  transition: all 0.15s ease;
}

.button.primary {
  background: var(--color-accent, #3b82f6);
  color: #ffffff;
}

.button.primary:hover {
  filter: brightness(1.08);
}

.button.ghost {
  background: transparent;
  color: var(--color-muted);
}

.button.ghost:hover {
  background: var(--color-surface-hover);
  color: var(--color-inverse-bg);
}

.button.danger-ghost {
  background: transparent;
  color: var(--color-danger, #ef4444);
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
}

.button.danger-ghost:hover {
  background: color-mix(in srgb, var(--color-danger) 10%, transparent);
}

@media (max-width: 768px) {
  .map-relation-popover-card {
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
  .reverse-direction-btn {
    min-width: 44px;
    min-height: 44px;
  }
}
</style>
