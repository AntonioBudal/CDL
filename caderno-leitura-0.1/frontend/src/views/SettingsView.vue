<script setup lang="ts">
import { onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import { RouterLink } from 'vue-router'
import AppearanceControls from '../components/AppearanceControls.vue'
import AppearancePreview from '../components/AppearancePreview.vue'
import DatabaseBackup from '../components/DatabaseBackup.vue'
import ConfirmResetModal from '../components/ConfirmResetModal.vue'
import RestoreModal from '../components/RestoreModal.vue'
import SessionsManager from '../components/auth/SessionsManager.vue'
import { fetchHealth, type HealthResponse } from '../services/api'
import { useSuperclassPhysics } from '../composables/useSuperclassPhysics'
import type { AppearancePreferences } from '../appearance'
import type { HealthCheckResult, HomeViewPreference, SettingsTab, SettingsTabId, StorageDiagnostic } from '../types'

const appearance = window.cadernoAppearance
const preferences = reactive(appearance?.get() ?? ({} as AppearancePreferences))
const message = ref('')
const physics = useSuperclassPhysics()

const activeTab = ref<SettingsTabId>('aparencia')

const tabs: SettingsTab[] = [
  { id: 'aparencia', label: 'Aparência', description: 'Paleta cromática, Superclasse e dimensões' },
  { id: 'leitura', label: 'Leitura', description: 'Tipografia literária, tamanho e destaques' },
  { id: 'sistema', label: 'Sistema', description: 'Diagnóstico, conexão, armazenamento e backup' },
  { id: 'conta', label: 'Conta & Dispositivos', description: 'Sessões ativas e dispositivos conectados' },
]

function save() {
  if (!appearance) return
  message.value = appearance.set({ ...preferences })
    ? 'Preferências salvas neste navegador.'
    : 'Aparência aplicada, mas o navegador não permitiu salvar. As escolhas podem ser perdidas ao recarregar.'
}

function update(patch: Partial<AppearancePreferences>) {
  Object.assign(preferences, patch)
  save()
  if (typeof document !== 'undefined' && document.activeElement instanceof HTMLElement) {
    physics.triggerHapticPulse(document.activeElement, 'step')
  }
}

// Navegação por teclado entre as abas
function onTabKeydown(event: KeyboardEvent, currentId: SettingsTabId) {
  const currentIndex = tabs.findIndex(t => t.id === currentId)
  if (currentIndex === -1) return

  let nextIndex = -1

  if (event.key === 'ArrowRight' || event.key === 'ArrowDown') {
    event.preventDefault()
    nextIndex = (currentIndex + 1) % tabs.length
  } else if (event.key === 'ArrowLeft' || event.key === 'ArrowUp') {
    event.preventDefault()
    nextIndex = (currentIndex - 1 + tabs.length) % tabs.length
  } else if (event.key === 'Home') {
    event.preventDefault()
    nextIndex = 0
  } else if (event.key === 'End') {
    event.preventDefault()
    nextIndex = tabs.length - 1
  }

  if (nextIndex >= 0) {
    const nextTab = tabs[nextIndex]
    activeTab.value = nextTab.id
    const el = document.getElementById(`tab-${nextTab.id}`)
    el?.focus()
    if (el) {
      physics.triggerHapticPulse(el, 'step')
    }
  }
}

function selectTab(id: SettingsTabId, event?: MouseEvent) {
  activeTab.value = id
  if (event?.currentTarget) {
    physics.triggerHapticPulse(event.currentTarget as HTMLElement, 'step')
  }
}

// Diagnóstico de Armazenamento
const storageDiag = ref<StorageDiagnostic>({
  isAvailable: false,
  keyCount: 0,
  totalBytes: 0,
  formattedSize: 'Calculando…',
  cadernoKeysCount: 0,
})

function updateStorageDiagnostic() {
  try {
    const storage = window.localStorage
    if (!storage) throw new Error('No storage')

    let totalBytes = 0
    let cadernoKeysCount = 0
    const keys = Object.keys(storage)

    for (const key of keys) {
      const val = storage.getItem(key) ?? ''
      totalBytes += (key.length + val.length) * 2
      if (key.startsWith('caderno.')) {
        cadernoKeysCount++
      }
    }

    const formattedSize =
      totalBytes < 1024
        ? `${totalBytes} B`
        : `${(totalBytes / 1024).toFixed(1)} KB`

    storageDiag.value = {
      isAvailable: true,
      keyCount: keys.length,
      totalBytes,
      formattedSize,
      cadernoKeysCount,
    }
  } catch {
    storageDiag.value = {
      isAvailable: false,
      keyCount: 0,
      totalBytes: 0,
      formattedSize: 'Indisponível',
      cadernoKeysCount: 0,
    }
  }
}

function handleCleanOrphans() {
  const removed = appearance?.cleanOrphanKeys?.() ?? 0
  updateStorageDiagnostic()
  systemActionFeedback.value = removed > 0
    ? `${removed} chave(s) obsoleta(s) removida(s) com sucesso.`
    : 'Nenhuma chave obsoleta encontrada. O armazenamento está otimizado.'
}

// Verificação de Conexão com a API Local
const healthCheck = ref<HealthCheckResult>({
  status: 'loading',
  version: null,
  latencyMs: null,
  message: 'Verificando conexão com o servidor local…',
})

let healthAbortController: AbortController | null = null

async function checkHealth() {
  healthAbortController?.abort()
  const controller = new AbortController()
  healthAbortController = controller

  healthCheck.value = {
    status: 'loading',
    version: null,
    latencyMs: null,
    message: 'Consultando /api/health…',
  }

  const startTime = Date.now()

  try {
    const res: HealthResponse = await fetchHealth(controller.signal)
    const latency = Math.max(0, Date.now() - startTime)
    healthCheck.value = {
      status: 'ok',
      version: res.version,
      latencyMs: latency,
      message: `Conectado com sucesso (${latency}ms).`,
    }
  } catch (err: unknown) {
    if (controller.signal.aborted) return
    healthCheck.value = {
      status: 'error',
      version: null,
      latencyMs: null,
      message: err instanceof Error ? err.message : 'Falha ao conectar com o backend local.',
    }
  } finally {
    if (healthAbortController === controller) {
      healthAbortController = null
    }
  }
}

// Modal de Restauração de Fábrica
const isResetModalOpen = ref(false)
const isResetting = ref(false)
const systemActionFeedback = ref('')

// Modal de Restauração de Backup
const isRestoreModalOpen = ref(false)

function onAcervoRestored() {
  systemActionFeedback.value = 'Acervo restaurado com sucesso! A base e as capas foram atualizadas.'
}

function openResetModal() {
  isResetModalOpen.value = true
}

function closeResetModal() {
  isResetModalOpen.value = false
}

function confirmFactoryReset() {
  isResetting.value = true
  try {
    const success = appearance?.factoryReset?.() ?? false
    if (success) {
      Object.assign(preferences, appearance.get())
      systemActionFeedback.value = 'Padrões de aparência restaurados com sucesso!'
      message.value = 'Padrões de fábrica aplicados.'
    } else {
      systemActionFeedback.value = 'Não foi possível salvar o reset no armazenamento do navegador.'
    }
    updateStorageDiagnostic()
  } finally {
    isResetting.value = false
    isResetModalOpen.value = false
  }
}

// Preferência de Tela Inicial Padrão (F07)
const homeViewPreference = ref<HomeViewPreference>('dashboard')

function initHomeViewPreference() {
  try {
    const val = window.localStorage?.getItem('caderno_home_view')
    if (val === 'books' || val === 'dashboard') {
      homeViewPreference.value = val
    } else {
      homeViewPreference.value = 'dashboard'
    }
  } catch {
    homeViewPreference.value = 'dashboard'
  }
}

function setHomeViewPreference(val: HomeViewPreference) {
  homeViewPreference.value = val
  try {
    window.localStorage?.setItem('caderno_home_view', val)
    window.dispatchEvent(new CustomEvent('caderno_home_view_changed', { detail: val }))
    systemActionFeedback.value = `Tela inicial padrão definida como: ${val === 'dashboard' ? 'Dashboard 2.0' : 'Acervo de Livros'}.`
  } catch {
    // ignore
  }
}

onMounted(() => {
  initHomeViewPreference()
  updateStorageDiagnostic()
  void checkHealth()
})

onBeforeUnmount(() => {
  healthAbortController?.abort()
})
</script>

<template>
  <section class="settings-page wrap">
    <header class="page-header">
      <h1>Ajustes</h1>
      <p class="intro">
        Personalize a experiência de estudo ou gerencie a integridade do sistema.
      </p>
    </header>

    <!-- Barra de Abas Segmentadas WAI-ARIA -->
    <nav class="settings-nav" aria-label="Seções de Ajustes">
      <div class="settings-tabs" role="tablist">
        <button
          v-for="tab in tabs"
          :id="`tab-${tab.id}`"
          :key="tab.id"
          type="button"
          role="tab"
          class="settings-tab"
          :aria-selected="activeTab === tab.id"
          :aria-controls="`panel-${tab.id}`"
          :tabindex="activeTab === tab.id ? 0 : -1"
          @click="selectTab(tab.id, $event)"
          @keydown="onTabKeydown($event, tab.id)"
        >
          {{ tab.label }}
        </button>
      </div>
    </nav>

    <div class="settings-layout">
      <!-- Coluna Principal (Controles e Painéis da Aba Ativa) -->
      <div class="settings-main">
        <!-- Aba 1: Aparência -->
        <section
          v-show="activeTab === 'aparencia'"
          id="panel-aparencia"
          role="tabpanel"
          aria-labelledby="tab-aparencia"
          tabindex="0"
          class="panel"
        >
          <h2 id="appearance-title">Aparência</h2>
          <p class="muted">
            Paleta de cores, Superclasse física e proporção visual. Mudanças têm efeito imediato.
          </p>

          <AppearanceControls
            :preferences="preferences"
            tab="aparencia"
            @change="update"
          />

          <p class="settings-status muted" role="status">
            {{ message }}
          </p>
        </section>

        <!-- Aba 2: Leitura -->
        <section
          v-show="activeTab === 'leitura'"
          id="panel-leitura"
          role="tabpanel"
          aria-labelledby="tab-leitura"
          tabindex="0"
          class="panel"
        >
          <h2 id="reading-title">Leitura</h2>
          <p class="muted">
            Conforto tipográfico, tamanho do texto, densidade e realce de anotações.
          </p>

          <AppearanceControls
            :preferences="preferences"
            tab="leitura"
            @change="update"
          />

          <p class="settings-status muted" role="status">
            {{ message }}
          </p>
        </section>

        <!-- Aba 3: Sistema (Central de Diagnóstico) -->
        <section
          v-show="activeTab === 'sistema'"
          id="panel-sistema"
          role="tabpanel"
          aria-labelledby="tab-sistema"
          tabindex="0"
          class="panel system-panel"
        >
          <h2 id="system-title">Central do Sistema</h2>
          <p class="muted">
            Diagnóstico de conectividade, métricas de armazenamento, restauração e backup.
          </p>

          <p
            v-if="systemActionFeedback"
            class="notice"
            role="status"
            aria-live="polite"
          >
            {{ systemActionFeedback }}
          </p>

          <!-- Card 0: Tela Inicial Padrão (F07) -->
          <article class="system-card">
            <h3>Tela Inicial Padrão</h3>
            <p class="muted">
              Escolha qual tela deve ser carregada por padrão ao abrir o Caderno de Leitura na rota inicial.
            </p>
            <div class="home-view-options" role="radiogroup" aria-label="Tela inicial padrão">
              <label class="radio-option">
                <input
                  type="radio"
                  name="homeViewPreference"
                  value="dashboard"
                  :checked="homeViewPreference === 'dashboard'"
                  @change="setHomeViewPreference('dashboard')"
                />
                <span class="radio-text">
                  <strong>Dashboard 2.0</strong> (Cockpit de Estudos e Retoma)
                </span>
              </label>
              <label class="radio-option">
                <input
                  type="radio"
                  name="homeViewPreference"
                  value="books"
                  :checked="homeViewPreference === 'books'"
                  @change="setHomeViewPreference('books')"
                />
                <span class="radio-text">
                  <strong>Acervo de Livros</strong> (Prateleira de Obras)
                </span>
              </label>
            </div>
          </article>

          <!-- Card 1: Informativo de Escopo de Persistência -->
          <article class="system-card">
            <h3>Escopo de Armazenamento</h3>
            <p>
              As <strong>preferências de aparência</strong> (tema, tipografia e superclasses) ficam salvas exclusivamente na memória local deste navegador (<code>localStorage</code>).
            </p>
            <p class="muted">
              O seu <strong>acervo literário</strong> (livros, capítulos, estudos, anotações e capas) reside com segurança no banco de dados SQLite local (<code>caderno.db</code>) no servidor deste computador.
            </p>
          </article>

          <!-- Card 2: Conexão e Integridade -->
          <article class="system-card">
            <h3>Status da Conexão Local</h3>
            <div class="actions wrap" style="align-items: center; justify-content: space-between;">
              <div>
                <span
                  class="connection-status-badge"
                  :class="healthCheck.status"
                >
                  <span v-if="healthCheck.status === 'ok'">● Conectado</span>
                  <span v-else-if="healthCheck.status === 'loading'">◌ Verificando…</span>
                  <span v-else>▲ Indisponível</span>
                </span>
                <span v-if="healthCheck.version" class="muted" style="margin-left: 0.5rem;">
                  v{{ healthCheck.version }}
                </span>
              </div>

              <div class="actions wrap">
                <button
                  type="button"
                  class="secondary"
                  :disabled="healthCheck.status === 'loading'"
                  @click="checkHealth"
                >
                  Testar novamente
                </button>
                <RouterLink class="button secondary text-link" to="/conexao">
                  Diagnóstico completo
                </RouterLink>
              </div>
            </div>
            <p class="muted" style="margin-top: 0.5rem; margin-bottom: 0;">
              {{ healthCheck.message }}
            </p>
          </article>

          <!-- Card 3: Armazenamento do Navegador -->
          <article class="system-card">
            <h3>Armazenamento do Navegador</h3>
            <p class="muted">
              Uso atual do <code>localStorage</code> neste dispositivo.
            </p>

            <div class="system-stats-grid">
              <div class="system-stat">
                <span class="system-stat-value">{{ storageDiag.formattedSize }}</span>
                <span class="system-stat-label">Tamanho Estimado</span>
              </div>
              <div class="system-stat">
                <span class="system-stat-value">{{ storageDiag.cadernoKeysCount }}</span>
                <span class="system-stat-label">Chaves do Caderno</span>
              </div>
              <div class="system-stat">
                <span class="system-stat-value">{{ storageDiag.keyCount }}</span>
                <span class="system-stat-label">Total de Chaves</span>
              </div>
            </div>

            <div class="actions wrap" style="margin-top: calc(var(--space-unit) * 0.75);">
              <button
                type="button"
                class="secondary"
                @click="handleCleanOrphans"
              >
                Limpar chaves obsoletas
              </button>
            </div>
          </article>

          <!-- Card 4: Restauração de Padrões -->
          <article class="system-card">
            <h3>Restaurar Padrões de Fábrica</h3>
            <p class="muted">
              Redefine as configurações visuais para o estado original caso deseje recomeçar a personalização.
            </p>

            <div class="actions wrap">
              <button
                type="button"
                class="secondary"
                @click="openResetModal"
              >
                Restaurar padrões de aparência
              </button>
            </div>
          </article>

          <!-- Card 5: Backup do Acervo -->
          <DatabaseBackup @open-restore="isRestoreModalOpen = true" />
        </section>

        <!-- Aba 4: Conta & Dispositivos (F02) -->
        <section
          v-show="activeTab === 'conta'"
          id="panel-conta"
          role="tabpanel"
          aria-labelledby="tab-conta"
          tabindex="0"
          class="panel"
        >
          <h2 id="conta-title">Conta & Dispositivos</h2>
          <p class="muted">
            Gerenciamento da conta conectada, sessões ativas e revogação remota de dispositivos.
          </p>

          <SessionsManager />
        </section>
      </div>

      <!-- Coluna Direita (Amostra Interativa / Live Preview) -->
      <div class="settings-sidebar">
        <AppearancePreview :preferences="preferences" />
      </div>
    </div>

    <!-- Modal de Confirmação de Reset -->
    <ConfirmResetModal
      :open="isResetModalOpen"
      :busy="isResetting"
      @confirm="confirmFactoryReset"
      @cancel="closeResetModal"
    />

    <!-- Modal de Restauração de Acervo -->
    <RestoreModal
      :open="isRestoreModalOpen"
      @close="isRestoreModalOpen = false"
      @restored="onAcervoRestored"
    />
  </section>
</template>

<style scoped>
.home-view-options {
  display: flex;
  flex-direction: column;
  gap: 0.625rem;
  margin-top: 0.75rem;
}

.radio-option {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0.625rem 0.875rem;
  min-height: 44px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-control, 0.5rem);
  background: var(--color-surface);
  cursor: pointer;
  transition: border-color 0.15s ease, background-color 0.15s ease;
  user-select: none;
}

.radio-option:hover {
  border-color: var(--color-border-hover, var(--color-accent));
  background-color: var(--color-surface-hover);
}

.radio-option input[type="radio"] {
  margin: 0;
  padding: 0;
  flex-shrink: 0;
  width: 1.15rem;
  height: 1.15rem;
  accent-color: var(--color-accent);
  cursor: pointer;
  display: inline-block;
  vertical-align: middle;
}

.radio-text {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.9375rem;
  line-height: 1.4;
  color: var(--color-text);
}
</style>