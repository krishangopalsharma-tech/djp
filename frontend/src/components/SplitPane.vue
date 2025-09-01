<script setup>
import { ref, onBeforeUnmount } from 'vue'

const props = defineProps({
  modelValue: { type: Number, default: 66 },   // left pane width in %
  minLeft:    { type: Number, default: 35 },
  maxLeft:    { type: Number, default: 80 },
})
const emit = defineEmits(['update:modelValue'])

const container = ref(null)
let dragging = false

function onPointerDown(e) {
  dragging = true
  window.addEventListener('pointermove', onPointerMove)
  window.addEventListener('pointerup', onPointerUp)
  e.preventDefault()
}
function onPointerMove(e) {
  if (!dragging || !container.value) return
  const rect = container.value.getBoundingClientRect()
  let pct = ((e.clientX - rect.left) / rect.width) * 100
  pct = Math.max(props.minLeft, Math.min(props.maxLeft, pct))
  emit('update:modelValue', Math.round(pct))
}
function onPointerUp() {
  dragging = false
  window.removeEventListener('pointermove', onPointerMove)
  window.removeEventListener('pointerup', onPointerUp)
}
onBeforeUnmount(() => onPointerUp())
</script>

<template>
  <!-- Stacks on small screens; draggable on lg+ -->
  <div ref="container" class="w-full">
    <div class="grid grid-cols-1 gap-4 lg:block">
      <div class="lg:flex">
        <!-- Left -->
        <div class="lg:shrink-0 lg:grow-0 lg:pr-3" :style="{ width: modelValue + '%' }">
          <slot name="left" />
        </div>

        <!-- Divider / handle -->
        <div
          class="hidden lg:block w-2 lg:shrink-0 lg:grow-0 cursor-col-resize"
          @pointerdown="onPointerDown"
          title="Drag to resize"
        >
          <div class="h-full mx-auto w-0.5 bg-[var(--border)] rounded hover:bg-[var(--text)]/30"></div>
        </div>

        <!-- Right -->
        <div class="lg:pl-3 lg:min-w-[280px]" :style="{ width: (100 - modelValue) + '%' }">
          <slot name="right" />
        </div>
      </div>
    </div>
  </div>
</template>
