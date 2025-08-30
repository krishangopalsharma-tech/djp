<script setup>
import { computed, toRefs } from 'vue'
import BarChart from '@/components/BarChart.vue'
import LineChart from '@/components/LineChart.vue'
import PieChart from '@/components/PieChart.vue'
import DoughnutChart from '@/components/DoughnutChart.vue'
import RecentFailures from '@/components/RecentFailures.vue'

/**
 * Runtime props with defaults (no withDefaults).
 * Safe to mount as <SplitPane v-model="split" /> with nothing else.
 */
const props = defineProps({
  panel: {
    type: Object,
    default: () => ({ kind: 'recent' })
  },
  state: {
    type: Object,
    default: () => ({ type: 'table' })
  },
  data: {
    type: Object,
    default: () => ({ labels: [], datasets: [{ data: [] }], recent: [] })
  },
  chartOptions: {
    type: Object,
    default: () => ({ responsive: true, maintainAspectRatio: false })
  },
  /** support v-model */
  modelValue: {
    type: [Number, String],
    default: 50
  }
})

const emit = defineEmits(['update:modelValue'])

/** expose individual props as refs for easy use in template/computed */
const { panel, state, data, chartOptions } = toRefs(props)

function onResize(val) {
  const n = Number(val)
  if (!Number.isNaN(n)) emit('update:modelValue', n)
}

/** Guards so template never explodes when data is empty */
const hasAnyData = computed(() => {
  const d = data.value
  return (
    (Array.isArray(d?.labels) && d.labels.length > 0) ||
    (Array.isArray(d?.recent) && d.recent.length > 0) ||
    (Array.isArray(d?.datasets?.[0]?.data) && d.datasets[0].data.length > 0)
  )
})

/** Safe view type */
const viewType = computed(() => state.value?.type ?? 'table')
</script>

<template>
  <!-- Fallback when no data supplied -->
  <div v-if="!hasAnyData" class="h-full flex items-center justify-center text-sm text-gray-500">
    No data.
  </div>

  <!-- TABLE MODE -->
  <div v-else-if="viewType === 'table'" class="h-full overflow-auto">
    <div v-if="panel.kind !== 'recent'" class="min-w-full text-sm">
      <table class="min-w-full text-sm">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-3 py-2 text-right">Label</th>
            <th class="px-3 py-2 text-right">Value</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="(v, i) in (data.datasets?.[0]?.data || [])"
            :key="i"
            class="border-t"
          >
            <td class="px-3 py-2 text-right">{{ data.labels?.[i] }}</td>
            <td class="px-3 py-2 text-right">{{ v }}</td>
          </tr>
          <tr v-if="!(data.labels?.length)" class="border-t">
            <td colspan="2" class="px-3 py-6 text-center text-gray-500">No data</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Recent failures table -->
    <RecentFailures
      v-else
      :items="data.recent || []"
      :show-toolbar="false"
      :show-bottom-actions="false"
      :show-row-actions="true"
      :loading="false"
      storage-key="rf-analytics"
    />
  </div>

  <!-- CHART MODES -->
  <div v-else-if="viewType==='bar'" class="h-full">
    <BarChart
      :data="{
        labels: data.labels,
        datasets: [{ ...(data.datasets?.[0] || {}), backgroundColor: 'rgba(59,130,246,0.35)', borderColor: 'rgba(59,130,246,1)' }]
      }"
      :options="chartOptions"
    />
  </div>

  <div v-else-if="viewType==='line'" class="h-full">
    <LineChart
      :data="{
        labels: data.labels,
        datasets: [{ ...(data.datasets?.[0] || {}), fill: true, tension: 0.3, backgroundColor: 'rgba(59,130,246,0.2)', borderColor: 'rgba(59,130,246,1)' }]
      }"
      :options="chartOptions"
    />
  </div>

  <div v-else-if="viewType==='pie'" class="h-full">
    <PieChart
      :data="{ labels: data.labels, datasets: [{ ...(data.datasets?.[0] || {}) }] }"
      :options="chartOptions"
    />
  </div>

  <div v-else-if="viewType==='doughnut'" class="h-full">
    <DoughnutChart
      :data="{ labels: data.labels, datasets: [{ ...(data.datasets?.[0] || {}) }] }"
      :options="{ ...chartOptions, cutout: '60%' }"
    />
  </div>

  <!-- FALLBACK -->
  <div v-else class="h-full flex items-center justify-center text-sm text-gray-500">
    No content.
  </div>
</template>

<style scoped>
</style>
