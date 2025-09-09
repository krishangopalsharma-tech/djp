<script setup lang="ts">
import { onMounted, computed } from 'vue'
import { useInfrastructureStore } from '@/stores/infrastructure.js'

const infrastructureStore = useInfrastructureStore()

// Data for the table now comes directly from the store
const rows = computed(() => infrastructureStore.circuits)

// Fetch circuit data when the component is mounted
onMounted(() => {
  infrastructureStore.fetchCircuits()
})

// The functions below are for the UI and will be fully connected to the API later
type Severity = 'Minor' | 'Major' | 'Critical'
const severityOptions: Severity[] = ['Minor', 'Major', 'Critical']

function addRow() {
  alert('This will be connected to the API in a future step.')
}

function removeRow(index: number) {
  alert('This will be connected to the API in a future step.')
}

function onSubmit() {
  alert('This will be connected to the API in a future step.')
}
</script>

<template>
  <div class="space-y-4">
    <p class="text-app/80 text-sm">Manage circuits with severity and equipment mapping.</p>

    <!-- Table -->
    <div class="rounded-2xl border-app bg-card text-app overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead>
            <tr class="text-left border-b border-app/40">
              <th class="py-2.5 px-3 whitespace-nowrap">Circuit ID</th>
              <th class="py-2.5 px-3 whitespace-nowrap">Circuit Name</th>
              <th class="py-2.5 px-3 whitespace-nowrap">Related Equipment</th>
              <th class="py-2.5 px-3 whitespace-nowrap">Severity</th>
              <th class="py-2.5 px-3 whitespace-nowrap">Details</th>
              <th class="py-2.5 px-3 w-16 text-center">Remove</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="infrastructureStore.loading.circuits">
              <td colspan="6" class="py-6 px-3 text-center text-muted">Loading circuits...</td>
            </tr>
            <tr v-else-if="infrastructureStore.error">
              <td colspan="6" class="py-6 px-3 text-center text-red-500">{{ infrastructureStore.error }}</td>
            </tr>

            <tr v-for="(r, i) in rows" :key="r.id" class="border-t border-app/30">
              <td class="py-2 px-3 align-top">
                <input v-model="r.circuit_id" class="field h-9" placeholder="e.g., CKT-001" />
              </td>
              <td class="py-2 px-3 align-top">
                <input v-model="r.name" class="field h-9" placeholder="e.g., Feeder Line A" />
              </td>
              <td class="py-2 px-3 align-top">
                <input v-model="r.related_equipment" class="field h-9" placeholder="e.g., Breaker-12, XFMR-3" />
              </td>
              <td class="py-2 px-3 align-top">
                <select v-model="r.severity" class="field h-9">
                  <option v-for="s in severityOptions" :key="s" :value="s">{{ s }}</option>
                </select>
              </td>
              <td class="py-2 px-3 align-top">
                <textarea v-model="r.details" class="field-textarea min-h-[44px]" placeholder="Notes / details..."></textarea>
              </td>
              <td class="py-2 px-3 align-top text-center">
                <button class="inline-flex items-center justify-center h-9 w-9 rounded-md text-app border border-app hover:bg-[color-mix(in_oklab,_var(--card-bg),_#000_12%)] transition" title="Remove row" @click="removeRow(i)">
                  <span class="sr-only">Remove row</span>
                  <svg viewBox="0 0 24 24" class="w-6 h-6" aria-hidden="true"><path fill="currentColor" d="M12 2a10 10 0 1 0 0 20a10 10 0 0 0 0-20Zm3.11 13.11l-1 1L12 13l-2.11 3.11l-1-1L11 12L8.89 9.89l1-1L12 11l2.11-2.11l1 1L13 12z"/></svg>
                </button>
              </td>
            </tr>
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
