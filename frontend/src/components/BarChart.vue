<script setup>
import { computed } from 'vue'
import { Bar } from 'vue-chartjs'
import { Chart, registerables } from 'chart.js'
import { colorsForDatasetLabel } from '@/lib/statusColors'
import { currentThemeColors, withAlpha } from '@/lib/theme'

// Register EVERYTHING to verify if we were missing a hidden dependency
Chart.register(...registerables)

const props = defineProps({
  data: { type: Object, required: true },
  options: { 
    type: Object, 
    default: () => ({ 
      responsive: true, 
      maintainAspectRatio: false,
      // Re-enable interaction but keep tooltip disabled for now
      scales: {
        x: { type: 'category' }
      },
      interaction: {
        mode: 'nearest',
        axis: 'x',
        intersect: false
      },
      plugins: {
        tooltip: { 
          enabled: true,
          position: 'nearest'
        }, 
        legend: { display: true }
      }
    }) 
  },
})

const normalized = computed(() => {
  const d = JSON.parse(JSON.stringify(props.data || { labels: [], datasets: [] }))
  if (!d || !Array.isArray(d.datasets)) return props.data
  
  d.datasets = d.datasets.map((ds) => {
    const out = { ...ds }
    const label = String(out.label ?? '')
    const mapped = colorsForDatasetLabel(label, 0.85)
    
    // Ensure bar type is explicit
    out.type = 'bar'
    
    if (mapped) {
      out.backgroundColor = mapped.bg
      out.borderColor = mapped.border
      out.borderWidth = 1
      out.hoverBackgroundColor = mapped.bg
      out.hoverBorderColor = mapped.border
    } else {
      // Fallback for non-status charts (e.g. counts)
      const theme = currentThemeColors()
      const bg = withAlpha(theme.primary, 0.85)
      out.backgroundColor = out.backgroundColor ?? bg
      out.borderColor = out.borderColor ?? theme.primary
      out.borderWidth = 1
      out.hoverBackgroundColor = out.hoverBackgroundColor ?? bg
      out.hoverBorderColor = out.hoverBorderColor ?? theme.primary
    }
    
    return out
  })
  return d
})
  // Unique key to force re-render if needed (though :key on component is better)
  const computedOptions = computed(() => {
    const opts = JSON.parse(JSON.stringify(props.options))
    
    // Ensure scales exist
    if (!opts.scales) opts.scales = {}
    if (!opts.scales.x) opts.scales.x = {}
    
    // FORCE category type explicitly
    opts.scales.x.type = 'category'
    // Ensure we parse the x strings if needed (Chart.js usually does this auto for category)

    // Ensure visible bars
    opts.barPercentage = 0.9
    opts.categoryPercentage = 0.8
    
    // Disable animation to prevent visual glitches
    opts.animation = false

    return opts
  })
</script>

<template>
  <div class="relative w-full h-full min-h-[260px]">
    <!-- Key forces destroy/recreate to clear any bad internal state -->
    <Bar :key="JSON.stringify(normalized)" :data="normalized" :options="computedOptions" />
  </div>
</template>


