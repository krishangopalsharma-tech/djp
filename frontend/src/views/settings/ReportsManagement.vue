<script setup>
import { computed } from 'vue'
import WidgetShell from '@/components/WidgetShell.vue'
import { useReportsStore } from '@/stores/reports.js'
import { useTelegramStore } from '@/stores/telegram.js'

// mock-only store
const store = useReportsStore()
const rows = computed(() => store.items)
const tg = useTelegramStore()
const tgOptions = computed(() => tg.list)

function onTemplatePicked(id, e) {
  const file = e.target.files?.[0]
  if (file) store.update(id, { templateName: file.name })
}

const freqOptions = [
  { label: 'Daily', value: 'daily' },
  { label: 'Weekly', value: 'weekly' },
  { label: 'Monthly', value: 'monthly' },
]
const dowOptions = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']
const domOptions = Array.from({ length: 31 }, (_, i) => String(i + 1))

function onFreqChange(id, v) { store.updateSchedule(id, { freq: v }) }
function onDowChange(id, v)  { store.updateSchedule(id, { dow: v }) }
function onDomChange(id, v)  { store.updateSchedule(id, { dom: v }) }
function onTimeChange(id, v) { store.updateSchedule(id, { time: v }) }
</script>

<template>
  <div class="p-4 md:p-6 space-y-4">

    <WidgetShell title="Schedule & Delivery" :hideHeader="true">
      <div class="flex items-center justify-between mb-3">
        <p class="text-sm opacity-80">
          Configure scheduled report emails / Telegram deliveries. (Frontend-only mock.)
        </p>
        <button class="chip selected-primary" @click="store.addEmpty()">+ Add Report</button>
      </div>

      <div class="overflow-x-auto">
        <table class="min-w-[960px] w-full text-sm">
          <thead>
            <tr class="text-left border-b border-app">
              <th class="py-2 pr-3 w-[220px]">Report Name</th>
              <th class="py-2 pr-3 w-[260px]">Report Template (Excel)</th>
              <th class="py-2 pr-3 w-[280px]">Schedule</th>
              <th class="py-2 pr-3 w-[120px]">Emails</th>
              <th class="py-2 pr-3 w-[220px]">Telegram Group</th>
              <th class="py-2 pr-0  w-[90px]">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="r in rows" :key="r.id" class="border-b border-app/60">
              <!-- Report Name -->
              <td class="py-2 pr-3">
                <input
                  class="w-full px-3 py-2 rounded-lg bg-card border border-app focus:outline-none"
                  v-model="r.name"
                  placeholder="e.g., Daily Failure Summary"
                />
              </td>

              <!-- Template -->
              <td class="py-2 pr-3">
                <div class="flex items-center gap-2">
                  <label class="chip cursor-pointer">
                    <input type="file" accept=".xlsx,.xls" class="hidden" @change="e => onTemplatePicked(r.id, e)" />
                    Choose…
                  </label>
                  <span class="opacity-80 truncate max-w-[180px]" :title="r.templateName || 'No file chosen'">
                    {{ r.templateName || 'No file chosen' }}
                  </span>
                </div>
                <p class="text-xs opacity-70 mt-1">
                  Placeholders supported (e.g., <code>{{ '{date}' }}</code>, <code>{{ '{section}' }}</code>) — backend wiring later.
                </p>
              </td>

              <!-- Schedule -->
              <td class="py-2 pr-3">
                <div class="flex flex-wrap items-center gap-2">
                  <select class="chip" :value="r.schedule.freq" @change="onFreqChange(r.id, $event.target.value)">
                    <option v-for="o in freqOptions" :key="o.value" :value="o.value">{{ o.label }}</option>
                  </select>

                  <!-- Weekly: show Day-of-Week -->
                  <select
                    v-if="r.schedule.freq==='weekly'"
                    class="chip"
                    :value="r.schedule.dow"
                    @change="onDowChange(r.id, $event.target.value)"
                  >
                    <option v-for="d in dowOptions" :key="d" :value="d">{{ d }}</option>
                  </select>

                  <!-- Monthly: show Day-of-Month -->
                  <select
                    v-if="r.schedule.freq==='monthly'"
                    class="chip"
                    :value="r.schedule.dom"
                    @change="onDomChange(r.id, $event.target.value)"
                  >
                    <option v-for="d in domOptions" :key="d" :value="d">{{ d }}</option>
                  </select>

                  <!-- Time -->
                  <input
                    type="time"
                    class="chip"
                    :value="r.schedule.time"
                    @change="onTimeChange(r.id, $event.target.value)"
                  />
                </div>
              </td>

              <!-- Emails -->
              <td class="py-2 pr-3">
                <label class="inline-flex items-center gap-2">
                  <input type="checkbox" v-model="r.sendEmail" />
                  <span>Enable</span>
                </label>
              </td>

              <!-- Telegram: enable + group select -->
              <td class="py-2 pr-3">
                <div class="flex flex-wrap items-center gap-2">
                  <label class="inline-flex items-center gap-2">
                    <input type="checkbox" v-model="r.sendTelegram" />
                    <span>Enable</span>
                  </label>
                  <select
                    class="chip"
                    :disabled="!r.sendTelegram"
                    :value="r.telegramGroupKey ?? 'reports'"
                    @change="store.update(r.id, { telegramGroupKey: $event.target.value })"
                  >
                    <option v-for="g in tgOptions" :key="g.key" :value="g.key">{{ g.name }}</option>
                  </select>
                </div>
                <p class="text-xs opacity-70 mt-1">
                  Groups managed in <span class="underline">Settings → Telegram</span>.
                </p>
              </td>

              <!-- Actions -->
              <td class="py-2 pr-0">
                <button class="chip" @click="store.remove(r.id)">Delete</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </WidgetShell>
  </div>
</template>

<style scoped>
/* keep page compact and consistent */
</style>
