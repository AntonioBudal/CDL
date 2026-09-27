import { createApp } from 'vue'
import App from './App.vue'
import { router } from './router'
import './appearance-bootstrap.js'
import { usePreferences } from './composables/usePreferences'

// Leitura síncrona das preferências e do tema antes da montagem para evitar FOUC e reset
usePreferences().loadFromLocal()

createApp(App).use(router).mount('#app')
