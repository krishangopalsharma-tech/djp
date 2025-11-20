    import { defineStore } from 'pinia';
    import { http } from '@/lib/http';
    import { useUIStore } from './ui';

    export const useReportsStore = defineStore('reports', {
      state: () => ({
        schedules: [],
        loading: false,
        error: null,
      }),
      actions: {
        async fetchSchedules() {
          this.loading = true;
          this.error = null;
          try {
            const response = await http.get('/reports/');
            this.schedules = response.data.results || response.data;
          } catch (err) {
            this.error = 'Failed to fetch report schedules.';
            console.error(err);
          } finally {
            this.loading = false;
          }
        },
        async addSchedule(payload) {
          const uiStore = useUIStore();
          try {
            await http.post('/reports/', payload);
            uiStore.pushToast({ type: 'success', title: 'Success', message: 'Report schedule added.' });
            await this.fetchSchedules();
          } catch (err) {
            console.error('Failed to add schedule:', err);
            uiStore.pushToast({ type: 'error', title: 'Error', message: 'Could not add report schedule.' });
          }
        },
        async updateSchedule(scheduleId, payload) {
          const uiStore = useUIStore();
          // The backend now expects 'telegram_group_keys'
          const apiPayload = { ...payload };
          delete apiPayload.id; // Don't send the ID in the body of a PATCH request

          try {
            await http.patch(`/reports/${scheduleId}/`, apiPayload);
            uiStore.pushToast({ type: 'success', title: 'Saved', message: 'Report schedule updated.' });
            await this.fetchSchedules(); // Refresh list to get latest state
          } catch (err) {
            console.error('Failed to update schedule:', err);
            uiStore.pushToast({ type: 'error', title: 'Error', message: 'Could not update schedule.' });
          }
        },
        async removeSchedule(scheduleId) {
          const uiStore = useUIStore();
          try {
            await http.delete(`/reports/${scheduleId}/`);
            uiStore.pushToast({ type: 'success', title: 'Deleted', message: 'Report schedule removed.' });
            await this.fetchSchedules();
          } catch (err) {
            console.error('Failed to remove schedule:', err);
            uiStore.pushToast({ type: 'error', title: 'Error', message: 'Could not remove schedule.' });
          }
        },
        async uploadTemplate(scheduleId, file) {
          const uiStore = useUIStore();
          const formData = new FormData();
          formData.append('template', file);
          this.loading = true;
          try {
            await http.post(`/reports/${scheduleId}/upload_template/`, formData, {
              headers: { 'Content-Type': 'multipart/form-data' },
            });
            uiStore.pushToast({ type: 'success', title: 'Success', message: 'Template uploaded.' });
            await this.fetchSchedules();
          } catch (err) {
            console.error('Failed to upload template:', err);
            uiStore.pushToast({ type: 'error', title: 'Upload Failed', message: 'Could not upload template.' });
          } finally {
            this.loading = false;
          }
        },
      },
    });
    
