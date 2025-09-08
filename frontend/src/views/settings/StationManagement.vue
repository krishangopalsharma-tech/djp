<script setup>
import { reactive, ref, computed } from 'vue'
import { useDepotStore } from '@/stores/depot.js'

// helpers
const uid = () => Math.random().toString(36).slice(2) + Date.now().toString(36)
const clone = (o) => JSON.parse(JSON.stringify(o))

// depot dropdown options
const depotStore = useDepotStore()
const depotOptions = computed(() =>
  depotStore.depots.map(d => ({ value: d.uid, label: d.name + (d.code ? ` (${d.code})` : '') }))
)

// stations table (frontend-only)
const stations = reactive([])

// modal state for per-station equipment
const showModal = ref(false)
const selectedIndex = ref(null)
const tempEquipments = reactive([])

function addStationRow() {
  stations.push({
    uid: uid(),
    depotUid: depotOptions.value[0]?.value || '',
    name: '',
    code: '',
    equipments: []
  })
}
function removeStationRow(i) { stations.splice(i, 1) }

function openManage(i) {
  selectedIndex.value = i
  tempEquipments.splice(0, tempEquipments.length, ...clone(stations[i].equipments))
  showModal.value = true
}
function closeModal() { showModal.value = false; selectedIndex.value = null; tempEquipments.splice(0) }
function saveEquipments() {
  if (selectedIndex.value == null) return
  stations[selectedIndex.value].equipments = clone(tempEquipments)
  console.log('Saved station equipments:', stations[selectedIndex.value])
  closeModal()
}

// equipment rows (modal)
function addEquipmentRow() {
  tempEquipments.push({ uid: uid(), equipmentName: '', modelNumber: '', address: '', installedAt: '', notes: '' })
}
function removeEquipmentRow(i) { tempEquipments.splice(i, 1) }
function importCSV() { console.log('Import CSV clicked (stations modal)') }

function onSave() { console.log('Saving stations:', clone(stations)) }
</script>

<template>
  <div class="space-y-5">
    <p class="text-app/80 text-sm">Map stations to depots and manage installed communication equipment.</p>

    <!-- Stations table -->
    <div class="rounded-2xl border-app bg-card text-app overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead>
            <tr class="text-left border-b border-app/40">
              <th class="py-2.5 px-3">Depot</th>
              <th class="py-2.5 px-3">Station Name</th>
              <th class="py-2.5 px-3">Station Code</th>
              <th class="py-2.5 px-3 w-[260px]">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="stations.length===0">
              <td colspan="4" class="px-3 py-6 text-app/60 text-center">No stations yet — add a row below.</td>
            </tr>
            <tr v-for="(s, i) in stations" :key="s.uid" class="border-t border-app/30">
              <td class="py-2 px-3 align-top min-w-[220px]">
                <select v-model="s.depotUid" class="field h-9">
                  <option v-for="opt in depotOptions" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
                </select>
              </td>
              <td class="py-2 px-3 align-top">
                <input v-model="s.name" class="field h-9" placeholder="e.g., Dadar" />
              </td>
              <td class="py-2 px-3 align-top">
                <input v-model="s.code" class="field h-9" placeholder="e.g., DDR" />
              </td>
              <td class="py-2 px-3 align-top">
                <div class="flex flex-wrap items-center gap-2">
                  <button class="btn" @click="openManage(i)">Manage Equipment</button>
                  <button
                    class="inline-flex items-center justify-center h-9 w-9 rounded-md text-app ring-1 ring-app/60 hover:bg-black/10 transition"
                    title="Remove station"
                    @click="removeStationRow(i)"
                  >
                    <span class="sr-only">Remove station</span>
                    <svg viewBox="0 0 24 24" class="w-6 h-6" aria-hidden="true">
                      <path fill="currentColor" d="M12 2a10 10 0 1 0 0 20a10 10 0 0 0 0-20Zm3.11 13.11l-1 1L12 13l-2.11 3.11l-1-1L11 12L8.89 9.89l1-1L12 11l2.11-2.11l1 1L13 12z"/>
                    </svg>
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
      <div></div>
      <div class="justify-self-center">
        <button class="btn" @click="addStationRow">+ Add Row</button>
      </div>
      <div class="justify-self-end flex items-center gap-2">
        <button class="btn" @click="importCSV">Import CSV</button>
        <button class="btn btn-primary" @click="onSave">Save</button>
      </div>
    </div>

    <!-- Equipment modal -->
    <div v-if="showModal" class="fixed inset-0 z-50">
      <div class="absolute inset-0 bg-black/40" @click="closeModal"></div>
      <div class="absolute inset-0 grid place-items-center p-4">
        <section class="w-full max-w-6xl rounded-2xl border-app bg-card text-app shadow-2xl overflow-hidden">
          <header class="flex items-center justify-between px-4 py-3 border-b border-app/40">
            <div class="min-w-0">
              <h3 class="font-semibold truncate">Manage Station Equipment — {{ selectedIndex!=null ? stations[selectedIndex].name : '' }}</h3>
              <p class="text-xs text-app/70">Add communication equipment details for this station.</p>
            </div>
            <button class="icon-btn" title="Close" @click="closeModal">
              <svg viewBox="0 0 24 24" class="w-5 h-5"><path fill="currentColor" d="M6.4 4.99L5 6.4L10.6 12L5 17.6L6.4 19L12 13.4L17.6 19l1.4-1.4L13.4 12L19 6.4L17.6 4.99L12 10.6z"/></svg>
            </button>
          </header>

          <div class="p-3">
            <div class="rounded-2xl border-app bg-card text-app overflow-hidden">
              <div class="overflow-x-auto">
                <table class="w-full text-sm">
                  <thead>
                    <tr class="text-left border-b border-app/40">
                      <th class="py-2.5 px-3">Equipment Name</th>
                      <th class="py-2.5 px-3">Model Number</th>
                      <th class="py-2.5 px-3">Address</th>
                      <th class="py-2.5 px-3">Date of Installation</th>
                      <th class="py-2.5 px-3">Notes</th>
                      <th class="py-2.5 px-3 w-16 text-center">Remove</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-if="tempEquipments.length===0">
                      <td colspan="6" class="px-3 py-6 text-app/60 text-center">No equipment yet — add a row below.</td>
                    </tr>
                    <tr v-for="(r, i) in tempEquipments" :key="r.uid" class="border-t border-app/30">
                      <td class="py-2 px-3 align-top">
                        <input v-model="r.equipmentName" class="field h-9" placeholder="e.g., OFC Media Converter" />
                      </td>
                      <td class="py-2 px-3 align-top">
                        <input v-model="r.modelNumber" class="field h-9" placeholder="e.g., MC-200CM" />
                      </td>
                      <td class="py-2 px-3 align-top">
                        <input v-model="r.address" class="field h-9" placeholder="e.g., Rack A, U-12" />
                      </td>
                      <td class="py-2 px-3 align-top">
                        <input v-model="r.installedAt" type="date" class="field h-9" />
                      </td>
                      <td class="py-2 px-3 align-top">
                        <textarea v-model="r.notes" class="field-textarea min-h-[44px]" placeholder="Notes..."></textarea>
                      </td>
                      <td class="py-2 px-3 align-top text-center">
                        <button
                          class="inline-flex items-center justify-center h-9 w-9 rounded-md text-app ring-1 ring-app/60 hover:bg-black/10 transition"
                          title="Remove row"
                          @click="removeEquipmentRow(i)"
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

            <div class="mt-3 grid grid-cols-[1fr_auto_1fr] items-center">
              <div></div>
              <div class="justify-self-center">
                <button class="btn" @click="addEquipmentRow">+ Add Row</button>
              </div>
              <div class="justify-self-end flex items-center gap-2">
                <button class="btn" @click="importCSV">Import CSV</button>
                <button class="btn btn-primary" @click="saveEquipments">Save</button>
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>
  </div>
</template>
