// frontend/src/main.js
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import { router } from './router'   // ✅ named import to match your router file
import './assets/tailwind.css'
import './style.css'
import { applyChartTheme, activateChartThemeAutoUpdate } from './lib/chartTheme'

const app = createApp(App)
app.use(createPinia())
app.use(router)
// Apply Chart.js theme defaults from CSS vars and re-apply on theme changes
applyChartTheme()
activateChartThemeAutoUpdate()
app.mount('#app')
