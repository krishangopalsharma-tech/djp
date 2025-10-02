<script setup>
import { reactive, ref, computed, onMounted } from 'vue'
import { useInfrastructureStore } from '@/stores/infrastructure.js'
import { useUIStore } from '@/stores/ui'
// Wrench and Pencil are no longer needed
import { Trash2 } from 'lucide-vue-next';

const infrastructureStore = useInfrastructureStore()
const uiStore = useUIStore()

const depotOptions = computed(() =>
  infrastructureStore.depots.map(d => ({ value: d.id, label: d.name + (d.code ? ` (${d.code})` : '') }))
)
const stations = computed(() => infrastructureStore.stations)

// --- Sorting State ---
const sortKey = ref('name');
const sortDir = ref('asc');

const sortedStations = computed(() => {
  const data = [...stations.value];
  data.sort((a, b) => {
    let valA = a[sortKey.value];
    let valB = b[sortKey.value];
    const modifier = sortDir.value === 'asc' ? 1 : -1;

    // Handle nested properties like depot_name
    if (sortKey.value === 'depot_name') {
        valA = a.depot_name;
        valB = b.depot_name;
    }

    if (valA < valB) return -1 * modifier;
    if (valA > valB) return 1 * modifier;
    return 0;
  });
  return data;
});

function toggleSort(key) {
  if (sortKey.value === key) {
    sortDir.value = sortDir.value === 'asc' ? 'desc' : 'asc';
  } else {
    sortKey.value = key;
    sortDir.value = 'asc';
  }
}


// --- State for file upload ---
const selectedFile = ref(null)
const fileInput = ref(null)

onMounted(() => {
  if (infrastructureStore.depots.length === 0) {
    infrastructureStore.fetchDepots()
  }
  infrastructureStore.fetchStations()
})

// Form for creating a new station
const newStation = reactive({
  name: '',
  code: '',
  category: '',
  depot: null,
})

function addStation() {
  if (!newStation.name || !newStation.depot) {
    uiStore.pushToast({type: 'error', title: 'Missing Fields', message: 'Please provide a station name and select a depot.'})
    return
  }
  infrastructureStore.addStation({ ...newStation })
  // Reset the form
  newStation.name = ''
  newStation.code = ''
  newStation.category = ''
  newStation.depot = null
}

// --- Edit Modal State ---
const isEditModalOpen = ref(false);
const stationToEdit = ref(null);

function openEditModal(station) {
  stationToEdit.value = { ...station }; // Create a copy to edit
  isEditModalOpen.value = true;
}

async function saveStationChanges() {
  if (!stationToEdit.value) return;
  await infrastructureStore.updateStation(stationToEdit.value.id, stationToEdit.value);
  isEditModalOpen.value = false;
  stationToEdit.value = null;
}


// --- Delete confirmation modal state ---
const isDeleteModalOpen = ref(false);
const stationToDelete = ref(null);

function openDeleteModal(station) {
  stationToDelete.value = station;
  isDeleteModalOpen.value = true;
}

async function confirmDelete() {
  if (!stationToDelete.value) return;
  await infrastructureStore.removeStation(stationToDelete.value.id);
  isDeleteModalOpen.value = false;
  stationToDelete.value = null;
}

// --- File Upload Logic ---
function handleFileSelect(event) {
  const target = event.target;
  if (target.files && target.files[0]) {
    selectedFile.value = target.files[0];
  }
}

function triggerFileInput() {
  fileInput.value?.click();
}

async function handleFileUpload() {
  if (!selectedFile.value) {
    alert('Please select a file to upload.');
    return;
  }
  await infrastructureStore.uploadStationsFile(selectedFile.value);
  selectedFile.value = null;
  if (fileInput.value) fileInput.value.value = '';
}


// --- Logic for the "Manage Equipment" Modal ---
const clone = (o) => JSON.parse(JSON.stringify(o))
const showModal = ref(false)
const selectedStation = ref(null)
const tempEquipments = reactive([])
const originalEquipments = ref([]) // To compare for changes


function openManage(station) {
  selectedStation.value = station
  const equipments = station.equipments || []
  originalEquipments.value = clone(equipments); // Store original state
  tempEquipments.splice(0, tempEquipments.length, ...clone(equipments))
  showModal.value = true
}
function closeModal() {
  showModal.value = false
  selectedStation.value = null
  tempEquipments.splice(0)
  originalEquipments.value = []
}

async function saveEquipments() {
    if (!selectedStation.value) return;

    const originalIds = new Set(originalEquipments.value.map(eq => eq.id));
    const currentIds = new Set(tempEquipments.map(eq => eq.id).filter(id => id));

    for (const originalEq of originalEquipments.value) {
        if (!currentIds.has(originalEq.id)) {
            await infrastructureStore.removeStationEquipment(originalEq.id);
        }
    }

    for (const tempEq of tempEquipments) {
        if (tempEq.id) { 
            const originalEq = originalEquipments.value.find(eq => eq.id === tempEq.id);
            if (JSON.stringify(originalEq) !== JSON.stringify(tempEq)) {
                await infrastructureStore.updateStationEquipment(tempEq.id, tempEq);
            }
        } else {
            const payload = { ...tempEq, station: selectedStation.value.id };
            await infrastructureStore.addStationEquipment(payload);
        }
    }
    
    await infrastructureStore.fetchStations();
    closeModal();
}

function addEquipmentRow() {
  tempEquipments.push({ 
    category: '',
    name: '',
    make_modal: '',
    address: '',
    location_in_station: '',
    quantity: 1,
  })
}
function removeEquipmentRow(i) {
  tempEquipments.splice(i, 1)
}
</script>

<template>
  <div class="space-y-5">
    <p class="text-app/80 text-sm">Map stations to depots, manage communication equipment, or upload a complete list via Excel.</p>

    <!-- Form for creating a new station -->
    <div class="card">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div class="md:col-span-1">
          <label class="block text-sm font-medium mb-1">Depot</label>
          <select v-model="newStation.depot" class="field h-9">
            <option :value="null" disabled>Select Depot</option>
            <option v-for="opt in depotOptions" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
          </select>
        </div>
        <div class="md:col-span-1">
          <label class="block text-sm font-medium mb-1">Station Name</label>
          <input v-model="newStation.name" class="field h-9" placeholder="e.g., Dadar" />
        </div>
        <div class="md:col-span-1">
          <label class="block text-sm font-medium mb-1">Station Code</label>
          <input v-model="newStation.code" class="field h-9" placeholder="e.g., DDR" />
        </div>
         <div class="md:col-span-1">
          <label class="block text-sm font-medium mb-1">Station Category</label>
          <input v-model="newStation.category" class="field h-9" placeholder="e.g., NSG6" />
        </div>
      </div>
       <div class="mt-3 flex justify-end">
          <button class="btn btn-primary" @click="addStation">Add Station</button>
      </div>
    </div>
    
    <!-- File Upload Section -->
    <div class="card">
       <div class="flex items-end gap-4">
          <div class="flex-grow">
            <label class="block text-sm font-medium mb-1">Upload Stations & Equipment File</label>
             <p class="text-xs text-app/60 mb-2">Select an Excel file with Depot, Station Name, Code, Category, and Equipment details.</p>
             <div class="flex items-center gap-2">
                <input type="file" ref="fileInput" @change="handleFileSelect" class="hidden" accept=".xlsx, .xls, .csv" />
                <button class="btn" @click="triggerFileInput">Choose File...</button>
                <span v-if="selectedFile" class="text-sm text-muted truncate max-w-xs">{{ selectedFile.name }}</span>
             </div>
          </div>
          <div>
            <button v-if="selectedFile" class="btn btn-primary" @click="handleFileUpload" :disabled="infrastructureStore.loading.stations">
              {{ infrastructureStore.loading.stations ? 'Uploading...' : 'Upload' }}
            </button>
          </div>
       </div>
    </div>

    <!-- Stations List Table -->
    <div class="rounded-2xl border-app bg-card text-app overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <colgroup>
            <col class="w-[20%]">
            <col class="w-[20%]">
            <col class="w-[15%]">
            <col class="w-[15%]">
            <col class="w-[15%]">
            <col class="w-[15%]">
          </colgroup>
          <thead>
            <tr class="text-left border-b border-app/40">
              <th @click="toggleSort('depot_name')" class="py-2.5 px-3 cursor-pointer select-none text-left">Depot <span v-if="sortKey === 'depot_name'">{{ sortDir === 'asc' ? '▲' : '▼' }}</span></th>
              <th @click="toggleSort('name')" class="py-2.5 px-3 cursor-pointer select-none text-center">Station Name <span v-if="sortKey === 'name'">{{ sortDir === 'asc' ? '▲' : '▼' }}</span></th>
              <th @click="toggleSort('code')" class="py-2.5 px-3 cursor-pointer select-none text-center">Station Code <span v-if="sortKey === 'code'">{{ sortDir === 'asc' ? '▲' : '▼' }}</span></th>
              <th @click="toggleSort('category')" class="py-2.5 px-3 cursor-pointer select-none text-center">Category <span v-if="sortKey === 'category'">{{ sortDir === 'asc' ? '▲' : '▼' }}</span></th>
              <th class="py-2.5 px-3 text-center">Equipment Count</th>
              <th class="py-2.5 px-3 text-center">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="infrastructureStore.loading.stations && sortedStations.length === 0">
              <td colspan="6" class="px-3 py-6 text-center text-muted">Loading...</td>
            </tr>
            <tr v-else-if="infrastructureStore.error">
              <td colspan="6" class="px-3 py-6 text-center text-red-500">{{ infrastructureStore.error }}</td>
            </tr>
            <tr v-else-if="sortedStations.length === 0">
              <td colspan="6" class="px-3 py-6 text-app/60 text-center">No stations yet — add one above or upload a file.</td>
            </tr>
            <tr v-for="s in sortedStations" :key="s.id" class="border-t border-app/30">
              <td class="py-2 px-3 align-middle text-left">{{ s.depot_name }}</td>
              <td class="py-2 px-3 align-middle text-center">{{ s.name }}</td>
              <td class="py-2 px-3 align-middle text-center">{{ s.code }}</td>
              <td class="py-2 px-3 align-middle text-center">{{ s.category }}</td>
              <td class="py-2 px-3 align-middle text-center">{{ s.equipment_count }}</td>
              <td class="py-2 px-3 align-middle">
                <div class="flex flex-wrap items-center justify-center gap-2">
                  <button class="h-9 w-9 flex items-center justify-center rounded-lg bg-[var(--button-primary)] text-[var(--seasalt)] hover:bg-[var(--button-hover)] transition" @click="openEditModal(s)" title="Edit Station">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6">
                      <path stroke-linecap="round" stroke-linejoin="round" d="m16.862 4.487 1.687-1.688a1.875 1.875 0 1 1 2.652 2.652L10.582 16.07a4.5 4.5 0 0 1-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 0 1 1.13-1.897l8.932-8.931Zm0 0L19.5 7.125M18 14v4.75A2.25 2.25 0 0 1 15.75 21H5.25A2.25 2.25 0 0 1 3 18.75V8.25A2.25 2.25 0 0 1 5.25 6H10" />
                    </svg>
                  </button>
                  <button class="h-9 w-9 flex items-center justify-center rounded-lg bg-[var(--button-primary)] text-[var(--seasalt)] hover:bg-[var(--button-hover)] transition" @click="openManage(s)" title="Manage Equipment">
                     <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M11.42 15.17 17.25 21A2.652 2.652 0 0 0 21 17.25l-5.877-5.877M11.42 15.17l2.496-3.03c.317-.384.74-.626 1.208-.766M11.42 15.17l-4.655 5.653a2.548 2.548 0 1 1-3.586-3.586l6.837-5.63m5.108-.233c.55-.164 1.163-.188 1.743-.14a4.5 4.5 0 0 0 4.486-6.336l-3.276 3.277a3.004 3.004 0 0 1-2.25-2.25l3.276-3.276a4.5 4.5 0 0 0-6.336 4.486c.091 1.076-.071 2.264-.904 2.95l-.102.085m-1.745 1.437L5.909 7.5H4.5L2.25 3.75l1.5-1.5L7.5 4.5v1.409l4.26 4.26m-1.745 1.437 1.745-1.437m6.615 8.206L15.75 15.75M4.867 19.125h.008v.008h-.008v-.008Z" />
                    </svg>
                  </button>
                  <button
                    class="inline-flex items-center justify-center h-9 w-9 rounded-md text-app ring-1 ring-app/60 hover:bg-black/10 transition"
                    title="Remove station" @click="openDeleteModal(s)">
                    <Trash2 class="w-6 h-6" />
                  </button>
                </div>
              </td>

            </tr>
          </tbody>
        </table>
      </div>
    </div>
    
    <!-- Edit Station Modal -->
    <div v-if="isEditModalOpen" class="fixed inset-0 z-50 bg-black/40 flex items-center justify-center p-4">
      <div class="bg-card rounded-2xl p-6 w-full max-w-2xl space-y-4">
        <h3 class="text-lg font-semibold">Edit Station</h3>
        <div v-if="stationToEdit" class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium mb-1">Depot</label>
            <select v-model="stationToEdit.depot" class="field h-9">
              <option v-for="opt in depotOptions" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Station Name</label>
            <input v-model="stationToEdit.name" class="field h-9" />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Station Code</label>
            <input v-model="stationToEdit.code" class="field h-9" />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Station Category</label>
            <input v-model="stationToEdit.category" class="field h-9" />
          </div>
        </div>
        <div class="flex justify-end gap-3 pt-4">
          <button @click="isEditModalOpen = false" class="btn btn-outline">Cancel</button>
          <button @click="saveStationChanges" class="btn btn-primary">Save Changes</button>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div v-if="isDeleteModalOpen" class="fixed inset-0 z-50 bg-black/40 flex items-center justify-center p-4">
      <div class="bg-card rounded-2xl p-6 w-full max-w-md space-y-4">
        <h3 class="text-lg font-semibold">Confirm Deletion</h3>
        <p>Are you sure you want to delete station "{{ stationToDelete?.name }}"? This action cannot be undone.</p>
        <div class="flex justify-end gap-3 pt-4">
          <button @click="isDeleteModalOpen = false" class="btn btn-outline">Cancel</button>
          <button @click="confirmDelete" class="btn" style="background-color: #ef4444; color: white;">Delete</button>
        </div>
      </div>
    </div>

    <!-- Manage Equipment Modal -->
    <div v-if="showModal" class="fixed inset-0 z-50">
      <div class="absolute inset-0 bg-black/40" @click="closeModal"></div>
      <div class="absolute inset-0 grid place-items-center p-4">
        <section class="w-full max-w-7xl rounded-2xl border-app bg-card text-app shadow-2xl overflow-hidden flex flex-col">
          <header class="flex items-center justify-between px-4 py-3 border-b border-app/40">
            <div class="min-w-0">
              <h3 class="font-semibold truncate">Manage Communication Equipment — {{ selectedStation?.name || '' }}</h3>
              <p class="text-xs text-app/70">Add, edit, or remove circuit equipment for this station.</p>
            </div>
            <button class="icon-btn" title="Close" @click="closeModal">
              <svg viewBox="0 0 24 24" class="w-5 h-5"><path fill="currentColor" d="M6.4 4.99L5 6.4L10.6 12L5 17.6L6.4 19L12 13.4L17.6 19l1.4-1.4L13.4 12L19 6.4L17.6 4.99L12 10.6z" /></svg>
            </button>
          </header>
          <div class="p-3 flex-1 overflow-y-auto">
            <div class="rounded-2xl border-app bg-card text-app overflow-hidden">
              <div class="overflow-x-auto">
                <table class="w-full text-sm">
                  <thead>
                    <tr class="text-left border-b border-app/40">
                      <th class="py-2.5 px-3">Category</th>
                      <th class="py-2.5 px-3">Equipment Name</th>
                      <th class="py-2.5 px-3">Make / Model</th>
                      <th class="py-2.5 px-3">Address</th>
                      <th class="py-2.5 px-3">Location</th>
                      <th class="py-2.5 px-3">Quantity</th>
                      <th class="py-2.5 px-3 w-16 text-center">Remove</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-if="tempEquipments.length === 0">
                      <td colspan="7" class="px-3 py-6 text-app/60 text-center">No equipment yet — add a row below.</td>
                    </tr>
                    <tr v-for="(r, i) in tempEquipments" :key="r.id || i" class="border-t border-app/30">
                      <td class="py-2 px-3 align-top"><input v-model="r.category" class="field h-9" placeholder="e.g., Telecom" /></td>
                      <td class="py-2 px-3 align-top"><input v-model="r.name" class="field h-9" placeholder="e.g., Modem" /></td>
                      <td class="py-2 px-3 align-top"><input v-model="r.make_modal" class="field h-9" placeholder="e.g., Cisco / 887VA" /></td>
                      <td class="py-2 px-3 align-top"><input v-model="r.address" class="field h-9" placeholder="e.g., 16.12.13.39" /></td>
                      <td class="py-2 px-3 align-top"><input v-model="r.location_in_station" class="field h-9" placeholder="e.g., OFC HUT" /></td>
                      <td class="py-2 px-3 align-top"><input v-model.number="r.quantity" type="number" class="field h-9 w-20" /></td>
                      <td class="py-2 px-3 align-top text-center">
                        <button
                          class="inline-flex items-center justify-center h-9 w-9 rounded-md text-app ring-1 ring-app/60 hover:bg-black/10 transition"
                          title="Remove row" @click="removeEquipmentRow(i)">
                          <span class="sr-only">Remove row</span>
                          <svg viewBox="0 0 24 24" class="w-6 h-6" aria-hidden="true">
                            <path fill="currentColor"
                              d="M12 2a10 10 0 1 0 0 20a10 10 0 0 0 0-20Zm3.11 13.11l-1 1L12 13l-2.11 3.11l-1-1L11 12L8.89 9.89l1-1L12 11l2.11-2.11l1 1L13 12z" />
                          </svg>
                        </button>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
            <div class="mt-3 grid grid-cols-[1fr_auto_1fr] items-center">
              <div></div>
              <div class="justify-self-center">
                <button class="btn" @click="addEquipmentRow">+ Add Row</button>
              </div>
              <div class="justify-self-end flex items-center gap-2">
                <button class="btn btn-primary" @click="saveEquipments">Save Changes</button>
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>
  </div>
</template>



