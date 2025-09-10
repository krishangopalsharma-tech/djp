<script setup>
import { reactive, ref, computed, onMounted } from 'vue'
import { useInfrastructureStore } from '@/stores/infrastructure.js'
import { useUIStore } from '@/stores/ui'


const infrastructureStore = useInfrastructureStore()

const depotOptions = computed(() =>
  infrastructureStore.depots.map(d => ({ value: d.id, label: d.name + (d.code ? ` (${d.code})` : '') }))
)
const stations = computed(() => infrastructureStore.stations)

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
    const uiStore = useUIStore()
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

    // 1. Find and process deletions
    for (const originalEq of originalEquipments.value) {
        if (!currentIds.has(originalEq.id)) {
            await infrastructureStore.removeStationEquipment(originalEq.id);
        }
    }

    // 2. Find and process updates and additions
    for (const tempEq of tempEquipments) {
        if (tempEq.id) { // Existing equipment
            const originalEq = originalEquipments.value.find(eq => eq.id === tempEq.id);
            // Check if anything actually changed to avoid unnecessary API calls
            if (JSON.stringify(originalEq) !== JSON.stringify(tempEq)) {
                await infrastructureStore.updateStationEquipment(tempEq.id, tempEq);
            }
        } else { // New equipment
            const payload = { ...tempEq, station: selectedStation.value.id };
            await infrastructureStore.addStationEquipment(payload);
        }
    }
    
    // Refresh station list to show updated equipment counts
    await infrastructureStore.fetchStations();
    closeModal();
}

function addEquipmentRow() {
  tempEquipments.push({ 
    // No ID for new items
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
          <thead>
            <tr class="text-left border-b border-app/40">
              <th class="py-2.5 px-3">Depot</th>
              <th class="py-2.5 px-3">Station Name</th>
              <th class="py-2.5 px-3">Station Code</th>
              <th class="py-2.5 px-3">Category</th>
              <th class="py-2.5 px-3">Equipment Count</th>
              <th class="py-2.5 px-3 w-[260px]">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="infrastructureStore.loading.stations && stations.length === 0">
              <td colspan="6" class="px-3 py-6 text-center text-muted">Loading...</td>
            </tr>
            <tr v-else-if="infrastructureStore.error">
              <td colspan="6" class="px-3 py-6 text-center text-red-500">{{ infrastructureStore.error }}</td>
            </tr>
            <tr v-else-if="stations.length === 0">
              <td colspan="6" class="px-3 py-6 text-app/60 text-center">No stations yet — add one above or upload a file.</td>
            </tr>
            <tr v-for="s in stations" :key="s.id" class="border-t border-app/30">
              <td class="py-2 px-3 align-top min-w-[220px]">
                {{ s.depot_name }}
              </td>
              <td class="py-2 px-3 align-top">
                {{ s.name }}
              </td>
              <td class="py-2 px-3 align-top">
                {{ s.code }}
              </td>
               <td class="py-2 px-3 align-top">
                {{ s.category }}
              </td>
               <td class="py-2 px-3 align-top text-center">
                {{ s.equipments?.length || 0 }}
              </td>
              <td class="py-2 px-3 align-top">
                <div class="flex flex-wrap items-center gap-2">
                  <button class="btn" @click="openManage(s)">Manage Equipment</button>
                  <button
                    class="inline-flex items-center justify-center h-9 w-9 rounded-md text-app ring-1 ring-app/60 hover:bg-black/10 transition"
                    title="Remove station" @click="openDeleteModal(s)">
                    <span class="sr-only">Remove station</span>
                    <svg viewBox="0 0 24 24" class="w-6 h-6" aria-hidden="true">
                      <path fill="currentColor"
                        d="M12 2a10 10 0 1 0 0 20a10 10 0 0 0 0-20Zm3.11 13.11l-1 1L12 13l-2.11 3.11l-1-1L11 12L8.89 9.89l1-1L12 11l2.11-2.11l1 1L13 12z" />
                    </svg>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      
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

