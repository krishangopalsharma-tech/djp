<script setup>
import { reactive, ref, onMounted } from 'vue' // <-- Add onMounted
import { useInfrastructureStore } from '@/stores/infrastructure.js'

const clone = (o) => JSON.parse(JSON.stringify(o))

// Store state
const depotStore = useInfrastructureStore()
// No longer need to reference `depots` directly from the store here

// Fetch data when the component is first mounted
onMounted(() => {
  depotStore.fetchDepots()
})


// New depot inline form
const newDepot = reactive({ name: '', code: '', location: '' })

// Modal state for selected depot equipments
const showModal = ref(false)
const selectedDepotIndex = ref(null)
const tempEquipments = reactive([]) // local edit list inside modal

function addDepot() {
  if (!newDepot.name.trim()) return
  // Call the store action instead of modifying state directly
  depotStore.addDepot({
    name: newDepot.name.trim(),
    code: newDepot.code.trim(),
    location: newDepot.location.trim(),
  })
  newDepot.name = ''; newDepot.code = ''; newDepot.location = ''
}

function removeDepot(depotId) {
  // Call the store action with the depot's ID
  depotStore.removeDepot(depotId)
}

function openManage(index) {
  selectedDepotIndex.value = index
  const eq = depotStore.depots[index]?.equipments ?? []
  tempEquipments.splice(0, tempEquipments.length, ...clone(eq))
  showModal.value = true
}
function closeModal() {
  showModal.value = false
  selectedDepotIndex.value = null
  tempEquipments.splice(0)
}
function saveEquipments() {
  if (selectedDepotIndex.value == null) return
  const targetId = depotStore.depots[selectedDepotIndex.value].id
  depotStore.setEquipments(targetId, clone(tempEquipments))
  // eslint-disable-next-line no-console
  console.log('Saved equipments for depot:', depotStore.depots[selectedDepotIndex.value])
  closeModal()
}

// Equipment rows inside modal
const uid = () => Math.random().toString(36).slice(2) + Date.now().toString(36)
function addEquipmentRow() {
  tempEquipments.push({
    uid: uid(),
    equipment: '',
    model: '',
    assetId: '',
    location: '',
    notes: ''
  })
}
function removeEquipmentRow(i) {
  tempEquipments.splice(i, 1)
}
function importCSV() {
  // TODO: parse & merge rows
  // eslint-disable-next-line no-console
  console.log('Import CSV clicked (Depot modal)')
}
</script>

<template>
  <div class="space-y-5">
    <p class="text-app/80 text-sm">Add depots first, then manage measuring equipment per depot.</p>

    <!-- New Depot form -->
    <div class="card">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <label class="block text-sm font-medium mb-1">Depot Name</label>
          <input v-model="newDepot.name" class="field" placeholder="e.g., West Yard" />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">Depot Code</label>
          <input v-model="newDepot.code" class="field" placeholder="e.g., WY-01" />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">Location</label>
          <input v-model="newDepot.location" class="field" placeholder="e.g., Sector 12" />
        </div>
      </div>
      <div class="mt-3 flex justify-end">
        <button class="btn btn-primary" @click="addDepot">Add Depot</button>
      </div>
    </div>

    <!-- Depots list -->
    <div class="rounded-2xl border-app bg-card text-app overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead>
            <tr class="text-left border-b border-app/40">
              <th class="py-2.5 px-3">Depot Name</th>
              <th class="py-2.5 px-3">Code</th>
              <th class="py-2.5 px-3">Location</th>
              <th class="py-2.5 px-3 whitespace-nowrap">Equipment Count</th>
              <th class="py-2.5 px-3 w-[240px]">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="depotStore.loading">
                <td colspan="5" class="px-3 py-6 text-center text-muted">Loading...</td>
            </tr>
            <tr v-else-if="depotStore.error">
                <td colspan="5" class="px-3 py-6 text-center text-red-500">{{ depotStore.error }}</td>
            </tr>
            <tr v-else-if="depotStore.depots.length===0">
                <td colspan="5" class="px-3 py-6 text-app/60 text-center">No depots yet — add one above.</td>
            </tr>
            <tr v-for="(d, i) in depotStore.depots" :key="d.id" class="border-t border-app/30">
              <td class="py-2 px-3 align-middle">{{ d.name }}</td>
              <td class="py-2 px-3 align-middle">{{ d.code || '—' }}</td>
              <td class="py-2 px-3 align-middle">{{ d.location || '—' }}</td>
              <td class="py-2 px-3 align-middle">{{ d.equipments?.length || 0 }}</td>
              <td class="py-2 px-3 align-middle">
                <div class="flex flex-wrap items-center gap-2">
                  <button class="btn" @click="openManage(i)">Manage Equipment</button>
                  <button
                    class="inline-flex items-center justify-center h-9 w-9 rounded-md text-app border border-app hover:bg-[color-mix(in_oklab,_var(--card-bg),_#000_12%)] transition"
                    title="Remove depot"
                    @click="removeDepot(d.id)"
                  >
                    <span class="sr-only">Remove depot</span>
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

    <!-- Equipment Modal -->
    <div v-if="showModal" class="fixed inset-0 z-50">
      <div class="absolute inset-0 bg-black/40" @click="closeModal" />
      <div class="absolute inset-0 grid place-items-center p-4">
        <section class="w-full max-w-6xl rounded-2xl border-app bg-card text-app shadow-2xl overflow-hidden">
          <!-- Modal header -->
          <header class="flex items-center justify-between px-4 py-3 border-b border-app/40">
            <div class="min-w-0">
              <h3 class="font-semibold truncate">
                Manage Equipment — {{ selectedDepotIndex!=null ? depotStore.depots[selectedDepotIndex].name : '' }}
              </h3>
              <p class="text-xs text-app/70">Add multiple measuring equipment and their location inside this depot.</p>
            </div>
            <button class="icon-btn" title="Close" @click="closeModal">
              <svg viewBox="0 0 24 24" class="w-5 h-5"><path fill="currentColor" d="M6.4 4.99L5 6.4L10.6 12L5 17.6L6.4 19L12 13.4L17.6 19l1.4-1.4L13.4 12L19 6.4L17.6 4.99L12 10.6z"/></svg>
            </button>
          </header>

          <!-- Equipment table -->
          <div class="p-3">
            <div class="rounded-2xl border-app bg-card text-app overflow-hidden">
              <div class="overflow-x-auto">
                <table class="w-full text-sm">
                  <thead>
                    <tr class="text-left border-b border-app/40">
                      <th class="py-2.5 px-3 whitespace-nowrap">Measuring Equipment</th>
                      <th class="py-2.5 px-3 whitespace-nowrap">Model / Type</th>
                      <th class="py-2.5 px-3 whitespace-nowrap">Asset / Serial ID</th>
                      <th class="py-2.5 px-3 whitespace-nowrap">Location in Depot</th>
                      <th class="py-2.5 px-3 whitespace-nowrap">Notes</th>
                      <th class="py-2.5 px-3 w-16 text-center">Remove</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-if="tempEquipments.length===0">
                      <td colspan="6" class="px-3 py-6 text-app/60 text-center">No equipment yet — add a row below.</td>
                    </tr>
                    <tr v-for="(r, i) in tempEquipments" :key="r.uid" class="border-t border-app/30">
                      <td class="py-2 px-3 align-top">
                        <input v-model="r.equipment" class="field h-9" placeholder="e.g., Multimeter" />
                      </td>
                      <td class="py-2 px-3 align-top">
                        <input v-model="r.model" class="field h-9" placeholder="e.g., Fluke 117" />
                      </td>
                      <td class="py-2 px-3 align-top">
                        <input v-model="r.assetId" class="field h-9" placeholder="e.g., SN-123456" />
                      </td>
                      <td class="py-2 px-3 align-top">
                        <input v-model="r.location" class="field h-9" placeholder="e.g., Bay 3, Shelf A" />
                      </td>
                      <td class="py-2 px-3 align-top">
                        <textarea v-model="r.notes" class="field-textarea min-h-[44px]" placeholder="Calibration due, assigned to team, etc."></textarea>
                      </td>
                      <td class="py-2 px-3 align-top text-center">
                        <button
                          class="inline-flex items-center justify-center h-9 w-9 rounded-md text-app ring-1 ring-app/60
                                 hover:bg-[color-mix(in_oklab,_var(--surface),_#000_12%)] transition"
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

            <!-- Bottom actions inside modal -->
            <div class="mt-3 grid grid-cols-[1fr_auto_1fr] items-center">
              <div></div>
              <div class="justify-self-center">
                <button class="btn" @click="addEquipmentRow">+ Add Row</button>
              </div>
              <div class="justify-self-end flex items-center gap-2">
                <button class="btn" @click="importCSV">Import CSV</button>
                <button class="btn btn-primary" @click="saveEquipments">Submit</button>
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>
  </div>
</template>