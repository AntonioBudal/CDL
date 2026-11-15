<script setup lang="ts">
/** F0.12.09 (spec 122): idioma da interface. Aplica na hora, lembra no navegador e salva na conta. */
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { LOCALE_NAMES, SUPPORTED_LOCALES, isAppLocale, setLocale } from '../../i18n/index.ts'
import { usePreferences } from '../../composables/usePreferences'
import { useAuthStore } from '../../stores/auth.ts'

const { t, locale } = useI18n()
const preferences = usePreferences()
const auth = useAuthStore()
const status = ref('')
const current = computed(() => String(locale.value))

async function change(event: Event) {
  const value = (event.target as HTMLSelectElement).value
  if (!isAppLocale(value) || value === current.value) return
  setLocale(value)
  status.value = t('settings.languageSaved', { language: LOCALE_NAMES[value] })
  if (auth.isAuthenticated.value) await preferences.updatePreferences({ locale: value })
}
</script>

<template>
  <div class="language-selector">
    <label class="language-field" for="interface-language">
      <span class="language-label">{{ t('settings.language') }}</span>
      <select id="interface-language" :value="current" @change="change">
        <option v-for="code in SUPPORTED_LOCALES" :key="code" :value="code" :lang="code">{{ LOCALE_NAMES[code] }}</option>
      </select>
    </label>
    <p class="language-hint muted">{{ t('settings.languageHint') }}</p>
    <p class="visually-hidden" role="status" aria-live="polite">{{ status }}</p>
  </div>
</template>

<style scoped>
.language-selector {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  margin-top: 1.25rem;
  padding-top: 1rem;
  border-top: 1px solid var(--color-border-subtle);
}

.language-field {
  display: grid;
  gap: 4px;
  max-width: 22rem;
}

.language-label {
  font-weight: 600;
}

.language-field select {
  min-height: 44px;
  width: 100%;
}

.language-hint {
  margin: 0;
  font-size: 0.9rem;
}
</style>
