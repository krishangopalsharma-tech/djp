// Path: frontend/src/stores/depots.js
import { defineStore } from 'pinia';
import { http } from '@/lib/http';
import { useUIStore } from './ui';

export const useDepotsStore = defineStore('depots', {
  state: () => ({
    depots: [],
    loading: false,
    error: null,
  }),
  actions: {
    async fetchDepots() {
      this.loading = true;
      this.error = null;
      try {
        const response = await http.get('/depots/'); // CORRECTED PATH
        this.depots = response.data.results || response.data;
      } catch (err) {
        this.error = 'Failed to fetch depots.';
        useUIStore().pushToast({ type: 'error', title: 'Error', message: this.error });
        console.error(err);
      } finally {
        this.loading = false;
      }
    },
    async addDepot(payload) {
      this.loading = true;
      const uiStore = useUIStore();
      try {
        await http.post('/depots/', payload); // CORRECTED PATH
        uiStore.pushToast({ type: 'success', title: 'Success', message: 'Depot added.' });
        await this.fetchDepots();
      } catch (err) {
        this.error = 'Failed to add depot.';
        uiStore.pushToast({ type: 'error', title: 'Error', message: this.error });
      } finally {
        this.loading = false;
      }
    },
    async updateDepot(id, payload) {
      this.loading = true;
      const uiStore = useUIStore();
      try {
        const updateData = {
          name: payload.name,
          code: payload.code,
          location: payload.location,
        };
        await http.patch(`/depots/${id}/`, updateData);
        uiStore.pushToast({ type: 'success', title: 'Success', message: 'Depot updated.' });
        await this.fetchDepots();
      } catch (err) {
        this.error = 'Failed to update depot.'; // Keep a generic error state

        // --- IMPROVED ERROR HANDLING ---
        let errorDetail = 'An unknown error occurred.';
        if (err.response && err.response.data) {
            // DRF validation errors are often objects where keys are field names
            if (typeof err.response.data === 'object') {
                errorDetail = Object.entries(err.response.data)
                    .map(([field, messages]) => `${field}: ${Array.isArray(messages) ? messages.join(', ') : messages}`)
                    .join('; ');
            } else {
                // Fallback for non-field errors or simple strings
                errorDetail = String(err.response.data.detail || err.response.data);
            }
        } else if (err.message) {
            errorDetail = err.message;
        }
        
        // Log the detailed error to the console
        console.error("Update Depot Error:", err.response?.data || err);

        // Show the detailed error in the toast
        uiStore.pushToast({ type: 'error', title: 'Update Failed', message: errorDetail });

      } finally {
        this.loading = false;
      }
    },
    async removeDepot(id) {
      this.loading = true;
      const uiStore = useUIStore();
      try {
        await http.delete(`/depots/${id}/`); // CORRECTED PATH
        uiStore.pushToast({ type: 'success', title: 'Success', message: 'Depot removed.' });
        await this.fetchDepots();
      } catch (err) {
        this.error = 'Failed to remove depot.';
        uiStore.pushToast({ type: 'error', title: 'Error', message: this.error });
      } finally {
        this.loading = false;
      }
    },
    async uploadDepotsFile(file) {
      this.loading = true;
      const uiStore = useUIStore();
      const formData = new FormData();
      formData.append('file', file);
      try {
        const response = await http.post('/depots/import_from_excel/', formData, { // CORRECTED PATH
          headers: { 'Content-Type': 'multipart/form-data' },
        });
        uiStore.pushToast({ type: 'success', title: 'Import Complete', message: response.data.message });
        await this.fetchDepots();
      } catch (err) {
        const message = err.response?.data?.error || 'File upload failed.';
        uiStore.pushToast({ type: 'error', title: 'Import Failed', message });
      } finally {
        this.loading = false;
      }
    },
    async downloadDepotsExcel() {
        this.loading = true;
        const uiStore = useUIStore();
        try {
            // --- FIX: CORRECTED URL PATH ---
            // Ensure it calls /depots/export_to_excel/ (relative to the base /api/v1/)
            const response = await http.get('/depots/export_to_excel/', {
                responseType: 'blob', // Keep this for file handling
            });

            // ... (rest of the download logic remains the same) ...
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', 'depot_equipment_export.xlsx');
            document.body.appendChild(link);
            link.click();
            link.remove();
            window.URL.revokeObjectURL(url);
            uiStore.pushToast({ type: 'success', title: 'Success', message: 'Depot data export started.' });
        } catch (err) {
            uiStore.pushToast({ type: 'error', title: 'Error', message: 'Failed to download depot data.' });
            console.error("Download Error:", err); // Log the error for debugging
        } finally {
            this.loading = false;
        }
    },
    async addEquipment(payload) {
      const uiStore = useUIStore();
      try {
        await http.post('/equipments/', payload); // CORRECTED PATH
        uiStore.pushToast({ type: 'success', title: 'Success', message: 'Equipment added.' });
      } catch (err) {
        uiStore.pushToast({ type: 'error', title: 'Error', message: 'Could not add equipment.' });
      }
    },
    async updateEquipment(id, payload) {
      const uiStore = useUIStore();
      try {
        await http.patch(`/equipments/${id}/`, payload); // CORRECTED PATH
        uiStore.pushToast({ type: 'success', title: 'Success', message: 'Equipment updated.' });
      } catch (err) {
        uiStore.pushToast({ type: 'error', title: 'Error', message: 'Could not update equipment.' });
      }
    },
    async removeEquipment(id) {
      const uiStore = useUIStore();
      try {
        await http.delete(`/equipments/${id}/`); // CORRECTED PATH
        uiStore.pushToast({ type: 'success', title: 'Success', message: 'Equipment removed.' });
      } catch (err) {
        uiStore.pushToast({ type: 'error', title: 'Error', message: 'Could not remove equipment.' });
      }
    },
  },
});