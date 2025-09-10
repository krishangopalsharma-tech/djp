<script setup>
import { ref, computed, onMounted } from 'vue'
import DataTable from '@/components/DataTable.vue'
import FailureDetailsDrawer from '@/components/FailureDetailsDrawer.vue'
import FailureCard from '@/components/FailureCard.vue'
import KanbanColumn from '@/components/KanbanColumn.vue'
import TimelineItem from '@/components/TimelineItem.vue'
import Spinner from '@/components/ui/Spinner.vue'
import SearchSelect from '@/components/form/SearchSelect.vue'
import { Bell, Pencil, Trash2, FileDown, FileText, ChevronLeft, ChevronRight, ChevronsLeft, ChevronsRight } from 'lucide-vue-next'
import { useFailureStore } from '@/stores/failures'
import { useInfrastructureStore } from '@/stores/infrastructure'

// --- Store setup ---
const failureStore = useFailureStore()
const infrastructureStore = useInfrastructureStore()

// --- UI State ---
const view = ref('table') // table | cards | board | timeline
const drawerOpen = ref(false)
const activeItem = ref(null)

// --- Filtering, Sorting, and Pagination State ---
const query = ref('')
const selectedCircuits = ref([])
const selectedSections = ref([])
const selectedStations = ref([])
const selectedSupervisors = ref([])
const selectedStatuses = ref([])
const sortKey = ref('reported_at')
const sortDir = ref('desc')
const currentPage = ref(1)
const rowsPerPage = ref(20)

// --- Data Fetching ---
onMounted(() => {
  failureStore.fetchFailures()
  infrastructureStore.fetchCircuits()
  infrastructureStore.fetchSections()
  infrastructureStore.fetchStations()
  infrastructureStore.fetchSupervisors()
})

// --- Computed Data for UI ---
const loading = computed(() => failureStore.loading)
const error = computed(() => failureStore.error)

// --- Options for Filter Dropdowns ---
const circuitOptions = computed(() => infrastructureStore.circuits.map(c => ({ label: `${c.circuit_id} (${c.name})`, value: c.id })))
const sectionOptions = computed(() => infrastructureStore.sections.map(s => ({ label: s.name, value: s.id })))
const stationOptions = computed(() => infrastructureStore.stations.map(s => ({ label: s.name, value: s.id })))
const supervisorOptions = computed(() => infrastructureStore.supervisors.map(s => ({ label: s.name, value: s.id })))
const statusOptions = computed(() => ([
    { label: 'Active', value: 'Active' }, { label: 'In Progress', value: 'In Progress' },
    { label: 'Resolved', value: 'Resolved' }, { label: 'On Hold', value: 'On Hold' },
]))

// --- Filtering & Sorting Logic ---
const filteredRows = computed(() => {
  const q = query.value.trim().toLowerCase()
  return failureStore.failures.filter(row => {
    if (!row) return false;
    const inQuery = q ? JSON.stringify(row).toLowerCase().includes(q) : true
    const inCircuits = selectedCircuits.value.length ? selectedCircuits.value.includes(row.circuit?.id) : true
    const inSections = selectedSections.value.length ? selectedSections.value.includes(row.section?.id) : true
    const inStations = selectedStations.value.length ? selectedStations.value.includes(row.station?.id) : true
    const inSupervisors = selectedSupervisors.value.length ? selectedSupervisors.value.includes(row.assigned_to?.id) : true
    const inStatuses = selectedStatuses.value.length ? selectedStatuses.value.includes(row.current_status) : true
    return inQuery && inCircuits && inSections && inStations && inSupervisors && inStatuses
  })
})

const sortedRows = computed(() => {
    const data = [...filteredRows.value];
    if (!sortKey.value) return data;

    return data.sort((a, b) => {
        let valA = a[sortKey.value];
        let valB = b[sortKey.value];

        // Handle nested properties for sorting
        if (sortKey.value === 'circuit') { valA = a.circuit; valB = b.circuit; }
        if (sortKey.value === 'station') { valA = a.station; valB = b.station; }
        if (sortKey.value === 'section') { valA = a.section; valB = b.section; }
        if (sortKey.value === 'assigned_to') { valA = a.assigned_to; valB = b.assigned_to; }
        
        const dir = sortDir.value === 'asc' ? 1 : -1;
        if (valA > valB) return 1 * dir;
        if (valA < valB) return -1 * dir;
        return 0;
    });
});


const totalPages = computed(() => Math.ceil(sortedRows.value.length / rowsPerPage.value))
const paginatedRows = computed(() => {
  const start = (currentPage.value - 1) * rowsPerPage.value
  const end = start + rowsPerPage.value
  return sortedRows.value.slice(start, end)
})

// --- Methods ---
function toggleSort(key) {
  if (sortKey.value === key) {
    sortDir.value = sortDir.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortKey.value = key
    sortDir.value = 'desc'
  }
}

function openDetails(row) {
  activeItem.value = row
  drawerOpen.value = true
}

function formatDuration(start, end) {
  if (!start || !end) return '–'
  const diff = new Date(end) - new Date(start)
  if (diff < 0) return '–'
  const minutes = Math.floor(diff / 60000)
  if (minutes < 60) return `${minutes}m`
  const hours = Math.floor(minutes / 60)
  const mins = minutes % 60
  return `${hours}h ${mins}m`
}

const columns = [
  { key: 'reported_at', label: 'Reported', sortable: true },
  { key: 'resolved_at', label: 'Resolved', sortable: true },
  { key: 'duration',    label: 'Duration', sortable: false, align: 'text-center' },
  { key: 'fail_id',     label: 'Event ID', sortable: true },
  { key: 'circuit',     label: 'Circuit', sortable: true },
  { key: 'station',     label: 'Station', sortable: true },
  { key: 'section',     label: 'Section', sortable: true },
  { key: 'assigned_to', label: 'Assigned', sortable: true },
  { key: 'current_status', label: 'Status', sortable: true },
  { key: 'actions',     label: 'Actions', sortable: false, align: 'text-center', width: '120px' },
]

function badgeClasses(status) {
    if (status === 'Resolved') return 'badge-success'
    if (status === 'Active') return 'badge-danger'
    if (status === 'In Progress') return 'badge-warning'
    if (status === 'On Hold') return 'badge-hold'
    return 'badge-neutral'
}

// --- Pagination Methods ---
function goToFirstPage() { currentPage.value = 1 }
function goToLastPage() { currentPage.value = totalPages.value }
function goToNextPage() { if (currentPage.value < totalPages.value) currentPage.value++ }
function goToPreviousPage() { if (currentPage.value > 1) currentPage.value-- }
</script>

<template>
  <div class="space-y-4">
    <div class="grid grid-cols-1 gap-3 md:grid-cols-3 md:items-center">
      <div></div>
      <h2 class="text-2xl font-semibold text-center">Logbook</h2>
      <div class="md:justify-self-end">
        <div class="chip-group">
          <button v-for="m in ['table','cards','board','timeline']" :key="m" class="chip capitalize" :class="view === m ? 'selected-primary' : 'text-app hover-primary'" @click="view = m">
            {{ m }}
          </button>
        </div>
      </div>
    </div>

    <div class="sticky top-0 z-10 bg-app py-4">
       <div class="flex flex-wrap items-center gap-4">
        <input v-model="query" type="search" placeholder="Search anything..." class="h-11 w-full rounded-lg border-app bg-card text-app px-3 text-sm shadow-card md:w-auto" />
        <SearchSelect v-model="selectedCircuits" :options="circuitOptions" placeholder="Filter by Circuit" multiple class="shadow-card" />
        <SearchSelect v-model="selectedSections" :options="sectionOptions" placeholder="Filter by Section" multiple class="shadow-card" />
        <SearchSelect v-model="selectedStations" :options="stationOptions" placeholder="Filter by Station" multiple class="shadow-card" />
        <SearchSelect v-model="selectedSupervisors" :options="supervisorOptions" placeholder="Filter by Supervisor" multiple class="shadow-card" />
        <SearchSelect v-model="selectedStatuses" :options="statusOptions" placeholder="Filter by Status" multiple class="shadow-card" />
      </div>
    </div>

    <div v-if="loading" class="text-center p-6"><Spinner /></div>
    <div v-else-if="error" class="rounded-2xl border-app bg-card p-6 text-center text-red-500">{{ error }}</div>

    <div v-else>
      <div v-if="view === 'table'" class="rounded-2xl border-app bg-card p-4 shadow-card">
        <DataTable
          :columns="columns"
          :rows="paginatedRows"
          :sort-key="sortKey"
          :sort-dir="sortDir"
          @sort="toggleSort"
          @rowclick="openDetails"
        >
          <template #reported_at="{ row }">{{ new Date(row.reported_at).toLocaleString() }}</template>
          <template #resolved_at="{ row }">{{ row.resolved_at ? new Date(row.resolved_at).toLocaleString() : '–' }}</template>
          <template #duration="{ row }">{{ formatDuration(row.reported_at, row.resolved_at) }}</template>
          <template #current_status="{ row }"><span class="badge" :class="badgeClasses(row.current_status)">{{ row.current_status }}</span></template>
          <template #actions="{ row }">
            <div class="flex items-center justify-center gap-1.5">
              <button class="btn-ghost border-app rounded-md hover-primary p-2" title="Notify" @click.stop><Bell class="w-4 h-4" /></button>
              <button class="btn-ghost border-app rounded-md hover-primary p-2" title="Edit" @click.stop><Pencil class="w-4 h-4" /></button>
              <button class="btn-ghost border-app rounded-md hover-primary p-2" title="Delete" @click.stop><Trash2 class="w-4 h-4" /></button>
            </div>
          </template>
        </DataTable>
      </div>

      <div v-if="view === 'cards'" class="text-center p-6 text-muted">Cards View Coming Soon</div>
      <div v-if="view === 'board'" class="text-center p-6 text-muted">Board View Coming Soon</div>
      <div v-if="view === 'timeline'" class="text-center p-6 text-muted">Timeline View Coming Soon</div>
      
      <div v-if="view === 'table'" class="sticky bottom-0 bg-app py-4 flex items-center justify-between">
        <div class="flex items-center justify-center gap-2 p-2 rounded-lg">
          <button class="chip capitalize text-app hover-primary gap-2"><FileDown class="w-4 h-4" /><span>Export CSV</span></button>
          <button class="chip capitalize text-app hover-primary gap-2"><FileText class="w-4 h-4" /><span>Export PDF</span></button>
        </div>
        <div class="flex items-center justify-end gap-2 p-2 rounded-lg shadow-card">
          <button @click="goToFirstPage" :disabled="currentPage === 1" class="btn-ghost p-2" title="First"><ChevronsLeft class="w-4 h-4" /></button>
          <button @click="goToPreviousPage" :disabled="currentPage === 1" class="btn-ghost p-2" title="Previous"><ChevronLeft class="w-4 h-4" /></button>
          <span class="text-sm text-muted">Page {{ currentPage }} of {{ totalPages }}</span>
          <button @click="goToNextPage" :disabled="currentPage >= totalPages" class="btn-ghost p-2" title="Next"><ChevronRight class="w-4 h-4" /></button>
          <button @click="goToLastPage" :disabled="currentPage >= totalPages" class="btn-ghost p-2" title="Last"><ChevronsRight class="w-4 h-4" /></button>
        </div>
      </div>
    </div>

    <FailureDetailsDrawer v-model="drawerOpen" :item="activeItem" />
  </div>
</template>