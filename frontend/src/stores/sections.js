// Path: frontend/src/stores/sections.js
import { defineStore } from 'pinia';
import { http } from '@/lib/http';
import { useUIStore } from './ui';

export const useSectionsStore = defineStore('sections', {
  state: () => ({
    sections: [],
    sectionSubsections: [], // Store fetched subsections for the modal
    loading: false,
    error: null,
  }),
  actions: {
    // --- Section Actions ---
    async fetchSections() {
      this.loading = true; this.error = null;
      try {
        const response = await http.get('/sections/'); // Uses the sections router base path
        this.sections = response.data.results || response.data;
      } catch (err) {
        this.error = 'Failed to fetch sections.';
        useUIStore().pushToast({ type: 'error', title: 'Error', message: this.error });
      } finally { this.loading = false; }
    },
    async addSection(payload) {
      this.loading = true; const uiStore = useUIStore();
      try {
        await http.post('/sections/', payload);
        uiStore.pushToast({ type: 'success', title: 'Success', message: 'Section added.' });
        await this.fetchSections();
      } catch (err) {
        this.error = 'Failed to add section.';
        const errorDetail = err.response?.data ? JSON.stringify(err.response.data) : this.error;
        uiStore.pushToast({ type: 'error', title: 'Error', message: errorDetail });
      } finally { this.loading = false; }
    },
    async updateSection(id, payload) {
      this.loading = true; const uiStore = useUIStore();
      try {
        await http.patch(`/sections/${id}/`, payload);
        uiStore.pushToast({ type: 'success', title: 'Success', message: 'Section updated.' });
        await this.fetchSections();
      } catch (err) {
        this.error = 'Failed to update section.';
        const errorDetail = err.response?.data ? JSON.stringify(err.response.data) : this.error;
        uiStore.pushToast({ type: 'error', title: 'Error', message: errorDetail });
      } finally { this.loading = false; }
    },
    async removeSection(id) {
      this.loading = true; const uiStore = useUIStore();
      try {
        await http.delete(`/sections/${id}/`);
        uiStore.pushToast({ type: 'success', title: 'Success', message: 'Section removed.' });
        await this.fetchSections();
      } catch (err) {
        this.error = 'Failed to remove section.';
        uiStore.pushToast({ type: 'error', title: 'Error', message: this.error });
      } finally { this.loading = false; }
    },
    async uploadSectionsFile(file) {
      this.loading = true; const uiStore = useUIStore();
      const formData = new FormData();
      formData.append('file', file);
      try {
        const response = await http.post('/sections/import_master_file/', formData, { // Use correct action path
           headers: { 'Content-Type': 'multipart/form-data' },
        });
        
        // --- START OF FIX: Show detailed errors ---
        const data = response.data;
        if (data.errors && data.errors.length > 0) {
            uiStore.pushToast({ 
                type: 'warning', 
                title: 'Import Finished with Errors', 
                message: `${data.message} First error: ${data.errors[0]}`,
                duration: 10000 // Show for 10 seconds
            });
        } else {
            uiStore.pushToast({ type: 'success', title: 'Import Complete', message: data.message });
        }
        // --- END OF FIX ---
        
        await this.fetchSections(); // Refresh after import
      } catch (err) {
        // Handle 400/500 level errors
        const message = err.response?.data?.error || err.response?.data?.message || 'File upload failed.';
        this.error = message;
        uiStore.pushToast({ type: 'error', title: 'Import Failed', message });
      } finally { this.loading = false; }
    },

    // --- SubSection Actions ---
    async fetchSubsectionsForSection(sectionId) {
        this.loading = true; this.error = null;
        try {
            // Use the dedicated subsections endpoint with filtering
            const response = await http.get(`/subsections/?section=${sectionId}`);
            this.sectionSubsections = response.data.results || response.data;
        } catch (err) {
            this.error = 'Failed to fetch sub-sections.';
            useUIStore().pushToast({ type: 'error', title: 'Error', message: this.error });
            this.sectionSubsections = []; // Clear on error
        } finally { this.loading = false; }
    },
    async addSubSection(payload) {
      const uiStore = useUIStore();
      try {
        const response = await http.post('/subsections/', payload);
        uiStore.pushToast({ type: 'success', title: 'Success', message: 'Sub-section added.' });
        return response.data; // Return the created object with its ID
      } catch (err) {
        const errorDetail = err.response?.data ? JSON.stringify(err.response.data) : 'Could not add sub-section.';
        uiStore.pushToast({ type: 'error', title: 'Error', message: errorDetail });
        return null;
      }
    },
    async updateSubSection(id, payload) {
      const uiStore = useUIStore();
      try {
        await http.patch(`/subsections/${id}/`, payload);
        // uiStore.pushToast({ type: 'success', title: 'Success', message: 'Sub-section updated.' });
      } catch (err) {
        const errorDetail = err.response?.data ? JSON.stringify(err.response.data) : 'Could not update sub-section.';
        uiStore.pushToast({ type: 'error', title: 'Error', message: errorDetail });
      }
    },
    async removeSubSection(id) {
      const uiStore = useUIStore();
      try {
        await http.delete(`/subsections/${id}/`);
        uiStore.pushToast({ type: 'success', title: 'Success', message: 'Sub-section removed.' });
      } catch (err) {
        uiStore.pushToast({ type: 'error', title: 'Error', message: 'Could not remove sub-section.' });
      }
    },

    // --- Asset Actions ---
    async addAsset(payload) {
      const uiStore = useUIStore();
      try {
        await http.post('/assets/', payload);
      } catch (err) {
        const errorDetail = err.response?.data ? JSON.stringify(err.response.data) : 'Could not add asset.';
        uiStore.pushToast({ type: 'error', title: 'Error', message: errorDetail });
      }
    },
    async updateAsset(id, payload) {
      const uiStore = useUIStore();
      try {
        await http.patch(`/assets/${id}/`, payload);
      } catch (err) {
        const errorDetail = err.response?.data ? JSON.stringify(err.response.data) : 'Could not update asset.';
        uiStore.pushToast({ type: 'error', title: 'Error', message: errorDetail });
      }
    },
    async removeAsset(id) {
      const uiStore = useUIStore();
      try {
        await http.delete(`/assets/${id}/`);
      } catch (err) {
        uiStore.pushToast({ type: 'error', title: 'Error', message: 'Could not remove asset.' });
      }
    },
  },
});
