<script setup>
import { onMounted, computed, ref } from 'vue';
import { useCircuitsStore } from '@/stores/circuits';
import { Trash2 } from 'lucide-vue-next';

const circuitsStore = useCircuitsStore();
const rows = computed(() => circuitsStore.circuits);

onMounted(() => {
  circuitsStore.fetchCircuits();
});

// ... (ensure all other functions now call `circuitsStore`) ...
</script>

<template>
  <div class="space-y-4">
    <div class="flex justify-between items-center">
        <p class="text-app/80 text-sm">Manage circuits with severity and equipment mapping.</p>
        <button class="btn btn-primary" @click="openAddModal">+ Add Circuit</button>
    </div>

    <!-- Table -->
    <div class="rounded-2xl border-app bg-card text-app overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead>
            <tr class="text-left border-b border-app/40">
              <th @click="toggleSort('circuit_id')" class="py-2.5 px-3 whitespace-nowrap cursor-pointer select-none">Circuit ID <span v-if="sortKey === 'circuit_id'">{{ sortDir === 'asc' ? '▲' : '▼' }}</span></th>
              <th @click="toggleSort('name')" class="py-2.5 px-3 whitespace-nowrap cursor-pointer select-none">Circuit Name <span v-if="sortKey === 'name'">{{ sortDir === 'asc' ? '▲' : '▼' }}</span></th>
              <th @click="toggleSort('related_equipment')" class="py-2.5 px-3 whitespace-nowrap cursor-pointer select-none">Related Equipment <span v-if="sortKey === 'related_equipment'">{{ sortDir === 'asc' ? '▲' : '▼' }}</span></th>
              <th @click="toggleSort('severity')" class="py-2.5 px-3 whitespace-nowrap cursor-pointer select-none">Severity <span v-if="sortKey === 'severity'">{{ sortDir === 'asc' ? '▲' : '▼' }}</span></th>
              <th class="py-2.5 px-3 whitespace-nowrap">Details</th>
              <th class="py-2.5 px-3 w-40 text-center">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="circuitsStore.loading.circuits && sortedRows.length === 0">
              <td colspan="6" class="py-6 px-3 text-center text-muted">Loading circuits...</td>
            </tr>
            <tr v-else-if="circuitsStore.error">
              <td colspan="6" class="py-6 px-3 text-center text-red-500">{{ circuitsStore.error }}</td>
            </tr>
             <tr v-else-if="sortedRows.length === 0">
              <td colspan="6" class="py-6 px-3 text-center text-app/60">No circuits defined. Add one above.</td>
            </tr>
            <tr v-for="r in sortedRows" :key="r.id" class="border-t border-app/30">
              <td class="py-2 px-3 align-top">{{ r.circuit_id }}</td>
              <td class="py-2 px-3 align-top">{{ r.name }}</td>
              <td class="py-2 px-3 align-top">{{ r.related_equipment }}</td>
              <td class="py-2 px-3 align-top">{{ r.severity }}</td>
              <td class="py-2 px-3 align-top">{{ r.details }}</td>
              <td class="py-2 px-3 align-top text-center">
                 <div class="flex items-center justify-center gap-2">
                    <button @click="openEditModal(r)" class="h-9 w-9 flex items-center justify-center rounded-lg bg-[var(--button-primary)] text-[var(--seasalt)] hover:bg-[var(--button-hover)] transition" title="Edit Circuit">
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6">
                          <path stroke-linecap="round" stroke-linejoin="round" d="m16.862 4.487 1.687-1.688a1.875 1.875 0 1 1 2.652 2.652L10.582 16.07a4.5 4.5 0 0 1-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 0 1 1.13-1.897l8.932-8.931Zm0 0L19.5 7.125M18 14v4.75A2.25 2.25 0 0 1 15.75 21H5.25A2.25 2.25 0 0 1 3 18.75V8.25A2.25 2.25 0 0 1 5.25 6H10" />
                        </svg>
                    </button>
                    <button class="inline-flex items-center justify-center h-9 w-9 rounded-md text-app border border-app hover:bg-gray-100 transition" title="Remove row" @click="openDeleteModal(r)">
                      <Trash2 class="w-6 h-6" />
                    </button>
                 </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Bottom action bar -->
    <div class="mt-3 flex justify-end">
        <div class="flex items-center gap-2">
            <input type="file" ref="fileInput" @change="handleFileSelect" class="hidden" accept=".xlsx, .xls, .csv" />
            <button class="btn" @click="triggerFileInput">Choose File</button>
            <span v-if="selectedFile" class="text-sm text-muted truncate max-w-xs">{{ selectedFile.name }}</span>
            <button v-if="selectedFile" class="btn btn-primary" @click="handleFileUpload" :disabled="circuitsStore.loading.circuits">
                {{ circuitsStore.loading.circuits ? 'Uploading...' : 'Upload' }}
            </button>
        </div>
    </div>

     <!-- Add/Edit Modal -->
    <div v-if="isModalOpen" class="fixed inset-0 z-50 bg-black/40 flex items-center justify-center p-4">
      <div class="bg-card rounded-2xl p-6 w-full max-w-3xl space-y-4">
        <h3 class="text-lg font-semibold">{{ currentCircuit.id ? 'Edit' : 'Add' }} Circuit</h3>
        <div v-if="currentCircuit" class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium mb-1">Circuit ID</label>
            <input v-model="currentCircuit.circuit_id" class="field h-9" placeholder="e.g., CKT-001" />
          </div>
           <div>
            <label class="block text-sm font-medium mb-1">Circuit Name</label>
            <input v-model="currentCircuit.name" class="field h-9" placeholder="e.g., Feeder Line A" />
          </div>
           <div class="md:col-span-2">
            <label class="block text-sm font-medium mb-1">Related Equipment</label>
            <input v-model="currentCircuit.related_equipment" class="field h-9" placeholder="e.g., Breaker-12, XFMR-3" />
          </div>
           <div>
            <label class="block text-sm font-medium mb-1">Severity</label>
            <select v-model="currentCircuit.severity" class="field h-9">
              <option v-for="s in severityOptions" :key="s" :value="s">{{ s }}</option>
            </select>
          </div>
           <div class="md:col-span-2">
            <label class="block text-sm font-medium mb-1">Details</label>
            <textarea v-model="currentCircuit.details" class="field-textarea min-h-[80px]" placeholder="Notes / details..."></textarea>
          </div>
        </div>
        <div class="flex justify-end gap-3 pt-4">
          <button @click="isModalOpen = false" class="btn btn-outline">Cancel</button>
          <button @click="saveChanges" class="btn btn-primary">Save Changes</button>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div v-if="isDeleteModalOpen" class="fixed inset-0 z-50 bg-black/40 flex items-center justify-center p-4">
      <div class="bg-card rounded-2xl p-6 w-full max-w-md space-y-4">
        <h3 class="text-lg font-semibold">Confirm Deletion</h3>
        <p>Are you sure you want to delete the circuit "{{ circuitToDelete?.name }}"? This action cannot be undone.</p>
        <div class="flex justify-end gap-3 pt-4">
          <button @click="isDeleteModalOpen = false" class="btn btn-outline">Cancel</button>
          <button @click="confirmDelete" class="btn" style="background-color: #ef4444; color: white;">Delete</button>
        </div>
      </div>
    </div>
  </div>
</template>