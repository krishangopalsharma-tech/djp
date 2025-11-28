<script setup>
import { ref, onBeforeUnmount, computed } from 'vue'

const props = defineProps({
  modelValue: { type: Number, default: 66 },   // first pane size in %
  min:        { type: Number, default: 20 },
  max:        { type: Number, default: 80 },
  layout:     { type: String, default: 'horizontal' }, // 'horizontal' | 'vertical'
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
  let pct = 0
  
  if (props.layout === 'vertical') {
    pct = ((e.clientY - rect.top) / rect.height) * 100
  } else {
    pct = ((e.clientX - rect.left) / rect.width) * 100
  }
  
  pct = Math.max(props.min, Math.min(props.max, pct))
  emit('update:modelValue', Math.round(pct))
}

function onPointerUp() {
  dragging = false
  window.removeEventListener('pointermove', onPointerMove)
  window.removeEventListener('pointerup', onPointerUp)
}
onBeforeUnmount(() => onPointerUp())

const isVertical = computed(() => props.layout === 'vertical')
</script>

<template>
  <!-- Stacks on small screens; draggable on lg+ -->
  <div ref="container" class="w-full h-full">
    <div class="grid grid-cols-1 gap-4 lg:block h-full">
      <div :class="['lg:flex', isVertical ? 'lg:flex-col h-full' : 'h-full']">
        <!-- First Pane -->
        <div 
          :class="['lg:shrink-0 lg:grow-0', isVertical ? 'lg:pb-3' : 'lg:pr-3']" 
          :style="{ [isVertical ? 'height' : 'width']: modelValue + '%' }"
        >
          <slot name="one" />
        </div>

        <!-- Divider / handle -->
        <div
          :class="[
            'hidden lg:block lg:shrink-0 lg:grow-0',
            isVertical ? 'h-2 w-full cursor-row-resize' : 'w-2 h-full cursor-col-resize'
          ]"
          @pointerdown="onPointerDown"
          title="Drag to resize"
        >
          <div :class="['bg-[var(--border)] rounded hover:bg-[var(--text)]/30 mx-auto', isVertical ? 'w-full h-0.5' : 'h-full w-0.5']"></div>
        </div>

        <!-- Second Pane -->
        <div 
          :class="['lg:min-w-0', isVertical ? 'lg:pt-3' : 'lg:pl-3']" 
          :style="{ [isVertical ? 'height' : 'width']: (100 - modelValue) + '%' }"
        >
          <slot name="two" />
        </div>
      </div>
    </div>
  </div>
</template>
