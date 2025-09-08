<script setup>
import WidgetShell from '@/components/WidgetShell.vue'
import { useTelegramStore } from '@/stores/telegram.js'

const tg = useTelegramStore()

function onSave(g) {
  // Mock persist
  console.log('Saved group config:', { ...g })
  alert(`Saved settings for ${g.name}`)
}

function onTest(g) {
  // Mock send
  console.log('Test message to group:', { ...g })
  alert(`Test message sent to ${g.name}`)
}
</script>

<template>
  <div class="p-4 md:p-6 space-y-4">
    <WidgetShell :hideHeader="true">
      <div class="space-y-3">
        <h2 class="text-lg font-semibold">Telegram Integration Settings</h2>
        <p class="text-sm opacity-80">
          Configure three Telegram groups used across the app (frontend-only mock).
        </p>

        <div class="grid gap-4">
          <div
            v-for="g in tg.list"
            :key="g.key"
            class="rounded-2xl border bg-white p-4 space-y-3"
          >
            <div class="grid md:grid-cols-3 gap-3">
              <div>
                <label class="block text-sm font-medium mb-1">Group Label</label>
                <input
                  class="w-full px-3 py-2 rounded-lg border border-[var(--surface-3)]"
                  :value="g.name"
                  @input="tg.rename(g.key, $event.target.value)"
                />
                <p class="text-xs opacity-70 mt-1">Shown in dropdowns (e.g., “{{ g.name }}”).</p>
              </div>

              <div>
                <label class="block text-sm font-medium mb-1">Chat ID</label>
                <input
                  class="w-full px-3 py-2 rounded-lg border border-[var(--surface-3)]"
                  :value="g.chat_id"
                  @input="tg.setChatId(g.key, $event.target.value)"
                />
                <p class="text-xs opacity-70 mt-1">e.g., -1001234567890</p>
              </div>

              <div>
                <label class="block text-sm font-medium mb-1">Link / Note (optional)</label>
                <input
                  class="w-full px-3 py-2 rounded-lg border border-[var(--surface-3)]"
                  :value="g.link"
                  @input="tg.setLink(g.key, $event.target.value)"
                />
              </div>
            </div>

            <!-- Action buttons -->
            <div class="flex gap-3">
              <button class="chip selected-primary" @click="onSave(g)">Save</button>
              <button class="chip" @click="onTest(g)">Test Message</button>
            </div>
          </div>
        </div>

        <div class="text-xs opacity-70">
          Tip: Use BotFather to create a bot, add it to your group(s), then paste the Group Chat ID here.
        </div>
      </div>
    </WidgetShell>
  </div>
  
</template>

<style scoped></style>

