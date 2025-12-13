<script setup>
import { computed } from 'vue'

const props = defineProps({
  modelValue: { type: Boolean, default: false }, // open/close
  item: { type: Object, default: () => null },   // failure object
})
const emit = defineEmits(['update:modelValue', 'notify', 'edit', 'delete'])

function close() { emit('update:modelValue', false) }

const duration = computed(() => {
  const r = props.item?.reported_at || props.item?.reportedAt
  const x = props.item?.resolved_at || props.item?.resolvedAt
  if (!r || !x) return '—'
  const ms = new Date(x) - new Date(r)
  const d = Math.floor(ms / 86400000)
  const h = Math.floor((ms % 86400000) / 3600000)
  const m = Math.round((ms % 3600000) / 60000)
  
  if (d > 0) return `${d}d ${h}h ${m}m`
  return `${h}h ${m}m`
})
function fmt(ts) { return ts ? new Date(ts).toLocaleString('en-GB', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', hour12: false }) : '—' }

function badgeClasses(s) {
  if (s === 'Active')       return 'badge-danger'
  if (s === 'In Progress')  return 'badge-warning'
  if (s === 'Resolved')     return 'badge-success'
  if (s === 'On Hold')      return 'badge-hold'
  return 'badge-neutral'
}
</script>

<template>
  <!-- Overlay -->
  <div
    v-show="modelValue"
    class="fixed inset-0 z-50"
    aria-modal="true"
    role="dialog"
  >
    <div class="absolute inset-0 bg-black/30" @click="close" />

    <!-- Panel -->
    <div class="absolute inset-y-0 right-0 w-full max-w-md bg-card text-app shadow-xl border-l border-app flex flex-col">
      <!-- Header -->
      <div class="px-4 py-3 border-b border-app flex items-center justify-between">
        <div class="font-semibold">Failure Details</div>
        <button class="p-2 rounded-lg hover:bg-card" @click="close" aria-label="Close">
          <svg viewBox="0 0 24 24" class="w-5 h-5"><path fill="currentColor" d="M18.3 5.71L12 12l6.3 6.29l-1.41 1.42L10.59 13.4L4.29 19.7L2.88 18.3L9.17 12L2.88 5.71L4.29 4.29l6.3 6.3l6.29-6.3z"/></svg>
        </button>
      </div>

      <!-- Body -->
      <div class="p-4 space-y-4 overflow-auto">
        <div class="flex items-center justify-between">
          <div class="text-lg font-semibold">{{ item?.fail_id || item?.id || '—' }}</div>
          <span class="badge" :class="badgeClasses(item?.current_status || item?.status)">{{ item?.current_status || item?.status || '—' }}</span>
        </div>

        <div class="grid grid-cols-2 gap-3 text-sm">
          <div>
            <div class="text-muted">Section</div>
            <div class="font-medium">{{ item?.section?.name || item?.section || '—' }}</div>
          </div>
          <div>
            <div class="text-muted">Sub-Section</div>
            <div class="font-medium">{{ item?.sub_section?.name || item?.sub_section || '—' }}</div>
          </div>
          <div>
            <div class="text-muted">Depot</div>
            <div class="font-medium">{{ item?.station?.depot_display || item?.section?.depot_display || '—' }}</div>
          </div>
          <div>
            <div class="text-muted">Severity</div>
            <div class="font-medium">{{ item?.severity || '—' }}</div>
          </div>
          <div>
            <div class="text-muted">Station</div>
            <div class="font-medium">{{ item?.station?.code || item?.station?.name || item?.station || '—' }}</div>
          </div>
          <div>
            <div class="text-muted">Circuit</div>
            <div>
              <div class="font-medium">{{ item?.circuit?.circuit_id || item?.circuit || '—' }}</div>
              <div class="font-medium text-xs" style="color: #E1AA36;">{{ item?.circuit?.name || '' }}</div>
            </div>
          </div>
          <div>
            <div class="text-muted">Assigned To</div>
            <div class="font-medium">{{ item?.assigned_to?.name || item?.assigned_to?.username || '—' }}</div>
          </div>
          <div>
            <div class="text-muted">Reported</div>
            <div class="font-medium">{{ fmt(item?.reported_at || item?.reportedAt) }}</div>
          </div>
          <div>
            <div class="text-muted">Resolved</div>
            <div class="font-medium">{{ fmt(item?.resolved_at || item?.resolvedAt) }}</div>
          </div>
          <div>
            <div class="text-muted">Resolution Time</div>
            <div class="font-medium">{{ duration }}</div>
          </div>
        </div>

        <div>
          <div class="text-muted text-sm mb-1">Failure Remarks</div>
          <div class="rounded-lg border-app bg-card text-app p-3 min-h-[72px] text-sm">
            {{ item?.remark_fail || item?.notes || '—' }}
          </div>
        </div>

        <div v-if="item?.remark_right">
          <div class="text-muted text-sm mb-1">Resolution Remarks</div>
          <div class="rounded-lg border-app bg-card text-app p-3 min-h-[72px] text-sm">
            {{ item?.remark_right }}
          </div>
        </div>
      </div>

      <!-- Footer -->
      <div class="px-4 py-3 border-t border-app flex items-center justify-end">
        <button class="text-sm px-3 py-2 rounded-lg border-app bg-card hover:bg-card" @click="close">Close</button>
      </div>
    </div>
  </div>
</template>
