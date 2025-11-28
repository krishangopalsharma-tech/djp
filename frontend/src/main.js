// frontend/src/main.js
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import { router } from './router'   // ✅ named import to match your router file
import './assets/tailwind.css'
import './style.css'
import { applyChartTheme } from './lib/chartTheme'

const app = createApp(App)
const pinia = createPinia()
app.use(pinia)

// Hydrate auth store from localStorage
import { useAuthStore } from './stores/auth'
const authStore = useAuthStore()
authStore.initFromStorage()
app.use(router)
// Apply Chart.js theme defaults from CSS vars (single theme)
applyChartTheme()
app.mount('#app')
