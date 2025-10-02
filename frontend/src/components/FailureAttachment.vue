<script setup>
import { ref, watch, computed } from 'vue';
import { useAttachmentStore } from '@/stores/attachments';
import { http } from '@/lib/http';
import { useUIStore } from '@/stores/ui';
import { Trash2 } from 'lucide-vue-next';

const props = defineProps({
  failureId: {
    type: [Number, String],
    required: true,
  },
});

const attachmentStore = useAttachmentStore();
const uiStore = useUIStore();
const attachments = computed(() => attachmentStore.attachments);

const fileInput = ref(null);
const selectedFile = ref(null);
const description = ref('');
const isLoading = ref(false);
const selectedGroupKeys = ref(['files']); // Default 'files' group is selected

watch(() => props.failureId, (newId) => {
  if (newId) {
    attachmentStore.fetchAttachments(newId);
  }
}, { immediate: true });

function handleFileSelect(event) {
  selectedFile.value = event.target.files[0] || null;
}

async function handleUpload() {
  if (!selectedFile.value || !props.failureId) {
    uiStore.pushToast({ type: 'error', title: 'Missing File', message: 'Please select a file to upload.' });
    return;
  }

  const formData = new FormData();
  formData.append('failure_id', props.failureId);
  formData.append('file', selectedFile.value);
  formData.append('group_keys', JSON.stringify(selectedGroupKeys.value));

  isLoading.value = true;
  try {
    // Use the new, direct-send endpoint
    await http.post('/failures/send-attachment-to-telegram/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });

    uiStore.pushToast({ type: 'success', title: 'Success', message: 'File sent to Telegram.' });

    // Reset the form
    selectedFile.value = null;
    if (fileInput.value) {
      fileInput.value.value = '';
    }

  } catch (err) {
    const message = err.response?.data?.error || 'Could not send file to Telegram.';
    uiStore.pushToast({ type: 'error', title: 'Upload Failed', message });
    console.error(err);
  } finally {
    isLoading.value = false;
  }
}

async function handleDelete(attachmentId) {
  if (confirm('Are you sure you want to delete this attachment?')) {
    await attachmentStore.deleteAttachment(attachmentId, props.failureId);
  }
}

function getFileUrl(fileUrl) {
    if (fileUrl && !fileUrl.startsWith('http')) {
        // Assumes Vite dev server proxy is at /api
        const rootUrl = '/'; // Go to the root of the Django server
        return `${rootUrl}${fileUrl.startsWith('/') ? fileUrl.substring(1) : fileUrl}`;
    }
    return fileUrl;
}
</script>

<template>
  <div class="sm:col-span-2 space-y-4">
    <hr class="border-app/30 my-2" />
    <div>
      <h3 class="text-sm font-medium text-app mb-2">Attachments</h3>

      <div class="p-3 border border-dashed border-app/50 rounded-lg space-y-3">
        <div class="flex items-center justify-between gap-4">
            <div>
              <label class="block text-sm font-medium mb-1">Upload New File</label>
              <input type="file" ref="fileInput" @change="handleFileSelect" class="text-sm" />
            </div>
            <div class="self-end">
              <button @click="handleUpload" :disabled="!selectedFile || isLoading || selectedGroupKeys.length === 0" class="btn btn-secondary">
                {{ isLoading ? 'Uploading...' : 'Upload to Telegram' }}
              </button>
            </div>
        </div>

        <div class="flex items-center gap-4 pt-2">
            <span class="text-sm font-medium">Send to:</span>
            <label class="flex items-center gap-2">
                <input type="checkbox" value="alert" v-model="selectedGroupKeys" class="h-4 w-4 rounded" />
                <span>Alerts Group</span>
            </label>
            <label class="flex items-center gap-2">
                <input type="checkbox" value="files" v-model="selectedGroupKeys" class="h-4 w-4 rounded" />
                <span>Files Group</span>
            </label>
        </div>
      </div>

      <div class="mt-4 space-y-2">
        <div v-if="attachments.length === 0 && !attachmentStore.loading" class="text-xs text-app/60">
          No attachments for this entry.
        </div>
         <div v-if="attachmentStore.loading" class="text-xs text-app/60">
            Loading attachments...
        </div>
        <div v-for="att in attachments" :key="att.id" class="flex items-center justify-between p-2 rounded-lg bg-gray-100">
          <div class="flex-grow min-w-0">
            <a :href="getFileUrl(att.file)" target="_blank" class="text-sm font-medium text-blue-600 hover:underline truncate block">
              {{ att.file.split('/').pop() }}
            </a>
            <p class="text-xs text-gray-600 truncate">{{ att.description }}</p>
          </div>
          <button @click="handleDelete(att.id)" class="ml-4 p-2 text-red-500 hover:bg-red-100 rounded-full">
            <Trash2 class="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
