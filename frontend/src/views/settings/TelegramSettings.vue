<script setup>
import { onMounted, computed } from 'vue';
import { useTelegramStore } from '@/stores/telegram.js';

const tg = useTelegramStore();

const groupList = computed(() => tg.list);

onMounted(() => {
  tg.fetchTelegramGroups();
});

function onSave(group) {
  tg.updateTelegramGroup(group);
}

function onTest(group) {
  tg.sendTestMessage(group);
}
</script>

<template>
  <div class="space-y-4">
    <p class="text-app/80 text-sm">
      Configure the three Telegram groups used for system alerts, file uploads, and scheduled reports.
    </p>

    <div v-if="tg.loading && groupList.length === 0" class="text-center py-10 text-muted">
      Loading Telegram settings...
    </div>
    <div v-else-if="tg.error" class="text-center py-10 text-red-500">
      {{ tg.error }}
    </div>

    <div v-else class="space-y-4">
      <div
        v-for="g in groupList"
        :key="g.key"
        class="card p-4 space-y-3"
      >
        <div class="grid md:grid-cols-3 gap-4">
          <div>
            <label class="block text-sm font-medium mb-1">Group Label</label>
            <input
              class="field"
              v-model="g.name"
            />
            <p class="text-xs opacity-70 mt-1">Shown in dropdowns (e.g., “{{ g.name }}”).</p>
          </div>

          <div>
            <label class="block text-sm font-medium mb-1">Chat ID</label>
            <input
              class="field"
              v-model="g.chat_id"
              placeholder="e.g., -1001234567890"
            />
            <p class="text-xs opacity-70 mt-1">The unique identifier for the group.</p>
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
          <button class="btn btn-primary" @click="onSave(g)" :disabled="tg.loading">
            {{ tg.loading ? 'Saving...' : 'Save' }}
          </button>
          <button class="btn" @click="onTest(g)">Test Message</button>
        </div>
      </div>
       <div class="text-xs opacity-70 px-1">
          Tip: Use BotFather to create a bot, add it to your group(s), then paste the Group Chat ID here.
        </div>
    </div>
  </div>
</template>
