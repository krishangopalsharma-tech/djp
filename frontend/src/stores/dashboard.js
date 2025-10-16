import { defineStore } from 'pinia';
import { http } from '@/lib/http';
import { useUIStore } from './ui';

export const useDashboardStore = defineStore('dashboard', {
  state: () => ({
    data: null,
    loading: false,
    error: null,
  }),
  actions: {
    async fetchDashboardData(filters = {}) {
      this.loading = true;
      this.error = null;
      const uiStore = useUIStore();
      try {
        // Convert filter object to query parameters
        const params = new URLSearchParams();
        if (filters.range) params.append('range', filters.range);
        if (filters.sections && filters.sections.length) {
            filters.sections.forEach(id => params.append('sections[]', id));
        }
        // Add other filters like status if needed in the future

        const response = await http.get('/dashboard/data/', { params });
        this.data = response.data;
      } catch (err) {
        this.error = 'Failed to fetch dashboard data.';
        uiStore.pushToast({ type: 'error', title: 'Error', message: this.error });
        console.error(err);
      } finally {
        this.loading = false;
      }
    },
  },
});