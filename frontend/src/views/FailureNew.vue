<script setup>
import { reactive, ref, computed, watch, onMounted } from 'vue'
import InputText from '@/components/form/InputText.vue'
import SelectBox from '@/components/form/SelectBox.vue'
import DateTime from '@/components/form/DateTime.vue'
import SearchSelect from '@/components/form/SearchSelect.vue'
import TagsInput from '@/components/form/TagsInput.vue'
import { useUIStore } from '@/stores/ui'
import RecentFailures from '@/components/RecentFailures.vue'
import { useInfrastructureStore } from '@/stores/infrastructure'
import { useFailureStore } from '@/stores/failures'
import FailureAttachment from '@/components/FailureAttachment.vue'

const ui = useUIStore()
const infrastructureStore = useInfrastructureStore()
const failureStore = useFailureStore()

const editingFailureId = ref(null)
const isArchiveModalOpen = ref(false)
const failureToArchive = ref(null)
const archiveReason = ref('')

onMounted(() => {
  Promise.all([
    infrastructureStore.fetchDepots(),
    infrastructureStore.fetchCircuits(),
    infrastructureStore.fetchStations(),
    infrastructureStore.fetchSections(),
    infrastructureStore.fetchSubSections(),
    infrastructureStore.fetchSupervisors(),
    failureStore.fetchFailures(),
  ])
})

// ... (keep the existing computed properties like depotOptions, circuitOptions, etc.)
const depotOptions = computed(() => infrastructureStore.depots.map(d => ({ label: d.name, value: d.id })));
const circuitOptions = computed(() => infrastructureStore.circuits.map(c => ({ label: c.name, value: c.id })));
const stationOptions = computed(() => form.depot ? infrastructureStore.stations.filter(s => s.depot === form.depot).map(s => ({ label: s.name, value: s.id })) : []);
const sectionOptions = computed(() => form.depot ? infrastructureStore.sections.filter(s => s.depot === form.depot).map(s => ({ label: s.name, value: s.id })) : []);
const subSectionOptions = computed(() => form.section ? infrastructureStore.subSections.filter(s => s.section === form.section).map(s => ({ label: s.name, value: s.id })) : []);
const supervisorOptions = computed(() => infrastructureStore.supervisors.map(s => ({ label: s.name, value: s.id })));
const selectedCircuitSeverity = computed(() => { if (!form.circuit) return ''; const circuit = infrastructureStore.circuits.find(c => c.id === form.circuit); return circuit ? circuit.severity : ''; });
const statusOptions = [ { label: 'Draft', value: 'Draft' }, { label: 'Active', value: 'Active' }, { label: 'In Progress', value: 'In Progress' }, { label: 'Resolved', value: 'Resolved' }, { label: 'On Hold', value: 'On Hold' }, ];
const initialFormState = { fail_id: '', depot: null, circuit: null, entry_type: 'item', station: null, section: null, sub_section: null, reported_at: new Date().toISOString().slice(0, 16), assigned_to: null, current_status: 'Active', remark_fail: '', resolved_at: '', duration_minutes: '', remark_right: '', };
const form = reactive({ ...initialFormState });
const errors = reactive({});
const autoTags = computed(() => { const t = []; if (form.depot) { const depot = infrastructureStore.depots.find(d => d.id === form.depot); if (depot) t.push(`#${depot.name}`) } if (form.circuit) { const circuit = infrastructureStore.circuits.find(c => c.id === form.circuit); if (circuit) t.push(`#${circuit.name}`) } if (form.station) { const station = infrastructureStore.stations.find(s => s.id === form.station); if (station) t.push(`#${station.name}`) } if (form.section) { const section = infrastructureStore.sections.find(s => s.id === form.section); if (section) t.push(`#${section.name}`) } if (form.sub_section) { const subSection = infrastructureStore.subSections.find(s => s.id === form.sub_section); if (subSection) t.push(`#${subSection.name}`) } return t });
const userTags = ref([]);
const allTags = computed(() => [...autoTags.value, ...userTags.value]);
function validate() { errors.circuit = form.circuit ? '' : 'Required'; return Object.values(errors).every(v => !v) }
function nowLocalISO() { return new Date(Date.now() - new Date().getSeconds() * 1000 - new Date().getMilliseconds()).toISOString().slice(0, 16) }
function calcDurationMinutes(startISO, endISO) { if (!startISO || !endISO) return ''; const ms = new Date(endISO) - new Date(startISO); if (isNaN(ms) || ms < 0) return ''; return Math.round(ms / 60000) }
watch(() => form.current_status, v => { if (v === 'Resolved' && !form.resolved_at) form.resolved_at = nowLocalISO() });
watch(() => [form.reported_at, form.resolved_at], ([rep, res]) => { form.duration_minutes = calcDurationMinutes(rep, res) });
watch(() => form.depot, () => { form.section = null; form.station = null; form.sub_section = null });
watch(() => form.section, () => { form.sub_section = null });
watch(() => failureStore.currentFailure, (failure) => { if (failure) { Object.assign(form, { ...failure, depot: failure.depot?.id, circuit: failure.circuit?.id, station: failure.station?.id, section: failure.section?.id, sub_section: failure.sub_section?.id, assigned_to: failure.assigned_to?.id, reported_at: failure.reported_at ? new Date(failure.reported_at).toISOString().slice(0, 16) : '', resolved_at: failure.resolved_at ? new Date(failure.resolved_at).toISOString().slice(0, 16) : '' }); } });
const split = ref(50);
const dragging = ref(false);
const splitWrap = ref(null);
function onDragStart(e) { dragging.value = true; window.addEventListener('mousemove', onDrag); window.addEventListener('mouseup', onDragEnd); }
function onDrag(e) { if (!splitWrap.value) return; const rect = splitWrap.value.getBoundingClientRect(); let pct = ((e.clientX - rect.left) / rect.width) * 100; pct = Math.max(25, Math.min(75, pct)); split.value = Math.round(pct); }
function onDragEnd() { dragging.value = false; window.removeEventListener('mousemove', onDrag); window.removeEventListener('mouseup', onDragEnd); }

// --- Updated Logic ---
async function saveAsDraft() {
  form.current_status = 'Draft'
  await submit(false); // Submit without notification
}

async function submit(notify = true) {
  if (!validate()) {
    ui.pushToast({ type: 'error', title: 'Missing fields', message: 'Circuit is required.' })
    return
  }
  const payload = {
    entry_type: form.entry_type,
    current_status: form.current_status,
    circuit: form.circuit,
    station: form.station,
    section: form.section,
    sub_section: form.sub_section,
    assigned_to: form.assigned_to,
    reported_at: form.reported_at,
    resolved_at: form.resolved_at || null,
    remark_fail: form.remark_fail,
    remark_right: form.remark_right,
  }

  let savedFailure;
  if (editingFailureId.value) {
    savedFailure = await failureStore.updateFailure(editingFailureId.value, payload);
  } else {
    savedFailure = await failureStore.addFailure(payload);
  }

  if (savedFailure) {
    let toastMessage = 'Logbook entry saved.';
    if (notify && savedFailure.current_status !== 'Draft') {
      await failureStore.sendFailureNotification(savedFailure.id, ['alert']);
      toastMessage = 'Entry saved and notification sent.';
    }
    ui.pushToast({ type: 'success', title: 'Success', message: toastMessage });
    resetForm();
  }
}

function resetForm() {
  Object.assign(form, initialFormState);
  form.reported_at = new Date().toISOString().slice(0, 16);
  userTags.value = [];
  editingFailureId.value = null;
}

function handleEditRequest(id) {
  editingFailureId.value = id;
  failureStore.fetchFailure(id);
}

function openArchiveModal(failure) {
  failureToArchive.value = failure;
  isArchiveModalOpen.value = true;
  archiveReason.value = '';
}

async function confirmArchive() {
  if (failureToArchive.value) {
    await failureStore.archiveFailure(failureToArchive.value.id, archiveReason.value);
    failureToArchive.value = null;
    isArchiveModalOpen.value = false;
  }
}

function handleArchiveRequest(failure) {
  openArchiveModal(failure);
}

const recentFailures = computed(() => failureStore.failures);
</script>
<template>
  <div class="flex-1 flex flex-col gap-4 p-4 overflow-y-auto">
    <div class="flex items-center justify-between">
      <h1 class="text-2xl font-bold">New Logbook Entry</h1>
    </div>

    <div ref="splitWrap" class="flex-1 flex gap-2" :class="dragging ? 'cursor-col-resize select-none' : ''">
      <div class="space-y-4" :style="{ width: split + '%' }">
        <div class="card">
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
                  <SearchSelect v-model="form.current_status" :options="statusOptions" placeholder="Select status..." />
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
            <div class="sm:col-span-2 flex items-center justify-between pt-2">
              <button type="button" class="btn btn-solid" @click="saveAsDraft">
                Save as Draft
              </button>
              <div class="flex gap-3">
                <button type="button" class="btn btn-outline" @click="resetForm">{{ editingFailureId ? 'Cancel Edit' : 'Reset' }}</button>
                <button type="button" class="btn btn-primary" @click="submit()">{{ editingFailureId ? 'Save Changes & Notify' : 'Submit & Notify' }}</button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div
        class="w-1 self-stretch bg-[var(--border)] hover:bg-[var(--text)]/30 cursor-col-resize rounded"
        :class="dragging ? 'bg-[var(--text)]/40' : ''"
        @mousedown="onDragStart"
      />

      <div class="space-y-4" :style="{ width: 100 - split + '%' }">
        <RecentFailures
          :items="recentFailures"
          storage-key="rf-newfailure"
          :editing-id="editingFailureId"
          @view="row => console.log('open details', row)"
          @edit="handleEditRequest"
          @delete="handleArchiveRequest"
        />
      </div>
    </div>

    <!-- Archive Confirmation Modal -->
    <div v-if="isArchiveModalOpen" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div class="bg-card rounded-lg p-6 shadow-xl w-full max-w-md">
        <h3 class="text-lg font-bold">Confirm Archival</h3>
        <p class="mt-2">
          Are you sure you want to archive failure log
          <span class="font-semibold">{{ failureToArchive?.fail_id }}</span>?
        </p>
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