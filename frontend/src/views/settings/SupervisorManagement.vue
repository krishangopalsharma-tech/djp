<script setup lang="ts">
import { reactive, onMounted, computed } from 'vue'
import TagsInput from '@/components/form/TagsInput.vue'
import { useInfrastructureStore } from '@/stores/infrastructure.js' // <-- Use new store

const infrastructureStore = useInfrastructureStore()

// The table will now display data directly from the store
const rows = computed(() => infrastructureStore.supervisors)

// Fetch all necessary catalog data when the component mounts
onMounted(() => {
  infrastructureStore.fetchSupervisors()

  // Fetch related data for dropdowns if not already present
  if (infrastructureStore.depots.length === 0) {
    infrastructureStore.fetchDepots()
  }
  if (infrastructureStore.stations.length === 0) {
    infrastructureStore.fetchStations()
  }
  // We will fetch sections and assets later
})

// The functions below are for the UI and will be fully connected to the API later
function addRow() {
  console.log('TODO: Implement Add Supervisor API call')
  alert('This will be connected to the API in a future step.')
}

function removeRow(index: number) {
  console.log('TODO: Implement Remove Supervisor API call for row index', index)
  alert('This will be connected to the API in a future step.')
}

function onSubmit() {
  console.log('TODO: Implement Save All Supervisors API call')
  alert('This will be connected to the API in a future step.')
}

// These functions for populating the TagsInput dropdowns can remain for now
function stationOptions(depotId?: string) {
  if (!depotId) return []
  return infrastructureStore.stations
    .filter(s => s.depot === depotId)
    .map(s => ({ label: s.name, value: s.id }))
}
function subSectionOptions(depotId?: string) {
  // We will implement sub-sections later
  return []
}
function assetOptions(stationIds: string[] = [], subSectionIds: string[] = []) {
  // We will implement assets later
  return []
}
</script>

<template>
  <div class="space-y-4">
    <p class="text-app/80 text-sm">Add/update depot supervisors and contact details.</p>

    <!-- Table -->
    <div class="rounded-2xl border-app bg-card text-app overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-sm min-w-[900px]">
          <thead>
            <tr class="text-left border-b border-app/40">
              <th class="py-2.5 px-3 whitespace-nowrap">Supervisor</th>
              <th class="py-2.5 px-3 whitespace-nowrap">Phone</th>
              <th class="py-2.5 px-3 whitespace-nowrap">Depot</th>
              <th class="py-2.5 px-3 w-16 text-center">Remove</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="infrastructureStore.loading.supervisors">
              <td colspan="4" class="py-6 px-3 text-center text-muted">Loading supervisors...</td>
            </tr>
            <tr v-else-if="infrastructureStore.error">
              <td colspan="4" class="py-6 px-3 text-center text-red-500">{{ infrastructureStore.error }}</td>
            </tr>

            <template v-for="(r, i) in rows" :key="r.id">
              <tr class="border-t border-app/30">
                <td class="py-2 px-3 align-top">
                  <input v-model="r.name" class="field h-9" placeholder="e.g., Priya Sharma" />
                </td>
                <td class="py-2 px-3 align-top">
                  <input v-model="r.mobile" type="tel" inputmode="tel" class="field h-9" placeholder="e.g., 9876543210" />
                </td>
                <td class="py-2 px-3 align-top">
                  <select class="chip w-full" v-model="r.depot">
                    <option :value="null" disabled>Select Depot</option>
                    <option v-for="d in infrastructureStore.depots" :key="d.id" :value="d.id">{{ d.name }}</option>
                  </select>
                </td>
                <td class="py-2 px-3 align-top text-center">
                  <button class="inline-flex items-center justify-center h-9 w-9 rounded-md text-app border border-app hover:bg-[color-mix(in_oklab,_var(--card-bg),_#000_12%)] transition" title="Remove row" @click="removeRow(i)">
                    <span class="sr-only">Remove row</span>
                    <svg viewBox="0 0 24 24" class="w-6 h-6" aria-hidden="true"><path fill="currentColor" d="M12 2a10 10 0 1 0 0 20a10 10 0 0 0 0-20Zm3.11 13.11l-1 1L12 13l-2.11 3.11l-1-1L11 12L8.89 9.89l1-1L12 11l2.11-2.11l1 1L13 12z"/></svg>
                  </button>
                </td>
              </tr>
              </template>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Bottom action bar: Add (center), Import/Submit (right) -->
    <div class="mt-3 grid grid-cols-[1fr_auto_1fr] items-center">
      <!-- left spacer -->
      <div></div>
      <!-- center: Add Row -->
      <div class="justify-self-center">
        <button class="btn" @click="addRow" title="Add a new row">+ Add Row</button>
      </div>
      <!-- right: Import CSV + Submit -->
      <div class="justify-self-end flex items-center gap-2">
        <button class="btn" title="Import CSV">Import CSV</button>
        <button class="btn btn-primary" @click="onSubmit">Submit</button>
      </div>
    </div>
  </div>
</template>