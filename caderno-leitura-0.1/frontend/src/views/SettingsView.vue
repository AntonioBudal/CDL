<script setup lang="ts">
import { onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import AppearanceControls from '../components/AppearanceControls.vue'
import AppearancePreview from '../components/AppearancePreview.vue'
import DatabaseBackup from '../components/DatabaseBackup.vue'
import ConfirmResetModal from '../components/ConfirmResetModal.vue'
import RestoreModal from '../components/RestoreModal.vue'
import SessionsManager from '../components/auth/SessionsManager.vue'
import AvatarUploadModal from '../components/profile/AvatarUploadModal.vue'
import Icon from '../components/ui/Icon.vue'
import { fetchHealth, type HealthResponse } from '../services/api'
import { useSuperclassPhysics } from '../composables/useSuperclassPhysics'
import { useProfile } from '../composables/useProfile.ts'
import type { AppearancePreferences } from '../appearance'
import type { HealthCheckResult, HomeViewPreference, SettingsTab, SettingsTabId, StorageDiagnostic, VisibilityLevel } from '../types'

const appearance = window.cadernoAppearance
const preferences = reactive(appearance?.get() ?? ({} as AppearancePreferences))
const message = ref('')
const physics = useSuperclassPhysics()

const route = useRoute()
const profileService = useProfile()
const isAvatarModalOpen = ref(false)
const profileSuccessMessage = ref('')
const profileErrorMessage = ref('')
const isSavingProfile = ref(false)

const profileForm = reactive<{
  username: string
  display_name: string
  bio: string
  profile_visibility: VisibilityLevel
  dashboard_visibility: VisibilityLevel
  is_discoverable: boolean
  show_reading_stats: boolean
}>({
  username: '',
  display_name: '',
  bio: '',
  profile_visibility: 'public',
  dashboard_visibility: 'private',
  is_discoverable: true,
  show_reading_stats: true,
})

function populateProfileForm() {
  const p = profileService.profile.value
  if (!p) return
  profileForm.username = p.username || ''
  profileForm.display_name = p.display_name || ''
  profileForm.bio = p.bio || ''
  profileForm.profile_visibility = p.profile_visibility || 'public'
  profileForm.dashboard_visibility = p.dashboard_visibility || 'private'
  profileForm.is_discoverable = p.is_discoverable ?? true
  profileForm.show_reading_stats = p.show_reading_stats ?? true
}

async function loadProfileData() {
  await profileService.fetchProfile()
  populateProfileForm()
}

async function handleSaveProfile() {
  profileErrorMessage.value = ''
  profileSuccessMessage.value = ''

  const cleanUsername = profileForm.username.trim()
  if (!cleanUsername) {
    profileErrorMessage.value = 'O identificador (@username) não pode ficar vazio.'
    return
  }
  if (!/^[a-zA-Z0-9._-]{3,30}$/.test(cleanUsername)) {
    profileErrorMessage.value = 'O identificador @username deve ter entre 3 e 30 caracteres alfanuméricos, hífens ou pontos.'
    return
  }
  if (profileForm.display_name.trim().length > 60) {
    profileErrorMessage.value = 'O nome de exibição não pode ultrapassar 60 caracteres.'
    return
  }
  if (profileForm.bio.length > 280) {
    profileErrorMessage.value = 'A biografia não pode ultrapassar 280 caracteres.'
    return
  }

  isSavingProfile.value = true
  try {
    await profileService.updateProfile({
      username: cleanUsername,
      display_name: profileForm.display_name.trim() || cleanUsername,
      bio: profileForm.bio.trim() || null,
      profile_visibility: profileForm.profile_visibility,
      dashboard_visibility: profileForm.dashboard_visibility,
      is_discoverable: profileForm.is_discoverable,
      show_reading_stats: profileForm.show_reading_stats,
    })
    populateProfileForm()
    profileSuccessMessage.value = 'Perfil e preferências de privacidade atualizados com sucesso.'
    if (typeof document !== 'undefined' && document.activeElement instanceof HTMLElement) {
      physics.triggerHapticPulse(document.activeElement, 'step')
    }
  } catch (err: unknown) {
    const msg = err instanceof Error ? err.message : 'Falha ao salvar perfil.'
    if (msg.includes('409') || msg.toLowerCase().includes('conflict') || msg.toLowerCase().includes('já está em uso')) {
      profileErrorMessage.value = `O identificador @${cleanUsername} já está sendo utilizado por outro leitor.`
    } else {
      profileErrorMessage.value = msg
    }
  } finally {
    isSavingProfile.value = false
  }
}

const activeTab = ref<SettingsTabId>('perfil')

const tabs: SettingsTab[] = [
  { id: 'perfil', label: 'Perfil & Privacidade', description: 'Identidade pública, avatar e visibilidade' },
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
  if (route.query.tab && tabs.some(t => t.id === route.query.tab)) {
    activeTab.value = route.query.tab as SettingsTabId
  }
  initHomeViewPreference()
  updateStorageDiagnostic()
  void checkHealth()
  void loadProfileData()
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
        <!-- Aba 0: Perfil & Privacidade (F05) -->
        <section
          v-show="activeTab === 'perfil'"
          id="panel-perfil"
          role="tabpanel"
          aria-labelledby="tab-perfil"
          tabindex="0"
          class="panel profile-settings-panel"
        >
          <div class="panel-header-row">
            <div>
              <h2 id="profile-title">Perfil & Privacidade</h2>
              <p class="muted">
                Gerencie sua identidade pública, avatar e os níveis de visibilidade de estudos e acervo.
              </p>
            </div>
            <RouterLink
              v-if="profileService.profile.value?.username"
              :to="'/@' + profileService.profile.value.username"
              class="button secondary view-public-btn"
              title="Visualizar como outros leitores veem seu perfil"
            >
              <Icon name="external-link" :size="15" />
              <span>Ver perfil público</span>
            </RouterLink>
          </div>

          <!-- Mensagens de Feedback -->
          <p
            v-if="profileSuccessMessage"
            class="notice"
            role="status"
            aria-live="polite"
          >
            {{ profileSuccessMessage }}
          </p>
          <div
            v-if="profileErrorMessage"
            class="auth-error-alert"
            role="alert"
          >
            <Icon name="alert-triangle" :size="16" />
            <span>{{ profileErrorMessage }}</span>
          </div>

          <form @submit.prevent="handleSaveProfile" class="profile-form">
            <!-- Card de Avatar -->
            <article class="system-card">
              <h3>Avatar do Perfil</h3>
              <p class="muted">
                Foto ou imagem exibida nos seus comentários, perfil público e cabeçalho.
              </p>

              <div class="avatar-edit-row">
                <div class="avatar-current-wrap">
                  <img
                    v-if="profileService.profile.value?.avatar_url"
                    :src="profileService.profile.value.avatar_url"
                    alt="Avatar atual"
                    class="avatar-thumb"
                  />
                  <div v-else class="avatar-thumb-initials" aria-hidden="true">
                    {{ profileService.initials.value }}
                  </div>
                </div>

                <div class="avatar-actions-wrap">
                  <button
                    type="button"
                    class="secondary"
                    @click="isAvatarModalOpen = true"
                  >
                    <Icon name="camera" :size="16" />
                    <span>Alterar Avatar…</span>
                  </button>
                  <span class="muted font-small">
                    Recorte quadrado de 256x256 WebP (PNG, JPEG ou WebP até 2MB).
                  </span>
                </div>
              </div>
            </article>

            <!-- Card de Identidade Pública -->
            <article class="system-card">
              <h3>Identidade Pública</h3>
              <p class="muted">
                Defina como você é reconhecido por outros leitores na rede do Caderno.
              </p>

              <div class="field-group">
                <label for="profile-username" class="field-label">
                  Identificador Público (@username)
                  <span class="required-mark">*</span>
                </label>
                <div class="handle-input-wrap">
                  <span class="handle-prefix" aria-hidden="true">@</span>
                  <input
                    id="profile-username"
                    v-model="profileForm.username"
                    type="text"
                    required
                    maxlength="30"
                    placeholder="leitor"
                    class="handle-input"
                    autocomplete="username"
                  />
                </div>
                <span class="field-hint muted">
                  De 3 a 30 caracteres (letras, números, hífens ou pontos).
                </span>
              </div>

              <div class="field-group">
                <label for="profile-display-name" class="field-label">
                  Nome de Exibição
                  <span class="required-mark">*</span>
                </label>
                <input
                  id="profile-display-name"
                  v-model="profileForm.display_name"
                  type="text"
                  required
                  maxlength="60"
                  placeholder="Seu nome ou pseudônimo"
                  class="text-input"
                />
                <span class="field-hint muted">
                  Nome amigável exibido com destaque nos cartões e anotações (até 60 caracteres).
                </span>
              </div>

              <div class="field-group">
                <div class="label-with-counter">
                  <label for="profile-bio" class="field-label">Biografia Curta</label>
                  <span
                    class="char-counter"
                    :class="{ 'counter-limit': 280 - (profileForm.bio?.length || 0) < 20 }"
                  >
                    {{ 280 - (profileForm.bio?.length || 0) }} restantes
                  </span>
                </div>
                <textarea
                  id="profile-bio"
                  v-model="profileForm.bio"
                  rows="3"
                  maxlength="280"
                  placeholder="Compartilhe seus interesses de leitura, temas de estudo ou uma breve citação..."
                  class="textarea-input"
                ></textarea>
                <span class="field-hint muted">
                  Apresentação sucinta aos outros leitores (até 280 caracteres).
                </span>
              </div>

              <!-- Blindagem de E-mail (Aviso de Sigilo) -->
              <div class="email-protection-note">
                <Icon name="shield" :size="18" class="shield-icon" />
                <div class="protection-text">
                  <strong>E-mail Estritamente Protegido</strong>
                  <p class="muted">
                    Seu endereço de e-mail (<code>{{ profileService.profile.value?.email || 'vinculado' }}</code>) é de uso estritamente privativo da sua conta e nunca é revelado a terceiros em buscas, perfis públicos ou compartilhamentos.
                  </p>
                </div>
              </div>
            </article>

            <!-- Card de Níveis de Visibilidade Desacoplados -->
            <article class="system-card">
              <h3>Controles de Privacidade Desacoplados</h3>
              <p class="muted">
                Escolha com autonomia o nível de exposição do seu perfil e do seu painel de estudos.
              </p>

              <!-- Visibilidade do Perfil -->
              <div class="privacy-section">
                <h4 class="privacy-subheading">
                  <Icon name="user" :size="16" />
                  <span>Visibilidade do Perfil</span>
                </h4>
                <p class="muted">
                  Controla quem pode visualizar seu nome, avatar, biografia e acervo.
                </p>

                <div class="privacy-options" role="radiogroup" aria-label="Visibilidade do Perfil">
                  <label class="radio-option">
                    <input
                      type="radio"
                      name="profileVisibility"
                      value="public"
                      :checked="profileForm.profile_visibility === 'public'"
                      @change="profileForm.profile_visibility = 'public'"
                    />
                    <span class="radio-text">
                      <strong>Público</strong> — Acessível para qualquer leitor do sistema
                    </span>
                  </label>
                  <label class="radio-option">
                    <input
                      type="radio"
                      name="profileVisibility"
                      value="friends"
                      :checked="profileForm.profile_visibility === 'friends'"
                      @change="profileForm.profile_visibility = 'friends'"
                    />
                    <span class="radio-text">
                      <strong>Apenas Amigos</strong> — Restrito a leitores com relacionamento aceito
                    </span>
                  </label>
                  <label class="radio-option">
                    <input
                      type="radio"
                      name="profileVisibility"
                      value="private"
                      :checked="profileForm.profile_visibility === 'private'"
                      @change="profileForm.profile_visibility = 'private'"
                    />
                    <span class="radio-text">
                      <strong>Privado</strong> — Oculta biografia e exibe cartão institucional discreto
                    </span>
                  </label>
                </div>
              </div>

              <!-- Visibilidade do Dashboard -->
              <div class="privacy-section">
                <h4 class="privacy-subheading">
                  <Icon name="layout-dashboard" :size="16" />
                  <span>Visibilidade do Painel de Estudos (Dashboard)</span>
                </h4>
                <p class="muted">
                  Controla quem pode acessar a síntese dos seus hábitos de estudo e leituras recentes.
                </p>

                <div class="privacy-options" role="radiogroup" aria-label="Visibilidade do Dashboard">
                  <label class="radio-option">
                    <input
                      type="radio"
                      name="dashboardVisibility"
                      value="public"
                      :checked="profileForm.dashboard_visibility === 'public'"
                      @change="profileForm.dashboard_visibility = 'public'"
                    />
                    <span class="radio-text">
                      <strong>Público</strong> — Visitantes podem explorar seu painel de estudos
                    </span>
                  </label>
                  <label class="radio-option">
                    <input
                      type="radio"
                      name="dashboardVisibility"
                      value="friends"
                      :checked="profileForm.dashboard_visibility === 'friends'"
                      @change="profileForm.dashboard_visibility = 'friends'"
                    />
                    <span class="radio-text">
                      <strong>Apenas Amigos</strong> — Apenas seus amigos veem o painel
                    </span>
                  </label>
                  <label class="radio-option">
                    <input
                      type="radio"
                      name="dashboardVisibility"
                      value="private"
                      :checked="profileForm.dashboard_visibility === 'private'"
                      @change="profileForm.dashboard_visibility = 'private'"
                    />
                    <span class="radio-text">
                      <strong>Privado</strong> — Hábitos e ritmo de estudos estritamente restritos a você
                    </span>
                  </label>
                </div>
              </div>
            </article>

            <!-- Card de Estatísticas e Descobrimento -->
            <article class="system-card">
              <h3>Descoberta e Métricas de Leitura</h3>
              <p class="muted">
                Ajuste fino de exposição quantitativa de estudos e aparição em buscas.
              </p>

              <div class="checkbox-options">
                <label class="checkbox-option">
                  <input
                    type="checkbox"
                    v-model="profileForm.show_reading_stats"
                  />
                  <span class="checkbox-text">
                    <strong>Exibir estatísticas no perfil público</strong>
                    <span class="muted font-small">
                      Apresenta contadores de obras, fichamentos e dias consecutivos de estudo.
                    </span>
                  </span>
                </label>

                <label class="checkbox-option">
                  <input
                    type="checkbox"
                    v-model="profileForm.is_discoverable"
                  />
                  <span class="checkbox-text">
                    <strong>Perfil descobrível em buscas</strong>
                    <span class="muted font-small">
                      Permite que seu nome de exibição e @username apareçam nos resultados de pesquisa de leitores.
                    </span>
                  </span>
                </label>
              </div>
            </article>

            <!-- Botão de Gravação do Formulário -->
            <div class="form-submit-row actions">
              <button
                type="submit"
                class="primary save-profile-btn"
                :disabled="isSavingProfile"
                :aria-busy="isSavingProfile"
              >
                {{ isSavingProfile ? 'Gravando alterações…' : 'Salvar Alterações de Perfil' }}
              </button>
            </div>
          </form>
        </section>

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

    <!-- Modal de Upload de Avatar (F05) -->
    <AvatarUploadModal
      :open="isAvatarModalOpen"
      :current-avatar-url="profileService.profile.value?.avatar_url"
      :google-avatar-url="profileService.profile.value?.google_avatar_url"
      :has-google-avatar="profileService.profile.value?.has_google_avatar"
      :initials="profileService.initials.value"
      @close="isAvatarModalOpen = false"
      @updated="loadProfileData"
    />
  </section>
</template>

<style scoped>
.panel-header-row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 1.25rem;
}

.view-public-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  min-height: 44px;
  padding: 0.4rem 0.85rem;
  font-size: 0.875rem;
  text-decoration: none;
}

.profile-form {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.avatar-edit-row {
  display: flex;
  align-items: center;
  gap: 1.25rem;
  margin-top: 0.75rem;
}

.avatar-current-wrap {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  overflow: hidden;
  border: 2px solid var(--color-accent);
  background: var(--color-surface-soft, rgba(0, 0, 0, 0.04));
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.avatar-thumb {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-thumb-initials {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--color-accent);
  letter-spacing: 0.04em;
  user-select: none;
}

.avatar-actions-wrap {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.field-group {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  margin-top: 1rem;
}

.field-label {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text);
}

.required-mark {
  color: #dc2626;
}

.field-hint {
  font-size: 0.75rem;
}

.handle-input-wrap {
  display: flex;
  align-items: center;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-control, 6px);
  background: var(--color-surface);
  overflow: hidden;
  transition: border-color 0.15s ease;
}

.handle-input-wrap:focus-within {
  border-color: var(--color-accent);
}

.handle-prefix {
  padding: 0.625rem 0.85rem;
  background: var(--color-surface-soft, rgba(0, 0, 0, 0.04));
  color: var(--color-muted);
  font-weight: 600;
  border-right: 1px solid var(--color-border);
  user-select: none;
}

.handle-input {
  flex: 1;
  border: none;
  background: transparent;
  padding: 0.625rem 0.85rem;
  min-height: 44px;
  font-size: 0.9375rem;
  color: var(--color-text);
  outline: none;
}

.text-input {
  width: 100%;
  min-height: 44px;
  padding: 0.625rem 0.85rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-control, 6px);
  background: var(--color-surface);
  font-size: 0.9375rem;
  color: var(--color-text);
}

.text-input:focus {
  border-color: var(--color-accent);
  outline: none;
}

.label-with-counter {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.char-counter {
  font-size: 0.75rem;
  color: var(--color-muted);
}

.counter-limit {
  color: #dc2626;
  font-weight: 600;
}

.textarea-input {
  width: 100%;
  padding: 0.625rem 0.85rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-control, 6px);
  background: var(--color-surface);
  font-size: 0.9375rem;
  line-height: 1.5;
  color: var(--color-text);
  resize: vertical;
  min-height: 80px;
}

.textarea-input:focus {
  border-color: var(--color-accent);
  outline: none;
}

.email-protection-note {
  display: flex;
  gap: 0.75rem;
  padding: 0.875rem 1rem;
  border-radius: var(--radius-control, 6px);
  background: var(--color-surface-soft, rgba(0, 0, 0, 0.03));
  border: 1px solid var(--color-border);
  margin-top: 1.25rem;
}

.shield-icon {
  color: var(--color-accent);
  flex-shrink: 0;
  margin-top: 0.15rem;
}

.protection-text {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  font-size: 0.8125rem;
}

.protection-text p {
  margin: 0;
  line-height: 1.4;
}

.privacy-section {
  margin-top: 1.25rem;
}

.privacy-subheading {
  display: flex;
  align-items: center;
  gap: 0.45rem;
  font-size: 0.9375rem;
  margin: 0 0 0.25rem;
  color: var(--color-text);
}

.privacy-options {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-top: 0.625rem;
}

.checkbox-options {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-top: 0.75rem;
}

.checkbox-option {
  display: flex;
  align-items: flex-start;
  gap: 0.625rem;
  padding: 0.75rem 1rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-control, 6px);
  background: var(--color-surface);
  cursor: pointer;
  min-height: 44px;
  user-select: none;
  transition: border-color 0.15s ease, background-color 0.15s ease;
}

.checkbox-option:hover {
  border-color: var(--color-border-hover, var(--color-accent));
  background-color: var(--color-surface-hover);
}

.checkbox-option input[type="checkbox"] {
  width: 1.15rem;
  height: 1.15rem;
  margin-top: 0.15rem;
  flex-shrink: 0;
  accent-color: var(--color-accent);
  cursor: pointer;
}

.checkbox-text {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
  font-size: 0.9375rem;
  color: var(--color-text);
}

.form-submit-row {
  margin-top: 0.5rem;
  justify-content: flex-start;
}

.save-profile-btn {
  min-height: 44px;
  padding: 0.625rem 1.75rem;
  font-size: 0.9375rem;
}

.auth-error-alert {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  border-radius: var(--radius-control, 6px);
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #991b1b;
  font-size: 0.8125rem;
  margin-bottom: 1rem;
}

.font-small {
  font-size: 0.75rem;
}

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