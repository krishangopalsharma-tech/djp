<script setup>
import { reactive, ref, computed } from 'vue'
import { useDepotStore } from '@/stores/depot.js'

const uid = () => Math.random().toString(36).slice(2) + Date.now().toString(36)
const clone = (o) => JSON.parse(JSON.stringify(o))

// Depot options from store
const depotStore = useDepotStore()
const depotOptions = computed(() =>
  depotStore.depots.map(d => ({ value: d.uid, label: d.name + (d.code ? ` (${d.code})` : '') }))
)

// Sections table (frontend-only)
const sections = reactive([])
// shape: { uid, depotUid, sectionName, subsections: [{ uid, name, assets: [...] }] }

// Modals
const showSubsModal = ref(false)
const selectedSectionIdx = ref(null)
const tempSubsections = reactive([]) // editing copy inside modal

const showAssetsModal = ref(false)
const selectedSubIdx = ref(null)
const tempAssets = reactive([]) // editing copy for a sub-section

function addSectionRow() {
  sections.push({
    uid: uid(),
    depotUid: depotOptions.value[0]?.value || '',
    sectionName: '',
    subsections: []
  })
}
function removeSectionRow(i) { sections.splice(i, 1) }

function openSubsections(i) {
  selectedSectionIdx.value = i
  const subs = sections[i].subsections || []
  tempSubsections.splice(0, tempSubsections.length, ...clone(subs))
  showSubsModal.value = true
}
function closeSubsModal() { showSubsModal.value = false; selectedSectionIdx.value = null; tempSubsections.splice(0) }
function saveSubsections() {
  if (selectedSectionIdx.value == null) return
  sections[selectedSectionIdx.value].subsections = clone(tempSubsections)
  console.log('Saved subsections for section:', sections[selectedSectionIdx.value])
  closeSubsModal()
}
function addSubRow() { tempSubsections.push({ uid: uid(), name: '', assets: [] }) }
function removeSubRow(i) { tempSubsections.splice(i, 1) }

// Assets (nested modal within subsections modal)
const ASSET_TYPES = ['Cable', 'Optical Fiber', 'Joint']

function openAssets(i) {
  selectedSubIdx.value = i
  const assets = tempSubsections[i].assets || []
  tempAssets.splice(0, tempAssets.length, ...clone(assets))
  showAssetsModal.value = true
}
function closeAssetsModal() { showAssetsModal.value = false; selectedSubIdx.value = null; tempAssets.splice(0) }
function saveAssets() {
  if (selectedSubIdx.value == null) return
  tempSubsections[selectedSubIdx.value].assets = clone(tempAssets)
  console.log('Saved assets for subsection:', tempSubsections[selectedSubIdx.value])
  closeAssetsModal()
}
function addAssetRow() {
  tempAssets.push({ uid: uid(), type: ASSET_TYPES[0], name: '', spec: '', installedAt: '', notes: '' })
}
function removeAssetRow(i) { tempAssets.splice(i, 1) }

function importCSV(where) { console.log('Import CSV clicked in', where) }
function onSavePage() { console.log('Saving sections:', clone(sections)) }
</script>

<template>
  <div class="space-y-5">
    <p class="text-app/80 text-sm">Define Sections per Depot, add Sub-sections, and track assets (cables, optical fibers, joints) in each Sub-section.</p>

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
            <tr v-if="sections.length===0">
              <td colspan="3" class="px-3 py-6 text-app/60 text-center">No sections yet — add a row below.</td>
            </tr>
            <tr v-for="(s, i) in sections" :key="s.uid" class="border-t border-app/30">
              <td class="py-2 px-3 align-top min-w-56">
                <select v-model="s.depotUid" class="field h-9">
                  <option v-for="opt in depotOptions" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
                </select>
              </td>
              <td class="py-2 px-3 align-top">
                <input v-model="s.sectionName" class="field h-9" placeholder="e.g., Central Line" />
              </td>
              <td class="py-2 px-3 align-top">
                <div class="flex flex-wrap items-center gap-2">
                  <button class="btn" @click="openSubsections(i)">Manage Sub-sections</button>
                  <button
                    class="inline-flex items-center justify-center h-9 w-9 rounded-md text-app border border-app hover:bg-black/10 transition"
                    title="Remove Section"
                    @click="removeSectionRow(i)"
                  >
                    <span class="sr-only">Remove Section</span>
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
        <button class="btn" @click="addSectionRow">+ Add Row</button>
      </div>
      <div class="justify-self-end flex items-center gap-2">
        <button class="btn" @click="importCSV('sections')">Import CSV</button>
        <button class="btn btn-primary" @click="onSavePage">Save</button>
      </div>
    </div>

    <!-- Sub-sections Modal -->
    <div v-if="showSubsModal" class="fixed inset-0 z-50">
      <div class="absolute inset-0 bg-black/40" @click="closeSubsModal"></div>
      <div class="absolute inset-0 grid place-items-center p-4">
        <section class="w-full max-w-5xl rounded-2xl border-app bg-card text-app shadow-2xl overflow-hidden">
          <header class="flex items-center justify-between px-4 py-3 border-b border-app/40">
            <div class="min-w-0">
              <h3 class="font-semibold truncate">Manage Sub-sections — {{ selectedSectionIdx!=null ? sections[selectedSectionIdx].sectionName : '' }}</h3>
              <p class="text-xs text-app/70">Add sub-sections and their assets.</p>
            </div>
            <button class="icon-btn" title="Close" @click="closeSubsModal">
              <svg viewBox="0 0 24 24" class="w-5 h-5"><path fill="currentColor" d="M6.4 4.99L5 6.4L10.6 12L5 17.6L6.4 19L12 13.4L17.6 19l1.4-1.4L13.4 12L19 6.4L17.6 4.99L12 10.6z"/></svg>
            </button>
          </header>

          <div class="p-3">
            <div class="rounded-2xl border-app bg-card text-app overflow-hidden">
              <div class="overflow-x-auto">
                <table class="w-full text-sm">
                  <thead>
                    <tr class="text-left border-b border-app/40">
                      <th class="py-2.5 px-3">Sub-section</th>
                      <th class="py-2.5 px-3 w-64">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-if="tempSubsections.length===0">
                      <td colspan="2" class="px-3 py-6 text-app/60 text-center">No sub-sections yet — add a row below.</td>
                    </tr>
                    <tr v-for="(sub, i) in tempSubsections" :key="sub.uid" class="border-t border-app/30">
                      <td class="py-2 px-3 align-top">
                        <input v-model="sub.name" class="field h-9" placeholder="e.g., Sub-section A" />
                      </td>
                      <td class="py-2 px-3 align-top">
                        <div class="flex flex-wrap items-center gap-2">
                          <button class="btn" @click="openAssets(i)">Manage Assets</button>
                          <button
                            class="inline-flex items-center justify-center h-9 w-9 rounded-md text-app border border-app hover:bg-black/10 transition"
                            title="Remove Sub-section"
                            @click="removeSubRow(i)"
                          >
                            <span class="sr-only">Remove Sub-section</span>
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

            <!-- Sub-sections actions -->
            <div class="mt-3 grid grid-cols-[1fr_auto_1fr] items-center">
              <div></div>
              <div class="justify-self-center"><button class="btn" @click="addSubRow">+ Add Row</button></div>
              <div class="justify-self-end flex items-center gap-2">
                <button class="btn" @click="importCSV('subsections')">Import CSV</button>
                <button class="btn btn-primary" @click="saveSubsections">Save</button>
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>

    <!-- Assets Modal (nested) -->
    <div v-if="showAssetsModal" class="fixed inset-0 z-[60]">
      <div class="absolute inset-0 bg-black/50" @click="closeAssetsModal"></div>
      <div class="absolute inset-0 grid place-items-center p-4">
        <section class="w-full max-w-6xl rounded-2xl border-app bg-card text-app shadow-2xl overflow-hidden">
          <header class="flex items-center justify-between px-4 py-3 border-b border-app/40">
            <div class="min-w-0">
              <h3 class="font-semibold truncate">Assets — {{ selectedSubIdx!=null ? tempSubsections[selectedSubIdx].name : '' }}</h3>
              <p class="text-xs text-app/70">Add cables, optical fiber, and joints for this sub-section.</p>
            </div>
            <button class="icon-btn" title="Close" @click="closeAssetsModal">
              <svg viewBox="0 0 24 24" class="w-5 h-5"><path fill="currentColor" d="M6.4 4.99L5 6.4L10.6 12L5 17.6L6.4 19L12 13.4L17.6 19l1.4-1.4L13.4 12L19 6.4L17.6 4.99L12 10.6z"/></svg>
            </button>
          </header>

          <div class="p-3">
            <div class="rounded-2xl border-app bg-card text-app overflow-hidden">
              <div class="overflow-x-auto">
                <table class="w-full text-sm">
                  <thead>
                    <tr class="text-left border-b border-app/40">
                      <th class="py-2.5 px-3">Asset Type</th>
                      <th class="py-2.5 px-3">Name / ID</th>
                      <th class="py-2.5 px-3">Spec / Length</th>
                      <th class="py-2.5 px-3">Installed At</th>
                      <th class="py-2.5 px-3">Notes</th>
                      <th class="py-2.5 px-3 w-16 text-center">Remove</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-if="tempAssets.length===0">
                      <td colspan="6" class="px-3 py-6 text-app/60 text-center">No assets yet — add a row below.</td>
                    </tr>
                    <tr v-for="(a, i) in tempAssets" :key="a.uid" class="border-t border-app/30">
                      <td class="py-2 px-3 align-top min-w-40">
                        <select v-model="a.type" class="field h-9">
                          <option v-for="t in ASSET_TYPES" :key="t" :value="t">{{ t }}</option>
                        </select>
                      </td>
                      <td class="py-2 px-3 align-top">
                        <input v-model="a.name" class="field h-9" placeholder="e.g., Fiber #12" />
                      </td>
                      <td class="py-2 px-3 align-top">
                        <input v-model="a.spec" class="field h-9" placeholder="e.g., 300m / 24-core" />
                      </td>
                      <td class="py-2 px-3 align-top">
                        <input v-model="a.installedAt" type="date" class="field h-9" />
                      </td>
                      <td class="py-2 px-3 align-top">
                        <textarea v-model="a.notes" class="field-textarea min-h-[44px]" placeholder="Notes..."></textarea>
                      </td>
                      <td class="py-2 px-3 align-top text-center">
                        <button
                          class="inline-flex items-center justify-center h-9 w-9 rounded-md text-app border border-app hover:bg-black/10 transition"
                          title="Remove asset"
                          @click="removeAssetRow(i)"
                        >
                          <span class="sr-only">Remove asset</span>
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

            <!-- Assets actions -->
            <div class="mt-3 grid grid-cols-[1fr_auto_1fr] items-center">
              <div></div>
              <div class="justify-self-center"><button class="btn" @click="addAssetRow">+ Add Row</button></div>
              <div class="justify-self-end flex items-center gap-2">
                <button class="btn" @click="importCSV('assets')">Import CSV</button>
                <button class="btn btn-primary" @click="saveAssets">Save</button>
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>
  </div>
</template>
