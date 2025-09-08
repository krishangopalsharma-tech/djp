<script setup lang="ts">
import { reactive, onMounted } from 'vue'
import TagsInput from '@/components/form/TagsInput.vue'
import { useCatalogStore } from '@/stores/catalog.js'

type Row = {
  uid: string
  depot?: string
  depotId?: string
  supervisorName: string
  designation: string
  mobile: string
  email: string
  stations?: string[]
  subSections?: string[]
  assets?: string[]
}

function uid() {
  return Math.random().toString(36).slice(2) + Date.now().toString(36)
}

const rows = reactive<Row[]>([
  { uid: uid(), depotId: '', supervisorName: '', designation: '', mobile: '', email: '', stations: [], subSections: [], assets: [] },
])

function addRow() {
  rows.push({ uid: uid(), depotId: '', supervisorName: '', designation: '', mobile: '', email: '', stations: [], subSections: [], assets: [] })
}

function removeRow(index: number) {
  rows.splice(index, 1)
}

function onSubmit() {
  // Frontend-only placeholder — wire API later
  // eslint-disable-next-line no-console
  console.log('Submitting supervisors:', JSON.parse(JSON.stringify(rows)))
}

const catalog = useCatalogStore()
function stationOptions(depotId?: string) {
  return catalog.stationsForDepot(depotId || '').map(s => ({ label: s.name, value: s.id }))
}
function subSectionOptions(depotId?: string) {
  return catalog.subSectionsForDepot(depotId || '').map(s => ({ label: s.name, value: s.id }))
}
function assetOptions(stationIds: string[] = [], subSectionIds: string[] = []) {
  return catalog.assetsFor(stationIds, subSectionIds).map(a => ({ label: a.name, value: a.id }))
}

onMounted(() => {
  for (const r of rows) {
    if (!r.stations) r.stations = []
    if (!r.subSections) r.subSections = []
    if (!r.assets) r.assets = []
  }
})
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
            <template v-for="(r, i) in rows" :key="r.uid">
              <!-- Row 1: compact line -->
              <tr class="border-t border-app/30">
                <td class="py-2 px-3 align-top">
                  <input v-model="r.supervisorName" class="field h-9" placeholder="e.g., Priya Sharma" />
                </td>
                <td class="py-2 px-3 align-top">
                  <input v-model="r.mobile" type="tel" inputmode="tel" class="field h-9" placeholder="e.g., 9876543210" />
                </td>
                <td class="py-2 px-3 align-top">
                  <select class="chip w-full" v-model="r.depotId">
                    <option :value="''" disabled>Select Depot</option>
                    <option v-for="d in catalog.depots" :key="d.id" :value="d.id">{{ d.name }}</option>
                  </select>
                </td>
                <td class="py-2 px-3 align-top text-center">
                  <button
                    class="inline-flex items-center justify-center h-9 w-9 rounded-md text-app border border-app hover:bg-[color-mix(in_oklab,_var(--card-bg),_#000_12%)] transition"
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

              <!-- Row 2: tag fields -->
              <tr class="border-b border-app/30 bg-[var(--card-bg)]/60">
                <td class="py-3 px-3" :colspan="4">
                  <div class="grid gap-3 md:grid-cols-2 lg:grid-cols-3">
                    <!-- Stations -->
                    <div>
                      <div class="text-xs font-medium mb-1">Stations</div>
                      <TagsInput
                        v-model="r.stations"
                        :options="stationOptions(r.depotId)"
                        placeholder="Add stations…"
                        :disabled="!r.depotId"
                      />
                      <p v-if="!r.depotId" class="text-xs opacity-70 mt-1">Pick a depot to list stations.</p>
                    </div>
                    <!-- Sub-sections -->
                    <div>
                      <div class="text-xs font-medium mb-1">Sub-sections</div>
                      <TagsInput
                        v-model="r.subSections"
                        :options="subSectionOptions(r.depotId)"
                        placeholder="Add sub-sections…"
                        :disabled="!r.depotId"
                      />
                      <p v-if="!r.depotId" class="text-xs opacity-70 mt-1">Pick a depot to list sub-sections.</p>
                    </div>
                    <!-- Assets -->
                    <div>
                      <div class="text-xs font-medium mb-1">Assets</div>
                      <TagsInput
                        v-model="r.assets"
                        :options="assetOptions(r.stations || [], r.subSections || [])"
                        placeholder="Select assets…"
                        :disabled="!(r.stations?.length && r.subSections?.length)"
                      />
                      <p class="text-xs opacity-70 mt-1">Options combine selected Stations × Sub-sections.</p>
                    </div>
                  </div>
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
