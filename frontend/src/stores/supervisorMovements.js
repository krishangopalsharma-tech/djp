// Path: frontend/src/stores/supervisorMovements.js
import { defineStore } from 'pinia';
import { http } from '@/lib/http';
import { useUIStore } from './ui';

export const useSupervisorMovementsStore = defineStore('supervisorMovements', {
  state: () => ({
    // This will now store the list of supervisors with their nested movement data
    dailyMovements: [],
    loading: false,
    error: null,
  }),
  actions: {
    /**
     * Fetches all supervisors and their movements for a specific date.
     * @param {string} date - The date in 'YYYY-MM-DD' format.
     */
    async fetchMovementsByDate(date) {
      if (!date) return;
      this.loading = true;
      this.error = null;
      try {
        const response = await http.get(`/operations/by-date/?date=${date}`);
        this.dailyMovements = response.data;
      } catch (err) {
        this.error = 'Failed to fetch movements for the selected date.';
        this.dailyMovements = [];
        console.error(err);
      } finally {
        this.loading = false;
      }
    },

    /**
     * Creates or updates a movement record.
     * @param {object} payload - The full movement object.
     */
    async saveMovement(payload) {
      const uiStore = useUIStore();
      this.loading = true;
      this.error = null;
      try {
        if (payload.id) {
          // If it has an ID, it's an update (PATCH)
          await http.patch(`/operations/movements/${payload.id}/`, payload);
          uiStore.pushToast({ type: 'success', title: 'Success', message: 'Movement updated.' });
        } else {
          // Otherwise, it's a new record (POST)
          await http.post('/operations/movements/', payload);
          uiStore.pushToast({ type: 'success', title: 'Success', message: 'Movement saved.' });
        }
        // Refresh the data for the current date to show the change
        await this.fetchMovementsByDate(payload.date);
      } catch (err) {
        this.error = 'Failed to save movement.';
        uiStore.pushToast({ type: 'error', title: 'Error', message: this.error });
        console.error(err);
      } finally {
        this.loading = false;
      }
    },
     /**
     * Deletes a movement record.
     * @param {number} movementId - The ID of the movement record to delete.
     * @param {string} date - The date for which to refresh data after deletion.
     */
    async deleteMovement(movementId, date) {
        if (!movementId) return;
        const uiStore = useUIStore();
        this.loading = true;
        this.error = null;
        try {
            await http.delete(`/operations/movements/${movementId}/`);
            uiStore.pushToast({ type: 'success', title: 'Success', message: 'Movement entry deleted.' });
            await this.fetchMovementsByDate(date);
        } catch (err) {
            this.error = 'Failed to delete movement.';
            uiStore.pushToast({ type: 'error', title: 'Error', message: this.error });
            console.error(err);
        } finally {
            this.loading = false;
        }
    },

    async sendMovementReport(date) {
      const uiStore = useUIStore();
      this.loading = true;
      this.error = null;
      try {
        await http.post('/operations/send-report/', { date });
        uiStore.pushToast({ type: 'success', title: 'Success', message: 'Report sent successfully.' });
      } catch (err) {
        const message = err.response?.data?.error || 'Failed to send report.';
        this.error = message;
        uiStore.pushToast({ type: 'error', title: 'Error', message });
        console.error(err);
      } finally {
        this.loading = false;
      }
    }
  },
});