import { defineStore } from 'pinia';
import { http } from '@/lib/http';
import { useUIStore } from './ui';

export const useTelegramStore = defineStore('telegram', {
  state: () => ({
    groups: [],
    loading: false,
    error: null,
  }),
  getters: {
    list: (state) => state.groups,
  },
  actions: {
    async fetchTelegramGroups() {
      this.loading = true;
      this.error = null;
      const uiStore = useUIStore();
      try {
        const response = await http.get('/notifications/telegram-groups/');
        this.groups = response.data;
      } catch (err) {
        this.error = 'Failed to fetch Telegram groups.';
        uiStore.pushToast({ type: 'error', title: 'Error', message: this.error });
        console.error(err);
      } finally {
        this.loading = false;
      }
    },

    async updateTelegramGroup(groupData) {
      this.loading = true;
      this.error = null;
      const uiStore = useUIStore();
      try {
        await http.patch(`/notifications/telegram-groups/${groupData.id}/`, groupData);
        uiStore.pushToast({ type: 'success', title: 'Saved', message: `Settings for ${groupData.name} saved.` });
        // No need to re-fetch, just update local state if needed or let user see the change
      } catch (err) {
        this.error = 'Failed to save Telegram group settings.';
        uiStore.pushToast({ type: 'error', title: 'Error', message: this.error });
        console.error(err);
      } finally {
        this.loading = false;
      }
    },

    async sendTestMessage(group) {
      const uiStore = useUIStore();
      uiStore.pushToast({ type: 'info', title: 'Sending...', message: `Sending test message to ${group.name}.` });
      try {
        const response = await http.post('/notifications/telegram-groups/test/', { group_id: group.id });
        uiStore.pushToast({ type: 'success', title: 'Success', message: response.data.message });
      } catch (err) {
        const message = err.response?.data?.error || 'Failed to send test message.';
        uiStore.pushToast({ type: 'error', title: 'Error', message });
        console.error(err);
      }
    },
  },
});

