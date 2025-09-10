<script setup>
import { reactive, ref, computed, onMounted } from 'vue'
import { useInfrastructureStore } from '@/stores/infrastructure.js'
import { useUIStore } from '@/stores/ui'

const infrastructureStore = useInfrastructureStore()
const uiStore = useUIStore()

const depotOptions = computed(() =>
  infrastructureStore.depots.map(d => ({ value: d.id, label: d.name + (d.code ? ` (${d.code})` : '') }))
)
const sections = computed(() => infrastructureStore.sections)

// --- State for file upload ---
const selectedFile = ref(null)
const fileInput = ref(null)

onMounted(() => {
  if (infrastructureStore.depots.length === 0) {
    infrastructureStore.fetchDepots()
  }
  infrastructureStore.fetchSections()
})

// --- Form for adding a new section ---
const newSection = reactive({
  name: '',
  depot: null,
})

async function addSection() {
  if (!newSection.name || !newSection.depot) {
    uiStore.pushToast({type: 'error', title: 'Missing Fields', message: 'Please provide a section name and select a depot.'})
    return
  }
  await infrastructureStore.addSection({ ...newSection });
  newSection.name = '';
  newSection.depot = null;
}


// --- Delete confirmation modal ---
const isDeleteModalOpen = ref(false);
const sectionToDelete = ref(null);

function openDeleteModal(section) {
  sectionToDelete.value = section;
  isDeleteModalOpen.value = true;
}

async function confirmDelete() {
  if (!sectionToDelete.value) return;
  await infrastructureStore.removeSection(sectionToDelete.value.id);
  isDeleteModalOpen.value = false;
  sectionToDelete.value = null;
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
  await infrastructureStore.uploadSectionsFile(selectedFile.value);
  selectedFile.value = null;
  if (fileInput.value) fileInput.value.value = '';
}


// --- Placeholder for Sub-sections Modal ---
const showSubsModal = ref(false)

function openSubsections(i) {
  alert('Managing sub-sections will be implemented in a future step.');
}
function closeSubsModal() { 
  showSubsModal.value = false; 
}
</script>

<template>
  <div class="space-y-5">
    <p class="text-app/80 text-sm">Define Sections per Depot. Managing Sub-sections and Assets will be implemented next.</p>
    
    <!-- Add Section Form -->
    <div class="card">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <label class="block text-sm font-medium mb-1">Depot</label>
          <select v-model="newSection.depot" class="field h-9">
            <option :value="null" disabled>Select Depot</option>
            <option v-for="opt in depotOptions" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">New Section Name</label>
          <input v-model="newSection.name" class="field h-9" placeholder="e.g., Central Line" />
        </div>
        <div class="self-end">
          <button class="btn btn-primary w-full" @click="addSection" :disabled="infrastructureStore.loading.sections">
            {{ infrastructureStore.loading.sections ? 'Adding...' : 'Add Section' }}
          </button>
        </div>
      </div>
    </div>
    
    <!-- File Upload Section -->
     <div class="card">
       <div class="flex items-end gap-4">
          <div class="flex-grow">
            <label class="block text-sm font-medium mb-1">Upload Sections File</label>
             <p class="text-xs text-app/60 mb-2">Excel file should have two columns: 'Depot' and 'Section Name'.</p>
             <div class="flex items-center gap-2">
                <input type="file" ref="fileInput" @change="handleFileSelect" class="hidden" accept=".xlsx, .xls, .csv" />
                <button class="btn" @click="triggerFileInput">Choose File...</button>
                <span v-if="selectedFile" class="text-sm text-muted truncate max-w-xs">{{ selectedFile.name }}</span>
             </div>
          </div>
          <div>
            <button v-if="selectedFile" class="btn btn-primary" @click="handleFileUpload" :disabled="infrastructureStore.loading.sections">
              {{ infrastructureStore.loading.sections ? 'Uploading...' : 'Upload' }}
            </button>
          </div>
       </div>
    </div>


    <!-- Sections table -->
    <div class="rounded-2xl border-app bg-card text-app overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead>
            <tr class="text-left border-b border-app/40">
              <th class="py-2.5 px-3">Depot</th>
              <th class="py-2.5 px-3">Section</th>
              <th class="py-2.5 px-3 w-72">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="infrastructureStore.loading.sections && sections.length === 0">
              <td colspan="3" class="px-3 py-6 text-center text-muted">Loading sections...</td>
            </tr>
            <tr v-else-if="infrastructureStore.error">
              <td colspan="3" class="px-3 py-6 text-center text-red-500">{{ infrastructureStore.error }}</td>
            </tr>
            <tr v-else-if="sections.length===0">
              <td colspan="3" class="px-3 py-6 text-app/60 text-center">No sections yet — add one above.</td>
            </tr>
            <tr v-for="(s, i) in sections" :key="s.id" class="border-t border-app/30">
              <td class="py-2 px-3 align-top min-w-56">
                {{ s.depot_name }}
              </td>
              <td class="py-2 px-3 align-top">
                {{ s.name }}
              </td>
              <td class="py-2 px-3 align-top">
                <div class="flex flex-wrap items-center gap-2">
                  <button class="btn" @click="openSubsections(i)">Manage Sub-sections</button>
                  <button class="inline-flex items-center justify-center h-9 w-9 rounded-md text-app border border-app hover:bg-black/10 transition" title="Remove Section" @click="openDeleteModal(s)">
                    <span class="sr-only">Remove Section</span>
                    <svg viewBox="0 0 24 24" class="w-6 h-6" aria-hidden="true"><path fill="currentColor" d="M12 2a10 10 0 1 0 0 20a10 10 0 0 0 0-20Zm3.11 13.11l-1 1L12 13l-2.11 3.11l-1-1L11 12L8.89 9.89l1-1L12 11l2.11-2.11l1 1L13 12z"/></svg>
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
        <p>Are you sure you want to delete the section "{{ sectionToDelete?.name }}"? This may affect associated data.</p>
        <div class="flex justify-end gap-3 pt-4">
          <button @click="isDeleteModalOpen = false" class="btn btn-outline">Cancel</button>
          <button @click="confirmDelete" class="btn" style="background-color: #ef4444; color: white;">Delete</button>
        </div>
      </div>
    </div>


    <!-- Sub-sections Modal (Placeholder) -->
    <div v-if="showSubsModal" class="fixed inset-0 z-50">
      <div class="absolute inset-0 bg-black/40" @click="closeSubsModal"></div>
      <div class="absolute inset-0 grid place-items-center p-4">
        <section class="w-full max-w-5xl rounded-2xl border-app bg-card text-app shadow-2xl overflow-hidden">
          <header class="flex items-center justify-between px-4 py-3 border-b border-app/40">
            <div class="min-w-0">
              <h3 class="font-semibold truncate">Manage Sub-sections</h3>
              <p class="text-xs text-app/70">Add sub-sections and their assets.</p>
            </div>
            <button class="icon-btn" title="Close" @click="closeSubsModal">
              <svg viewBox="0 0 24 24" class="w-5 h-5"><path fill="currentColor" d="M6.4 4.99L5 6.4L10.6 12L5 17.6L6.4 19L12 13.4L17.6 19l1.4-1.4L13.4 12L19 6.4L17.6 4.99L12 10.6z"/></svg>
            </button>
          </header>
          <div class="p-3">
             <div class="text-center py-10 text-muted">Sub-section management will be implemented next.</div>
          </div>
        </section>
      </div>
    </div>
  </div>
</template>

