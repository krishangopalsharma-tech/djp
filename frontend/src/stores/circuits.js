// Path: frontend/src/stores/circuits.js
import { defineStore } from 'pinia';
import { http } from '@/lib/http';
import { useUIStore } from './ui';

export const useCircuitsStore = defineStore('circuits', {
  state: () => ({
    circuits: [],
    loading: false,
    error: null,
  }),
  actions: {
    async fetchCircuits() {
      this.loading = true; this.error = null;
      try {
        const response = await http.get('/circuits/');
        this.circuits = response.data.results || response.data;
      } catch (err) {
        this.error = 'Failed to fetch circuits.';
        useUIStore().pushToast({ type: 'error', title: 'Error', message: this.error });
      } finally { this.loading = false; }
    },
    async addCircuit(payload) {
      this.loading = true; const uiStore = useUIStore();
      try {
        await http.post('/circuits/', payload);
        uiStore.pushToast({ type: 'success', title: 'Success', message: 'Circuit added.' });
        await this.fetchCircuits();
      } catch (err) {
        const errorDetail = err.response?.data ? JSON.stringify(err.response.data) : 'Failed to add circuit.';
        uiStore.pushToast({ type: 'error', title: 'Error', message: errorDetail });
      } finally { this.loading = false; }
    },
    async updateCircuit(id, payload) {
      this.loading = true; const uiStore = useUIStore();
      try {
        await http.patch(`/circuits/${id}/`, payload);
        uiStore.pushToast({ type: 'success', title: 'Success', message: 'Circuit updated.' });
        await this.fetchCircuits();
      } catch (err) {
        const errorDetail = err.response?.data ? JSON.stringify(err.response.data) : 'Failed to update circuit.';
        uiStore.pushToast({ type: 'error', title: 'Error', message: errorDetail });
      } finally { this.loading = false; }
    },
    async removeCircuit(id) {
      this.loading = true; const uiStore = useUIStore();
      try {
        await http.delete(`/circuits/${id}/`);
        uiStore.pushToast({ type: 'success', title: 'Success', message: 'Circuit removed.' });
        await this.fetchCircuits();
      } catch (err) {
        this.error = 'Failed to remove circuit.';
        uiStore.pushToast({ type: 'error', title: 'Error', message: this.error });
      } finally { this.loading = false; }
    },
    async uploadCircuitsFile(file) {
      this.loading = true; const uiStore = useUIStore(); const formData = new FormData(); formData.append('file', file);
      try {
        const response = await http.post('/circuits/import_from_excel/', formData, { headers: { 'Content-Type': 'multipart/form-data' } });
        uiStore.pushToast({ type: 'success', title: 'Import Complete', message: response.data.message });
        await this.fetchCircuits();
      } catch (err) {
        const message = err.response?.data?.error || err.response?.data?.message || 'File upload failed.';
        const errors = err.response?.data?.errors;
        if (errors && Array.isArray(errors)) { uiStore.pushToast({ type: 'warning', title: 'Import Issues', message: `${message} First errors: ${errors.slice(0, 3).join(', ')}`, duration: 10000 }); }
        else { uiStore.pushToast({ type: 'error', title: 'Import Failed', message }); }
      } finally { this.loading = false; }
    },
    async exportCircuitsToExcel() {
      this.loading = true; const uiStore = useUIStore();
      try {
        const response = await http.get('/circuits/export_to_excel/', { responseType: 'blob' });
        const url = window.URL.createObjectURL(new Blob([response.data])); const link = document.createElement('a'); link.href = url;
        link.setAttribute('download', 'circuits_export.xlsx'); document.body.appendChild(link); link.click(); link.remove(); window.URL.revokeObjectURL(url);
        uiStore.pushToast({ type: 'success', title: 'Success', message: 'Circuit data export started.' });
      } catch (err) {
        this.error = 'Failed to export circuit data.'; uiStore.pushToast({ type: 'error', title: 'Export Error', message: this.error });
      } finally { this.loading = false; }
    },
  },
});