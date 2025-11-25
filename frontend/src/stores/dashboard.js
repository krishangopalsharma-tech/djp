import { defineStore } from 'pinia'
import { http } from '@/lib/http'

export const useDashboardStore = defineStore('dashboard', {
  state: () => ({
    kpis: null,
    charts: null,
    loading: false,
    error: null,
  }),
  actions: {
    async fetchDashboardData(filters = {}) {
      this.loading = true
      this.error = null
      try {
        const params = {
          range: filters.range,
          'sections[]': filters.sections,
        }
        const response = await http.get('/dashboard/data/', { params })
        this.kpis = response.data.kpis
        this.charts = response.data.charts
      } catch (err) {
        this.error = 'Failed to fetch dashboard data.'
        console.error(err)
      } finally {
        this.loading = false
      }
    },
  },
})