<script setup>
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import Chart from 'chart.js/auto'

const props = defineProps({
  data: { type: Object, required: true },
  options: { type: Object, default: () => ({ responsive: true, maintainAspectRatio: false }) },
})

const canvas = ref(null)
let chart

function render() {
  if (!canvas.value) return
  if (chart) chart.destroy()
  chart = new Chart(canvas.value, {
    type: 'pie',
    data: props.data,
    options: props.options,
  })
}

onMounted(render)
watch(() => props.data, render, { deep: true })
watch(() => props.options, render, { deep: true })
onBeforeUnmount(() => { if (chart) chart.destroy() })
</script>

<template>
  <div class="h-full w-full">
    <canvas ref="canvas" class="h-full w-full"></canvas>
  </div>
</template>