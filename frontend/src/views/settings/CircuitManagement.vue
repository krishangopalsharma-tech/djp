<script setup lang="ts">
import { reactive } from 'vue'

type Severity = 'Minor' | 'Major' | 'Critical'
type Row = {
  uid: string
  circuitId: string
  circuitName: string
  relatedEquipment: string
  severity: Severity
  details: string
}

const severityOptions: Severity[] = ['Minor', 'Major', 'Critical']

function uid() {
  return Math.random().toString(36).slice(2) + Date.now().toString(36)
}

const rows = reactive<Row[]>([
  { uid: uid(), circuitId: '', circuitName: '', relatedEquipment: '', severity: 'Minor', details: '' },
])

function addRow() {
  rows.push({ uid: uid(), circuitId: '', circuitName: '', relatedEquipment: '', severity: 'Minor', details: '' })
}

function removeRow(index: number) {
  rows.splice(index, 1)
}

function onSubmit() {
  // Frontend-only: replace with API integration later
  // eslint-disable-next-line no-console
  console.log('Submitting circuits:', JSON.parse(JSON.stringify(rows)))
  // Optional UX: keep data, or clear after submit. We keep for now.
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
            <tr v-for="(r, i) in rows" :key="r.uid" class="border-t border-app/30">
              <td class="py-2 px-3 align-top">
                <input v-model="r.circuitId" class="field h-9" placeholder="e.g., CKT-001" />
              </td>
              <td class="py-2 px-3 align-top">
                <input v-model="r.circuitName" class="field h-9" placeholder="e.g., Feeder Line A" />
              </td>
              <td class="py-2 px-3 align-top">
                <input v-model="r.relatedEquipment" class="field h-9" placeholder="e.g., Breaker-12, XFMR-3" />
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
                <!-- More visible remove button: bold X-circle icon + stronger hover -->
                <button
                  class="inline-flex items-center justify-center h-9 w-9 rounded-md text-app border border-app
                         hover:bg-[color-mix(in_oklab,_var(--card-bg),_#000_12%)] transition"
                  title="Remove row"
                  @click="removeRow(i)"
                >
                  <span class="sr-only">Remove row</span>
                  <svg viewBox="0 0 24 24" class="w-6 h-6" aria-hidden="true">
                    <!-- X-circle (filled) -->
                    <path fill="currentColor" d="M12 2a10 10 0 1 0 0 20a10 10 0 0 0 0-20Zm3.11 13.11l-1 1L12 13l-2.11 3.11l-1-1L11 12L8.89 9.89l1-1L12 11l2.11-2.11l1 1L13 12z"/>
                  </svg>
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
