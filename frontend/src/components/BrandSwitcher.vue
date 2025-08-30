<script setup>
import { useUIStore } from '@/stores/ui'
const ui = useUIStore()

const brands = [
  { label: 'Indigo (default)', value: 'indigo' },
  { label: 'Rail (#bc5a45)', value: 'rail' },
  { label: 'Emerald', value: 'emerald' },
]
</script>

<template>
  <div class="inline-flex items-center gap-token-3">
    <span class="text-muted text-token-sm">Brand:</span>
    <div class="inline-flex gap-token-2">
      <button
        v-for="b in brands"
        :key="b.value"
        class="btn btn-outline"
        :aria-pressed="ui.brand === b.value"
        @click="ui.setBrand(b.value)"
      >
        {{ b.label }}
      </button>
    </div>
  </div>
</template>
