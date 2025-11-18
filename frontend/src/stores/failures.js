// Path: frontend/src/stores/failures.js
import { defineStore } from 'pinia';
import { http } from '@/lib/http';
import { useUIStore } from './ui';

export const useFailureStore = defineStore('failure', {
  state: () => ({
    failures: [],
    currentFailure: null,
    loading: false,
    error: null,
    archivedFailures: [],
  }),
  actions: {
    async fetchFailures() {
      this.loading = true;
      this.error = null;
      try {
        const response = await http.get('/failures/logs/');
        this.failures = response.data.results || response.data;
      } catch (err) {
        this.error = 'Failed to fetch failure logs.';
        console.error(err);
      } finally {
        this.loading = false;
      }
    },

    async fetchFailure(id) {
      this.loading = true;
      this.error = null;
      try {
        const response = await http.get(`/failures/logs/${id}/`);
        this.currentFailure = response.data;
      } catch (err) {
        this.error = 'Failed to fetch failure log.';
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
        const response = await http.post('/failures/logs/', payload);
        uiStore.pushToast({ type: 'success', title: 'Success', message: 'Failure log created.' });
        this.fetchFailures();
        return response.data; // Return the new failure object
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

    async updateFailure(id, payload) {
      const uiStore = useUIStore();
      this.loading = true;
      this.error = null;
      try {
        const response = await http.patch(`/failures/logs/${id}/`, payload);
        uiStore.pushToast({ type: 'success', title: 'Success', message: 'Failure log updated.' });
        this.fetchFailures();
        return response.data; // <-- Add this line
      } catch (err) {
        const message = err.response?.data ? JSON.stringify(err.response.data) : 'Failed to update failure log.';
        this.error = message;
        uiStore.pushToast({ type: 'error', title: 'Error', message });
        console.error(err);
      } finally {
        this.loading = false;
      }
    },

    async archiveFailure(id, reason) {
      const uiStore = useUIStore();
      this.loading = true;
      this.error = null;
      try {
        await http.post(`/failures/logs/${id}/archive/`, { reason });
        uiStore.pushToast({ type: 'success', title: 'Success', message: 'Failure log archived.' });
        await this.fetchFailures();
      } catch (err) {
        const message = err.response?.data ? JSON.stringify(err.response.data) : 'Failed to archive failure log.';
        this.error = message;
        uiStore.pushToast({ type: 'error', title: 'Error', message });
        console.error(err);
      } finally {
        this.loading = false;
      }
    },

    async sendFailureNotification(failureId, groupKeys) {
      const uiStore = useUIStore();
      this.loading = true;
      this.error = null;
      try {
        const response = await http.post(`/failures/logs/${failureId}/notify/`, { groups: groupKeys });
        // (The toast is already handled in FailureNew.vue, so no need to add one here)
      } catch (err) {
        const message = err.response?.data?.error || 'Failed to send notification.';
        this.error = message;
        uiStore.pushToast({ type: 'error', title: 'Error', message });
        console.error(err);
      } finally {
        this.loading = false;
      }
    },

    async fetchArchivedFailures() {
      this.loading = true;
      this.error = null;
      const uiStore = useUIStore();
      try {
        const response = await http.get('/failures/logs/archived/');
        this.archivedFailures = response.data.results || response.data;
      } catch (err) {
        this.error = 'Failed to fetch archived failures.';
        uiStore.pushToast({ type: 'error', title: 'Error', message: this.error });
        console.error(err);
      } finally {
        this.loading = false;
      }
    },

    async permanentlyDeleteFailure(id) {
      const uiStore = useUIStore();
      this.loading = true;
      this.error = null;
      try {
        await http.delete(`/failures/logs/${id}/permanent-delete/`);
        uiStore.pushToast({ type: 'success', title: 'Success', message: 'Failure log permanently deleted.' });
        await this.fetchArchivedFailures(); // Refresh the list
      } catch (err) {
        const message = err.response?.data ? JSON.stringify(err.response.data) : 'Failed to delete failure log.';
        this.error = message;
        uiStore.pushToast({ type: 'error', title: 'Error', message });
        console.error(err);
      } finally {
        this.loading = false;
      }
    },
  },
});