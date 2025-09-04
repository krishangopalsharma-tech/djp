<script setup>
import { computed } from 'vue'

const props = defineProps({
  modelValue: {
    type: Object,
    // { range: 'today' | '7d' | '30d', status: string[] }
    default: () => ({ range: 'today', status: ['Active','In Progress','Resolved','On Hold'] })
  },
  // New: render controls selectively so page header can place them
  showRanges: { type: Boolean, default: true },
  showStatuses: { type: Boolean, default: true },
})
const emit = defineEmits(['update:modelValue'])

const ranges = [
  { key: 'today', label: 'Today' },
  { key: '7d',    label: 'Last 7 days' },
  { key: '30d',   label: 'Last 30 days' },
]

const statusOptions = [
  { key: 'Active',      label: 'Active' },
  { key: 'In Progress', label: 'In Progress' },
  { key: 'Resolved',    label: 'Resolved' },
  { key: 'On Hold',     label: 'On Hold' },
]

const selectedRange = computed(() => props.modelValue.range)
const selectedStatuses = computed(() => new Set(props.modelValue.status || []))

function setRange(key) {
  emit('update:modelValue', { ...props.modelValue, range: key })
}

function toggleStatus(key) {
  const set = new Set(selectedStatuses.value)
  set.has(key) ? set.delete(key) : set.add(key)
  emit('update:modelValue', { ...props.modelValue, status: Array.from(set) })
}

function chipClassForStatus(key) {
  switch (key) {
    case 'Resolved':    return 'chip chip-active-resolved'
    case 'In Progress': return 'chip chip-active-inprogress'
    case 'On Hold':     return 'chip chip-active-onhold'
    case 'Active':      return 'chip chip-active-active'
    default:            return 'chip'
  }
}
</script>

<template>
  <div class="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
    <!-- Range pills -->
    <div v-if="showRanges" class="chip-group">
      <button
        v-for="r in ranges"
        :key="r.key"
        class="chip"
        :class="selectedRange === r.key ? 'selected-primary' : 'text-app hover-primary'"
        @click="setRange(r.key)"
      >
        {{ r.label }}
      </button>
    </div>

    <!-- Status toggles -->
    <div v-if="showStatuses" class="flex flex-wrap gap-2">
      <button
        v-for="s in statusOptions"
        :key="s.key"
        class="rounded-full transition"
        :class="selectedStatuses.has(s.key) ? chipClassForStatus(s.key) : 'chip text-app hover-primary'"
        @click="toggleStatus(s.key)"
      >
        {{ s.label }}
      </button>
    </div>
  </div>
</template>
