<script setup>
import { ref, onMounted, computed } from 'vue'
import { useInfrastructureStore } from '@/stores/infrastructure.js'

const infrastructureStore = useInfrastructureStore()
const rows = computed(() => infrastructureStore.supervisors)
const depotOptions = computed(() => infrastructureStore.depots.map(d => ({ label: d.name, value: d.id })));


// --- State for file upload ---
const selectedFile = ref(null)
const fileInput = ref(null)

// --- State for Modals ---
const isEditModalOpen = ref(false)
const currentSupervisor = ref(null)
const isDeleteModalOpen = ref(false)
const supervisorToDelete = ref(null)


onMounted(() => {
  infrastructureStore.fetchSupervisors()
  if (infrastructureStore.depots.length === 0) infrastructureStore.fetchDepots()
  if (infrastructureStore.stations.length === 0) infrastructureStore.fetchStations()
})

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
  await infrastructureStore.uploadSupervisorsFile(selectedFile.value);
  selectedFile.value = null;
  if(fileInput.value) fileInput.value.value = '';
}

// --- Modal and Form Functions ---
function openEditModal(supervisor) {
  // Create a copy for editing
  currentSupervisor.value = { ...supervisor };
  isEditModalOpen.value = true;
}

function openAddModal() {
  // Open with a blank object
  currentSupervisor.value = {
    name: '',
    designation: '',
    depot: null,
    mobile: '',
    email: ''
  };
  isEditModalOpen.value = true;
}


async function saveSupervisorChanges() {
  if (!currentSupervisor.value) return;

  if (currentSupervisor.value.id) {
    // If it has an ID, it's an update
    await infrastructureStore.updateSupervisor(currentSupervisor.value.id, currentSupervisor.value);
  } else {
    // Otherwise, it's a new supervisor
    await infrastructureStore.addSupervisor(currentSupervisor.value);
  }

  isEditModalOpen.value = false;
  currentSupervisor.value = null;
}

function openDeleteModal(supervisor) {
  supervisorToDelete.value = supervisor;
  isDeleteModalOpen.value = true;
}

async function confirmDelete() {
  if (!supervisorToDelete.value) return;
  await infrastructureStore.removeSupervisor(supervisorToDelete.value.id);
  isDeleteModalOpen.value = false;
  supervisorToDelete.value = null;
}


// Dropdown options logic
function stationOptions(depotId) {
  if (!depotId) return []
  return infrastructureStore.stations
    .filter(s => s.depot === depotId)
    .map(s => ({ label: s.name, value: s.id }))
}
function subSectionOptions(depotId) { return [] }
function assetOptions(stationIds = [], subSectionIds = []) { return [] }
</script>

<template>
  <div class="space-y-4">
    <p class="text-app/80 text-sm">Add/update depot supervisors by uploading an Excel file or manage them individually below.</p>

    <!-- Table -->
    <div class="rounded-2xl border-app bg-card text-app overflow-hidden">
        <div class="overflow-x-auto">
            <table class="w-full text-sm min-w-[1200px]">
                <thead>
                    <tr class="text-left border-b border-app/40">
                        <th class="py-2.5 px-3 whitespace-nowrap">Supervisor</th>
                        <th class="py-2.5 px-3 whitespace-nowrap">Designation</th>
                        <th class="py-2.5 px-3 whitespace-nowrap">Depot</th>
                        <th class="py-2.5 px-3 whitespace-nowrap">Mobile</th>
                        <th class="py-2.5 px-3 whitespace-nowrap">Email</th>
                        <th class="py-2.5 px-3 w-40 text-center">Actions</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-if="infrastructureStore.loading.supervisors && rows.length === 0">
                        <td colspan="6" class="py-6 px-3 text-center text-muted">Loading supervisors...</td>
                    </tr>
                    <tr v-else-if="infrastructureStore.error">
                        <td colspan="6" class="py-6 px-3 text-center text-red-500">{{ infrastructureStore.error }}</td>
                    </tr>
                    <tr v-for="(r, i) in rows" :key="r.id">
                        <td class="py-2 px-3 align-top">{{ r.name }}</td>
                        <td class="py-2 px-3 align-top">{{ r.designation }}</td>
                        <td class="py-2 px-3 align-top">{{ r.depot_name || 'N/A' }}</td>
                        <td class="py-2 px-3 align-top">{{ r.mobile || 'N/A' }}</td>
                        <td class="py-2 px-3 align-top">{{ r.email || 'N/A' }}</td>
                        <td class="py-2 px-3 align-top text-center">
                            <div class="flex items-center justify-center gap-2">
                                <button @click="openEditModal(r)" class="btn h-9 px-3">Edit</button>
                                <button @click="openDeleteModal(r)" class="inline-flex items-center justify-center h-9 w-9 rounded-md text-app border border-app hover:bg-gray-100 transition">
                                    &times;
                                </button>
                            </div>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>

    <!-- Bottom action bar -->
    <div class="mt-3 grid grid-cols-[1fr_auto_1fr] items-center">
      <div class="justify-self-start flex items-center gap-2">
        <input type="file" ref="fileInput" @change="handleFileSelect" class="hidden" accept=".xlsx, .xls, .csv" />
        <button class="btn" @click="triggerFileInput">Choose Supervisor File</button>
        <span v-if="selectedFile" class="text-sm text-muted truncate max-w-xs">{{ selectedFile.name }}</span>
        <button v-if="selectedFile" class="btn btn-primary" @click="handleFileUpload" :disabled="infrastructureStore.loading.supervisors">
          {{ infrastructureStore.loading.supervisors ? 'Uploading...' : 'Upload' }}
        </button>
      </div>
      <div class="justify-self-center"></div>
      <div class="justify-self-end"><button class="btn" @click="openAddModal">+ Add Row</button></div>
    </div>

    <!-- Add/Edit Supervisor Modal -->
    <div v-if="isEditModalOpen" class="fixed inset-0 z-50 bg-black/40 flex items-center justify-center p-4">
      <div class="bg-card rounded-2xl p-6 w-full max-w-2xl space-y-4">
        <h3 class="text-lg font-semibold">{{ currentSupervisor.id ? 'Edit' : 'Add' }} Supervisor</h3>
        <div v-if="currentSupervisor" class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium mb-1">Name</label>
            <input v-model="currentSupervisor.name" class="field" />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Designation</label>
            <input v-model="currentSupervisor.designation" class="field" />
          </div>
           <div>
            <label class="block text-sm font-medium mb-1">Depot</label>
            <select v-model="currentSupervisor.depot" class="field">
              <option :value="null">-- No Depot --</option>
              <option v-for="depot in depotOptions" :key="depot.value" :value="depot.value">
                {{ depot.label }}
              </option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Mobile</label>
            <input v-model="currentSupervisor.mobile" class="field" />
          </div>
          <div class="md:col-span-2">
            <label class="block text-sm font-medium mb-1">Email</label>
            <input v-model="currentSupervisor.email" type="email" class="field" />
          </div>
        </div>
        <div class="flex justify-end gap-3 pt-4">
          <button @click="isEditModalOpen = false" class="btn btn-outline">Cancel</button>
          <button @click="saveSupervisorChanges" class="btn btn-primary">Save Changes</button>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div v-if="isDeleteModalOpen" class="fixed inset-0 z-50 bg-black/40 flex items-center justify-center p-4">
      <div class="bg-card rounded-2xl p-6 w-full max-w-md space-y-4">
        <h3 class="text-lg font-semibold">Confirm Deletion</h3>
        <p>Are you sure you want to delete the supervisor "{{ supervisorToDelete?.name }}"? This action cannot be undone.</p>
        <div class="flex justify-end gap-3 pt-4">
          <button @click="isDeleteModalOpen = false" class="btn btn-outline">Cancel</button>
          <button @click="confirmDelete" class="btn" style="background-color: #ef4444; color: white;">Delete</button>
        </div>
      </div>
    </div>

  </div>
</template>

