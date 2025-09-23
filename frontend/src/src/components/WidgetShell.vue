<script setup>
import { computed } from 'vue'

const props = defineProps({
  // Make title optional so callers can omit it when header is hidden
  title: { type: String, default: '' },

  // v-models
  chartType: { type: String, default: 'bar' },              // 'bar' | 'line' | 'pie' | 'doughnut' | 'table'
  range:     { type: String, default: 'today' },            // 'today' | '7d' | '30d' | 'custom'

  // optional: show the small “…” action icons later
  dense: { type: Boolean, default: false },
  // allow hiding the entire header area (title + selector + chips)
  hideHeader: { type: Boolean, default: false },
})

const emit = defineEmits(['update:chartType', 'update:range', 'refresh'])

const ranges = [
  { key: 'today', label: 'Today' },
  { key: '7d',    label: 'Last 7 days' },
  { key: '30d',   label: 'Last 30 days' },
  { key: 'custom',label: 'Custom' },
]

const rangeLabel = computed(() => ranges.find(r => r.key === props.range)?.label ?? '')
function setRange(key){ emit('update:range', key) }
function setType(e){ emit('update:chartType', e.target.value) }
</script>

<template>
  <div class="rounded-2xl border bg-white p-3 md:p-4">
    <!-- Header -->
    <div v-if="!hideHeader" class="mb-3 flex items-center gap-2">
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

    <!-- Time filters (chips) -->
    <div v-if="!hideHeader" class="mb-3 chip-group">
      <button
        v-for="r in ranges"
        :key="r.key"
        class="chip"
        :class="range === r.key ? 'selected-primary' : 'text-app hover-primary'"
        :aria-pressed="String(range === r.key)"
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
