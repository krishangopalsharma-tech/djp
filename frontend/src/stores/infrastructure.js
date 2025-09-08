// Path: frontend/src/stores/infrastructure.js

import { defineStore } from 'pinia'
import { http } from '@/lib/http'

export const useInfrastructureStore = defineStore('infrastructure', {
  state: () => ({
    depots: [],
    stations: [],
    sections: [],
    circuits: [],
    supervisors: [],
    loading: {
      depots: false,
      stations: false,
      sections: false,
      circuits: false,
      supervisors: false,
    },
    error: null,
  }),
  actions: {
    async fetchDepots() {
      this.loading.depots = true
      this.error = null
      try {
        const response = await http.get('/infrastructure/depots/')
        this.depots = response.data.results || response.data
      } catch (err) {
        this.error = 'Failed to fetch depots.'
        console.error(err)
      } finally {
        this.loading.depots = false
      }
    },
    async fetchStations() {
      this.loading.stations = true
      this.error = null
      try {
        const response = await http.get('/infrastructure/stations/')
        this.stations = response.data.results || response.data
      } catch (err) {
        this.error = 'Failed to fetch stations.'
        console.error(err)
      } finally {
        this.loading.stations = false
      }
    },
    // We will add more fetch actions for sections, circuits, etc. here later.
  },
})