<script setup>
import { useFailureStore } from '@/stores/failures';

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  failure: { type: Object, default: null },
});
const emit = defineEmits(['update:modelValue']);

const failureStore = useFailureStore();

function close() {
  emit('update:modelValue', false);
}

async function sendNotification() {
  if (!props.failure) {
    return;
  }
  // THE FIX: Hard-code 'alerts' plural
  await failureStore.sendFailureNotification(props.failure.id, ['alerts']);
  close();
}
</script>

<template>
  <div v-if="modelValue && failure" class="fixed inset-0 z-50 bg-black/40 flex items-center justify-center p-4">
    <div class="bg-card rounded-2xl p-6 w-full max-w-md space-y-4">
      <h3 class="text-lg font-semibold">Confirm Notification</h3>
      <p>
        Send a reminder notification to the <strong>Alerts</strong> Telegram group for Event ID: <strong>{{ failure.fail_id }}</strong>?
      </p>
      
      <div class="flex justify-end gap-3 pt-4">
        <button @click="close" class="btn btn-outline">Cancel</button>
        <button 
          @click="sendNotification" 
          class="btn btn-primary" 
          :disabled="failureStore.loading">
          {{ failureStore.loading ? 'Sending...' : 'Send Reminder' }}
        </button>
      </div>
    </div>
  </div>
</template>