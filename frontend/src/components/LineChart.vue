<script setup>
import { computed } from 'vue'
import { Line } from 'vue-chartjs'
import { Chart, LineController, LineElement, PointElement, CategoryScale, LinearScale, Title, Legend, Filler } from 'chart.js'
import { STATUS_ORDER, bgColor, borderColor } from '@/lib/statusColors'

// Removed Tooltip to prevent global side-effects crashing BarChart
Chart.register(LineController, LineElement, PointElement, CategoryScale, LinearScale, Title, Legend, Filler)

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
      if (!out.backgroundColor) out.backgroundColor = bgColor(label, 0.25)
      if (out.fill == null) out.fill = true
      if (out.tension == null) out.tension = 0.3
    }
    return out
  })
  return d
})
</script>

<template>
  <div class="relative w-full h-full min-h-[300px]">
    <Line :data="normalized" :options="options" />
  </div>
  
</template>

<style scoped>
:global(canvas) { width: 100% !important; }
</style>
