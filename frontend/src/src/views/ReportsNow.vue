<script setup>
import WidgetShell from '@/components/WidgetShell.vue'
import { computed, ref } from 'vue'
import { useReportsStore } from '@/stores/reports.js'
import { useTelegramStore } from '@/stores/telegram.js'

const reports = useReportsStore()
const tg = useTelegramStore()
const rows = computed(() => reports.items)
const tgOptions = computed(() => tg.list)

const sendingIds = ref(new Set())

function sendNow(row) {
  const payload = {
    id: row.id,
    name: row.name,
    templateName: row.templateName,
    sendEmail: row.sendEmail ?? false,
    sendTelegram: row.sendTelegram ?? false,
    telegramGroupKey: row.telegramGroupKey ?? 'reports',
  }
  sendingIds.value.add(row.id)
  setTimeout(() => {
    console.log('[ReportsNow] SEND NOW payload:', payload)
    alert(`Queued send for “${row.name}”\nEmail: ${payload.sendEmail}\nTelegram: ${payload.sendTelegram} (${payload.telegramGroupKey})`)
    sendingIds.value.delete(row.id)
  }, 400)
}
</script>

<template>
  <div class="p-4 md:p-6 space-y-4">
    <h1 class="text-xl md:text-2xl font-semibold">Reports Now</h1>

    <WidgetShell :hideHeader="true">
      <div class="space-y-3">
        <p class="text-sm opacity-80">Trigger any defined report immediately. (Frontend-only mock)</p>

        <div class="overflow-x-auto">
          <table class="min-w-[960px] w-full text-sm">
            <thead>
              <tr class="text-left border-b border-[var(--surface-3)]">
                <th class="py-2 pr-3 w-[280px]">Report</th>
                <th class="py-2 pr-3 w-[220px]">Template</th>
                <th class="py-2 pr-3 w-[140px]">Email</th>
                <th class="py-2 pr-3 w-[240px]">Telegram</th>
                <th class="py-2 pr-0  w-[120px]">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="r in rows" :key="r.id" class="border-b border-[var(--surface-2)]">
                <td class="py-2 pr-3">
                  <div class="font-medium">{{ r.name || '—' }}</div>
                  <div class="text-xs opacity-70">ID: {{ r.id.slice(0,8) }}</div>
                </td>
                <td class="py-2 pr-3">
                  <span class="opacity-80">{{ r.templateName || 'No file chosen' }}</span>
                </td>
                <td class="py-2 pr-3">
                  <label class="inline-flex items-center gap-2">
                    <input type="checkbox" v-model="r.sendEmail" />
                    <span>Send Email</span>
                  </label>
                </td>
                <td class="py-2 pr-3">
                  <div class="flex flex-wrap items-center gap-2">
                    <label class="inline-flex items-center gap-2">
                      <input type="checkbox" v-model="r.sendTelegram" />
                      <span>Telegram</span>
                    </label>
                    <select
                      class="chip"
                      :disabled="!r.sendTelegram"
                      :value="r.telegramGroupKey ?? 'reports'"
                      @change="reports.update(r.id, { telegramGroupKey: $event.target.value })"
                    >
                      <option v-for="g in tgOptions" :key="g.key" :value="g.key">{{ g.name }}</option>
                    </select>
                  </div>
                </td>
                <td class="py-2 pr-0">
                  <button
                    class="chip selected-primary"
                    :disabled="sendingIds.has(r.id) || (!r.sendEmail && !r.sendTelegram)"
                    @click="sendNow(r)"
                  >
                    {{ sendingIds.has(r.id) ? 'Sending…' : 'Send Now' }}
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <p class="text-xs opacity-70">
          Note: backend/bot wiring comes later; this page logs a mock payload.
        </p>
      </div>
    </WidgetShell>
  </div>
</template>

<style scoped></style>

