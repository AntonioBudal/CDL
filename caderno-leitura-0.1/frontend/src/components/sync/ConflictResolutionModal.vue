<script setup lang="ts">
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import { AlertTriangle, ArrowRightLeft, Check, RefreshCw, X } from 'lucide-vue-next'
import type { ConflictData } from '../../types.ts'

interface FormFieldComparison {
  key: string
  label: string
  localValue: string
  serverValue: string
  isDifferent: boolean
}

const props = withDefaults(
  defineProps<{
    open: boolean
    conflictData?: ConflictData | null
    localData?: Record<string, any>
    busy?: boolean
  }>(),
  {
    conflictData: null,
    localData: () => ({}),
    busy: false,
  }
)

const emit = defineEmits<{
  (e: 'overwrite'): void
  (e: 'keepServer'): void
  (e: 'close'): void
}>()

const dialogRef = ref<HTMLDivElement | null>(null)
const defaultButtonRef = ref<HTMLButtonElement | null>(null)
const showComparison = ref(false)

const serverData = computed<Record<string, any>>(() => {
  return props.conflictData?.server_data || {}
})

const serverVersion = computed<number>(() => {
  return props.conflictData?.server_version ?? 1
})

const comparisonFields = computed<FormFieldComparison[]>(() => {
  const fields = [
    { key: 'title', label: 'Título' },
    { key: 'location', label: 'Localização' },
    { key: 'summary', label: 'Resumo' },
    { key: 'explanation', label: 'Explicação' },
    { key: 'concepts', label: 'Conceitos-chave' },
    { key: 'references', label: 'Referências' },
    { key: 'notes', label: 'Anotações pessoais' },
  ]

  return fields.map(({ key, label }) => {
    const localVal = String(props.localData?.[key] ?? '').trim()
    const serverVal = String(serverData.value?.[key] ?? '').trim()
    return {
      key,
      label,
      localValue: localVal,
      serverValue: serverVal,
      isDifferent: localVal !== serverVal,
    }
  })
})

const hasDifferences = computed(() => {
  return comparisonFields.value.some((f) => f.isDifferent)
})

function handleKeyDown(event: KeyboardEvent) {
  if (!props.open || props.busy) return

  if (event.key === 'Escape') {
    event.preventDefault()
    emit('close')
    return
  }

  if (event.key === 'Tab' && dialogRef.value) {
    const focusable = dialogRef.value.querySelectorAll<HTMLElement>(
      'button:not([disabled]), [tabindex="0"]'
    )
    if (focusable.length > 0) {
      const first = focusable[0]
      const last = focusable[focusable.length - 1]

      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault()
        last.focus()
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault()
        first.focus()
      }
    }
  }
}

watch(
  () => props.open,
  async (isOpen) => {
    if (isOpen) {
      showComparison.value = false
      await nextTick()
      defaultButtonRef.value?.focus()
    }
  }
)

onMounted(() => {
  window.addEventListener('keydown', handleKeyDown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyDown)
})
</script>

<template>
  <Teleport to="body">
    <div
      v-if="open"
      class="modal-backdrop"
      role="presentation"
      @click="!busy && emit('close')"
    >
      <div
        ref="dialogRef"
        class="modal-dialog"
        role="dialog"
        aria-modal="true"
        aria-labelledby="conflict-resolution-title"
        aria-describedby="conflict-resolution-desc"
        @click.stop
      >
        <div class="modal-header">
          <div class="title-with-icon">
            <span class="warning-icon" aria-hidden="true">
              <AlertTriangle :size="20" />
            </span>
            <h2 id="conflict-resolution-title">Conflito de Concorrência Detectado</h2>
          </div>
          <button
            type="button"
            class="close-btn"
            aria-label="Fechar diálogo de conflito"
            :disabled="busy"
            @click="emit('close')"
          >
            <X :size="18" aria-hidden="true" />
          </button>
        </div>

        <div class="warning-box" role="alert">
          <p id="conflict-resolution-desc">
            Este registro foi modificado e salvo em outro dispositivo enquanto você editava.
            A versão no servidor agora é a <strong>#{{ serverVersion }}</strong>.
          </p>
          <p class="data-safe-note">
            <Check :size="15" class="safe-icon" aria-hidden="true" />
            <strong>Seus dados não foram perdidos:</strong> todo o conteúdo que você digitou permanece preservado no formulário.
          </p>
        </div>

        <!-- Botão para alternar comparação lado a lado -->
        <div class="comparison-toggle-bar">
          <button
            type="button"
            class="secondary comparison-toggle-btn"
            :disabled="busy"
            @click="showComparison = !showComparison"
          >
            <ArrowRightLeft :size="16" aria-hidden="true" />
            <span>{{ showComparison ? 'Ocultar comparação detalhada' : 'Comparar alterações lado a lado' }}</span>
          </button>
        </div>

        <!-- Painel de Comparação Lado a Lado -->
        <div v-if="showComparison" class="comparison-panel" tabindex="0" role="region" aria-label="Comparação de versões">
          <div class="comparison-table">
            <div class="comparison-row header-row">
              <div class="col-label">Campo</div>
              <div class="col-local">Rascunho Local (Seu Dispositivo)</div>
              <div class="col-server">Versão Vigente no Servidor (v{{ serverVersion }})</div>
            </div>
            <div
              v-for="field in comparisonFields"
              :key="field.key"
              class="comparison-row"
              :class="{ 'is-different': field.isDifferent }"
            >
              <div class="col-label">
                <strong>{{ field.label }}</strong>
                <span v-if="field.isDifferent" class="diff-tag">Modificado</span>
              </div>
              <div class="col-local">
                <pre class="field-text">{{ field.localValue || '(em branco)' }}</pre>
              </div>
              <div class="col-server">
                <pre class="field-text">{{ field.serverValue || '(em branco)' }}</pre>
              </div>
            </div>
          </div>
          <p v-if="!hasDifferences" class="no-differences-note">
            Não foram detectadas divergências de texto entre os campos (apenas metadados de versão foram atualizados).
          </p>
        </div>

        <p class="options-prompt">
          Como você deseja resolver este conflito?
        </p>

        <div class="conflict-actions">
          <button
            ref="defaultButtonRef"
            type="button"
            class="primary action-btn overwrite-btn"
            :disabled="busy"
            @click="emit('overwrite')"
          >
            <span class="btn-title">Sobrescrever com rascunho local</span>
            <span class="btn-subtext">Grava suas alterações no servidor avançando para a versão #{{ serverVersion + 1 }}</span>
          </button>

          <button
            type="button"
            class="secondary action-btn keep-server-btn"
            :disabled="busy"
            @click="emit('keepServer')"
          >
            <span class="btn-title">
              <RefreshCw :size="15" aria-hidden="true" />
              Adotar versão do servidor
            </span>
            <span class="btn-subtext">Descarta as edições locais e recarrega os dados salvos no servidor</span>
          </button>
        </div>

        <div class="modal-footer">
          <button
            type="button"
            class="text-link"
            :disabled="busy"
            @click="emit('close')"
          >
            Permanecer no formulário e revisar manualmente
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.modal-backdrop {
  position: fixed;
  inset: 0;
  background-color: rgba(0, 0, 0, 0.65);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.modal-dialog {
  background-color: var(--color-bg, #ffffff);
  color: var(--color-text, #111827);
  border: var(--border-width, 1px) solid var(--color-border, #e5e7eb);
  border-radius: var(--border-radius, 8px);
  padding: 1.5rem;
  max-width: 44rem;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.25);
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1rem;
}

.title-with-icon {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.warning-icon {
  color: var(--color-warning, #d97706);
  display: inline-flex;
}

.modal-header h2 {
  font-size: 1.15rem;
  font-weight: 700;
  margin: 0;
}

.close-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.25rem;
  color: var(--color-text-muted, #6b7280);
  border-radius: 4px;
}

.close-btn:hover {
  color: var(--color-text, #111827);
}

.warning-box {
  background-color: var(--color-bg-warning, #fffbeb);
  border: 1px solid var(--color-border-warning, #fef3c7);
  padding: 0.85rem 1rem;
  border-radius: 6px;
  font-size: 0.95rem;
  line-height: 1.5;
}

.data-safe-note {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  margin-top: 0.5rem;
  color: var(--color-success, #059669);
  font-size: 0.9rem;
}

.safe-icon {
  flex-shrink: 0;
}

.comparison-toggle-bar {
  margin-top: 1rem;
  display: flex;
  justify-content: flex-start;
}

.comparison-toggle-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.85rem;
  padding: 0.4rem 0.75rem;
}

.comparison-panel {
  margin-top: 0.75rem;
  border: 1px solid var(--color-border, #e5e7eb);
  border-radius: 6px;
  max-height: 16rem;
  overflow-y: auto;
  background-color: var(--color-bg-subtle, #f9fafb);
}

.comparison-table {
  display: flex;
  flex-direction: column;
  width: 100%;
}

.comparison-row {
  display: grid;
  grid-template-columns: 8rem 1fr 1fr;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  border-bottom: 1px solid var(--color-border, #e5e7eb);
  font-size: 0.85rem;
}

.comparison-row:last-child {
  border-bottom: none;
}

.header-row {
  background-color: var(--color-bg-muted, #f3f4f6);
  font-weight: 600;
  position: sticky;
  top: 0;
  z-index: 1;
}

.is-different {
  background-color: rgba(234, 179, 8, 0.08);
}

.diff-tag {
  display: inline-block;
  font-size: 0.68rem;
  font-weight: 600;
  padding: 0.1rem 0.3rem;
  border-radius: 3px;
  background-color: var(--color-warning-subtle, #fef3c7);
  color: var(--color-warning-text, #92400e);
  margin-top: 0.2rem;
}

.field-text {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
  font-family: inherit;
  font-size: 0.82rem;
  max-height: 6rem;
  overflow-y: auto;
}

.options-prompt {
  margin-top: 1.25rem;
  margin-bottom: 0.5rem;
  font-weight: 600;
  font-size: 0.9rem;
}

.conflict-actions {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.action-btn {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  text-align: left;
  padding: 0.75rem 1rem;
  min-height: 3.5rem;
  border-radius: 6px;
}

.btn-title {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  font-weight: 600;
  font-size: 0.95rem;
}

.btn-subtext {
  font-size: 0.8rem;
  font-weight: 400;
  opacity: 0.85;
  margin-top: 0.2rem;
}

.modal-footer {
  display: flex;
  justify-content: center;
  margin-top: 1.25rem;
}
</style>
