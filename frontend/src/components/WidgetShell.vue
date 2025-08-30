<script setup>
import { computed } from 'vue'

const props = defineProps({
  title: { type: String, required: true },

  // v-models
  chartType: { type: String, default: 'bar' },              // 'bar' | 'line' | 'pie' | 'doughnut' | 'table'
  range:     { type: String, default: 'today' },            // 'today' | 'week' | 'month' | 'year' | 'custom'

  // optional: show the small “…” action icons later
  dense: { type: Boolean, default: false },
})

const emit = defineEmits(['update:chartType', 'update:range', 'refresh'])

const ranges = [
  { key: 'today', label: 'Today' },
  { key: 'week',  label: 'This Week' },
  { key: 'month', label: 'This Month' },
  { key: 'year',  label: 'This Year' },
  { key: 'custom',label: 'Custom' },
]

const rangeLabel = computed(() => ranges.find(r => r.key === props.range)?.label ?? '')
function setRange(key){ emit('update:range', key) }
function setType(e){ emit('update:chartType', e.target.value) }
</script>

<template>
  <div class="rounded-2xl border bg-white p-3 md:p-4">
    <!-- Header -->
    <div class="mb-3 flex items-center gap-2">
      <h3 class="text-lg md:text-xl font-semibold flex-1 leading-tight">{{ title }}</h3>

      <!-- Chart type selector -->
      <select
        :value="chartType"
        @change="setType"
        class="rounded-lg border px-2 py-1 text-sm bg-white"
        title="Chart type"
      >
        <option value="bar">Bar</option>
        <option value="line">Line</option>
        <option value="pie">Pie</option>
        <option value="doughnut">Doughnut</option>
        <option value="table">Table</option>
      </select>

      <!-- (optional action icons we can wire later)
      <button class="p-2 rounded-lg hover:bg-gray-100" title="Refresh" @click="$emit('refresh')">
        <i class="pi pi-refresh text-sm"></i>
      </button>
      -->
    </div>

    <!-- Time filters -->
    <div class="mb-3 flex flex-wrap gap-2">
      <button
        v-for="r in ranges"
        :key="r.key"
        class="px-3 py-1.5 text-sm rounded-md border transition"
        :class="range === r.key ? 'bg-gray-900 text-white border-gray-900' : 'bg-white text-gray-700 hover:bg-gray-100'"
        @click="setRange(r.key)"
      >
        {{ r.label }}
      </button>
    </div>

    <!-- Body slot: give range & chartType to child -->
    <div class="min-h-[220px]">
      <slot :range="range" :chart-type="chartType" :rangeLabel="rangeLabel"></slot>
    </div>
  </div>
</template>