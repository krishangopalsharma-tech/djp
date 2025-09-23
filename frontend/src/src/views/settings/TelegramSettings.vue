<script setup>
import { onMounted, computed } from 'vue';
import { useTelegramStore } from '@/stores/telegram.js';

const tg = useTelegramStore();

const settings = computed(() => tg.settings);
const groupList = computed(() => tg.groups);

onMounted(() => {
  tg.fetchTelegramSettings();
  tg.fetchTelegramGroups();
});

function onSaveToken() {
  tg.saveTelegramSettings();
}

function onSaveGroup(group) {
  tg.updateTelegramGroup(group);
}

function onTest(group) {
  tg.sendTestMessage(group);
}
</script>

<template>
  <div class="space-y-6">
    <p class="text-app/80 text-sm">
      Configure the Telegram Bot and the three groups used for system alerts, file uploads, and scheduled reports.
    </p>

    <div class="card p-4 space-y-3">
        <h3 class="font-semibold text-app">Telegram Bot Configuration</h3>
        <div>
          <label class="block text-sm font-medium mb-1">Bot Token (HTTP API Key)</label>
          <input
            class="field"
            v-model="settings.bot_token"
            placeholder="Paste your bot token here, e.g., 8404126856:AAEXUY..."
          />
          <p class="text-xs opacity-70 mt-1">Get this from the BotFather on Telegram.</p>
        </div>
         <div class="flex gap-3 pt-2">
          <button class="btn btn-primary" @click="onSaveToken" :disabled="tg.loading">
            {{ tg.loading ? 'Saving...' : 'Save Token' }}
          </button>
        </div>
    </div>

    <div v-if="tg.loading && groupList.length === 0" class="text-center py-10 text-muted">
      Loading Telegram settings...
    </div>
    <div v-else-if="tg.error && groupList.length === 0" class="text-center py-10 text-red-500">
      {{ tg.error }}
    </div>
    <div v-else class="space-y-4">
      <div v-for="g in groupList" :key="g.key" class="card p-4 space-y-3">
        <h3 class="font-semibold text-app">{{ g.name }}</h3>
        <div class="grid md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium mb-1">Chat ID</label>
            <input
              class="field"
              v-model="g.chat_id"
              :placeholder="{
                reports: '-4923590033',
                alerts: '-4905455511',
                files: '-4812151797'
              }[g.key] || 'e.g., -1001234567890'"
            />
            <p class="text-xs opacity-70 mt-1">The unique identifier for the {{ g.name }}.</p>
          </div>

          <div>
            <label class="block text-sm font-medium mb-1">Link / Note (optional)</label>
            <input
              class="field"
              v-model="g.link"
              placeholder="e.g., Invitation link"
            />
          </div>
        </div>

        <div class="flex gap-3 pt-2">
          <button class="btn btn-primary" @click="onSaveGroup(g)" :disabled="tg.loading">
            {{ tg.loading ? 'Saving...' : 'Save Group' }}
          </button>
          <button class="btn" @click="onTest(g)" :disabled="tg.loading || !g.chat_id">Test Message</button>
        </div>
      </div>
    </div>
  </div>
</template>
