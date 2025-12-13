<script setup>
import { computed } from 'vue'

const props = defineProps({
  columns: { type: Array, required: true },
  rows: { type: Array, required: true },
  sortKey: { type: String, default: '' },
  sortDir: { type: String, default: 'asc' },
  loading: { type: Boolean, default: false },
})
const emit = defineEmits(['rowclick', 'sort'])

function handleSort(key, sortable = true) {
  if (!sortable) return
  emit('sort', key)
}
</script>

<template>
  <div class="overflow-x-auto rounded-2xl border-app bg-card text-app">
    <table class="min-w-full text-sm">
      <thead class="bg-card">
        <tr>
          <th v-for="c in columns" :key="c.key"
              :class="['font-semibold text-app px-4 py-3 select-none', c.align || 'text-left']"
              :style="c.width ? { width: c.width } : null"
              @click="handleSort(c.key, c.sortable !== false)"
              role="columnheader"
              :aria-sort="sortKey===c.key ? (sortDir==='asc'?'ascending':'descending') : 'none'">
            <div class="inline-flex items-center gap-1">
              <span>{{ c.label }}</span>
              <span v-if="c.sortable !== false" class="text-xs text-muted">
                <span v-if="sortKey!==c.key">↕</span>
                <span v-else>{{ sortDir==='asc' ? '▲' : '▼' }}</span>
              </span>
            </div>
          </th>
        </tr>
      </thead>
      <tbody>
        <template v-if="loading">
            <tr v-for="n in 10" :key="'skel-'+n" class="border-t animate-pulse">
                <td v-for="c in columns" :key="c.key" class="px-4 py-3">
                    <div class="h-4 bg-gray-200 dark:bg-gray-700 rounded w-full"></div>
                </td>
            </tr>
        </template>
        <template v-else>
            <tr v-for="(r, i) in rows" :key="i" class="border-t hover-row cursor-pointer"
                @click="emit('rowclick', r)">
            <td v-for="c in columns" :key="c.key" :class="['px-4 py-3', c.align || 'text-left']">
                <slot :name="c.key" :row="r">
                {{ r[c.key] }}
                </slot>
            </td>
            </tr>
            <tr v-if="rows.length === 0" class="border-t">
            <td :colspan="columns.length" class="px-4 py-6 text-center text-muted">
                No data
            </td>
            </tr>
        </template>
      </tbody>
    </table>
  </div>
</template>