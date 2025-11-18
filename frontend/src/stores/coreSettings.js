import { defineStore } from 'pinia'
import { ref } from 'vue'
import { http } from '@/lib/http'
import { useUIStore } from './ui'

export const useCoreSettingsStore = defineStore('coreSettings', () => {
  const failureIdSettings = ref({
    prefix: 'RF',
    padding: 4,
    reset_cycle: 'yearly',
  })
  const loading = ref(false)

  async function fetchFailureIdSettings() {
    loading.value = true
    const uiStore = useUIStore()
    try {
      // The backend list view for the singleton returns the object directly.
      const response = await http.get('/core/failure-id-settings/')
      // The response for a list is often nested, but our custom view returns the object directly.
      // However, a standard ViewSet list view would return { results: [...] }
      // So we handle both cases.
      if (response.data && response.data.results) {
         // This handles the case where the default list view is used.
         // Since we expect only one, we take the first.
        if (response.data.results.length > 0) {
            failureIdSettings.value = response.data.results[0];
        }
      } else {
        // This handles our custom list view that returns a single object.
        failureIdSettings.value = response.data
      }
    } catch (err) {
      console.error('Failed to fetch Failure ID settings:', err)
      uiStore.pushToast({ type: 'error', title: 'Error', message: 'Could not load Failure ID settings.' })
    } finally {
      loading.value = false
    }
  }

  async function saveFailureIdSettings(payload) {
    loading.value = true
    const uiStore = useUIStore()
    try {
      // The singleton is always at pk=1, so we update it there.
      const response = await http.patch('/core/failure-id-settings/1/', payload)
      failureIdSettings.value = response.data
      uiStore.pushToast({ type: 'success', title: 'Success', message: 'Failure ID settings saved.' })
    } catch (err) {
      console.error('Failed to save Failure ID settings:', err)
      uiStore.pushToast({ type: 'error', title: 'Error', message: 'Could not save Failure ID settings.' })
    } finally {
      loading.value = false
    }
  }

  return {
    failureIdSettings,
    loading,
    fetchFailureIdSettings,
    saveFailureIdSettings,
  }
})