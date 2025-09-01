<script setup>
import { reactive, ref, computed, watch } from 'vue'
import InputText from '@/components/form/InputText.vue'
import SelectBox from '@/components/form/SelectBox.vue'
import DateTime from '@/components/form/DateTime.vue'
import SearchSelect from '@/components/form/SearchSelect.vue'
import TagsInput from '@/components/form/TagsInput.vue'
import { useUIStore } from '@/stores/ui'
import RecentFailures from '@/components/RecentFailures.vue'

const ui = useUIStore()

const split = ref(50) // left pane width in %
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
  pct = Math.max(25, Math.min(75, pct)) // clamp 25%..75%
  split.value = Math.round(pct)
}
function onDragEnd() {
  dragging.value = false
  window.removeEventListener('mousemove', onDrag)
  window.removeEventListener('mouseup', onDragEnd)
}

// --- Mock options (we'll wire real data later) ---
const circuitOptions = [
  { label: 'CIR-01', value: 'CIR-01' },
  { label: 'CIR-05', value: 'CIR-05' },
  { label: 'CIR-12', value: 'CIR-12' },
  { label: 'CIR-77', value: 'CIR-77' },
]

// Current Status now includes "In Progress"
const statusOptions = [
  { label: 'Active', value: 'Active' },
  { label: 'In Progress', value: 'In Progress' },
  { label: 'Resolved', value: 'Resolved' },
  { label: 'On Hold', value: 'On Hold' },
]

// --- Form state ---
const form = reactive({
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
})

const errors = reactive({})

// Build auto tags from selected values
const autoTags = computed(() => {
  const t = []
  if (form.circuit) t.push(`#${form.circuit}`)
  if (form.station) t.push(`#${form.station}`)
  if (form.section) t.push(`#${form.section}`)
  if (form.sub_section) t.push(`#${form.sub_section}`)
  return t
})

const userTags = ref([])
const allTags = computed(() => [...autoTags.value, ...userTags.value])

function validate() {
  errors.circuit = form.circuit ? '' : 'Required'
  return Object.values(errors).every(v => !v)
}

// helpers for resolved fields
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

const payloadPreview = computed(() => ({
  ...form,
  fail_id: form.fail_id || '(server-generated later)',
  circuit_tags: allTags.value,
}))

async function submit() {
  if (!validate()) {
    ui.pushToast({ type: 'error', title: 'Missing fields', message: 'Circuit is required.' })
    return
  }
  ui.pushToast({ type: 'success', title: 'Submitted', message: 'Demo submit — backend later.' })
  console.log('SUBMIT PAYLOAD', payloadPreview.value)
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
  })
  userTags.value = []
}
</script>

<template>
  <div ref="splitWrap" class="flex items-start gap-4">
    <!-- LEFT: New Failure form -->
    <div class="space-y-4" :style="{ width: split + '%' }">
      <div class="text-center">
        <h2 class="text-2xl font-semibold leading-tight">New Failure</h2>
      </div>

      <div class="card">
        <div class="grid gap-4 sm:grid-cols-2">
          <!-- Fail ID / Circuit -->
          <div>
            <InputText label="Fail ID (server will assign)" v-model="form.fail_id" placeholder="Leave empty" />
          </div>
          <div>
            <label class="block space-y-1">
              <span class="text-sm text-app">Circuit</span>
              <SearchSelect v-model="form.circuit" :options="circuitOptions" placeholder="Select circuit..." />
              <p v-if="errors.circuit" class="text-xs text-red-600">{{ errors.circuit }}</p>
            </label>
          </div>

          <!-- Circuit Tags -->
          <div class="sm:col-span-2">
            <label class="block space-y-1">
              <span class="text-sm text-app">Circuit Tags</span>
              <TagsInput v-model="userTags" :preset="autoTags" placeholder="Add tag and press Enter" />
              <p class="text-xs text-muted">Auto from selections; you can add/remove your own.</p>
            </label>
          </div>

          <!-- Station / Section / Sub Section -->
          <div class="sm:col-span-2 grid gap-4 sm:grid-cols-3">
            <SearchSelect v-model="form.station" :options="[]" placeholder="Select station..." />
            <SearchSelect v-model="form.section" :options="[]" placeholder="Select section..." />
            <SearchSelect v-model="form.sub_section" :options="[]" placeholder="Select sub section..." />
          </div>

          <!-- Reported At / Assigned To / Current Status -->
          <div class="sm:col-span-2 grid gap-4 sm:grid-cols-3">
            <DateTime label="Reported At" v-model="form.reported_at" />
            <SearchSelect v-model="form.assigned_to" :options="[]" placeholder="Select assignee..." />
            <SelectBox label="Current Status" v-model="form.current_status" :options="statusOptions" />
          </div>

          <!-- Remark of Fail -->
          <div class="sm:col-span-2">
            <textarea v-model="form.remark_fail" rows="2" class="w-full rounded-lg border-app bg-card text-app p-3 text-sm" placeholder="Notes..."></textarea>
          </div>

          <!-- Resolved-only fields -->
          <template v-if="form.current_status === 'Resolved'">
            <DateTime label="Resolve At" v-model="form.resolved_at" />
            <InputText label="Duration (minutes)" v-model="form.duration_minutes" />
            <textarea v-model="form.remark_right" rows="2" class="sm:col-span-2 w-full rounded-lg border-app bg-card text-app p-3 text-sm" placeholder="Notes on resolution..."></textarea>
          </template>

          <!-- Attachments -->
          <div class="sm:col-span-2 text-sm text-muted">Attachments: (uploader to be added)</div>

          <!-- Buttons -->
          <div class="sm:col-span-2 flex items-center justify-between pt-2">
            <!-- left group -->
            <button type="button" class="btn btn-solid" @click="ui.pushToast({ type: 'info', title: 'Draft', message: 'Saved as draft (demo).' })">
              Save as Draft
            </button>
            <!-- right group -->
            <div class="flex gap-3">
              <button type="button" class="btn btn-outline" @click="resetForm">Reset</button>
              <button type="button" class="btn btn-primary" @click="submit">Submit</button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Divider -->
    <div
      class="w-1 self-stretch bg-[var(--border)] hover:bg-[var(--text)]/30 cursor-col-resize rounded"
      :class="dragging ? 'bg-[var(--text)]/40' : ''"
      @mousedown="onDragStart"
    />

    <!-- RIGHT: Recent Failure Logs -->
    <div class="space-y-4" :style="{ width: 100 - split + '%' }">
      <RecentFailures
        storage-key="rf-newfailure"
        @view="row => console.log('open details', row)"
        @notify="row => console.log('notify', row)"
        @edit="row => console.log('edit', row)"
        @delete="row => console.log('delete', row)"
      />
    </div>
  </div>
</template>
