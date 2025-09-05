<script setup>
import { computed } from 'vue'
import { Bar } from 'vue-chartjs'
import { Chart, BarElement, CategoryScale, LinearScale, Title, Tooltip, Legend, Filler } from 'chart.js'
import { STATUS_ORDER, bgColor, borderColor } from '@/lib/statusColors'

Chart.register(BarElement, CategoryScale, LinearScale, Title, Tooltip, Legend, Filler)

const props = defineProps({
  data: { type: Object, required: true },
  options: { type: Object, default: () => ({ responsive: true, maintainAspectRatio: false }) },
})

const normalized = computed(() => {
  const d = JSON.parse(JSON.stringify(props.data || { labels: [], datasets: [] }))
  if (!d || !Array.isArray(d.datasets)) return props.data
  d.datasets = d.datasets.map((ds) => {
    const out = { ...ds }
    const label = String(out.label ?? '')
    if (STATUS_ORDER.includes(label)) {
      if (!out.borderColor) out.borderColor = borderColor(label)
      if (!out.backgroundColor) out.backgroundColor = bgColor(label, 0.8)
      if (out.borderWidth == null) out.borderWidth = 1
    }
    return out
  })
  return d
})
</script>

<template>
  <!-- Fill parent; keep a safe minimum for axes + legend -->
  <div class="relative w-full h-full min-h-[260px]">
    <Bar :data="normalized" :options="options" />
  </div>
  
</template>

<style scoped>
/* Important: do NOT force height:100% on the canvas */
:global(canvas) { width: 100% !important; }
</style>
