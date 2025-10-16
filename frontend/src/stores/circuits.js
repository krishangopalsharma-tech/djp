import { defineStore } from 'pinia';

export const useCircuitsStore = defineStore('circuits', {
  state: () => ({
    circuits: [{ id: 1, circuit_id: 'CKT-MAIN-01', name: 'Main Line Feeder', severity: 'Critical' }],
    loading: false,
  }),
  actions: {
    async fetchCircuits() { this.loading = false; },
  },
});