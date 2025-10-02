<script setup>
import { computed } from 'vue'

const props = defineProps({
  modelValue: { type: Boolean, default: false }, // open/close
  item: { type: Object, default: () => null },   // failure object
  showActions: { type: Boolean, default: true },
})
const emit = defineEmits(['update:modelValue', 'notify', 'edit', 'delete'])

function close() { emit('update:modelValue', false) }

// Correctly calculates duration from 'reported_at' and 'resolved_at'
const duration = computed(() => {
  const start = props.item?.reported_at;
  const end = props.item?.resolved_at;
  if (!start || !end) return '—'
  const diff = new Date(end) - new Date(start)
  if (diff < 0) return '—'
  const minutes = Math.floor(diff / 60000)
  if (minutes < 60) return `${minutes}m`
  const hours = Math.floor(minutes / 60)
  const mins = minutes % 60
  return `${hours}h ${mins}m`
})

function fmt(ts) { 
  return ts ? new Date(ts).toLocaleString('en-IN') : '—' 
}

function badgeClasses(s) {
  if (s === 'Active')       return 'badge-danger'
  if (s === 'In Progress')  return 'badge-warning'
  if (s === 'Resolved')     return 'badge-success'
  if (s === 'On Hold')      return 'badge-hold'
  if (s === 'Information')  return 'badge-neutral'
  return 'badge-neutral'
}

const depotCode = computed(() => {
    if (props.item?.station?.depot_name) return props.item.station.depot_name;
    if (props.item?.section?.depot_name) return props.item.section.depot_name;
    return '—';
});

const circuitTags = computed(() => {
    if (props.item?.circuit?.circuit_id) {
        return `#${props.item.circuit.circuit_id.replace(/\s+/g, '_')}`;
    }
    return '—';
});

</script>

<template>
  <div v-show="modelValue" class="fixed inset-0 z-50" aria-modal="true" role="dialog">
    <div class="absolute inset-0 bg-black/30" @click="close" />

    <div class="absolute inset-y-0 right-0 w-full max-w-md bg-card text-app shadow-xl border-l border-app flex flex-col">
      <div class="px-4 py-3 border-b border-app flex items-center justify-between">
        <div class="font-semibold">Failure Details</div>
        <button class="p-2 rounded-lg hover:bg-card" @click="close" aria-label="Close">
          <svg viewBox="0 0 24 24" class="w-5 h-5"><path fill="currentColor" d="M18.3 5.71L12 12l6.3 6.29l-1.41 1.42L10.59 13.4L4.29 19.7L2.88 18.3L9.17 12L2.88 5.71L4.29 4.29l6.3 6.3l6.29-6.3z"/></svg>
        </button>
      </div>

      <div v-if="item" class="p-4 space-y-4 overflow-auto">
        <div class="flex items-start justify-between">
          <div class="text-lg font-semibold">{{ item.fail_id || '—' }}</div>
          <span class="badge" :class="badgeClasses(item.current_status)">{{ item.current_status || '—' }}</span>
        </div>

        <div class="grid grid-cols-2 gap-x-4 gap-y-3 text-sm">
          <div>
            <div class="text-muted">Circuit</div>
            <div class="font-medium">{{ item.circuit?.circuit_id || '—' }}</div>
          </div>
          <div>
            <div class="text-muted">Severity</div>
            <div class="font-medium">{{ item.severity || '—' }}</div>
          </div>
          <div>
            <div class="text-muted">Depot</div>
            <div class="font-medium">{{ depotCode }}</div>
          </div>
           <div>
            <div class="text-muted">Station Code</div>
            <div class="font-medium">{{ item.station?.code || '—' }}</div>
          </div>
          <div>
            <div class="text-muted">Section</div>
            <div class="font-medium">{{ item.section?.name || '—' }}</div>
          </div>
          <div>
            <div class="text-muted">Sub Section</div>
            <div class="font-medium">{{ item.sub_section?.name || '—' }}</div>
          </div>
           <div>
            <div class="text-muted">Reported At</div>
            <div class="font-medium">{{ fmt(item.reported_at) }}</div>
          </div>
          <div>
            <div class="text-muted">Assigned To</div>
            <div class="font-medium">{{ item.assigned_to?.name || '—' }}</div>
          </div>
        </div>

        <div>
          <div class="text-muted text-sm mb-1">Remarks for Fail</div>
          <div class="rounded-lg border-app bg-gray-100 p-3 min-h-[60px] text-sm whitespace-pre-wrap">
            {{ item.remark_fail || 'No remarks.' }}
          </div>
        </div>
        
        <div class="border-t border-app pt-3 space-y-3">
            <div class="grid grid-cols-2 gap-4 text-sm">
                <div>
                    <div class="text-muted">Resolution Time</div>
                    <div class="font-medium">{{ fmt(item.resolved_at) }}</div>
                </div>
                <div>
                    <div class="text-muted">Duration</div>
                    <div class="font-medium">{{ duration }}</div>
                </div>
            </div>
            <div>
              <div class="text-muted text-sm mb-1">Remarks for Resolve</div>
              <div class="rounded-lg border-app bg-gray-100 p-3 min-h-[60px] text-sm whitespace-pre-wrap">
                {{ item.remark_right || 'No remarks.' }}
              </div>
            </div>
        </div>

        <div class="border-t border-app pt-3">
          <div class="text-muted text-sm mb-1">Circuit Tags</div>
          <div class="font-medium text-sm text-blue-700">{{ circuitTags }}</div>
        </div>
      </div>
      
      <div v-else class="p-6 text-center text-muted">Select an item to see details.</div>

      <div v-if="showActions" class="mt-auto px-4 py-3 border-t border-app flex items-center justify-between">
        <button class="btn btn-outline" @click="close">Close</button>
        <div class="flex items-center gap-2">
          <button class="btn" @click="$emit('notify', item)">Notify</button>
          <button class="btn" @click="$emit('edit', item)">Edit</button>
          <button class="btn btn-danger" @click="$emit('delete', item)">Delete</button>
        </div>
      </div>
    </div>
  </div>
</template>