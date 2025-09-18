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
    failureStore.fetchFailures(),
  ])
})

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

const circuitOptions = computed(() =>
  infrastructureStore.circuits.map(c => ({ label: c.name, value: c.id }))
)
const stationOptions = computed(() =>
  infrastructureStore.stations.map(s => ({ label: s.name, value: s.id }))
)
const sectionOptions = computed(() =>
  infrastructureStore.sections.map(s => ({ label: s.name, value: s.id }))
)
const subSectionOptions = computed(() =>
  infrastructureStore.subSections.map(s => ({ label: s.name, value: s.id }))
)
const supervisorOptions = computed(() =>
  infrastructureStore.supervisors.map(s => ({ label: `${s.first_name} ${s.last_name} (${s.username})`, value: s.id }))
)

const statusOptions = [
  { label: 'Active', value: 'Active' },
  { label: 'In Progress', value: 'In Progress' },
  { label: 'Resolved', value: 'Resolved' },
  { label: 'On Hold', value: 'On Hold' },
]

const form = reactive({
  fail_id: '',
  circuit: null,
  entryType: 'item',
  station: null,
  section: null,
  sub_section: null,
  reported_at: new Date().toISOString().slice(0, 16),
  assigned_to: null,
  current_status: 'Active',
  remark_fail: '',
  resolved_at: '',
  duration_minutes: '',
  remark_right: '',
})

const entryTypeOptions = [
  { value: 'item', label: 'Item' },
  { value: 'message', label: 'Message' },
  { value: 'warning', label: 'Warning' },
  { value: 'major', label: 'Major' },
  { value: 'critical', label: 'Critical' },
]

const errors = reactive({})

const autoTags = computed(() => {
  const t = []
  if (form.circuit) {
    const circuit = infrastructureStore.circuits.find(c => c.id === form.circuit)
    if (circuit) t.push(`#${circuit.name}`)
  }
  if (form.station) {
    const station = infrastructureStore.stations.find(s => s.id === form.station)
    if (station) t.push(`#${station.name}`)
  }
  if (form.section) {
    const section = infrastructureStore.sections.find(s => s.id === form.section)
    if (section) t.push(`#${section.name}`)
  }
  if (form.sub_section) {
    const subSection = infrastructureStore.subSections.find(s => s.id === form.sub_section)
    if (subSection) t.push(`#${subSection.name}`)
  }
  return t
})

const userTags = ref([])
const allTags = computed(() => [...autoTags.value, ...userTags.value])

function validate() {
  errors.circuit = form.circuit ? '' : 'Required'
  return Object.values(errors).every(v => !v)
}

function nowLocalISO() {
  return new Date(Date.now() - new Date().getSeconds() * 1000 - new Date().getMilliseconds())
    .toISOString()
    .slice(0, 16)
}
function calcDurationMinutes(startISO, endISO) {
  if (!startISO || !endISO) return ''
  const ms = new Date(endISO) - new Date(startISO)
  if (isNaN(ms) || ms < 0) return ''
  return Math.round(ms / 60000)
}

watch(() => form.current_status, v => {
  if (v === 'Resolved' && !form.resolved_at) form.resolved_at = nowLocalISO()
})
watch(() => [form.reported_at, form.resolved_at], ([rep, res]) => {
  form.duration_minutes = calcDurationMinutes(rep, res)
})

const payload = computed(() => ({
  ...form,
  circuit_tags: allTags.value,
}))

async function submit() {
  if (!validate()) {
    ui.pushToast({ type: 'error', title: 'Missing fields', message: 'Circuit is required.' })
    return
  }
  await failureStore.addFailure(payload.value)
  if (!failureStore.error) {
    resetForm()
  }
}

function resetForm() {
  Object.assign(form, {
    fail_id: '',
    circuit: null,
    station: null,
    section: null,
    sub_section: null,
    reported_at: new Date().toISOString().slice(0, 16),
    assigned_to: null,
    current_status: 'Active',
    remark_fail: '',
    resolved_at: '',
    duration_minutes: '',
    remark_right: '',
    entryType: 'item',
  })
  userTags.value = []
}

const recentFailures = computed(() => failureStore.failures)
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
                <label class="block space-y-1">
                  <span class="text-sm text-app">Event ID (server will assign)</span>
                  <input v-model="form.fail_id" class="field" placeholder="Leave empty" />
                </label>
              </div>
              <div>
                <label class="block space-y-1">
                  <span class="text-sm text-app">Entry Type</span>
                  <SearchSelect v-model="form.entryType" :options="entryTypeOptions" placeholder="Select type..." />
                </label>
              </div>
              <div>
                <label class="block space-y-1">
                  <span class="text-sm text-app">Circuit</span>
                  <SearchSelect v-model="form.circuit" :options="circuitOptions" placeholder="Select circuit..." />
                  <p v-if="errors.circuit" class="text-xs text-red-600">{{ errors.circuit }}</p>
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
            <div class="sm:col-span-2 grid gap-4 sm:grid-cols-3">
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
            <div class="sm:col-span-2 text-sm text-muted">Attachments: (uploader to be added)</div>
            <div class="sm:col-span-2 flex items-center justify-between pt-2">
              <button type="button" class="btn btn-solid" @click="ui.pushToast({ type: 'info', title: 'Draft', message: 'Saved as draft (demo).' })">
                Save as Draft
              </button>
              <div class="flex gap-3">
                <button type="button" class="btn btn-outline" @click="resetForm">Reset</button>
                <button type="button" class="btn btn-primary" @click="submit">Submit</button>
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
          @view="row => console.log('open details', row)"
          @notify="row => console.log('notify', row)"
          @edit="row => console.log('edit', row)"
          @delete="row => console.log('delete', row)"
        />
      </div>
    </div>
  </div>
</template>
