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
      this.loading = true;
          const uiStore = useUIStore();
          try {
        await http.post('/reports/', payload);
            uiStore.pushToast({ type: 'success', title: 'Success', message: 'Report schedule added.' });
            await this.fetchSchedules();
          } catch (err) {
            console.error('Failed to add schedule:', err);
        const errorDetail = err.response?.data ? JSON.stringify(err.response.data) : 'Could not add schedule.';
        uiStore.pushToast({ type: 'error', title: 'Error', message: errorDetail });
      } finally {
          this.loading = false;
          }
        },
        async updateSchedule(scheduleId, payload) {
      this.loading = true;
          const uiStore = useUIStore();
      
      // The frontend uses 'telegram_group_keys', but the serializer expects 'telegram_groups'
      const apiPayload = {
        ...payload,
        telegram_groups: payload.telegram_group_keys || [], // Rename key
      };
      // Clean up fields not in the backend model
      delete apiPayload.id;
      delete apiPayload.template_name;
      delete apiPayload.telegram_group_keys;

          try {
        await http.patch(`/reports/${scheduleId}/`, apiPayload);
            uiStore.pushToast({ type: 'success', title: 'Saved', message: 'Report schedule updated.' });
        await this.fetchSchedules(); // Refresh list
          } catch (err) {
            console.error('Failed to update schedule:', err);
        const errorDetail = err.response?.data ? JSON.stringify(err.response.data) : 'Could not update schedule.';
        uiStore.pushToast({ type: 'error', title: 'Error', message: errorDetail });
      } finally {
          this.loading = false;
          }
        },
        async removeSchedule(scheduleId) {
      this.loading = true;
          const uiStore = useUIStore();
          try {
        await http.delete(`/reports/${scheduleId}/`);
            uiStore.pushToast({ type: 'success', title: 'Deleted', message: 'Report schedule removed.' });
            await this.fetchSchedules();
          } catch (err) {
            console.error('Failed to remove schedule:', err);
            uiStore.pushToast({ type: 'error', title: 'Error', message: 'Could not remove schedule.' });
      } finally {
          this.loading = false;
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
        await this.fetchSchedules(); // Refresh to show new template name
          } catch (err) {
            console.error('Failed to upload template:', err);
            uiStore.pushToast({ type: 'error', title: 'Upload Failed', message: 'Could not upload template.' });
          } finally {
            this.loading = false;
          }
        },
      },
    });
    
