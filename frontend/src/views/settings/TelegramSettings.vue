<script setup>
</script>
<template>
  <div class="space-y-4">
    <h2 class="text-xl font-semibold">Telegram Integration</h2>
    <p class="text-app/80 text-sm">Set bot token, chat/group IDs, and message templates. (Frontend placeholder)</p>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div>
        <label class="block text-sm font-medium mb-1">Bot Token</label>
        <input class="field" placeholder="123456:ABC-DEF..." />
      </div>
      <div>
        <label class="block text-sm font-medium mb-1">Default Chat ID</label>
        <input class="field" placeholder="-1001234567890" />
      </div>
      <div class="md:col-span-2">
        <label class="block text-sm font-medium mb-1">Message Template</label>
        <textarea class="field-textarea" placeholder="New Event: {{event_id}} — {{summary}}"></textarea>
      </div>
    </div>

    <div class="flex gap-2">
      <button class="btn btn-primary">Save</button>
      <button class="btn">Test Message</button>
    </div>
  </div>
</template>

