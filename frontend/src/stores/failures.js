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
    // The toast is now handled in the component
    // uiStore.pushToast({ type: 'success', title: 'Success', message: 'Failure log created.' });
    this.fetchFailures();
    return response.data; // Return the created object
  } catch (err) {
    const message = err.response?.data ? JSON.stringify(err.response.data) : 'Failed to create failure log.';
    this.error = message;
    uiStore.pushToast({ type: 'error', title: 'Error', message });
    console.error(err);
    return null; // Return null on failure
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
    // The toast is now handled in the component
    // uiStore.pushToast({ type: 'success', title: 'Success', message: 'Failure log updated.' });
    await this.fetchFailures();
    return response.data; // Return the updated object
  } catch (err) {
    const message = err.response?.data ? JSON.stringify(err.response.data) : 'Failed to update failure log.';
    this.error = message;
    uiStore.pushToast({ type: 'error', title: 'Error', message });
    console.error(err);
    return null; // Return null on failure
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
        uiStore.pushToast({ type: 'success', title: 'Success', message: response.data.message });
        this.fetchFailures();
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
      try {
        const response = await http.get('/failures/archived/');
        this.archivedFailures = response.data.results || response.data;
      } catch (err) {
        this.error = 'Failed to fetch archived failures.';
        console.error(err);
        useUIStore().pushToast({ type: 'error', title: 'Error', message: this.error });
      } finally {
        this.loading = false;
      }
    },

    async permanentlyDeleteFailure(id) {
      const uiStore = useUIStore();
      this.loading = true;
      this.error = null;
      try {
        await http.delete(`/failures/archived/${id}/`);
        uiStore.pushToast({ type: 'success', title: 'Deleted', message: `Failure log #${id} has been permanently deleted.` });
        await this.fetchArchivedFailures();
      } catch (err) {
        const message = err.response?.data ? JSON.stringify(err.response.data) : 'Failed to permanently delete failure.';
        this.error = message;
        uiStore.pushToast({ type: 'error', title: 'Error', message });
        console.error(err);
      } finally {
        this.loading = false;
      }
    },

    async sendAttachmentToTelegram(attachmentId, groupKeys) {
      const uiStore = useUIStore();
      this.loading = true;
      this.error = null;
      try {
        const response = await http.post(`/failures/attachments/${attachmentId}/send_to_telegram/`, { group_keys: groupKeys });
        uiStore.pushToast({ type: 'success', title: 'Success', message: response.data.message });
      } catch (err) {
        const message = err.response?.data?.error || 'Failed to send attachment.';
        this.error = message;
        uiStore.pushToast({ type: 'error', title: 'Error', message });
        console.error(err);
      } finally {
        this.loading = false;
      }
    },
  },
});
