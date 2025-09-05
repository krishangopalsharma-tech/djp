<script setup>
import { ref, computed, watch } from 'vue'
import { Bell, Pencil, Trash2, ChevronLeft, ChevronRight } from 'lucide-vue-next'


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

})


/* -------- Emits -------- */
const emit = defineEmits(['view', 'notify', 'edit', 'delete'])

/* -------- Local UI state -------- */
const q = ref('')
const status = ref('all') // 'all' | 'Active' | 'In Progress' | 'Resolved' | 'On Hold'
const statusTabs = ['all', 'Active', 'In Progress', 'Resolved', 'On Hold']

/* -------- Sorting -------- */
const sortKey = ref('reportedAt') // 'id' | 'circuit' | 'station' | 'section' | 'status' | 'reportedAt' | 'resolvedAt'
const sortDir = ref('desc')       // 'asc' | 'desc'
function setSort(key) {
  if (sortKey.value === key) {
    sortDir.value = sortDir.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortKey.value = key
    sortDir.value = (key === 'id' || key === 'reportedAt' || key === 'resolvedAt') ? 'desc' : 'asc'
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
  { id: 'RF001', circuit: 'CKT-001', station: 'Bandra',  section: 'Western Line',  status: 'Active',      reportedAt: Date.now() - 3600_000 },
  { id: 'RF002', circuit: 'CKT-002', station: 'Andheri', section: 'Western Line',  status: 'In Progress', reportedAt: Date.now() - 7200_000 },
  { id: 'RF003', circuit: 'CKT-003', station: 'Dadar',   section: 'Central Line',  status: 'Resolved',    reportedAt: Date.now() - 8600_000, resolvedAt: Date.now() - 1800_000 },
  { id: 'RF004', circuit: 'CKT-004', station: 'Virar',   section: 'Western Line',  status: 'On Hold',     reportedAt: Date.now() - 9300_000 },
]
const sourceRows = computed(() => (props.items?.length ? props.items : fallbackRows))

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
    ? sourceRows.value.filter(r => r.status === status.value)
    : sourceRows.value

  const term = q.value.trim().toLowerCase()
  const filtered = term
    ? base.filter(r => Object.values(r).some(v => String(v ?? '').toLowerCase().includes(term)))
    : base

  const key = sortKey.value
  const dir = sortDir.value === 'asc' ? 1 : -1
  return [...filtered].sort((a, b) => {
    const av =
      key === 'reportedAt' ? (toMs(a.reportedAt) ?? 0) :
      key === 'resolvedAt' ? (toMs(a.resolvedAt) ?? 0) :
      key === 'id'        ? a.id :
      key === 'circuit'   ? a.circuit :
      key === 'station'   ? a.station :
      key === 'section'   ? a.section :
      key === 'status'    ? a.status : ''
    const bv =
      key === 'reportedAt' ? (toMs(b.reportedAt) ?? 0) :
      key === 'resolvedAt' ? (toMs(b.resolvedAt) ?? 0) :
      key === 'id'        ? b.id :
      key === 'circuit'   ? b.circuit :
      key === 'station'   ? b.station :
      key === 'section'   ? b.section :
      key === 'status'    ? b.status : ''
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
function onNotify(row) { emit('notify', row) }
function onEdit(row)   { emit('edit', row) }
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
function rowStyle(s) {
  const mixed =
    s === 'Active'       ? 'color-mix(in srgb, var(--s-active) 50%, white)' :
    s === 'In Progress'  ? 'color-mix(in srgb, var(--s-inprogress) 50%, white)' :
    s === 'Resolved'     ? 'color-mix(in srgb, var(--s-resolved) 50%, white)' :
    s === 'On Hold'      ? 'color-mix(in srgb, var(--s-onhold) 50%, white)' :
    'transparent'
  return { background: mixed }
}

</script>

<template>
  <div class="space-y-4">
    <div class="text-center" v-if="showHeader">
      <h2 class="text-2xl font-semibold leading-tight">Recent Failure Logs</h2>
    </div>

    <div class="rounded-2xl border-app bg-card text-app p-4">
      <!-- Toolbar -->
      <div v-if="showToolbar" class="p-3 flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
        <div class="inline-flex rounded-lg border-app bg-card p-1 w-fit">
          <button
            v-for="tab in statusTabs"
            :key="tab"
            class="px-3 py-1.5 text-sm rounded-md capitalize"
            :class="status === tab ? 'selected-primary' : 'text-app hover-primary'"
            @click="status = tab"
          >
            {{ tab }}
          </button>
        </div>

        <input
          v-model="q"
          type="text"
          placeholder="Search..."
          class="h-10 w-full sm:w-64 rounded-lg border-app bg-card text-app px-3 text-sm"
        />
      </div>

      <!-- Table -->
      <div class="overflow-x-hidden">
        <table class="min-w-full text-sm table-fixed">
          <colgroup>
            <col class="w-1/6" /><col class="w-1/6" /><col class="w-1/6" />
            <col class="w-1/6" /><col class="w-1/6" />  <!-- Reported -->
            <col v-if="showRowActions" class="w-1/6" />
          </colgroup>

          <thead class="bg-card">
            <tr>
              <th class="text-center font-semibold text-app px-3 py-1.5 cursor-pointer select-none"
                  :aria-sort="sortKey==='id' ? (sortDir==='asc'?'ascending':'descending') : 'none'"
                  @click="setSort('id')">
                <div class="inline-flex items-center gap-1">RF ID <span v-if="sortKey==='id'">{{ sortDir==='asc' ? '▲' : '▼' }}</span></div>
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
                  :aria-sort="sortKey==='reportedAt' ? (sortDir==='asc'?'ascending':'descending') : 'none'"
                  @click="setSort('reportedAt')">
                <div class="inline-flex items-center gap-1">Reported <span v-if="sortKey==='reportedAt'">{{ sortDir==='asc' ? '▲' : '▼' }}</span></div>
              </th>

              <th v-if="showRowActions" class="text-center font-semibold text-app px-3 py-1.5">Actions</th>
            </tr>
          </thead>

          <tbody>
            <!-- Rows -->
             <!-- SKELETON ROWS (show while loading) -->
          <tr v-if="!loading && filteredSorted.length === 0" class="border-t">
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
              v-if="!loading" v-for="r in pagedRows"
              :key="r.id"
              class="border-t hover-primary cursor-pointer"
              :style="rowStyle(r.status)"
              role="button"
              tabindex="0"
              @click="emit('view', r)"
              @keydown.enter.space="emit('view', r)"
            >
              <td class="px-3 py-1.5 text-center"><div class="truncate">{{ r.id ?? '—' }}</div></td>
              <td class="px-3 py-1.5 text-center"><div class="truncate">{{ r.circuit ?? '—' }}</div></td>
              <td class="px-3 py-1.5 text-center"><div class="truncate">{{ r.station ?? '—' }}</div></td>
              <td class="px-3 py-1.5 text-center"><div class="truncate">{{ r.section ?? '—' }}</div></td>

              <!-- NEW: Reported cell (relative text + PrimeVue tooltip + native title) -->
              <td class="px-3 py-1.5 text-center">
                <span
                 
                  :title="fmt(r.reportedAt)"
                >
                  {{ timeAgo(r.reportedAt) }}
                </span>
              </td>

              <!-- PrimeVue black action buttons -->
             <td v-if="showRowActions" class="px-3 py-1.5 text-center">
              <div class="inline-flex items-center justify-center gap-2">
                <button
                  class="btn-ghost border-app rounded-md hover-primary p-2"
                  aria-label="Notify" title="Notify" @click.stop="onNotify(r)">
                  <Bell class="w-4 h-4" />
                </button>
                <button
                  class="btn-ghost border-app rounded-md hover-primary p-2"
                  aria-label="Edit" title="Edit" @click.stop="onEdit(r)">
                  <Pencil class="w-4 h-4" />
                </button>
                <button
                  class="btn-ghost border-app rounded-md hover-primary p-2"
                  aria-label="Delete" title="Delete" @click.stop="onDelete(r)">
                  <Trash2 class="w-4 h-4" />
                </button>
              </div>
            </td>
            </tr>

            <!-- Empty state -->
            <tr v-if="!loading && filteredSorted.length === 0" class="border-t">
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
      <div v-if="showBottomActions" class="flex justify-center gap-4 px-3 py-5">
        <button
          class="btn shadow-lg hover:shadow-xl inline-flex h-11 w-11 rounded-full p-0"
          aria-label="Retrieve Drafts"
          title="Retrieve Drafts"
        >
          ⟳
        </button>
        <button
          class="btn shadow-lg hover:shadow-xl inline-flex h-11 w-11 rounded-full p-0"
          aria-label="Export CSV"
          title="Export CSV"
        >
          ⭳
        </button>
        <button
          class="btn shadow-lg hover:shadow-xl inline-flex h-11 w-11 rounded-full p-0"
          aria-label="Export PDF"
          title="Export PDF"
        >
          ⎙
        </button>
      </div>
    </div>
  </div>
</template>
