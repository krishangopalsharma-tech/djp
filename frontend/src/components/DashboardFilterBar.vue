<script setup>
import { computed } from 'vue'

const props = defineProps({
  modelValue: {
    type: Object,
    // { range: 'today' | '7d' | '30d', status: string[] }
    default: () => ({ range: 'today', status: ['Active','In Progress','Resolved','On Hold'] })
  }
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
</script>

<template>
  <div class="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
    <!-- Range pills -->
    <div class="inline-flex rounded-xl border border-app bg-card p-1">
      <button
        v-for="r in ranges"
        :key="r.key"
        class="px-3 py-1.5 text-sm rounded-lg transition"
        :class="selectedRange === r.key
          ? 'bg-[var(--primary)] text-[var(--primary-foreground)]'
          : 'text-muted hover:bg-card'"
        @click="setRange(r.key)"
      >
        {{ r.label }}
      </button>
    </div>

    <!-- Status toggles -->
    <div class="flex flex-wrap gap-2">
      <button
        v-for="s in statusOptions"
        :key="s.key"
        class="px-3 py-1.5 text-sm rounded-full border transition"
        :class="selectedStatuses.has(s.key)
          ? 'bg-[var(--primary)] text-[var(--primary-foreground)] border-transparent'
          : 'bg-card text-app border-app hover:bg-card'"
        @click="toggleStatus(s.key)"
      >
        {{ s.label }}
      </button>
    </div>
  </div>
</template>
