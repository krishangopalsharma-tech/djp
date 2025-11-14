<script setup>
import { ref, onMounted, computed, reactive, watch } from 'vue';
import { useSupervisorsStore } from '@/stores/supervisors';
import { useDepotsStore } from '@/stores/depots';
import { useInfrastructureStore } from '@/stores/infrastructure'; // Import new store
import { useUIStore } from '@/stores/ui';
import { Trash2, Wrench } from 'lucide-vue-next'; // Import Wrench icon

const supervisorsStore = useSupervisorsStore();
const depotsStore = useDepotsStore();
const infrastructureStore = useInfrastructureStore(); // Init new store
const uiStore = useUIStore();

const rows = computed(() => supervisorsStore.supervisors);
const depotOptions = computed(() => (depotsStore.depots || []).map(d => ({ label: d.code || d.name, value: d.id })));
const infraTree = computed(() => infrastructureStore.tree); // Get tree data

// --- Sorting ---
const sortKey = ref('name'); const sortDir = ref('asc');
const sortedRows = computed(() => {
  const data = Array.isArray(rows.value) ? [...rows.value] : [];
  data.sort((a, b) => {
    let valA = a[sortKey.value]; let valB = b[sortKey.value];
    const modifier = sortDir.value === 'asc' ? 1 : -1;
    if (sortKey.value === 'depot_display') { valA = a.depot_display || ''; valB = b.depot_display || ''; }
    if (valA < valB) return -1 * modifier; if (valA > valB) return 1 * modifier; return 0;
  });
  return data;
});
function toggleSort(key) { if (sortKey.value === key) { sortDir.value = sortDir.value === 'asc' ? 'desc' : 'asc'; } else { sortKey.value = key; sortDir.value = 'asc'; } }

// --- File Upload ---
const selectedFile = ref(null); const fileInput = ref(null);
function handleFileSelect(event) { const target = event.target; if (target.files && target.files[0]) { selectedFile.value = target.files[0]; } }
function triggerFileInput() { fileInput.value?.click(); }
async function handleFileUpload() { if (!selectedFile.value) { uiStore.pushToast({ type: 'error', title: 'No File', message: 'Please select a file to upload.' }); return; } await supervisorsStore.uploadSupervisorsFile(selectedFile.value); selectedFile.value = null; if(fileInput.value) fileInput.value.value = ''; }
async function exportSupervisorsExcel() { await supervisorsStore.exportSupervisorsToExcel(); }

// --- Add/Edit/Delete Modals ---
const isEditModalOpen = ref(false); const currentSupervisor = ref(null); const isDeleteModalOpen = ref(false); const supervisorToDelete = ref(null);
// Add subsections and assets to initial state
const initialFormState = { name: '', designation: '', depot: null, mobile: '', email: '', user: null, subsections: [], assets: [] };

function openEditModal(supervisor) { 
  // Ensure all fields, including new M2M fields, are copied
  currentSupervisor.value = { ...initialFormState, ...supervisor, depot: supervisor.depot }; 
  isEditModalOpen.value = true; 
}
function openAddModal() { currentSupervisor.value = reactive({ ...initialFormState }); isEditModalOpen.value = true; }
async function saveSupervisorChanges() {
  if (!currentSupervisor.value) return;
  // Ensure M2M fields are part of the payload if they exist
  const payload = { ...currentSupervisor.value };
  if (currentSupervisor.value.id) { 
    await supervisorsStore.updateSupervisor(currentSupervisor.value.id, payload); 
  } else { 
    await supervisorsStore.addSupervisor(payload); 
  }
  isEditModalOpen.value = false; currentSupervisor.value = null;
}
function openDeleteModal(supervisor) { supervisorToDelete.value = supervisor; isDeleteModalOpen.value = true; }
async function confirmDelete() { if (!supervisorToDelete.value) return; await supervisorsStore.removeSupervisor(supervisorToDelete.value.id); isDeleteModalOpen.value = false; supervisorToDelete.value = null; }

// --- Infrastructure Assignment Modal ---
const isInfraModalOpen = ref(false);
const supervisorToAssign = ref(null);
const selectedSubsections = ref(new Set());
const selectedAssets = ref(new Set());
const activeDepotTab = ref(null);
const activeSectionTab = ref(null);

// Watcher to reset tabs when modal opens
watch(isInfraModalOpen, (isOpen) => {
  if (isOpen) {
    if (infraTree.value.length > 0) {
      // Try to default to supervisor's depot, else first depot
      activeDepotTab.value = supervisorToAssign.value?.depot || infraTree.value[0]?.id;
    }
  }
});
// Watcher to reset section tab when depot changes
watch(activeDepotTab, (newDepotId) => {
  const depot = infraTree.value.find(d => d.id === newDepotId);
  if (depot && depot.sections.length > 0) {
    activeSectionTab.value = depot.sections[0]?.id;
  } else {
    activeSectionTab.value = null;
  }
}, { immediate: true }); // Run immediately to set initial section tab

async function openInfraModal(supervisor) {
  // Fetch tree data if not already loaded
  await infrastructureStore.fetchInfrastructureTree();
  
  supervisorToAssign.value = supervisor;
  // Initialize selections from the supervisor object
  selectedSubsections.value = new Set(supervisor.subsections || []);
  selectedAssets.value = new Set(supervisor.assets || []);
  
  // Set initial tabs
  if (infraTree.value.length > 0) {
    activeDepotTab.value = supervisor.depot || infraTree.value[0]?.id;
  }
  
  isInfraModalOpen.value = true;
}
function closeInfraModal() { isInfraModalOpen.value = false; supervisorToAssign.value = null; }

async function saveInfraAssignments() {
  if (!supervisorToAssign.value) return;
  
  // Construct the payload with only the fields the serializer expects for update
  const payload = {
    ...supervisorToAssign.value, // This includes name, designation, depot, etc.
    subsections: Array.from(selectedSubsections.value),
    assets: Array.from(selectedAssets.value),
  };
  
  await supervisorsStore.updateSupervisor(supervisorToAssign.value.id, payload);
  // Refetch supervisor data to get updated list
  await supervisorsStore.fetchSupervisors(); 
  closeInfraModal();
}

// Checkbox helper functions
function toggleAsset(assetId) {
  const set = selectedAssets.value;
  if (set.has(assetId)) set.delete(assetId);
  else set.add(assetId);
}
function getSubSectionSelectionState(subsection) {
  const totalAssets = subsection.assets.length;
  if (totalAssets === 0) {
    // If no assets, just rely on the subsection selection
    return selectedSubsections.value.has(subsection.id); // True or False
  }
  const selectedCount = subsection.assets.filter(a => selectedAssets.value.has(a.id)).length;
  if (selectedCount === 0) return false;
  if (selectedCount === totalAssets) return true;
  return 'indeterminate';
}
function handleSubSectionCheckboxChange(subsection) {
  const currentState = getSubSectionSelectionState(subsection);
  if (currentState === true) {
    // Currently all selected -> de-select all
    selectedSubsections.value.delete(subsection.id);
    (subsection.assets || []).forEach(asset => selectedAssets.value.delete(asset.id));
  } else {
    // Currently none or some selected -> select all
    selectedSubsections.value.add(subsection.id);
    (subsection.assets || []).forEach(asset => selectedAssets.value.add(asset.id));
  }
}

// --- Data Fetching ---
onMounted(() => {
  supervisorsStore.fetchSupervisors();
  if (depotsStore.depots.length === 0) { depotsStore.fetchDepots(); }
  infrastructureStore.fetchInfrastructureTree(); // Pre-fetch tree on load
});
</script>

<template>
  <div class="space-y-4">
    <p class="text-app/80 text-sm">Add/update supervisors, manage infrastructure assignments, or upload/download via Excel.</p>
    
    <div class="mt-3 grid grid-cols-[1fr_auto_1fr] items-center">
      <div class="justify-self-start flex items-center gap-2">
        <input type="file" ref="fileInput" @change="handleFileSelect" class="hidden" accept=".xlsx, .xls, .csv" />
        <button class="btn" @click="triggerFileInput">Choose File</button>
        <span v-if="selectedFile" class="text-sm text-muted truncate max-w-xs">{{ selectedFile.name }}</span>
        <button v-if="selectedFile" class="btn btn-primary" @click="handleFileUpload" :disabled="supervisorsStore.loading">
          {{ supervisorsStore.loading ? 'Uploading...' : 'Upload' }}
        </button>
        <button class="btn btn-outline" @click="exportSupervisorsExcel" :disabled="supervisorsStore.loading">Export Excel</button>
      </div>
      <div class="justify-self-end"><button class="btn" @click="openAddModal">+ Add Row</button></div>
    </div>

    <div class="rounded-2xl border-app bg-card text-app overflow-hidden">
        <div class="overflow-x-auto">
            <table class="w-full text-sm">
                <thead>
                    <tr class="text-left border-b border-app/40">
                        <th @click="toggleSort('name')" class="py-2.5 px-3 whitespace-nowrap cursor-pointer select-none text-left">Supervisor</th>
                        <th @click="toggleSort('designation')" class="py-2.5 px-3 whitespace-nowrap cursor-pointer select-none text-center">Designation</th>
                        <th @click="toggleSort('depot_display')" class="py-2.5 px-3 whitespace-nowrap cursor-pointer select-none text-center">Depot</th>
                        <th @click="toggleSort('mobile')" class="py-2.5 px-3 whitespace-nowrap cursor-pointer select-none text-center">Mobile</th>
                        <th @click="toggleSort('email')" class="py-2.5 px-3 whitespace-nowrap cursor-pointer select-none text-center">Email</th>
                        <th class="py-2.5 px-3 w-40 text-center">Actions</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-if="supervisorsStore.loading && sortedRows.length === 0"><td colspan="6" class="py-6 px-3 text-center text-muted">Loading supervisors...</td></tr>
                    <tr v-else-if="supervisorsStore.error && sortedRows.length === 0"><td colspan="6" class="py-6 px-3 text-center text-red-500">{{ supervisorsStore.error }}</td></tr>
                    <tr v-else-if="sortedRows.length === 0"><td colspan="6" class="py-6 px-3 text-center text-app/60">No supervisors found.</td></tr>
                    <tr v-for="r in sortedRows" :key="r.id" class="border-t border-app/30">
                        <td class="py-2 px-3 align-middle text-left">{{ r.name }}</td>
                        <td class="py-2 px-3 align-middle text-center">{{ r.designation || 'N/A' }}</td>
                        <td class="py-2 px-3 align-middle text-center">{{ r.depot_display || 'N/A' }}</td>
                        <td class="py-2 px-3 align-middle text-center">{{ r.mobile || 'N/A' }}</td>
                        <td class="py-2 px-3 align-middle text-center">{{ r.email || 'N/A' }}</td>
                        <td class="py-2 px-3 align-middle text-center">
                             <div class="flex items-center justify-center gap-2">
                                <button @click="openEditModal(r)" class="h-9 w-9 flex items-center justify-center rounded-lg bg-[var(--button-primary)] text-[var(--seasalt)] hover:bg-[var(--button-hover)] transition" title="Edit Supervisor"><svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6"><path stroke-linecap="round" stroke-linejoin="round" d="m16.862 4.487 1.687-1.688a1.875 1.875 0 1 1 2.652 2.652L10.582 16.07a4.5 4.5 0 0 1-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 0 1 1.13-1.897l8.932-8.931Zm0 0L19.5 7.125M18 14v4.75A2.25 2.25 0 0 1 15.75 21H5.25A2.25 2.25 0 0 1 3 18.75V8.25A2.25 2.25 0 0 1 5.25 6H10" /></svg></button>
                                <button @click="openInfraModal(r)" class="h-9 w-9 flex items-center justify-center rounded-lg bg-[var(--button-primary)] text-[var(--seasalt)] hover:bg-[var(--button-hover)] transition" title="Manage Infrastructure"><Wrench class="w-6 h-6" /></button>
                                <button @click="openDeleteModal(r)" class="inline-flex items-center justify-center h-9 w-9 rounded-md text-app border border-app hover:bg-gray-100 transition" title="Remove Supervisor"><Trash2 class="w-6 h-6" /></button>
                            </div>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
    
    <div v-if="isEditModalOpen" class="fixed inset-0 z-50 bg-black/40 flex items-center justify-center p-4">
      <div class="bg-card rounded-2xl p-6 w-full max-w-2xl space-y-4">
        <h3 class="text-lg font-semibold">{{ currentSupervisor.id ? 'Edit' : 'Add' }} Supervisor</h3>
        <div v-if="currentSupervisor" class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div><label class="block text-sm font-medium mb-1">Name</label><input v-model="currentSupervisor.name" class="field" /></div>
          <div><label class="block text-sm font-medium mb-1">Designation</label><input v-model="currentSupervisor.designation" class="field" /></div>
           <div><label class="block text-sm font-medium mb-1">Depot</label><select v-model="currentSupervisor.depot" class="field"><option :value="null">-- No Depot --</option><option v-for="depot in depotOptions" :key="depot.value" :value="depot.value">{{ depot.label }}</option></select></div>
          <div><label class="block text-sm font-medium mb-1">Mobile</label><input v-model="currentSupervisor.mobile" class="field" /></div>
          <div class="md:col-span-2"><label class="block text-sm font-medium mb-1">Email</label><input v-model="currentSupervisor.email" type="email" class="field" /></div>
        </div>
        <div class="flex justify-end gap-3 pt-4"><button @click="isEditModalOpen = false" class="btn btn-outline">Cancel</button><button @click="saveSupervisorChanges" class="btn btn-primary" :disabled="supervisorsStore.loading">{{ supervisorsStore.loading ? 'Saving...' : 'Save Changes' }}</button></div>
      </div>
    </div>
    
    <div v-if="isDeleteModalOpen" class="fixed inset-0 z-50 bg-black/40 flex items-center justify-center p-4">
      <div class="bg-card rounded-2xl p-6 w-full max-w-md space-y-4">
        <h3 class="text-lg font-semibold">Confirm Deletion</h3>
        <p>Are you sure you want to delete the supervisor "<strong>{{ supervisorToDelete?.name }}</strong>"?</p>
        <div class="flex justify-end gap-3 pt-4"><button @click="isDeleteModalOpen = false" class="btn btn-outline">Cancel</button><button @click="confirmDelete" class="btn" style="background-color: #ef4444; color: white;" :disabled="supervisorsStore.loading">{{ supervisorsStore.loading ? 'Deleting...' : 'Delete' }}</button></div>
      </div>
    </div>

    <div v-if="isInfraModalOpen" class="fixed inset-0 z-50">
      <div class="absolute inset-0 bg-black/40" @click="closeInfraModal"></div>
      <div class="absolute inset-0 grid place-items-center p-4">
        <section class="w-full max-w-6xl rounded-2xl border-app bg-card text-app shadow-2xl overflow-hidden flex flex-col" style="max-height: 90vh;">
           <header class="flex items-center justify-between px-4 py-3 border-b border-app/40">
            <div class="min-w-0"><h3 class="font-semibold truncate">Manage Infrastructure for {{ supervisorToAssign?.name }}</h3></div>
            <button class="icon-btn" title="Close" @click="closeInfraModal"><svg viewBox="0 0 24 24" class="w-5 h-5"><path fill="currentColor" d="M6.4 4.99L5 6.4L10.6 12L5 17.6L6.4 19L12 13.4L17.6 19l1.4-1.4L13.4 12L19 6.4L17.6 4.99L12 10.6z"/></svg></button>
          </header>
          
           <div v-if="infrastructureStore.loading" class="p-6 text-center text-muted" style="min-height: 60vh;">Loading infrastructure tree...</div>
          <div v-else-if="!infraTree.length" class="p-6 text-center text-muted" style="min-height: 60vh;">No infrastructure found. Please add Depots, Sections, and Assets first.</div>
          
          <div v-else class="flex-1 flex" style="min-height: 60vh;">
            <nav class="w-48 border-r border-app/40 bg-gray-50 overflow-y-auto">
               <button
                v-for="depot in infraTree" :key="depot.id"
                class="w-full text-left p-3 text-sm font-medium border-b border-app/40"
                :class="activeDepotTab === depot.id ? 'bg-white text-blue-600' : 'text-app/80 hover:bg-gray-100'"
                @click="activeDepotTab = depot.id"
               >
                {{ depot.code || depot.name }}
              </button>
            </nav>
            
            <div class="flex-1 flex flex-col">
               <div v-for="depot in infraTree" :key="depot.id" v-show="activeDepotTab === depot.id" class="flex-1 flex" style="min-height: 100%;">
                <nav class="w-64 border-r border-app/40 bg-gray-50 overflow-y-auto">
                  <div v-if="!depot.sections.length" class="p-3 text-xs text-muted">No sections in this depot.</div>
                  <button
                     v-for="section in depot.sections" :key="section.id"
                    class="w-full text-left p-3 text-sm font-medium border-b border-app/40"
                    :class="activeSectionTab === section.id ? 'bg-white text-blue-600' : 'text-app/80 hover:bg-gray-100'"
                    @click="activeSectionTab = section.id"
                  >
                    {{ section.name }}
                  </button>
                </nav>
                
                <div class="flex-1 overflow-y-auto p-4 space-y-4">
                  <div v-for="section in depot.sections" :key="section.id" v-show="activeSectionTab === section.id">
                    <div v-if="!section.subsections.length" class="p-3 text-sm text-muted">No sub-sections in this section.</div>
                     <div v-for="subsection in section.subsections" :key="subsection.id" class="mb-3">
                      <div class="flex items-center gap-2 p-2 rounded-lg bg-gray-100 border border-gray-200">
                        <input
                          type="checkbox"
                          class="h-4 w-4"
                          :checked="getSubSectionSelectionState(subsection)"
                          :indeterminate="getSubSectionSelectionState(subsection) === 'indeterminate'"
                          @change="handleSubSectionCheckboxChange(subsection)"
                        />
                        <label class-="font-semibold text-sm cursor-pointer" @click="handleSubSectionCheckboxChange(subsection)">{{ subsection.name }}</label>
                      </div>
                      <div class="pl-6 pt-2 space-y-1">
                        <div v-if="!subsection.assets.length" class="text-xs text-muted pl-2">No assets in this sub-section.</div>
                        <div v-for="asset in subsection.assets" :key="asset.id">
                          <label class="flex items-center gap-2 p-1 rounded hover:bg-gray-50 cursor-pointer">
                            <input
                              type="checkbox"
                              class="h-4 w-4"
                              :checked="selectedAssets.has(asset.id)"
                              @change="toggleAsset(asset.id)"
                            />
                            <span class="text-sm">{{ asset.name }}</span>
                          </label>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <footer class="p-3 border-t border-app/40 flex justify-end gap-3">
            <button class="btn btn-outline" @click="closeInfraModal">Cancel</button>
            <button class="btn btn-primary" @click="saveInfraAssignments" :disabled="supervisorsStore.loading">
              {{ supervisorsStore.loading ? 'Saving...' : 'Save Assignments' }}
            </button>
          </footer>
        </section>
      </div>
    </div>
    
  </div>
</template>