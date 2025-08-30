<script setup>
import { computed } from 'vue'
import { useUIStore } from '@/stores/ui'

const ui = useUIStore()
const isDark = computed(() => ui.theme === 'dark')

function toLight() { ui.setTheme('light') }
function toDark()  { ui.setTheme('dark') }
function toggle()  { ui.toggleTheme() }
</script>

<template>
  <div class="inline-flex items-center gap-token-3">
    <span class="text-muted text-token-sm">Theme:</span>
    <button class="btn btn-outline" @click="toLight" :aria-pressed="!isDark">Light</button>
    <button class="btn btn-outline" @click="toDark"  :aria-pressed="isDark">Dark</button>
    <button class="btn btn-primary" @click="toggle">Toggle</button>
  </div>
</template>
