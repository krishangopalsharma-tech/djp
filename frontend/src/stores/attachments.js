import { defineStore } from 'pinia';
import { http } from '@/lib/http';
import { useUIStore } from './ui';

export const useAttachmentStore = defineStore('attachments', {
  state: () => ({
    attachments: [],
    loading: false,
    error: null,
  }),
  actions: {
    async fetchAttachments(failureId) {
      if (!failureId) {
        this.attachments = [];
        return;
      }
      this.loading = true;
      this.error = null;
      try {
        const response = await http.get(`/failures/attachments/?failure=${failureId}`);
        this.attachments = response.data.results || response.data;
      } catch (err) {
        this.error = 'Failed to fetch attachments.';
        console.error(err);
      } finally {
        this.loading = false;
      }
    },

    async uploadAttachment(failureId, file, description) {
  const uiStore = useUIStore();
  const formData = new FormData();
  formData.append('failure', failureId);
  formData.append('file', file);
  formData.append('description', description);

  this.loading = true;
  try {
    const response = await http.post('/failures/attachments/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    uiStore.pushToast({ type: 'success', title: 'Success', message: 'File uploaded.' });
    await this.fetchAttachments(failureId);
    return response.data;
  } catch (err) {
    uiStore.pushToast({ type: 'error', title: 'Upload Failed', message: 'Could not upload file.' });
    console.error(err);
    return null;
  } finally {
    this.loading = false;
  }
},

    async deleteAttachment(attachmentId, failureId) {
      const uiStore = useUIStore();
      this.loading = true;
      try {
        await http.delete(`/failures/attachments/${attachmentId}/`);
        uiStore.pushToast({ type: 'success', title: 'Deleted', message: 'Attachment removed.' });
        await this.fetchAttachments(failureId); // Refresh the list
      } catch (err) {
        uiStore.pushToast({ type: 'error', title: 'Error', message: 'Could not remove attachment.' });
        console.error(err);
      } finally {
        this.loading = false;
      }
    },
  },
});