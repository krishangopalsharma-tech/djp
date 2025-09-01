<script setup>
import { ref, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import Chart from 'chart.js/auto'

const props = defineProps({
  data: { type: Object, required: true },
  options: { type: Object, default: () => ({ responsive: true, maintainAspectRatio: false }) },
})

const canvas = ref(null)
let chart

async function render() {
  await nextTick()
  const el = canvas.value
  if (!el || !el.isConnected) return
  if (chart) { try { chart.destroy() } catch (_) {} }
  chart = new Chart(el, { type: 'pie', data: props.data, options: props.options })
}

onMounted(render)
watch(() => props.data, render, { deep: true })
watch(() => props.options, render, { deep: true })
onBeforeUnmount(() => { if (chart) try { chart.destroy() } catch (_) {} })
</script>

<template>
  <div class="h-full w-full">
    <canvas ref="canvas" class="h-full w-full"></canvas>
  </div>
</template>
