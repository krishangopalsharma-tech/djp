<script setup>
import { Bar } from 'vue-chartjs'
import { Chart, BarElement, CategoryScale, LinearScale, Title, Tooltip, Legend, Filler } from 'chart.js'

Chart.register(BarElement, CategoryScale, LinearScale, Title, Tooltip, Legend, Filler)

defineProps({
  data: { type: Object, required: true },
  options: { type: Object, default: () => ({ responsive: true, maintainAspectRatio: false }) },
})
</script>

<template>
  <!-- Fill parent; keep a safe minimum for axes + legend -->
  <div class="relative w-full h-full min-h-[260px]">
    <Bar :data="data" :options="options" />
  </div>
  
</template>

<style scoped>
/* Important: do NOT force height:100% on the canvas */
:global(canvas) { width: 100% !important; }
</style>
