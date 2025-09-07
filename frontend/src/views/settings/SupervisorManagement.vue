<script setup lang="ts">
import { reactive } from 'vue'

type Row = {
  uid: string
  depot: string
  supervisorName: string
  designation: string
  mobile: string
  email: string
}

function uid() {
  return Math.random().toString(36).slice(2) + Date.now().toString(36)
}

const rows = reactive<Row[]>([
  { uid: uid(), depot: '', supervisorName: '', designation: '', mobile: '', email: '' },
])

function addRow() {
  rows.push({ uid: uid(), depot: '', supervisorName: '', designation: '', mobile: '', email: '' })
}

function removeRow(index: number) {
  rows.splice(index, 1)
}

function onSubmit() {
  // Frontend-only placeholder — wire API later
  // eslint-disable-next-line no-console
  console.log('Submitting supervisors:', JSON.parse(JSON.stringify(rows)))
}
</script>

<template>
  <div class="space-y-4">
    <h2 class="text-xl font-semibold">Supervisor Management</h2>
    <p class="text-app/80 text-sm">Add/update depot supervisors and contact details.</p>

    <!-- Table -->
    <div class="rounded-2xl border-app bg-card text-app overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead>
            <tr class="text-left border-b border-app/40">
              <th class="py-2.5 px-3 whitespace-nowrap">Depot</th>
              <th class="py-2.5 px-3 whitespace-nowrap">Name of Supervisor</th>
              <th class="py-2.5 px-3 whitespace-nowrap">Designation</th>
              <th class="py-2.5 px-3 whitespace-nowrap">Mobile Number</th>
              <th class="py-2.5 px-3 whitespace-nowrap">Email Address</th>
              <th class="py-2.5 px-3 w-16 text-center">Remove</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(r, i) in rows" :key="r.uid" class="border-t border-app/30">
              <td class="py-2 px-3 align-top">
                <input v-model="r.depot" class="field h-9" placeholder="e.g., Depot A" />
              </td>
              <td class="py-2 px-3 align-top">
                <input v-model="r.supervisorName" class="field h-9" placeholder="e.g., Priya Sharma" />
              </td>
              <td class="py-2 px-3 align-top">
                <input v-model="r.designation" class="field h-9" placeholder="e.g., Sr. Supervisor" />
              </td>
              <td class="py-2 px-3 align-top">
                <input v-model="r.mobile" type="tel" inputmode="tel" class="field h-9" placeholder="e.g., 9876543210" />
              </td>
              <td class="py-2 px-3 align-top">
                <input v-model="r.email" type="email" class="field h-9" placeholder="name@example.com" />
              </td>
              <td class="py-2 px-3 align-top text-center">
                <!-- Clear, visible remove: X-circle icon + hover tint (matches Circuit) -->
                <button
                  class="inline-flex items-center justify-center h-9 w-9 rounded-md text-app border border-app
                         hover:bg-[color-mix(in_oklab,_var(--card-bg),_#000_12%)] transition"
                  title="Remove row"
                  @click="removeRow(i)"
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
