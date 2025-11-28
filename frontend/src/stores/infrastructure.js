// Path: frontend/src/stores/infrastructure.js
import { defineStore } from 'pinia';
import { http } from '@/lib/http';
import { useUIStore } from './ui';

export const useInfrastructureStore = defineStore('infrastructure', {
  state: () => ({
    tree: [], // For the assignment modal
    loading: {
      tree: false,
    },
    error: null,
  }),
  actions: {
    async fetchInfrastructureTree() {
      // Don't re-fetch if already loaded
      if (this.tree.length > 0) return; 
      
      this.loading.tree = true;
      this.error = null;
      try {
        // --- THIS IS THE FIX ---
        // The URL is at the root /api/v1/, not under /sections/
        const response = await http.get('/infrastructure-tree/');
        // --- END OF FIX ---
        
        this.tree = response.data;
      } catch (err) {
        this.error = 'Failed to fetch infrastructure tree.';
        useUIStore().pushToast({ type: 'error', title: 'Error', message: this.error });
        console.error('Fetch Infrastructure Tree Error:', err);
      } finally {
        this.loading.tree = false;
      }
    },
  },
});