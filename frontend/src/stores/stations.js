import { defineStore } from 'pinia';

export const useStationsStore = defineStore('stations', {
  state: () => ({
    stations: [{ id: 1, name: 'Central Station', code: 'CTR', depot: 1, depot_name: 'Main Depot', equipment_count: 5 }],
    loading: false,
  }),
  actions: {
    async fetchStations() { this.loading = false; },
  },
});