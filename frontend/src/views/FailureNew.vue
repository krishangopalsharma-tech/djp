<script setup>
import { reactive, ref, computed, watch, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useUIStore } from '@/stores/ui'
import { useSectionsStore } from '@/stores/sections';
import { useFailureStore } from '@/stores/failures'
import { useRecentFailuresStore } from '@/stores/recentFailures';
import { useTelegramStore } from '@/stores/telegram'
import { useAttachmentStore } from '@/stores/attachments'
import FailureForm from '@/components/FailureForm.vue'
import RecentFailures from '@/components/RecentFailures.vue'
import NotificationModal from '@/components/NotificationModal.vue'

// Helper to format dates
function toLocalISOString(date) {
  if (!date) return '';
  const d = new Date(date);
  if (isNaN(d.getTime())) return '';
  const offset = d.getTimezoneOffset();
  const localDate = new Date(d.getTime() - (offset * 60 * 1000));
  return localDate.toISOString().slice(0, 16);
}

// Initialize Stores
const ui = useUIStore();
const sectionsStore = useSectionsStore();
const failureStore = useFailureStore();
const recentFailuresStore = useRecentFailuresStore();
const telegramStore = useTelegramStore();
const attachmentStore = useAttachmentStore();
const router = useRouter();

// Component State
const editingFailureId = ref(null);
const isEditMode = computed(() => !!editingFailureId.value);
const isArchiveModalOpen = ref(false);
const failureToArchive = ref(null);
const archiveReason = ref('');
const isNotifyModalOpen = ref(false);
const failureToNotify = ref(null);

// Form State
const initialFormState = { id: null, fail_id: '', depot: null, circuit: null, entry_type: 'item', station: null, section: null, sub_section: null, reported_at: toLocalISOString(new Date()), assigned_to: null, current_status: 'Active', remark_fail: '', resolved_at: '', duration_minutes: '', remark_right: '', userTags: [] };
const form = reactive({ ...initialFormState });
const errors = reactive({});

// Data Loading
let initialDataLoadPromise = null;
onMounted(() => {
  initialDataLoadPromise = Promise.all([
    infrastructureStore.fetchDepots(),
    infrastructureStore.fetchCircuits(),
    infrastructureStore.fetchStations(),
    infrastructureStore.fetchSections(),
    infrastructureStore.fetchSubSections(),
    infrastructureStore.fetchSupervisors(),
    recentFailuresStore.fetchRecentFailures(),
    telegramStore.fetchTelegramGroups(),
  ]).catch(error => {
    console.error("Failed to load initial form data:", error);
    ui.pushToast({ type: 'error', title: 'Load Failed', message: 'Could not load necessary form data.' });
  });
});

// Computed properties for dropdowns
const options = computed(() => ({
  depots: infrastructureStore.depots.map(d => ({ label: d.code || d.name, value: d.id })),
  circuits: infrastructureStore.circuits,
  stations: infrastructureStore.stations,
  sections: infrastructureStore.sections,
  subSections: infrastructureStore.subSections,
  supervisors: infrastructureStore.supervisors.map(s => ({ label: s.name, value: s.id })),
  statuses: [ { label: 'Active', value: 'Active' }, { label: 'In Progress', value: 'In Progress' }, { label: 'Resolved', value: 'Resolved' }, { label: 'On Hold', value: 'On Hold' }, { label: 'Information', value: 'Information' }],
}));

const recentFailures = computed(() => recentFailuresStore.items)

async function handleEditRequest(id) {
  await initialDataLoadPromise;
  await failureStore.fetchFailure(id); // 1. Call the action to update the store
  const failureData = failureStore.currentFailure; // 2. Get the data from the store's state

  if (failureData) {
    resetForm();
    editingFailureId.value = id;
    Object.assign(form, {
      ...failureData,
      circuit: failureData.circuit?.id || null,
      assigned_to: failureData.assigned_to?.id || null,
      reported_at: toLocalISOString(failureData.reported_at),
      resolved_at: toLocalISOString(failureData.resolved_at),
      userTags: [],
    });
    form.depot = failureData.station?.depot || failureData.section?.depot || null;
    await nextTick();
    form.station = failureData.station?.id || null;
    form.section = failureData.section?.id || null;
    await nextTick();
    form.sub_section = failureData.sub_section?.id || null;
  }
}

// Other form logic
watch(() => form.entry_type, (newType, oldType) => {
  if (newType === 'message') {
    const infoCircuit = infrastructureStore.circuits.find(c => c.name === 'Info');
    const allDepot = infrastructureStore.depots.find(d => d.name === 'ALL');
    const allSupervisor = infrastructureStore.supervisors.find(s => s.name === 'ALL');
    form.circuit = infoCircuit?.id || null;
    form.current_status = 'Information';
    form.depot = allDepot?.id || null;
    form.assigned_to = allSupervisor?.id || null;
  } else if (oldType === 'message') {
    resetForm();
  }
});
watch(() => form.current_status, v => { if (v === 'Resolved' && !form.resolved_at) form.resolved_at = toLocalISOString(new Date()) });
watch(() => [form.reported_at, form.resolved_at], ([rep, res]) => { if (!rep || !res) { form.duration_minutes = '' } else { const ms = new Date(res) - new Date(rep); form.duration_minutes = isNaN(ms) || ms < 0 ? '' : Math.round(ms / 60000) } });
function validate() { errors.circuit = form.circuit ? '' : 'Required'; return !errors.circuit; }

function resetForm() {
  Object.assign(form, initialFormState);
  form.reported_at = toLocalISOString(new Date());
  editingFailureId.value = null;
  attachmentStore.attachments = [];
}

async function submit() {
  if (!validate()) {
    ui.pushToast({ type: 'error', title: 'Missing fields', message: 'Circuit is required.' });
    return;
  }
  const payload = { ...form };
  delete payload.userTags;
  payload.resolved_at = payload.resolved_at || null;

  let savedFailure;
  if (isEditMode.value) {
    savedFailure = await failureStore.updateFailure(editingFailureId.value, payload);
    if (savedFailure) {
        ui.pushToast({ type: 'success', title: 'Success', message: 'Logbook entry updated.' });
        // After updating, you might want to stay on the page or redirect
        // For now, we stay.
    }
  } else {
    // This is a new entry
    savedFailure = await failureStore.addFailure(payload);
     if (savedFailure) {
        ui.pushToast({ type: 'success', title: 'Success', message: 'Entry saved. You can now add attachments.' });
        // Reset the form for the next entry
        resetForm();

        if (savedFailure.current_status !== 'Information') {
             await failureStore.sendFailureNotification(savedFailure.id, ['alerts']);
             ui.pushToast({ type: 'info', title: 'Notified', message: 'Alert notification sent.' });
        }
    }
  }
}

function openNotifyModal(row) { failureToNotify.value = row; isNotifyModalOpen.value = true; }
function handleArchiveRequest(failure) { failureToArchive.value = failure; isArchiveModalOpen.value = true; archiveReason.value = ''; }
async function confirmArchive() { if (failureToArchive.value) { await failureStore.archiveFailure(failureToArchive.value.id, archiveReason.value); failureToArchive.value = null; isArchiveModalOpen.value = false; } }
const split = ref(50);
const dragging = ref(false);
const splitWrap = ref(null);
function onDragStart(e) { dragging.value = true; window.addEventListener('mousemove', onDrag); window.addEventListener('mouseup', onDragEnd); }
function onDrag(e) { if (!splitWrap.value) return; const rect = splitWrap.value.getBoundingClientRect(); let pct = ((e.clientX - rect.left) / rect.width) * 100; pct = Math.max(25, Math.min(75, pct)); split.value = Math.round(pct); }
function onDragEnd() { dragging.value = false; window.removeEventListener('mousemove', onDrag); window.removeEventListener('mouseup', onDragEnd); }
</script>

<template>
  <div class="flex-1 flex flex-col gap-4 p-4 overflow-y-auto">
    <div ref="splitWrap" class="flex-1 flex items-start gap-4" :class="dragging ? 'cursor-col-resize select-none' : ''">
      <div class="flex flex-col" :style="{ width: split + '%' }">
        <h2 class="text-xl font-semibold leading-tight mb-4">{{ isEditMode ? `Editing Entry #${form.fail_id}` : 'New Logbook Entry' }}</h2>
        <div class="card">
          <FailureForm v-model="form" :options="options" :errors="errors" :is-edit-mode="isEditMode" />
          <div class="sm:col-span-2 flex items-center justify-end pt-4 mt-4 border-t border-app">
            <div class="flex gap-3">
              <button type="button" class="btn btn-outline" @click="resetForm">{{ editingFailureId ? 'Cancel Edit' : 'Reset Form' }}</button>
              <button type="button" class="btn btn-primary" @click="submit">{{ editingFailureId ? 'Save Changes' : 'Submit' }}</button>
            </div>
          </div>
        </div>
      </div>

      <div class="w-1 self-stretch bg-[var(--border)] hover:bg-[var(--text)]/30 cursor-col-resize rounded" @mousedown="onDragStart" />

      <div class="flex flex-col" :style="{ width: 100 - split + '%' }">
        <h2 class="text-xl font-semibold leading-tight mb-4">Recent Failure Logs</h2>
        <RecentFailures
          :items="recentFailures"
          storage-key="rf-newfailure"
          :editing-id="editingFailureId"
          :show-header="false"
          @notify="openNotifyModal"
          @edit="handleEditRequest"
          @delete="handleArchiveRequest"
        />
      </div>
    </div>

    <NotificationModal v-model="isNotifyModalOpen" :failure="failureToNotify" />
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