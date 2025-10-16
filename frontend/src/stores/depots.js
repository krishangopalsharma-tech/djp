import { defineStore } from 'pinia';

export const useDepotsStore = defineStore('depots', {
  state: () => ({
    depots: [{ id: 1, name: 'Main Depot', code: 'MAIN', location: 'Central City' }],
    loading: false,
  }),
  actions: {
    async fetchDepots() { this.loading = false; },
  },
});