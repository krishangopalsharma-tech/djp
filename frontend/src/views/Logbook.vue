<script setup>
import { ref, computed, watch, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useDebounce } from '@/composables/useDebounce';
import { useLogbookStore } from '@/stores/logbook';
// --- START OF FIX ---
import { useInfrastructureStore } from '@/stores/infrastructure';
// --- END OF FIX ---
import { useFailureStore } from '@/stores/failures';
import DataTable from '@/components/DataTable.vue';
import FailureDetailsDrawer from '@/components/FailureDetailsDrawer.vue';
import Spinner from '@/components/ui/Spinner.vue';
import SearchSelect from '@/components/form/SearchSelect.vue';
import { Bell, Pencil, Trash2, FileDown, FileText, ChevronLeft, ChevronRight, ChevronsLeft, ChevronsRight } from 'lucide-vue-next';

// --- Store setup ---
const logbookStore = useLogbookStore();
// --- START OF FIX ---
const infrastructureStore = useInfrastructureStore();
// --- END OF FIX ---
const failureStore = useFailureStore(); // Keep for archive action
const router = useRouter();

// --- UI State ---
const drawerOpen = ref(false);
const activeItem = ref(null);
const isArchiveModalOpen = ref(false);
const failureToArchive = ref(null);
const archiveReason = ref('');

// --- Filtering, Sorting, and Pagination State ---
const filters = ref({
  query: '',
  circuits: [],
  sections: [],
  stations: [],
  supervisors: [],
  statuses: [],
  sortKey: 'reported_at',
  sortDir: 'desc',
  page: 1,
  rowsPerPage: 20,
});

// --- Data Fetching ---
onMounted(() => {
  fetchData(); // Initial data load
  // Fetch data for filter dropdowns
  infrastructureStore.fetchCircuits();
  infrastructureStore.fetchSections();
  infrastructureStore.fetchStations();
  infrastructureStore.fetchSupervisors();
});

const fetchData = useDebounce(() => {
    // Construct params object for the API call
    const params = {
        query: filters.value.query,
        'circuits[]': filters.value.circuits,
        'sections[]': filters.value.sections,
        'stations[]': filters.value.stations,
        'supervisors[]': filters.value.supervisors,
        'statuses[]': filters.value.statuses,
        sortKey: filters.value.sortKey,
        sortDir: filters.value.sortDir,
        page: filters.value.page,
        rowsPerPage: filters.value.rowsPerPage,
    };
    logbookStore.fetchLogbookData(params);
}, 300); // Debounce API calls

watch(filters, fetchData, { deep: true });

// --- Computed Data for UI ---
const loading = computed(() => logbookStore.loading);
const error = computed(() => logbookStore.error);
const paginatedRows = computed(() => logbookStore.failures);
const totalPages = computed(() => logbookStore.num_pages);
const currentPage = computed({
    get: () => filters.value.page,
    set: (val) => { filters.value.page = val; }
});

// --- Options for Filter Dropdowns ---
const circuitOptions = computed(() => infrastructureStore.circuits.map(c => ({ label: `${c.circuit_id} (${c.name})`, value: c.id })));
const sectionOptions = computed(() => infrastructureStore.sections.map(s => ({ label: s.name, value: s.id })));
const stationOptions = computed(() => infrastructureStore.stations.map(s => ({ label: s.name, value: s.id })));
const supervisorOptions = computed(() => infrastructureStore.supervisors.map(s => ({ label: s.name, value: s.id })));
const statusOptions = computed(() => ([
    { label: 'Active', value: 'Active' }, { label: 'In Progress', value: 'In Progress' },
    { label: 'Resolved', value: 'Resolved' }, { label: 'On Hold', value: 'On Hold' },
]));

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
];

// --- Methods ---
function toggleSort(key) {
  if (filters.value.sortKey === key) {
    filters.value.sortDir = filters.value.sortDir === 'asc' ? 'desc' : 'asc';
  } else {
    filters.value.sortKey = key;
    filters.value.sortDir = 'desc';
  }
}

function goToFirstPage() { filters.value.page = 1; }
function goToLastPage() { filters.value.page = totalPages.value; }
function goToNextPage() { if (filters.value.page < totalPages.value) filters.value.page++; }
function goToPreviousPage() { if (filters.value.page > 1) filters.value.page--; }

function openDetails(row) { activeItem.value = row; drawerOpen.value = true; }
function editFailure(row) { router.push(`/failures/edit/${row.id}`); }
function openArchiveModal(row) { failureToArchive.value = row; isArchiveModalOpen.value = true; archiveReason.value = ''; }
async function confirmArchive() {
  if (failureToArchive.value) {
    await failureStore.archiveFailure(failureToArchive.value.id, archiveReason.value);
    failureToArchive.value = null;
    isArchiveModalOpen.value = false;
    fetchData(); // Re-fetch data after archiving
  }
}
function formatDuration(start, end) {
  if (!start || !end) return '—';
  const diff = new Date(end) - new Date(start);
  if (diff < 0) return '—';
  const minutes = Math.floor(diff / 60000);
  if (minutes < 60) return `${minutes}m`;
  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;
  return `${hours}h ${mins}m`;
}
function badgeClasses(status) {
    if (status === 'Resolved') return 'badge-success';
    if (status === 'Active') return 'badge-danger';
    if (status === 'In Progress') return 'badge-warning';
    if (status === 'On Hold') return 'badge-hold';
    if (status === 'Information') return 'badge-neutral';
    return 'badge-neutral';
}
</script>

<template>
  <div class="space-y-4">
    <div class="text-center">
      <h2 class="text-2xl font-semibold">Logbook</h2>
    </div>

    <div class="sticky top-0 z-10 bg-app py-4 card">
       <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
        <input v-model="filters.query" type="search" placeholder="Search anything..." class="h-11 w-full rounded-lg border-app bg-card text-app px-3 text-sm" />
        <SearchSelect v-model="filters.circuits" :options="circuitOptions" placeholder="Filter by Circuit" multiple />
        <SearchSelect v-model="filters.sections" :options="sectionOptions" placeholder="Filter by Section" multiple />
        <SearchSelect v-model="filters.stations" :options="stationOptions" placeholder="Filter by Station" multiple />
        <SearchSelect v-model="filters.supervisors" :options="supervisorOptions" placeholder="Filter by Supervisor" multiple />
        <SearchSelect v-model="filters.statuses" :options="statusOptions" placeholder="Filter by Status" multiple />
      </div>
    </div>

    <div v-if="loading" class="text-center p-6"><Spinner /></div>
    <div v-else-if="error" class="card p-6 text-center text-red-500">{{ error }}</div>

    <div v-else>
      <div class="card p-4">
        <DataTable
          :columns="columns"
          :rows="paginatedRows"
          :sort-key="filters.sortKey"
          :sort-dir="filters.sortDir"
          @sort="toggleSort"
          @rowclick="openDetails"
        >
          <template #body-cell-comp="{ row, column }">
            <tr :class="{ 'opacity-60': row.is_archived }">
              <component :is="column.cell" :row="row" />
            </tr>
          </template>
          <template #reported_at="{ row }">{{ new Date(row.reported_at).toLocaleString() }}</template>
          <template #resolved_at="{ row }">{{ row.resolved_at ? new Date(row.resolved_at).toLocaleString() : '–' }}</template>
          <template #duration="{ row }">{{ formatDuration(row.reported_at, row.resolved_at) }}</template>
          <template #circuit="{ row }">{{ row.circuit?.name || '–' }}</template>
          <template #station="{ row }">{{ row.station?.name || '–' }}</template>
          <template #section="{ row }">{{ row.section?.name || '–' }}</template>
          <template #assigned_to="{ row }">{{ row.assigned_to?.name || '–' }}</template>
          <template #current_status="{ row }"><span class="badge" :class="badgeClasses(row.current_status)">{{ row.current_status }}</span></template>
          <template #actions="{ row }">
            <div class="flex items-center justify-center gap-1.5">
              <button class="btn-ghost border-app rounded-md hover-primary p-2" title="Notify" @click.stop disabled><Bell class="w-4 h-4" /></button>
              <button class="btn-ghost border-app rounded-md hover-primary p-2" title="Edit" @click.stop="editFailure(row)"><Pencil class="w-4 h-4" /></button>
              <button class="btn-ghost border-app rounded-md hover-primary p-2" title="Archive" @click.stop="openArchiveModal(row)"><Trash2 class="w-4 h-4" /></button>
            </div>
          </template>
        </DataTable>
      </div>
        
      <div class="mt-4 flex items-center justify-between">
        <div class="flex items-center justify-center gap-2 p-2 rounded-lg">
          <button class="btn btn-outline btn-sm gap-2"><FileDown class="w-4 h-4" /><span>Export CSV</span></button>
          <button class="btn btn-outline btn-sm gap-2"><FileText class="w-4 h-4" /><span>Export PDF</span></button>
        </div>
        <div class="flex items-center justify-end gap-2 p-2 rounded-lg">
          <button @click="goToFirstPage" :disabled="filters.page === 1" class="btn-ghost p-2" title="First"><ChevronsLeft class="w-4 h-4" /></button>
          <button @click="goToPreviousPage" :disabled="filters.page === 1" class="btn-ghost p-2" title="Previous"><ChevronLeft class="w-4 h-4" /></button>
          <span class="text-sm text-muted">Page {{ filters.page }} of {{ totalPages }}</span>
          <button @click="goToNextPage" :disabled="filters.page >= totalPages" class="btn-ghost p-2" title="Next"><ChevronRight class="w-4 h-4" /></button>
          <button @click="goToLastPage" :disabled="filters.page >= totalPages" class="btn-ghost p-2" title="Last"><ChevronsRight class="w-4 h-4" /></button>
        </div>
      </div>
    </div>

    <FailureDetailsDrawer v-model="drawerOpen" :item="activeItem" />

    <div v-if="isArchiveModalOpen" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div class="bg-card rounded-lg p-6 shadow-xl w-full max-w-md">
        <h3 class="text-lg font-bold">Confirm Archival</h3>
        <p class="mt-2">
          Are you sure you want to archive failure log
          <span class="font-semibold">{{ failureToArchive?.fail_id }}</span>?
        </p>
        <div class="mt-4">
          <label for="archiveReason" class="block text-sm font-medium text-app">Reason for archiving</label>
          <textarea v-model="archiveReason" id="archiveReason" rows="3" class="field-textarea mt-1"></textarea>
        </div>
        <div class="mt-6 flex justify-end gap-3">
          <button @click="isArchiveModalOpen = false" class="btn btn-outline">Cancel</button>
          <button @click="confirmArchive" class="btn btn-danger">Archive</button>
        </div>
      </div>
    </div>
  </div>
</template>