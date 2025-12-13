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
          'status[]': filters.status,
        }
        const response = await http.get('/dashboard/data/', { params })
        console.log('Dashboard Store Response:', response.data)
        this.kpis = response.data.kpis
        this.charts = response.data.charts
      } catch (err) {
        this.error = 'Failed to fetch dashboard data.'
        console.error('Dashboard Store Error:', err)
      } finally {
        this.loading = false
      }
    },
  },
})