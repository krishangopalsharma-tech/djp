<script setup>
import { computed } from 'vue'
import { useUIStore } from '@/stores/ui'

const ui = useUIStore()

const options = computed(() => ui.themes.map(k => ({
  key: k,
  label: ({
    light: 'Light',
    dark: 'Dark',
    railway: 'Railway',
    feather: 'Feather',
    fashion: 'Fashion',
    cherry: 'Cherry',
  }[k]) || k
})))

function onChange(e) {
  ui.setTheme(e.target.value)
}
</script>

<template>
  <div class="flex items-center gap-2">
    <span class="hidden sm:inline text-xs text-muted">Theme</span>
    <select
      class="h-9 rounded-md border border-app bg-card px-2 text-sm text-app"
      :value="ui.theme"
      @change="onChange"
      aria-label="Theme"
      :title="`Current theme: ${ui.theme}`"
    >
      <option v-for="opt in options" :key="opt.key" :value="opt.key">
        {{ opt.label }}
      </option>
    </select>
  </div>
</template>
