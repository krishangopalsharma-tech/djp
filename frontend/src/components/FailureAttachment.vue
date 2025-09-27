<script setup>
import { ref } from 'vue';
import { http } from '@/lib/http';
import { useUIStore } from '@/stores/ui';
import { useFailureStore } from '@/stores/failures';

const props = defineProps({
  failureId: {
    type: [Number, String],
    required: true,
  },
});

const uiStore = useUIStore();
const failureStore = useFailureStore();
const fileInput = ref(null);
const selectedFile = ref(null);
const description = ref('');
const isLoading = ref(false);

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
  formData.append('description', description.value);

  isLoading.value = true;
  try {
    // Post to the new backend endpoint
    await http.post('/failures/attachments/send-to-telegram/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    
    uiStore.pushToast({ type: 'success', title: 'Success', message: 'File sent to Telegram group.' });
    
    // Reset form after successful upload
    selectedFile.value = null;
    description.value = '';
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
          <button @click="handleUpload" :disabled="!selectedFile || isLoading" class="btn btn-secondary w-full">
            {{ isLoading ? 'Uploading...' : 'Upload to Telegram' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>