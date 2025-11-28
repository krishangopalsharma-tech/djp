<script setup>
import { computed } from 'vue'
import { Bar } from 'vue-chartjs'
import { Chart, BarElement, CategoryScale, LinearScale, Title, Tooltip, Legend, Filler } from 'chart.js'
import { colorsForDatasetLabel } from '@/lib/statusColors'

Chart.register(BarElement, CategoryScale, LinearScale, Title, Tooltip, Legend, Filler)

const props = defineProps({
  data: { type: Object, required: true },
  options: { type: Object, default: () => ({ responsive: true, maintainAspectRatio: false }) },
})

// Disable any plugin-driven color overrides to ensure our palette wins
const computedOptions = computed(() => {
  const base = JSON.parse(JSON.stringify(props.options || {}))
  base.plugins = base.plugins || {}
  base.plugins.colors = false
  return base
})

const normalized = computed(() => {
  const d = JSON.parse(JSON.stringify(props.data || { labels: [], datasets: [] }))
  if (!d || !Array.isArray(d.datasets)) return props.data
  d.datasets = d.datasets.map((ds) => {
    const out = { ...ds }
    const label = String(out.label ?? '')
    const mapped = colorsForDatasetLabel(label, 0.85)
    if (mapped) {
      out.backgroundColor = mapped.bg
      out.borderColor = mapped.border
      out.borderWidth = out.borderWidth ?? 1
      out.hoverBackgroundColor = mapped.bg
      out.hoverBorderColor = mapped.border
    }
    return out
  })
  return d
})
</script>

<template>
  <!-- Fill parent; keep a safe minimum for axes + legend -->
  <div class="relative w-full h-full min-h-[260px]">
    <Bar :data="normalized" :options="computedOptions" />
  </div>
  
</template>

<style scoped>
/* Important: do NOT force height:100% on the canvas */
:global(canvas) { width: 100% !important; }
</style>
