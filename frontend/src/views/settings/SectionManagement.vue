<script setup>
import { reactive, ref, computed, onMounted } from 'vue';
import { useSectionsStore } from '@/stores/sections';
import { useDepotsStore } from '@/stores/depots';
import { useUIStore } from '@/stores/ui';
import { Wrench, Trash2 } from 'lucide-vue-next';

// Initialize stores
const sectionsStore = useSectionsStore();
const depotsStore = useDepotsStore();
const uiStore = useUIStore();

// Data from stores
const sections = computed(() => sectionsStore.sections);
const depotOptions = computed(() =>
  (depotsStore.depots || []).map(d => ({ value: d.id, label: d.code || d.name }))
);

// --- Sorting ---
const sortKey = ref('name');
const sortDir = ref('asc');
const sortedSections = computed(() => {
  const data = [...sections.value];
  return data.sort((a, b) => {
    const modifier = sortDir.value === 'asc' ? 1 : -1;
    const valA = sortKey.value === 'depot_display' ? (a.depot_display || '') : (a[sortKey.value] || '');
    const valB = sortKey.value === 'depot_display' ? (b.depot_display || '') : (b[sortKey.value] || '');
    if (valA < valB) return -1 * modifier;
    if (valA > valB) return 1 * modifier;
    return 0;
  });
});
function toggleSort(key) {
  if (sortKey.value === key) {
    sortDir.value = sortDir.value === 'asc' ? 'desc' : 'asc';
  } else {
    sortKey.value = key;
    sortDir.value = 'asc';
  }
}

// --- Fetch initial data ---
onMounted(() => {
  sectionsStore.fetchSections();
  // Ensure depots are loaded for the dropdown
  if (depotsStore.depots.length === 0) {
    depotsStore.fetchDepots();
  }
});

// --- Add Form ---
const newSection = reactive({ name: '', depot: null });
async function addSection() {
  if (!newSection.name || !newSection.depot) {
    uiStore.pushToast({type: 'error', title: 'Missing Fields', message: 'Please provide a section name and select a depot.'});
    return;
  }
  await sectionsStore.addSection({ ...newSection });
  newSection.name = ''; // Clear name after adding
  // Keep depot selected
}

// --- Edit Modal ---
const isEditModalOpen = ref(false);
const sectionToEdit = ref(null);
function openEditModal(section) {
  // Ensure we set the depot ID correctly for the select dropdown
  sectionToEdit.value = { ...section, depot: section.depot };
  isEditModalOpen.value = true;
}
async function saveSectionChanges() {
  if (!sectionToEdit.value) return;
  await sectionsStore.updateSection(sectionToEdit.value.id, sectionToEdit.value);
  isEditModalOpen.value = false;
  sectionToEdit.value = null;
}

// --- Delete Modal ---
const isDeleteModalOpen = ref(false);
const sectionToDelete = ref(null);
function openDeleteModal(section) {
  sectionToDelete.value = section;
  isDeleteModalOpen.value = true;
}
async function confirmDelete() {
  if (!sectionToDelete.value) return;
  await sectionsStore.removeSection(sectionToDelete.value.id);
  isDeleteModalOpen.value = false;
  sectionToDelete.value = null;
}

// --- File Upload ---
const selectedFile = ref(null);
const fileInput = ref(null);
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
        uiStore.pushToast({ type: 'error', title: 'No File', message: 'Please select a file to upload.' });
        return;
    }
    await sectionsStore.uploadSectionsFile(selectedFile.value);
    selectedFile.value = null;
    if (fileInput.value) fileInput.value.value = '';
}

// --- Sub-sections & Assets Modal ---
const clone = (o) => JSON.parse(JSON.stringify(o));
const isSubSectionModalOpen = ref(false);
const selectedSection = ref(null);
const tempSubsections = ref([]); // Use ref for reactivity
const originalSubsections = ref([]);

async function openSubsectionsModal(section) {
  selectedSection.value = section;
  await sectionsStore.fetchSubsectionsForSection(section.id); // Fetch data first
  const subsections = sectionsStore.sectionSubsections; // Use the fetched data
  originalSubsections.value = clone(subsections);
  // Ensure assets array exists
  tempSubsections.value = clone(subsections.map(ss => ({ ...ss, assets: ss.assets || [] })));
  isSubSectionModalOpen.value = true;
}

function closeSubsectionsModal() {
    isSubSectionModalOpen.value = false;
    selectedSection.value = null;
    sectionsStore.sectionSubsections = []; // Clear store data on close
}

async function saveSubsectionsAndAssets() {
    if (!selectedSection.value) return;
    uiStore.pushToast({ type: 'info', title: 'Saving...', message: 'Processing sub-sections and assets.' });

    const originalSubMap = new Map(originalSubsections.value.map(s => [s.id, s]));
    const currentSubMap = new Map(tempSubsections.value.filter(s => s.id).map(s => [s.id, s]));
    const promises = [];

    // --- Process Deletions First ---
    for (const originalSub of originalSubsections.value) {
        if (!currentSubMap.has(originalSub.id)) {
            promises.push(sectionsStore.removeSubSection(originalSub.id));
        } else {
            // Check for asset deletions within existing subsections
            const currentSub = currentSubMap.get(originalSub.id);
            const originalAssetIds = new Set((originalSub.assets || []).map(a => a.id));
            const currentAssetIds = new Set((currentSub.assets || []).filter(a => a.id).map(a => a.id));
            for (const originalAssetId of originalAssetIds) {
                if (!currentAssetIds.has(originalAssetId)) {
                    promises.push(sectionsStore.removeAsset(originalAssetId));
                }
            }
        }
    }
    // Wait for deletions before proceeding
    await Promise.all(promises);
    promises.length = 0;

    // --- Process Updates and Creations ---
    for (const sub of tempSubsections.value) {
        if (sub.id) { // Existing sub-section
            const originalSub = originalSubMap.get(sub.id);
            if (originalSub && originalSub.name !== sub.name) {
                promises.push(sectionsStore.updateSubSection(sub.id, { name: sub.name }));
            }
            // Process assets for existing sub-section
            for (const asset of (sub.assets || [])) {
                if (asset.id) { // Existing asset
                    const originalAsset = originalSub?.assets?.find(a => a.id === asset.id);
                    if (originalAsset && JSON.stringify(originalAsset) !== JSON.stringify(asset)) {
                         promises.push(sectionsStore.updateAsset(asset.id, asset));
                    }
                } else { // New asset
                    promises.push(sectionsStore.addAsset({ ...asset, subsection: sub.id }));
                }
            }
        } else { // New sub-section
            // Use await here to get the new ID for subsequent asset creation
            const newSubSectionData = await sectionsStore.addSubSection({ name: sub.name, section: selectedSection.value.id });
            if (newSubSectionData && newSubSectionData.id) {
                for (const asset of (sub.assets || [])) {
                   promises.push(sectionsStore.addAsset({ ...asset, subsection: newSubSectionData.id }));
                }
            }
        }
    }

    await Promise.all(promises);

    uiStore.pushToast({ type: 'success', title: 'Save Complete', message: 'Infrastructure updated successfully.' });
    await sectionsStore.fetchSections(); // Refresh main list
    closeSubsectionsModal();
}


function addSubSectionRow() { tempSubsections.value.push({ name: '', assets: [] }); }
function removeSubSectionRow(index) { tempSubsections.value.splice(index, 1); }
function addAssetRow(subSection) { if (!subSection.assets) { subSection.assets = []; } subSection.assets.push({ name: '', quantity: null, unit: '' }); } // Default quantity null
function removeAssetRow(subSection, assetIndex) { subSection.assets.splice(assetIndex, 1); }
</script>

<template>
  <div class="space-y-5">
    <p class="text-app/80 text-sm">Define Sections per Depot, manage Sub-sections and their Assets, or upload a master file with the complete hierarchy.</p>

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
          <button class="btn btn-primary w-full" @click="addSection" :disabled="sectionsStore.loading">
            {{ sectionsStore.loading ? 'Adding...' : 'Add Section' }}
          </button>
        </div>
      </div>
    </div>

    <div class="card">
       <div class="flex items-end gap-4">
          <div class="flex-grow">
            <label class="block text-sm font-medium mb-1">Upload Master Infrastructure File</label>
             <p class="text-xs text-app/60 mb-2">Excel/CSV: Depot, Section, Sub-section, Asset, Quantity, Unit. Depots must exist.</p>
             <div class="flex items-center gap-2">
                <input type="file" ref="fileInput" @change="handleFileSelect" class="hidden" accept=".xlsx, .xls, .csv" />
                <button class="btn" @click="triggerFileInput">Choose File...</button>
                <span v-if="selectedFile" class="text-sm text-muted truncate max-w-xs">{{ selectedFile.name }}</span>
             </div>
          </div>
          <div>
            <button v-if="selectedFile" class="btn btn-primary" @click="handleFileUpload" :disabled="sectionsStore.loading">
              {{ sectionsStore.loading ? 'Uploading...' : 'Upload Master File' }}
            </button>
          </div>
       </div>
    </div>

    <div class="rounded-2xl border-app bg-card text-app overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead>
            <tr class="text-left border-b border-app/40">
              <th @click="toggleSort('depot_display')" class="py-2.5 px-3 text-left cursor-pointer select-none">Depot <span v-if="sortKey === 'depot_display'">{{ sortDir === 'asc' ? '▲' : '▼' }}</span></th>
              <th @click="toggleSort('name')" class="py-2.5 px-3 text-center cursor-pointer select-none">Section <span v-if="sortKey === 'name'">{{ sortDir === 'asc' ? '▲' : '▼' }}</span></th>
              <th class="py-2.5 px-3 text-center">Sub-sections</th>
              <th class="py-2.5 px-3 text-center">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="sectionsStore.loading && sortedSections.length === 0">
              <td colspan="4" class="px-3 py-6 text-center text-muted">Loading sections...</td>
            </tr>
            <tr v-else-if="sectionsStore.error && sortedSections.length === 0"> <td colspan="4" class="px-3 py-6 text-center text-red-500">{{ sectionsStore.error }}</td>
            </tr>
            <tr v-else-if="sortedSections.length === 0">
              <td colspan="4" class="px-3 py-6 text-app/60 text-center">No sections yet — add one above.</td>
            </tr>
            <tr v-for="s in sortedSections" :key="s.id" class="border-t border-app/30">
              <td class="py-2 px-3 align-middle text-left">{{ s.depot_display }}</td>
              <td class="py-2 px-3 align-middle text-center">{{ s.name }}</td>
              <td class="py-2 px-3 align-middle text-center">{{ s.subsection_count || 0 }}</td>
              <td class="py-2 px-3 align-middle">
                <div class="flex flex-wrap items-center justify-center gap-2">
                   <button class="h-9 w-9 flex items-center justify-center rounded-lg bg-[var(--button-primary)] text-[var(--seasalt)] hover:bg-[var(--button-hover)] transition" @click="openEditModal(s)" title="Edit Section">
                     <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6"><path stroke-linecap="round" stroke-linejoin="round" d="m16.862 4.487 1.687-1.688a1.875 1.875 0 1 1 2.652 2.652L10.582 16.07a4.5 4.5 0 0 1-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 0 1 1.13-1.897l8.932-8.931Zm0 0L19.5 7.125M18 14v4.75A2.25 2.25 0 0 1 15.75 21H5.25A2.25 2.25 0 0 1 3 18.75V8.25A2.25 2.25 0 0 1 5.25 6H10" /></svg>
                   </button>
                   <button class="h-9 w-9 flex items-center justify-center rounded-lg bg-[var(--button-primary)] text-[var(--seasalt)] hover:bg-[var(--button-hover)] transition" @click="openSubsectionsModal(s)" title="Manage Sub-sections & Assets">
                     <Wrench class="w-6 h-6" />
                   </button>
                  <button class="inline-flex items-center justify-center h-9 w-9 rounded-md text-app border border-app hover:bg-black/10 transition" title="Remove Section" @click="openDeleteModal(s)">
                    <Trash2 class="w-6 h-6" />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-if="isEditModalOpen" class="fixed inset-0 z-50 bg-black/40 flex items-center justify-center p-4">
      <div class="bg-card rounded-2xl p-6 w-full max-w-md space-y-4">
        <h3 class="text-lg font-semibold">Edit Section</h3>
        <div v-if="sectionToEdit" class="space-y-4">
          <div>
            <label class="block text-sm font-medium mb-1">Section Name</label>
            <input v-model="sectionToEdit.name" class="field h-9" />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Depot</label>
            <select v-model="sectionToEdit.depot" class="field h-9">
              <option :value="null" disabled>Select Depot</option>
              <option v-for="opt in depotOptions" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
            </select>
          </div>
        </div>
        <div class="flex justify-end gap-3 pt-4">
          <button @click="isEditModalOpen = false" class="btn btn-outline">Cancel</button>
          <button @click="saveSectionChanges" class="btn btn-primary" :disabled="sectionsStore.loading">{{ sectionsStore.loading ? 'Saving...' : 'Save Changes' }}</button>
        </div>
      </div>
    </div>

    <div v-if="isDeleteModalOpen" class="fixed inset-0 z-50 bg-black/40 flex items-center justify-center p-4">
      <div class="bg-card rounded-2xl p-6 w-full max-w-md space-y-4">
        <h3 class="text-lg font-semibold">Confirm Deletion</h3>
        <p>Are you sure you want to delete the section "<strong>{{ sectionToDelete?.name }}</strong>"? This will also delete its sub-sections and assets.</p>
        <div class="flex justify-end gap-3 pt-4">
          <button @click="isDeleteModalOpen = false" class="btn btn-outline">Cancel</button>
          <button @click="confirmDelete" class="btn" style="background-color: #ef4444; color: white;" :disabled="sectionsStore.loading">{{ sectionsStore.loading ? 'Deleting...' : 'Delete' }}</button>
        </div>
      </div>
    </div>

    <div v-if="isSubSectionModalOpen" class="fixed inset-0 z-50">
      <div class="absolute inset-0 bg-black/40" @click="closeSubsectionsModal"></div>
      <div class="absolute inset-0 grid place-items-center p-4">
        <section class="w-full max-w-4xl rounded-2xl border-app bg-card text-app shadow-2xl overflow-hidden flex flex-col" style="max-height: 90vh;">
          <header class="flex items-center justify-between px-4 py-3 border-b border-app/40">
            <div class="min-w-0">
              <h3 class="font-semibold truncate">Manage Sub-sections & Assets for "{{ selectedSection?.name }}"</h3>
            </div>
            <button class="icon-btn" title="Close" @click="closeSubsectionsModal">
              <svg viewBox="0 0 24 24" class="w-5 h-5"><path fill="currentColor" d="M6.4 4.99L5 6.4L10.6 12L5 17.6L6.4 19L12 13.4L17.6 19l1.4-1.4L13.4 12L19 6.4L17.6 4.99L12 10.6z"/></svg>
            </button>
          </header>
          <div class="p-3 flex-1 overflow-y-auto space-y-3">
            <div v-if="sectionsStore.loading" class="text-center py-10 text-muted">Loading sub-sections...</div>
            <div v-else-if="tempSubsections.length === 0" class="text-center py-10 text-muted">No sub-sections yet. Add one below.</div>
            <div v-for="(sub, subIndex) in tempSubsections" :key="sub.id || `new-${subIndex}`" class="card">
              <div class="flex items-center gap-2">
                <input v-model="sub.name" class="field h-9 flex-grow" placeholder="Enter sub-section name"/>
                <button class="inline-flex items-center justify-center h-9 w-9 rounded-md text-app border border-app hover:bg-gray-100 transition" title="Remove Sub-section" @click="removeSubSectionRow(subIndex)">
                   <Trash2 class="w-5 h-5" />
                </button>
              </div>
              <div class="mt-3 pl-4 border-l-2 border-app/40">
                <h4 class="text-xs font-semibold text-app/80 mb-2">Assets in this Sub-section</h4>
                <table class="w-full text-sm">
                  <tr v-for="(asset, assetIndex) in sub.assets" :key="asset.id || `new-asset-${assetIndex}`">
                    <td class="py-1 pr-2"><input v-model="asset.name" class="field h-8" placeholder="Asset Name"></td>
                    <td class="py-1 pr-2 w-28"><input v-model.number="asset.quantity" type="number" step="0.01" class="field h-8" placeholder="Qty"></td>
                    <td class="py-1 pr-2 w-28"><input v-model="asset.unit" class="field h-8" placeholder="Unit"></td>
                    <td class="py-1 w-10 text-center">
                      <button @click="removeAssetRow(sub, assetIndex)" class="text-app/50 hover:text-red-500 text-xl font-bold">&times;</button>
                    </td>
                  </tr>
                </table>
                <button @click="addAssetRow(sub)" class="text-xs btn btn-sm mt-2">+ Add Asset</button>
              </div>
            </div>
          </div>
          <footer class="p-3 border-t border-app/40 grid grid-cols-[1fr_auto_1fr] items-center">
            <div></div>
            <div class="justify-self-center"><button class="btn" @click="addSubSectionRow">+ Add Sub-section</button></div>
            <div class="justify-self-end"><button class="btn btn-primary" @click="saveSubsectionsAndAssets">Save All Changes</button></div>
          </footer>
        </section>
      </div>
    </div>
  </div>
</template>