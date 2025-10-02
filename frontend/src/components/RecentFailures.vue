<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { Bell, Pencil, Trash2, ChevronLeft, ChevronRight, FileSpreadsheet, FileText } from 'lucide-vue-next'
import NotificationModal from '@/components/NotificationModal.vue'
import { useTelegramStore } from '@/stores/telegram'
import FailureDetailsDrawer from '@/components/FailureDetailsDrawer.vue';

const drawerOpen = ref(false);
const activeItem = ref(null);

function openDetails(row) {
  activeItem.value = row;
  drawerOpen.value = true;
}

const telegramStore = useTelegramStore()

onMounted(() => {
  telegramStore.fetchTelegramGroups()
})

const isNotifyModalOpen = ref(false)
const failureToNotify = ref(null)

function openNotifyModal(row) {
  failureToNotify.value = row
  isNotifyModalOpen.value = true
}

const props = defineProps({
  items: { type: Array, default: () => [] },
  showToolbar: { type: Boolean, default: true },
  showBottomActions: { type: Boolean, default: true },
  showRowActions: { type: Boolean, default: true },
  loading: { type: Boolean, default: false },
  storageKey: { type: String, default: 'recentFailures' },
  showHeader: { type: Boolean, default: true },
  editingId: { type: [String, Number], default: null },
})

const emit = defineEmits(['view', 'edit', 'delete'])

const q = ref('')
const status = ref('all')
const statusTabs = ['all', 'Active', 'In Progress', 'Resolved', 'On Hold']

function statusTabVariant(tab) {
  if (tab === 'all') return 'chip-variant-all'
  if (tab === 'Active') return 'chip-variant-active'
  if (tab === 'In Progress') return 'chip-variant-inprog'
  if (tab === 'Resolved') return 'chip-variant-resolved'
  if (tab === 'On Hold') return 'chip-variant-onhold'
  return ''
}

const sortKey = ref('reported_at')
const sortDir = ref('desc')
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

const sourceRows = computed(() => {
  const base = (props.items?.length ? props.items : [])
  return base.filter(i => {
    const type = i?.entry_type || 'item';
    return type !== 'message';
  });
})

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

const filteredSorted = computed(() => {
  const base = status.value !== 'all'
    ? sourceRows.value.filter(r => (r.current_status ?? r.status) === status.value)
    : sourceRows.value

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

const page = ref(0)
const perPage = ref(10)
const total = computed(() => filteredSorted.value.length)
const pageCount = computed(() => Math.max(1, Math.ceil(total.value / perPage.value)))
const pagedRows = computed(() => {
  const start = page.value * perPage.value
  return filteredSorted.value.slice(start, start + perPage.value)
})

loadState()

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

function onEdit(row)   { emit('edit', row.id) }
function onDelete(row) { emit('delete', row) }

function badgeClasses(s) {
  if (s === 'Active')       return 'badge-danger'
  if (s === 'In Progress')  return 'badge-warning'
  if (s === 'Resolved')     return 'badge-success'
  if (s === 'On Hold')      return 'badge-hold'
  return 'badge-neutral'
}

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

function exportToExcel() {
  const ids = pagedRows.value.map(row => row.id);
  if (ids.length === 0) {
    alert("No visible failures to export.");
    return;
  }
  const url = `/api/v1/failures/logs/export_excel/?ids=${ids.join(',')}`;
  window.open(url, '_blank');
}

function exportToPdf() {
  const ids = pagedRows.value.map(row => row.id);
  if (ids.length === 0) {
    alert("No visible failures to export.");
    return;
  }
  const url = `/api/v1/failures/logs/export_pdf/?ids=${ids.join(',')}`;
  window.open(url, '_blank');
}
</script>

<template>
  <div class="space-y-4">
    <div v-if="showHeader">
      <h2 class="text-xl font-semibold leading-tight">Recent Failure Logs</h2>
    </div>

    <div class="rounded-2xl border-app bg-card text-app p-4">
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
        <input v-model="q" type="text" placeholder="Search..." class="h-10 w-full sm:w-64 max-w-full min-w-0 rounded-lg border-app bg-card text-app px-3 text-sm"/>
      </div>

      <div class="overflow-x-auto">
        <table class="min-w-full text-sm">
          <thead class="bg-card">
            <tr>
              <th class="text-center font-semibold text-app px-3 py-1.5 cursor-pointer select-none" :aria-sort="sortKey==='id' ? (sortDir==='asc'?'ascending':'descending') : 'none'" @click="setSort('id')">
                <div class="inline-flex items-center gap-1">EV ID <span v-if="sortKey==='id'">{{ sortDir==='asc' ? '▲' : '▼' }}</span></div>
              </th>
              <th class="text-center font-semibold text-app px-3 py-1.5 cursor-pointer select-none" :aria-sort="sortKey==='circuit' ? (sortDir==='asc'?'ascending':'descending') : 'none'" @click="setSort('circuit')">
                <div class="inline-flex items-center gap-1">Circuit <span v-if="sortKey==='circuit'">{{ sortDir==='asc' ? '▲' : '▼' }}</span></div>
              </th>
              <th class="text-center font-semibold text-app px-3 py-1.5 cursor-pointer select-none" :aria-sort="sortKey==='station' ? (sortDir==='asc'?'ascending':'descending') : 'none'" @click="setSort('station')">
                <div class="inline-flex items-center gap-1">Station <span v-if="sortKey==='station'">{{ sortDir==='asc' ? '▲' : '▼' }}</span></div>
              </th>
              <th class="text-center font-semibold text-app px-3 py-1.5 cursor-pointer select-none" :aria-sort="sortKey==='section' ? (sortDir==='asc'?'ascending':'descending') : 'none'" @click="setSort('section')">
                <div class="inline-flex items-center gap-1">Section <span v-if="sortKey==='section'">{{ sortDir==='asc' ? '▲' : '▼' }}</span></div>
              </th>
              <th class="text-center font-semibold text-app px-3 py-1.5 cursor-pointer select-none" :aria-sort="sortKey==='reported_at' ? (sortDir==='asc'?'ascending':'descending') : 'none'" @click="setSort('reported_at')">
                <div class="inline-flex items-center gap-1">Reported <span v-if="sortKey==='reported_at'">{{ sortDir==='asc' ? '▲' : '▼' }}</span></div>
              </th>
              <th v-if="showRowActions" class="text-center font-semibold text-app px-3 py-1.5">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="!loading && filteredSorted.length === 0">
              <td :colspan="showRowActions ? 6 : 5" class="px-4 py-6 text-center text-muted">No recent failures</td>
            </tr>
            <tr v-if="!loading" v-for="(r, i) in pagedRows" :key="r.id ?? i" class="cursor-pointer" role="button" tabindex="0" @click="openDetails(r)" @keydown.enter.space="emit('view', r)" @mouseenter="hoveredIndex = i" @mouseleave="hoveredIndex = -1" :style="{ backgroundColor: rowBg(r.current_status ?? r.status, hoveredIndex === i) }">
              <td class="px-3 py-1.5 text-center rounded-l-xl"><div class="truncate">{{ (r.fail_id ?? r.id)?.split('-').pop() ?? '—' }}</div></td>
              <td class="px-3 py-1.5 text-center"><div class="truncate">{{ r.circuit?.circuit_id ?? r.circuit ?? '—' }}</div></td>
              <td class="px-3 py-1.5 text-center"><div class="truncate">{{ r.station?.code ?? r.station ?? '—' }}</div></td>
              <td class="px-3 py-1.5 text-center"><div class="truncate">{{ r.section?.name ?? r.section ?? '—' }}</div></td>
              <td class="px-3 py-1.5 text-center">
                <span :title="fmt(r.reported_at ?? r.reportedAt)">{{ timeAgo(r.reported_at ?? r.reportedAt) }}</span>
              </td>
             <td v-if="showRowActions" class="px-3 py-1.5 text-center rounded-r-xl">
                <div class="inline-flex items-center justify-center gap-2">
                    <button class="btn-ghost border-app rounded-md hover-primary p-2" aria-label="Notify" title="Notify" @click.stop="$emit('notify', r)">
                        <Bell class="w-4 h-4" />
                    </button>
                    <button class="btn-ghost border-app rounded-md hover-primary p-2" aria-label="Edit" title="Edit" @click.stop="$emit('edit', r.id)">
                        <Pencil class="w-4 h-4" />
                    </button>
                    <button class="btn-ghost border-app rounded-md hover-primary p-2" aria-label="Delete" title="Delete" @click.stop="onDelete(r)">
                        <Trash2 class="w-4 h-4" />
                    </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>

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
              <button class="btn-ghost border-app rounded-md hover-primary p-2 disabled:opacity-40" :disabled="page === 0" aria-label="Previous page" title="Previous" @click="prevPage">
                <ChevronLeft class="w-4 h-4" />
              </button>
              <span class="text-sm tabular-nums">{{ page + 1 }} / {{ pageCount }}</span>
              <button class="btn-ghost border-app rounded-md hover-primary p-2 disabled:opacity-40" :disabled="page >= pageCount - 1" aria-label="Next page" title="Next" @click="nextPage">
                <ChevronRight class="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </div>

      <div v-if="showBottomActions" class="flex justify-center gap-3 px-3 py-5">
        <button
          class="btn-ghost border-app rounded-md hover-primary p-2"
          aria-label="Export Excel"
          title="Export Excel"
          @click="exportToExcel"
        >
          <FileSpreadsheet class="w-4 h-4" />
        </button>
        <button
          class="btn-ghost border-app rounded-md hover-primary p-2"
          aria-label="Export PDF"
          title="Export PDF"
          @click="exportToPdf"
        >
          <FileText class="w-4 h-4" />
        </button>
      </div>
    </div>
    <NotificationModal v-model="isNotifyModalOpen" :failure="failureToNotify" />
    <FailureDetailsDrawer v-model="drawerOpen" :item="activeItem" :show-actions="false" />
  </div>
</template>