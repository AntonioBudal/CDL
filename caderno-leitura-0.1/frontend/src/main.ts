import { createApp } from 'vue'
import App from './App.vue'
import { router } from './router'
import './appearance-bootstrap.js'
import { usePreferences } from './composables/usePreferences'
import { installAvatarFallback } from './utils/avatarFallback'
import { i18n } from './i18n/index.ts'

// Leitura síncrona das preferências e do tema antes da montagem para evitar FOUC e reset
usePreferences().loadFromLocal()

installAvatarFallback()
createApp(App).use(i18n).use(router).mount('#app')
