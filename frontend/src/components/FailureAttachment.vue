<script setup>
import { ref, watch, computed } from 'vue';
import { useAttachmentStore } from '@/stores/attachments';
import { useFailureStore } from '@/stores/failures'; // <-- New import
import { Trash2 } from 'lucide-vue-next';

const props = defineProps({
  failureId: {
    type: [Number, String],
    required: true,
  },
});

const attachmentStore = useAttachmentStore();
const failureStore = useFailureStore(); // <-- Initialize failure store
const attachments = computed(() => attachmentStore.attachments);

const fileInput = ref(null);
const selectedFile = ref(null);
const description = ref('');

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
    return;
  }
  // This now returns true or false
  const success = await attachmentStore.uploadAttachment(props.failureId, selectedFile.value, description.value);

  if (success) {
    // On success, send notification to both groups
    await failureStore.sendFailureNotification(props.failureId, ['alert', 'files']);

    // Reset form
    selectedFile.value = null;
    description.value = '';
    if (fileInput.value) {
      fileInput.value.value = '';
    }
  }
}

async function handleDelete(attachmentId) {
  if (confirm('Are you sure you want to delete this attachment?')) {
    await attachmentStore.deleteAttachment(attachmentId, props.failureId);
  }
}

function getFileUrl(fileUrl) {
  if (fileUrl && !fileUrl.startsWith('http')) {
    const baseUrl = import.meta.env.VITE_API_BASE_URL || '';
    const rootUrl = baseUrl.replace('/api', '');
    return `${rootUrl}${fileUrl}`;
  }
  return fileUrl;
}
</script>

<template>
  <div class="sm:col-span-2 space-y-4">
    <hr class="border-app/30 my-2" />
    <div>
      <h3 class="text-sm font-medium text-app mb-2">Attachments</h3>
      
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 p-3 border border-dashed border-app/50 rounded-lg">
        <div class="md:col-span-1">
          <label class="block text-sm font-medium mb-1">Upload New File</label>
          <input type="file" ref="fileInput" @change="handleFileSelect" class="text-sm" />
        </div>
        <div class="md:col-span-1">
          <label class="block text-sm font-medium mb-1">Description (Optional)</label>
          <input v-model="description" class="field h-9" placeholder="e.g., Photo of damaged cable" />
        </div>
        <div class="self-end">
          <button @click="handleUpload" :disabled="!selectedFile || attachmentStore.loading" class="btn btn-secondary w-full">
            {{ attachmentStore.loading ? 'Uploading...' : 'Upload' }}
          </button>
        </div>
      </div>

      <div class="mt-4 space-y-2">
        <div v-if="attachments.length === 0" class="text-xs text-app/60">
          No attachments for this entry.
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