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
  if (s === 'Active')       return 'bg-red-100 text-red-700'
  if (s === 'In Progress')  return 'bg-amber-100 text-amber-700'
  if (s === 'Resolved')     return 'bg-green-100 text-green-700'
  if (s === 'On Hold')      return 'bg-orange-100 text-orange-700'
  return 'bg-gray-100 text-gray-700'
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
    <div class="absolute inset-y-0 right-0 w-full max-w-md bg-white shadow-xl border-l flex flex-col">
      <!-- Header -->
      <div class="px-4 py-3 border-b flex items-center justify-between">
        <div class="font-semibold">Failure Details</div>
        <button class="p-2 rounded-lg hover:bg-gray-100" @click="close" aria-label="Close">
          <svg viewBox="0 0 24 24" class="w-5 h-5"><path fill="currentColor" d="M18.3 5.71L12 12l6.3 6.29l-1.41 1.42L10.59 13.4L4.29 19.7L2.88 18.3L9.17 12L2.88 5.71L4.29 4.29l6.3 6.3l6.29-6.3z"/></svg>
        </button>
      </div>

      <!-- Body -->
      <div class="p-4 space-y-4 overflow-auto">
        <div class="flex items-center justify-between">
          <div class="text-lg font-semibold">{{ item?.id ?? '—' }}</div>
          <span class="text-xs px-2 py-0.5 rounded-full border" :class="badgeClasses(item?.status)">{{ item?.status ?? '—' }}</span>
        </div>

        <div class="grid grid-cols-2 gap-3 text-sm">
          <div>
            <div class="text-gray-500">Section</div>
            <div class="font-medium">{{ item?.section ?? '—' }}</div>
          </div>
          <div>
            <div class="text-gray-500">Severity</div>
            <div class="font-medium">{{ item?.severity ?? '—' }}</div>
          </div>
          <div>
            <div class="text-gray-500">Station</div>
            <div class="font-medium">{{ item?.station ?? '—' }}</div>
          </div>
          <div>
            <div class="text-gray-500">Circuit</div>
            <div class="font-medium">{{ item?.circuit ?? '—' }}</div>
          </div>
          <div>
            <div class="text-gray-500">Reported</div>
            <div class="font-medium">{{ fmt(item?.reportedAt) }}</div>
          </div>
          <div>
            <div class="text-gray-500">Resolved</div>
            <div class="font-medium">{{ fmt(item?.resolvedAt) }}</div>
          </div>
          <div>
            <div class="text-gray-500">Resolution Time</div>
            <div class="font-medium">{{ duration }}</div>
          </div>
        </div>

        <div>
          <div class="text-gray-500 text-sm mb-1">Notes</div>
          <div class="rounded-lg border p-3 min-h-[72px] text-sm bg-gray-50">
            {{ item?.notes ?? '—' }}
          </div>
        </div>
      </div>

      <!-- Footer -->
      <div class="px-4 py-3 border-t flex items-center justify-between">
        <button class="text-sm px-3 py-2 rounded-lg border hover:bg-gray-50" @click="close">Close</button>
        <div class="flex items-center gap-2">
          <button class="text-sm px-3 py-2 rounded-lg border hover:bg-gray-50" @click="$emit('notify', item)">Notify</button>
          <button class="text-sm px-3 py-2 rounded-lg border hover:bg-gray-50" @click="$emit('edit', item)">Edit</button>
          <button class="text-sm px-3 py-2 rounded-lg border text-red-600 hover:bg-red-50 border-red-200" @click="$emit('delete', item)">Delete</button>
        </div>
      </div>
    </div>
  </div>
</template>