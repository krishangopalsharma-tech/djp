import { defineStore } from 'pinia';
import { http } from '@/lib/http';
import { useUIStore } from './ui';

export const useLogbookStore = defineStore('logbook', {
  state: () => ({
    failures: [],
    count: 0,
    num_pages: 1,
    loading: false,
    error: null,
  }),
  actions: {
    async fetchLogbookData(params = {}) {
      this.loading = true;
      this.error = null;
      const uiStore = useUIStore();
      try {
        const response = await http.get('/logbook/data/', { params });
        this.failures = response.data.results;
        this.count = response.data.count;
        this.num_pages = response.data.num_pages;
      } catch (err) {
        this.error = 'Failed to fetch logbook data.';
        uiStore.pushToast({ type: 'error', title: 'Error', message: this.error });
        console.error(err);
      } finally {
        this.loading = false;
      }
    },
  },
});