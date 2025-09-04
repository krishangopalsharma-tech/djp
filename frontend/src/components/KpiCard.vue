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
  <div class="card p-4 md:p-5 min-h-28 flex items-center justify-center text-center">
    <div class="flex flex-col items-center gap-1 w-full">
      <div class="text-sm text-app whitespace-nowrap overflow-hidden text-ellipsis" :title="label">{{ label }}</div>
      <div class="text-2xl font-semibold">{{ value }}</div>
      <div class="text-xs text-muted">{{ sublabel }}</div>

      <div
        v-if="trendDir"
        class="text-xs inline-flex items-center gap-1"
        :class="trendDir==='up' ? 'text-[var(--success)]' : trendDir==='down' ? 'text-[var(--danger)]' : 'text-muted'"
      >
        <svg v-if="trendDir==='up'" class="w-3 h-3" viewBox="0 0 24 24"><path fill="currentColor" d="M12 5l6 6h-4v8h-4v-8H6z"/></svg>
        <svg v-else-if="trendDir==='down'" class="w-3 h-3" viewBox="0 0 24 24"><path fill="currentColor" d="M12 19l-6-6h4V5h4v8h4z"/></svg>
        <svg v-else class="w-3 h-3" viewBox="0 0 24 24"><path fill="currentColor" d="M5 12h14v2H5z"/></svg>
        <span>{{ trendLabel }}</span>
      </div>
    </div>
  </div>
  
</template>
