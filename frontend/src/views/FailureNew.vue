<script setup>
import { reactive, ref, computed, onMounted } from 'vue'
import InputText from '@/components/form/InputText.vue'
import DateTime from '@/components/form/DateTime.vue'
import SearchSelect from '@/components/form/SearchSelect.vue'
import TagsInput from '@/components/form/TagsInput.vue'
import RecentFailures from '@/components/RecentFailures.vue'
import { useUIStore } from '@/stores/ui'
import { useInfrastructureStore } from '@/stores/infrastructure'
import { useFailureStore } from '@/stores/failures'

const ui = useUIStore()
const infrastructureStore = useInfrastructureStore()
const failureStore = useFailureStore()

onMounted(() => {
  Promise.all([
    infrastructureStore.fetchCircuits(),
    infrastructureStore.fetchStations(),
    infrastructureStore.fetchSections(),
    infrastructureStore.fetchSubSections(),
    infrastructureStore.fetchSupervisors(),
  ]);
});

const circuitOptions = computed(() => infrastructureStore.circuits.map(c => ({ label: `${c.circuit_id} (${c.name})`, value: c.id })))
const stationOptions = computed(() => infrastructureStore.stations.map(s => ({ label: s.name, value: s.id })))
const sectionOptions = computed(() => infrastructureStore.sections.map(s => ({ label: s.name, value: s.id })))
const subSectionOptions = computed(() => infrastructureStore.subSections.map(ss => ({ label: `${ss.name} (${ss.section_name})`, value: ss.id })))
const supervisorOptions = computed(() => infrastructureStore.supervisors.map(s => ({ label: s.name, value: s.id })))
const statusOptions = [ { label: 'Active', value: 'Active' }, { label: 'In Progress', value: 'In Progress' }, { label: 'Resolved', value: 'Resolved' }, { label: 'On Hold', value: 'On Hold' } ]
const entryTypeOptions = [ { value: 'item', label: 'Item' }, { value: 'message', label: 'Message' }, { value: 'warning', label: 'Warning' }, { value: 'major', label: 'Major' }, { value: 'critical', label: 'Critical' } ]

const initialFormState = {
  circuit: null, entryType: 'item', station: null, section: null, sub_section: null,
  reported_at: new Date(new Date().getTime() - new Date().getTimezoneOffset() * 60000).toISOString().slice(0, 16),
  assigned_to: null, current_status: 'Active', remark_fail: '', resolved_at: null, remark_right: '', severity: 'Minor',
}
const form = reactive({ ...initialFormState })
const errors = reactive({})

const userTags = ref([])
const autoTags = computed(() => {
  const tags = [];
  if (form.circuit) {
    const circuitObj = infrastructureStore.circuits.find(c => c.id === form.circuit);
    if (circuitObj) tags.push(`#${circuitObj.circuit_id}`);
  }
  if (form.station) {
    const stationObj = infrastructureStore.stations.find(s => s.id === form.station);
    if (stationObj) tags.push(`#${stationObj.name.replace(/\s+/g, '-')}`);
  }
  if (form.section) {
    const sectionObj = infrastructureStore.sections.find(s => s.id === form.section);
    if (sectionObj) tags.push(`#${sectionObj.name.replace(/\s+/g, '-')}`);
  }
  return tags;
});

async function submit() {
  errors.circuit = form.circuit ? '' : 'Circuit is required.'
  if (errors.circuit) {
    ui.pushToast({ type: 'error', title: 'Missing fields', message: errors.circuit })
    return
  }
  const payload = { ...form }
  if (!payload.resolved_at) payload.resolved_at = null
  const success = await failureStore.addFailure(payload)
  if (success) {
    resetForm()
  }
}

function resetForm() {
  Object.assign(form, initialFormState)
  form.reported_at = new Date(new Date().getTime() - new Date().getTimezoneOffset() * 60000).toISOString().slice(0, 16)
  userTags.value = []
}

const split = ref(50)
</script>

<template>
  <div class="flex items-start gap-4">
    <div class="space-y-4" :style="{ width: split + '%' }">
      <div class="text-center">
        <h2 class="text-2xl font-semibold leading-tight">Logbook Entry</h2>
      </div>
      <div class="card">
        <div class="grid gap-4 sm:grid-cols-2">
          <div class="sm:col-span-2 grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
            <div><label class="block space-y-1"><span class="text-sm text-app">Event ID (auto)</span><input class="field" placeholder="Generated on save" readonly /></label></div>
            <div><label class="block space-y-1"><span class="text-sm text-app">Entry Type</span><SearchSelect v-model="form.entryType" :options="entryTypeOptions" /></label></div>
            <div><label class="block space-y-1"><span class="text-sm text-app">Circuit</span><SearchSelect v-model="form.circuit" :options="circuitOptions" placeholder="Select circuit..." /><p v-if="errors.circuit" class="text-xs text-red-600">{{ errors.circuit }}</p></label></div>
          </div>
          <div class="sm:col-span-2"><label class="block space-y-1"><span class="text-sm text-app">Circuit Tags</span><TagsInput v-model="userTags" :preset="autoTags" placeholder="Add custom tags..." /><p class="text-xs text-muted">Auto-tags are generated from selections.</p></label></div>
          <div class="sm:col-span-2 grid gap-4 sm:grid-cols-3">
            <div><label class="block space-y-1"><span class="text-sm text-app">Station</span><SearchSelect v-model="form.station" :options="stationOptions" placeholder="Select station..." /></label></div>
            <div><label class="block space-y-1"><span class="text-sm text-app">Section</span><SearchSelect v-model="form.section" :options="sectionOptions" placeholder="Select section..." /></label></div>
            <div><label class="block space-y-1"><span class="text-sm text-app">Sub Section</span><SearchSelect v-model="form.sub_section" :options="subSectionOptions" placeholder="Select sub section..." /></label></div>
          </div>
          <div class="sm:col-span-2 grid gap-4 grid-cols-1 md:grid-cols-3">
            <DateTime label="Reported At" v-model="form.reported_at" />
            <div><label class="block space-y-1"><span class="text-sm text-app">Assigned To</span><SearchSelect v-model="form.assigned_to" :options="supervisorOptions" placeholder="Select assignee..." /></label></div>
            <div><label class="block space-y-1"><span class="text-sm text-app">Current Status</span><SearchSelect v-model="form.current_status" :options="statusOptions" /></label></div>
          </div>
          <div class="sm:col-span-2"><textarea v-model="form.remark_fail" rows="2" class="field-textarea" placeholder="Notes..."></textarea></div>
          <template v-if="form.current_status === 'Resolved'">
            <DateTime label="Resolved At" v-model="form.resolved_at" />
            <InputText label="Duration (minutes)" :model-value="form.duration_minutes" readonly />
            <textarea v-model="form.remark_right" rows="2" class="sm:col-span-2 field-textarea" placeholder="Notes on resolution..."></textarea>
          </template>
          <div class="sm:col-span-2 flex items-center justify-between pt-2">
            <div class="flex gap-3">
              <button type="button" class="btn btn-outline" @click="resetForm">Reset</button>
              <button type="button" class="btn btn-primary" @click="submit">Submit</button>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div class="w-1 self-stretch bg-[var(--border)]"></div>
    <div class="space-y-4" :style="{ width: 100 - split + '%' }">
      <RecentFailures storage-key="rf-newfailure" />
    </div>
  </div>
</template>