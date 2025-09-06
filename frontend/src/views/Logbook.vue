<script setup>
import DataTable from '@/components/DataTable.vue'
import FailureDetailsDrawer from '@/components/FailureDetailsDrawer.vue'
import FailureCard from '@/components/FailureCard.vue'
import KanbanColumn from '@/components/KanbanColumn.vue'
import TimelineItem from '@/components/TimelineItem.vue'
import Spinner from '@/components/ui/Spinner.vue'
import SearchSelect from '@/components/form/SearchSelect.vue'
import SectionFilterChips from '@/components/SectionFilterChips.vue'
import { Bell, Pencil, Trash2, FileDown, FileText, ChevronLeft, ChevronRight, ChevronsLeft, ChevronsRight } from 'lucide-vue-next'

import { ref, computed, onMounted } from 'vue'
import { listFailures, getCircuits, getSections, getStations, getSupervisors, getStatuses } from '@/api/mock'

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

// Filter options
const circuitOptions = ref([])
const sectionOptions = ref([])
const stationOptions = ref([])
const supervisorOptions = ref([])
const statusOptions = ref([])

// Selected filters
const selectedCircuits = ref([])
const selectedSections = ref([])
const selectedStations = ref([])
const selectedSupervisors = ref([])
const selectedStatuses = ref([])

// Pagination and sorting
const rowsPerPage = ref(20)
const currentPage = ref(1)
const sortKey = ref('reported_at')
const sortDir = ref('desc')

onMounted(async () => {
  loading.value = true
  error.value = ''
  try {
    const [failures, circuits, sections, stations, supervisors, statuses] = await Promise.all([
      listFailures(),
      getCircuits(),
      getSections(),
      getStations(),
      getSupervisors(),
      getStatuses(),
    ])
    rows.value = failures.results
    circuitOptions.value = circuits
    sectionOptions.value = sections
    stationOptions.value = stations
    supervisorOptions.value = supervisors
    statusOptions.value = statuses
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

function formatDuration(start, end) {
  if (!start || !end) return '–'
  const diff = toTs(end) - toTs(start)
  if (diff < 0) return '–'
  const minutes = Math.floor(diff / 60000)
  if (minutes < 60) return `${minutes}m`
  const hours = Math.floor(minutes / 60)
  const mins = minutes % 60
  return `${hours}h ${mins}m`
}

const columns = [
  { key: 'reported_at', label: 'Reported', sortAccessor: (r) => toTs(r.reported_at), align: 'text-left' },
  { key: 'resolved_at', label: 'Resolve Time', sortAccessor: (r) => toTs(r.resolved_at), align: 'text-center' },
  { key: 'duration',    label: 'Duration', sortable: false, align: 'text-center' },
  { key: 'fail_id',     label: 'Event ID', align: 'text-center' },
  { key: 'circuit',     label: 'Circuit', align: 'text-center' },
  { key: 'station',     label: 'Station', align: 'text-center' },
  { key: 'section',     label: 'Section', align: 'text-center' },
  { key: 'assigned_to', label: 'Assigned', align: 'text-center' },
  { key: 'status',      label: 'Status', sortAccessor: (r) => statusOrder[r.status] || 99, align: 'text-center' },
  { key: 'actions',     label: 'Actions', sortable: false, align: 'text-center', width: '120px' },
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
    .filter(r => selectedCircuits.value.length === 0 || selectedCircuits.value.includes(r.circuit))
    .filter(r => selectedSections.value.length === 0 || selectedSections.value.includes(r.section))
    .filter(r => selectedStations.value.length === 0 || selectedStations.value.includes(r.station))
    .filter(r => selectedSupervisors.value.length === 0 || selectedSupervisors.value.includes(r.assigned_to))
    .filter(r => selectedStatuses.value.length === 0 || selectedStatuses.value.includes(r.status))
})

const sortedRows = computed(() => {
  const data = [...filteredRows.value]
  const col = columns.find(c => c.key === sortKey.value)
  if (!col) return data
  const dir = sortDir.value === 'asc' ? 1 : -1
  const acc = typeof col.sortAccessor === 'function'
    ? (r) => col.sortAccessor(r)
    : (r) => r[col.key]
  return data.sort((a, b) => {
    const av = acc(a)
    const bv = acc(b)
    if (av == null && bv == null) return 0
    if (av == null) return -1 * dir
    if (bv == null) return  1 * dir
    const na = Number(av), nb = Number(bv)
    const va = Number.isNaN(na) ? String(av) : na
    const vb = Number.isNaN(nb) ? String(bv) : nb
    return (va > vb ? 1 : va < vb ? -1 : 0) * dir
  })
})

const totalPages = computed(() => Math.ceil(sortedRows.value.length / rowsPerPage.value))

const paginatedRows = computed(() => {
  const start = (currentPage.value - 1) * rowsPerPage.value
  const end = start + rowsPerPage.value
  return sortedRows.value.slice(start, end)
})

const activeFilters = computed(() => {
  const filters = {}
  if (selectedCircuits.value.length) filters['Circuit'] = selectedCircuits.value
  if (selectedSections.value.length) filters['Section'] = selectedSections.value
  if (selectedStations.value.length) filters['Station'] = selectedStations.value
  if (selectedSupervisors.value.length) filters['Supervisor'] = selectedSupervisors.value
  if (selectedStatuses.value.length) filters['Status'] = selectedStatuses.value
  return filters
})

function removeFilter(category, value) {
  if (category === 'Circuit') selectedCircuits.value = selectedCircuits.value.filter(v => v !== value)
  if (category === 'Section') selectedSections.value = selectedSections.value.filter(v => v !== value)
  if (category === 'Station') selectedStations.value = selectedStations.value.filter(v => v !== value)
  if (category === 'Supervisor') selectedSupervisors.value = selectedSupervisors.value.filter(v => v !== value)
  if (category === 'Status') selectedStatuses.value = selectedStatuses.value.filter(v => v !== value)
}

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
    resolvedAt: r.resolved_at ? toTs(r.resolved_at) : null,
    notes: r.notes || ''
  }
  drawerOpen.value = true
}

function exportCSV(data, filename = 'logbook.csv') {
  const cols = ['reported_at','fail_id','circuit','station','section','assigned_to','status']
  const header = ['Reported','Event ID','Circuit','Station','Section','Assigned','Status']
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
      <th>Reported</th><th>Event ID</th><th>Circuit</th><th>Station</th><th>Section</th><th>Assigned</th><th>Status</th>
    </tr></thead><tbody>${rowsHtml}</tbody></table>
  </body></html>`)
  w.document.close(); w.focus(); w.print()
}

const statuses = ['Active', 'Resolved']
const byStatus = computed(() =>
  Object.fromEntries(statuses.map(s => [s, filteredRows.value.filter(r => r.status === s)]))
)

function toggleSort(key) {
  if (sortKey.value === key) {
    sortDir.value = sortDir.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortKey.value = key
    sortDir.value = 'asc'
  }
}

function goToFirstPage() { currentPage.value = 1 }
function goToLastPage() { currentPage.value = totalPages.value }
function goToNextPage() { if (currentPage.value < totalPages.value) currentPage.value++ }
function goToPreviousPage() { if (currentPage.value > 1) currentPage.value-- }

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

    <!-- Search and Filter Bar -->
    <div class="sticky top-0 z-50 bg-app py-4">
      <div class="flex flex-wrap items-center gap-4">
        <input
          v-model="query"
          type="text"
          placeholder="Search..."
          class="h-10 w-full rounded-lg border-app bg-card text-app px-3 text-sm shadow-card md:w-auto placeholder:text-gray-700"
        />
        <SearchSelect v-model="selectedCircuits" :options="circuitOptions" placeholder="Filter by Circuit" multiple class="shadow-card" />
        <SearchSelect v-model="selectedSections" :options="sectionOptions" placeholder="Filter by Section" multiple class="shadow-card" />
        <SearchSelect v-model="selectedStations" :options="stationOptions" placeholder="Filter by Station" multiple class="shadow-card" />
        <SearchSelect v-model="selectedSupervisors" :options="supervisorOptions" placeholder="Filter by Supervisor" multiple class="shadow-card" />
        <SearchSelect v-model="selectedStatuses" :options="statusOptions" placeholder="Filter by Status" multiple class="shadow-card" />
        <div class="flex items-center gap-2 ml-auto">
            <span class="text-sm text-muted">Per page</span>
            <select v-model="rowsPerPage" class="chip text-app hover-primary">
              <option value="10">10</option>
              <option value="20">20</option>
              <option value="30">30</option>
              <option value="50">50</option>
              <option value="100">100</option>
            </select>
        </div>
      </div>
    </div>

    <!-- Filter Chips -->
    <div v-if="Object.keys(activeFilters).length">
      <SectionFilterChips :filters="activeFilters" @remove="removeFilter" />
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
        <FailureCard v-for="(r, i) in paginatedRows" :key="i" :item="r" />
      </div>

      <!-- Table view -->
      <div v-else-if="view === 'table'" class="rounded-2xl border-app bg-card p-4 shadow-card">
        <DataTable
          :columns="columns"
          :rows="paginatedRows"
          :sort-key="sortKey"
          :sort-dir="sortDir"
          @sort="toggleSort"
          @rowclick="openDetails"
        >
          <template #reported_at="{ row }">
            {{ new Date(row.reported_at.replace(' ', 'T')).toLocaleString() }}
          </template>
          <template #resolved_at="{ row }">
            {{ row.resolved_at ? new Date(row.resolved_at.replace(' ', 'T')).toLocaleString() : '–' }}
          </template>
          <template #duration="{ row }">
            {{ formatDuration(row.reported_at, row.resolved_at) }}
          </template>
          <template #status="{ row }">
            <span class="badge"
              :class="row.status==='Resolved' ? 'badge-success' : row.status==='Active' ? 'badge-danger' : row.status==='In Progress' ? 'badge-warning' : row.status==='On Hold' ? 'badge-hold' : 'badge-neutral'"
            >
              {{ row.status }}
            </span>
          </template>
          <template #actions="{ row }">
            <div class="flex items-center justify-center gap-1.5">
              <button class="btn-ghost border-app rounded-md hover-primary p-2" aria-label="Notify" title="Notify" @click.stop>
                <Bell class="w-4 h-4" />
              </button>
              <button class="btn-ghost border-app rounded-md hover-primary p-2" aria-label="Edit" title="Edit" @click.stop>
                <Pencil class="w-4 h-4" />
              </button>
              <button class="btn-ghost border-app rounded-md hover-primary p-2" aria-label="Delete" title="Delete" @click.stop>
                <Trash2 class="w-4 h-4" />
              </button>
            </div>
          </template>
        </DataTable>
      </div>

      <!-- Sticky Bottom controls for Table view -->
      <div v-if="view === 'table'" class="sticky bottom-0 z-50 bg-app p-4 flex items-center justify-between">
        <!-- Export buttons -->
        <div class="flex items-center justify-center gap-2 p-2 rounded-lg">
            <button class="chip capitalize text-app hover-primary gap-2" @click="exportCSV(sortedRows)">
              <FileDown class="w-4 h-4" />
              <span>Export CSV</span>
            </button>
            <button class="chip capitalize text-app hover-primary gap-2" @click="exportPDF(sortedRows, 'Logbook Export')">
              <FileText class="w-4 h-4" />
              <span>Export PDF</span>
            </button>
        </div>

        <!-- Pagination -->
        <div class="flex items-center justify-end gap-2 p-2 rounded-lg shadow-card">
            <button @click="goToFirstPage" :disabled="currentPage === 1" class="btn-ghost border-app rounded-md hover-primary p-2" title="First Page">
              <ChevronsLeft class="w-4 h-4" />
            </button>
            <button @click="goToPreviousPage" :disabled="currentPage === 1" class="btn-ghost border-app rounded-md hover-primary p-2" title="Previous Page">
              <ChevronLeft class="w-4 h-4" />
            </button>
            <span class="text-sm text-muted">Page {{ currentPage }} of {{ totalPages }}</span>
            <button @click="goToNextPage" :disabled="currentPage === totalPages" class="btn-ghost border-app rounded-md hover-primary p-2" title="Next Page">
              <ChevronRight class="w-4 h-4" />
            </button>
            <button @click="goToLastPage" :disabled="currentPage === totalPages" class="btn-ghost border-app rounded-md hover-primary p-2" title="Last Page">
              <ChevronsRight class="w-4 h-4" />
            </button>
        </div>
      </div>

      <!-- Timeline view -->
      <div v-else-if="view === 'timeline'" class="space-y-4">
        <TimelineItem v-for="(r, i) in sortedRows" :key="i" :item="r" />
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
