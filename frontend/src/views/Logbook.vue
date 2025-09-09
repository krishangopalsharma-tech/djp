<script setup>
import { ref, computed, onMounted } from 'vue'
import DataTable from '@/components/DataTable.vue'
import FailureDetailsDrawer from '@/components/FailureDetailsDrawer.vue'
import SearchSelect from '@/components/form/SearchSelect.vue' // <-- Add this import
import { useFailureStore } from '@/stores/failures'
import { useInfrastructureStore } from '@/stores/infrastructure'
import { Bell, Pencil, Trash2 } from 'lucide-vue-next'

// --- Store setup ---
const failureStore = useFailureStore()
const infrastructureStore = useInfrastructureStore()

// --- Local UI State for Filters and Sorting ---
const drawerOpen = ref(false)
const activeItem = ref(null)
const query = ref('')
const selectedCircuits = ref([])
const selectedSections = ref([])
const selectedStations = ref([])
const selectedSupervisors = ref([])
const selectedStatuses = ref([])
const sortKey = ref('reported_at')
const sortDir = ref('desc')

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

// --- Filtering and Sorting Logic ---
const filteredRows = computed(() => {
  const q = query.value.trim().toLowerCase()
  return failureStore.failures.filter(row => {
    // Text search
    const inQuery = q ? JSON.stringify(row).toLowerCase().includes(q) : true
    // Filter checks
    const inCircuits = selectedCircuits.value.length ? selectedCircuits.value.includes(row.circuit.id) : true
    const inSections = selectedSections.value.length ? selectedSections.value.includes(row.section.id) : true
    const inStations = selectedStations.value.length ? selectedStations.value.includes(row.station.id) : true
    const inSupervisors = selectedSupervisors.value.length ? selectedSupervisors.value.includes(row.assigned_to.id) : true
    const inStatuses = selectedStatuses.value.length ? selectedStatuses.value.includes(row.current_status) : true

    return inQuery && inCircuits && inSections && inStations && inSupervisors && inStatuses
  })
})

const sortedRows = computed(() => {
  const data = [...filteredRows.value]
  const key = sortKey.value
  const dir = sortDir.value === 'asc' ? 1 : -1

  return data.sort((a, b) => {
    let valA, valB
    // Handle nested object access for sorting
    switch (key) {
        case 'circuit': valA = a.circuit?.circuit_id; valB = b.circuit?.circuit_id; break;
        case 'station': valA = a.station?.name; valB = b.station?.name; break;
        case 'section': valA = a.section?.name; valB = b.section?.name; break;
        case 'assigned_to': valA = a.assigned_to?.name; valB = b.assigned_to?.name; break;
        default: valA = a[key]; valB = b[key];
    }
    if (valA > valB) return 1 * dir
    if (valA < valB) return -1 * dir
    return 0
  })
})

function toggleSort(key) {
  if (sortKey.value === key) {
    sortDir.value = sortDir.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortKey.value = key
    sortDir.value = 'desc'
  }
}

// --- Columns for the DataTable ---
const columns = [
  { key: 'reported_at', label: 'Reported', sortable: true },
  { key: 'fail_id', label: 'Event ID', sortable: true },
  { key: 'circuit', label: 'Circuit', sortable: true },
  { key: 'station', label: 'Station', sortable: true },
  { key: 'section', label: 'Section', sortable: true },
  { key: 'assigned_to', label: 'Assigned', sortable: true },
  { key: 'current_status', label: 'Status', sortable: true },
  { key: 'actions', label: 'Actions', sortable: false, align: 'text-center' },
]

// --- Methods ---
function openDetails(row) {
  activeItem.value = row
  drawerOpen.value = true
}

function badgeClasses(status) {
    if (status === 'Resolved') return 'badge-success'
    if (status === 'Active') return 'badge-danger'
    if (status === 'In Progress') return 'badge-warning'
    if (status === 'On Hold') return 'badge-hold'
    return 'badge-neutral'
}
</script>

<template>
  <div class="space-y-4">
    <h2 class="text-2xl font-semibold text-center">Logbook</h2>

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

    <div v-if="loading" class="rounded-2xl border-app bg-card p-6 text-center text-muted">
      Loading logbook entries...
    </div>
    <div v-else-if="error" class="rounded-2xl border-app bg-card p-6 text-center text-red-500">
      {{ error }}
    </div>
    <div v-else class="rounded-2xl border-app bg-card p-4 shadow-card">
      <DataTable
        :columns="columns"
        :rows="sortedRows"
        :sort-key="sortKey"
        :sort-dir="sortDir"
        @sort="toggleSort"
        @rowclick="openDetails"
      >
        <template #reported_at="{ row }">
          {{ new Date(row.reported_at).toLocaleString() }}
        </template>
        <template #circuit="{ row }">
          {{ row.circuit }}
        </template>
        <template #station="{ row }">
          {{ row.station }}
        </template>
        <template #section="{ row }">
          {{ row.section }}
        </template>
        <template #assigned_to="{ row }">
          {{ row.assigned_to }}
        </template>
        <template #current_status="{ row }">
          <span class="badge" :class="badgeClasses(row.current_status)">
            {{ row.current_status }}
          </span>
        </template>
        <template #actions="{ row }">
          <div class="flex items-center justify-center gap-1.5">
            <button class="btn-ghost border-app rounded-md hover-primary p-2" title="Notify" @click.stop><Bell class="w-4 h-4" /></button>
            <button class="btn-ghost border-app rounded-md hover-primary p-2" title="Edit" @click.stop><Pencil class="w-4 h-4" /></button>
            <button class="btn-ghost border-app rounded-md hover-primary p-2" title="Delete" @click.stop><Trash2 class="w-4 h-4" /></button>
          </div>
        </template>
      </DataTable>
    </div>
  </div>
  <FailureDetailsDrawer v-model="drawerOpen" :item="activeItem" />
</template>