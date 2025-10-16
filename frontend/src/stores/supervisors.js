import { defineStore } from 'pinia';

export const useSupervisorsStore = defineStore('supervisors', {
  state: () => ({
    supervisors: [{ id: 1, name: 'John Doe', designation: 'Sr. Supervisor', depot: 1, depot_name: 'Main Depot' }],
    loading: false,
  }),
  actions: {
    async fetchSupervisors() { this.loading = false; },
  },
});