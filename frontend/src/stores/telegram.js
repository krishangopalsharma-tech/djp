import { defineStore } from 'pinia';
import { http } from '@/lib/http';
import { useUIStore } from './ui';

export const useTelegramStore = defineStore('telegram', {
  state: () => ({
    settings: {
      bot_token: '',
    },
    groups: [],
    loading: false,
    error: null,
  }),

  getters: {
    // A getter to easily access the list of groups
    list: (state) => state.groups,
  },

  actions: {
    async fetchTelegramSettings() {
      this.loading = true;
      try {
        const response = await http.get('/notifications/settings/telegram/');
        // ADD THIS CHECK to ensure we don't overwrite with a null/undefined value
        if (response.data && typeof response.data === 'object') {
          this.settings = response.data;
        } else {
          console.warn('Received invalid data for Telegram settings, preserving initial state.');
        }
      } catch (err) {
        console.error('Failed to fetch Telegram settings', err);
        useUIStore().pushToast({ type: 'error', title: 'Error', message: 'Could not load Telegram settings.' });
      } finally {
        this.loading = false;
      }
    },

    // ... (rest of the actions remain unchanged)
    async saveTelegramSettings() {
      this.loading = true;
      const uiStore = useUIStore();
      try {
        const response = await http.patch('/notifications/settings/telegram/1/', this.settings);
        this.settings = response.data;
        uiStore.pushToast({ type: 'success', title: 'Success', message: 'Bot Token saved.' });
      } catch (err) {
        uiStore.pushToast({ type: 'error', title: 'Error', message: 'Could not save Bot Token.' });
        console.error(err);
      } finally {
        this.loading = false;
      }
    },

    async fetchTelegramGroups() {
      this.loading = true;
      try {
        const response = await http.get('/telegram/telegram-groups/');
        this.groups = response.data.results || response.data;
      } catch (err) {
        console.error('Failed to fetch Telegram groups', err);
        useUIStore().pushToast({ type: 'error', title: 'Error', message: 'Could not load Telegram groups.' });
      } finally {
        this.loading = false;
      }
    },

    async updateTelegramGroup(group) {
      this.loading = true;
      const uiStore = useUIStore();
      try {
        await http.patch(`/notifications/telegram-groups/${group.id}/`, group);
        uiStore.pushToast({ type: 'success', title: 'Success', message: `Group "${group.name}" updated.` });
        await this.fetchTelegramGroups();
      } catch (err) {
        uiStore.pushToast({ type: 'error', title: 'Error', message: 'Could not update group.' });
        console.error(err);
      } finally {
        this.loading = false;
      }
    },

    async sendTestMessage(group) {
      this.loading = true;
      const uiStore = useUIStore();
      try {
        const response = await http.post('/telegram/groups/test/', { group_id: group.id });
        uiStore.pushToast({ type: 'success', title: 'Success', message: response.data.message });
      } catch (err) {
        const message = err.response?.data?.error || 'Failed to send test message.';
        uiStore.pushToast({ type: 'error', title: 'Test Failed', message });
        console.error(err);
      } finally {
        this.loading = false;
      }
    },
  },
});