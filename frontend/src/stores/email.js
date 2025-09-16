import { defineStore } from 'pinia';
import { http } from '@/lib/http';
import { useUIStore } from './ui';

export const useEmailStore = defineStore('email', {
  state: () => ({
    settings: {
      host: '',
      port: 587,
      encryption: 'STARTTLS',
      username: '',
      password: '',
      from_name: 'RFMS Notifications',
      from_address: 'no-reply@rfms.local',
      recipients: {
        to: [],
        cc: [],
        bcc: [],
      },
    },
    loading: false,
    error: null,
  }),
  actions: {
    async fetchSettings() {
      this.loading = true;
      this.error = null;
      const uiStore = useUIStore();
      try {
        const response = await http.get('/notifications/settings/email/');
        const recipients = response.data.recipients || {};
        // Ensure recipients object and its arrays exist
        this.settings = {
          ...response.data,
          recipients: {
            to: recipients.to || [],
            cc: recipients.cc || [],
            bcc: recipients.bcc || [],
          }
        };
      } catch (err) {
        this.error = 'Failed to fetch email settings.';
        uiStore.pushToast({ type: 'error', title: 'Error', message: this.error });
        console.error(err);
      } finally {
        this.loading = false;
      }
    },
    async saveSettings() {
      this.loading = true;
      this.error = null;
      const uiStore = useUIStore();
      try {
        // Create a payload to send, omitting the password if it's blank
        const payload = { ...this.settings };
        if (payload.password === '') {
          delete payload.password;
        }
        
        const response = await http.put('/notifications/settings/email/', payload);
        const recipients = response.data.recipients || {};
        this.settings = {
          ...response.data,
          recipients: {
            to: recipients.to || [],
            cc: recipients.cc || [],
            bcc: recipients.bcc || [],
          }
        };
        uiStore.pushToast({ type: 'success', title: 'Success', message: 'Email settings saved.' });
      } catch (err) {
        this.error = 'Failed to save email settings.';
        uiStore.pushToast({ type: 'error', title: 'Error', message: this.error });
        console.error(err);
      } finally {
        this.loading = false;
      }
    },
    async sendTestEmail(toEmail) {
      if (!toEmail) {
        useUIStore().pushToast({ type: 'error', title: 'Input Required', message: 'Please enter a recipient for the test email.' });
        return;
      }
      this.loading = true;
      const uiStore = useUIStore();
      try {
        const response = await http.post('/notifications/settings/email/test/', { to_email: toEmail });
        uiStore.pushToast({ type: 'success', title: 'Success', message: response.data.message });
      } catch (err) {
        const message = err.response?.data?.error || 'An unknown error occurred.';
        uiStore.pushToast({ type: 'error', title: 'Test Failed', message: message, duration: 8000 });
        console.error(err);
      } finally {
        this.loading = false;
      }
    }
  },
});

