// Path: frontend/src/stores/failures.js
import { defineStore } from 'pinia';
import { http } from '@/lib/http';
import { useUIStore } from './ui';

export const useFailureStore = defineStore('failure', {
  state: () => ({
    failures: [], // <-- ADD THIS LINE TO STORE THE LIST
    loading: false,
    error: null,
  }),
  actions: {
    // ADD THIS NEW ACTION TO FETCH THE LIST
    async fetchFailures() {
      this.loading = true;
      this.error = null;
      try {
        const response = await http.get('/failures/logs/');
        // The API nests results under a 'results' key if pagination is on
        this.failures = response.data.results || response.data;
      } catch (err) {
        this.error = 'Failed to fetch failure logs.';
        console.error(err);
      } finally {
        this.loading = false;
      }
    },

    async addFailure(payload) {
      const uiStore = useUIStore();
      this.loading = true;
      this.error = null;
      try {
        await http.post('/failures/logs/', payload);
        uiStore.pushToast({ type: 'success', title: 'Success', message: 'Failure log created.' });
        // After adding a new failure, refresh the main logbook list
        this.fetchFailures();
        return true;
      } catch (err) {
        const message = err.response?.data ? JSON.stringify(err.response.data) : 'Failed to create failure log.';
        this.error = message;
        uiStore.pushToast({ type: 'error', title: 'Error', message });
        console.error(err);
        return false;
      } finally {
        this.loading = false;
      }
    },
  },
});