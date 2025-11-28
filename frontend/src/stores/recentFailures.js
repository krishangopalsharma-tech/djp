// Path: frontend/src/stores/recentFailures.js
import { defineStore } from 'pinia';
import { http } from '@/lib/http';
import { useUIStore } from './ui';

export const useRecentFailuresStore = defineStore('recentFailures', {
  state: () => ({
    items: [],
    loading: false,
    error: null,
  }),
  actions: {
    async fetchRecentFailures() {
      this.loading = true;
      this.error = null;
      const uiStore = useUIStore();
      try {
        const response = await http.get('/recent-failures/');
        this.items = response.data.results || response.data;
      } catch (err) {
        this.error = 'Failed to fetch recent failures.';
        uiStore.pushToast({ type: 'error', title: 'Error', message: this.error });
        console.error(err);
      } finally {
        this.loading = false;
      }
    },
  },
});