<script setup>
const props = defineProps({
  label: String,
  value: [String, Number],
  sublabel: String,
  // NEW
  trendDir: { type: String, default: null },   // 'up' | 'down' | 'flat' | null
  trendLabel: { type: String, default: '' },
})
</script>

<template>
  <div class="rounded-2xl border bg-white p-4">
    <div class="text-sm text-gray-600">{{ label }}</div>
    <div class="mt-1 text-2xl font-semibold">{{ value }}</div>
    <div class="mt-1 text-xs text-gray-500">{{ sublabel }}</div>

    <div
      v-if="trendDir"
      class="mt-1 text-xs inline-flex items-center gap-1"
      :class="trendDir==='up' ? 'text-green-600' : trendDir==='down' ? 'text-red-600' : 'text-gray-500'"
    >
      <svg v-if="trendDir==='up'" class="w-3 h-3" viewBox="0 0 24 24"><path fill="currentColor" d="M12 5l6 6h-4v8h-4v-8H6z"/></svg>
      <svg v-else-if="trendDir==='down'" class="w-3 h-3" viewBox="0 0 24 24"><path fill="currentColor" d="M12 19l-6-6h4V5h4v8h4z"/></svg>
      <svg v-else class="w-3 h-3" viewBox="0 0 24 24"><path fill="currentColor" d="M5 12h14v2H5z"/></svg>
      <span>{{ trendLabel }}</span>
    </div>
  </div>
</template>