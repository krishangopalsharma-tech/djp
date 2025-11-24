<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { Bell, Pencil, Trash2, ChevronLeft, ChevronRight, History, FileSpreadsheet, FileText } from 'lucide-vue-next'
// import NotificationModal from '@/components/NotificationModal.vue' // Removed
import { useTelegramStore } from '@/stores/telegram'
import { useFailureStore } from '@/stores/failures'
import FailureDetailsDrawer from '@/components/FailureDetailsDrawer.vue'

const telegramStore = useTelegramStore()
const failureStore = useFailureStore()

onMounted(() => {
  telegramStore.fetchTelegramGroups()
})

const drawerOpen = ref(false)
const activeItem = ref(null)

function openDetails(row) {
  activeItem.value = row
  drawerOpen.value = true
}

// const isNotifyModalOpen = ref(false) // Removed
// const failureToNotify = ref(null)    // Removed

async function onNotify(row) {
  // Hardcoded to 'alerts' group as requested
  await failureStore.sendFailureNotification(row.id, ['alerts'])
}


/* -------- Props -------- */
const props = defineProps({
  items: { type: Array, default: () => [] },
  showToolbar: { type: Boolean, default: true },
  showBottomActions: { type: Boolean, default: true },
  showRowActions: { type: Boolean, default: true },
  // NEW:
  loading: { type: Boolean, default: false },
  // add this prop
  storageKey: { type: String, default: 'recentFailures' },
  // allow hiding the component's own title when embedded in dashboards
  showHeader: { type: Boolean, default: true },
  editingId: { type: [String, Number], default: null },

})


/* -------- Emits -------- */
const emit = defineEmits(['view', 'edit', 'delete'])

/* -------- Local UI state -------- */
const q = ref('')
const status = ref('all') // 'all' | 'Active' | 'In Progress' | 'Resolved' | 'On Hold'
const statusTabs = ['all', 'Active', 'In Progress', 'Resolved', 'On Hold', 'Information']

function statusTabVariant(tab) {
  if (tab === 'all') return 'chip-variant-all'
  if (tab === 'Active') return 'chip-variant-active'
  if (tab === 'In Progress') return 'chip-variant-inprog'
  if (tab === 'Resolved') return 'chip-variant-resolved'
  if (tab === 'On Hold') return 'chip-variant-onhold'
  if (tab === 'Information') return 'chip-variant-info' // You might need to define this class or use a default
  return ''
}

/* -------- Sorting -------- */
const sortKey = ref('reported_at') // 'id' | 'circuit' | 'station' | 'section' | 'status' | 'reported_at' | 'resolved_at'
const sortDir = ref('desc')       // 'asc' | 'desc'
function setSort(key) {
  if (sortKey.value === key) {
    sortDir.value = sortDir.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortKey.value = key
    sortDir.value = (key === 'id' || key === 'reported_at' || key === 'resolved_at') ? 'desc' : 'asc'
  }
}
function cmp(a, b) {
  if (a == null && b == null) return 0
  if (a == null) return -1
  if (b == null) return 1
  const na = Number(a), nb = Number(b)
  if (!Number.isNaN(na) && !Number.isNaN(nb)) return na - nb
  return String(a).localeCompare(String(b), undefined, { sensitivity: 'base', numeric: true })
}

/* -------- Data source (props fallback safe) -------- */
const fallbackRows = [
  { fail_id: 'RF001', circuit: 'CKT-001', station: 'Bandra',  section: 'Western Line',  current_status: 'Active',      reported_at: Date.now() - 3600_000 },
  { fail_id: 'RF002', circuit: 'CKT-002', station: 'Andheri', section: 'Western Line',  current_status: 'In Progress', reported_at: Date.now() - 7200_000 },
  { fail_id: 'RF003', circuit: 'CKT-003', station: 'Dadar',   section: 'Central Line',  current_status: 'Resolved',    reported_at: Date.now() - 8600_000, resolved_at: Date.now() - 1800_000 },
  { fail_id: 'RF004', circuit: 'CKT-004', station: 'Virar',   section: 'Western Line',  current_status: 'On Hold',     reported_at: Date.now() - 9300_000 },
]
// Filter out UI-only 'message' entries from the dashboard list
const sourceRows = computed(() => {
  return (props.items?.length ? props.items : fallbackRows)
})

/* -------- Time helpers (robust: numbers or ISO strings) -------- */
function toMs(ts) {
  if (ts == null) return null
  if (typeof ts === 'number') return ts
  const ms = new Date(ts).getTime()
  return Number.isNaN(ms) ? null : ms
}
function timeAgo(ts) {
  const ms = toMs(ts)
  if (ms == null) return '—'
  const diff = Date.now() - ms
  const m = Math.floor(diff / 60000)
  if (m < 1) return 'just now'
  if (m < 60) return `${m}m ago`
  const h = Math.floor(m / 60)
  if (h < 24) return `${h}h ago`
  const d = Math.floor(h / 24)
  return `${d}d ago`
}
function fmt(ts) {
  const ms = toMs(ts)
  return ms == null ? '—' : new Date(ms).toLocaleString()
}

/* -------- Filter + Sort -------- */
const filteredSorted = computed(() => {
  const base = status.value !== 'all'
    ? sourceRows.value.filter(r => (r.current_status ?? r.status) === status.value)
    : sourceRows.value.filter(r => (r.current_status ?? r.status) !== 'Information')

  const term = q.value.trim().toLowerCase()
  const filtered = term
    ? base.filter(r => JSON.stringify(r).toLowerCase().includes(term))
    : base

  const key = sortKey.value
  const dir = sortDir.value === 'asc' ? 1 : -1

  const getSortValue = (row, sortKey) => {
    switch (sortKey) {
      case 'reported_at': return toMs(row.reported_at ?? row.reportedAt) ?? 0
      case 'resolved_at': return toMs(row.resolved_at ?? row.resolvedAt) ?? 0
      case 'id': return row.fail_id ?? row.id
      case 'circuit': return row.circuit?.name ?? row.circuit
      case 'station': return row.station?.name ?? row.station
      case 'section': return row.section?.name ?? row.section
      case 'status': return row.current_status ?? row.status
      default: return ''
    }
  }

  return [...filtered].sort((a, b) => {
    const av = getSortValue(a, key)
    const bv = getSortValue(b, key)
    return cmp(av, bv) * dir
  })
})
// ---- Load persisted table UI (safe parse) ----
function loadState() {
  let st = null
  try { st = JSON.parse(localStorage.getItem(props.storageKey) || 'null') } catch (_) {}
  if (!st || typeof st !== 'object') return
  if (typeof st.q === 'string') q.value = st.q
  if (typeof st.status === 'string') status.value = st.status
  if (typeof st.sortKey === 'string') sortKey.value = st.sortKey
  if (st.sortDir === 'asc' || st.sortDir === 'desc') sortDir.value = st.sortDir
  if (typeof st.perPage === 'number' && st.perPage > 0) perPage.value = st.perPage
  if (typeof st.page === 'number' && st.page >= 0) page.value = st.page
}

/* -------- Pagination -------- */
const page = ref(0)
const perPage = ref(10)
const total = computed(() => filteredSorted.value.length)
const pageCount = computed(() => Math.max(1, Math.ceil(total.value / perPage.value)))
const pagedRows = computed(() => {
  const start = page.value * perPage.value
  return filteredSorted.value.slice(start, start + perPage.value)
})

loadState()


// ---- Persist table UI whenever it changes ----
watch([q, status, sortKey, sortDir, perPage, page], ([Q, S, K, D, P, Pg]) => {
  localStorage.setItem(props.storageKey, JSON.stringify({
    q: Q, status: S, sortKey: K, sortDir: D, perPage: Number(P), page: Number(Pg),
  }))
})

watch([total, pageCount], () => { if (page.value > pageCount.value - 1) page.value = Math.max(0, pageCount.value - 1) })
const showingFrom = computed(() => (total.value ? page.value * perPage.value + 1 : 0))
const showingTo = computed(() => Math.min(total.value, (page.value + 1) * perPage.value))
function prevPage() { if (page.value > 0) page.value-- }
function nextPage() { if (page.value < pageCount.value - 1) page.value++ }

/* -------- Row-action helpers -------- */
function onEdit(row)   { emit('edit', row.id) }
function onDelete(row) { emit('delete', row) }

/* -------- UI helpers -------- */
function badgeClasses(s) {
  if (s === 'Active')       return 'badge-danger'
  if (s === 'In Progress')  return 'badge-warning'
  if (s === 'Resolved')     return 'badge-success'
  if (s === 'On Hold')      return 'badge-hold'
  return 'badge-neutral'
}

// For Dashboard: status pill sized to text, text hidden
function statusPillClass(s) {
  if (s === 'Active')       return 'bg-[var(--s-active)]'
  if (s === 'In Progress')  return 'bg-[var(--s-inprogress)]'
  if (s === 'Resolved')     return 'bg-[var(--s-resolved)]'
  if (s === 'On Hold')      return 'bg-[var(--s-onhold)]'
  return 'bg-[var(--platinum)]'
}

// Light row tint based on status color (new global palette)
// Hover handling for rows to intensify background tint slightly
const hoveredIndex = ref(-1)
function rowBg(s, hovered = false) {
  const pct = hovered ? 65 : 50
  return (
    s === 'Active'       ? `color-mix(in srgb, var(--s-active) ${pct}%, white)` :
    s === 'In Progress'  ? `color-mix(in srgb, var(--s-inprogress) ${pct}%, white)` :
    s === 'Resolved'     ? `color-mix(in srgb, var(--s-resolved) ${pct}%, white)` :
    s === 'On Hold'      ? `color-mix(in srgb, var(--s-onhold) ${pct}%, white)` :
    'transparent'
  )
}

import ExcelJS from 'exceljs'

async function downloadExcel() {
  const data = pagedRows.value
  if (!data.length) return

  const workbook = new ExcelJS.Workbook()
  const worksheet = workbook.addWorksheet('Recent Failures')

  // Define columns
  worksheet.columns = [
    { header: 'ID', key: 'id', width: 15 },
    { header: 'Circuit', key: 'circuit', width: 15 },
    { header: 'Station', key: 'station', width: 15 },
    { header: 'Section', key: 'section', width: 20 },
    { header: 'Status', key: 'status', width: 15 },
    { header: 'Reported At', key: 'reported', width: 25 }
  ]

  // Style header row
  worksheet.getRow(1).font = { bold: true, color: { argb: 'FFFFFFFF' } }
  worksheet.getRow(1).fill = {
    type: 'pattern',
    pattern: 'solid',
    fgColor: { argb: 'FF2980B9' } // Blue header
  }

  // Color mapping (ARGB)
  const statusColors = {
    'Active': 'FFFFC8C8',      // Light Red
    'In Progress': 'FFFFF0C8', // Light Yellow/Orange
    'Resolved': 'FFC8FFC8',    // Light Green
    'On Hold': 'FFF0F0F0',     // Light Grey
    'Information': 'FFC8F0FF'  // Light Blue
  }

  // Add rows
  data.forEach(r => {
    const row = worksheet.addRow({
      id: r.fail_id,
      circuit: r.circuit?.circuit_id || r.circuit || '',
      station: r.station?.code || r.station || '',
      section: r.section?.name || r.section || '',
      status: r.current_status || r.status || '',
      reported: new Date(r.reported_at || r.reportedAt).toLocaleString()
    })

    // Apply color to the status cell (or whole row if preferred, user asked for "colour in csv" implying the row/cell concept)
    // Only color the filled cells, not the entire infinite row
    const status = r.current_status || r.status
    const color = statusColors[status]
    if (color) {
      row.eachCell({ includeEmpty: true }, (cell) => {
        cell.fill = {
          type: 'pattern',
          pattern: 'solid',
          fgColor: { argb: color }
        }
        // Add border for better look
        cell.border = {
          top: { style: 'thin' },
          left: { style: 'thin' },
          bottom: { style: 'thin' },
          right: { style: 'thin' }
        }
      })
    }
  })

  // Generate buffer
  const buffer = await workbook.xlsx.writeBuffer()
  
  // Trigger download
  const blob = new Blob([buffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = `failures_export_${new Date().toISOString().slice(0, 10)}.xlsx`
  link.click()
}

import jsPDF from 'jspdf'
import autoTable from 'jspdf-autotable'

function downloadPDF() {
  const data = pagedRows.value // Changed from filteredSorted.value to pagedRows.value
  if (!data.length) return

  const doc = new jsPDF()
  
  // Title
  doc.setFontSize(16)
  doc.text('Recent Failure Logs', 14, 15)
  doc.setFontSize(10)
  doc.text(`Generated on: ${new Date().toLocaleString()}`, 14, 22)

  const headers = [['ID', 'Circuit', 'Station', 'Section', 'Status', 'Reported At']]
  const rows = data.map(r => [
    r.fail_id,
    r.circuit?.circuit_id || r.circuit || '',
    r.station?.code || r.station || '',
    r.section?.name || r.section || '',
    r.current_status || r.status || '',
    new Date(r.reported_at || r.reportedAt).toLocaleString()
  ])

  // Color mapping based on status (RGB values)
  const statusColors = {
    'Active': [255, 200, 200],      // Light Red
    'In Progress': [255, 240, 200], // Light Yellow/Orange
    'Resolved': [200, 255, 200],    // Light Green
    'On Hold': [240, 240, 240],     // Light Grey
    'Information': [200, 240, 255]  // Light Blue
  }

  autoTable(doc, {
    head: headers,
    body: rows,
    startY: 25,
    theme: 'grid',
    styles: { fontSize: 8, textColor: 20 }, // Dark text for readability
    headStyles: { fillColor: [41, 128, 185], textColor: 255 },
    didParseCell: (data) => {
      if (data.section === 'body') {
        const status = data.row.raw[4] // Status is at index 4
        const color = statusColors[status]
        if (color) {
          data.cell.styles.fillColor = color
        }
      }
    }
  })

  doc.save(`failures_export_${new Date().toISOString().slice(0, 10)}.pdf`)
}

</script>

<template>
  <div class="space-y-4">
    <div class="rounded-2xl border-app bg-card text-app p-4 shadow-lg">
      <div class="pb-3 mb-3 border-b border-app" v-if="showHeader">
         <h2 class="text-xl font-semibold leading-tight text-center">Recent Logs</h2>
      </div>

      <!-- Toolbar -->
      <div v-if="showToolbar" class="p-3 flex flex-col sm:flex-row sm:items-center sm:justify-between flex-wrap gap-2">
        <div class="chip-group">
          <button
            v-for="tab in statusTabs"
            :key="tab"
            class="chip capitalize"
            :class="status === tab ? statusTabVariant(tab) + ' is-active' : 'text-app hover-primary'"
            :aria-pressed="String(status === tab)"
            @click="status = tab"
          >
            {{ tab }}
          </button>
        </div>

        <input
          v-model="q"
          type="text"
          placeholder="Search..."
          class="h-10 w-full sm:w-64 max-w-full min-w-0 rounded-lg border-app bg-card text-app px-3 text-sm"
        />
      </div>

      <!-- Table -->
      <div class="overflow-x-auto">
        <table class="min-w-full text-sm">
          <thead class="bg-card">
            <tr>
              <th class="text-center font-semibold text-app px-3 py-1.5 cursor-pointer select-none"
                  :aria-sort="sortKey==='id' ? (sortDir==='asc'?'ascending':'descending') : 'none'"                  @click="setSort('id')">
                <div class="inline-flex items-center gap-1">EV ID <span v-if="sortKey==='id'">{{ sortDir==='asc' ? '▲' : '▼' }}</span></div>
              </th>
              <th class="text-center font-semibold text-app px-3 py-1.5 cursor-pointer select-none"
                  :aria-sort="sortKey==='circuit' ? (sortDir==='asc'?'ascending':'descending') : 'none'"
                  @click="setSort('circuit')">
                <div class="inline-flex items-center gap-1">Circuit <span v-if="sortKey==='circuit'">{{ sortDir==='asc' ? '▲' : '▼' }}</span></div>
              </th>
              <th class="text-center font-semibold text-app px-3 py-1.5 cursor-pointer select-none"
                  :aria-sort="sortKey==='station' ? (sortDir==='asc'?'ascending':'descending') : 'none'"
                  @click="setSort('station')">
                <div class="inline-flex items-center gap-1">Station <span v-if="sortKey==='station'">{{ sortDir==='asc' ? '▲' : '▼' }}</span></div>
              </th>
              <th class="text-center font-semibold text-app px-3 py-1.5 cursor-pointer select-none"
                  :aria-sort="sortKey==='section' ? (sortDir==='asc'?'ascending':'descending') : 'none'"
                  @click="setSort('section')">
                <div class="inline-flex items-center gap-1">Section <span v-if="sortKey==='section'">{{ sortDir==='asc' ? '▲' : '▼' }}</span></div>
              </th>

              <!-- NEW: Reported (sortable) -->
              <th class="text-center font-semibold text-app px-3 py-1.5 cursor-pointer select-none"
                  :aria-sort="sortKey==='reported_at' ? (sortDir==='asc'?'ascending':'descending') : 'none'"
                  @click="setSort('reported_at')">
                <div class="inline-flex items-center gap-1">Reported <span v-if="sortKey==='reported_at'">{{ sortDir==='asc' ? '▲' : '▼' }}</span></div>
              </th>

              <th v-if="showRowActions" class="text-center font-semibold text-app px-3 py-1.5">Actions</th>
            </tr>
          </thead>

          <tbody>
            <!-- Rows -->
             <!-- SKELETON ROWS (show while loading) -->
          <tr v-if="!loading && filteredSorted.length === 0">
            <td class="px-4 py-3"><div class="h-4 rounded bg-[var(--border)]/40 animate-pulse mx-auto w-20" /></td>
            <td class="px-4 py-3"><div class="h-4 rounded bg-[var(--border)]/40 animate-pulse mx-auto w-24" /></td>
            <td class="px-4 py-3"><div class="h-4 rounded bg-[var(--border)]/40 animate-pulse mx-auto w-24" /></td>
            <td class="px-4 py-3"><div class="h-4 rounded bg-[var(--border)]/40 animate-pulse mx-auto w-28" /></td>
            <td class="px-4 py-3"><div class="h-4 rounded bg-[var(--border)]/40 animate-pulse mx-auto w-20" /></td>
            <td v-if="showRowActions" class="px-4 py-3"> 
              <div class="h-4 rounded bg-[var(--border)]/40 animate-pulse mx-auto w-24" />
            </td>
            <td :colspan="showRowActions ? 6 : 5" class="px-4 py-6 text-center text-muted"></td>
          </tr>

            <tr
              v-if="!loading" v-for="(r, i) in pagedRows"
              :key="r.id ?? i"
              class="cursor-pointer"
              role="button"
              tabindex="0"
              @click="openDetails(r)"
              @keydown.enter.space="openDetails(r)"
              @mouseenter="hoveredIndex = i"
              @mouseleave="hoveredIndex = -1"
              :style="{ backgroundColor: rowBg(r.current_status ?? r.status, hoveredIndex === i) }"
            >
              <td class="px-3 py-1.5 text-center rounded-l-xl"><div class="truncate">{{ (r.fail_id ?? r.id)?.split('-').pop() ?? '—' }}</div></td>
              <td class="px-3 py-1.5 text-center"><div class="truncate">{{ r.circuit?.circuit_id ?? r.circuit ?? '—' }}</div></td>
              <td class="px-3 py-1.5 text-center"><div class="truncate">{{ r.station?.code ?? r.station ?? '—' }}</div></td>
              <td class="px-3 py-1.5 text-center"><div class="truncate">{{ r.section?.name ?? r.section ?? '—' }}</div></td>

              <!-- NEW: Reported cell (relative text + PrimeVue tooltip + native title) -->
              <td class="px-3 py-1.5 text-center">
                <span
                
                  :title="fmt(r.reported_at ?? r.reportedAt)"
                >
                  {{ timeAgo(r.reported_at ?? r.reportedAt) }}
                </span>
              </td>

              <!-- PrimeVue black action buttons -->
             <td v-if="showRowActions" class="px-3 py-1.5 text-center rounded-r-xl">
              <div class="inline-flex items-center justify-center gap-2">
                <button
                  class="btn-ghost border-app rounded-md hover-primary p-2"
                  aria-label="Notify" title="Notify" @click.stop="onNotify(r)">
                  <Bell class="w-4 h-4" />
                </button>
                <button
                  class="btn-ghost border-app rounded-md hover-primary p-2"
                  aria-label="Edit" title="Edit" @click.stop="$emit('edit', r.id)">
                  <Pencil class="w-4 h-4" />
                </button>
                <button
                  class="btn-ghost border-app rounded-md hover-primary p-2"
                  aria-label="Delete" title="Delete" @click.stop="onDelete(r)">
                  <Trash2 class="w-4 h-4" />
                </button>
              </div>
            </td>
            <td v-else class="px-3 py-1.5 text-center rounded-r-xl"></td>
            </tr>

            <!-- Empty state -->
            <tr v-if="!loading && filteredSorted.length === 0" class="rounded-xl overflow-hidden">
              <td :colspan="showRowActions ? 6 : 5" class="px-4 py-6 text-center text-muted">
                No recent failures
              </td>
            </tr>
          </tbody>
        </table>

        <!-- Pager -->
        <div class="mt-3 flex flex-col sm:flex-row sm:items-center gap-3 justify-between">
          <div class="text-xs text-muted">
            Showing {{ showingFrom }}–{{ showingTo }} of {{ total }}
          </div>

          <div class="inline-flex items-center gap-2">
            <label class="text-sm text-app">Rows per page</label>
            <select v-model.number="perPage" class="rounded-lg border-app bg-card text-app px-2 py-1 text-sm">
              <option :value="10">10</option>
              <option :value="20">20</option>
              <option :value="50">50</option>
            </select>

            <div class="ml-2 inline-flex items-center gap-2">
              <button
                class="btn-ghost border-app rounded-md hover-primary p-2 disabled:opacity-40"
                :disabled="page === 0"
                aria-label="Previous page" title="Previous" @click="prevPage">
                <ChevronLeft class="w-4 h-4" />
              </button>

              <span class="text-sm tabular-nums">{{ page + 1 }} / {{ pageCount }}</span>

              <button
                class="btn-ghost border-app rounded-md hover-primary p-2 disabled:opacity-40"
                :disabled="page >= pageCount - 1"
                aria-label="Next page" title="Next" @click="nextPage">
                <ChevronRight class="w-4 h-4" />
              </button>

            </div>
          </div>
        </div>
      </div>

      <!-- Bottom actions (Dashboard hides via prop) -->
      <div v-if="showBottomActions" class="flex justify-center gap-3 px-3 py-5">

        <button
          class="btn-ghost border-app rounded-md hover-primary p-2"
          aria-label="Export Excel"
          title="Export Excel"
          @click="downloadExcel"
        >
          <FileSpreadsheet class="w-4 h-4" />
        </button>
        <button
          class="btn-ghost border-app rounded-md hover-primary p-2"
          aria-label="Export PDF"
          title="Export PDF"
          @click="downloadPDF"
        >
          <FileText class="w-4 h-4" />
        </button>
      </div>
    </div>
    <!-- NotificationModal removed -->
    <FailureDetailsDrawer v-model="drawerOpen" :item="activeItem" />
  </div>
</template>
  