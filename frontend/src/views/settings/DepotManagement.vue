<script setup>
import { reactive, ref, onMounted, computed } from 'vue'
import { useDepotsStore } from '@/stores/depots.js'
import { Trash2 } from 'lucide-vue-next'

const clone = (o) => JSON.parse(JSON.stringify(o))

// Store state
const depotStore = useDepotsStore()

// --- Sorting State ---
const sortKey = ref('name');
const sortDir = ref('asc');

const sortedDepots = computed(() => {
  const data = [...depotStore.depots];
  data.sort((a, b) => {
    let valA = a[sortKey.value];
    let valB = b[sortKey.value];
    const modifier = sortDir.value === 'asc' ? 1 : -1;
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
const tempEquipments = reactive([])
const originalEquipments = ref([])

// --- Edit Modal State ---
const isEditModalOpen = ref(false);
const depotToEdit = ref(null);

function openEditModal(depot) {
  depotToEdit.value = { ...depot };
  isEditModalOpen.value = true;
}

async function saveDepotChanges() {
  if (!depotToEdit.value) return;
  await depotStore.updateDepot(depotToEdit.value.id, depotToEdit.value);
  isEditModalOpen.value = false;
  depotToEdit.value = null;
}


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

    const promises = [];

    for (const original of originalEquipments.value) {
        if (!currentIds.has(original.id)) {
            promises.push(depotStore.removeEquipment(original.id));
        }
    }

    for (const current of tempEquipments) {
        if (current.id) { 
            const original = originalEquipments.value.find(o => o.id === current.id);
            if (JSON.stringify(original) !== JSON.stringify(current)) {
                promises.push(depotStore.updateEquipment(current.id, current));
            }
        } else { 
            const payload = { ...current, depot: selectedDepot.value.id };
            promises.push(depotStore.addEquipment(payload));
        }
    }

    await Promise.all(promises);
    await depotStore.fetchDepots();
    closeManageModal();
}

function addEquipmentRow() {
  tempEquipments.push({
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
           <colgroup>
            <col class="w-[25%]">
            <col class="w-[20%]">
            <col class="w-[25%]">
            <col class="w-[15%]">
            <col class="w-[15%]">
          </colgroup>
          <thead>
            <tr class="text-left border-b border-app/40">
              <th @click="toggleSort('name')" class="py-2.5 px-3 cursor-pointer select-none text-center">Depot Name <span v-if="sortKey === 'name'">{{ sortDir === 'asc' ? '▲' : '▼' }}</span></th>
              <th @click="toggleSort('code')" class="py-2.5 px-3 cursor-pointer select-none text-center">Code <span v-if="sortKey === 'code'">{{ sortDir === 'asc' ? '▲' : '▼' }}</span></th>
              <th @click="toggleSort('location')" class="py-2.5 px-3 cursor-pointer select-none text-center">Location <span v-if="sortKey === 'location'">{{ sortDir === 'asc' ? '▲' : '▼' }}</span></th>
              <th class="py-2.5 px-3 text-center">Equipment Count</th>
              <th class="py-2.5 px-3 text-center">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="depotStore.loading.depots && sortedDepots.length === 0">
                <td colspan="5" class="px-3 py-6 text-center text-muted">Loading...</td>
            </tr>
            <tr v-else-if="depotStore.error">
                <td colspan="5" class="px-3 py-6 text-center text-red-500">{{ depotStore.error }}</td>
            </tr>
            <tr v-else-if="sortedDepots.length === 0">
                <td colspan="5" class="px-3 py-6 text-app/60 text-center">No depots yet — add one above.</td>
            </tr>
            <tr v-for="d in sortedDepots" :key="d.id" class="border-t border-app/30">
              <td class="py-2 px-3 align-middle text-center">{{ d.name }}</td>
              <td class="py-2 px-3 align-middle text-center">{{ d.code || '—' }}</td>
              <td class="py-2 px-3 align-middle text-center">{{ d.location || '—' }}</td>
              <td class="py-2 px-3 align-middle text-center">{{ d.equipments?.length || 0 }}</td>
              <td class="py-2 px-3 align-middle">
                <div class="flex flex-wrap items-center justify-center gap-2">
                  <button class="h-9 w-9 flex items-center justify-center rounded-lg bg-[var(--button-primary)] text-[var(--seasalt)] hover:bg-[var(--button-hover)] transition" @click="openEditModal(d)" title="Edit Depot">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6">
                      <path stroke-linecap="round" stroke-linejoin="round" d="m16.862 4.487 1.687-1.688a1.875 1.875 0 1 1 2.652 2.652L10.582 16.07a4.5 4.5 0 0 1-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 0 1 1.13-1.897l8.932-8.931Zm0 0L19.5 7.125M18 14v4.75A2.25 2.25 0 0 1 15.75 21H5.25A2.25 2.25 0 0 1 3 18.75V8.25A2.25 2.25 0 0 1 5.25 6H10" />
                    </svg>
                  </button>
                  <button class="h-9 w-9 flex items-center justify-center rounded-lg bg-[var(--button-primary)] text-[var(--seasalt)] hover:bg-[var(--button-hover)] transition" @click="openManageModal(d)" title="Manage Equipment">
                     <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M11.42 15.17 17.25 21A2.652 2.652 0 0 0 21 17.25l-5.877-5.877M11.42 15.17l2.496-3.03c.317-.384.74-.626 1.208-.766M11.42 15.17l-4.655 5.653a2.548 2.548 0 1 1-3.586-3.586l6.837-5.63m5.108-.233c.55-.164 1.163-.188 1.743-.14a4.5 4.5 0 0 0 4.486-6.336l-3.276 3.277a3.004 3.004 0 0 1-2.25-2.25l3.276-3.276a4.5 4.5 0 0 0-6.336 4.486c.091 1.076-.071 2.264-.904 2.95l-.102.085m-1.745 1.437L5.909 7.5H4.5L2.25 3.75l1.5-1.5L7.5 4.5v1.409l4.26 4.26m-1.745 1.437 1.745-1.437m6.615 8.206L15.75 15.75M4.867 19.125h.008v.008h-.008v-.008Z" />
                    </svg>
                  </button>
                  <button
                    class="inline-flex items-center justify-center h-9 w-9 rounded-md text-app ring-1 ring-app/60 hover:bg-black/10 transition"
                    title="Remove depot"
                    @click="openDeleteModal(d)"
                  >
                    <Trash2 class="w-6 h-6" />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Edit Depot Modal -->
    <div v-if="isEditModalOpen" class="fixed inset-0 z-50 bg-black/40 flex items-center justify-center p-4">
      <div class="bg-card rounded-2xl p-6 w-full max-w-2xl space-y-4">
        <h3 class="text-lg font-semibold">Edit Depot</h3>
        <div v-if="depotToEdit" class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium mb-1">Depot Name</label>
            <input v-model="depotToEdit.name" class="field" />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Depot Code</label>
            <input v-model="depotToEdit.code" class="field" />
          </div>
          <div class="md:col-span-2">
            <label class="block text-sm font-medium mb-1">Location</label>
            <input v-model="depotToEdit.location" class="field" />
          </div>
        </div>
        <div class="flex justify-end gap-3 pt-4">
          <button @click="isEditModalOpen = false" class="btn btn-outline">Cancel</button>
          <button @click="saveDepotChanges" class="btn btn-primary">Save Changes</button>
        </div>
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

