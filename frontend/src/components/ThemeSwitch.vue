<script setup>
import { useUIStore } from '@/stores/ui'
const ui = useUIStore()
const swatches = [
  { key: 'light',   label: 'Light' },
  { key: 'dark',    label: 'Dark' },
  { key: 'railway', label: 'Railway' },
]
</script>

<template>
  <div class="space-y-2">
    <h3 class="text-base font-semibold">Color theme</h3>
    <div class="flex items-center gap-3">
      <button
        v-for="s in swatches"
        :key="s.key"
        class="btn border"
        :class="ui.theme === s.key ? 'btn-primary' : 'btn-outline'"
        @click="ui.setTheme(s.key)"
      >
        {{ s.label }}
      </button>
    </div>
    <p class="text-sm text-muted">Themes switch CSS variables for background, text, cards, and buttons.</p>
  </div>
</template>
