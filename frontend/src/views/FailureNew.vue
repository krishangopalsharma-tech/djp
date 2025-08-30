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

const split = ref(50)          // left pane width in %
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
  fail_id: '',                        // read-only for now (server will assign later)
  circuit: null,                      // SearchSelect
  //circuit_tags: '',                   // simple text for now
  //severity: '',
  station: null,                      // dependent SearchSelect (next steps)
  section: null,                      // dependent
  sub_section: null,                  // dependent
  reported_at: new Date().toISOString().slice(0,16),
  assigned_to: null,                  // dependent SearchSelect (next steps)
  current_status: 'Active',
  remark_fail: '',
  // attachments: []                  // will add uploader later
  resolved_at: '',                 // shown when status = Resolved
  duration_minutes: '',            // auto-calculated
  remark_right: '',                // shown when status = Resolved
})

const errors = reactive({})

// Build auto tags from selected values
const autoTags = computed(() => {
  const t = []
  if (form.circuit)    t.push(`#${form.circuit}`)
  if (form.station)    t.push(`#${form.station}`)
  if (form.section)    t.push(`#${form.section}`)
  if (form.sub_section)t.push(`#${form.sub_section}`)
  return t
})

// user-added tags
const userTags = ref([])
// combined tags (used in payload)
const allTags = computed(() => [...autoTags.value, ...userTags.value])

function validate() {
  errors.circuit = form.circuit ? '' : 'Required'
  return Object.values(errors).every(v => !v)
}

// helpers for resolved fields
function nowLocalISO() {
  return new Date(Date.now() - (new Date()).getSeconds()*1000 - (new Date()).getMilliseconds())
    .toISOString().slice(0,16)
}

function calcDurationMinutes(startISO, endISO) {
  if (!startISO || !endISO) return ''
  const ms = new Date(endISO) - new Date(startISO)
  if (isNaN(ms) || ms < 0) return ''
  return Math.round(ms / 60000)
}

// Auto-fill Resolve At when status flips to Resolved
watch(() => form.current_status, (v) => {
  if (v === 'Resolved' && !form.resolved_at) form.resolved_at = nowLocalISO()
})

// Recalculate duration whenever reported_at or resolved_at changes
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
    ui.pushToast({ type: 'error', title: 'Missing fields', message: 'Circuit & Severity are required.' })
    return
  }
  ui.pushToast({ type: 'success', title: 'Submitted', message: 'Demo submit — backend later.' })
  console.log('SUBMIT PAYLOAD', payloadPreview.value)
}
</script>


  <template>
    <!-- Two-column layout: left = form, right = recent failures -->
    <div ref="splitWrap" class="flex items-start gap-4">
      <!-- LEFT: New Failure form -->
      <div class="space-y-4" :style="{ width: split + '%' }">
          <div class="text-center">
            <h2 class="text-2xl font-semibold leading-tight">New Failure</h2>
          </div>
        
        <div class="rounded-2xl border bg-white p-4 text-gray-900">
          <div class="grid gap-4 sm:grid-cols-2">
            <!-- Fail ID / Circuit -->
            <div>
              <InputText label="Fail ID (server will assign)" v-model="form.fail_id" placeholder="Leave empty" />
            </div>
             <div>
              <label class="block space-y-1">
                <span class="text-sm text-gray-700">Circuit</span>
                <SearchSelect v-model="form.circuit" :options="circuitOptions" placeholder="Select circuit..." />
                <p v-if="errors.circuit" class="text-xs text-red-600">{{ errors.circuit }}</p>
              </label>
            </div>
                    <!-- Circuit Tags (editable: auto + custom) FULL WIDTH -->
            <div class="sm:col-span-2">
              <label class="block space-y-1">
                <span class="text-sm text-gray-700">Circuit Tags</span>
                <TagsInput v-model="userTags" :preset="autoTags" placeholder="Add tag and press Enter" />
                <p class="text-xs text-gray-500">Auto from selections; you can add/remove your own.</p>
              </label>
            </div>
            
            <!-- Station / Section / Sub Section (same line: 3 cols) -->
            <div class="sm:col-span-2 grid gap-4 sm:grid-cols-3">
              <div>
                <label class="block space-y-1">
                  <span class="text-sm text-gray-700">Station</span>
                  <SearchSelect v-model="form.station" :options="[]" placeholder="Select station..." />
                </label>
              </div>
              <div>
                <label class="block space-y-1">
                  <span class="text-sm text-gray-700">Section</span>
                  <SearchSelect v-model="form.section" :options="[]" placeholder="Select section..." />
                </label>
              </div>
              <div>
                <label class="block space-y-1">
                  <span class="text-sm text-gray-700">Sub Section</span>
                  <SearchSelect v-model="form.sub_section" :options="[]" placeholder="Select sub section..." />
                </label>
              </div>
            </div>
            
            <!-- Reported At / Assigned To / Current Status (same line: 3 cols) -->
            <div class="sm:col-span-2 grid gap-4 sm:grid-cols-3">
              <div>
                <DateTime label="Reported At" v-model="form.reported_at" />
              </div>
              <div>
                <label class="block space-y-1">
                  <span class="text-sm text-gray-700">Assigned To</span>
                  <SearchSelect v-model="form.assigned_to" :options="[]" placeholder="Select assignee..." />
                </label>
              </div>
              <div>
                <SelectBox label="Current Status" v-model="form.current_status" :options="statusOptions" />
              </div>
            </div>

            
            <!-- Remark of Fail (full width) -->
            <div class="sm:col-span-2">
              <label class="block space-y-1">
                <span class="text-sm text-gray-700">Remark of Fail</span>
                <textarea v-model="form.remark_fail" rows="2" class="w-full rounded-lg border p-3 text-sm bg-white" placeholder="Notes..."></textarea>
              </label>
            </div>
            
            <!-- Resolved-only fields (below Remark of Fail) -->
            <template v-if="form.current_status === 'Resolved'">
              <div>
                <DateTime label="Resolve At" v-model="form.resolved_at" />
              </div>
              <div>
                <InputText label="Duration (minutes)" v-model="form.duration_minutes" />
              </div>
              <div class="sm:col-span-2">
                <label class="block space-y-1">
                  <span class="text-sm text-gray-700">Remark of Right</span>
                  <textarea v-model="form.remark_right" rows="2" class="w-full rounded-lg border p-3 text-sm bg-white" placeholder="Notes on resolution..."></textarea>
                </label>
              </div>
            </template>
            
            <!-- Attachments (placeholder) -->
            <div class="sm:col-span-2 text-sm text-gray-500">
              Attachments: (uploader to be added)
            </div>
            
            <!-- Buttons -->
            <div class="sm:col-span-2 flex items-center justify-between pt-2">
               <!-- left group -->
                <div class="flex flex-wrap gap-4">
                  <PButton
                    label="Save as Draft"
                    icon="pi pi-save"
                    class="btn-solid-1 shadow-lg hover:shadow-xl transition-shadow"
                    :pt="{
                      root: { class: 'inline-flex h-11 px-6 rounded-full gap-2 whitespace-nowrap' },
                      icon: { class: 'text-base' },
                      label: { class: 'leading-none font-medium' }
                          }"
                  />
                </div>

              <!-- right -->
              <div class="flex gap-5">
                <PButton
                  label="Reset"
                  icon="pi pi-refresh"
                  class="btn-solid-2 shadow-lg hover:shadow-xl transition-shadow"
                  :pt="{
                    root: { class: 'inline-flex h-11 px-6 rounded-full gap-2 whitespace-nowrap' },
                    icon: { class: 'text-base' },
                    label: { class: 'leading-none font-medium' }
                      }"
                />
                <PButton
                label="Submit"
                icon="pi pi-send"
                class="btn-solid-3 shadow-lg hover:shadow-xl transition-shadow"
                :pt="{
                  root: { class: 'h-11 min-w-[7.5rem] px-5 rounded-lg gap-2 whitespace-nowrap' },
                  icon: { class: 'text-base' },
                  label: { class: 'leading-none font-medium' }
                }"
                 @click="submit"
                />
              </div>
            </div>

          </div>
        </div>
      </div>
      <div
          class="w-1 self-stretch bg-gray-200 hover:bg-gray-400 cursor-col-resize rounded"
          :class="dragging ? 'bg-gray-400' : ''"
          @mousedown="onDragStart"/>

      <!-- RIGHT: Recent Failure Logs -->
      <div class="space-y-4" :style="{ width: (100 - split) + '%' }">
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