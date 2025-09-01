import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useUIStore = defineStore('ui', () => {
  // --- THEME ---
  const theme = ref(localStorage.getItem('theme') || 'light')

// Add the palettes you want to expose in the UI
const themes = ref([
  'light',
  'dark',
  'railway',
  'feather',  // Feather Step Classic
  'fashion',  // Fashion
  'cherry',   // The Cherry Tree
  'lgm',
  'haqq', 'axencis', 'gantry', 'lukas', 'askit', 'shipp', 'wemakefab', 'stereotype', 'wildgoats', 'gymicons',
  // you can keep adding more here later:
  // 'lgm', 'haqq', 'axencis', 'gantry', 'lukas', 'askit', 'shipp', 'wemakefab', 'stereotype', 'wildgoats', 'gymicons'
])

  /**
   * Set the active theme and persist it.
   * @param {string} name - Theme key (e.g., 'light', 'dark', 'railway').
   * @returns {void}
   */
  function setTheme(name) {
    if (!themes.value.includes(name)) return
    theme.value = name
    localStorage.setItem('theme', name)
  }
  /**
   * Toggle between 'light' and 'dark' themes.
   * @returns {void}
   */
  function toggleDark() {
    setTheme(theme.value === 'dark' ? 'light' : 'dark')
  }

  // --- SIDEBAR ---
  const SIDEBAR_MIN = 56
  const SIDEBAR_COLLAPSED = 64
  const SIDEBAR_MAX = 360
  const SNAP_THRESHOLD = 80 // px

  const sidebarWidth = ref(Number(localStorage.getItem('sidebarWidth') || 256))
  if (isNaN(sidebarWidth.value)) sidebarWidth.value = 256
  const sidebarCollapsed = ref(localStorage.getItem('sidebarCollapsed') === 'true')

  const computedSidebarWidth = computed(() => (sidebarCollapsed.value ? SIDEBAR_COLLAPSED : sidebarWidth.value))
  function setSidebarWidth(px) {
    const n = Math.round(Number(px))
    if (Number.isFinite(n)) {
      const clamped = Math.max(SIDEBAR_MIN, Math.min(SIDEBAR_MAX, n))
      sidebarWidth.value = clamped
      localStorage.setItem('sidebarWidth', String(clamped))
    }
  }
  function setSidebarCollapsed(v) {
    sidebarCollapsed.value = !!v
    localStorage.setItem('sidebarCollapsed', String(sidebarCollapsed.value))
  }
  function toggleSidebarCollapsed() { setSidebarCollapsed(!sidebarCollapsed.value) }
  function snapSidebar(currentPx) {
    const w = Number(currentPx ?? sidebarWidth.value)
    if (w <= SNAP_THRESHOLD) {
      setSidebarCollapsed(true)
      setSidebarWidth(SIDEBAR_COLLAPSED)
    } else {
      setSidebarCollapsed(false)
    }
  }

  // --- TOASTS (unchanged API) ---
  const toasts = ref([])
  let idSeq = 1
  /**
   * Push a toast notification to the queue.
   * @param {{ type?: string, title?: string, message?: string }} [opts]
   * @returns {void}
   */
  function pushToast({ type = 'info', title = '', message = '' } = {}) {
    const id = idSeq++
    toasts.value.push({ id, type, title, message })
    setTimeout(() => removeToast(id), 4000)
  }
  /**
   * Remove a toast by its id.
   * @param {number} id
   * @returns {void}
   */
  function removeToast(id) {
    toasts.value = toasts.value.filter(t => t.id !== id)
  }
  function clearToasts() {
    toasts.value = []
  }

  return {
    theme, themes, setTheme, toggleDark,
    // sidebar
    sidebarWidth, sidebarCollapsed, computedSidebarWidth,
    setSidebarWidth, setSidebarCollapsed, toggleSidebarCollapsed, snapSidebar,
    // toasts
    toasts, pushToast, removeToast, clearToasts,
    // constants (optional export for tests)
    SIDEBAR_MIN, SIDEBAR_COLLAPSED, SIDEBAR_MAX, SNAP_THRESHOLD,
  }
})
