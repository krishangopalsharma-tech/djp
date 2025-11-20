<script setup>
import { reactive, ref, computed, watch, onMounted } from 'vue'
import InputText from '@/components/form/InputText.vue'
import DateTime from '@/components/form/DateTime.vue'
import SearchSelect from '@/components/form/SearchSelect.vue'
import TagsInput from '@/components/form/TagsInput.vue'
import { useUIStore } from '@/stores/ui'
import RecentFailures from '@/components/RecentFailures.vue'
import NotificationModal from '@/components/NotificationModal.vue'
import { useInfrastructureStore } from '@/stores/infrastructure_lists';
import { useFailureStore } from '@/stores/failures';
import { useRecentFailuresStore } from '@/stores/recentFailures';
import { useTelegramStore } from '@/stores/telegram';
import { useAttachmentStore } from '@/stores/attachments';
import FailureAttachment from '@/components/FailureAttachment.vue'

const ui = useUIStore()
const infrastructureStore = useInfrastructureStore()
const failureStore = useFailureStore()
const recentFailuresStore = useRecentFailuresStore()
const telegramStore = useTelegramStore()
const attachmentStore = useAttachmentStore()

const editingFailureId = ref(null)
const isArchiveModalOpen = ref(false)
const failureToArchive = ref(null)
const archiveReason = ref('')
const isNotifyModalOpen = ref(false)
const failureToNotify = ref(null)

onMounted(() => {
  Promise.all([
    infrastructureStore.fetchDepots(),
    infrastructureStore.fetchCircuits(),
    infrastructureStore.fetchStations(),
    infrastructureStore.fetchSections(),
    infrastructureStore.fetchSubSections(),
    infrastructureStore.fetchSupervisors(),
    recentFailuresStore.fetchRecentFailures(),
    telegramStore.fetchTelegramGroups(),
  ])
})

function openNotifyModal(row) {
  failureToNotify.value = row
  isNotifyModalOpen.value = true
}

// --- Layout Resizing ---
const split = ref(50)
const dragging = ref(false)
const splitWrap = ref(null)

function onDragStart(e) {
  dragging.value = true
  window.addEventListener('mousemove', onDrag)
  window.addEventListener('mouseup', onDragEnd)
}
function onDrag(e) {
  if (!splitWrap.value) return
  const rect = splitWrap.value.getBoundingClientRect()
  let pct = ((e.clientX - rect.left) / rect.width) * 100
  pct = Math.max(25, Math.min(75, pct))
  split.value = Math.round(pct)
}
function onDragEnd() {
  dragging.value = false
  window.removeEventListener('mousemove', onDrag)
  window.removeEventListener('mouseup', onDragEnd)
}

// --- Dropdown Options (Smart Filtering) ---
// If a parent is selected, filter by it. Otherwise, show all to allow global search.
const depotOptions = computed(() => infrastructureStore.depots.map(d => ({ label: d.name, value: d.id })))
const circuitOptions = computed(() => infrastructureStore.circuits.map(c => ({ label: c.circuit_id, value: c.id })))

const stationOptions = computed(() => {
  let stations = infrastructureStore.stations;
  if (form.depot) {
    stations = stations.filter(s => s.depot === form.depot);
  }
  return stations.map(s => ({ label: s.code, value: s.id }));
})

const sectionOptions = computed(() => {
  let sections = infrastructureStore.sections;
  if (form.depot) {
    sections = sections.filter(s => s.depot === form.depot);
  }
  return sections.map(s => ({ label: s.name, value: s.id }));
})

const subSectionOptions = computed(() => {
  let sub = infrastructureStore.subSections;
  // Filter by Section if selected
  if (form.section) {
    sub = sub.filter(s => s.section === form.section);
  }
  // If no Section but Depot is selected, filter by Depot via Section
  else if (form.depot) {
     // We need to find sections belonging to this depot first
     const depotSectionIds = infrastructureStore.sections
        .filter(sec => sec.depot === form.depot)
        .map(sec => sec.id);
     sub = sub.filter(s => depotSectionIds.includes(s.section));
  }
  return sub.map(s => ({ label: s.name, value: s.id }));
})

const supervisorOptions = computed(() => 
  infrastructureStore.supervisors
    .filter(s => s.user) 
    .map(s => ({ label: s.name, value: s.user }))
)

const selectedCircuitSeverity = computed(() => {
  if (!form.circuit) return ''
  const circuit = infrastructureStore.circuits.find(c => c.id === form.circuit)
  return circuit ? circuit.severity : ''
})

const statusOptions = [
  { label: 'Draft', value: 'Draft' },
  { label: 'Active', value: 'Active' },
  { label: 'In Progress', value: 'In Progress' },
  { label: 'Resolved', value: 'Resolved' },
  { label: 'On Hold', value: 'On Hold' },
]

function getLocalNowString() {
  const now = new Date();
  const offsetMs = now.getTimezoneOffset() * 60000;
  return new Date(now.getTime() - offsetMs).toISOString().slice(0, 16);
}

const initialFormState = {
  fail_id: '',
  depot: null,
  circuit: null,
  entry_type: 'item',
  station: null,
  section: null,
  sub_section: null,
  reported_at: getLocalNowString(),
  assigned_to: null,
  current_status: 'Active',
  remark_fail: '',
  resolved_at: '',
  duration_minutes: '',
  remark_right: '',
}

const form = reactive({ ...initialFormState })
const errors = reactive({})
const userTags = ref([])

// --- Auto Tags ---
const autoTags = computed(() => {
  const t = []
  if (form.depot) { const d = infrastructureStore.depots.find(i => i.id === form.depot); if (d) t.push(`#${d.name}`) }
  if (form.circuit) { const c = infrastructureStore.circuits.find(i => i.id === form.circuit); if (c) t.push(`#${c.circuit_id}`) }
  if (form.station) { const s = infrastructureStore.stations.find(i => i.id === form.station); if (s) t.push(`#${s.code}`) }
  if (form.section) { const s = infrastructureStore.sections.find(i => i.id === form.section); if (s) t.push(`#${s.name}`) }
  return t
})

// --- Validation ---
function validate() {
  errors.circuit = form.circuit ? '' : 'Required'
  return Object.values(errors).every(v => !v)
}

// --- Smart Watchers (Dependency Logic) ---

// 1. If Depot changes, only clear children if they don't match the new depot
watch(() => form.depot, (newDepot) => {
  if (!newDepot) return; // Don't auto-clear if user just cleared depot, let them search
  
  if (form.station) {
    const s = infrastructureStore.stations.find(x => x.id === form.station);
    if (s && s.depot !== newDepot) form.station = null;
  }
  if (form.section) {
    const s = infrastructureStore.sections.find(x => x.id === form.section);
    if (s && s.depot !== newDepot) {
        form.section = null;
        form.sub_section = null;
    }
  }
});

// 2. If Station selected -> Auto-select Depot
watch(() => form.station, (newStationId) => {
  if (!newStationId) return;
  const station = infrastructureStore.stations.find(s => s.id === newStationId);
  if (station && station.depot) {
      // Only update if different to avoid loop
      if (form.depot !== station.depot) form.depot = station.depot;
  }
});

// 3. If Section selected -> Auto-select Depot
watch(() => form.section, (newSectionId) => {
  if (!newSectionId) {
      form.sub_section = null; // Clear child
      return;
  }
  const section = infrastructureStore.sections.find(s => s.id === newSectionId);
  if (section && section.depot) {
      if (form.depot !== section.depot) form.depot = section.depot;
  }
});

// 4. If Sub-Section selected -> Auto-select Section (which triggers Depot)
watch(() => form.sub_section, (newSubId) => {
  if (!newSubId) return;
  const sub = infrastructureStore.subSections.find(s => s.id === newSubId);
  if (sub && sub.section) {
      if (form.section !== sub.section) form.section = sub.section;
  }
});


watch(() => form.current_status, v => {
  if (v === 'Resolved' && !form.resolved_at) form.resolved_at = getLocalNowString()
})
watch(() => [form.reported_at, form.resolved_at], ([rep, res]) => {
  if (!rep || !res) { form.duration_minutes = ''; return }
  const ms = new Date(res) - new Date(rep)
  form.duration_minutes = (isNaN(ms) || ms < 0) ? '' : Math.round(ms / 60000)
})

// --- Submit ---
async function submit() {
  if (!validate()) {
    ui.pushToast({ type: 'error', title: 'Missing fields', message: 'Circuit is required.' })
    return
  }
  const payload = {
    entry_type: form.entry_type,
    current_status: form.current_status,
    circuit_id: form.circuit,
    station_id: form.station,
    section_id: form.section,
    sub_section_id: form.sub_section,
    assigned_to_id: form.assigned_to,
    reported_at: form.reported_at,
    resolved_at: form.resolved_at || null,
    remark_fail: form.remark_fail,
    remark_right: form.remark_right,
  }

  let savedFailure
  if (editingFailureId.value) {
    savedFailure = await failureStore.updateFailure(editingFailureId.value, payload)
    if (savedFailure) {
      ui.pushToast({ type: 'success', title: 'Success', message: 'Logbook entry updated.' })
      recentFailuresStore.fetchRecentFailures()
      if (savedFailure.current_status !== 'Information') {
           await failureStore.sendFailureNotification(savedFailure.id, ['alerts'])
           ui.pushToast({ type: 'info', title: 'Notified', message: 'Alert notification sent.' })
      }
      resetForm()
    }
  } else {
    savedFailure = await failureStore.addFailure(payload)
    if (savedFailure) {
      ui.pushToast({ type: 'success', title: 'Success', message: 'Entry saved.' })
      recentFailuresStore.fetchRecentFailures()
      resetForm()
      if (savedFailure.current_status !== 'Information') {
           await failureStore.sendFailureNotification(savedFailure.id, ['alerts'])
           ui.pushToast({ type: 'info', title: 'Notified', message: 'Alert notification sent.' })
      }
    }
  }
}

function resetForm() {
  Object.assign(form, initialFormState)
  form.reported_at = getLocalNowString()
  userTags.value = []
  editingFailureId.value = null
}

function saveAsDraft() {
  form.current_status = 'Draft'
  submit()
}

function handleEditRequest(id) {
  editingFailureId.value = id
  failureStore.fetchFailure(id)
}

// Populate form when editing
watch(() => failureStore.currentFailure, (failure) => {
  if (failure) {
    form.fail_id = failure.fail_id
    form.depot = failure.depot?.id || failure.station?.depot || failure.section?.depot
    form.circuit = failure.circuit?.id
    form.entry_type = failure.entry_type
    form.station = failure.station?.id
    form.section = failure.section?.id
    form.sub_section = failure.sub_section?.id
    form.reported_at = failure.reported_at ? new Date(failure.reported_at).toISOString().slice(0, 16) : ''
    form.assigned_to = failure.assigned_to?.id
    form.current_status = failure.current_status
    form.remark_fail = failure.remark_fail
    form.resolved_at = failure.resolved_at ? new Date(failure.resolved_at).toISOString().slice(0, 16) : ''
    form.duration_minutes = failure.duration_minutes
    form.remark_right = failure.remark_right
  }
})

// --- Archive ---
function openArchiveModal(failure) {
  failureToArchive.value = failure
  isArchiveModalOpen.value = true
  archiveReason.value = ''
}
async function confirmArchive() {
  if (failureToArchive.value) {
    await failureStore.archiveFailure(failureToArchive.value.id, archiveReason.value)
    failureToArchive.value = null
    isArchiveModalOpen.value = false
  }
}

const recentFailures = computed(() => recentFailuresStore.items)
</script>

<template>
  <div class="flex-1 flex flex-col gap-4 p-4 overflow-y-auto">
    
    <div ref="splitWrap" class="flex-1 flex gap-4" :class="dragging ? 'cursor-col-resize select-none' : ''">
      <div class="flex flex-col" :style="{ width: split + '%' }">
        <div class="rounded-2xl border-app bg-card text-app p-4">
          <div class="pb-3 mb-3 border-b border-app">
             <h2 class="text-xl font-semibold leading-tight">
               {{ editingFailureId ? `Editing Entry #${form.fail_id}` : 'New Logbook Entry' }}
             </h2>
          </div>

          <div class="grid gap-4 sm:grid-cols-2">
            <div class="sm:col-span-2 grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
              <div>
                <span class="text-sm text-app">Entry Type</span>
                <div class="flex items-center gap-4 pt-2">
                  <label class="flex items-center gap-2">
                    <input type="radio" v-model="form.entry_type" value="item" class="radio" />
                    <span>Failure</span>
                  </label>
                  <label class="flex items-center gap-2">
                    <input type="radio" v-model="form.entry_type" value="message" class="radio" />
                    <span>General Message</span>
                  </label>
                </div>
              </div>
              <div>
                <label class="block space-y-1">
                  <span class="text-sm text-app">Circuit</span>
                  <SearchSelect v-model="form.circuit" :options="circuitOptions" placeholder="Select circuit..." />
                  <p v-if="errors.circuit" class="text-xs text-red-600">{{ errors.circuit }}</p>
                </label>
              </div>
              <div>
                <label class="block space-y-1">
                  <span class="text-sm text-app">Circuit Severity</span>
                  <input readonly :value="selectedCircuitSeverity" class="field bg-app-hover" />
                </label>
              </div>
            </div>

            <div class="sm:col-span-2">
              <label class="block space-y-1">
                <span class="text-sm text-app">Circuit Tags</span>
                <TagsInput v-model="userTags" :preset="autoTags" placeholder="Add tag and press Enter" />
                <p class="text-xs text-muted">Auto from selections; you can add/remove your own.</p>
              </label>
            </div>

            <div class="sm:col-span-2 grid gap-4 sm:grid-cols-2 md:grid-cols-4">
              <div>
                <label class="block space-y-1">
                  <span class="text-sm text-app">Depot</span>
                  <SearchSelect v-model="form.depot" :options="depotOptions" placeholder="Select depot..." />
                </label>
              </div>
              <div>
                <label class="block space-y-1">
                  <span class="text-sm text-app">Station</span>
                  <SearchSelect v-model="form.station" :options="stationOptions" placeholder="Select station..." />
                </label>
              </div>
              <div>
                <label class="block space-y-1">
                  <span class="text-sm text-app">Section</span>
                  <SearchSelect v-model="form.section" :options="sectionOptions" placeholder="Select section..." />
                </label>
              </div>
              <div>
                <label class="block space-y-1">
                  <span class="text-sm text-app">Sub Section</span>
                  <SearchSelect v-model="form.sub_section" :options="subSectionOptions" placeholder="Select sub section..." />
                </label>
              </div>
            </div>

            <div class="sm:col-span-2 grid gap-4 grid-cols-1 md:grid-cols-3">
              <DateTime label="Reported At" v-model="form.reported_at" />
              <div>
                <label class="block space-y-1">
                  <span class="text-sm text-app">Assigned To</span>
                  <SearchSelect v-model="form.assigned_to" :options="supervisorOptions" placeholder="Select assignee..." />
                </label>
              </div>
              <div>
                <label class="block space-y-1">
                  <span class="text-sm text-app">Current Status</span>
                  <SearchSelect v-model="form.current_status" :options="statusOptions" placeholder="Select status..." :disabled="form.entry_type === 'message'" />
                </label>
              </div>
            </div>

            <div class="sm:col-span-2">
              <textarea v-model="form.remark_fail" rows="2" class="field-textarea" placeholder="Notes..."></textarea>
            </div>

            <template v-if="form.current_status === 'Resolved'">
              <DateTime label="Resolve At" v-model="form.resolved_at" />
              <InputText label="Duration (minutes)" v-model="form.duration_minutes" />
              <textarea v-model="form.remark_right" rows="2" class="sm:col-span-2 field-textarea" placeholder="Notes on resolution..."></textarea>
            </template>

            <FailureAttachment v-if="editingFailureId" :failure-id="editingFailureId" />

            <div class="sm:col-span-2 flex items-center justify-between pt-4 mt-4 border-t border-app">
              <button type="button" class="btn btn-solid" @click="saveAsDraft">Save as Draft</button>
              <div class="flex gap-3">
                <button type="button" class="btn btn-outline" @click="resetForm">{{ editingFailureId ? 'Cancel Edit' : 'Reset' }}</button>
                <button type="button" class="btn btn-primary" @click="submit">{{ editingFailureId ? 'Save Changes' : 'Submit' }}</button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="w-1 self-stretch bg-[var(--border)] hover:bg-[var(--text)]/30 cursor-col-resize rounded" :class="dragging ? 'bg-[var(--text)]/40' : ''" @mousedown="onDragStart" />

      <div class="flex flex-col" :style="{ width: 100 - split + '%' }">
        <RecentFailures
          :items="recentFailures"
          storage-key="rf-newfailure"
          :editing-id="editingFailureId"
          @view="row => console.log('open details', row)"
          @notify="openNotifyModal"
          @edit="handleEditRequest"
          @delete="openArchiveModal"
        />
      </div>
    </div>

    <NotificationModal v-model="isNotifyModalOpen" :failure="failureToNotify" />

    <div v-if="isArchiveModalOpen" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div class="bg-card rounded-lg p-6 shadow-xl w-full max-w-md">
        <h3 class="text-lg font-bold">Confirm Archival</h3>
        <p class="mt-2">Are you sure you want to archive failure log <span class="font-semibold">{{ failureToArchive?.fail_id }}</span>?</p>
        <div class="mt-4">
          <label for="archiveReason" class="block text-sm font-medium text-app">Reason for archiving</label>
          <textarea v-model="archiveReason" id="archiveReason" rows="3" class="field-textarea mt-1"></textarea>
        </div>
        <div class="mt-6 flex justify-end gap-3">
          <button @click="isArchiveModalOpen = false" class="btn btn-outline">Cancel</button>
          <button @click="confirmArchive" class="btn btn-danger">Archive</button>
        </div>
      </div>
    </div>
  </div>
</template>