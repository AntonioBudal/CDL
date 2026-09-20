<script setup lang="ts">
import { ref, watch } from 'vue'
import { RouterLink } from 'vue-router'
import type { StudyRelationItem, StudyRelationType } from '../../types'
import { useStudyRelations, RELATION_TYPE_LABELS } from '../../composables/useStudyRelations'
import Icon from '../ui/Icon.vue'

interface Props {
  studyId: number
  bookId?: number
  readOnly?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  bookId: undefined,
  readOnly: false,
})

const emit = defineEmits<{
  (e: 'open-create-modal'): void
  (e: 'relation-removed', relationId: number): void
  (e: 'relation-updated', relationId: number): void
}>()

const {
  outboundRelations,
  inboundRelations,
  totalRelationsCount,
  loading,
  error,
  loadRelations,
  updateRelation,
  removeRelation,
} = useStudyRelations()

const editingRelationId = ref<number | null>(null)
const editType = ref<StudyRelationType>('relacionado_com')
const editDescription = ref('')
const isSavingEdit = ref(false)

function startEdit(relation: StudyRelationItem) {
  if (props.readOnly) return
  editingRelationId.value = relation.id
  editType.value = relation.relation_type
  editDescription.value = relation.description || ''
}

function cancelEdit() {
  editingRelationId.value = null
}

async function saveEdit(relationId: number) {
  if (props.readOnly || isSavingEdit.value) return
  isSavingEdit.value = true
  try {
    await updateRelation(relationId, {
      relation_type: editType.value,
      description: editDescription.value.trim(),
    })
    editingRelationId.value = null
    emit('relation-updated', relationId)
  } catch {
    // Erro capturado no composable
  } finally {
    isSavingEdit.value = false
  }
}

async function handleRemove(relation: StudyRelationItem) {
  if (props.readOnly) return
  try {
    await removeRelation(relation.id)
    emit('relation-removed', relation.id)
  } catch {
    // Erro já tratado no composable
  }
}

watch(
  () => props.studyId,
  (newId) => {
    if (newId) {
      loadRelations(newId)
    }
  },
  { immediate: true }
)

defineExpose({
  loadRelations: () => loadRelations(props.studyId),
})
</script>

<template>
  <section class="study-relations-panel" aria-labelledby="relations-heading">
    <header class="relations-header">
      <div class="relations-title-wrap">
        <Icon name="network" :size="18" class="relations-icon" />
        <h2 id="relations-heading" class="relations-title">
          Relações e Conexões
          <span v-if="totalRelationsCount > 0" class="relations-count-badge">
            {{ totalRelationsCount }}
          </span>
        </h2>
      </div>

      <button
        v-if="!readOnly"
        type="button"
        class="add-relation-btn"
        @click="emit('open-create-modal')"
        aria-label="Adicionar nova relação semântica"
      >
        <Icon name="plus" :size="16" />
        <span>Conectar</span>
      </button>
    </header>

    <div v-if="loading" class="relations-state-panel" role="status">
      <p>Carregando conexões…</p>
    </div>

    <div v-else-if="error" class="relations-error-notice" role="alert">
      <Icon name="alert-triangle" :size="16" />
      <span>{{ error }}</span>
    </div>

    <div v-else-if="totalRelationsCount === 0" class="relations-empty-state">
      <Icon name="network" :size="28" class="empty-icon" />
      <p class="empty-text">Nenhuma relação semântica estabelecida para este estudo.</p>
      <button
        v-if="!readOnly"
        type="button"
        class="empty-add-btn"
        @click="emit('open-create-modal')"
      >
        Adicionar primeira conexão
      </button>
    </div>

    <div v-else class="relations-content-layout">
      <!-- Relações de Saída -->
      <div v-if="outboundRelations.length > 0" class="relations-group">
        <h3 class="group-subtitle">Relações Estabelecidas ({{ outboundRelations.length }})</h3>
        <ul class="relations-list" role="list">
          <li
            v-for="rel in outboundRelations"
            :key="rel.id"
            class="relation-card outbound-card"
            :class="{ 'editing-card': editingRelationId === rel.id }"
          >
            <!-- Modo de Edição Rápida -->
            <div v-if="editingRelationId === rel.id" class="edit-card-form">
              <div class="edit-form-header">
                <span class="edit-target-label">Editar vínculo com <strong>{{ rel.connected_study.title }}</strong></span>
              </div>
              <div class="edit-form-fields">
                <label class="edit-field-label">
                  Tipo:
                  <select v-model="editType" class="edit-type-select">
                    <option value="relacionado_com">Relacionado com</option>
                    <option value="complementa">Complementa</option>
                    <option value="contradiz">Contradiz</option>
                    <option value="depende_de">Depende de</option>
                    <option value="mesmo_tema">Mesmo tema</option>
                    <option value="desdobramento_de">Desdobramento de</option>
                  </select>
                </label>
                <label class="edit-field-label">
                  Anotação / Justificativa:
                  <input
                    v-model="editDescription"
                    type="text"
                    class="edit-description-input"
                    placeholder="Nota explicativa (opcional)"
                    maxlength="255"
                    @keydown.enter.prevent="saveEdit(rel.id)"
                    @keydown.esc.prevent="cancelEdit"
                  />
                </label>
              </div>
              <div class="edit-form-actions">
                <button
                  type="button"
                  class="btn-save-edit"
                  :disabled="isSavingEdit"
                  @click="saveEdit(rel.id)"
                >
                  <Icon name="check" :size="14" />
                  <span>{{ isSavingEdit ? 'Salvando…' : 'Salvar' }}</span>
                </button>
                <button
                  type="button"
                  class="btn-cancel-edit"
                  @click="cancelEdit"
                >
                  <Icon name="x" :size="14" />
                  <span>Cancelar</span>
                </button>
              </div>
            </div>

            <!-- Modo de Exibição Normal -->
            <template v-else>
              <div class="card-left">
                <span
                  class="relation-badge"
                  :class="RELATION_TYPE_LABELS[rel.relation_type]?.badgeClass || 'badge-neutral'"
                >
                  {{ RELATION_TYPE_LABELS[rel.relation_type]?.outbound || rel.relation_type }}
                </span>

                <div class="card-details">
                  <RouterLink
                    :to="{
                      name: 'study',
                      params: {
                        bookId: rel.connected_study.book_id,
                        studyId: rel.connected_study.id,
                      },
                    }"
                    class="connected-title-link"
                  >
                    {{ rel.connected_study.title }}
                  </RouterLink>

                  <div class="connected-meta">
                    <span class="meta-book">{{ rel.connected_study.book_title }}</span>
                    <span class="meta-divider" aria-hidden="true">•</span>
                    <span class="meta-chapter">{{ rel.connected_study.chapter_title }}</span>
                  </div>

                  <p v-if="rel.description" class="relation-description">
                    "{{ rel.description }}"
                  </p>
                </div>
              </div>

              <div v-if="!readOnly" class="card-actions">
                <button
                  type="button"
                  class="edit-relation-btn"
                  title="Editar anotação ou tipo da relação"
                  aria-label="Editar esta relação"
                  @click="startEdit(rel)"
                >
                  <Icon name="pencil" :size="15" />
                </button>

                <button
                  type="button"
                  class="remove-relation-btn"
                  title="Desfazer esta relação"
                  aria-label="Desfazer esta relação"
                  @click="handleRemove(rel)"
                >
                  <Icon name="x" :size="16" />
                </button>
              </div>
            </template>
          </li>
        </ul>
      </div>

      <!-- Referências Cruzadas / Backlinks Recebidos -->
      <div v-if="inboundRelations.length > 0" class="relations-group">
        <h3 class="group-subtitle">Referências Cruzadas Recebidas ({{ inboundRelations.length }})</h3>
        <ul class="relations-list" role="list">
          <li
            v-for="rel in inboundRelations"
            :key="rel.id"
            class="relation-card inbound-card"
          >
            <div class="card-left">
              <span
                class="relation-badge inbound-badge"
                :class="RELATION_TYPE_LABELS[rel.relation_type]?.badgeClass || 'badge-neutral'"
              >
                {{ RELATION_TYPE_LABELS[rel.relation_type]?.inbound || rel.relation_type }}
              </span>

              <div class="card-details">
                <RouterLink
                  :to="{
                    name: 'study',
                    params: {
                      bookId: rel.connected_study.book_id,
                      studyId: rel.connected_study.id,
                    },
                  }"
                  class="connected-title-link"
                >
                  {{ rel.connected_study.title }}
                </RouterLink>

                <div class="connected-meta">
                  <span class="meta-book">{{ rel.connected_study.book_title }}</span>
                  <span class="meta-divider" aria-hidden="true">•</span>
                  <span class="meta-chapter">{{ rel.connected_study.chapter_title }}</span>
                </div>

                <p v-if="rel.description" class="relation-description">
                  "{{ rel.description }}"
                </p>
              </div>
            </div>
          </li>
        </ul>
      </div>
    </div>
  </section>
</template>

<style scoped>
.study-relations-panel {
  margin-top: 2rem;
  padding: 1.5rem;
  background-color: var(--color-surface, #ffffff);
  border: 1px solid var(--color-border, #e5e7eb);
  border-radius: 8px;
}

.relations-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.25rem;
  gap: 1rem;
}

.relations-title-wrap {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.relations-icon {
  color: var(--color-text-muted, #6b7280);
}

.relations-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--color-text, #111827);
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0;
}

.relations-count-badge {
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.125rem 0.5rem;
  background-color: var(--color-neutral-subtle, #f3f4f6);
  color: var(--color-text-muted, #4b5563);
  border-radius: 9999px;
}

.add-relation-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  min-height: 44px;
  min-width: 44px;
  padding: 0.5rem 0.875rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--color-accent, #2563eb);
  background-color: transparent;
  border: 1px solid var(--color-border, #d1d5db);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.15s ease;
}

.add-relation-btn:hover {
  background-color: var(--color-neutral-subtle, #f3f4f6);
  border-color: var(--color-accent, #2563eb);
}

.relations-state-panel {
  padding: 1rem;
  text-align: center;
  color: var(--color-text-muted, #6b7280);
}

.relations-error-notice {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  background-color: #fef2f2;
  color: #991b1b;
  border-radius: 6px;
  font-size: 0.875rem;
}

.relations-empty-state {
  text-align: center;
  padding: 2rem 1rem;
  color: var(--color-text-muted, #6b7280);
}

.empty-icon {
  margin: 0 auto 0.75rem auto;
  opacity: 0.4;
}

.empty-text {
  font-size: 0.9375rem;
  margin-bottom: 1rem;
}

.empty-add-btn {
  min-height: 44px;
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: #ffffff;
  background-color: var(--color-accent, #2563eb);
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.relations-content-layout {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.group-subtitle {
  font-size: 0.875rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--color-text-muted, #6b7280);
  margin-bottom: 0.75rem;
}

.relations-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.relation-card {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  padding: 0.875rem 1rem;
  background-color: var(--color-card-bg, #fafafa);
  border: 1px solid var(--color-border, #e5e7eb);
  border-radius: 6px;
  transition: border-color 0.15s ease;
}

.relation-card:hover {
  border-color: var(--color-accent, #93c5fd);
}

.inbound-card {
  border-left: 3px solid var(--color-accent, #3b82f6);
}

.outbound-card {
  border-left: 3px solid #10b981;
}

.card-left {
  display: flex;
  align-items: flex-start;
  gap: 0.875rem;
  flex: 1;
}

.relation-badge {
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  white-space: nowrap;
  flex-shrink: 0;
}

.badge-neutral {
  background-color: #f3f4f6;
  color: #374151;
}

.badge-complement {
  background-color: #ecfdf5;
  color: #065f46;
  border: 1px solid #a7f3d0;
}

.badge-contradict {
  background-color: #fef2f2;
  color: #991b1b;
  border: 1px solid #fecaca;
}

.badge-dependency {
  background-color: #eff6ff;
  color: #1e40af;
  border: 1px solid #bfdbfe;
}

.badge-theme {
  background-color: #faf5ff;
  color: #6b21a8;
  border: 1px solid #e9d5ff;
}

.badge-derivation {
  background-color: #fffbeb;
  color: #92400e;
  border: 1px solid #fde68a;
}

.card-details {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.connected-title-link {
  font-size: 0.9375rem;
  font-weight: 600;
  color: var(--color-text, #111827);
  text-decoration: none;
  transition: color 0.15s ease;
}

.connected-title-link:hover {
  color: var(--color-accent, #2563eb);
  text-decoration: underline;
}

.connected-meta {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  font-size: 0.8125rem;
  color: var(--color-text-muted, #6b7280);
}

.relation-description {
  font-size: 0.8125rem;
  font-style: italic;
  color: var(--color-text-muted, #4b5563);
  margin-top: 0.25rem;
  margin-bottom: 0;
}

.card-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.remove-relation-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  padding: 0;
  color: var(--color-text-muted, #9ca3af);
  background: transparent;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.15s ease;
}

.remove-relation-btn:hover {
  color: #ef4444;
  background-color: #fee2e2;
}

.edit-relation-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  padding: 0;
  color: var(--color-text-muted, #9ca3af);
  background: transparent;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.15s ease;
}

.edit-relation-btn:hover {
  color: var(--color-accent, #2563eb);
  background-color: #eff6ff;
}

.editing-card {
  border-color: var(--color-accent, #3b82f6) !important;
  background-color: #f8fafc !important;
}

.edit-card-form {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  width: 100%;
}

.edit-target-label {
  font-size: 0.8125rem;
  color: var(--color-text-muted, #64748b);
}

.edit-form-fields {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.edit-field-label {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--color-text-muted, #475569);
}

.edit-type-select,
.edit-description-input {
  min-height: 40px;
  padding: 0.375rem 0.625rem;
  font-size: 0.875rem;
  border: 1px solid var(--color-border, #cbd5e1);
  border-radius: 6px;
  background-color: #ffffff;
  color: var(--color-text, #0f172a);
}

.edit-type-select:focus,
.edit-description-input:focus {
  outline: none;
  border-color: var(--color-accent, #2563eb);
  box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.15);
}

.edit-form-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 0.25rem;
}

.btn-save-edit {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  min-height: 44px;
  padding: 0.375rem 0.875rem;
  font-size: 0.8125rem;
  font-weight: 500;
  color: #ffffff;
  background-color: var(--color-accent, #2563eb);
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.btn-save-edit:hover:not(:disabled) {
  opacity: 0.9;
}

.btn-cancel-edit {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  min-height: 44px;
  padding: 0.375rem 0.875rem;
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--color-text-muted, #64748b);
  background-color: transparent;
  border: 1px solid var(--color-border, #cbd5e1);
  border-radius: 6px;
  cursor: pointer;
}

.btn-cancel-edit:hover {
  background-color: #f1f5f9;
}

@media (max-width: 640px) {
  .card-left {
    flex-direction: column;
    gap: 0.5rem;
  }
}
</style>
