<script setup>
import { onMounted, reactive, computed, ref } from 'vue';
import { useEmailStore } from '@/stores/email';
import { useUIStore } from '@/stores/ui'; // Import the UI store

const emailStore = useEmailStore();
const uiStore = useUIStore(); // Initialize the UI store

const settings = computed(() => emailStore.settings);
const loading = computed(() => emailStore.loading);
const testEmail = ref('');

// Local state for the "add recipient" input fields
const add = reactive({ to: '', cc: '', bcc: '' });

// Fetch settings when the component is mounted
onMounted(() => {
  emailStore.fetchSettings().then(() => {
    // Pre-fill test email with first recipient if available
    if (settings.value.recipients?.to?.length > 0) {
      testEmail.value = settings.value.recipients.to[0];
    }
  });
});

function addRecipient(kind) {
  const email = (add[kind] || '').trim();
  if (!email) return;

  // Ensure the array exists before pushing
  if (!settings.value.recipients[kind]) {
    settings.value.recipients[kind] = [];
  }
  
  if (!settings.value.recipients[kind].includes(email)) {
    settings.value.recipients[kind].push(email);
  }
  add[kind] = ''; // Clear the input field
}

function removeRecipient(kind, email) {
  if (settings.value.recipients[kind]) {
    settings.value.recipients[kind] = settings.value.recipients[kind].filter(e => e !== email);
  }
}

function onSave() {
  emailStore.saveSettings();
}

function onTest() {
  // Add a frontend check to provide immediate feedback before calling the API
  if (!settings.value.host) {
    uiStore.pushToast({
      type: 'warn',
      title: 'Configuration Incomplete',
      message: 'Please enter and save your SMTP Host settings before sending a test.'
    });
    return;
  }
  emailStore.sendTestEmail(testEmail.value);
}
</script>

<template>
  <div class="space-y-4">
    <p class="text-app/80 text-sm">
      Configure the SMTP server for sending automated emails and set default recipients.
    </p>

    <!-- SMTP Section -->
    <div class="card">
      <h2 class="text-lg font-semibold mb-3">SMTP Server</h2>
      <div class="grid md:grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium mb-1">Host</label>
          <input class="field" v-model="settings.host" placeholder="smtp.example.com" />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">Port</label>
          <input type="number" class="field" v-model.number="settings.port" placeholder="587" />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">Encryption</label>
          <select class="field" v-model="settings.encryption">
            <option value="STARTTLS">STARTTLS</option>
            <option value="SSL/TLS">SSL/TLS</option>
            <option value="None">None</option>
          </select>
        </div>
        <div></div>
        <div>
          <label class="block text-sm font-medium mb-1">Username</label>
          <input class="field" v-model="settings.username" placeholder="user@example.com" autocomplete="username" />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">Password</label>
          <input type="password" class="field" v-model="settings.password" autocomplete="new-password" placeholder="Leave blank to keep unchanged" />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">From Name</label>
          <input class="field" v-model="settings.from_name" placeholder="RFMS Notifications" />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">From Address</label>
          <input class="field" v-model="settings.from_address" placeholder="no-reply@example.com" />
        </div>
      </div>
    </div>

    <!-- Recipients Section -->
    <div class="card">
       <h2 class="text-lg font-semibold mb-3">Default Recipients</h2>
       <div class="space-y-3">
          <!-- TO -->
          <div>
            <label class="block text-sm font-medium mb-1">To</label>
            <div class="flex gap-2 mb-2">
              <input class="field" v-model="add.to" @keydown.enter.prevent="addRecipient('to')" placeholder="Add recipient email and press Enter"/>
              <button class="btn btn-secondary" @click="addRecipient('to')">+</button>
            </div>
            <div class="flex flex-wrap gap-2" v-if="settings.recipients.to && settings.recipients.to.length">
              <span v-for="r in settings.recipients.to" :key="r" class="inline-flex items-center gap-2 px-2 py-1 rounded-lg border text-sm bg-gray-100">
                {{ r }}
                <button class="text-xs opacity-70 hover:opacity-100" @click="removeRecipient('to', r)">×</button>
              </span>
            </div>
          </div>
          <!-- CC -->
          <div>
            <label class="block text-sm font-medium mb-1">CC</label>
            <div class="flex gap-2 mb-2">
              <input class="field" v-model="add.cc" @keydown.enter.prevent="addRecipient('cc')" placeholder="Add CC email and press Enter" />
              <button class="btn btn-secondary" @click="addRecipient('cc')">+</button>
            </div>
             <div class="flex flex-wrap gap-2" v-if="settings.recipients.cc && settings.recipients.cc.length">
              <span v-for="r in settings.recipients.cc" :key="r" class="inline-flex items-center gap-2 px-2 py-1 rounded-lg border text-sm bg-gray-100">
                {{ r }}
                <button class="text-xs opacity-70 hover:opacity-100" @click="removeRecipient('cc', r)">×</button>
              </span>
            </div>
          </div>
          <!-- BCC -->
          <div>
            <label class="block text-sm font-medium mb-1">BCC</label>
            <div class="flex gap-2 mb-2">
              <input class="field" v-model="add.bcc" @keydown.enter.prevent="addRecipient('bcc')" placeholder="Add BCC email and press Enter"/>
              <button class="btn btn-secondary" @click="addRecipient('bcc')">+</button>
            </div>
            <div class="flex flex-wrap gap-2" v-if="settings.recipients.bcc && settings.recipients.bcc.length">
              <span v-for="r in settings.recipients.bcc" :key="r" class="inline-flex items-center gap-2 px-2 py-1 rounded-lg border text-sm bg-gray-100">
                {{ r }}
                <button class="text-xs opacity-70 hover:opacity-100" @click="removeRecipient('bcc', r)">×</button>
              </span>
            </div>
          </div>
       </div>
    </div>
    
    <!-- Actions -->
    <div class="flex items-center justify-end gap-3">
        <input v-model="testEmail" class="field w-64" placeholder="Enter test email address" />
        <button class="btn" @click="onTest" :disabled="loading || !testEmail">
          {{ loading ? 'Sending...' : 'Send Test Email' }}
        </button>
        <button class="btn btn-primary" @click="onSave" :disabled="loading">
          {{ loading ? 'Saving...' : 'Save Changes' }}
        </button>
    </div>
  </div>
</template>

