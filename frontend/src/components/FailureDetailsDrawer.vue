<script setup>
import { computed } from 'vue'

const props = defineProps({
  modelValue: { type: Boolean, default: false }, // open/close
  item: { type: Object, default: () => null },   // failure object
})
const emit = defineEmits(['update:modelValue', 'notify', 'edit', 'delete'])

function close() { emit('update:modelValue', false) }

const duration = computed(() => {
  const r = props.item?.reportedAt, x = props.item?.resolvedAt
  if (!r || !x) return '—'
  const ms = x - r
  const h = Math.floor(ms / 3600000)
  const m = Math.round((ms % 3600000) / 60000)
  return `${h}h ${m}m`
})
function fmt(ts) { return ts ? new Date(ts).toLocaleString() : '—' }

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
          <div class="text-lg font-semibold">{{ item?.id ?? '—' }}</div>
          <span class="badge" :class="badgeClasses(item?.status)">{{ item?.status ?? '—' }}</span>
        </div>

        <div class="grid grid-cols-2 gap-3 text-sm">
          <div>
            <div class="text-muted">Section</div>
            <div class="font-medium">{{ item?.section ?? '—' }}</div>
          </div>
          <div>
            <div class="text-muted">Severity</div>
            <div class="font-medium">{{ item?.severity ?? '—' }}</div>
          </div>
          <div>
            <div class="text-muted">Station</div>
            <div class="font-medium">{{ item?.station ?? '—' }}</div>
          </div>
          <div>
            <div class="text-muted">Circuit</div>
            <div class="font-medium">{{ item?.circuit ?? '—' }}</div>
          </div>
          <div>
            <div class="text-muted">Reported</div>
            <div class="font-medium">{{ fmt(item?.reportedAt) }}</div>
          </div>
          <div>
            <div class="text-muted">Resolved</div>
            <div class="font-medium">{{ fmt(item?.resolvedAt) }}</div>
          </div>
          <div>
            <div class="text-muted">Resolution Time</div>
            <div class="font-medium">{{ duration }}</div>
          </div>
        </div>

        <div>
          <div class="text-muted text-sm mb-1">Notes</div>
          <div class="rounded-lg border-app bg-card text-app p-3 min-h-[72px] text-sm">
            {{ item?.notes ?? '—' }}
          </div>
        </div>
      </div>

      <!-- Footer -->
      <div class="px-4 py-3 border-t border-app flex items-center justify-between">
        <button class="text-sm px-3 py-2 rounded-lg border-app bg-card hover:bg-card" @click="close">Close</button>
        <div class="flex items-center gap-2">
          <button class="text-sm px-3 py-2 rounded-lg border-app bg-card hover:bg-card" @click="$emit('notify', item)">Notify</button>
          <button class="text-sm px-3 py-2 rounded-lg border-app bg-card hover:bg-card" @click="$emit('edit', item)">Edit</button>
          <button class="text-sm px-3 py-2 rounded-lg border text-red-600 hover:bg-red-50 border-red-200" @click="$emit('delete', item)">Delete</button>
        </div>
      </div>
    </div>
  </div>
</template>
