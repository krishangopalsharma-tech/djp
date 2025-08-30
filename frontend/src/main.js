import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import { router } from './router'
import './assets/tailwind.css'

// Global theming system (tokens + themes + primitives)
import './styles/tokens.css'
import './styles/theme.css'
import './styles/brands.css'
import './styles/components.css'

// PrimeVue (FREE) + Tooltip + Toast (PT already wired in previous step)
import PrimeVue from 'primevue/config'
import Aura from '@primevue/themes/aura'
import Button from 'primevue/button'
import Tooltip from 'primevue/tooltip'
import ToastService from 'primevue/toastservice'
import 'primeicons/primeicons.css'
import primevuePT from './primevue-pt'

// Stores
import { useAuthStore } from './stores/auth'
import { useUIStore } from './stores/ui'

// Theme helper
import { initTheme } from './lib/theme'
import { initBrand } from './lib/brand'
import { initPresetIfAny } from './lib/presets'

// Initialize brand first (primary derives from brand), then theme
initBrand()
initTheme()
initPresetIfAny()

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)

app.use(PrimeVue, {
  theme: { preset: Aura },
  ripple: true,
  pt: primevuePT,
  ptOptions: { mergeSections: true, mergeProps: true }
})
app.use(ToastService)
app.component('PButton', Button)
app.directive('tooltip', Tooltip)

// Restore stores
const auth = useAuthStore()
auth.initFromStorage()

const ui = useUIStore()
ui.loadBrand()
ui.loadTheme()

app.mount('#app')

// DEV-only: quick showcase overlay when visiting ?style=1 (kept as-is)
if (import.meta.env.DEV && new URLSearchParams(window.location.search).has('style')) {
  import('./components/StyleShowcase.vue').then(({ default: StyleShowcase }) => {
    const host = document.createElement('div')
    host.id = '__style_showcase'
    host.style.position = 'fixed'
    host.style.inset = '0'
    host.style.zIndex = '9999'
    host.style.overflow = 'auto'
    host.style.pointerEvents = 'auto'
    document.body.appendChild(host)
    const showcase = createApp(StyleShowcase)
    // Install PrimeVue + PT + ToastService for the overlay app
    showcase.use(PrimeVue, {
      theme: { preset: Aura },
      ripple: true,
      pt: primevuePT,
      ptOptions: { mergeSections: true, mergeProps: true }
    })
    showcase.use(ToastService)
    showcase.component('PButton', Button)
    showcase.directive('tooltip', Tooltip)
    showcase.mount(host)
 })
}
