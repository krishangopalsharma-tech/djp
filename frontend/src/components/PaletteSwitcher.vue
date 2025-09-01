<script setup>
const PALETTES = [
  'gantry','fashion','feather-step-classic','cherry','lgm','haqq','axencis',
  'lukas','askit','shipp','wemakefab','stereotype','wild-goats','gym'
]

const PALETTE_KEY = 'ui.palette'
const root = document.documentElement

function setPalette(name) {
  root.dataset.palette = name
  localStorage.setItem(PALETTE_KEY, name)
}
</script>

<template>
  <div class="space-y-2">
    <div class="text-sm font-medium">Palette Switcher</div>
    <div class="flex flex-wrap gap-2">
      <button
        v-for="p in PALETTES"
        :key="p"
        class="px-3 py-1.5 rounded-lg border text-xs bg-white hover:bg-gray-50"
        @click="setPalette(p)"
      >
        {{ p }}
      </button>
    </div>

    <!-- live swatches -->
    <div class="mt-3 grid grid-cols-5 gap-2">
      <div class="h-8 rounded bg-p1"></div>
      <div class="h-8 rounded bg-p2"></div>
      <div class="h-8 rounded bg-p3"></div>
      <div class="h-8 rounded bg-p4"></div>
      <div class="h-8 rounded bg-p5"></div>
    </div>
  </div>
</template>


