<script setup>
import { ref, watch, computed } from 'vue';
import { useTelegramStore } from '@/stores/telegram';

const props = defineProps({
  modelValue: { type: Boolean, default: false }, // v-model for visibility
  failure: { type: Object, default: null },
});
const emit = defineEmits(['update:modelValue']);

const telegramStore = useTelegramStore();
const availableGroups = computed(() => telegramStore.groups);
const selectedGroupKeys = ref([]);

watch(() => props.failure, (newFailure) => {
  if (newFailure) {
    // Reset selection when a new failure is passed in
    selectedGroupKeys.value = [];
  }
});

function close() {
  emit('update:modelValue', false);
}

async function sendNotification() {
  if (!props.failure || selectedGroupKeys.value.length === 0) {
    return;
  }
  await telegramStore.sendFailureNotification(props.failure.id, selectedGroupKeys.value);
  close();
}
</script>

<template>
  <div v-if="modelValue && failure" class="fixed inset-0 z-50 bg-black/40 flex items-center justify-center p-4">
    <div class="bg-card rounded-2xl p-6 w-full max-w-md space-y-4">
      <h3 class="text-lg font-semibold">Notify via Telegram</h3>
      <p>
        Send a notification for Event ID: <strong>{{ failure.fail_id }}</strong>
      </p>
      
      <div class="space-y-2">
        <label class="block text-sm font-medium">Select Telegram Group(s):</label>
        <div v-if="availableGroups.length > 0" class="space-y-1">
          <label v-for="group in availableGroups" :key="group.key" class="flex items-center gap-2 p-2 rounded-lg hover:bg-gray-100 cursor-pointer">
            <input type="checkbox" :value="group.key" v-model="selectedGroupKeys" class="h-4 w-4" />
            <span>{{ group.name }}</span>
          </label>
        </div>
        <div v-else class="text-sm text-gray-500">
          No Telegram groups configured.
        </div>
      </div>
      
      <div class="flex justify-end gap-3 pt-4">
        <button @click="close" class="btn btn-outline">Cancel</button>
        <button 
          @click="sendNotification" 
          class="btn btn-primary" 
          :disabled="selectedGroupKeys.length === 0 || telegramStore.loading">
          {{ telegramStore.loading ? 'Sending...' : 'Send' }}
        </button>
      </div>
    </div>
  </div>
</template>