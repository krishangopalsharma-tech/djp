<script setup>
import { computed, reactive } from 'vue'
import WidgetShell from '@/components/WidgetShell.vue'
import { useSupervisorMovements } from '@/stores/supervisorMovements'
import { useTelegramStore } from '@/stores/telegram'

const store = useSupervisorMovements()
const tg = useTelegramStore()

// Telegram group selector (default to Reports group)
const tgOptions = computed(() => tg.list)
const selectedGroupKey = reactive({ value: 'reports' })

// Simple "send today" mock — logs payload and alerts
function sendTodayNow() {
  const today = new Date().toISOString().slice(0, 10)
  const list = store.rows
  const payload = {
    date: today,
    groupKey: selectedGroupKey.value,
    count: list.length,
    entries: list.map(r => ({
      id: r.id, dept: r.dept, name: r.name, designation: r.designation,
      location: r.location, onLeave: r.onLeave, leaveFrom: r.leaveFrom, leaveTo: r.leaveTo,
      lookAfterId: r.lookAfterId, purpose: r.purpose, notes: r.notes,
    })),
  }
  console.log('[SupervisorMovements] DAILY SEND PAYLOAD', payload)
  alert(`Daily summary prepared for ${today}\nGroup: ${selectedGroupKey.value}\nEntries: ${payload.count}`)
}

// ----- On Leave modal state -----
const leaveModal = reactive({
  open: false,
  id: '',
  from: '',
  to: '',
  lookAfterId: '',
})

// Open modal when toggling "On Leave" to true
function onLeaveToggle(r) {
  if (r.onLeave) {
    // open modal prefilled
    leaveModal.open = true
    leaveModal.id = r.id
    leaveModal.from = r.leaveFrom || new Date().toISOString().slice(0, 10)
    // default to +1 day if empty
    const next = new Date()
    next.setDate(next.getDate() + 1)
    leaveModal.to = r.leaveTo || next.toISOString().slice(0, 10)
    leaveModal.lookAfterId = r.lookAfterId || ''
  } else {
    // clearing leave info if unchecked
    store.update(r.id, { leaveFrom: '', leaveTo: '', lookAfterId: '' })
  }
}

// Confirm modal → persist to row
function confirmLeave() {
  if (!leaveModal.id) return
  store.update(leaveModal.id, {
    leaveFrom: leaveModal.from,
    leaveTo: leaveModal.to,
    lookAfterId: leaveModal.lookAfterId,
  })
  closeLeave()
}

// Cancel modal → revert checkbox in row
function cancelLeave() {
  if (leaveModal.id) {
    const i = store.rows.findIndex(x => x.id === leaveModal.id)
    if (i !== -1) store.rows[i].onLeave = false
  }
  closeLeave()
}

function closeLeave() {
  leaveModal.open = false
  leaveModal.id = ''
  leaveModal.from = ''
  leaveModal.to = ''
  leaveModal.lookAfterId = ''
}

const supervisorOptions = computed(() =>
  store.rows.map(r => ({ value: r.id, label: `${r.name || '—'} (${r.dept || '—'})` }))
)
</script>

<template>
  <div class="p-4 md:p-6 space-y-4">
    <h1 class="text-xl md:text-2xl font-semibold">Supervisor Movements</h1>

    <WidgetShell :hideHeader="true">
      <!-- Top controls: Add + Telegram quick send -->
      <div class="flex flex-wrap items-center gap-2 justify-between mb-3">
        <div class="text-sm opacity-80">
          Daily auto-send (evening) to Telegram (frontend mock). Choose group &amp; press Send Today Now to preview.
        </div>
        <div class="flex items-center gap-2">
          <select class="chip" v-model="selectedGroupKey.value">
            <option v-for="g in tgOptions" :key="g.key" :value="g.key">{{ g.name }}</option>
          </select>
          <button class="chip selected-primary" @click="sendTodayNow">Send Today Now</button>
          <button class="chip" @click="store.addEmpty()">+ Add Entry</button>
        </div>
      </div>

      <div class="overflow-x-auto">
        <table class="min-w-[1100px] w-full text-sm">
          <thead>
            <tr class="text-left border-b border-[var(--surface-3)]">
              <th class="py-2 pr-3 w-[120px]">Dept</th>
              <th class="py-2 pr-3 w-[200px]">Name</th>
              <th class="py-2 pr-3 w-[200px]">Designation</th>
              <th class="py-2 pr-3 w-[160px]">Location</th>
              <th class="py-2 pr-3 w-[110px]">On Leave</th>
              <th class="py-2 pr-3 w-[220px]">Purpose</th>
              <th class="py-2 pr-3">Notes</th>
              <th class="py-2 pr-0  w-[90px]">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="r in store.rows" :key="r.id" class="border-b border-[var(--surface-2)]">
              <!-- NEW Dept -->
              <td class="py-2 pr-3">
                <input class="w-full px-3 py-2 rounded-lg border border-[var(--surface-3)]" v-model="r.dept" placeholder="Dept" />
              </td>

              <!-- NEW Name -->
              <td class="py-2 pr-3">
                <input class="w-full px-3 py-2 rounded-lg border border-[var(--surface-3)]" v-model="r.name" placeholder="Supervisor name" />
              </td>

              <!-- NEW Designation -->
              <td class="py-2 pr-3">
                <input class="w-full px-3 py-2 rounded-lg border border-[var(--surface-3)]" v-model="r.designation" placeholder="Designation" />
              </td>

              <!-- NEW Location -->
              <td class="py-2 pr-3">
                <input class="w-full px-3 py-2 rounded-lg border border-[var(--surface-3)]" v-model="r.location" placeholder="Location" />
              </td>

              <!-- Removed: From/To/Out/In per request -->

              <!-- NEW On Leave -->
              <td class="py-2 pr-3">
                <label class="inline-flex items-center gap-2">
                  <input type="checkbox" v-model="r.onLeave" @change="onLeaveToggle(r)" />
                  <span>On Leave</span>
                </label>
                <div v-if="r.onLeave && (r.leaveFrom || r.leaveTo)" class="text-xs opacity-70 mt-1">
                  {{ r.leaveFrom || '—' }} → {{ r.leaveTo || '—' }}
                </div>
                <div v-if="r.onLeave && r.lookAfterId" class="text-xs opacity-70">
                  Look after: {{ supervisorOptions.find(o => o.value === r.lookAfterId)?.label || '—' }}
                </div>
              </td>

              <!-- NEW Purpose -->
              <td class="py-2 pr-3">
                <input class="w-full px-3 py-2 rounded-lg border border-[var(--surface-3)]" v-model="r.purpose" placeholder="Purpose" />
              </td>

              <!-- NEW Notes -->
              <td class="py-2 pr-3">
                <input class="w-full px-3 py-2 rounded-lg border border-[var(--surface-3)]" v-model="r.notes" placeholder="Notes" />
              </td>

              <td class="py-2 pr-0">
                <button class="chip" @click="store.remove(r.id)">Delete</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </WidgetShell>

    <!-- Leave Modal -->
    <div v-if="leaveModal.open" class="fixed inset-0 z-50">
      <div class="absolute inset-0 bg-black/50"></div>
      <div class="absolute inset-0 flex items-center justify-center p-4">
        <div class="w-full max-w-lg rounded-2xl border bg-white p-4 space-y-3">
          <h3 class="text-lg font-semibold">Mark Supervisor On Leave</h3>
          <div class="grid md:grid-cols-2 gap-3">
            <div>
              <label class="block text-sm font-medium mb-1">From</label>
              <input type="date" class="chip w-full" v-model="leaveModal.from" />
            </div>
            <div>
              <label class="block text-sm font-medium mb-1">To</label>
              <input type="date" class="chip w-full" v-model="leaveModal.to" />
            </div>
            <div class="md:col-span-2">
              <label class="block text-sm font-medium mb-1">Look after (another supervisor)</label>
              <select class="chip w-full" v-model="leaveModal.lookAfterId">
                <option :value="''" disabled>Please select</option>
                <option
                  v-for="o in supervisorOptions"
                  :key="o.value"
                  :value="o.value"
                >
                  {{ o.label }}
                </option>
              </select>
              <p class="text-xs opacity-70 mt-1">
                Choose the supervisor who will look after this section/station during the leave period.
              </p>
            </div>
          </div>
          <div class="flex items-center justify-end gap-2">
            <button class="chip" @click="cancelLeave">Cancel</button>
            <button class="chip selected-primary" @click="confirmLeave">Save</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped></style>
