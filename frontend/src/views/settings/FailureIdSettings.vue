<script setup>
import { onMounted, computed } from 'vue'
import { useCoreSettingsStore } from '@/stores/coreSettings'

const coreSettingsStore = useCoreSettingsStore()

// A computed property to easily access the settings object from the store
const settings = computed(() => coreSettingsStore.failureIdSettings)

// Fetch the settings from the backend when the component is first loaded
onMounted(() => {
  coreSettingsStore.fetchFailureIdSettings()
})

// Function to call the store action to save the current settings
function saveSettings() {
  // We pass the current state of the settings object to the action
  coreSettingsStore.saveFailureIdSettings(settings.value)
}

// A computed property to generate a live preview of the Failure ID format
const previewId = computed(() => {
  // Return a placeholder if settings haven't loaded yet
  if (!settings.value || !settings.value.prefix) {
    return '...';
  }
  
  const prefix = settings.value.prefix;
  const padding = settings.value.padding_digits || 4;
  const year = new Date().getFullYear();
  const month = String(new Date().getMonth() + 1).padStart(2, '0');
  const number = '1'.padStart(padding, '0');

  let datePart = '';
  if (settings.value.reset_cycle === 'yearly') {
    datePart = `-${year}`;
  } else if (settings.value.reset_cycle === 'monthly') {
    datePart = `-${year}${month}`;
  }

  return `${prefix}${datePart}-${number}`;
});
</script>

<template>
  <div class="space-y-4">
    <p class="text-app/80 text-sm">Configure Event ID/sequence rules, prefixes, padding, and resets.</p>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div>
        <label class="block text-sm font-medium mb-1">Prefix</label>
        <input class="field" v-model="settings.prefix" placeholder="e.g., RF" />
      </div>
      <div>
        <label class="block text-sm font-medium mb-1">Padding (digits)</label>
        <input class="field" type="number" min="1" max="10" v-model.number="settings.padding_digits" placeholder="4" />
      </div>
      <div>
        <label class="block text-sm font-medium mb-1">Reset Cycle</label>
        <select class="field" v-model="settings.reset_cycle">
          <option value="never">Never</option>
          <option value="yearly">Yearly</option>
          <option value="monthly">Monthly</option>
        </select>
      </div>
      <div>
        <label class="block text-sm font-medium mb-1">Preview</label>
        <input class="field" :value="previewId" readonly />
      </div>
    </div>

    <div class="flex gap-2">
      <button class="btn btn-primary" @click="saveSettings" :disabled="coreSettingsStore.loading">
        {{ coreSettingsStore.loading ? 'Saving...' : 'Save' }}
      </button>
    </div>
  </div>
</template>