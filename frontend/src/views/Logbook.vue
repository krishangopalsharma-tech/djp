<script setup>
import DataTable from '@/components/DataTable.vue'
import FailureDetailsDrawer from '@/components/FailureDetailsDrawer.vue'
import FailureCard from '@/components/FailureCard.vue'
import KanbanColumn from '@/components/KanbanColumn.vue'
import TimelineItem from '@/components/TimelineItem.vue'
import Spinner from '@/components/ui/Spinner.vue'

import { ref, computed, onMounted } from 'vue'
import { listFailures } from '@/api/mock'

const view = ref('table') // table | cards | board | timeline
const query = ref('')
const range = ref('30d') // today | 7d | 30d | custom
const customStart = ref('') // 'YYYY-MM-DD'
const customEnd = ref('')

const loading = ref(false)
const error = ref('')
const rows = ref([])
const drawerOpen = ref(false)
const activeItem = ref(null)

onMounted(async () => {
  loading.value = true
  error.value = ''
  try {
    const { results } = await listFailures()
    rows.value = results
  } catch (e) {
    error.value = e?.message || 'Failed to load logbook data'
  } finally {
    loading.value = false
  }
})

const statusOrder = { 'Active': 1, 'In Progress': 2, 'On Hold': 3, 'Resolved': 4 }
const toTs = (s) => {
  const d = new Date(s?.replace(' ', 'T'))
  return Number.isNaN(d.getTime()) ? 0 : d.getTime()
}

const columns = [
  { key: 'reported_at', label: 'Reported', sortAccessor: (r) => toTs(r.reported_at) },
  { key: 'fail_id',     label: 'FailID' },
  { key: 'circuit',     label: 'Circuit' },
  { key: 'station',     label: 'Station' },
  { key: 'section',     label: 'Section' },
  { key: 'assigned_to', label: 'Assigned' },
  { key: 'status',      label: 'Status', sortAccessor: (r) => statusOrder[r.status] || 99 },
  { key: 'actions',     label: 'Actions', sortable: false, align: 'text-right', width: '120px' },
]

function rangeStartEnd() {
  const now = new Date()
  let start = null, end = now
  if (range.value === 'today') {
    start = new Date(now); start.setHours(0,0,0,0)
  } else if (range.value === '7d') {
    start = new Date(now); start.setDate(now.getDate() - 6); start.setHours(0,0,0,0)
  } else if (range.value === '30d') {
    start = new Date(now); start.setDate(now.getDate() - 29); start.setHours(0,0,0,0)
  } else if (range.value === 'custom') {
    if (customStart.value) start = new Date(customStart.value + 'T00:00:00')
    if (customEnd.value)   end   = new Date(customEnd.value + 'T23:59:59')
  }
  return { start: start?.getTime() ?? null, end: end?.getTime() ?? null }
}

const filteredRows = computed(() => {
  const q = query.value.trim().toLowerCase()
  const { start, end } = rangeStartEnd()
  return rows.value
    .filter(r => {
      const ts = toTs(r.reported_at)
      const inRange = (start == null || ts >= start) && (end == null || ts <= end)
      return inRange
    })
    .filter(r => !q || Object.values(r).some(v => String(v).toLowerCase().includes(q)))
})

function openDetails(r) {
  // map to FailureDetailsDrawer schema
  activeItem.value = {
    id: r.fail_id,
    status: r.status,
    section: r.section,
    severity: r.severity,
    station: r.station,
    circuit: r.circuit,
    reportedAt: toTs(r.reported_at),
    resolvedAt: null,
    notes: r.notes || ''
  }
  drawerOpen.value = true
}

function exportCSV(data, filename = 'logbook.csv') {
  const cols = ['reported_at','fail_id','circuit','station','section','assigned_to','status']
  const header = ['Reported','FailID','Circuit','Station','Section','Assigned','Status']
  const lines = [header.join(',')]
  for (const r of data) {
    const row = [
      new Date(r.reported_at.replace(' ','T')).toLocaleString().replaceAll(',', ''),
      r.fail_id,
      r.circuit,
      r.station,
      r.section,
      r.assigned_to,
      r.status,
    ]
    lines.push(row.map(v => '"' + String(v ?? '').replaceAll('"','""') + '"').join(','))
  }
  const blob = new Blob([lines.join('\n')], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url; a.download = filename; a.click()
  URL.revokeObjectURL(url)
}

function exportPDF(data, title = 'Logbook Export') {
  const w = window.open('', '_blank')
  if (!w) return
  const rowsHtml = data.map(r => `
    <tr>
      <td>${new Date(r.reported_at.replace(' ','T')).toLocaleString()}</td>
      <td>${r.fail_id}</td>
      <td>${r.circuit}</td>
      <td>${r.station ?? ''}</td>
      <td>${r.section ?? ''}</td>
      <td>${r.assigned_to}</td>
      <td>${r.status}</td>
    </tr>`).join('')
  w.document.write(`<!doctype html><html><head><meta charset='utf-8'><title>${title}</title>
    <style>
      body{font-family:ui-sans-serif,system-ui;}
      table{border-collapse:collapse;width:100%}
      th,td{border:1px solid #ccc;padding:6px 8px;font-size:12px}
      h1{font-size:18px;text-align:center;margin:8px 0 12px}
    </style>
  </head><body>
    <h1>${title}</h1>
    <table><thead><tr>
      <th>Reported</th><th>FailID</th><th>Circuit</th><th>Station</th><th>Section</th><th>Assigned</th><th>Status</th>
    </tr></thead><tbody>${rowsHtml}</tbody></table>
  </body></html>`)
  w.document.close(); w.focus(); w.print()
}

const statuses = ['Active', 'Resolved']
const byStatus = computed(() =>
  Object.fromEntries(statuses.map(s => [s, filteredRows.value.filter(r => r.status === s)]))
)
</script>

<template>
  <div class="space-y-4">
    <!-- Header: left (date chips + custom inputs), center (title), right (view mode) -->
    <div class="grid grid-cols-1 gap-3 md:grid-cols-3 md:items-center">
      <!-- Left: date chips -->
      <div class="order-2 md:order-1">
        <div class="chip-group">
          <button
            v-for="r in [{k:'today',l:'Today'},{k:'7d',l:'Last 7 days'},{k:'30d',l:'Last 30 days'},{k:'custom',l:'Custom'}]"
            :key="r.k"
            class="chip"
            :class="range===r.k ? 'selected-primary' : 'text-app hover-primary'"
            :aria-pressed="String(range===r.k)"
            @click="range = r.k"
          >
            {{ r.l }}
          </button>
        </div>
        <div v-if="range==='custom'" class="mt-2 flex items-center gap-2 justify-end text-sm">
          <label>From <input v-model="customStart" type="date" class="rounded border-app bg-card text-app px-2 py-1" /></label>
          <label>To <input v-model="customEnd" type="date" class="rounded border-app bg-card text-app px-2 py-1" /></label>
        </div>
      </div>
      <!-- Center: title -->
      <div class="order-1 md:order-2 md:justify-self-center"><h2 class="text-2xl font-semibold text-center">Logbook</h2></div>
      <!-- Right: view modes -->
      <div class="order-3 md:order-3 md:justify-self-end">
        <!-- Transparent chip group: use same chip styles as date chips -->
        <div class="chip-group">
          <button
            v-for="m in ['table','cards','board','timeline']"
            :key="m"
            class="chip capitalize"
            :class="view === m ? 'selected-primary' : 'text-app hover-primary'"
            :aria-pressed="String(view === m)"
            @click="view = m"
          >
            {{ m }}
          </button>
        </div>
      </div>
    </div>

    <!-- Search below header row -->
    <div>
      <input
        v-model="query"
        type="text"
        placeholder="Search..."
        class="h-10 w-full sm:w-96 rounded-lg border-app bg-card text-app px-3 text-sm"
      />
    </div>

    <!-- Loading -->
    <div v-if="loading" class="rounded-2xl border-app bg-card p-6 text-sm text-app flex items-center gap-3">
      <Spinner :size="18" />
      Loading logbook...
    </div>

    <!-- Error -->
    <div v-else-if="error" class="rounded-2xl border-app bg-card p-6 text-sm text-red-600">
      {{ error }}
    </div>

    <!-- Views -->
    <div v-else>
      <!-- Board view -->
      <div v-if="view === 'board'" class="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <KanbanColumn v-for="s in statuses" :key="s" :title="s" :items="byStatus[s]" />
      </div>

      <!-- Cards view -->
      <div v-else-if="view === 'cards'" class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <FailureCard v-for="(r, i) in filteredRows" :key="i" :item="r" />
      </div>

      <!-- Table view -->
      <div v-else-if="view === 'table'">
      <DataTable
        :columns="columns"
        :rows="filteredRows"
        default-sort-key="reported_at"
        default-sort-dir="desc"
        @rowclick="openDetails"
      >
        <template #reported_at="{ row }">
          {{ new Date(row.reported_at.replace(' ', 'T')).toLocaleString() }}
        </template>
        <template #status="{ row }">
          <span class="badge"
            :class="row.status==='Resolved' ? 'badge-success' : row.status==='Active' ? 'badge-danger' : row.status==='In Progress' ? 'badge-warning' : row.status==='On Hold' ? 'badge-hold' : 'badge-neutral'">
            {{ row.status }}
          </span>
        </template>
        <template #actions="{ row }">
          <div class="flex items-center justify-end gap-1.5">
            <button class="btn-ghost border-app rounded-md hover-primary p-2" aria-label="Notify" title="Notify" @click.stop>
              <svg viewBox="0 0 24 24" class="w-4 h-4"><path fill="currentColor" d="M12 22a2 2 0 0 0 2-2H10a2 2 0 0 0 2 2Zm6-6V11a6 6 0 1 0-12 0v5l-2 2v1h16v-1Z"/></svg>
            </button>
            <button class="btn-ghost border-app rounded-md hover-primary p-2" aria-label="Edit" title="Edit" @click.stop>
              <svg viewBox="0 0 24 24" class="w-4 h-4"><path fill="currentColor" d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75ZM20.71 7.04a1.003 1.003 0 0 0 0-1.42l-2.34-2.34a1.003 1.003 0 0 0-1.42 0l-1.83 1.83l3.75 3.75l1.84-1.82Z"/></svg>
            </button>
            <button class="btn-ghost border-app rounded-md hover-primary p-2" aria-label="Delete" title="Delete" @click.stop>
              <svg viewBox="0 0 24 24" class="w-4 h-4"><path fill="currentColor" d="M6 7h12l-1 14H7L6 7Zm3-4h6l1 2h4v2H4V5h4l1-2Z"/></svg>
            </button>
          </div>
        </template>
      </DataTable>

      <!-- Bottom export buttons -->
      <div class="mt-4 flex items-center justify-end gap-2">
        <button class="btn-ghost border-app rounded-md hover-primary p-2" aria-label="Export CSV" title="Export CSV" @click="exportCSV(filteredRows)">
          <svg viewBox="0 0 24 24" class="w-5 h-5"><path fill="currentColor" d="M5 20h14v-2H5v2ZM5 4v2h14V4H5Zm7 8l-4 4h3v4h2v-4h3l-4-4Z"/></svg>
        </button>
        <button class="btn-ghost border-app rounded-md hover-primary p-2" aria-label="Export PDF" title="Export PDF" @click="exportPDF(filteredRows, 'Logbook Export')">
          <svg viewBox="0 0 24 24" class="w-5 h-5"><path fill="currentColor" d="M6 2h9l5 5v13a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2Zm8 7V3.5L19.5 9H14Z"/></svg>
        </button>
      </div>
      </div>

      <!-- Timeline view -->
      <div v-else-if="view === 'timeline'" class="space-y-4">
        <TimelineItem v-for="(r, i) in filteredRows" :key="i" :item="r" />
      </div>

      <!-- Fallback -->
      <div v-else class="rounded-2xl border-app bg-card p-6 text-sm text-muted">
        "{{ view }}" view coming soon.
      </div>
    </div>
  </div>

  <!-- Details drawer -->
  <FailureDetailsDrawer v-model="drawerOpen" :item="activeItem" />
</template>
