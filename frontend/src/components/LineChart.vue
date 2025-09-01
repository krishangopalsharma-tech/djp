<script setup>
import { Line } from 'vue-chartjs'
import { Chart, LineElement, PointElement, CategoryScale, LinearScale, Title, Tooltip, Legend, Filler } from 'chart.js'

Chart.register(LineElement, PointElement, CategoryScale, LinearScale, Title, Tooltip, Legend, Filler)

defineProps({
  data: { type: Object, required: true },
  options: { type: Object, default: () => ({ responsive: true, maintainAspectRatio: false }) },
})
</script>

<template>
  <div class="relative h-64 md:h-80">
    <Line :data="data" :options="options" />
  </div>
</template>

<style scoped>
:global(canvas) { width: 100% !important; }
</style>
