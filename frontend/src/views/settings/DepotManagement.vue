<script setup>
import { reactive, ref, onMounted } from 'vue'
import { useInfrastructureStore } from '@/stores/infrastructure.js'

const clone = (o) => JSON.parse(JSON.stringify(o))

// Store state
const depotStore = useInfrastructureStore()

// --- State for file upload ---
const selectedFile = ref(null)
const fileInput = ref(null)

// Fetch data when the component is first mounted
onMounted(() => {
  depotStore.fetchDepots()
})


// New depot inline form
const newDepot = reactive({ name: '', code: '', location: '' })

// --- State for Modals ---
const isDeleteModalOpen = ref(false)
const depotToDelete = ref(null)
const isEquipmentModalOpen = ref(false)
const selectedDepot = ref(null)
const tempEquipments = reactive([]) // local edit list inside modal
const originalEquipments = ref([]) // To compare for changes

function addDepot() {
  if (!newDepot.name.trim()) return
  depotStore.addDepot({
    name: newDepot.name.trim(),
    code: newDepot.code.trim(),
    location: newDepot.location.trim(),
  })
  newDepot.name = ''; newDepot.code = ''; newDepot.location = ''
}

function openDeleteModal(depot) {
  depotToDelete.value = depot;
  isDeleteModalOpen.value = true;
}

async function confirmDelete() {
  if (!depotToDelete.value) return;
  await depotStore.removeDepot(depotToDelete.value.id);
  isDeleteModalOpen.value = false;
  depotToDelete.value = null;
}

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
  await depotStore.uploadDepotsFile(selectedFile.value);
  selectedFile.value = null;
  if(fileInput.value) fileInput.value.value = '';
}


// --- Equipment Modal Functions ---

function openManageModal(depot) {
  selectedDepot.value = depot
  const equipments = depot.equipments || []
  originalEquipments.value = clone(equipments)
  tempEquipments.splice(0, tempEquipments.length, ...clone(equipments))
  isEquipmentModalOpen.value = true
}

function closeManageModal() {
  isEquipmentModalOpen.value = false
  selectedDepot.value = null
  tempEquipments.splice(0)
  originalEquipments.value = []
}

async function saveEquipmentChanges() {
    if (!selectedDepot.value) return;

    const originalIds = new Set(originalEquipments.value.map(e => e.id));
    const currentIds = new Set(tempEquipments.filter(e => e.id).map(e => e.id));

    // Promises for all API calls
    const promises = [];

    // 1. Find items to DELETE
    for (const original of originalEquipments.value) {
        if (!currentIds.has(original.id)) {
            promises.push(depotStore.removeEquipment(original.id));
        }
    }

    // 2. Find items to ADD or UPDATE
    for (const current of tempEquipments) {
        if (current.id) { // Existing item, check for updates
            const original = originalEquipments.value.find(o => o.id === current.id);
            if (JSON.stringify(original) !== JSON.stringify(current)) {
                promises.push(depotStore.updateEquipment(current.id, current));
            }
        } else { // New item
            const payload = { ...current, depot: selectedDepot.value.id };
            promises.push(depotStore.addEquipment(payload));
        }
    }

    await Promise.all(promises);
    await depotStore.fetchDepots(); // Refresh the main depot list
    closeManageModal();
}

function addEquipmentRow() {
  tempEquipments.push({
    // no 'id' means it's a new item
    name: '',
    model_type: '',
    asset_id: '',
    location_in_depot: '',
    notes: ''
  })
}

function removeEquipmentRow(index) {
  tempEquipments.splice(index, 1)
}
</script>

<template>
  <div class="space-y-5">
    <p class="text-app/80 text-sm">Add depots, upload depot/equipment lists from Excel, or manage equipment for each depot.</p>

    <!-- New Depot form -->
    <div class="card">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <label class="block text-sm font-medium mb-1">Depot Name</label>
          <input v-model="newDepot.name" class="field" placeholder="e.g., West Yard" />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">Depot Code</label>
          <input v-model="newDepot.code" class="field" placeholder="e.g., WY-01" />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">Location</label>
          <input v-model="newDepot.location" class="field" placeholder="e.g., Sector 12" />
        </div>
      </div>
      <div class="mt-3 flex justify-end">
        <button class="btn btn-primary" @click="addDepot">Add Depot</button>
      </div>
    </div>

     <!-- Bottom action bar -->
    <div class="mt-3 flex items-center justify-between">
      <div class="flex items-center gap-2">
        <input type="file" ref="fileInput" @change="handleFileSelect" class="hidden" accept=".xlsx, .xls, .csv" />
        <button class="btn" @click="triggerFileInput">Choose Depot File</button>
        <span v-if="selectedFile" class="text-sm text-muted truncate max-w-xs">{{ selectedFile.name }}</span>
        <button v-if="selectedFile" class="btn btn-primary" @click="handleFileUpload" :disabled="depotStore.loading.depots">
          {{ depotStore.loading.depots ? 'Uploading...' : 'Upload' }}
        </button>
      </div>
    </div>

    <!-- Depots list -->
    <div class="rounded-2xl border-app bg-card text-app overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead>
            <tr class="text-left border-b border-app/40">
              <th class="py-2.5 px-3">Depot Name</th>
              <th class="py-2.5 px-3">Code</th>
              <th class="py-2.5 px-3">Location</th>
              <th class="py-2.5 px-3 whitespace-nowrap">Equipment Count</th>
              <th class="py-2.5 px-3 w-[240px]">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="depotStore.loading.depots && depotStore.depots.length === 0">
                <td colspan="5" class="px-3 py-6 text-center text-muted">Loading...</td>
            </tr>
            <tr v-else-if="depotStore.error">
                <td colspan="5" class="px-3 py-6 text-center text-red-500">{{ depotStore.error }}</td>
            </tr>
            <tr v-else-if="depotStore.depots.length===0">
                <td colspan="5" class="px-3 py-6 text-app/60 text-center">No depots yet — add one above.</td>
            </tr>
            <tr v-for="(d, i) in depotStore.depots" :key="d.id" class="border-t border-app/30">
              <td class="py-2 px-3 align-middle">{{ d.name }}</td>
              <td class="py-2 px-3 align-middle">{{ d.code || '—' }}</td>
              <td class="py-2 px-3 align-middle">{{ d.location || '—' }}</td>
              <td class="py-2 px-3 align-middle text-center">{{ d.equipments?.length || 0 }}</td>
              <td class="py-2 px-3 align-middle">
                <div class="flex flex-wrap items-center gap-2">
                  <button class="btn" @click="openManageModal(d)">Manage Equipment</button>
                  <button
                    class="inline-flex items-center justify-center h-9 w-9 rounded-md text-app border border-app hover:bg-[color-mix(in_oklab,_var(--card-bg),_#000_12%)] transition"
                    title="Remove depot"
                    @click="openDeleteModal(d)"
                  >
                    <span class="sr-only">Remove depot</span>
                    <svg viewBox="0 0 24 24" class="w-6 h-6" aria-hidden="true">
                      <path fill="currentColor" d="M12 2a10 10 0 1 0 0 20a10 10 0 0 0 0-20Zm3.11 13.11l-1 1L12 13l-2.11 3.11l-1-1L11 12L8.89 9.89l1-1L12 11l2.11-2.11l1 1L13 12z"/>
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
        <p>Are you sure you want to delete the depot "{{ depotToDelete?.name }}"? This may affect associated supervisors and stations.</p>
        <div class="flex justify-end gap-3 pt-4">
          <button @click="isDeleteModalOpen = false" class="btn btn-outline">Cancel</button>
          <button @click="confirmDelete" class="btn" style="background-color: #ef4444; color: white;">Delete</button>
        </div>
      </div>
    </div>

    <!-- Equipment Modal -->
    <div v-if="isEquipmentModalOpen" class="fixed inset-0 z-50">
      <div class="absolute inset-0 bg-black/40" @click="closeManageModal" />
      <div class="absolute inset-0 grid place-items-center p-4">
        <section class="w-full max-w-6xl rounded-2xl border-app bg-card text-app shadow-2xl overflow-hidden flex flex-col">
          <!-- Modal header -->
          <header class="flex items-center justify-between px-4 py-3 border-b border-app/40">
            <div class="min-w-0">
              <h3 class="font-semibold truncate">
                Manage Measuring Equipment — {{ selectedDepot?.name }}
              </h3>
              <p class="text-xs text-app/70">Add, edit, or remove measuring equipment (e.g., Multimeter, OTDR) for this depot.</p>
            </div>
            <button class="icon-btn" title="Close" @click="closeManageModal">
              <svg viewBox="0 0 24 24" class="w-5 h-5"><path fill="currentColor" d="M6.4 4.99L5 6.4L10.6 12L5 17.6L6.4 19L12 13.4L17.6 19l1.4-1.4L13.4 12L19 6.4L17.6 4.99L12 10.6z"/></svg>
            </button>
          </header>

          <!-- Equipment table -->
          <div class="p-3 flex-1 overflow-y-auto">
            <div class="rounded-2xl border-app bg-card text-app overflow-hidden">
              <div class="overflow-x-auto">
                <table class="w-full text-sm">
                  <thead>
                    <tr class="text-left border-b border-app/40">
                      <th class="py-2.5 px-3 whitespace-nowrap">Measuring Equipment</th>
                      <th class="py-2.5 px-3 whitespace-nowrap">Model / Type</th>
                      <th class="py-2.5 px-3 whitespace-nowrap">Asset / Serial ID</th>
                      <th class="py-2.5 px-3 whitespace-nowrap">Location in Depot</th>
                      <th class="py-2.5 px-3 whitespace-nowrap">Notes</th>
                      <th class="py-2.5 px-3 w-16 text-center">Remove</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-if="tempEquipments.length===0">
                      <td colspan="6" class="px-3 py-6 text-app/60 text-center">No equipment yet — add a row below.</td>
                    </tr>
                    <tr v-for="(r, i) in tempEquipments" :key="r.id || i" class="border-t border-app/30">
                      <td class="py-2 px-3 align-top">
                        <input v-model="r.name" class="field h-9" placeholder="e.g., Multimeter" />
                      </td>
                      <td class="py-2 px-3 align-top">
                        <input v-model="r.model_type" class="field h-9" placeholder="e.g., Fluke 117" />
                      </td>
                      <td class="py-2 px-3 align-top">
                        <input v-model="r.asset_id" class="field h-9" placeholder="e.g., SN-123456" />
                      </td>
                      <td class="py-2 px-3 align-top">
                        <input v-model="r.location_in_depot" class="field h-9" placeholder="e.g., Bay 3, Shelf A" />
                      </td>
                      <td class="py-2 px-3 align-top">
                        <textarea v-model="r.notes" class="field-textarea min-h-[44px]" placeholder="Calibration due..."></textarea>
                      </td>
                      <td class="py-2 px-3 align-top text-center">
                        <button
                          class="inline-flex items-center justify-center h-9 w-9 rounded-md text-app ring-1 ring-app/60
                                 hover:bg-[color-mix(in_oklab,_var(--surface),_#000_12%)] transition"
                          title="Remove row"
                          @click="removeEquipmentRow(i)"
                        >
                          <span class="sr-only">Remove row</span>
                          <svg viewBox="0 0 24 24" class="w-6 h-6" aria-hidden="true">
                            <path fill="currentColor" d="M12 2a10 10 0 1 0 0 20a10 10 0 0 0 0-20Zm3.11 13.11l-1 1L12 13l-2.11 3.11l-1-1L11 12L8.89 9.89l1-1L12 11l2.11-2.11l1 1L13 12z"/>
                          </svg>
                        </button>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <!-- Bottom actions inside modal -->
            <div class="mt-3 grid grid-cols-[1fr_auto_1fr] items-center">
              <div></div>
              <div class="justify-self-center">
                <button class="btn" @click="addEquipmentRow">+ Add Row</button>
              </div>
              <div class="justify-self-end flex items-center gap-2">
                <button class="btn btn-primary" @click="saveEquipmentChanges">Submit</button>
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>
  </div>
</template>

