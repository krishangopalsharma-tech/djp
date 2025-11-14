import { defineStore } from 'pinia'
import { ref } from 'vue'
import { http } from '@/lib/http'
import { useUIStore } from './ui'

export const useCoreSettingsStore = defineStore('coreSettings', () => {
  const failureIdSettings = ref({
    prefix: 'RF',
    padding_digits: 4, // Use snake_case to match model
    reset_cycle: 'yearly',
  })
  const loading = ref(false)

  async function fetchFailureIdSettings() {
    loading.value = true
    const uiStore = useUIStore()
    try {
      // Fetch the singleton object directly. 
      // The viewset's list action returns the single object.
      const response = await http.get('/failure-id-settings/')
      failureIdSettings.value = response.data
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
      // We use PATCH on the singleton (pk=1)
      // The viewset's get_object() ensures we always update pk=1
      const response = await http.patch('/failure-id-settings/1/', payload)
      failureIdSettings.value = response.data
      uiStore.pushToast({ type: 'success', title: 'Success', message: 'Failure ID settings saved.' })
    } catch (err) {
      console.error('Failed to save Failure ID settings:', err)
      const errorDetail = err.response?.data ? JSON.stringify(err.response.data) : 'Could not save settings.';
      uiStore.pushToast({ type: 'error', title: 'Error', message: errorDetail })
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