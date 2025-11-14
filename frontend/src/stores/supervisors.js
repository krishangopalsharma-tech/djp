// Path: frontend/src/stores/supervisors.js
import { defineStore } from 'pinia';
import { http } from '@/lib/http';
import { useUIStore } from './ui';

export const useSupervisorsStore = defineStore('supervisors', {
  state: () => ({
    supervisors: [],
    loading: false,
    error: null,
  }),
  actions: {
    async fetchSupervisors() {
      this.loading = true; this.error = null;
      try {
        const response = await http.get('/supervisors/');
        this.supervisors = response.data.results || response.data;
      } catch (err) {
        this.error = 'Failed to fetch supervisors.';
        useUIStore().pushToast({ type: 'error', title: 'Error', message: this.error });
      } finally { this.loading = false; }
    },
    async addSupervisor(payload) {
      this.loading = true; const uiStore = useUIStore();
      try {
        await http.post('/supervisors/', payload);
        uiStore.pushToast({ type: 'success', title: 'Success', message: 'Supervisor added.' });
        await this.fetchSupervisors();
      } catch (err) {
        const errorDetail = err.response?.data ? JSON.stringify(err.response.data) : 'Failed to add supervisor.';
        uiStore.pushToast({ type: 'error', title: 'Error', message: errorDetail });
      } finally { this.loading = false; }
    },
    async updateSupervisor(id, payload) {
      this.loading = true; const uiStore = useUIStore();
      try {
        // The backend serializer now accepts M2M IDs
        await http.patch(`/supervisors/${id}/`, payload);
        uiStore.pushToast({ type: 'success', title: 'Success', message: 'Supervisor updated.' });
        await this.fetchSupervisors();
      } catch (err) {
        const errorDetail = err.response?.data ? JSON.stringify(err.response.data) : 'Failed to update supervisor.';
        uiStore.pushToast({ type: 'error', title: 'Error', message: errorDetail });
      } finally { this.loading = false; }
    },
    async removeSupervisor(id) {
      this.loading = true; const uiStore = useUIStore();
      try {
        await http.delete(`/supervisors/${id}/`);
        uiStore.pushToast({ type: 'success', title: 'Success', message: 'Supervisor removed.' });
        await this.fetchSupervisors();
      } catch (err) {
        this.error = 'Failed to remove supervisor.';
        uiStore.pushToast({ type: 'error', title: 'Error', message: this.error });
      } finally { this.loading = false; }
    },
    async uploadSupervisorsFile(file) {
      this.loading = true; const uiStore = useUIStore(); const formData = new FormData(); formData.append('file', file);
      try {
        const response = await http.post('/supervisors/import_from_excel/', formData, { headers: { 'Content-Type': 'multipart/form-data' } });
        uiStore.pushToast({ type: 'success', title: 'Import Complete', message: response.data.message });
        await this.fetchSupervisors();
      } catch (err) {
        const message = err.response?.data?.error || err.response?.data?.message || 'File upload failed.';
        const errors = err.response?.data?.errors;
        if (errors && Array.isArray(errors)) { uiStore.pushToast({ type: 'warning', title: 'Import Issues', message: `${message} First errors: ${errors.slice(0, 3).join(', ')}`, duration: 10000 }); }
        else { uiStore.pushToast({ type: 'error', title: 'Import Failed', message }); }
      } finally { this.loading = false; }
    },
    async exportSupervisorsToExcel() {
      this.loading = true; const uiStore = useUIStore();
      try {
        const response = await http.get('/supervisors/export_to_excel/', { responseType: 'blob' });
        const url = window.URL.createObjectURL(new Blob([response.data])); const link = document.createElement('a'); link.href = url;
        link.setAttribute('download', 'supervisors_export.xlsx'); document.body.appendChild(link); link.click(); link.remove(); window.URL.revokeObjectURL(url);
        uiStore.pushToast({ type: 'success', title: 'Success', message: 'Supervisor data export started.' });
      } catch (err) {
        this.error = 'Failed to export supervisor data.'; uiStore.pushToast({ type: 'error', title: 'Export Error', message: this.error });
      } finally { this.loading = false; }
    },
  },
});